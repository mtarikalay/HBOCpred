"""Audit every source row and score every resolved in-scope allele with frozen R4.
Replays from released matrices and transcript snapshots; no fitting or outcome
adjudication. Source records are retained, including exclusions and discrepancies.
"""
from pathlib import Path
from collections import defaultdict
import gzip,json,re,hashlib
import pandas as pd,numpy as np,joblib
from hbocpred_core import predict_partition
ROOT=Path(__file__).resolve().parents[1]
def key(s):
 a,p,r,v=s.split(':');return f'{int(a.split(".")[0].replace("NC_",""))}-{int(p)+1}-{r}-{v}'
def vk(v):
 t=v['input'].split();r,a=t[3].split('/');return f'{t[0]}-{t[1]}-{r}-{a}'
def prot(s):return str(s).replace('(','').replace(')','').split(':')[-1]
def cds(s):return str(s).split(':')[-1]
def base(s):return str(s).split('.')[0]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 src=pd.read_csv(ROOT/'audit/hospital_source_curation.csv',keep_default_na=False)
 A=pd.read_csv(ROOT/'data/anchors_all_numeric.csv');B=pd.read_csv(ROOT/'data/application_all_numeric.csv.gz');T=pd.read_csv(ROOT/'data/hospital_additional_training_numeric.csv')
 app=pd.read_csv(ROOT/'outputs/application_catalogue.csv.gz',dtype={'vote_vector':str})
 full=pd.read_csv(ROOT/'audit/full_training_identity.csv')
 # Identify only exact genomic alleles, never all alternatives sharing an rsID.
 lookup={key(s):s for s in pd.concat([A.SPDI,B.SPDI,T.SPDI])}
 idx=defaultdict(list);byspdi=defaultdict(list)
 snapshots=json.load(gzip.open(ROOT/'audit/cache/anchor_transcripts.json.gz','rt'))
 extras=json.load(gzip.open(ROOT/'audit/cache/hospital_additional_transcripts.json.gz','rt'))
 for e in extras:
  snapshots.extend(e.get('data',[]))
 for obj in snapshots:
  spdi=lookup.get(vk(obj))
  if not spdi:continue
  for t in obj.get('transcript_consequences',[]):
   if 'missense_variant' not in t.get('consequence_terms',[]):continue
   d={'SPDI':spdi,'Gene':t.get('gene_symbol'),'HGVSc':t.get('hgvsc',''),'HGVSp':t.get('hgvsp',''),'MANE_SELECT':t.get('mane_select',''),'Feature':t.get('transcript_id',''),'identity_source':'Ensembl VEP response snapshot'}
   idx[(d['Gene'],cds(d['HGVSc']),prot(d['HGVSp']))].append(d);byspdi[spdi].append(d)
 for _,r in app.iterrows():
  d={k:r[k] for k in ['SPDI','Gene','HGVSc','HGVSp','MANE_SELECT','Feature']};d['identity_source']='Frozen application annotation'
  idx[(d['Gene'],cds(d['HGVSc']),prot(d['HGVSp']))].append(d);byspdi[r.SPDI].append(d)
 rows=[]
 for _,s in src.iterrows():
  row=s.to_dict();row.update({'matched_SPDI':'','identity_status':'OUTSIDE_17_GENES','identity_note':'Gene outside the prespecified 17-gene scope; not scored.'})
  if s.in_17_gene_scope:
   hits=idx[(s.gene,s.HGVSc,prot(s.HGVSp))]
   preferred=[h for h in hits if h['MANE_SELECT'] and base(h['MANE_SELECT'])==base(s.transcript_as_supplied)]
   # A matching named RefSeq/MANE transcript resolves otherwise ambiguous bare HGVS.
   if preferred:hits=preferred
   ids=set(h['SPDI'] for h in hits)
   row['candidate_SPDIs']='; '.join(sorted(ids))
   if len(ids)==1:
    spdi=ids.pop();h=next(h for h in hits if h['SPDI']==spdi)
    row.update({'matched_SPDI':spdi,'identity_status':'RESOLVED','matched_HGVSc':h['HGVSc'],'matched_HGVSp':h['HGVSp'],'matched_transcript':h['Feature'],'identity_source':h['identity_source'],'identity_note':'Same-gene, coding-allele and protein match; available source RefSeq/MANE transcript used for disambiguation. Original source strings retained.'})
   else:
    row.update({'identity_status':'AMBIGUOUS' if ids else 'UNRESOLVED','identity_note':'No unique allele-level match; prediction withheld.'})
  rows.append(row)
 audit=pd.DataFrame(rows)
 resolved=audit[(audit.identity_status=='RESOLVED')]
 chosen=[];metas=[]
 for spdi,g in resolved.groupby('matched_SPDI',sort=False):
  s=g.iloc[0];candidates=byspdi[spdi];m=[d for d in candidates if d['Gene']==s.gene and d['MANE_SELECT']]
  desc=m[0] if m else next(d for d in candidates if d['Gene']==s.gene)
  if spdi in set(A.SPDI):d=A[A.SPDI==spdi];origin='Anchor';label=d.iloc[0].ACMG_variations
  elif spdi in set(B.SPDI):d=B[B.SPDI==spdi];origin='Catalogue';label=''
  else:d=T[T.SPDI==spdi];origin='Archive';label=''
  assert len(d)==1
  chosen.append(d.iloc[0]);metas.append({'SPDI':spdi,'Gene':s.gene,'HGVSc':desc['HGVSc'],'HGVSp':desc['HGVSp'],'MANE_SELECT':desc['MANE_SELECT'],'Feature':desc['Feature'],'n_source_records':len(g),'source_rows':','.join(g.source_row.astype(str)),'source_names':'; '.join(dict.fromkeys(g.HGVSc+' '+g.HGVSp)),'source_transcripts':'; '.join(dict.fromkeys(g.transcript_as_supplied)),'source_rsIDs':'; '.join(dict.fromkeys(x for x in g.rsID_as_supplied if re.fullmatch(r'rs\d+',x,re.I))),'record_origin':origin,'overlaps_anchors':spdi in set(A.SPDI),'overlaps_full_training_archive':spdi in set(full.SPDI),'overlaps_application_catalogue':spdi in set(B.SPDI),'anchor_source_label':label,'clinical_reference_status':'Not adjudicated'})
 X=pd.DataFrame(chosen).reset_index(drop=True);meta=pd.DataFrame(metas)
 obj=joblib.load(ROOT/'models/deployment.joblib')
 pred=predict_partition(obj,X)
 result=pd.concat([meta,pred],axis=1)
 result['prediction_context']='Frozen deployment model; anchor overlap is in-sample; no external performance estimate'
 # Keep a separate pre-existing OOF record for every anchor overlap.
 oof=pd.read_csv(ROOT/'outputs/oof_predictions_repeated_cv.csv',dtype={'vote_vector':str})
 oof[oof.SPDI.isin(result.loc[result.overlaps_anchors,'SPDI'])].to_csv(ROOT/'outputs/hospital_anchor_oof_records.csv',index=False)
 result.to_csv(ROOT/'tables/hospital_all_in_scope.csv',index=False)
 pd.concat([meta[['SPDI','Gene']],X[obj['columns']]],axis=1).to_csv(ROOT/'data/hospital_scoring_numeric.csv',index=False)
 for _,r in result.iterrows():
  mask=audit.matched_SPDI==r.SPDI
  for c in ['record_origin','overlaps_anchors','overlaps_full_training_archive','overlaps_application_catalogue','n_observed_panel','complete_flag','vote_vector','V','S_MAC']:
   audit.loc[mask,c]=str(r[c])
  audit.loc[mask,'prediction_status']='SCORED: frozen deployment; reference outcome not adjudicated' if r.complete_flag else 'INCOMPLETE: fewer than 20/25 predictors observed'
 for k,g in resolved.groupby(['gene','HGVSc','HGVSp']):
  rids=set(x.lower() for x in g.rsID_as_supplied if re.fullmatch(r'rs\d+',x,re.I))
  if len(rids)>1:audit.loc[audit.source_row.isin(g.source_row),'identity_note']+=' Source rsIDs disagree within this description; they were not used to override the coding/protein match.'
 audit.loc[audit.identity_status=='OUTSIDE_17_GENES','prediction_status']='NOT SCORED: gene outside prespecified scope'
 audit.to_csv(ROOT/'audit/hospital_all_rows_audit.csv',index=False)
 # Check unchanged catalogue results and all original source rows.
 c=result[result.overlaps_application_catalogue].merge(app[['SPDI','S_MAC','V','vote_vector']],on='SPDI',suffixes=('','_catalogue'))
 delta=float(np.max(np.abs(c.S_MAC-c.S_MAC_catalogue))) if len(c) else 0.
 assert delta<1e-12 and (c.V==c.V_catalogue).all() and (c.vote_vector==c.vote_vector_catalogue).all()
 assert len(audit)==len(src) and audit.source_row.is_unique
 assert int(result.n_source_records.sum())==len(resolved)
 assert result.SPDI.is_unique
 rpt={'status':'PASS','source_rows':len(src),'out_of_scope_source_rows':int((~src.in_17_gene_scope).sum()),'in_scope_source_rows':int(src.in_17_gene_scope.sum()),'source_coding_protein_groups_in_scope':int(src[src.in_17_gene_scope][['gene','HGVSc','HGVSp']].drop_duplicates().shape[0]),'resolved_source_rows':len(resolved),'unresolved_or_ambiguous_source_rows':int(src.in_17_gene_scope.sum()-len(resolved)),'unique_in_scope_genomic_variants':len(result),'record_origins':result.record_origin.value_counts().to_dict(),'scored_variants':int(result.complete_flag.sum()),'incomplete_variants':int((result.complete_flag==0).sum()),'V_counts':result.V.value_counts().sort_index().to_dict(),'catalogue_max_score_difference':delta,'all_source_rows_retained':True,'new_fits':0,'clinical_reference_labels_adjudicated':0,'independent_external_performance_estimates':0,'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'audit/hospital_source_curation.csv',ROOT/'models/deployment.joblib',ROOT/'data/hospital_additional_training_numeric.csv',ROOT/'audit/cache/hospital_additional_transcripts.json.gz']}}
 (ROOT/'audit/hospital_full_verification.json').write_text(json.dumps(rpt,indent=2));print(json.dumps(rpt,indent=2))
 print(result[['Gene','HGVSc','HGVSp','record_origin','n_source_records','n_observed_panel','vote_vector','V','S_MAC']].to_string(index=False))
if __name__=='__main__':main()
