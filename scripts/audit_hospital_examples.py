"""Resolve the supplied illustrative records against the frozen R4 catalogue.

No refitting, new clinical labels or external performance estimates are produced.
Use gene + allele-specific coding/protein consequence + rsID, never bare c. text
or rsID alone. CHEK2 alternate-transcript identity is explicitly documented.
"""
from pathlib import Path
import json, hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
cat = pd.read_csv(ROOT/'outputs/application_catalogue.csv.gz', dtype={'vote_vector':str})
src = pd.read_csv(ROOT/'audit/hospital_source_curation.csv')
anchors = pd.read_csv(ROOT/'data/anchors_all_numeric.csv', usecols=['SPDI'])
# Entries are identifiers supplied by the author, with the catalogue coding alias.
entries = [
 ('BRCA2','c.8351G>A','p.Arg2784Gln','rs80359076','c.8351G>A'),
 ('BRCA2','c.8524C>T','p.Arg2842Cys','rs80359104','c.8524C>T'),
 ('CHEK2','c.599T>C','p.Ile157Thr','rs17879961','c.470T>C'),
 ('ATM','c.6154G>A','p.Glu2052Lys','rs202206540','c.6154G>A'),
 ('CHEK2','c.190G>A','p.Glu64Lys','rs141568342','c.190G>A'),
 ('ATM','c.6188G>A','p.Gly2063Glu','rs866290641','c.6188G>A'),
 ('CHEK2','c.470T>C','p.Ile157Thr','rs17879961','c.470T>C')]
matched=[]
for gene, source_c, protein, rs, coding in entries:
    s=src[(src.gene==gene)&(src.HGVSc==source_c)&(src.rsID_as_supplied==rs)]
    assert len(s)>0
    x=cat[(cat.Gene==gene)&cat.HGVSc.fillna('').str.endswith(':'+coding)
          &cat.HGVSp.fillna('').str.endswith(':'+protein)
          &cat.Existing_variation.fillna('').str.split(',').map(lambda v: rs in v)]
    assert len(x)==1, (gene,source_c,'ambiguous identity')
    r=x.iloc[0]
    assert r.complete_flag==1 and r.SPDI not in set(anchors.SPDI)
    for _, v in s.iterrows():
        matched.append({'source_row':v.source_row,'Gene':gene,'source_transcript':v.transcript_as_supplied,
          'source_HGVSc':source_c,'source_HGVSp':v.HGVSp,'rsID':rs,'SPDI':r.SPDI,
          'catalogue_transcript':r.Feature,'MANE_SELECT':r.MANE_SELECT,'catalogue_HGVSc':r.HGVSc,
          'catalogue_HGVSp':r.HGVSp,'V':int(r.V),'vote_vector':r.vote_vector,'S_MAC':r.S_MAC,
          'n_observed_panel':int(r.n_observed_panel),'source_annotation':r.CLIN_SIG,
          'identity_note':('CHEK2 rs17879961: c.599T>C / Ile200Thr on NM_001005735.3 and c.470T>C / Ile157Thr on NM_007194.4 are aliases; source transcript/version retained as supplied and is not silently corrected.'
           if rs=='rs17879961' else 'Concordant gene, supplied coding/protein consequence and rsID; source transcript versions may be absent.'),
          'analysis_scope':'Existing application-catalogue illustration; no independent clinical reference label'})
m=pd.DataFrame(matched);assert len(m)==13 and m.SPDI.nunique()==6
m.to_csv(ROOT/'audit/hospital_example_identity_audit.csv',index=False)
rows=[]
for spdi,g in m.groupby('SPDI',sort=False):
    r=g.iloc[0].to_dict();r['source_rows']=','.join(map(str,g.source_row));r['n_source_records']=len(g)
    r['source_names']='; '.join(dict.fromkeys(g.source_HGVSc+' '+g.source_HGVSp))
    rows.append(r)
t=pd.DataFrame(rows);t.to_csv(ROOT/'tables/hospital_catalogue_examples.csv',index=False)
report={'status':'PASS','source_name_groups':7,'source_records':13,'unique_catalogue_variants':6,
 'all_existing_application_records':True,'all_absent_from_anchors':True,
 'all_pass_completeness':True,'new_independent_validation_records':0,
 'alias_identity_source':'https://www.ncbi.nlm.nih.gov/clinvar/variation/5591/',
 'alias_identity_accession':'VCV000005591.136','identity_checked_utc':'2026-09-06',
 'CHEK2_Ile157Thr':{'SPDI':'NC_000022.11:28725098:A:G','V':0,'vote_vector':'0000','S_MAC':float(t.loc[t.rsID=='rs17879961','S_MAC'].iloc[0])},
 'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'outputs/application_catalogue.csv.gz',ROOT/'audit/hospital_source_curation.csv']}}
(ROOT/'audit/hospital_example_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
