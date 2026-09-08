from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
import json,hashlib,re
from lxml import etree as E
from PIL import Image
import pandas as pd
from manuscript_content import P,LIMITATIONS,FEATURE_PREFIX,FEATURE_SUFFIX,S,ROOT
BASE=Path(__file__).resolve().parent
SOURCE=BASE/'source_manuscript.docx'
OUT=ROOT/'documentation'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
def q(k):p,n=k.split(':');return '{'+NS[p]+'}'+n
def el(k,**attrs):r=E.Element(q(k));[r.set(q('w:'+a),str(v)) for a,v in attrs.items()];return r
def highlight(p):
 for r in p.findall('.//w:r',NS):
  if r.find('w:t',NS) is None:continue
  rp=r.find('w:rPr',NS)
  if rp is None:rp=el('w:rPr');r.insert(0,rp)
  h=rp.find('w:highlight',NS)
  if h is None:h=el('w:highlight');rp.append(h)
  h.set(q('w:val'),'yellow')
def run(text,pr=None):
 r=el('w:r')
 if pr is not None:r.append(deepcopy(pr))
 t=E.SubElement(r,q('w:t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text
 return r

def setp(p,text,hi=False):
 assert not p.findall('.//w:instrText',NS),'Never flatten a citation paragraph'
 rp=p.find('w:r/w:rPr',NS);pr=deepcopy(rp) if rp is not None else None
 if pr is not None:
  for x in list(pr):
   if E.QName(x).localname in ['b','i','bCs','iCs','highlight']:pr.remove(x)
 for c in list(p):
  if c.tag!=q('w:pPr'):p.remove(c)
 match=re.match(r'((?:Figure|Table) [0-9]+\.|(?:Institutional Review Board Statement|Informed Consent Statement|Data Availability Statement|Code Availability|Abbreviations):)',text)
 if match:
  bold=deepcopy(pr) if pr is not None else el('w:rPr');bold.append(el('w:b'));p.append(run(match.group(0),bold));p.append(run(text[match.end():],pr))
 else:p.append(run(text,pr))
 if hi:highlight(p)

def equation(p,text,hi=False):
 for c in list(p):
  if c.tag!=q('w:pPr'):p.remove(c)
 mp=E.SubElement(p,q('m:oMathPara'));m=E.SubElement(mp,q('m:oMath'));mr=E.SubElement(m,q('m:r'));rp=E.SubElement(mr,q('w:rPr'));rp.append(el('w:rFonts',ascii='Cambria Math',hAnsi='Cambria Math'));rp.append(el('w:sz',val='22'))
 if hi:rp.append(el('w:highlight',val='yellow'))
 E.SubElement(mr,q('m:t')).text=text

def table(t,rows,widths,hi):
 old=t.findall('w:tr',NS);header=deepcopy(old[0]);bodyrow=deepcopy(old[1]);
 for r in old:t.remove(r)
 grid=t.find('w:tblGrid',NS)
 for c in list(grid):grid.remove(c)
 for w in widths:grid.append(el('w:gridCol',w=w))
 tp=t.find('w:tblPr',NS)
 tw=tp.find('w:tblW',NS)
 if tw is None:tw=el('w:tblW');tp.append(tw)
 tw.set(q('w:w'),str(sum(widths)));tw.set(q('w:type'),'dxa')
 layout=tp.find('w:tblLayout',NS)
 if layout is None:layout=el('w:tblLayout');tp.append(layout)
 layout.set(q('w:type'),'fixed')
 for ri,row in enumerate(rows):
  tr=deepcopy(header if ri==0 else bodyrow)
  trpr=tr.find('w:trPr',NS)
  if trpr is None:trpr=el('w:trPr');tr.insert(0,trpr)
  for h in trpr.findall('w:trHeight',NS):trpr.remove(h)
  if trpr.find('w:cantSplit',NS) is None:trpr.append(el('w:cantSplit'))
  if ri==0 and trpr.find('w:tblHeader',NS) is None:trpr.append(el('w:tblHeader'))
  cells=tr.findall('w:tc',NS)
  for c in cells:tr.remove(c)
  for ci,(txt,w) in enumerate(zip(row,widths)):
   c=deepcopy(cells[min(ci,len(cells)-1)])
   cp=c.find('w:tcPr',NS)
   for bad in cp.findall('w:gridSpan',NS)+cp.findall('w:vMerge',NS):cp.remove(bad)
   cw=cp.find('w:tcW',NS)
   if cw is None:cw=el('w:tcW');cp.append(cw)
   cw.set(q('w:w'),str(w));cw.set(q('w:type'),'dxa')
   pp=c.find('w:p',NS)
   for x in list(c):
    if x.tag!=q('w:tcPr') and x is not pp:c.remove(x)
   setp(pp,str(txt),hi)
   pppr=pp.find('w:pPr',NS)
   if pppr is None:pppr=el('w:pPr');pp.insert(0,pppr)
   for typ in ['ind','spacing','jc']:
    for v in pppr.findall('w:'+typ,NS):pppr.remove(v)
   pppr.append(el('w:ind',left='0',right='0',firstLine='0'));pppr.append(el('w:spacing',before='20',after='20',line='200',lineRule='auto'));pppr.append(el('w:jc',val='left' if ci==0 or (ci==1 and len(widths)==5) else 'center'))
   for rr in pp.findall('w:r',NS):
    rp=rr.find('w:rPr',NS)
    if rp is None:rp=el('w:rPr');rr.insert(0,rp)
    for oldsz in rp.findall('w:sz',NS):rp.remove(oldsz)
    rp.append(el('w:sz',val='17' if len(widths)<7 else '16'))
    if ri==0:rp.append(el('w:b'))
   if len(rows)<=5 and ri<len(rows)-1:pppr.append(el('w:keepNext'))
   tr.append(c)
  t.append(tr)

def table_data():
 panel=pd.read_csv(ROOT/'tables/deployment_panel.csv')
 cats={x:'Conservation/context' for x in ['GERP++_RS_rankscore','phyloP100way_vertebrate_rankscore','phyloP470way_mammalian_rankscore','phastCons100way_vertebrate_rankscore','bStatistic_converted_rankscore']}
 cats['SpliceAI_DS_max']='Splicing'
 a=[['Deployment rank','Predictor','Category','Outer folds','Frequency']]+[[r.deployment_rank,r.predictor,cats.get(r.predictor,'Variant-effect score'),r.selected_outer_folds,f'{100*r.selection_frequency:.0f}%'] for _,r in panel.iterrows()]
 params=S['deployment_parameters'];nice={'SVM_RBF':'SVM–RBF','ENET_LR':'L2 logistic','EXTRA_TREES':'Extra Trees','HIST_GB':'HistGB'}
 pars=['C = 6; gamma = scale','C = 1; L2 penalty','220 trees; depth 18; max features 0.7; min leaf 1','31 leaves; min leaf 20; 100 iterations; rate 0.1; L2 = 0']
 b=[['Component','Role','Hyperparameters','Intercept','Slope','Threshold','Interpretation']]
 for (n,v),p in zip(params.items(),pars):b.append([nice[n],'Base learner',p,f'{v["platt"][0]:.5f}',f'{v["platt"][1]:.5f}',f'{v["threshold"]:.4f}','One vote'])
 b.extend([['Mean4','Mean score','Four calibrated probabilities','—','—','—','No vote'],['S_MAC','Meta-calibration','Logit(Mean4)',f'{S["smac_parameters"][0]:.5f}',f'{S["smac_parameters"][1]:.5f}','—','Ranking only']])
 c=[['Source label','V0','V1–V3','V4','Incomplete','Total']]
 for n,v in S['group_counts'].items():c.append([n]+[f'{v[k]:,}' for k in ['V0','V1–V3','V4','Incomplete','Total']])
 d=[['Analysis','Total n','Scored n','BA','AUROC','AUPRC','Evaluation']]
 d.append(['Primary, five repeats','2,160','2,046','0.9604 ± 0.0023','0.9909 ± 0.0013','0.9912 ± 0.0013','Mean ± split SD'])
 names=['Primary, repeat 1','With Reliability_index','Without addAF + AlphaMissense','Current-missense refit','Primary, same missense subset']
 for n,v in zip(names,S['sensitivities']):d.append([n,f'{v["n_total"]:,}',f'{v["n_evaluable"]:,}',f'{v["balanced_accuracy"]:.4f}',f'{v["AUROC"]:.4f}',f'{v["AUPRC"]:.4f}','First-repeat folds'])
 v=S['logo'];d.append(['Leave one gene out',str(v['n_total']),str(v['n_evaluable']),f'{v["balanced_accuracy"]:.4f}',f'{v["AUROC"]:.4f}',f'{v["AUPRC"]:.4f}','17 complete gene holdouts'])
 e=[['Learner','Search space'],['L2 logistic regression','C: 0.03, 0.1, 0.3, 1, 3, 10; l1_ratio = 0'],['SVM–RBF','C: 0.25, 0.75, 2, 6, 16; gamma: scale, 0.01, 0.03, 0.1'],['Extra Trees','220 trees; max depth: none, 10, 18; max features: sqrt, 0.4, 0.7; min leaf: 1, 3, 7'],['HistGB','Max leaves: 15, 31; min leaf: 10, 20; iterations: 100, 200; learning rate: 0.03, 0.1; L2: 0, 1']]
 return [(0,a,[720,2980,1840,1140,1177]),(1,b,[1000,930,2850,850,850,850,1235]),(2,c,[1400,1400,1500,1400,1500,1400]),(3,d,[2430,650,700,1270,1270,1270,1811]),(5,e,[2300,8165])]

def build(hi):
 z=ZipFile(SOURCE);parts={n:z.read(n) for n in z.namelist()}
 tree=E.fromstring(parts['word/document.xml']);body=tree.find('w:body',NS);ps=body.findall('w:p',NS)
 originals={i:E.tostring(ps[i]) for i in list(range(11,16))+[66]+list(range(131,166))}
 fields=tree.xpath('.//w:instrText/text()',namespaces=NS)
 for i,txt in P.items():setp(ps[i],txt,hi)
 # Replace the limitation paragraph with separate connected paragraphs.
 setp(ps[68],LIMITATIONS[0],hi);previous=ps[68]
 for txt in LIMITATIONS[1:]:
  np=deepcopy(ps[68]);setp(np,txt,hi);previous.addnext(np);previous=np
 # Retain the complete SpliceAI citation field sequence unchanged.
 old=ps[101];children=list(old);start=next(i for i,x in enumerate(children) if x.find('.//w:fldChar[@w:fldCharType="begin"]',NS) is not None);end=next(i for i,x in enumerate(children[start:],start) if x.find('.//w:fldChar[@w:fldCharType="end"]',NS) is not None)
 chunks=[deepcopy(c) for c in children[start:end+1]];pr=old.find('w:r/w:rPr',NS)
 for x in list(old):
  if x.tag!=q('w:pPr'):old.remove(x)
 old.append(run(FEATURE_PREFIX,pr));old.extend(chunks);old.append(run(FEATURE_SUFFIX,pr))
 if hi:highlight(old)
 # Preserve literature citations; change only this now-obsolete local phrase.
 done=False
 for t in ps[67].findall('.//w:t',NS):
  if 'context-specific mapping' in (t.text or ''):t.text=t.text.replace('context-specific mapping','shared vote-state descriptor');done=True
 assert done
 if hi:highlight(ps[67])
 for i in [80,81,82]:body.remove(ps[i])
 equation(ps[85],'pᵢₘ = σ(aₘ + bₘ zᵢₘ),     σ(z) = 1 / (1 + exp(−z)).     (1)',hi)
 equation(ps[87],'τₘ = arg maxₜ [TPRₘ(t) + TNRₘ(t)] / 2.     (2)',hi)
 equation(ps[89],'vᵢₘ = I(pᵢₘ ≥ τₘ),     cᵢ = Σₘ∈M vᵢₘ,     |M| = 4.     (3)',hi)
 tables=body.findall('w:tbl',NS)
 for idx,rows,widths in table_data():table(tables[idx],rows,widths,hi)
 # Include every resolved in-scope hospital allele, with overlap context explicit.
 h=pd.read_csv(ROOT/'tables/hospital_all_in_scope.csv',dtype={'vote_vector':str})
 order={g:i for i,g in enumerate(['BRCA1','BRCA2','PALB2','ATM','CHEK2','TP53','PTEN','CDH1','STK11','BARD1','BRIP1','RAD51C','RAD51D','NBN','BLM','FANCA','FANCC'])}
 h=h.assign(gene_order=h.Gene.map(order),coding_order=h.HGVSc.str.extract(r'c\.(\d+)')[0].astype(int)).sort_values(['gene_order','coding_order'])
 rows=[['Gene','MANE description','Source rows','Observed / 25','Record origin','Votes','V','S_MAC']]
 for _,r in h.iterrows():
  rows.append([r.Gene,r.HGVSc.split(':',1)[1]+'; '+r.HGVSp.split(':',1)[1],int(r.n_source_records),int(r.n_observed_panel),r.record_origin,r.vote_vector,'V'+str(int(r.V)) if r.complete_flag else '—',f'{r.S_MAC:.4f}' if r.complete_flag else '—'])
 hc=deepcopy(ps[41]);setp(hc,'Table 7. Complete hospital-list audit of 31 distinct missense variants within the 17-gene scope.',hi)
 hp=hc.find('w:pPr',NS)
 if hp.find('w:keepNext',NS) is None:hp.append(el('w:keepNext'))
 ht=deepcopy(tables[3]);table(ht,rows,[850,3030,720,900,1150,850,470,1080],hi)
 for size in ht.findall('.//w:rPr/w:sz',NS):size.set(q('w:val'),'18')
 hn=deepcopy(ps[45]);setp(hn,'All 47 in-scope source rows are represented; 75 rows from other genes remain in the full source audit. Votes are ordered SVM–RBF, logistic regression, Extra Trees and HistGB. Anchor: variant used to fit the deployment model (22 variants; displayed scores are in-sample). Catalogue: existing application record (8). Archive: wider source training archive, outside the anchor and application sets (1). All 31 pass ≥20/25 completeness. CHEK2 Ile200Thr/Ile157Thr and Gly210Arg/Gly167Arg are transcript aliases and were collapsed. Other CHEK2 descriptions are also shown on MANE Select. The ATM Asp2016Gly source rows contain discrepant rsIDs, retained in the row-level audit; matching used concordant coding/protein descriptions. RefSeq versions, genomic identities and unchanged source strings accompany the table. Source-row counts do not establish patient counts. S_MAC is a ranking score, not a clinical probability; these outputs provide no independent external performance estimate.',hi)
 ps[45].addnext(hc);hc.addnext(ht);ht.addnext(hn)
 # Replace existing embedded artwork and keep figure positions and caption styles.
 rels=E.fromstring(parts['word/_rels/document.xml.rels']);targets={x.get('Id'):x.get('Target') for x in rels}
 figs={28:'Figure2_performance',37:'Figure3_vstates',47:'Figure4_per_gene',52:'Figure5_comparators',54:'Figure6_review_status',60:'Figure7_shift_gene_signal',74:'Figure1_workflow'}
 for i,fig in figs.items():
  pic=ps[i];blip=pic.find('.//a:blip',NS);rid=blip.get(q('r:embed'));target='word/'+targets[rid];f=ROOT/'figures'/f'{fig}.png';parts[target]=f.read_bytes()
  width=4990000 if i in [54,60] else (5900000 if i==74 else 6440000)
  w,h=Image.open(f).size;height=round(width*h/w)
  if height>6900000:width=round(width*6900000/height);height=6900000
  for x in pic.findall('.//wp:extent',NS)+pic.findall('.//a:xfrm/a:ext',NS):x.set('cx',str(width));x.set('cy',str(height))
  pr=pic.find('w:pPr',NS)
  if pr.find('w:keepNext',NS) is None:pr.append(el('w:keepNext'))
  for x in pic.findall('.//a:srcRect',NS):x.getparent().remove(x)
 # Captions must stay with the following table; source styles/geometry retained.
 for i in [20,23,30,41,98,104,77,78,83,92,94,96]:
  pr=ps[i].find('w:pPr',NS)
  if pr.find('w:keepNext',NS) is None:pr.append(el('w:keepNext'))
 for i in [29,38,48,53,55,61,75]:
  pr=ps[i].find('w:pPr',NS)
  if pr.find('w:keepLines',NS) is None:pr.append(el('w:keepLines'))
 for pp in body.findall('w:p',NS):
  pr=pp.find('w:pPr',NS);style=pr.find('w:pStyle',NS) if pr is not None else None
  if style is not None and style.get(q('w:val')) in ['MDPI21heading1','MDPI22heading2'] and pr.find('w:keepNext',NS) is None:pr.append(el('w:keepNext'))
 for i,b in originals.items():assert E.tostring(ps[i])==b,('protected paragraph changed',i)
 assert tree.xpath('.//w:instrText/text()',namespaces=NS)==fields
 assert len(fields)==27
 parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
 # Correct inherited journal text while preserving the MDPI header and page fields.
 for n in list(parts):
  if (n.startswith('word/header') or n.startswith('word/footer')) and n.endswith('.xml'):
   hr=E.fromstring(parts[n]);changed=False
   for t in hr.findall('.//w:t',NS):
    before=t.text or '';after=before.replace('Molecules ', 'Int. J. Mol. Sci. ')
    if n=='word/header2.xml':after={'2025':'2026',' 30':' 27'}.get(after,after)
    if n=='word/footer2.xml' and after==' 24':after=' 27'
    if after!=before:t.text=after;changed=True
   if changed:parts[n]=E.tostring(hr,xml_declaration=True,encoding='UTF-8',standalone=True)
 name='HBOCpred_IJMS_Reviewer1_Round2_'+('highlighted' if hi else 'clean')+'.docx';path=OUT/name
 with ZipFile(path,'w',ZIP_DEFLATED) as dest:
  for n,v in parts.items():dest.writestr(n,v)
 return {'file':name,'citation_fields':26,'bibliography_fields':1,'references':35,'protected_intro_paragraphs_unchanged':True,'protected_literature_discussion_unchanged':True,'all_field_codes_unchanged':True,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
if __name__=='__main__':
 reports=[build(False),build(True)];(ROOT/'audit/document_integrity.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
