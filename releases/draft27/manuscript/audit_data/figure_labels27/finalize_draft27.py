from pathlib import Path
import json,hashlib,shutil,zipfile,re
R=Path.cwd();H=Path(__file__).parent
P=R/'output/overleaf/aircraft_complete_labeled_draft27';S=R/'output/overleaf/aircraft_complete_editorial_draft26'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
qa={}
for n in ('main','main_joa_review'):
    q=json.loads((R/f'tmp/pdfs/draft27/{n}/qa.json').read_text())
    assert q['pages']==q['rendered_pages'] and not q['blank_pages'] and not q['unresolved_refs']
    q.update(compile_exit_code=0,pdf_sha256=sha(P/f'{n}.pdf'),visual_review='All pages inspected in contact sheets; all three relabeled figure pages inspected enlarged. Figure geometry preserved; names/keys now in-frame.',enlarged_pages_inspected=[p for p in q['detail_pages'] if p!=1])
    qa[n]=q
    shutil.copy2(P/f'{n}.pdf',R/'output/pdf'/('aircraft_complete_labeled_draft27'+('_joa_review' if n!='main' else '')+'.pdf'))
(P/'PDF_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
a=json.loads((P/'CONTENT_RECOVERY_AUDIT.json').read_text());a.update(compile='both exit 0',reading_pages=qa['main']['pages'],review_pages=qa['main_joa_review']['pages'],PDF_QA='completed',flight_proven=False,submission_approved=False)
changed={'astra_oblique_v0_detail.png','fable_oblique_v0_detail.png','opus_oblique_v0_detail.png'}
for f in (S/'figures').iterdir():
    if f.is_file() and f.name not in changed:assert sha(f)==sha(P/'figures'/f.name)
a['other_figure_assets_byte_identical']=True
(P/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(a,indent=2)+'\n')
(P/'README.md').write_text(f"Full draft27: {qa['main']['pages']} reading pages / {qa['main_joa_review']['pages']} double-spaced review pages. Three V0 detail figures now include source-matched English component names and numbered identification inside each plate. Annotation-only remnants removed; aircraft geometry unchanged. 18 figures,23 tables,44 numbered references plus two inline web sources retained. All other figure assets byte-identical to draft26; original V0 plates and prior drafts retained. Both PDF layouts compiled and visually checked. No engineering or submission approval claimed.\n")
f=P/'JOURNAL_READINESS.md';f.write_text(f.read_text()+ '\nDraft27: display-label corrections only; both PDF layouts recompiled and visually checked. All scientific limitations and author/publication actions remain open as in draft26.\n')
A=P/'audit_data/figure_labels27'
for n in ('integrate_draft27.py','qa_draft27.py','finalize_draft27.py'):shutil.copy2(H/n,A/n)
records=[dict(path=p.relative_to(P).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(P.rglob('*')) if p.is_file() and p!=P/'MANIFEST.json']
(P/'MANIFEST.json').write_text(json.dumps(dict(files=records,status='FULL_LABELED_DRAFT_NOT_SUBMISSION_APPROVED'),indent=2)+'\n')
with zipfile.ZipFile(P.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(P.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(P).as_posix())
with zipfile.ZipFile(P.with_suffix('.zip')) as z:
    assert z.testzip() is None
    for x in records:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
print(json.dumps(dict(audit=a,hashed_files=len(records),zip_bytes=P.with_suffix('.zip').stat().st_size)))
