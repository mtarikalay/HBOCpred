"""
HBOCpred core: fold-local preprocessing, consensus feature ranking, family-balanced
learners (SVM-RBF, elastic-net LR, Extra Trees, HistGB), Platt calibration,
balanced-accuracy thresholds, four-bit voting (V0-V4) and the S_MAC meta-calibrated score.

Everything that is *fitted* (imputer, scaler, feature ranking, hyper-parameters,
calibrators, thresholds, S_MAC meta-calibration) is fitted on the training partition only.
"""
import itertools, json, hashlib, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import StratifiedKFold

EPS = 1e-6
LEARNERS = ["SVM_RBF", "ENET_LR", "EXTRA_TREES", "HIST_GB"]
FAMILY = {"SVM_RBF": "classical", "ENET_LR": "classical", "EXTRA_TREES": "bagging", "HIST_GB": "boosting"}

# Prespecified search spaces (Table 2 of the manuscript)
GRIDS = {
    "ENET_LR": [dict(C=c, l1_ratio=l) for c in (0.03, 0.10, 0.30, 1, 3, 10) for l in (0, 0.5, 1)],
    "SVM_RBF": [dict(C=c, gamma=g) for c in (0.25, 0.75, 2, 6, 16) for g in ("scale", 0.01, 0.03, 0.10)],
    "EXTRA_TREES": [dict(max_depth=d, max_features=f, min_samples_leaf=m)
                    for d in (None, 10, 18) for f in ("sqrt", 0.4, 0.7) for m in (1, 3, 7)],
    "HIST_GB": [dict(max_leaf_nodes=ln, min_samples_leaf=m, max_iter=it, learning_rate=lr, l2_regularization=l2)
                for ln in (15, 31) for m in (10, 20) for it in (100, 200) for lr in (0.03, 0.10) for l2 in (0, 1)],
}
N_CONFIGS = 6          # configurations sampled without replacement per learner and split
N_FEATURES = 25        # consensus panel size
N_INNER = 4            # inner folds
R_MAX = 0.90           # fold-local correlation-cluster cut-off


def _seed_from(*parts):
    h = hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()
    return int(h[:8], 16)


def make_learner(name, params, seed):
    if name == "ENET_LR":
        return LogisticRegression(solver="saga", max_iter=5000, tol=1e-4, random_state=seed, **params)
    if name == "SVM_RBF":
        return SVC(kernel="rbf", random_state=seed, **params)
    if name == "EXTRA_TREES":
        return ExtraTreesClassifier(n_estimators=220, random_state=seed, n_jobs=1, **params)
    if name == "HIST_GB":
        return HistGradientBoostingClassifier(random_state=seed, **params)
    raise ValueError(name)


def raw_score(model, X):
    """LP/P-directed raw score: decision function for SVM, probability for the others."""
    if hasattr(model, "decision_function") and isinstance(model, SVC):
        return model.decision_function(X)
    return model.predict_proba(X)[:, 1]


def to_logit_input(name, s):
    if name == "SVM_RBF":
        return s
    s = np.clip(s, EPS, 1 - EPS)
    return np.log(s / (1 - s))


def platt_fit(z, y):
    lr = LogisticRegression(C=1e6, max_iter=1000)
    lr.fit(z.reshape(-1, 1), y)
    return float(lr.intercept_[0]), float(lr.coef_[0, 0])


def platt_apply(a, b, z):
    return 1.0 / (1.0 + np.exp(-(a + b * z)))


def ba_threshold(p, y):
    """Threshold maximising balanced accuracy; ties -> closest to 0.5, then lower."""
    cands = np.unique(np.concatenate([p, [0.5]]))
    best, best_ba = None, -1
    for t in cands:
        pred = (p >= t).astype(int)
        tpr = (pred[y == 1] == 1).mean()
        tnr = (pred[y == 0] == 0).mean()
        ba = (tpr + tnr) / 2
        if ba > best_ba + 1e-12:
            best, best_ba = t, ba
        elif abs(ba - best_ba) <= 1e-12:
            if abs(t - 0.5) < abs(best - 0.5) - 1e-12 or (abs(abs(t - 0.5) - abs(best - 0.5)) <= 1e-12 and t < best):
                best = t
    return float(best), float(best_ba)


def stratum_key(gene, y, min_n=5):
    key = gene.astype(str) + "|" + y.astype(str)
    vc = key.value_counts()
    small = vc[vc < min_n].index
    key = key.where(~key.isin(small), "pooled|" + y.astype(str))
    return key


# ---------------------------------------------------------------- feature ranking
def consensus_rank(Xtr, ytr, seed, n_keep=N_FEATURES):
    """Fold-local consensus ranking (mean rank over four criteria) on imputed+scaled data.
    Criteria: orientation-independent univariate AUROC, mutual information,
    L1-logistic |coefficient| (median over 12 bootstrap fits, selection frequency as tie-break),
    Extra Trees impurity importance over shadow features (median of 6 fits)."""
    rng = np.random.default_rng(seed)
    cols = list(Xtr.columns)
    X = Xtr.values
    n, p = X.shape
    # 1 univariate AUROC
    au = np.array([abs(roc_auc_score(ytr, X[:, j]) - 0.5) if np.std(X[:, j]) > 0 else 0 for j in range(p)])
    # 2 mutual information
    mi = mutual_info_classif(X, ytr, random_state=seed)
    # 3 L1 logistic bootstrap
    coef_abs = np.zeros((12, p)); sel = np.zeros(p)
    for b in range(12):
        idx = rng.integers(0, n, n)
        if len(np.unique(ytr[idx])) < 2:
            continue
        m = LogisticRegression(l1_ratio=1.0, solver="liblinear", C=0.3, max_iter=2000, random_state=seed + b)
        m.fit(X[idx], ytr[idx])
        coef_abs[b] = np.abs(m.coef_[0]); sel += (np.abs(m.coef_[0]) > 1e-8)
    l1 = np.median(coef_abs, axis=0) + 1e-6 * sel
    # 4 Extra Trees with shadow features
    imp = np.zeros((6, p))
    for b in range(6):
        shadow = X.copy()
        for j in range(p):
            shadow[:, j] = rng.permutation(shadow[:, j])
        et = ExtraTreesClassifier(n_estimators=150, random_state=seed + 100 + b, n_jobs=1)
        et.fit(np.hstack([X, shadow]), ytr)
        fi = et.feature_importances_
        imp[b] = fi[:p] - fi[p:].max()
    etimp = np.median(imp, axis=0)
    crit = pd.DataFrame({"auroc": au, "mi": mi, "l1": l1, "et": etimp}, index=cols)
    ranks = crit.rank(ascending=False)
    crit["mean_rank"] = ranks.mean(axis=1)
    crit = crit.sort_values("mean_rank")
    # correlation-cluster representatives: walk down the consensus order and skip a predictor
    # whose |Pearson r| with an already retained predictor exceeds R_MAX (fold-local)
    C = np.corrcoef(X.T) if p > 1 else np.ones((1, 1))
    col_idx = {c: i for i, c in enumerate(cols)}
    keep, dropped = [], []
    for c in crit.index:
        j = col_idx[c]
        if any(abs(C[j, col_idx[k]]) > R_MAX for k in keep):
            dropped.append(c); continue
        keep.append(c)
        if len(keep) == n_keep:
            break
    crit["selected"] = crit.index.isin(keep)
    crit["dropped_redundant"] = crit.index.isin(dropped)
    return keep, crit


# ---------------------------------------------------------------- one training partition
def fit_partition(Xtr_raw, ytr, gtr, seed, feature_panel=None, exclude=(), n_configs=N_CONFIGS, log=None):
    """Fit the complete HBOCpred object on one training partition. Returns a dict."""
    Xtr_raw = Xtr_raw.drop(columns=[c for c in exclude if c in Xtr_raw.columns])
    imp = SimpleImputer(strategy="median").fit(Xtr_raw)
    Xi = pd.DataFrame(imp.transform(Xtr_raw), columns=Xtr_raw.columns, index=Xtr_raw.index)
    sc = StandardScaler().fit(Xi)
    Xs = pd.DataFrame(sc.transform(Xi), columns=Xi.columns, index=Xi.index)
    ytr = np.asarray(ytr).astype(int)

    if feature_panel is None:
        panel, crit = consensus_rank(Xs, ytr, seed)
    else:
        panel, crit = [c for c in feature_panel if c in Xs.columns], None
    Xp = Xs[panel].values

    key = stratum_key(pd.Series(gtr, index=Xtr_raw.index), pd.Series(ytr, index=Xtr_raw.index))
    inner = StratifiedKFold(n_splits=N_INNER, shuffle=True, random_state=seed)
    inner_splits = list(inner.split(Xp, key))

    fitted = {}
    inner_oof_cal = {}
    for name in LEARNERS:
        rng = np.random.default_rng(_seed_from(seed, name))
        grid = GRIDS[name]
        idx = rng.choice(len(grid), size=min(n_configs, len(grid)), replace=False)
        results = []
        for gi in idx:
            params = grid[gi]
            aucs = []
            for tr_i, va_i in inner_splits:
                m = make_learner(name, params, seed)
                m.fit(Xp[tr_i], ytr[tr_i])
                aucs.append(roc_auc_score(ytr[va_i], raw_score(m, Xp[va_i])))
            results.append((np.mean(aucs), -np.std(aucs), json.dumps(params, sort_keys=True), params))
        results.sort(key=lambda r: (-r[0], -r[1], r[2]))
        best = results[0][3]
        # inner OOF raw scores with the best configuration -> calibration + threshold
        oof = np.zeros(len(ytr))
        for tr_i, va_i in inner_splits:
            m = make_learner(name, best, seed); m.fit(Xp[tr_i], ytr[tr_i])
            oof[va_i] = raw_score(m, Xp[va_i])
        z = to_logit_input(name, oof)
        a, b = platt_fit(z, ytr)
        pcal = platt_apply(a, b, z)
        thr, thr_ba = ba_threshold(pcal, ytr)
        final = make_learner(name, best, seed); final.fit(Xp, ytr)
        fitted[name] = dict(model=final, params=best, platt=(a, b), threshold=thr, inner_ba=thr_ba,
                            inner_auc=results[0][0], tuning=[(r[0], -r[1], r[2]) for r in results])
        inner_oof_cal[name] = pcal
        if log: log(f"    {name}: best={best} innerAUC={results[0][0]:.4f} thr={thr:.4f}")
    mean4 = np.mean(np.column_stack([inner_oof_cal[n] for n in LEARNERS]), axis=1)
    zm = np.log(np.clip(mean4, EPS, 1 - EPS) / (1 - np.clip(mean4, EPS, 1 - EPS)))
    ma, mb = platt_fit(zm, ytr)
    return dict(imputer=imp, scaler=sc, columns=list(Xtr_raw.columns), panel=panel, feature_criteria=crit,
                learners=fitted, smac=(ma, mb), seed=seed)


def predict_partition(obj, X_raw):
    X = X_raw[obj["columns"]]
    Xi = pd.DataFrame(obj["imputer"].transform(X), columns=obj["columns"], index=X.index)
    Xs = pd.DataFrame(obj["scaler"].transform(Xi), columns=obj["columns"], index=X.index)
    Xp = Xs[obj["panel"]].values
    out = pd.DataFrame(index=X.index)
    for name in LEARNERS:
        L = obj["learners"][name]
        z = to_logit_input(name, raw_score(L["model"], Xp))
        p = platt_apply(*L["platt"], z)
        out[f"p_{name}"] = p
        out[f"vote_{name}"] = (p >= L["threshold"]).astype(int)
    out["V"] = out[[f"vote_{n}" for n in LEARNERS]].sum(axis=1)
    out["vote_vector"] = out[[f"vote_{n}" for n in LEARNERS]].astype(str).agg("".join, axis=1)
    m4 = out[[f"p_{n}" for n in LEARNERS]].mean(axis=1).values
    zm = np.log(np.clip(m4, EPS, 1 - EPS) / (1 - np.clip(m4, EPS, 1 - EPS)))
    out["Mean4"] = m4
    out["S_MAC"] = platt_apply(*obj["smac"], zm)
    out["n_observed_panel"] = X_raw[obj["panel"]].notna().sum(axis=1).values
    out["complete_flag"] = (out["n_observed_panel"] >= 20).astype(int)
    return out


# ---------------------------------------------------------------- metrics
def wilson(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def binary_metrics(y, pred):
    y = np.asarray(y); pred = np.asarray(pred)
    tp = int(((pred == 1) & (y == 1)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    sens = tp / (tp + fn) if tp + fn else np.nan
    spec = tn / (tn + fp) if tn + fp else np.nan
    ppv = tp / (tp + fp) if tp + fp else np.nan
    npv = tn / (tn + fn) if tn + fn else np.nan
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else np.nan
    den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / den if den else np.nan
    return dict(TP=tp, TN=tn, FP=fp, FN=fn, sensitivity=sens, specificity=spec, PPV=ppv, NPV=npv, F1=f1, MCC=mcc,
                balanced_accuracy=np.nanmean([sens, spec]))


def continuous_metrics(y, s):
    y = np.asarray(y); s = np.asarray(s)
    out = dict(AUROC=np.nan, AUPRC=np.nan, Brier=brier_score_loss(y, s))
    if len(np.unique(y)) == 2:
        out["AUROC"] = roc_auc_score(y, s); out["AUPRC"] = average_precision_score(y, s)
        z = np.log(np.clip(s, EPS, 1 - EPS) / (1 - np.clip(s, EPS, 1 - EPS)))
        lr = LogisticRegression(C=1e6, max_iter=1000).fit(z.reshape(-1, 1), y)
        out["cal_intercept"] = float(lr.intercept_[0]); out["cal_slope"] = float(lr.coef_[0, 0])
    return out
