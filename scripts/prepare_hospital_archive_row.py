"""Recreate the additional non-anchor numeric row used in the hospital audit.
Usage: python scripts/prepare_hospital_archive_row.py --training SOURCE.xlsx
This uses the same source parser as prepare_inputs.py; it does not fit a model.
"""
from pathlib import Path
import argparse,hashlib,json,pandas as pd
from prepare_inputs import parse,DS
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--training',required=True);args=p.parse_args()
a=pd.read_csv(ROOT/'data/anchors_all_numeric.csv')
d=pd.read_excel(args.training)
h=pd.read_csv(ROOT/'tables/hospital_all_in_scope.csv')
ids=h.loc[h.record_origin=='Archive','SPDI']
s=d[d.SPDI.isin(ids)].copy();assert set(s.SPDI)==set(ids) and s.SPDI.is_unique
for c in DS:s[c]=s[c].map(parse)
s['SpliceAI_DS_max']=s[DS].max(axis=1)
metadata=['SPDI','Location','Gene','ACMG_variations','clinvar_id','clinvar_hgvs','clinvar_clnsig','clinvar_review','y']
for c in a:
 if c not in s:s[c]=float('nan')
 if c not in metadata:s[c]=s[c].map(parse)
out=ROOT/'data/hospital_additional_training_numeric.csv'
s[a.columns].to_csv(out,index=False)
report={'source_name':Path(args.training).name,'source_sha256':hashlib.sha256(Path(args.training).read_bytes()).hexdigest(),'records':s.SPDI.tolist(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parser':'first finite numeric token, as in prepare_inputs.py; SpliceAI_DS_max across four DS fields','new_reference_labels':False,'new_fits':0}
(ROOT/'audit/hospital_numeric_source.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
