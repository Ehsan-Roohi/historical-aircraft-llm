"""Freeze complete draft22 only after PDF rendering and visual inspection."""
import hashlib,json,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'output/overleaf/aircraft_complete_loading_draft22'
qa=json.loads((ROOT/'tmp/pdfs/loading22/qa.json').read_text())
assert not qa['blank_pages'] and not qa['double_question_marks']
qa['visual_review']='All pages reviewed in rendered contact sheets; newly added tables and discussion inspected at enlarged resolution.'
(P/'PDF_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
text=(P/'main.tex').read_text(encoding='utf-8')
source=(ROOT/'output/overleaf/aircraft_complete_corrected_draft21/main.tex').read_text(encoding='utf-8')
labels=re.findall(r'\\label\{([^}]+)\}',text)
refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',text)
assert len(labels)==len(set(labels)) and not set(refs)-set(labels)
assert re.findall(r'\\includegraphics[^\n]+',text)==re.findall(r'\\includegraphics[^\n]+',source)
# Verify the original complete narrative is retained in order, except the
# explicitly expanded availability sentence.
original=source.replace('The local review ZIP accompanying this draft contains the V15 lateral-screen scripts, inputs, outputs and checksum manifest,','The local review ZIP accompanying this draft contains the V15 lateral-screen, loading-envelope, researcher tail-trade and added-mass sensitivity scripts, inputs, outputs and checksum manifest,')
pos=0
for line in original.splitlines():
    if not line.strip():continue
    found=text.find(line,pos)
    assert found>=0,('Prior content missing',line[:90])
    pos=found+len(line)
audit=dict(status='COMPLETE_WORKING_DRAFT_NOT_SUBMISSION_APPROVED',pdf_pages=qa['pdf_pages'],figures=17,
           tables=len(re.findall(r'\\begin\{table\}',text)),original_draft21_narrative_and_figures_preserved=True,
           separate_review_layout_compiled=False,accepted_aircraft_modes=False)
(P/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
readme=(P/'README.md').read_text(encoding='utf-8').replace('Compilation and visual QA: pending.',f'Reading PDF compiled and visually reviewed: {qa["pdf_pages"]} pages, 17 figures and {audit["tables"]} tables. The separate review-layout source is not independently compiled.')
(P/'README.md').write_text(readme,encoding='utf-8')
readiness=(P/'JOURNAL_READINESS.md').read_text().replace('will be compiled and visually checked','has been compiled and visually checked')
(P/'JOURNAL_READINESS.md').write_text(readiness)
for name in ('build_complete_draft22.py','finalize_complete_draft22.py'):
    shutil.copy2(ROOT/'analysis'/name,P/'audit_data'/name)
shutil.copy2(P/'main.pdf',ROOT/'output/pdf/aircraft_complete_loading_draft22.pdf')
records=[]
for p in sorted(P.rglob('*')):
    if p.is_file() and p.name!='MANIFEST.json':records.append(dict(path=p.relative_to(P).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(P/'MANIFEST.json').write_text(json.dumps(dict(status=audit['status'],files=records),indent=2)+'\n')
with zipfile.ZipFile(P.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(P.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(P).as_posix())
with zipfile.ZipFile(P.with_suffix('.zip')) as z:
    assert z.testzip() is None
    for r in records:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
print(json.dumps(audit))
