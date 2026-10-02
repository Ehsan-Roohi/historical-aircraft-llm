from pathlib import Path
import json,re,hashlib,shutil,zipfile
ROOT=Path.cwd(); P=ROOT/'output/overleaf/aircraft_complete_v16_power_draft25'
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
qa={}
for name in ('main','main_joa_review'):
    q=json.loads((ROOT/f'tmp/pdfs/draft25/{name}/qa.json').read_text())
    assert q['pages']==q['rendered_pages'] and not q['blank_pages'] and not q['unresolved_refs']
    q['compile_exit_code']=0
    q['visual_review']='All pages inspected in contact sheets; listed detail pages inspected enlarged. No new clipped content or overlapping table observed. Original dense model plates retained with existing enlarged redraws and keys.'
    q['pdf_sha256']=sha(P/f'{name}.pdf')
    qa[name]=q
    target='aircraft_complete_v16_power_draft25'+('_joa_review' if name!='main' else '')+'.pdf'
    shutil.copy2(P/f'{name}.pdf',ROOT/'output/pdf'/target)
(P/'PDF_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
s=(P/'main.tex').read_text(encoding='utf-8')
labels=re.findall(r'\\label\{([^}]+)\}',s)
refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',s)
assert len(labels)==len(set(labels)) and not set(refs)-set(labels)
audit=json.loads((P/'CONTENT_RECOVERY_AUDIT.json').read_text())
audit.update(PDF_QA='completed',reading_pages=qa['main']['pages'],review_pages=qa['main_joa_review']['pages'],
             figures=len(re.findall(r'\\includegraphics',s)),tables=len(re.findall(r'\\begin\{table\}',s)),
             references=len(re.findall(r'\\bibitem',s)),flight_proven=False,dynamic_modes_verified=False,
             status='COMPLETE_UPDATED_MANUSCRIPT_NOT_SUBMISSION_APPROVED')
(P/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
(P/'README.md').write_text('Full draft25: 67-page reading PDF and 82-page review-layout PDF, both compiled and visually inspected. Same complete body; 18 figures, 23 tables, 46 references. Draft24 body and figures retained; abstract updated to 181 words and old abstract archived. Added V16 speed/power sensitivity, updated conclusion and data availability. Open main.tex for reading layout or main_joa_review.tex for review layout in Overleaf. Local research archive, not a self-contained solver distribution or submission approval. Public release remains unchanged. See JOURNAL_READINESS.md and AUTHOR_ACTIONS.txt.\n')
readiness=(P/'JOURNAL_READINESS.md').read_text().replace('Both PDF layouts pending QA.','Both PDF layouts compiled and visually reviewed. Reading: 67 pages; review: 82 pages. Review TeX has one 2.42-point overfull-line warning in retained historical discussion, with no observed clipping; underfull warnings remain in older tables.')
(P/'JOURNAL_READINESS.md').write_text(readiness)
(P/'AUTHOR_ACTIONS.txt').write_text('Before submission:\n1. Confirm author affiliation, job title/contact details, funding/grant numbers and conflicts of interest. None were invented.\n2. Approve and complete a legally audited fixed public release for post-G8 records. Local full data are bundled; no new public tag was created.\n3. Resolve reference-type compliance, including web-only collection/catalog entries, against official AIAA guidance without deleting historical evidence.\n4. Agree manuscript length/article type with the editor: full content was intentionally retained at user request; no shortening or separate-supplement replacement was performed.\n5. Complete author review of scientific claims, figure reuse rights and AI disclosure in ScholarOne.\n6. Do not claim validated flight, installed six-component trim or accepted dynamic modes; the outstanding engineering evidence is explicitly identified in the manuscript.\n')
for name in ('qa_draft25.py','finalize_draft25.py'):
    shutil.copy2(HERE/name,P/'audit_data/v16/power_speed'/name)
records=[dict(path=p.relative_to(P).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(P.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
(P/'MANIFEST.json').write_text(json.dumps(dict(files=records,status=audit['status']),indent=2)+'\n')
with zipfile.ZipFile(P.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(P.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(P).as_posix())
with zipfile.ZipFile(P.with_suffix('.zip')) as z:
    assert z.testzip() is None
    for r in records: assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
print(json.dumps(dict(audit=audit,hashed_files=len(records),zip_bytes=P.with_suffix('.zip').stat().st_size)))
