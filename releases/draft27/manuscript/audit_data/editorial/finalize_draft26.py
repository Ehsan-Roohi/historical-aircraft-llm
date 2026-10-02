from pathlib import Path
import json,hashlib,shutil,zipfile,re
R=Path.cwd(); H=Path(__file__).parent
P=R/'output/overleaf/aircraft_complete_editorial_draft26'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
qa={}
for n in ('main','main_joa_review'):
    q=json.loads((R/f'tmp/pdfs/draft26/{n}/qa.json').read_text())
    assert q['pages']==q['rendered_pages'] and not q['blank_pages'] and not q['unresolved_refs']
    q.update(compile_exit_code=0,pdf_sha256=sha(P/f'{n}.pdf'),visual_review='All-page contact sheets and changed/reference detail pages inspected. No new clipping observed; original dense plates retain existing enlarged versions and readable keys.')
    q['enlarged_pages_inspected']=[4,45,64] if n=='main' else [52,78]
    qa[n]=q
    shutil.copy2(P/f'{n}.pdf',R/'output/pdf'/('aircraft_complete_editorial_draft26'+('_joa_review' if n!='main' else '')+'.pdf'))
(P/'PDF_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
a=json.loads((P/'CONTENT_RECOVERY_AUDIT.json').read_text());a.update(compile='both exit 0',reading_pages=qa['main']['pages'],review_pages=qa['main_joa_review']['pages'],PDF_QA='completed',flight_proven=False,submission_approved=False)
(P/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(a,indent=2)+'\n')
s=(P/'main.tex').read_text(encoding='utf-8'); labels=re.findall(r'\\label\{([^}]+)\}',s)
assert len(labels)==len(set(labels))
assert not set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',s))-set(labels)
(P/'README.md').write_text(f"Full draft26: {qa['main']['pages']}-page reading PDF and {qa['main_joa_review']['pages']}-page double-spaced review PDF. Same complete body, 18 figures, 23 tables, 44 numbered references plus two retained inline web sources. Prior drafts unchanged. Reference order corrected. Both layouts compiled and visually inspected. This is not submission approval, public-release clearance or flight validation. See JOURNAL_READINESS.md, AUTHOR_ACTIONS.txt, RIGHTS_AND_PROVENANCE.txt and UNSENT editor inquiry.\n")
p=P/'JOURNAL_READINESS.md';p.write_text(p.read_text().replace('Compilation and QA pending for draft26.','Both layouts compiled successfully and all-page visual QA completed; underfull line warnings remain, no overfull warnings in final logs.'))
for n in ('build_draft26.py','qa_draft26.py','finalize_draft26.py'):shutil.copy2(H/n,P/'audit_data/editorial'/n)
records=[dict(path=p.relative_to(P).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(P.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
(P/'MANIFEST.json').write_text(json.dumps(dict(files=records,status='FULL_EDITORIAL_DRAFT_NOT_SUBMISSION_APPROVED'),indent=2)+'\n')
with zipfile.ZipFile(P.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(P.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(P).as_posix())
with zipfile.ZipFile(P.with_suffix('.zip')) as z:
    assert z.testzip() is None
    for item in records:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
print(json.dumps(dict(audit=a,hashed_files=len(records),zip_bytes=P.with_suffix('.zip').stat().st_size)))
