"""Apply the author's final response edits to the 7 September Word uploads.

Run after the five earlier authoring stages. The uploaded main document is
the source: its Mendeley record identities, images and Word settings are kept.
Restore the agreed 35-reference scope and verified metadata after a Desktop
refresh reintroduced two references and stale bibliographic fields.
"""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
import json,re,hashlib
from lxml import etree as E
from finalize_submission import NS,q,text,find,settext,replace_text,save,hi
from complete_author_updates import metadata,reference_paragraph

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'documentation'
SOURCE=DOC/'authoring/source_20260907'

def read(path):
    with ZipFile(path) as z: parts={n:z.read(n) for n in z.namelist()}
    return parts,E.fromstring(parts['word/document.xml'])

def doi(item):
    return item.get('itemData',{}).get('DOI','').replace('https://doi.org/','').lower()

def bold_prefix(p,prefix):
    run=p.find('w:r',NS);t=run.find('w:t',NS)
    assert t.text.startswith(prefix)
    rest=deepcopy(run);rest.find('w:t',NS).text=t.text[len(prefix):]
    t.text=prefix
    pr=run.find('w:rPr',NS)
    if pr is None:pr=E.Element(q('w:rPr'));run.insert(0,pr)
    if pr.find('w:b',NS) is None:E.SubElement(pr,q('w:b'))
    run.addnext(rest)

def main():
    parts,tree=read(SOURCE/'author_highlighted.docx')
    original=deepcopy(tree)
    body=tree.find('w:body',NS)
    fields=[];items={}
    for node in tree.xpath('//w:instrText',namespaces=NS):
        if 'ADDIN CSL_CITATION ' not in node.text: continue
        j=json.loads(node.text.split('ADDIN CSL_CITATION ',1)[1])
        fields.append((node,j))
        for item in j['citationItems']:
            if doi(item): items.setdefault(doi(item),deepcopy(item))
    assert len(fields)==26
    richards_uris=deepcopy(items['10.1038/gim.2015.30'].get('uris'))
    for node,j in fields:
        if any(doi(x)=='10.1136/jmedgenet-2020-106922' for x in j['citationItems']):
            j['citationItems']=[deepcopy(items[d]) for d in ['10.1016/j.gim.2021.11.018','10.1016/j.gim.2026.102606','10.1016/j.ajhg.2022.10.013']]
            for k,item in enumerate(j['citationItems'],1):item['id']=f'ITEM-{k}'
    verified=metadata()
    by_doi={d['DOI'].lower():d for d in verified.values()}
    for node,j in fields:
        for item in j['citationItems']:
            d=doi(item)
            if not d and item.get('itemData',{}).get('title','').startswith('HECTOR'): d=verified[16]['DOI'].lower()
            if d in by_doi:
                keep_id=item['itemData'].get('id')
                item['itemData']=deepcopy(by_doi[d])
                if keep_id is not None:item['itemData']['id']=keep_id
        if j != json.loads(node.text.split('ADDIN CSL_CITATION ',1)[1]):
            node.text=' ADDIN CSL_CITATION '+json.dumps(j,ensure_ascii=False,separators=(',',':'))+' '
    assert next(x for _,j in fields for x in j['citationItems'] if doi(x)=='10.1038/gim.2015.30').get('uris')==richards_uris

    p=next(p for p in body.findall('w:p',NS) if text(p).strip().startswith('Relative to hard voting alone'))
    replace_text(p,'alone[22,33]','alone [22,33]',True)
    replace_text(p,'threshold[19,34–36]','threshold [18,19,34]',True)
    p=find(body,'Numeric processing excluded')
    replace_text(p,'[37]','[35]',True)
    pars=body.findall('w:p',NS)
    start=next(i for i,p in enumerate(pars) if text(p)=='References')
    refs={int(m[1]):p for p in pars[start+1:] if (m:=re.match(r'^(\d+)\. ',text(p)))}
    assert len(refs)==37
    for n in [6,16,17,23,33]:reference_paragraph(refs[n],n,True)
    for n in [35,36]:
        assert not refs[n].findall('.//w:fldChar',NS)
        body.remove(refs[n])
    replace_text(refs[37],'37.','35.',True)
    for n in [n for n in refs if n not in [35,36]]:
        pr=refs[n].find('w:pPr',NS)
        if pr is None: pr=E.SubElement(refs[n],q('w:pPr'))
        if pr.find('w:keepLines',NS) is None:E.SubElement(pr,q('w:keepLines'))

    p=find(body,'Seventeen leave-one-gene-out fits')
    old='Figure 3 and Supplementary Table S1 and the accompanying per-gene CSV report the denominators in Shinny application, confusion counts, vote states and Wilson intervals for every gene.'
    new='Figure 3, Supplementary Table S1, the accompanying per-gene CSV and the Shiny viewer report denominators, confusion counts, vote states and Wilson intervals for every gene.'
    replace_text(p,old,new,True)
    p=find(body,'The complete hospital source list')
    replace_text(p,'Anchor-overlapping outputs are in-sample illustrations, not independent validation.',
      'The 22 anchor rows are retained solely to account for the complete source list; the nine non-anchor variants illustrate outputs outside the fitted anchor set.',True)
    p=find(body,'The companion Shiny catalogue viewer')
    replace_text(p,'The corresponding author confirmed testing the live viewer on 7 September 2026.','The corresponding author tested the live viewer on 7 September 2026.',True)
    p=find(body,'Figure 7. Companion Shiny')
    replace_text(p,'the locally running R4.4 viewer','the locally running viewer',True)
    p=find(body,'Analyses used Python')
    settext(p,'Analyses used Python 3.12.13, NumPy 2.3.5, pandas 2.2.3 and scikit-learn 1.8.0; figures were generated with Matplotlib. Split seeds start at 20260723 and modelling seeds at 20260714, with deterministic offsets recorded in the scripts. The release includes exact environment versions, fold maps, input hashes, feature-selection audits and 58 fitted models. Prediction replay reproduced all saved assessment outputs and the complete application catalogue to numerical precision.',True)
    heading=deepcopy(find(body,'4.9 Statistical analysis'))
    settext(heading,'4.10 Use of AI and AI-assisted Technologies',True)
    ai=deepcopy(p)
    settext(ai,'ChatGPT (OpenAI) and Claude (Anthropic) assisted English-language editing, manuscript revision, analysis-code development and debugging, and figure and interface layout. The authors reviewed and edited the outputs and take responsibility for the manuscript.',True)
    p.addnext(heading);heading.addnext(ai)
    p=find(body,'Acknowledgments:')
    replace_text(p,'Generative-AI assistance is described in Section 4.9.','Use of ChatGPT and Claude is described in Section 4.10.',True)
    replace_text(p,' The authors take responsibility for the content of this publication.','',True)
    p=find(body,'Data Availability Statement:')
    settext(p,'Data Availability Statement: The accompanying archive contains the 2,160-anchor and 25-predictor deployment matrices, gene and source annotations, fold maps, row-level assessment predictions, completeness and eligibility audits, and the frozen 43,679-record catalogue. Patient-level data are excluded. Persistent deposition, a DOI and reviewer access must be completed before resubmission.',True)
    bold_prefix(p,'Data Availability Statement:')
    p=find(body,'Code Availability:')
    replace_text(p,' The release reproduces the revised numerical analyses and includes a completed model-replay audit. Public repository and persistent-archive identifiers are pending; no post-publication-only availability promise or completed DOI deposition is asserted.',
      ' Persistent deposition and reviewer access remain pending.',True)

    # The new upload contains the author's refreshed Mendeley UUID for Richards;
    # keep it instead of recreating an identity or reverting to an older field.
    record={'date':'2026-09-07','input_references':37,'output_references':35,
      'removed_reintroduced_references':['10.1038/s41431-021-00858-1','10.1136/jmedgenet-2020-106922'],
      'author_added_existing_reference_22_retained':True,'richards_desktop_uri_preserved':True,
      'citation_fields':26,'bibliography_fields':1,'main_tables':7,'main_figures':8,
      'full_hospital_table_retained':31,'non_anchor_illustrations':9,
      'verified_metadata_restored':[6,16,17,23,33],'AI_section':'4.10',
      'only_main_document_XML_changed_relative_to_author_upload':True,
      'main_discussion_literature_paragraph_unchanged':E.tostring(find(original.find('w:body',NS),'This architecture distinguishes'))==E.tostring(find(body,'This architecture distinguishes'))}
    assert record['main_discussion_literature_paragraph_unchanged']
    assert tree.xpath('//w:fldChar/@w:fldCharType',namespaces=NS)==original.xpath('//w:fldChar/@w:fldCharType',namespaces=NS)
    for mode in ['highlighted','clean']:
        tr=deepcopy(tree)
        if mode=='clean':
            for h in tr.xpath('//w:highlight',namespaces=NS):h.getparent().remove(h)
        out=dict(parts);out['word/document.xml']=E.tostring(tr,xml_declaration=True,encoding='UTF-8',standalone=True)
        save(out,DOC/f'HBOCpred_IJMS_Reviewer1_Round2_{mode}.docx')
    (ROOT/'audit/final_response_refinements.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))

def response():
    parts,tree=read(SOURCE/'author_response.docx');body=tree.find('w:body',NS)
    before=[text(p) for p in body if text(p).startswith('Reviewer comment:')]
    p=find(body,'Response: We have withdrawn independent external-validation')
    replace_text(p,'Record origin is shown for every variant; anchor-overlapping scores are in-sample.',
      'Record origin is shown for every variant; anchor-overlapping scores are in-sample. The 22 anchor rows are retained solely to account for the complete source list; the nine non-anchor variants illustrate outputs outside the fitted anchor set.',False)
    p=find(body,'The Discussion connects both findings')
    settext(p,'The Discussion links this shift to selection of variants with decisive evidence into the classified anchor set. Internal consistency may therefore overestimate performance in unresolved variants; reference outcomes are needed to measure that performance.',False)
    p=find(body,'Response: The missing original fitted objects')
    replace_text(p,'the R4 matrices, models and predictions','the matrices, models and predictions in the current release',False)
    p=find(body,'The accompanying release contains')
    settext(p,'The accompanying release contains the 2,160-anchor numeric matrix, the 25-predictor deployment matrix, gene and source labels, outer and inner fold memberships, row-level predictions and all 58 fitted models. Prediction replay reproduced the saved assessment outputs and the complete application catalogue to numerical precision; audit/model_verification.json records the result. Scripts regenerate the analytical tables, seven main analytical figures and Supplementary Figure S1. Figure 7 is a browser capture of the companion viewer. The unreproducible UniProt analysis remains removed.',False)
    p=find(body,'Response: We corrected the software record')
    settext(p,'Response: We corrected the software record to the environment actually used: Python 3.12.13, NumPy 2.3.5, pandas 2.2.3 and scikit-learn 1.8.0, with exact auxiliary package versions in the release. No reanalysed result is attributed to an unverified R or RStudio version. The corresponding author tested the live Shiny viewer (https://alaymd.shinyapps.io/hbocpred/) on 7 September 2026; Figure 7 shows the updated interface.',False)
    bold_prefix(p,'Response:')
    p=find(body,'The manuscript retains 35 references')
    replace_text(p,'Methods 4.9 and Acknowledgments.','Section 4.10 (Use of AI and AI-assisted Technologies) and Acknowledgments.',False)
    assert before==[text(p) for p in body if text(p).startswith('Reviewer comment:')]
    parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    save(parts,DOC/'HBOCpred_Response_Reviewer1_Round2.docx')

if __name__=='__main__':
    main();response()
    print('Updated main documents and response; 35 references, 26 citation fields and full hospital table retained.')
