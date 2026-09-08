"""HBOCpred audited reanalysis, release R4.
All missingness screens, imputation, scaling and supervised feature selection are
refitted in each inner-training partition. No application record determines the
candidate set or a fitted parameter. Outer-test outputs are the evaluation data.
Fixed learner families are a revision-stage design choice, not re-selected nine-
learner competition. ENET_LR is a legacy key: every fitted LR uses L2 (l1_ratio=0).
"""
import json
import numpy as np,pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from learner_utils import (LEARNERS,FAMILY,GRIDS as OLD_GRIDS,N_FEATURES,EPS,
 _seed_from,make_learner,raw_score,to_logit_input,platt_fit,platt_apply,
 ba_threshold,stratum_key,consensus_rank,binary_metrics,continuous_metrics,wilson)
GRIDS={**OLD_GRIDS,'ENET_LR':[{'C':c,'l1_ratio':0.0} for c in (0.03,0.1,0.3,1.0,3.0,10.0)]}
N_INNER=4;N_CONFIGS=6

def fit_preprocess(X,y,seed):
 # Include no column with >40% missingness or no observed variation in training.
 eligible=[c for c in X if X[c].isna().mean()<=0.40 and X[c].nunique(dropna=True)>1]
 if not eligible:raise ValueError('No eligible training features')
 imp=SimpleImputer(strategy='median').fit(X[eligible])
 Xi=pd.DataFrame(imp.transform(X[eligible]),columns=eligible,index=X.index)
 sc=StandardScaler().fit(Xi)
 Xs=pd.DataFrame(sc.transform(Xi),columns=eligible,index=X.index)
 panel,crit=consensus_rank(Xs,np.asarray(y),seed)
 return dict(columns=eligible,imputer=imp,scaler=sc,panel=panel,feature_criteria=crit)

def transform(pre,X):
 Xi=pre['imputer'].transform(X[pre['columns']])
 Xs=pre['scaler'].transform(Xi)
 ix=[pre['columns'].index(c) for c in pre['panel']]
 return Xs[:,ix]

def fit_partition(Xtr_raw,ytr,gtr,seed,exclude=('Reliability_index',),n_configs=N_CONFIGS,log=None):
 X=Xtr_raw.drop(columns=[c for c in exclude if c in Xtr_raw]).copy()
 y=np.asarray(ytr).astype(int);g=np.asarray(gtr)
 key=stratum_key(pd.Series(g),pd.Series(y),min_n=N_INNER)
 splits=list(StratifiedKFold(N_INNER,shuffle=True,random_state=seed).split(X,key))
 # Cache transformations shared by learners/configurations, never across validation boundaries.
 inner=[];foldid=np.empty(len(y),dtype=int)
 for j,(tr,va) in enumerate(splits):
  pre=fit_preprocess(X.iloc[tr],y[tr],seed+1000+j)
  inner.append((tr,va,transform(pre,X.iloc[tr]),transform(pre,X.iloc[va]),pre))
  foldid[va]=j
 pre=fit_preprocess(X,y,seed);Xp=transform(pre,X)
 fitted={};p_cross={};tuning_records={};inner_raw={}
 for name in LEARNERS:
  rng=np.random.default_rng(_seed_from(seed,name));grid=GRIDS[name]
  indices=rng.choice(len(grid),size=min(n_configs,len(grid)),replace=False)
  results=[]
  for gi in indices:
   params=grid[gi];aucs=[];oof=np.empty(len(y))
   for tr,va,xt,xv,_ in inner:
    m=make_learner(name,params,seed);m.fit(xt,y[tr]);s=raw_score(m,xv);oof[va]=s
    from sklearn.metrics import roc_auc_score
    aucs.append(roc_auc_score(y[va],s))
   results.append({'auc_mean':float(np.mean(aucs)),'auc_sd':float(np.std(aucs,ddof=1)),'params':params,'oof':oof})
  results.sort(key=lambda r:(-r['auc_mean'],r['auc_sd'],json.dumps(r['params'],sort_keys=True)))
  best=results[0];z=to_logit_input(name,best['oof']);pc=np.empty(len(y))
  # Cross-fitted calibration reduces reuse of each row's label in threshold development.
  for tr,va,_,_,_ in inner:
   a,b=platt_fit(z[tr],y[tr]);pc[va]=platt_apply(a,b,z[va])
  thr,thr_ba=ba_threshold(pc,y)
  a,b=platt_fit(z,y)
  m=make_learner(name,best['params'],seed);m.fit(Xp,y)
  fitted[name]={'model':m,'params':best['params'],'platt':(a,b),'threshold':thr,'inner_ba':thr_ba,'inner_auc':best['auc_mean']}
  p_cross[name]=pc;inner_raw[name]=best['oof']
  tuning_records[name]=[{k:v for k,v in r.items() if k!='oof'} for r in results]
  if log:log(f'{name} best={best["params"]} inner AUROC={best["auc_mean"]:.4f}')
 mean4=np.mean(np.column_stack([p_cross[n] for n in LEARNERS]),axis=1)
 z=np.log(np.clip(mean4,EPS,1-EPS)/(1-np.clip(mean4,EPS,1-EPS)))
 ma,mb=platt_fit(z,y)
 return dict(**pre,learners=fitted,smac=(ma,mb),seed=seed,
  requested_columns=list(Xtr_raw.columns),excluded=list(exclude),
  inner_panels=[p['panel'] for *_,p in inner],inner_eligible=[p['columns'] for *_,p in inner],
  inner_fold_id=foldid,inner_raw_scores=inner_raw,inner_cross_calibrated=p_cross,
  tuning=tuning_records,release='R4_inductive_inner_preprocessing',
  development_note='Inner tuning/calibration reuse training labels; only outer-test data evaluate performance.')

def predict_partition(obj,X_raw):
 missing=set(obj['columns'])-set(X_raw.columns)
 if missing:raise ValueError(f'Missing columns: {sorted(missing)}')
 X=transform(obj,X_raw);o=pd.DataFrame(index=X_raw.index)
 for name in LEARNERS:
  L=obj['learners'][name];z=to_logit_input(name,raw_score(L['model'],X))
  o['p_'+name]=platt_apply(*L['platt'],z)
  o['vote_'+name]=(o['p_'+name]>=L['threshold']).astype(int)
 votes=['vote_'+n for n in LEARNERS];o['V']=o[votes].sum(axis=1);o['vote_vector']=o[votes].astype(str).agg(''.join,axis=1)
 o['Mean4']=o[['p_'+n for n in LEARNERS]].mean(axis=1)
 m=np.clip(o.Mean4.to_numpy(),EPS,1-EPS);o['S_MAC']=platt_apply(*obj['smac'],np.log(m/(1-m)))
 o['n_observed_panel']=X_raw[obj['panel']].notna().sum(axis=1)
 o['panel_size']=len(obj['panel']);o['complete_flag']=(o.n_observed_panel>=int(np.ceil(0.8*len(obj['panel'])))).astype(int)
 o['directional_descriptor']=np.where(o.V==0,'Unanimous B/LB-directed',np.where(o.V==4,'Unanimous LP/P-directed','Mixed votes'))
 cols=[c for c in o if c.startswith(('p_','vote_')) or c in ['V','Mean4','S_MAC','directional_descriptor']]
 o.loc[o.complete_flag==0,cols]=np.nan
 return o
