"""Freeze draft23 after compile, full contact sheets and enlarged pages 50-52."""
import hashlib,json,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'output/overleaf/aircraft_complete_structural_draft23'
qa=json.loads((ROOT/'tmp/pdfs/structural23/qa.json').read_text())
assert qa['compile_exit_code']==0 and qa['rendered_pages']==qa['pdf_pages']==64
assert not qa['blank_pages'] and not qa['double_question_marks']
qa['visual_review']='All 64 pages reviewed in four contact sheets; new pages 50-52 inspected at enlarged resolution. No clipping observed.'
(P/'PDF_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
text=(P/'main.tex').read_text(encoding='utf-8')
source=(ROOT/'output/overleaf/aircraft_complete_loading_draft22/main.tex').read_text(encoding='utf-8')
labels=re.findall(r'\\label\{([^}]+)\}',text)
refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',text)
assert len(labels)==len(set(labels)) and not set(refs)-set(labels)
pos=0
for line in source.splitlines():
    if not line.strip():continue
    found=text.find(line,pos)
    assert found>=0,('Prior content missing',line[:90])
    pos=found+len(line)
audit=dict(status='COMPLETE_WORKING_DRAFT_NOT_SUBMISSION_APPROVED',pdf_pages=64,
    figures=len(re.findall(r'\\includegraphics',text)),tables=len(re.findall(r'\\begin\{table\}',text)),
    references=len(re.findall(r'\\bibitem',text)),original_draft22_narrative_and_figures_preserved=True,
    separate_review_layout_compiled=False,accepted_aircraft_modes=False,flight_proven=False)
(P/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
readme=(P/'README.md').read_text(encoding='utf-8').replace('Compilation/visual QA pending.',f'Reading PDF compiled and visually reviewed: 64 pages, {audit["figures"]} figures, {audit["tables"]} tables and {audit["references"]} references.')
(P/'README.md').write_text(readme,encoding='utf-8')
readiness=(P/'JOURNAL_READINESS.md').read_text().replace('Reading PDF QA pending','Reading PDF compiled and visually reviewed (64 pages)')
(P/'JOURNAL_READINESS.md').write_text(readiness)
for name in ('build_complete_draft23.py','finalize_complete_draft23.py'):
    shutil.copy2(ROOT/'analysis'/name,P/'audit_data'/name)
shutil.copy2(P/'main.pdf',ROOT/'output/pdf/aircraft_complete_structural_draft23.pdf')
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
