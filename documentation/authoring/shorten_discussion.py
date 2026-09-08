"""Shorten the seven Discussion paragraphs identified by the author.

Run after complete_author_updates.py. Preserve all citation instructions and
the Introduction and literature-comparison paragraph. No numerical changes.
"""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
import json, hashlib
from lxml import etree as E
from finalize_submission import NS, text, find, replace_text, settext, save

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'documentation'
TEXTS=[
('Two forms of predictor–label dependence',
 'Agreement with ClinVar reflects two sources of shared information. Some constituent predictors were trained on clinical variant classifications, and ClinVar submitters may use computational evidence through PP3/BP4. A variant held out of HBOCpred can therefore remain linked to predictor training or to labels informed by similar tools. Removing BayesDel addAF and AlphaMissense left internal discrimination largely unchanged, while other clinically trained or frequency-informed predictors remained. The external lists face related limits: common gnomAD variants were selected by frequency, and long-documented hospital alleles may overlap upstream training. These records support an audit of selected variants; they do not provide an independent test of clinical accuracy.'),
('The development and application populations also differ',
 'Nineteen predictors shifted between anchors and unresolved variants, and mixed votes were 2.70 times as frequent in the application catalogue. This pattern is consistent with definite classifications being more common when the available evidence is decisive. Reference outcomes are needed to measure performance in the unresolved population. Gene identity was also recoverable from the predictors with 89.40% accuracy. The lower held-out sensitivity in FANCA and the small NBN stratum show why the pooled AUROC should be read alongside the per-gene results.'),
('The asymmetric opposite-direction counts',
 'V0 included 32 of 973 LP/P anchors, whereas V4 included 16 of 1,187 B/LB anchors. This asymmetry matters because low scores could delay review of pathogenic variants. V0 must therefore remain a model-direction descriptor, never a reason to exclude a variant from expert review or reassure a patient. Our balanced-accuracy threshold objective weighted the two classes equally; clinical decision costs require separate evaluation.'),
('Annotation quality and transcript scope impose',
 'Missing annotations were concentrated in the least documented records: 101 of the 114 incomplete anchors belonged to the NR group. Reliability_index was excluded because it describes annotation quality; the completeness audit documents the imbalance that remains across records. Forty anchors also lacked a current same-gene missense annotation, and historical transcript assignments remain incomplete despite the transcript-restricted sensitivity analysis. The next evaluation should use a frozen pipeline, matched transcripts and independently assessed functional, segregation or case–control evidence across genes and both classes. HBOCpred’s present role is to organise variants for research review and functional follow-up.')]

def run():
 stats=[]
 for path in DOC.glob('HBOCpred_IJMS_Reviewer1_Round2_*.docx'):
  with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
  tree=E.fromstring(parts['word/document.xml']);body=tree.find('w:body',NS)
  if any(text(p).startswith('Agreement with ClinVar reflects') for p in body):continue
  fields=tree.xpath('//w:instrText/text()',namespaces=NS)
  lit=E.tostring(find(body,'This architecture distinguishes HBOCpred'))
  pars=body.findall('w:p',NS)
  start=next(i for i,p in enumerate(pars) if text(p).strip().startswith('Relative to hard voting alone'))
  old='\n\n'.join(text(p).strip() for p in pars[start:start+7])
  p=pars[start];s=text(p)
  a=s.index(', S_MAC provides');b=s.index('[18,19,34]')
  replace_text(p,s[a:b],', S_MAC distinguishes variants with the same vote count for expert review and functional follow-up. The four learner decisions define V0–V4; S_MAC ranks variants without adding a vote or changing their descriptor. Its calibration against source labels does not provide a clinical probability or a PP3/BP4 evidence threshold ', 'highlighted' in path.name)
  for prefix,new in TEXTS:settext(find(body,prefix),new,'highlighted' in path.name)
  for prefix in ['The externally sourced records do not establish','HBOCpred offers an auditable way']:
   p=find(body,prefix);assert not p.findall('.//w:instrText',NS);body.remove(p)
  assert fields==tree.xpath('//w:instrText/text()',namespaces=NS)
  assert lit==E.tostring(find(body,'This architecture distinguishes HBOCpred'))
  pars=body.findall('w:p',NS);start=next(i for i,p in enumerate(pars) if text(p).strip().startswith('Relative to hard voting alone'))
  new='\n\n'.join(text(p).strip() for p in pars[start:start+5])
  assert len(new.split())<len(old.split())
  parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True);save(parts,path)
  stats.append({'document':path.name,'old_paragraphs':7,'new_paragraphs':5,'old_words':len(old.split()),'new_words':len(new.split()),'old_text':old,'new_text':new,'citation_instruction_bytes_unchanged':True,'literature_comparison_paragraph_bytes_unchanged':True,'numeric_token_parsing_detail_remains_in_methods_4_3':True})
 if stats:(ROOT/'audit/discussion_concision_20260907.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
 print([(s['document'],s['old_words'],s['new_words']) for s in stats])

if __name__=='__main__':run()
