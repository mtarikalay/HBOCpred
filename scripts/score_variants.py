"""Score already aligned numeric features with the frozen R4 deployment object.
No online annotation, transcript inference or clinical classification is performed.
"""
from pathlib import Path
import argparse,joblib,pandas as pd
from hbocpred_core import predict_partition
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
d=pd.read_csv(a.input);o=joblib.load(ROOT/'models/deployment.joblib')
for c in o['columns']:
 if c not in d:d[c]=float('nan')
 d[c]=pd.to_numeric(d[c],errors='coerce')
r=predict_partition(o,d);identity=[c for c in ['SPDI','Gene','HGVSc','HGVSp','Feature','MANE_SELECT'] if c in d]
pd.concat([d[identity],r],axis=1).to_csv(a.output,index=False)
print(f'{len(r)} records; {int(r.complete_flag.sum())} evaluable; {int((r.complete_flag==0).sum())} incomplete')
