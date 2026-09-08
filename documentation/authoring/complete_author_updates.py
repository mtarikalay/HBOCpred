"""Author-approved back matter and five reference corrections, 7 September 2026.

Run after finalize_submission.py. Preserve all other citation instructions,
reference paragraphs, numerical tables, pictures and Word package parts.
This edits embedded CSL metadata; it cannot synchronise Mendeley Desktop.
"""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
import json, re, hashlib
from lxml import etree as E
from finalize_submission import NS, q, text, hi, settext, replace_text, find, save

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'documentation'
REF=DOC/'reference_corrections'
AUTHOR=('Author Contributions: Conceptualization, M.T.A.; methodology, M.T.A.; software, M.T.A.; '
 'validation, M.T.A.; formal analysis, M.T.A.; investigation, M.T.A.; resources, M.T.A.; '
 'data curation, M.T.A.; writing—original draft preparation, M.T.A.; writing—review and editing, '
 'M.T.A. and H.B.E.; visualization, M.T.A.; supervision, M.T.A. and H.B.E.; project administration, '
 'M.T.A. All authors have read and agreed to the published version of the manuscript.')
BOOK='Digital Healthcare Technologies—Innovative Technologies and Changing Processes'
REFNUMS=[6,16,17,23,33]

def metadata():
 out={}
 for num in [6,16,17,23]:
  c=json.loads((REF/f'ref{num}.json').read_text())['message']
  d={'DOI':c['DOI'],'title':re.sub(r'\s+',' ',re.sub('<[^>]+>','',c['title'][0])).strip(),
     'issued':c['published'],'author':[({'literal':a['name']} if 'name' in a else {'given':a['given'],'family':a['family']}) for a in c['author']],
     'type':'article-journal','URL':'https://doi.org/'+c['DOI']}
  for k in ['page','volume','issue','publisher']:
   if c.get(k):d[k]=c[k]
  if c.get('container-title'):d['container-title']=c['container-title'][0]
  out[num]=d
 out[6]['DOI']='10.1056/NEJMoa1913948'
 out[16].update({'type':'article','container-title':'medRxiv','genre':'Preprint','note':'Preprint; posted 10 July 2026. Not a peer-reviewed journal article.'})
 out[17].update({'PMID':'25741868','PMCID':'PMC4544753'})
 out[23].update({'type':'chapter','container-title':BOOK,'publisher':'Sakarya University Press',
   'publisher-place':'Sakarya, Türkiye','page':'147-160','ISBN':'9786052238769',
   'editor':[{'given':'Murat','family':'Kirişci'},{'given':'Mahmut','family':'Akyiğit'},
             {'given':'Emrah Evren','family':'Kara'},{'given':'Necip','family':'Şimşek'}]})
 out[33]={'type':'article-journal','DOI':'10.38016/jista.1501164',
   'title':'Modified Hard Voting Classifier Implementation on MEFV Gene Variants Increases in Silico Tool Performance: A Novel Approach for Small Sample Size',
   'author':[{'given':'Tarık','family':'Alay'},{'given':'İbrahim','family':'Demir'},{'given':'Murat','family':'Kirisci'}],
   'container-title':'Journal of Intelligent Systems: Theory and Applications','volume':'8','issue':'1',
   'page':'35-46','issued':{'date-parts':[[2025]]},'ISSN':'2651-3927',
   'URL':'https://dergipark.org.tr/en/pub/jista/article/1501164'}
 return out

def segments(num):
 if num==6:return [('Breast Cancer Association Consortium. Breast Cancer Risk Genes — Association Analysis in More than 113,000 Women. ',''),('N. Engl. J. Med.','i'),(' ',''),('2021','b'),(', ',''),('384','i'),(', 428–439, doi:10.1056/NEJMoa1913948.','')]
 if num==16:return [('Düzenli, T.; Babazade, A.; Vural, O.; Bahap, Y.; Ergün, M.A. HECTOR: A Web-Based Tool for Automated BRCA1/BRCA2 Variant Classification Under the ClinGen ENIGMA Specifications. ',''),('medRxiv','i'),(' ',''),('2026','b'),(', doi:10.64898/2026.07.06.26357220 (preprint).','')]
 if num==17:return [('Richards, S.; Aziz, N.; Bale, S.; Bick, D.; Das, S.; Gastier-Foster, J.; Grody, W.W.; Hegde, M.; Lyon, E.; Spector, E.; et al. Standards and Guidelines for the Interpretation of Sequence Variants: A Joint Consensus Recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. ',''),('Genet. Med.','i'),(' ',''),('2015','b'),(', ',''),('17','i'),(', 405–424, doi:10.1038/gim.2015.30.','')]
 if num==23:return [('Alay, M.T. Integrative Classifiers for Variant Interpretation: Supervised Votes Meet Unsupervised Cluster Dominance. In ',''),(BOOK,'i'),('; Kirişci, M., Akyiğit, M., Kara, E.E., Şimşek, N., Eds.; Sakarya University Press: Sakarya, Türkiye, ',''),('2025','b'),('; pp. 147–160, doi:10.59537/saupress.2415.','')]
 if num==33:return [('Alay, T.; Demir, İ.; Kirisci, M. Modified Hard Voting Classifier Implementation on MEFV Gene Variants Increases in Silico Tool Performance: A Novel Approach for Small Sample Size. ',''),('J. Intell. Syst. Theory Appl.','i'),(' ',''),('2025','b'),(', ',''),('8','i'),(', 35–46, doi:10.38016/jista.1501164.','')]

def reference_paragraph(p,num,marked):
 assert not p.findall('.//w:fldChar',NS) and not p.findall('.//w:instrText',NS)
 base=deepcopy(p.find('w:r/w:rPr',NS))
 for e in list(base):
  if e.tag in [q('w:'+v) for v in ['b','bCs','i','iCs','highlight']]:base.remove(e)
 for e in list(p):
  if e.tag!=q('w:pPr'):p.remove(e)
 for i,(s,em) in enumerate([(str(num)+'. ','')]+segments(num)):
  r=E.SubElement(p,q('w:r'));pr=deepcopy(base)
  if em:E.SubElement(pr,q('w:'+em))
  r.append(pr)
  if i==1:E.SubElement(r,q('w:tab'))
  t=E.SubElement(r,q('w:t'));t.text=s;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
 if marked:hi(p)

def backmatter(p,s,marked):
 settext(p,s,marked)
 # Preserve the MDPI back-matter paragraph format, with a bold label.
 first=p.find('w:r',NS);t=first.find('w:t',NS);label,rest=s.split(':',1)
 t.text=label+':'
 pr=first.find('w:rPr',NS);E.SubElement(pr,q('w:b'))
 second=deepcopy(first);second.find('w:t',NS).text=rest
 for b in second.findall('w:rPr/w:b',NS):b.getparent().remove(b)
 p.append(second)

def edit_main(path,meta):
 marked='highlighted' in path.name
 with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
 tree=E.fromstring(parts['word/document.xml']);body=tree.find('w:body',NS)
 if any(text(p).startswith('Author Contributions:') for p in body):return
 old=deepcopy(tree);oldfields=old.xpath('.//w:instrText/text()',namespaces=NS)
 paragraphs=body.findall('w:p',NS)
 oldrefs={int(m[1]):E.tostring(p) for p in paragraphs if (m:=re.match(r'^(\d+)\. ',text(p))) and int(m[1])<=35}
 template=find(body,'Institutional Review Board Statement:')
 for s in [AUTHOR,'Funding: This research received no external funding.']:
  p=deepcopy(template);backmatter(p,s,marked);template.addprevious(p)
 p=find(body,'The companion Shiny catalogue viewer')
 replace_text(p,'The distributed viewer passed local runtime and browser interaction checks; deployment of this version to the public website has not been verified.',
  'The viewer is available at https://alaymd.shinyapps.io/hbocpred/. The corresponding author confirmed testing the live viewer on 7 September 2026.',marked)
 p=find(body,'Analyses used Python')
 replace_text(p,'assisted manuscript revision, analysis-code development and debugging, and figure and interface layout.',
  'assisted English-language editing and manuscript revision, analysis-code development and debugging, and figure and interface layout.',marked)
 p=find(body,'Acknowledgments:')
 backmatter(p,'Acknowledgments: We thank the Alay family for supporting novel ideas. Generative-AI assistance is described in Section 4.9. The authors take responsibility for the content of this publication.',marked)
 # Identify by bibliographic work, not ITEM-n (which restarts in each field).
 changes=[]
 for i,f in enumerate(tree.xpath('.//w:instrText',namespaces=NS)):
  if 'ADDIN CSL_CITATION ' not in f.text:continue
  d=json.loads(f.text.split('ADDIN CSL_CITATION ',1)[1]);changed=False
  for item in d['citationItems']:
   dat=item['itemData'];doi=dat.get('DOI','').lower();title=dat.get('title','')
   num=next((n for n in [6,23,33] if doi==meta[n]['DOI'].lower()),None)
   if doi=='10.1038/s41431-021-00858-1':num=17
   if title.startswith('HECTOR'):num=16
   if num:
    before=deepcopy(item);item['itemData']=dict(meta[num],id=dat['id'])
    if num==17:
     # New work: do not keep the old Alport paper's Mendeley UUID.
     # DOI URI is a real work identifier, not a fabricated Desktop library id.
     item['uris']=['https://doi.org/10.1038/gim.2015.30']
    changes.append({'reference':num,'field_index':i,'before':before,'after':deepcopy(item)})
    changed=True
  if changed:f.text=' ADDIN CSL_CITATION '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+' '
 for num in REFNUMS:
  p=next(p for p in body.findall('w:p',NS) if re.match(r'^'+str(num)+r'\. ',text(p)))
  reference_paragraph(p,num,marked)
 # Structural protection checks.
 fields=tree.xpath('.//w:instrText/text()',namespaces=NS)
 assert len(fields)==len(oldfields)==27
 changed_indices={c['field_index'] for c in changes};assert len(changes)==5 and len(changed_indices)==5
 assert all(fields[i]==oldfields[i] for i in range(27) if i not in changed_indices)
 newrefs={int(m[1]):E.tostring(p) for p in body.findall('w:p',NS) if (m:=re.match(r'^(\d+)\. ',text(p))) and int(m[1])<=35}
 assert set(newrefs)==set(oldrefs)==set(range(1,36))
 assert all(newrefs[n]==oldrefs[n] for n in newrefs if n not in REFNUMS)
 assert [E.tostring(x) for x in old.findall('.//w:tbl',NS)]==[E.tostring(x) for x in tree.findall('.//w:tbl',NS)]
 # Narrative text in every citation-bearing paragraph must stay unchanged.
 op=[text(p) for p in old.findall('.//w:p',NS) if p.findall('.//w:instrText',NS)]
 np=[text(p) for p in tree.findall('.//w:p',NS) if p.findall('.//w:instrText',NS)]
 assert op==np
 parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
 save(parts,path)
 (ROOT/'audit'/('author_reference_updates_'+('highlighted' if marked else 'clean')+'.json')).write_text(json.dumps({
  'date':'2026-09-07','reference_count':35,'citation_fields':26,'bibliography_fields':1,
  'uncorrected_citation_fields_byte_identical':True,'other_30_reference_paragraphs_byte_identical_before_pagination_fix':True,
  'citation_bearing_narrative_text_unchanged':True,'all_tables_byte_identical':True,
  'mendeley_desktop_database_accessed':False,'ref17_identity':'DOI URI replaces the unrelated Alport UUID; relink to the imported Richards record in Mendeley Desktop before refreshing.',
  'changes':changes},ensure_ascii=False,indent=2))

def edit_support(path):
 with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
 tree=E.fromstring(parts['word/document.xml']);body=tree.find('w:body',NS)
 quotes=[E.tostring(p) for p in body if text(p).startswith('Reviewer comment:')]
 for p in body.findall('.//w:p',NS):
  s=text(p)
  if s.startswith('Reviewer comment:'):continue
  if 'Public redeployment remains unverified.' in s:
   replace_text(p,'Public redeployment remains unverified.','The corresponding author confirmed testing the live viewer at https://alaymd.shinyapps.io/hbocpred/ on 7 September 2026.')
  if s.startswith('The source manuscript’s 35 reference entries'):
   settext(p,'The manuscript retains 35 references, 26 Mendeley citation fields and one bibliography field. We corrected the bibliographic records for references 6, 16, 23 and 33, and replaced the Alport-specific reference 17 with the general ACMG/AMP guidance of Richards et al. (2015). Introduction literature paragraphs and the main literature-comparison Discussion paragraph retain their wording. Supplementary Materials are supplied consistently. Figure and table numbering follows first appearance; the original numbering remains verbatim in the reviewer quotations. The current Shiny screenshot replaces the earlier interface illustration while preserving the gene and distribution-shift diagnostics. Author Contributions and Funding are completed, and generative-AI assistance is disclosed in Methods 4.9 and Acknowledgments.')
  if s=='Acknowledgments; conflicts statement':settext(p,'Funding; Author Contributions; conflicts statement')
  if s=='Conflict declaration retained. Funding declaration requires author completion.':settext(p,'No external funding declared. Author contributions and conflicts are stated in the manuscript.')
  if s.startswith('This is a study-specific reporting map,') and 'some author declarations remain incomplete' in s:
   replace_text(p,'some author declarations remain incomplete','patient/public-involvement information remain incomplete')
 assert quotes==[E.tostring(p) for p in body if text(p).startswith('Reviewer comment:')]
 parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True);save(parts,path)

def write_ris(meta):
 lines=[]
 for n,d in meta.items():
  kind={'article-journal':'JOUR','article':'UNPB','chapter':'CHAP'}[d['type']]
  lines += ['TY  - '+kind]
  for a in d['author']:lines+=['AU  - '+(a['literal'] if 'literal' in a else a['family']+', '+a['given'])]
  lines+=['TI  - '+d['title']]
  for e in d.get('editor',[]):lines+=['ED  - '+e['family']+', '+e['given']]
  for key,tag in [('container-title','T2'),('volume','VL'),('issue','IS'),('publisher','PB'),('publisher-place','CY'),('ISBN','SN'),('DOI','DO'),('URL','UR')]:
   if key in d:lines += [tag+'  - '+str(d[key])]
  lines+=['PY  - '+str(d['issued']['date-parts'][0][0])]
  if 'page' in d:
   start,end=d['page'].split('-',1);lines+=['SP  - '+start,'EP  - '+end]
  lines += ['N1  - HBOCpred manuscript reference '+str(n)+'.'+(' medRxiv preprint; posted 10 July 2026.' if n==16 else ''),'ER  - ','']
 (REF/'HBOCpred_Mendeley_corrected_6_16_17_23_33.ris').write_text('\n'.join(lines),encoding='utf-8')
 (REF/'corrected_records.csl.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))

def main():
 meta=metadata()
 for p in DOC.glob('HBOCpred_IJMS_Reviewer1_Round2_*.docx'):edit_main(p,meta)
 for name in ['HBOCpred_Response_Reviewer1_Round2.docx','HBOCpred_Supplementary_Audits_TRIPODAI.docx']:edit_support(DOC/name)
 write_ris(meta)
 # Keep reference 19 together: otherwise its DOI is orphaned on page 26.
 # This changes only its paragraph pagination property, not text or fields.
 for path in DOC.glob('HBOCpred_IJMS_Reviewer1_Round2_*.docx'):
  with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
  tree=E.fromstring(parts['word/document.xml']);body=tree.find('w:body',NS)
  p=next(p for p in body.findall('w:p',NS) if text(p).startswith('19. Zhuo'))
  pp=p.find('w:pPr',NS)
  if pp.find('w:keepLines',NS) is None:pp.insert(0,E.Element(q('w:keepLines')))
  disclaimer=find(body,'Disclaimer/Publisher’s Note:')
  # Retain the bibliography end-field and the MDPI notes style; compress
  # only empty spacer paragraphs so the publisher note is not stranded.
  for blank in [disclaimer.getprevious(),disclaimer.getnext()]:
   if blank is None or text(blank) or blank.tag!=q('w:p'):continue
   pp=blank.find('w:pPr',NS)
   if pp is None:pp=E.Element(q('w:pPr'));blank.insert(0,pp)
   sp=pp.find('w:spacing',NS)
   if sp is None:sp=E.SubElement(pp,q('w:spacing'))
   for key,val in [('before','0'),('after','0'),('line','20'),('lineRule','exact')]:sp.set(q('w:'+key),val)
  pp=disclaimer.find('w:pPr',NS);sp=pp.find('w:spacing',NS)
  if sp is None:sp=E.SubElement(pp,q('w:spacing'))
  sp.set(q('w:before'),'120')
  parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
  save(parts,path)
 print('Updated four documents; 35 references and 27 field instructions retained.')

if __name__=='__main__':main()
