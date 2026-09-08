"""Publication figures, regenerated only from R4 numerical outputs; 600-dpi PNG + PDF."""
from pathlib import Path
import json,io,os,numpy as np,pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
from matplotlib.ticker import FuncFormatter
from sklearn.metrics import roc_curve,precision_recall_curve
from hbocpred_core import LEARNERS,wilson
ROOT=Path(__file__).resolve().parents[1];T=ROOT/'tables';F=ROOT/'figures';O=ROOT/'outputs';F.mkdir(exist_ok=True)
s=json.loads((T/'summary.json').read_text());P=pd.read_csv(O/'oof_predictions_repeated_cv.csv');p=P[P.repeat==1];A=pd.read_csv(O/'application_catalogue.csv.gz');g=pd.read_csv(T/'per_gene_held_out.csv')
BLUE='#245f95';RED='#ad5058';TEAL='#328a7a';GREY='#9aa6af';GOLD='#d39a40';DARK='#243744'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'xtick.labelsize':8.5,'ytick.labelsize':8.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def title(ax,t):ax.set_title(t,loc='left',fontweight='bold',pad=10)
def save(fig,name):
 raw=io.BytesIO();fig.savefig(raw,format='png',dpi=600,bbox_inches='tight',facecolor='white')
 im=Image.open(io.BytesIO(raw.getvalue())).convert('RGB');buf=io.BytesIO();im.save(buf,format='PNG',dpi=(600,600))
 Image.open(io.BytesIO(buf.getvalue())).verify()
 tmp=F/(name+'.png.tmp');tmp.write_bytes(buf.getvalue());os.replace(tmp,F/(name+'.png'))
 pdf=io.BytesIO();fig.savefig(pdf,format='pdf',bbox_inches='tight',facecolor='white');tmp=F/(name+'.pdf.tmp');tmp.write_bytes(pdf.getvalue());os.replace(tmp,F/(name+'.pdf'));plt.close(fig)
def pct(k,n):return 100*k/n if n else np.nan
# Figure 1: preserve the source blue/green model-to-application visual vocabulary.
fig,ax=plt.subplots(figsize=(8.4,7.1));ax.set_xlim(0,100);ax.set_ylim(0,100);ax.axis('off')
def box(x,y,w,h,head,body,col):
 ax.add_patch(Rectangle((x,y),w,h,fc='#edf3f9' if col==BLUE else '#edf6f1',ec=col,lw=1.2));ax.text(x+w/2,y+h-2,head,ha='center',va='top',fontsize=8 if w<30 else 9,fontweight='bold',color=col);ax.text(x+w/2,y+2,body,ha='center',va='bottom',fontsize=8,linespacing=1.45,color=DARK)
def ar(x1,y1,x2,y2):ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,color=BLUE,lw=1.2))
ax.add_patch(Rectangle((0,40),4,59,fc=BLUE));ax.text(2,70,'A   MODEL DEVELOPMENT',rotation=90,color='white',ha='center',va='center',fontweight='bold')
ax.add_patch(Rectangle((0,0),4,37,fc=TEAL));ax.text(2,18,'B   APPLICATION',rotation=90,color='white',ha='center',va='center',fontweight='bold')
box(8,86,62,13,'Source-labelled development archive','2,160 variants across 17 genes\n1,187 B/LB and 973 LP/P',BLUE)
box(8,69,62,13,'Training-only feature construction','47 semantic candidates; Reliability_index excluded\nMissingness screen, imputation and scaling within training',BLUE)
box(8,49,62,16,'Repeated nested cross-validation','5 repeats × 5 outer folds; 4 inner folds\nFeature selection refitted inside each inner-training fold\nSVM–RBF · L2 logistic · Extra Trees · HistGB',BLUE)
box(75,69,24,13,'Gene-held-out audit','17 whole-gene holdouts\nPer-gene estimates',BLUE)
box(75,49,24,16,'Sensitivity analyses','Reliability_index inclusion\naddAF + AlphaMissense\nexclusion; transcript scope',BLUE)
box(8,27,62,13,'Frozen deployment model','25 predictors; four learners, calibrators and thresholds\nS_MAC parameters and fitted objects retained',TEAL)
box(75,27,24,13,'Application catalogue','43,679 unresolved records\nNo outcome labels',TEAL)
box(8,8,91,15,'Identical audit output for every evaluable record','Four probabilities and votes · four-bit pattern · V0–V4 · S_MAC\nV0: unanimous B/LB-directed | V1–V3: mixed votes | V4: unanimous LP/P-directed\nBelow 80% observed panel features: Incomplete; predictions suppressed',TEAL)
for a,b in [((39,86),(39,82)),((39,69),(39,65)),((39,49),(39,40)),((39,27),(39,23)),((70,76),(75,76)),((70,57),(75,57)),((75,33),(70,33))]:ar(*a,*b)
ax.text(53,1,'Research prioritisation; model unanimity does not assign an ACMG/AMP class.',ha='center',fontsize=8,color=DARK)
save(fig,'Figure1_workflow')
# Figure 2: genuine repeat-level performance and selection.
fig,ax=plt.subplots(2,2,figsize=(8.4,7.2),layout='constrained')
panel=pd.read_csv(T/'deployment_panel.csv').sort_values('selected_outer_folds');names=[x.replace('am_pathogenicity','AlphaMissense').replace('_rankscore','').replace('_converted','').replace('SpliceAI_DS_max','SpliceAI max') for x in panel.predictor]
ax[0,0].barh(names,panel.selected_outer_folds,color=TEAL);ax[0,0].tick_params(axis='y',labelsize=7);ax[0,0].set_xlim(0,26);ax[0,0].set_xlabel('Selected outer folds (of 25)');title(ax[0,0],'A  Deployment-panel stability')
for r,o in P[P.complete_flag==1].groupby('repeat'):
 x,y,_=roc_curve(o.y,o.S_MAC);ax[0,1].plot(x,y,color=BLUE,alpha=.65,lw=1.2)
 pr,rc,_=precision_recall_curve(o.y,o.S_MAC);ax[1,0].plot(rc,pr,color=RED,alpha=.65,lw=1.2)
 q=pd.qcut(o.S_MAC,10,duplicates='drop');cal=o.groupby(q,observed=True).agg(score=('S_MAC','mean'),observed=('y','mean'));ax[1,1].plot(cal.score,cal.observed,'o-',color=TEAL,alpha=.65,ms=3,lw=1)
ax[0,1].plot([0,1],[0,1],'--',color=GREY);ax[0,1].set(xlabel='False-positive rate',ylabel='True-positive rate');title(ax[0,1],f"B  ROC · AUROC {s['performance']['AUROC']['mean']:.4f}")
ax[1,0].axhline(p.loc[p.complete_flag==1,'y'].mean(),ls='--',color=GREY);ax[1,0].set(xlabel='Recall',ylabel='Precision');title(ax[1,0],f"C  Precision–recall · AUPRC {s['performance']['AUPRC']['mean']:.4f}")
ax[1,1].plot([0,1],[0,1],'--',color=GREY);ax[1,1].set(xlabel='Mean S_MAC within decile',ylabel='Observed LP/P fraction');title(ax[1,1],f"D  Calibration · Brier {s['performance']['Brier']['mean']:.4f}")
for a in [ax[0,1],ax[1,0],ax[1,1]]:a.set_xlim(-.02,1.02);a.set_ylim(-.02,1.02)
save(fig,'Figure2_performance')
# Figure 3: honest four-status accounting and exact votes.
fig,ax=plt.subplots(2,2,figsize=(8.4,6.4),layout='constrained');ct=pd.read_csv(T/'exact_state_by_label.csv',index_col=0);ct.columns=[int(float(x)) for x in ct.columns]
ax[0,0].bar(range(5),ct.loc[0],color=BLUE,label='B/LB');ax[0,0].bar(range(5),ct.loc[1],bottom=ct.loc[0],color=RED,label='LP/P');ax[0,0].legend(frameon=False,fontsize=8);ax[0,0].set(xticks=range(5),xticklabels=[f'V{i}' for i in range(5)],ylabel='Evaluable anchors');title(ax[0,0],'A  Fixed out-of-fold vote states')
for i in range(5):ax[0,0].text(i,ct[i].sum()+15,str(ct[i].sum()),ha='center',fontsize=8)
ax[0,0].set_ylim(0,ct.sum().max()*1.18)
cts=A.V.value_counts().reindex(range(5),fill_value=0);ax[0,1].bar(range(5),cts,color=[BLUE,GREY,GREY,GREY,RED]);ax[0,1].set(xticks=range(5),xticklabels=[f'V{i}' for i in range(5)],ylabel='Unresolved variants');title(ax[0,1],'B  Application vote states')
for i,v in enumerate(cts):ax[0,1].text(i,v+600,f'{v:,}',ha='center',fontsize=8)
ax[0,1].set_ylim(0,cts.max()*1.17);ax[0,1].yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x/1000:g}k'))
GC=pd.read_csv(T/'state_by_label.csv',index_col=0);bottom=np.zeros(2)
for key,col in [('V0',BLUE),('V1–V3',GREY),('V4',RED),('Incomplete',GOLD)]:
 vals=100*GC.loc[['B/LB','LP/P'],key].to_numpy()/GC.loc[['B/LB','LP/P'],'Total'].to_numpy();ax[1,0].barh([0,1],vals,left=bottom,color=col,label=key);bottom+=vals
ax[1,0].set(yticks=[0,1],yticklabels=['B/LB (n=1,187)','LP/P (n=973)'],xlabel='Percentage of all source-labelled anchors',xlim=(0,100));fig.legend(*ax[1,0].get_legend_handles_labels(),frameon=False,fontsize=8,ncol=4,loc='lower center',bbox_to_anchor=(.33,-.055));title(ax[1,0],'C  Output and incomplete accounting')
vc=pd.read_csv(T/'V2_pair_composition.csv',index_col=0);vc.index=['Both tree','One of each','Both conventional'];ax[1,1].barh(vc.index,vc['0'],color=BLUE,label='B/LB');ax[1,1].barh(vc.index,vc['1'],left=vc['0'],color=RED,label='LP/P');ax[1,1].set_xlabel('Anchors at exact 2:2 disagreement');title(ax[1,1],'D  LP/P-directed pair at V2')
for j,(_,r) in enumerate(vc.iterrows()):ax[1,1].text(r.sum()+.25,j,str(int(r.sum())),va='center',fontsize=8)
ax[1,1].set_xlim(0,vc.sum(axis=1).max()+3)
save(fig,'Figure3_vstates')
# Figure 4: per-gene estimates, with readable class denominators.
fig,ax=plt.subplots(1,2,figsize=(8.4,5.8),sharey=True,layout='constrained');yy=np.arange(len(g))
for a,metric,col in [(ax[0],'sensitivity',RED),(ax[1],'specificity',BLUE)]:
 a.errorbar(g[metric],yy,xerr=np.vstack([g[metric]-g[metric+'_lo'],g[metric+'_hi']-g[metric]]).clip(min=0),fmt='o',color=col,ms=4.5,capsize=2,lw=1.1);a.set_xlim(-.03,1.04);a.set_xlabel('Proportion (Wilson 95% interval)');a.grid(axis='x',alpha=.15)
ax[0].set_yticks(yy);ax[0].set_yticklabels([f"{r.Gene}  ({int(r.TP+r.FN)} LP/P; {int(r.TN+r.FP)} B/LB)" for _,r in g.iterrows()],fontsize=8);ax[0].invert_yaxis();title(ax[0],'A  Held-out-gene sensitivity');title(ax[1],'B  Held-out-gene specificity')
save(fig,'Figure4_per_gene')
# Figure 5: constituent comparison and stable rescue.
c=pd.read_csv(T/'comparator_by_repeat.csv').groupby('comparator').mean(numeric_only=True);r=pd.read_csv(T/'stable_rescue.csv');fig,ax=plt.subplots(1,2,figsize=(8.4,4.2),layout='constrained');yy=np.arange(len(c))
ax[0].plot(c.AUROC_comparator,yy-.12,'s',color=GREY,label='Native score');ax[0].plot(c.AUROC_HBOCpred,yy+.12,'o',color=TEAL,label='HBOCpred');ax[0].set_yticks(yy);ax[0].set_yticklabels([f'{n}\n(n={int(c.loc[n,"n"])})' for n in c.index],fontsize=8);ax[0].set(xlim=(.84,1.002),xlabel='Mean matched-record AUROC');fig.legend(*ax[0].get_legend_handles_labels(),frameon=False,fontsize=8,ncol=2,loc='lower center',bbox_to_anchor=(.27,-.05));title(ax[0],'A  Descriptive paired comparison')
order=list(c.index)
for i,name in enumerate(order):
 for lab,col,sign in [('B/LB',BLUE,-1),('LP/P',RED,1)]:
  row=r[(r.comparator==name)&(r.source_label==lab)].iloc[0];v=sign*pct(row.rescued,row.denominator);ax[1].barh(i,v,color=col);ax[1].text(v+sign*.7,i,f'{int(row.rescued)}/{int(row.denominator)}',ha='right' if sign<0 else 'left',va='center',fontsize=7.5)
ax[1].axvline(0,color=DARK,lw=.8);ax[1].set(yticks=yy,yticklabels=order,xlim=(-35,35),xlabel='Stable rescue among native-score-available\nanchors (%)');ax[1].xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{abs(x):g}'));title(ax[1],'B  ≥3-of-4 stable rescue');ax[1].text(.02,.02,'B/LB ←',transform=ax[1].transAxes,color=BLUE,fontsize=8);ax[1].text(.98,.02,'→ LP/P',transform=ax[1].transAxes,ha='right',color=RED,fontsize=8)
save(fig,'Figure5_comparators')
# Figure 6: source review status, with nonevaluable denominators visible.
rr=pd.read_csv(T/'review_status.csv');order=['3-star','2-star','1-star','0-star','NR'];rr=rr.set_index(['review_stratum','source_label']);fig,ax=plt.subplots(1,2,figsize=(8.4,4.7),gridspec_kw={'width_ratios':[.85,1.5]},layout='constrained')
for j,lab in enumerate(['B/LB','LP/P']):
 vals=[rr.loc[(q,lab),'n'] if (q,lab) in rr.index else 0 for q in order];ax[0].barh(np.arange(5)+(j-.5)*.35,vals,.35,label=lab,color=BLUE if j==0 else RED)
ax[0].set(yticks=range(5),yticklabels=order,xlabel='All source-labelled anchors');ax[0].invert_yaxis();ax[0].legend(frameon=False,fontsize=8);title(ax[0],'A  Source review strata')
rows=[];labels=[];texts=[]
for q in order:
 for lab in ['LP/P','B/LB']:
  z=rr.loc[(q,lab)];den=int(z.n_evaluable);nums=[int(z[n+'_concordant']) for n in LEARNERS]+[int(z.ensemble_concordant)];rows.append([pct(k,den) for k in nums]);texts.append([f'{k}/{den}' if den else '—' for k in nums]);labels.append(f'{q} · {lab} ({den}/{int(z.n)})')
mat=np.array(rows);ax[1].imshow(mat,cmap='Blues',vmin=0,vmax=100,aspect='auto');ax[1].set_yticks(range(len(labels)));ax[1].set_yticklabels(labels,fontsize=7.3);ax[1].set_xticks(range(5));ax[1].set_xticklabels(['SVM\nRBF','L2\nlogistic','Extra\nTrees','HistGB','≥3/4'],fontsize=7.5)
for i in range(len(labels)):
 for j in range(5):ax[1].text(j,i,texts[i][j],ha='center',va='center',fontsize=7,color='white' if mat[i,j]>65 else DARK)
title(ax[1],'B  Source-direction agreement');save(fig,'Figure6_review_status')
# Figure 7: shift and gene signal, replacing an unverified application screenshot.
sh=pd.read_csv(T/'feature_shift.csv').sort_values('SMD');fig,ax=plt.subplots(1,2,figsize=(8.4,5.7),gridspec_kw={'width_ratios':[1.2,1]},layout='constrained');names=[x.replace('am_pathogenicity','AlphaMissense').replace('_rankscore','').replace('_converted','') for x in sh.predictor]
ax[0].barh(names,sh.SMD,color=[RED if abs(v)>=.2 else GREY for v in sh.SMD]);ax[0].axvline(0,color=DARK,lw=.8);ax[0].axvline(-.2,color=GREY,ls='--');ax[0].set_xlabel('SMD (application − anchors)');ax[0].tick_params(axis='y',labelsize=7.8);title(ax[0],'A  Predictor-distribution shift')
vals=[100*s['gene_recoverability']['majority_accuracy'],100*s['gene_recoverability']['accuracy']];ax[1].bar(['Majority\ngene baseline','Gene recovered\nfrom predictors'],vals,color=[GREY,TEAL],width=.58)
for i,v in enumerate(vals):ax[1].text(i,v+2,f'{v:.1f}%',ha='center',fontweight='bold',fontsize=10)
ax[1].set(ylim=(0,104),ylabel='Out-of-fold gene-identification accuracy (%)');title(ax[1],'B  Gene signal in the feature vector')
save(fig,'Figure7_shift_gene_signal')
# Supplementary population-control eligibility: alternate transcripts are retained explicitly.
d=pd.read_csv(ROOT/'audit/gnomAD_candidates.csv');fig,ax=plt.subplots(1,2,figsize=(8.4,5.2),layout='constrained');genes=list(g.Gene);dis=[]
for gene in genes:
 q=d[d.gene==gene];dis.append([int(q.in_any_training_record.sum()),int((~q.in_any_training_record&q.in_full_VOUS_archive).sum()),int((~q.in_any_training_record&~q.in_full_VOUS_archive).sum())])
dis=np.array(dis);left=np.zeros(len(genes))
for j,(lab,col) in enumerate([('Training archive',BLUE),('VOUS archive',GOLD),('Neither archive',TEAL)]):ax[0].barh(genes,dis[:,j],left=left,color=col,label=lab);left+=dis[:,j]
ax[0].invert_yaxis();ax[0].set_xlabel('AF-screened gene-level missense candidates');fig.legend(*ax[0].get_legend_handles_labels(),frameon=False,fontsize=8,ncol=3,loc='lower center',bbox_to_anchor=(.3,-.055));title(ax[0],'A  Candidate overlap across 17 genes')
ax[1].barh(['AF-screened\nmissense candidates','Absent from training','Absent from both\ntraining and VOUS','Also MANE missense'],[50,3,2,0],color=[BLUE,GOLD,TEAL,GREY]);ax[1].invert_yaxis();ax[1].set_xlim(0,56);ax[1].set_xlabel('Candidates retained')
for i,v in enumerate([50,3,2,0]):ax[1].text(v+1,i,str(v),va='center',fontweight='bold')
title(ax[1],'B  Overlap and transcript eligibility');save(fig,'FigureS1_gnomAD_eligibility')
print('Eight figures written',flush=True)
