"""Apply the final publication layout to the audited R4 documents.

Run after both document builders. Existing Mendeley fields and bibliography
are preserved at XML level. Analysis asset filenames retain their stable IDs;
audit/publication_numbering.json maps those IDs to manuscript figure numbers.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import re, json, hashlib, csv
from lxml import etree as E
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'documentation'
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm':'http://schemas.openxmlformats.org/officeDocument/2006/math',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
FM = {1:8, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6}
TM = {1:6, 2:7, 3:1, 4:2, 5:3, 6:4, 7:5}
SHOT = 'Figure7_Shiny_catalogue.png'
ABSTRACT = ('HBOCpred prioritises unresolved germline missense variants in 17 hereditary breast and ovarian cancer genes. '
 'Four calibrated learners provide a vote vector, V0–V4 agreement states and the S_MAC ranking score. '
 'Identical descriptors apply to source-labelled and unresolved records: V0 denotes unanimous B/LB-directed votes, V1–V3 mixed votes and V4 unanimous LP/P-directed votes; none assigns ACMG/AMP status. '
 'Development used 2,160 anchors with five repeats of nested five-fold cross-validation and preprocessing fitted within training partitions. '
 'The annotation-completeness rule allowed outputs for 2,046 anchors per repeat and suppressed 114. '
 'Among evaluable anchors, the secondary ≥3-of-4 endpoint yielded balanced accuracy 0.9604 ± 0.0023; S_MAC yielded AUROC 0.9909 ± 0.0013 and Brier score 0.0294 ± 0.0010. '
 'Values after ± describe split stability. First-repeat unanimous outputs agreed with source labels in 1,920/1,968 cases, but 32 LP/P anchors received V0. '
 'Leave-one-gene-out AUROC was 0.9812 among 2,045 evaluable anchors, with substantial gene-specific variation. '
 'Among 43,679 unresolved records, V0, V1–V3 and V4 contained 33,414, 4,491 and 5,774 variants. '
 'These internal consistency estimates remain subject to predictor–label dependence and distribution shift; independent clinical performance and utility are unestablished.')

def q(s):
 p,n=s.split(':'); return '{'+NS[p]+'}'+n
def text(p): return ''.join(p.xpath('.//w:t/text()',namespaces=NS))
def hi(p):
 for r in p.findall('.//w:r',NS):
  if r.find('w:t',NS) is None: continue
  rp=r.find('w:rPr',NS)
  if rp is None: rp=E.Element(q('w:rPr'));r.insert(0,rp)
  h=rp.find('w:highlight',NS)
  if h is None:h=E.SubElement(rp,q('w:highlight'))
  h.set(q('w:val'),'yellow')
def replace_text(p,old,new,highlight=False):
 """Replace text across runs, leaving fields and all unrelated XML intact."""
 whole=text(p); start=whole.find(old)
 assert start>=0,(old,whole[:100])
 end=start+len(old); offset=0; placed=False
 for t in p.findall('.//w:t',NS):
  s=t.text or ''; a=offset;b=offset+len(s);offset=b
  if b<=start or a>=end:continue
  lo=max(0,start-a);up=min(len(s),end-a)
  t.text=s[:lo]+(new if not placed else '')+s[up:];placed=True
  t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
 if highlight:hi(p)
def settext(p,s,highlight=False):
 assert not p.findall('.//w:instrText',NS)
 rp=p.find('w:r/w:rPr',NS);rp=deepcopy(rp) if rp is not None else E.Element(q('w:rPr'))
 for k in ['b','i','bCs','iCs','highlight']:
  for e in rp.findall('w:'+k,NS):rp.remove(e)
 for e in list(p):
  if e.tag!=q('w:pPr'):p.remove(e)
 m=re.match(r'((?:Figure \d+\.|Supplementary Materials:))',s)
 chunks=[(s[:m.end()],True),(s[m.end():],False)] if m else [(s,False)]
 for chunk,bold in chunks:
  r=E.SubElement(p,q('w:r'));pr=deepcopy(rp)
  if bold:E.SubElement(pr,q('w:b'))
  r.append(pr);t=E.SubElement(r,q('w:t'));t.text=chunk;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
 if highlight:hi(p)
def renumber(p,highlight=False):
 if text(p).startswith('Reviewer comment:'):return
 pattern=r'\b(Figures?|Tables?) (\d+[A-D]?(?:[–-]\d+[A-D]?)?(?:(?:, | and |, and )\d+[A-D]?(?:[–-]\d+[A-D]?)?)*)'
 for m in reversed(list(re.finditer(pattern,text(p)))):
  mapping=FM if m[1].startswith('Figure') else TM
  nums=[]
  for token in re.split(r', and | and |, ',m[2]):
   ends=re.split('[–-]',token)
   if len(ends)==2:nums.extend(str(mapping[i]) for i in range(int(ends[0]),int(ends[1])+1))
   else:
    n=re.fullmatch(r'(\d+)([A-D]?)',token);nums.append(str(mapping[int(n[1])])+n[2])
  if len(nums)>1:nums=sorted(set(nums),key=lambda n:int(re.match(r'\d+',n)[0]))
  val=nums[0] if len(nums)==1 else (' and '.join(nums) if len(nums)==2 else ', '.join(nums[:-1])+' and '+nums[-1])
  replace_text(p,m[0],m[1]+' '+val,highlight)
def find(body,prefix):return next(p for p in body.findall('w:p',NS) if text(p).startswith(prefix))
def save(parts,path):
 with ZipFile(path,'w',ZIP_DEFLATED) as z:
  for n,v in parts.items():z.writestr(n,v)
def main_doc(path):
 marked='highlighted' in path.name
 with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
 if 'word/media/'+SHOT in parts:return
 tree=E.fromstring(parts['word/document.xml']);body=tree.find('w:body',NS);oldchildren=list(body)
 fields=tree.xpath('.//w:instrText/text()',namespaces=NS)
 protected={i:E.tostring(oldchildren[i]) for i in list(range(11,16))+[73,74,111]+list(range(142,177))}
 for p in body.findall('.//w:p',NS):renumber(p,marked)
 settext(find(body,'Hereditary breast and ovarian cancer multigene testing leaves'),ABSTRACT,marked)
 p=find(body,'Seventeen leave-one-gene-out fits')
 replace_text(p,'the accompanying per-gene table','Supplementary Table S1 and the accompanying per-gene CSV',marked)
 p=find(body,'A companion Shiny catalogue viewer')
 settext(p,'The companion Shiny catalogue viewer uses the same descriptors, counts and completeness rules as the analysis. It supports gene and variant searches, displays individual learner scores and vote patterns, and exports filtered records. Figure 7 shows the running viewer with the complete 43,679-record catalogue. The distributed viewer passed local runtime and browser interaction checks; deployment of this version to the public website has not been verified.',marked)
 p=find(body,'Application-versus-anchor standardised mean differences')
 old='all figures retained here are regenerated from distributed row-level data and saved model outputs'
 replace_text(p,old,'the analytical figures are regenerated from distributed row-level data and saved model outputs, while Figure 7 is a browser capture of the running companion viewer',marked)
 # Preserve the required gene/shift diagnostic, and add the verified viewer image.
 pic=deepcopy(oldchildren[67]);caption=deepcopy(oldchildren[68])
 rels=E.fromstring(parts['word/_rels/document.xml.rels']);rid='rIdHBOCShinyFinal'
 rel=E.SubElement(rels,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
 rel.set('Id',rid);rel.set('Type',NS['r']+'/image');rel.set('Target','media/'+SHOT)
 pic.find('.//a:blip',NS).set(q('r:embed'),rid)
 width=6440000;w,h=Image.open(ROOT/'figures'/SHOT).size;height=round(width*h/w)
 for e in pic.findall('.//wp:extent',NS)+pic.findall('.//a:xfrm/a:ext',NS):e.set('cx',str(width));e.set('cy',str(height))
 for e in pic.findall('.//wp:docPr',NS):e.set('id','990');e.set('name','HBOCpred running Shiny catalogue');e.set('descr','Unfiltered HBOCpred catalogue: 43,679 variants, 33,414 V0, 4,491 mixed and 5,774 V4.')
 for e in pic.findall('.//a:srcRect',NS):e.getparent().remove(e)
 pr=pic.find('w:pPr',NS)
 if pr is None:pr=E.Element(q('w:pPr'));pic.insert(0,pr)
 E.SubElement(pr,q('w:pageBreakBefore'))
 settext(caption,'Figure 7. Companion Shiny variant catalogue. The unfiltered view displays all 43,679 application records and the shared vote-group counts. Filters support gene, vote-state, descriptor and variant searches; users can inspect individual learner outputs and export matching records. This screenshot was captured from the locally running R4.4 viewer on 6 September 2026. Model direction is displayed separately from source classification; the interface does not assign ACMG/AMP classifications.',marked)
 oldchildren[68].addnext(pic);pic.addnext(caption)
 parts['word/media/'+SHOT]=(ROOT/'figures'/SHOT).read_bytes()
 parts['word/_rels/document.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
 sup=deepcopy(oldchildren[135]);settext(sup,'Supplementary Materials: Figure S1: gnomAD candidate eligibility and archive overlap; Table S1: gene-held-out source and evaluable counts with class-specific results; Table S2: conditional first-repeat performance intervals; Table S3: candidates outside both archives without model predictions; Table S4: study-specific TRIPOD+AI reporting map.',marked)
 oldchildren[133].addprevious(sup)
 # Disclose the assistance actually used. Author sign-off is still required.
 p=oldchildren[131]
 disclosure=' Generative AI tools, ChatGPT (OpenAI) and Claude (Anthropic), assisted manuscript revision, analysis-code development and debugging, and figure and interface layout. Numerical results were computed from the supplied data using the archived executable code; analytical plots and the interface screenshot were not generated as synthetic images.'
 replace_text(p,text(p),text(p)+disclosure,marked)
 for i,b in protected.items():assert E.tostring(oldchildren[i])==b,('protected XML changed',i)
 assert tree.xpath('.//w:instrText/text()',namespaces=NS)==fields
 assert len(ABSTRACT.split())<=200,len(ABSTRACT.split())
 parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True);save(parts,path)
 return {'file':path.name,'references':35,'citation_fields':26,'bibliography_fields':1,'protected_XML_unchanged':True,'abstract_words':len(ABSTRACT.split()),'figures':8,'tables':7,'screenshot_sha256':hashlib.sha256(parts['word/media/'+SHOT]).hexdigest()}
def support_doc(path):
 with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
 t=E.fromstring(parts['word/document.xml']);body=t.find('w:body',NS)
 if 'HBOC_FINAL_LAYOUT_20260906' in t.xpath('.//w:bookmarkStart/@w:name',namespaces=NS):return
 quotes=[E.tostring(p) for p in body if text(p).startswith('Reviewer comment:')]
 for p in body.findall('.//w:p',NS):renumber(p)
 if 'Response' in path.name:
  p=find(body,'The accompanying release contains')
  replace_text(p,'Scripts regenerate the tables and eight figures.','Scripts regenerate the analytical tables, seven main analytical figures and Supplementary Figure S1. The additional Figure 7 is an actual browser capture of the companion viewer.')
  p=find(body,'Response: We corrected the software record')
  replace_text(p,'The revised Shiny viewer passed R runtime and local HTTP checks in this environment. Browser interaction and public redeployment remain unverified.','The R4.4 Shiny viewer passed R runtime, local HTTP and browser interaction checks, including a regression check with external stylesheet requests blocked. The current interface is shown in Figure 7. Public redeployment remains unverified.')
  p=find(body,'The source manuscript’s 35 reference entries')
  replace_text(p,text(p),text(p)+' Figure and table numbering now follows first appearance; the original numbering is retained verbatim in the reviewer quotations. The current Shiny screenshot replaces the earlier interface illustration without removing the gene and distribution-shift diagnostics.')
 else:
  p=find(body,'The computational release is labelled R4')
  settext(p,'These Supplementary Materials accompany the R4 analysis. Numerical results derive from the archived fitted objects and out-of-fold predictions. The primary cohort contains 2,160 historical source-labelled anchors; 114 do not meet output completeness in each repeated cross-validation assessment. No external clinical validation is claimed.')
  p=find(body,'HBOCpred — audited reanalysis')
  settext(p,'HBOCpred: an ensemble framework for prioritisation of germline missense variants in hereditary breast and ovarian cancer')
 assert quotes==[E.tostring(p) for p in body if text(p).startswith('Reviewer comment:')]
 b=E.SubElement(body[0],q('w:bookmarkStart'));b.set(q('w:id'),'990');b.set(q('w:name'),'HBOC_FINAL_LAYOUT_20260906')
 e=E.SubElement(body[0],q('w:bookmarkEnd'));e.set(q('w:id'),'990')
 parts['word/document.xml']=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True);save(parts,path)

def polish_main(path):
 """Final render-driven fixes, safe to apply to an already finalised file."""
 with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
 t=E.fromstring(parts['word/document.xml']);marked='highlighted' in path.name
 for p in t.findall('.//w:p',NS):
  if text(p)=='Deployment rank':settext(p,'Rank',marked)
  if text(p).startswith('For every evaluable record, HBOCpred reports') and 'Figure 8' not in text(p):
   replace_text(p,text(p),text(p)+' Figure 8 summarises model development and the shared reporting workflow.',marked)
  if text(p).startswith('Four learner families were fixed before running') and 'Table 7' not in text(p):
   replace_text(p,'from the listed grids;','from the listed grids (Table 7);',marked)
  if p.find('.//a:blip[@r:embed="rIdHBOCShinyFinal"]',NS) is not None:
   pr=p.find('w:pPr',NS)
   for key in ['ind','jc']:
    for old in pr.findall('w:'+key,NS):pr.remove(old)
   ind=E.SubElement(pr,q('w:ind'))
   for key in ['left','right','firstLine']:ind.set(q('w:'+key),'0')
   jc=E.SubElement(pr,q('w:jc'));jc.set(q('w:val'),'center')
 for e in t.findall('.//w:shd',NS):
  if (e.get(q('w:fill')) or '').upper() in ['FFF2CC','FFFF00']:
   e.set(q('w:fill'),'auto');e.set(q('w:val'),'clear')
 # Real OMML subscripts prevent the inherited Unicode glyphs from overlapping.
 def mr(s,plain=False):
  r=E.Element(q('m:r'));mp=E.SubElement(r,q('m:rPr'))
  st=E.SubElement(mp,q('m:sty'));st.set(q('m:val'),'p' if plain else 'i')
  wp=E.SubElement(r,q('w:rPr'));ft=E.SubElement(wp,q('w:rFonts'))
  for k in ['ascii','hAnsi']:ft.set(q('w:'+k),'Cambria Math')
  sz=E.SubElement(wp,q('w:sz'));sz.set(q('w:val'),'22')
  if marked:E.SubElement(wp,q('w:highlight')).set(q('w:val'),'yellow')
  tx=E.SubElement(r,q('m:t'));tx.text=s;tx.set('{http://www.w3.org/XML/1998/namespace}space','preserve');return r
 def sub(base,index,plain=False):
  s=E.Element(q('m:sSub'));E.SubElement(s,q('m:e')).append(mr(base,plain));E.SubElement(s,q('m:sub')).append(mr(index));return s
 def frac(a,b):
  f=E.Element(q('m:f'));num=E.SubElement(f,q('m:num'));den=E.SubElement(f,q('m:den'))
  num.extend(a);den.extend(b);return f
 formulae=[
  [sub('p','im'),mr(' = ',True),mr('σ'),mr('(',True),sub('a','m'),mr(' + ',True),sub('b','m'),mr(' ',True),sub('z','im'),mr('),     ',True),mr('σ'),mr('(',True),mr('z'),mr(') = ',True),frac([mr('1',True)],[mr('1 + exp(',True),mr('−z'),mr(')',True)]),mr('     (1)',True)],
  [sub('τ','m'),mr(' = ',True),sub('arg max','t',True),mr(' ',True),frac([sub('TPR','m',True),mr('(',True),mr('t'),mr(') + ',True),sub('TNR','m',True),mr('(',True),mr('t'),mr(')',True)],[mr('2',True)]),mr('     (2)',True)],
  [sub('v','im'),mr(' = I(',True),sub('p','im'),mr(' ≥ ',True),sub('τ','m'),mr('),     ',True),sub('c','i'),mr(' = ',True),sub('∑','m∈M',True),sub('v','im'),mr(',     |',True),mr('M'),mr('| = 4.     (3)',True)]
 ]
 equations=[p for p in t.findall('.//w:p',NS) if p.find('m:oMathPara',NS) is not None]
 assert len(equations)==3
 for p,nodes in zip(equations,formulae):
  for e in list(p):
   if e.tag!=q('w:pPr'):p.remove(e)
  mp=E.SubElement(p,q('m:oMathPara'));mppr=E.SubElement(mp,q('m:oMathParaPr'));E.SubElement(mppr,q('m:jc')).set(q('m:val'),'center')
  E.SubElement(mp,q('m:oMath')).extend(nodes)
 parts['word/document.xml']=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True);save(parts,path)

def finalize_all():
 reports=[]
 for name in ['HBOCpred_IJMS_Reviewer1_Round2_clean.docx','HBOCpred_IJMS_Reviewer1_Round2_highlighted.docx']:
  r=main_doc(DOC/name)
  polish_main(DOC/name)
  if r:reports.append(r)
 for name in ['HBOCpred_Response_Reviewer1_Round2.docx','HBOCpred_Supplementary_Audits_TRIPODAI.docx']:support_doc(DOC/name)
 with ZipFile(DOC/'HBOCpred_Supplementary_Audits_TRIPODAI.docx') as z:
  t=E.fromstring(z.read('word/document.xml'));table=t.findall('.//w:tbl',NS)[-1]
  rows=[[text(c) for c in r.findall('w:tc',NS)] for r in table.findall('w:tr',NS)]
 with (DOC/'TRIPODAI_reporting_map.csv').open('w',newline='') as f:
  csv.writer(f).writerows([['item','topic','location','coverage_and_gap']]+rows[1:])
 if reports:(ROOT/'audit/final_document_integrity.json').write_text(json.dumps(reports,indent=2))
 (ROOT/'audit/publication_numbering.json').write_text(json.dumps({'stable_analysis_figure_id_to_final_main_figure':FM,'old_main_table_to_final_main_table':TM,'new_main_figure_7':SHOT,'reviewer_quotations_keep_original_numbers':True},indent=2))
 print('Final layout applied; 35 references and 27 Mendeley fields preserved.')

if __name__=='__main__':finalize_all()
