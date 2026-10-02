"""Freeze corrected full-manuscript package after compilation and visual QA."""
import hashlib,json,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'output/overleaf/aircraft_complete_corrected_draft21'
qa=json.loads((ROOT/'tmp/pdfs/corrected21/qa.json').read_text())
assert not qa['blank_pages'] and not qa['double_question_marks']
qa['visual_review']='All rendered pages inspected in contact sheets; changed numerical section inspected at larger resolution. Original dense V0 figures remain accompanied by enlarged detail figures and readable keys.'
(P/'PDF_QA.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
text=(P/'main.tex').read_text(encoding='utf-8')
labels=re.findall(r'\\label\{([^}]+)\}',text)
refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',text)
assert len(labels)==len(set(labels)) and not set(refs)-set(labels)
source=(ROOT/'output/overleaf/aircraft_complete_restored_draft20/main.tex').read_text(encoding='utf-8')
assert re.findall(r'\\includegraphics[^\n]+',text)==re.findall(r'\\includegraphics[^\n]+',source)
audit={'status':'COMPLETE_CORRECTED_MASTER_NOT_SUBMISSION_APPROVED','pdf_compiled':True,'pdf_pages':qa['pdf_pages'],'figures':17,'tables':len(re.findall(r'\\begin\{table\}',text)),'all_draft20_figure_inclusions_preserved':True,'old_draft20_unchanged':True,'undefined_references':[],'correction':'Explicit evaluator component, vertical discretization and full-chord tail command corrections; old numerical results retained as superseded history.'}
(P/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
readme=(P/'README.md').read_text(encoding='utf-8')
readme=readme.replace('The PDF and manifest must be refreshed after compilation; source completeness is checked against draft20.',f'The reading PDF has successfully compiled ({qa["pdf_pages"]} pages, 17 figures, {audit["tables"]} tables). All pages were rendered and visually reviewed. All draft20 figure inclusions are preserved. The separate double-spaced review source has not been independently compiled. Local post-G8 evidence still awaits a fixed public release.')
(P/'README.md').write_text(readme,encoding='utf-8')
(P/'JOURNAL_READINESS.md').write_text('# Corrected complete draft21\n\nThe reading master is compiled and visually checked; see PDF_QA.json. All figures and the complete article are retained. Corrected evaluator predictions now replace the invalid split-tip input conclusions, with the error and old records retained explicitly. The separate review-layout source still needs its own compile. Public V14/V15 deposition, physical inertia, unsteady aerodynamics, installed propulsion, whole-aircraft trim and modes remain unresolved. The full reading master is not submission-approved.\n',encoding='utf-8')
shutil.copy2(P/'main.pdf',ROOT/'output/pdf/aircraft_complete_corrected_draft21.pdf')
shutil.copy2(ROOT/'analysis/finalize_corrected_draft21.py',P/'audit_data/finalize_corrected_draft21.py')
records=[]
for p in sorted(P.rglob('*')):
    if p.is_file() and p.name!='MANIFEST.json':records.append({'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(P/'MANIFEST.json').write_text(json.dumps({'status':audit['status'],'files':records},indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(P.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(P.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(P).as_posix())
with zipfile.ZipFile(P.with_suffix('.zip')) as z:
    assert z.testzip() is None
    for r in records:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
print(json.dumps(audit))
