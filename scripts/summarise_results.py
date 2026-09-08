"""Regenerate all R4 numerical tables from saved, genuine model outputs."""
import json,re,sys
from pathlib import Path
import numpy as np,pandas as pd,joblib
from sklearn.metrics import roc_auc_score,average_precision_score,accuracy_score
from sklearn.ensemble import ExtraTreesClassifier
from hbocpred_core import *
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';TAB=ROOT/'tables';DATA=ROOT/'data';MOD=ROOT/'models'
GENES=['BRCA1','BRCA2','PALB2','ATM','CHEK2','TP53','PTEN','CDH1','STK11','BARD1','BRIP1','RAD51C','RAD51D','NBN','BLM','FANCA','FANCC']
A=pd.read_csv(DATA/'anchors_all_numeric.csv');B=pd.read_csv(DATA/'application_all_numeric.csv.gz')
features=json.loads((DATA/'candidate_features.json').read_text())
allnum=[c for c in A if c not in ['SPDI','Location','Gene','ACMG_variations','clinvar_id','clinvar_hgvs','clinvar_clnsig','clinvar_review','y']]
pd.DataFrame({'predictor':allnum,'missing_n':[int(A[c].isna().sum()) for c in allnum],'missing_fraction':[float(A[c].isna().mean()) for c in allnum],'observed_mean':[A[c].mean() for c in allnum],'observed_sd':[A[c].std() for c in allnum]}).to_csv(TAB/'all_numeric_predictor_summary.csv',index=False)
def group(v):return np.where(pd.isna(v),'Incomplete',np.where(v==0,'V0',np.where(v==4,'V4','V1–V3')))
def metrics(p):
 e=p[p.complete_flag==1].copy()
 return dict(n_total=len(p),n_evaluable=len(e),**binary_metrics(e.y,(e.V>=3).astype(int)),**continuous_metrics(e.y,e.S_MAC))
def proportion(k,n):
 lo,hi=wilson(k,n);return {'n':int(k),'denominator':int(n),'proportion':float(k/n) if n else None,'lo':float(lo),'hi':float(hi)}
def combine(pattern,expected):
 files=sorted(OUT.glob(pattern));assert len(files)==expected,(pattern,len(files))
 return pd.concat([pd.read_csv(p,dtype={'vote_vector':str}) for p in files],ignore_index=True)
P=combine('cv_r*f*_predictions.csv',25);P['repeat']=P.partition.str.extract(r'cv_r(\d+)').astype(int);P['outer_fold']=P.partition.str.extract(r'f(\d+)').astype(int)
P.to_csv(OUT/'oof_predictions_repeated_cv.csv',index=False)
L=combine('logo_*_predictions.csv',17);L.to_csv(OUT/'logo_predictions.csv',index=False)
F=P[P.repeat==1].copy();D=pd.read_csv(OUT/'application_catalogue.csv.gz',dtype={'vote_vector':str})
summary={'analysis_release':'R4','source_counts':A.groupby('Gene').y.agg(['count','sum']).to_dict('index')}
perf=pd.DataFrame([dict(repeat=r,**metrics(p)) for r,p in P.groupby('repeat')]);perf.to_csv(TAB/'performance_by_repeat.csv',index=False)
summary['performance']={c:{'mean':float(perf[c].mean()),'sd':float(perf[c].std()),'min':float(perf[c].min()),'max':float(perf[c].max())} for c in perf if c!='repeat'}
summary['fixed']=metrics(F);summary['logo']=metrics(L)
# Full state-label accounting, including any nonevaluable cases.
F['group']=group(F.V);counts=pd.crosstab(F.y,F.group).reindex(index=[0,1],columns=['V0','V1–V3','V4','Incomplete'],fill_value=0)
counts.index=['B/LB','LP/P'];counts['Total']=counts.sum(axis=1);counts.loc['Total']=counts.sum();counts.to_csv(TAB/'state_by_label.csv')
ct=pd.crosstab(F.y,F.V).reindex(index=[0,1],columns=range(5),fill_value=0);ct.to_csv(TAB/'exact_state_by_label.csv')
summary['state_counts']=ct.to_dict('index');summary['group_counts']=counts.to_dict('index')
n=len(F);un=int(F.V.isin([0,4]).sum());agree=int(((F.y==0)&(F.V==0)|((F.y==1)&(F.V==4))).sum())
summary['unanimity']=proportion(un,n);summary['conditional_agreement']=proportion(agree,un);summary['mixed']=proportion(int(F.V.between(1,3).sum()),n)
summary['LP_at_V0']=proportion(int(((F.y==1)&(F.V==0)).sum()),int((F.y==1).sum()))
summary['B_at_V4']=proportion(int(((F.y==0)&(F.V==4)).sum()),int((F.y==0).sum()))
summary['directional_error_rate_ratio']=summary['LP_at_V0']['proportion']/summary['B_at_V4']['proportion'] if summary['B_at_V4']['n'] else None
summary['state_LP_fraction']={str(v):proportion(int(((F.y==1)&(F.V==v)).sum()),int((F.V==v).sum())) for v in range(5)}
v2=F[F.V==2].copy();v2['pair']=np.where(v2.vote_EXTRA_TREES+v2.vote_HIST_GB==2,'Both tree learners',np.where(v2.vote_SVM_RBF+v2.vote_ENET_LR==2,'Both conventional learners','One of each family'))
vc=pd.crosstab(v2['pair'],v2.y).reindex(index=['Both tree learners','One of each family','Both conventional learners'],columns=[0,1],fill_value=0);vc.to_csv(TAB/'V2_pair_composition.csv');summary['V2_pairs']=vc.to_dict('index')
stable=P.assign(group=group(P.V)).pivot(index='SPDI',columns='repeat',values='group').nunique(axis=1)==1;summary['group_stability']=proportion(int(stable.sum()),len(stable))
# Per-gene held-out outputs and Wilson intervals are conditional on these samples.
rows=[]
for gene in GENES:
 p=L[L.Gene==gene];m=metrics(p);row=dict(Gene=gene,**m,n_B=int((p.y==0).sum()),n_LP=int((p.y==1).sum()))
 for y,name in [(0,'B'),(1,'LP')]:
  for v in [0,1,2,3,4]:row[f'{name}_V{v}']=int(((p.y==y)&(p.V==v)).sum())
 row['sensitivity_lo'],row['sensitivity_hi']=wilson(m['TP'],m['TP']+m['FN']);row['specificity_lo'],row['specificity_hi']=wilson(m['TN'],m['TN']+m['FP']);rows.append(row)
G=pd.DataFrame(rows);G.to_csv(TAB/'per_gene_held_out.csv',index=False);summary['per_gene']=G.to_dict('records')
# Sensitivity analyses are paired on exactly the primary repeat-1 fold map.
sens=[dict(analysis='Primary, repeat 1',**metrics(F))]
for pattern,name in [('with_RI_f*_predictions.csv','Reliability_index included'),('without_addAF_AlphaMissense_f*_predictions.csv','BayesDel addAF and AlphaMissense excluded'),('transcript_subset_f*_predictions.csv','Transcript missense subset, refitted')]:
 p=combine(pattern,5);p.to_csv(OUT/(pattern.split('_f')[0]+'_oof.csv'),index=False);sens.append(dict(analysis=name,**metrics(p)))
# Primary predictions restricted to the same transcript missense subset, to show population versus refitting effects.
scope=pd.read_csv(ROOT/'data/transcript_scope.csv');ids=set(scope.loc[scope.any_gene_transcript_missense,'SPDI']);sens.append(dict(analysis='Primary predictions in transcript missense subset',**metrics(F[F.SPDI.isin(ids)])))
S=pd.DataFrame(sens);S.to_csv(TAB/'sensitivity_analyses.csv',index=False);summary['sensitivities']=S.to_dict('records')
# Deployment and panel-selection frequency.
obj=joblib.load(MOD/'deployment.joblib');panel=obj['panel'];freq=pd.Series([c for f in sorted(MOD.glob('cv_r*f*.joblib')) for c in joblib.load(f)['panel']]).value_counts()
paneltab=pd.DataFrame({'predictor':panel,'deployment_rank':range(1,len(panel)+1),'selected_outer_folds':[int(freq.get(c,0)) for c in panel]});paneltab['selection_frequency']=paneltab.selected_outer_folds/25;paneltab.to_csv(TAB/'deployment_panel.csv',index=False)
A[['SPDI','Gene','y']+panel].to_csv(DATA/'anchor_deployment_panel.csv',index=False)
B[['SPDI','Gene']+panel].to_csv(DATA/'application_deployment_panel.csv.gz',index=False)
summary['panel']=paneltab.to_dict('records');summary['deployment_parameters']={n:{k:v for k,v in obj['learners'][n].items() if k!='model'} for n in LEARNERS};summary['smac_parameters']=obj['smac']
summary['application']={'n':len(D),'evaluable':int(D.complete_flag.sum()),'group_counts':pd.Series(group(D.V)).value_counts().to_dict(),'state_counts':D.V.value_counts().sort_index().to_dict(),'observed_min':int(D.n_observed_panel.min()),'observed_median':float(D.n_observed_panel.median()),'panel_size':len(panel),'learner_positive_fractions':{n:float(D.loc[D.complete_flag==1,'vote_'+n].mean()) for n in LEARNERS}}
pd.crosstab(D.Gene,group(D.V)).reindex(GENES).to_csv(TAB/'application_by_gene.csv')
summary['mixed_among_evaluable']=proportion(int(F.V.between(1,3).sum()),int(F.complete_flag.sum()))
summary['mixed_fraction_ratio']=summary['application']['group_counts'].get('V1–V3',0)/int(D.complete_flag.sum())/summary['mixed_among_evaluable']['proportion']
# SMD on observed values, training and application missingness reported separately.
rows=[]
for c in panel:
 a=A[c].dropna();b=B[c].dropna();smd=(b.mean()-a.mean())/np.sqrt((a.var(ddof=1)+b.var(ddof=1))/2)
 rows.append(dict(predictor=c,SMD=smd,anchor_missing=A[c].isna().mean(),application_missing=B[c].isna().mean()))
shift=pd.DataFrame(rows);shift.to_csv(TAB/'feature_shift.csv',index=False);summary['shift']={'ge020':int((shift.SMD.abs()>=.2).sum()),'ge010':int((shift.SMD.abs()>=.1).sum()),'negative':int((shift.SMD<0).sum())}
# Review strata: 0-star conflicting kept distinguishable in source table.
rev=A[['SPDI','clinvar_review']].copy();rev['stratum']=rev.clinvar_review.map({'reviewed_by_expert_panel':'3-star','practice_guideline':'4-star','criteria_provided,_multiple_submitters,_no_conflicts':'2-star','criteria_provided,_single_submitter':'1-star','no_assertion_criteria_provided':'0-star','criteria_provided,_conflicting_classifications':'0-star'}).fillna('NR')
F=F.merge(rev[['SPDI','stratum']],on='SPDI');rr=[]
for (s,y),p in F.groupby(['stratum','y']):
 row={'review_stratum':s,'source_label':'LP/P' if y else 'B/LB','n':len(p),'n_evaluable':int(p.complete_flag.sum())};p=p[p.complete_flag==1]
 for name in LEARNERS:row[name+'_concordant']=int((p['vote_'+name]==y).sum())
 row['ensemble_concordant']=int(((p.V>=3).astype(int)==y).sum());rr.append(row)
RR=pd.DataFrame(rr);RR.to_csv(TAB/'review_status.csv',index=False);summary['review_status']=RR.to_dict('records')
# Explicit source-label-concordant subset, no selection based on model correctness.
labels={0:{'Benign','Likely_benign','Benign/Likely_benign'},1:{'Pathogenic','Likely_pathogenic','Pathogenic/Likely_pathogenic'}}
ids=set(A.loc[A.apply(lambda r:r.clinvar_clnsig in labels[r.y],axis=1),'SPDI']);summary['embedded_label_concordant_n']=len(ids)
lc=pd.DataFrame([dict(repeat=r,**metrics(p[p.SPDI.isin(ids)])) for r,p in P.groupby('repeat')]);lc.to_csv(TAB/'embedded_label_concordant.csv',index=False);summary['embedded_label_concordant']={'BA':float(lc.balanced_accuracy.mean()),'BA_sd':float(lc.balanced_accuracy.std()),'AUROC':float(lc.AUROC.mean()),'AUROC_sd':float(lc.AUROC.std())}
# Matched-record descriptive comparisons; each comparator may be a model input.
COMP={'REVEL_rankscore':'REVEL','MetaLR_rankscore':'MetaLR','VARITY_R_rankscore':'VARITY_R','BayesDel_addAF_rankscore':'BayesDel addAF','am_pathogenicity':'AlphaMissense'}
cr=[];resc={};maps=pd.read_csv(OUT/'fold_assignments.csv')
for c,name in COMP.items():
 cp=P.merge(A[['SPDI',c]],on='SPDI');cp=cp[(cp.complete_flag==1)&cp[c].notna()]
 for r,p in cp.groupby('repeat'):
  cr.append(dict(comparator=name,repeat=r,n=len(p),AUROC_HBOCpred=roc_auc_score(p.y,p.S_MAC),AUROC_comparator=roc_auc_score(p.y,p[c]),AUPRC_HBOCpred=average_precision_score(p.y,p.S_MAC),AUPRC_comparator=average_precision_score(p.y,p[c])))
 for part,p in cp.groupby('partition'):
  train=A[~A.SPDI.isin(maps.loc[maps.partition==part,'SPDI'])&A[c].notna()]
  thr,_=ba_threshold(train[c].to_numpy(),train.y.to_numpy())
  for _,row in p.iterrows():
   key=(name,row.SPDI);resc.setdefault(key,[]).append(int((int(row.V>=3)==row.y) and (int(row[c]>=thr)!=row.y)))
C=pd.DataFrame(cr);C.to_csv(TAB/'comparator_by_repeat.csv',index=False);CA=C.drop(columns='repeat').groupby('comparator').agg(['mean','std']);CA.to_csv(TAB/'comparator_summary.csv')
rt=[]
for c,name in COMP.items():
 for y in [0,1]:
  ids=A.loc[(A.y==y)&A[c].notna(),'SPDI'];k=sum(len(resc.get((name,i),[]))==5 and all(resc[(name,i)]) for i in ids);rt.append(dict(comparator=name,source_label='LP/P' if y else 'B/LB',rescued=k,denominator=len(ids)))
RT=pd.DataFrame(rt);RT.to_csv(TAB/'stable_rescue.csv',index=False);summary['stable_rescue']=RT.to_dict('records')
# Gene recoverability uses only the panel fitted on the corresponding outer-training data.
recover=[];prevout=[]
for f in range(1,6):
 ob=joblib.load(MOD/f'cv_r1f{f}.joblib');tr=A.SPDI.isin(ob['training_SPDI']);te=A.SPDI.isin(ob['test_SPDI'])
 xt=transform(ob,A.loc[tr,features]);xe=transform(ob,A.loc[te,features])
 m=ExtraTreesClassifier(n_estimators=300,random_state=20260714+f,n_jobs=1).fit(xt,A.loc[tr,'Gene'])
 pred=m.predict(xe);baseline=A.loc[tr,'Gene'].value_counts().index[0]
 recover.extend(dict(SPDI=s,gene=g,predicted_gene=p,majority_gene=baseline) for s,g,p in zip(A.loc[te,'SPDI'],A.loc[te,'Gene'],pred))
 prev=A.loc[tr].groupby('Gene').y.mean();scores=A.loc[te,'Gene'].map(prev).fillna(A.loc[tr,'y'].mean())
 prevout.extend(dict(SPDI=s,y=int(y),gene_prevalence_score=float(q)) for s,y,q in zip(A.loc[te,'SPDI'],A.loc[te,'y'],scores))
R=pd.DataFrame(recover);R.to_csv(OUT/'gene_recoverability_oof.csv',index=False);Q=pd.DataFrame(prevout);Q.to_csv(OUT/'gene_prevalence_baseline_oof.csv',index=False)
summary['gene_recoverability']={'accuracy':float((R.gene==R.predicted_gene).mean()),'majority_accuracy':float((R.gene==R.majority_gene).mean()),'gene_prevalence_AUROC':float(roc_auc_score(Q.y,Q.gene_prevalence_score))}
# Normalized JSON without NaN is suitable for documentation builders.
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,(np.integer,)):return int(x)
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
 return x
(TAB/'summary.json').write_text(json.dumps(clean(summary),indent=2,allow_nan=False))
print(json.dumps({k:summary[k] for k in ['fixed','logo','group_counts','application','gene_recoverability']},indent=2,default=str),flush=True)
