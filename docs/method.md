# Method and formulas

The ensemble contains SVM–RBF, L2 logistic regression, Extra Trees and histogram gradient boosting. Preprocessing and feature selection are fitted inside each training partition. Source labels are B/LB = 0 and LP/P = 1.

Let $z_j$ be learner $j$'s decision value (SVM) or the logit of its clipped raw probability (the other learners). Its calibrated score is

$$p_j=\sigma(a_j+b_jz_j),\qquad \sigma(t)=\frac{1}{1+e^{-t}}.$$

For the fitted threshold $t_j$,

$$v_j=\mathbb{1}(p_j\ge t_j),\qquad V=\sum_{j=1}^{4}v_j.$$

V0 denotes unanimous B/LB-directed votes, V1–V3 mixed votes and V4 unanimous LP/P-directed votes. The four-bit vector preserves learner order: SVM–RBF, L2 logistic, Extra Trees, HistGB.

The continuous score uses

$$\mathrm{Mean4}=\frac{1}{4}\sum_{j=1}^{4}p_j,$$

$$S_{\mathrm{MAC}}=\sigma\left(\alpha+\beta\log\frac{m}{1-m}\right),\quad m=\mathrm{clip}(\mathrm{Mean4},10^{-6},1-10^{-6}).$$

The frozen deployment parameters are $\alpha=0.03387594909065403$ and $\beta=1.1353639821459005$. Learner-specific parameters and thresholds are in `models/parameters.json`.

At least 80% of selected predictors must be observed before imputation: 20 of 25 in deployment. Otherwise all scores and vote outputs are suppressed. S_MAC adds ranking resolution and does not contribute an extra vote.

Internal performance is assessed against the source labels using repeated nested cross-validation and complete gene holdouts. Label dependence, predictor training overlap and the difference between classified and unresolved variants limit clinical interpretation. Neither V0 nor S_MAC establishes benignity, clinical risk or PP3/BP4 evidence strength.
