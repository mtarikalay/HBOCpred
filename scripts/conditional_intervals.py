"""Conditional intervals on one OOF prediction per variant, never on repeated rows.
Class-stratified bootstrap of fixed scores, without model refitting or gene-cluster
resampling: does not capture training uncertainty, ascertainment or transport.
"""
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score
ROOT=Path(__file__).resolve().parents[1]
p=pd.read_csv(ROOT/'outputs/oof_predictions_repeated_cv.csv');p=p[(p.repeat==1)&(p.complete_flag==1)]
rng=np.random.default_rng(20260905);y=p.y.to_numpy();v=(p.V.to_numpy()>=3);s=p.S_MAC.to_numpy();neg=np.flatnonzero(y==0);pos=np.flatnonzero(y==1)
def evaluate(ids):
 t=y[ids];z=s[ids];d=v[ids];se=d[t==1].mean();sp=(~d[t==0]).mean()
 return [se,sp,(se+sp)/2,roc_auc_score(t,z),average_precision_score(t,z),((z-t)**2).mean()]
boot=np.array([evaluate(np.r_[rng.choice(neg,len(neg),replace=True),rng.choice(pos,len(pos),replace=True)]) for _ in range(2000)])
lo,hi=np.quantile(boot,[.025,.975],axis=0);point=evaluate(np.arange(len(p)))
r=pd.DataFrame({'metric':['sensitivity','specificity','balanced_accuracy','AUROC','AUPRC','Brier'],'estimate':point,'conditional_lower':lo,'conditional_upper':hi,'n_evaluable':len(p),'bootstrap_replicates':2000,'seed':20260905})
r.to_csv(ROOT/'tables/conditional_intervals_repeat1.csv',index=False);print(r.to_string(index=False))
