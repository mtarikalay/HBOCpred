"""Build numeric matrices from the supplied source files without application-based selection.
Usage: python scripts/prepare_inputs.py --training FILE.xlsx --vous FILE.zip
The positional first-numeric parser is retained for source comparability; it is not
claimed to align every dbNSFP multi-transcript value with the VEP transcript.
"""
import argparse,re,json,zipfile,hashlib
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
GENES=['BRCA1','BRCA2','PALB2','ATM','CHEK2','TP53','PTEN','CDH1','STK11','BARD1','BRIP1','RAD51C','RAD51D','NBN','BLM','FANCA','FANCC']
IDS=['No','SPDI','Location','Gene','ACMG_variations','genename','clinvar_clnsig','clinvar_hgvs','clinvar_id','clinvar_review','clinvar_trait','Uniprot_acc','Uniprot_entry','Interpro_domain','Denisova']
DS=['SpliceAI_pred_DS_AG','SpliceAI_pred_DS_AL','SpliceAI_pred_DS_DG','SpliceAI_pred_DS_DL']
DP=['SpliceAI_pred_DP_AG','SpliceAI_pred_DP_AL','SpliceAI_pred_DP_DG','SpliceAI_pred_DP_DL']
DEFINITE=['Likely_benign','Likely_pathogenic','Pathogenic/Likely_pathogenic','Benign/Likely_benign','Benign','Pathogenic']
SEMANTIC_DROP=['BayesDel_addAF_score','BayesDel_noAF_score','ClinPred_score','ClinPred','DANN_score','DEOGEN2_score','ESM1b_score','Eigen-PC-phred_coding','Eigen-PC-raw_coding','Eigen-phred_coding','Eigen-raw_coding','GERP++_NR','GERP++_RS','GERP_91_mammals','LIST-S2_score','MPC_score','MVP_score','MetaLR_score','MetaRNN_score','MetaSVM_score','MutFormer_score','MutPred2_score','MutationAssessor_score','PHACTboost_score','PROVEAN_score','PrimateAI_score','REVEL_score','REVEL','VARITY_ER_LOO_score','VARITY_ER_score','VARITY_R_LOO_score','VARITY_R_score','bStatistic','fathmm-XF_coding_score','gMVP_score','phastCons100way_vertebrate','phastCons17way_primate','phastCons470way_mammalian','phyloP100way_vertebrate','phyloP17way_primate','phyloP470way_mammalian','CADD_RAW']
def parse(v):
 if pd.isna(v):return np.nan
 for s in re.split('[,;]',str(v)):
  try:
   f=float(s)
   if np.isfinite(f):return f
  except ValueError:pass
 return np.nan
def numeric(d,cols):
 x=d[cols].map(parse);x['SpliceAI_DS_max']=x[DS].max(axis=1)
 return x.drop(columns=DS+DP)
def main(training,vous):
 d=pd.read_excel(training);a=d[d.Gene.isin(GENES)&d.ACMG_variations.isin(['LP','LB'])].reset_index(drop=True)
 cols=[c for c in a if c not in IDS and not c.endswith('_pred') and c!='EVE_CLASS']
 x=numeric(a,cols);meta=a[['SPDI','Location','Gene','ACMG_variations','clinvar_id','clinvar_hgvs','clinvar_clnsig','clinvar_review']].copy();meta['y']=(a.ACMG_variations=='LP').astype(int)
 A=pd.concat([meta,x],axis=1);A.to_csv(ROOT/'data/anchors_all_numeric.csv',index=False)
 parts=[]
 with zipfile.ZipFile(vous) as z:
  member='hcs_ensembl_VOUS.txt'
  for v in pd.read_csv(z.open(member),sep='\t',chunksize=10000,low_memory=False):
   m=v[v.SYMBOL.isin(GENES)&v.Consequence.str.contains('missense_variant',na=False)&~v.clinvar_clnsig.isin(DEFINITE)].reset_index(drop=True)
   if len(m):
    mb=m[['#Uploaded_variation','Location','SYMBOL','Feature','MANE_SELECT','Consequence','HGVSc','HGVSp','Existing_variation','CLIN_SIG','clinvar_clnsig','clinvar_review','clinvar_id']].rename(columns={'#Uploaded_variation':'SPDI','SYMBOL':'Gene'})
    parts.append(pd.concat([mb,numeric(m,cols)],axis=1))
 B=pd.concat(parts,ignore_index=True);B.to_csv(ROOT/'data/application_all_numeric.csv.gz',index=False)
 features=[c for c in x.columns if c not in SEMANTIC_DROP]
 (ROOT/'data/candidate_features.json').write_text(json.dumps(features,indent=2))
 # All original training IDs, including labels other than LP/LB, support broader overlap checks.
 d[['SPDI','Gene','ACMG_variations']].to_csv(ROOT/'audit/full_training_identity.csv',index=False)
 report={'anchors':len(A),'anchor_label_counts':A.y.value_counts().to_dict(),'application':len(B),'numeric_fields_before_aggregation':len(cols),'numeric_after_aggregation':len(x.columns),'semantic_candidates_including_reliability':len(features),'semantic_candidates_primary':len(features)-1,'source_training_sha256':hashlib.sha256(Path(training).read_bytes()).hexdigest(),'source_vous_sha256':hashlib.sha256(Path(vous).read_bytes()).hexdigest(),'anchor_application_exact_overlap':len(set(A.SPDI)&set(B.SPDI)),'application_MANE_SELECT_populated':int(B.MANE_SELECT.notna().sum()),'parser':'first finite numeric token; no transcript-aware remapping inferred','missingness_selection':'none at matrix construction; applied within each training partition'}
 (ROOT/'audit/input_manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--training',required=True);p.add_argument('--vous',required=True);a=p.parse_args();main(a.training,a.vous)
