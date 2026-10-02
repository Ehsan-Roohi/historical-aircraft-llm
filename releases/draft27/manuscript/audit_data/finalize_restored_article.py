"""Package the compiled complete reading master after visual review."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'output/overleaf/aircraft_complete_restored_draft20'
qa=json.loads((ROOT/'tmp/pdfs/restored20/qa.json').read_text())
qa['visual_review']='All 61 pages inspected as contact sheets; full-size spot review of original plate and V15 tables. No clipped content or unresolved references observed. Dense original V0 labels remain accompanied by enlarged plates and readable keys. Reading master retains generous landscape page breaks; this is the complete master, not a length-edited submission.'
(P/'PDF_QA.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
a=json.loads((P/'CONTENT_RECOVERY_AUDIT.json').read_text())
a.update(pdf_compiled=True,pdf_pages=qa['pdf_pages'],pdf_text_words=qa['pdf_text_words'])
(P/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(a,indent=2)+'\n',encoding='utf-8')
readme=(P/'README.md').read_text()
readme=readme.replace('PDF compile status will be recorded separately after testing.','The integrated main.pdf successfully compiled locally with Tectonic 0.17.0: 61 pages, 17 figures, 17 tables, 45 references, and approximately 21,623 extracted words including captions/tables/references. All pages were rendered and reviewed at overview scale, with detailed spot checks. No missing references or blank pages were found. PDF_QA.json records this review. The separate main_joa_review.tex has the same content but has not been separately compiled.')
(P/'README.md').write_text(readme,encoding='utf-8')
status=P/'JOURNAL_READINESS.md'
s=status.read_text()
s='# Restored draft20 status update\n\nThe complete reading main.tex has now compiled to main.pdf (61 pages), and all pages have undergone visual overview review. The separate double-spaced review source has not been compiled. Historical compiler-block notes below describe draft19 and are superseded for this reading master. All scientific limitations and pending public-data release requirements remain. This file is retained as an editorial history; README.md and CONTENT_RECOVERY_AUDIT.json describe the delivered package.\n\n'+s
status.write_text(s,encoding='utf-8')
for name in ['restore_complete_manuscript.py','qa_restored_article.py','finalize_restored_article.py']:
    shutil.copy2(ROOT/'analysis'/name,P/'audit_data'/name)
destination=ROOT/'output/pdf/aircraft_complete_restored_draft20.pdf'
shutil.copy2(P/'main.pdf',destination)
records=[]
for f in sorted(P.rglob('*')):
    if f.is_file() and f.name!='MANIFEST.json':
        records.append({'path':f.relative_to(P).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'MANIFEST.json').write_text(json.dumps({'status':'COMPLETE_READING_MASTER_NOT_SUBMISSION_APPROVED','compiled_reading_pdf':True,'files':records},indent=2)+'\n',encoding='utf-8')
archive=P.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(P.rglob('*')):
        if f.is_file(): z.write(f,f.relative_to(P).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={r['path'] for r in records}|{'MANIFEST.json'}
    for r in records:
        assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
print(f'Complete reading master: {qa["pdf_pages"]} pages; ZIP verified with {len(records)} file hashes.')
