"""Execute the audited R4 analysis. Model fits are checkpointed per partition.
python scripts/run_analysis.py --jobs 6 [--stages cv logo deployment sensitivity]
A completed object is reused only under the current source/input SHA256 signature.
"""
import os,sys,json,time,hashlib,argparse
from pathlib import Path
import numpy as np,pandas as pd,joblib
from concurrent.futures import ProcessPoolExecutor,as_completed
from sklearn.model_selection import StratifiedKFold,LeaveOneGroupOut
from hbocpred_core import *
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data';OUT=ROOT/'outputs';MOD=ROOT/'models'
SEED_DATA=20260723;SEED_MODEL=20260714

def signature():
 h=hashlib.sha256()
 for p in [Path(__file__),Path(__file__).with_name('hbocpred_core.py'),Path(__file__).with_name('legacy_r3_core.py'),DATA/'anchors_all_numeric.csv',DATA/'candidate_features.json']:
  h.update(p.read_bytes())
 return h.hexdigest()

def task_worker(task):
 kind,tag,tr,te,seed,exclude=task
 d=pd.read_csv(DATA/'anchors_all_numeric.csv');features=json.loads((DATA/'candidate_features.json').read_text())
 X=d[features];yp=d.y.to_numpy();g=d.Gene.to_numpy()
 model=MOD/f'{tag}.joblib';pred=OUT/f'{tag}_predictions.csv';sig=signature()
 if model.exists() and pred.exists():
  ob=joblib.load(model)
  if ob.get('analysis_signature')==sig:return tag,'cached'
 start=time.time();o=fit_partition(X.iloc[tr],yp[tr],g[tr],seed,exclude=exclude)
 o['training_SPDI']=d.SPDI.iloc[tr].tolist();o['test_SPDI']=d.SPDI.iloc[te].tolist();o['analysis_signature']=sig;o['partition']=tag
 joblib.dump(o,model,compress=3)
 if kind=='deployment':
  app=pd.read_csv(DATA/'application_all_numeric.csv.gz');P=predict_partition(o,app)
  P=pd.concat([app[[c for c in app if c not in features]],P],axis=1)
  P.to_csv(OUT/'application_catalogue.csv.gz',index=False)
  P=predict_partition(o,X);P=pd.concat([d[['SPDI','Gene','y']],P],axis=1);P['evaluation']='deployment_in_sample_not_validation'
 else:
  P=predict_partition(o,X.iloc[te]);P=pd.concat([d.iloc[te][['SPDI','Gene','y']],P],axis=1)
 P['partition']=tag;P.to_csv(pred,index=False)
 (OUT/f'{tag}_fit_audit.json').write_text(json.dumps({'signature':sig,'seconds':time.time()-start,'panel':o['panel'],'eligible':o['columns'],'inner_panels':o['inner_panels'],'inner_eligible':o['inner_eligible'],'n_train':len(tr),'n_test':len(te),'excluded':list(exclude),'training_SPDI':o['training_SPDI'],'inner_fold_id':o['inner_fold_id'].tolist(),'parameters':{n:{k:v for k,v in o['learners'][n].items() if k!='model'} for n in LEARNERS}},indent=2))
 return tag,round(time.time()-start,1)

def build_tasks(stages):
 d=pd.read_csv(DATA/'anchors_all_numeric.csv');key=stratum_key(d.Gene,d.y,min_n=5);tasks=[];fold_rows=[]
 for r in range(5):
  for f,(tr,te) in enumerate(StratifiedKFold(5,shuffle=True,random_state=SEED_DATA+r).split(d,key)):
   tag=f'cv_r{r+1}f{f+1}'
   fold_rows.extend({'SPDI':d.SPDI.iloc[i],'repeat':r+1,'outer_fold':f+1,'partition':tag} for i in te)
   if 'cv' in stages:tasks.append(('cv',tag,tr,te,SEED_MODEL+100*r+f,('Reliability_index',)))
   if r==0 and 'sensitivity' in stages:
    tasks.append(('sensitivity',f'with_RI_f{f+1}',tr,te,SEED_MODEL+f,()))
    tasks.append(('sensitivity',f'without_addAF_AlphaMissense_f{f+1}',tr,te,SEED_MODEL+f,('Reliability_index','BayesDel_addAF_rankscore','am_pathogenicity')))
    scope=pd.read_csv(ROOT/'audit/transcript_scope_audit.csv').set_index('SPDI')
    allowed=d.SPDI.map(scope.any_gene_transcript_missense).fillna(False).to_numpy()
    tasks.append(('sensitivity',f'current_missense_f{f+1}',tr[allowed[tr]],te[allowed[te]],SEED_MODEL+f,('Reliability_index',)))
 if 'logo' in stages:
  for i,(tr,te) in enumerate(LeaveOneGroupOut().split(d,d.y,d.Gene)):
   gene=d.Gene.iloc[te[0]];tasks.append(('logo',f'logo_{gene}',tr,te,SEED_MODEL+10000+i,('Reliability_index',)))
 if 'deployment' in stages:tasks.append(('deployment','deployment',np.arange(len(d)),np.arange(len(d)),SEED_MODEL+20000,('Reliability_index',)))
 pd.DataFrame(fold_rows).to_csv(OUT/'fold_assignments.csv',index=False)
 return tasks

def main():
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=6);p.add_argument('--stages',nargs='+',default=['cv','logo','deployment','sensitivity']);p.add_argument('--limit',type=int);a=p.parse_args()
 tasks=build_tasks(a.stages)
 if a.limit:tasks=tasks[:a.limit]
 print('START',time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'tasks',len(tasks),'signature',signature(),flush=True)
 failures=[]
 with ProcessPoolExecutor(max_workers=a.jobs) as pool:
  futs={pool.submit(task_worker,t):t[1] for t in tasks}
  for fut in as_completed(futs):
   try:print('DONE',*fut.result(),flush=True)
   except Exception as e:
    import traceback;failures.append(futs[fut]);print('FAILED',futs[fut],repr(e),traceback.format_exc(),flush=True)
 if failures:raise RuntimeError(f'Failed partitions: {failures}')
 print('COMPLETE',time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),flush=True)
if __name__=='__main__':main()
