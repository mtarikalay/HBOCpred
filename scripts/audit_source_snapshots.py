"""Recheck source audits using distributed response snapshots, without live API changes.
The snapshots retain frequency query evidence and transcript consequences, not
colocated clinical assertions. They are not independent clinical reference labels.
"""
from pathlib import Path
import gzip,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'audit/cache'
def key(s):
 a,p,r,v=s.split(':');return f'{int(a.split(".")[0].replace("NC_",""))}-{int(p)+1}-{r}-{v}'
def vk(v):
 t=v['input'].split();r,a=t[3].split('/');return f'{t[0]}-{t[1]}-{r}-{a}'
def read(n):return json.loads(gzip.decompress((CACHE/n).read_bytes()))
A=pd.read_csv(ROOT/'data/anchors_all_numeric.csv');old=pd.read_csv(ROOT/'audit/transcript_scope_audit.csv').set_index('SPDI');vep={vk(v):v for v in read('anchor_transcripts.json.gz')};rows=[]
for _,r in A.iterrows():
 v=vep[key(r.SPDI)];ts=[t for t in v.get('transcript_consequences',[]) if t.get('gene_symbol')==r.Gene]
 miss=any('missense_variant' in t.get('consequence_terms',[]) for t in ts);mane=any(t.get('mane_select') and 'missense_variant' in t.get('consequence_terms',[]) for t in ts)
 assert miss==old.loc[r.SPDI,'any_gene_transcript_missense'];assert mane==old.loc[r.SPDI,'MANE_missense']
 rows.append({'SPDI':r.SPDI,'Gene':r.Gene,'any_gene_transcript_missense':miss,'MANE_missense':mane})
pd.DataFrame(rows).to_csv(ROOT/'audit/rechecked_transcript_scope.csv',index=False)
train=set(pd.read_csv(ROOT/'audit/full_training_identity.csv').SPDI.map(key));app=set(pd.read_csv(ROOT/'data/application_all_numeric.csv.gz',usecols=['SPDI']).SPDI.map(key));anchors=set(A.SPDI.map(key));got=[]
for d in read('gnomAD_gene_queries.json.gz'):
 g=d['response']['data']['gene']
 for v in g['variants']:
  if v['consequence']!='missense_variant' or any(len(a)!=1 for a in v['variant_id'].split('-')[2:]):continue
  hit=[]
  for cs in ['exome','genome']:
   x=v[cs]
   if not x or x['filters']:continue
   for p in x['populations']:
    if p['id'] in ['afr','amr','eas','nfe','sas','mid'] and p['an']>=2000 and p['ac']/p['an']>.05:hit.append([cs,p['id'],p['ac'],p['an'],p['ac']/p['an']])
  if hit:got.append(dict(gene=g['symbol'],variant_id=v['variant_id'],in_any_training_record=v['variant_id'] in train,in_application_catalogue=v['variant_id'] in app,in_HBOC_anchors=v['variant_id'] in anchors,qualifying_populations=json.dumps(hit)))
g=pd.DataFrame(got);ref=pd.read_csv(ROOT/'audit/gnomAD_candidates.csv').set_index('variant_id');assert set(g.variant_id)==set(ref.index)
for _,r in g.iterrows():
 for k in ['in_any_training_record','in_application_catalogue','in_HBOC_anchors']:assert r[k]==ref.loc[r.variant_id,k]
gv={vk(v):v for v in read('gnomAD_candidate_transcripts.json.gz')}
for _,r in ref.reset_index().iterrows():
 ts=[t for t in gv[r.variant_id].get('transcript_consequences',[]) if t.get('gene_symbol')==r.gene]
 assert any('missense_variant' in t.get('consequence_terms',[]) for t in ts)==r.any_gene_transcript_missense
 assert any(t.get('mane_select') and 'missense_variant' in t.get('consequence_terms',[]) for t in ts)==r.MANE_missense
pd.DataFrame(got).to_csv(ROOT/'audit/rechecked_gnomAD_screen.csv',index=False)
report={'anchor_rows':len(rows),'current_same_gene_missense':sum(r['any_gene_transcript_missense'] for r in rows),'MANE_missense':sum(r['MANE_missense'] for r in rows),'gnomAD_candidates':len(g),'full_training_overlap':int(g.in_any_training_record.sum()),'application_overlap':int(g.in_application_catalogue.sum()),'anchor_overlap':int(g.in_HBOC_anchors.sum()),'status':'PASS: source query and transcript results replayed'}
(ROOT/'audit/source_snapshot_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
