"""Verify row identities, fold isolation, saved-model replay, and completeness suppression."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,joblib
from hbocpred_core import predict_partition,LEARNERS
ROOT=Path(__file__).resolve().parents[1]
A=pd.read_csv(ROOT/'data/anchors_all_numeric.csv');B=pd.read_csv(ROOT/'data/application_all_numeric.csv.gz');P=pd.read_csv(ROOT/'outputs/oof_predictions_repeated_cv.csv');L=pd.read_csv(ROOT/'outputs/logo_predictions.csv')
assert len(A)==2160 and len(B)==43679 and A.SPDI.is_unique and B.SPDI.is_unique
assert not(set(A.SPDI)&set(B.SPDI));assert P.groupby('repeat').SPDI.nunique().eq(len(A)).all();assert len(P)==10800
assert L.SPDI.is_unique and set(L.SPDI)==set(A.SPDI)
maxerr=0;count=0
for path in sorted((ROOT/'models').glob('*.joblib')):
 ob=joblib.load(path);tag=ob['partition'];tr=set(ob['training_SPDI']);te=set(ob['test_SPDI'])
 if tag!='deployment':assert not tr&te
 if tag.startswith('logo_'):
  held=tag[len('logo_'):];assert not A[A.SPDI.isin(tr)].Gene.eq(held).any();assert A[A.SPDI.isin(te)].Gene.eq(held).all()
 if not tag.startswith('with_RI_'):assert 'Reliability_index' not in ob['columns'] and all('Reliability_index' not in v for v in ob['inner_eligible'])
 saved=pd.read_csv(ROOT/'outputs'/f'{tag}_predictions.csv',dtype={'vote_vector':str});x=A.set_index('SPDI').loc[saved.SPDI].reset_index();actual=predict_partition(ob,x)
 for c in ['S_MAC','Mean4']+['p_'+n for n in LEARNERS]+['vote_'+n for n in LEARNERS]+['V','n_observed_panel','complete_flag']:
  np.testing.assert_allclose(saved[c],actual[c],atol=1e-12,rtol=1e-10,equal_nan=True)
  diff=np.abs(saved[c].to_numpy()-actual[c].to_numpy());maxerr=max(maxerr,float(np.nanmax(diff)))
 for p,ids in zip(ob['inner_panels'],ob['inner_eligible']):assert set(p)<=set(ids)
 incomplete=saved.complete_flag==0;assert saved.loc[incomplete,['S_MAC','V','Mean4']].isna().all().all()
 assert saved.loc[~incomplete,[f'vote_{n}' for n in LEARNERS]].sum(axis=1).eq(saved.loc[~incomplete,'V']).all()
 count+=1
ob=joblib.load(ROOT/'models/deployment.joblib');actual=predict_partition(ob,B);saved=pd.read_csv(ROOT/'outputs/application_catalogue.csv.gz')
np.testing.assert_allclose(actual.S_MAC,saved.S_MAC,atol=1e-12,equal_nan=True);np.testing.assert_allclose(actual.V,saved.V,equal_nan=True)
# A real missing-annotation input must withhold scores, votes and state.
q=B.iloc[:1].copy();q.loc[:,ob['panel']]=np.nan;r=predict_partition(ob,q);assert r.complete_flag.iloc[0]==0;assert r[['V','S_MAC']].isna().all().all()
report={'saved_partition_models_replayed':count,'application_records_replayed':len(B),'maximum_numeric_replay_difference':maxerr,'original_reference_count':35,'manuscript_fields_checked_separately':True,'fold_isolation':'PASS','gene_holdout_isolation':'PASS','completeness_suppression':'PASS'}
(ROOT/'audit/model_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
