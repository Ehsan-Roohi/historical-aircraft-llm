from pathlib import Path
import shutil,re,json,hashlib
ROOT=Path.cwd(); HERE=Path(__file__).resolve().parent
SRC=ROOT/'output/overleaf/aircraft_complete_v16_power_draft25'
DST=ROOT/'output/overleaf/aircraft_complete_editorial_draft26'
skip={'main.pdf','main.log','main_joa_review.pdf','main_joa_review.log','MANIFEST.json','PDF_QA.json','CONTENT_RECOVERY_AUDIT.json'}
if not DST.exists():
    shutil.copytree(SRC,DST,ignore=lambda d,n:[x for x in n if Path(d)==SRC and x in skip])
changes=[]
for name in ('main.tex','main_joa_review.tex'):
    old=(SRC/name).read_text(encoding='utf-8'); s=old
    removed={}
    for key in ('ref14','ref45'):
        pattern=r'\\bibitem\{'+key+r'\}[^\n]+\n'
        found=re.search(pattern,s); assert found
        removed[key]=found.group();s=s[:found.start()]+s[found.end():]
    s=s.replace(r'\cite{ref41,ref45}',r"\cite{ref41} (The Franklin Institute, ``Exploring an Original 1911 Wright Model B Airplane,'' 2022, \url{https://fi.edu/en/blog/exploring-original-1911-wright-model-b-airplane}, accessed 30 September 2026)")
    s=s.replace(r'\cite{ref14}',r"(Wright Flyer Project, ``Structural Tests of the AIAA Wright Flyer,'' \url{https://www.wrightflyerproject.org/structural-testing}, accessed 26 September 2026)")
    oldref=re.search(r'\\bibitem\{ref1\}[^\n]+',s).group()
    newref=r'\bibitem{ref1} Chanute, O., \emph{Progress in Flying Machines}, American Engineer and Railroad Journal, New York, 1894. Digitized book, Library of Congress, LCCN 31015366, \url{https://www.loc.gov/item/31015366/}.'
    s=s.replace(oldref,newref)
    # Prevent tiny retained historical overrun without modifying its scientific prose.
    s=s.replace(r'\setlength{\emergencystretch}{3em}',r'\setlength{\emergencystretch}{5em}')
    (DST/name).write_text(s,encoding='utf-8')
    assert re.findall(r'\\includegraphics[^\n]+',s)==re.findall(r'\\includegraphics[^\n]+',old)
    assert s.count(r'\begin{table}')==old.count(r'\begin{table}')
    keys=re.findall(r'\\bibitem\{([^}]+)\}',s)
    cited=[]
    for group in re.findall(r'\\cite\{([^}]+)\}',s):
        for key in group.split(','):
            if key not in cited: cited.append(key)
    assert set(cited)==set(keys)
    entries={}
    for match in re.finditer(r'\\bibitem\{([^}]+)\}.*?(?=\\bibitem|\\end\{thebibliography\})',s,re.S):
        entries[match.group(1)]=match.group(0).rstrip()
    start=s.index(r'\bibitem'); end=s.index(r'\end{thebibliography}',start)
    s=s[:start]+'\n\n'.join(entries[key] for key in cited)+'\n'+s[end:]
    assert re.findall(r'\\bibitem\{([^}]+)\}',s)==cited
    (DST/name).write_text(s,encoding='utf-8')
    changes.append(dict(file=name,old_reference=oldref,new_reference=newref,web_entries_relocated_not_discarded=removed))
assert (DST/'main.tex').read_text().split(r'\begin{document}',1)[1]==(DST/'main_joa_review.tex').read_text().split(r'\begin{document}',1)[1]
auditdir=DST/'audit_data/editorial';auditdir.mkdir(exist_ok=True)
(auditdir/'reference_changes.json').write_text(json.dumps(changes,indent=2)+'\n')
shutil.copy2(Path(__file__),auditdir/'build_draft26.py')
# Redacted reporting: never output matching secret values.
patterns=[rb'sk-[A-Za-z0-9_-]{20,}',rb'ghp_[A-Za-z0-9]{20,}',rb'github_pat_[A-Za-z0-9_]{20,}',rb'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----']
hits=[]; localpaths=[]; binary=[]; count=0
for p in DST.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(DST).as_posix()
    if p.suffix.lower() in {'.json','.txt','.py','.js','.tex','.svg','.md','.avl','.dat'}:
        data=p.read_bytes();count+=1
        if any(re.search(pattern,data) for pattern in patterns):hits.append(rel)
        if re.search(rb'(?:C:[/\\]Users[/\\]|/work/pi_|/home/)',data):localpaths.append(rel)
    else:binary.append(dict(path=rel,bytes=p.stat().st_size))
report=dict(text_files_scanned=count,known_secret_signature_files=hits,local_machine_path_files=localpaths,
            binary_inventory=binary,public_release_approved=False,
            limitations='Pattern screen is not exhaustive privacy or copyright clearance. Raw prompt/source rights and local machine identifiers need a curated public export; originals must remain unchanged.')
(auditdir/'public_release_screen.json').write_text(json.dumps(report,indent=2)+'\n')
assert not hits, 'Credential-pattern matches: consult report paths; do not publish.'
(DST/'EDITOR_INQUIRY_DRAFT.txt').write_text('UNSENT DRAFT - author approval required\n\nSubject: Presubmission inquiry: full-length design-audit manuscript and length\n\nDear Editor,\n\nWould Journal of Aircraft consider a full-length research article entitled "Auditing Historically Constrained Language-Model Aircraft Against the Wright Flyer"? It reports three model-generated historical-aircraft concepts, retained design iterations, independent geometry and mass audits, conditional lifting-surface calculations, and propulsion sensitivity checks. It does not claim validated flight or complete dynamic-mode acceptance.\n\nThe complete manuscript is approximately 25,600 extracted PDF words, with 18 figures and 23 tables. This raw count is not the journal equivalent-word calculation. It exceeds the usual 10,000-12,000-word guidance. The author wishes to retain the integrated design history rather than replace it with a short paper and separate supplement. Before submission, could you advise whether this length and research framing are suitable, or whether a different scope is required?\n\nThe manuscript discloses model-generated designs and AI assistance in drafting, code and figures. A fixed post-G8 public evidence release is being prepared. This inquiry is not a submission and no approval has yet been obtained.\n\nSincerely,\nEhsan Roohi\n')
(DST/'RIGHTS_AND_PROVENANCE.txt').write_text('Prepublication evidence record, not legal certification.\nHistorical flight photograph: Library of Congress item 00652085, rights advisory "No known restrictions on publication" (catalog search checked 2026-09-30), source https://www.loc.gov/item/00652085/. The Library does not grant a license or guarantee all uses; credit remains in caption.\nGenerated design plates and evaluator drawings: retain existing source SVG, model/evaluator attribution and hashes; AI assistance disclosed. Do not represent these as measured hardware or original historical engineering drawings.\nBooks, journal PDFs and private course scans: not authorized for wholesale redistribution. Curate any public export by file inventory and source rights, not by suffix alone.\nSource datasets/scripts carry provenance paths. Public release screen flags local paths separately from credential signatures. No new release or universal license has been declared.\n')
(DST/'JOURNAL_READINESS.md').write_text('Draft26 editorial follow-up. Two nonarchival web entries moved to parenthetical text, with source URLs retained and original entries archived. Chanute book publisher/location corrected from Library of Congress record. Remaining 44 numbered references are in first-citation order with no missing keys; this is not a claim that every bibliographic field was independently reverified. Complete body, 18 figures and 23 tables retained.\nOfficial sources checked 2026-09-30: https://aiaa.org/publications/journals/reference-style-and-format/ ; https://aiaa.org/publications/journals/journal-author/ ; https://aiaa.org/publications/journals/journal-scopes-and-content/ .\nLength: approximately 25,600 PDF-extracted words, above usual 10,000-12,000 equivalent-word guidance; UNSENT editor inquiry prepared. No editor approval claimed and no automatic shortening.\nOpen: author title/affiliation/funding/conflicts confirmation; full human scientific and image-rights review; curated public release after privacy/source review; engineering evidence for installed trim, inertia, derivatives and modes. No flight acceptance. Compilation and QA pending for draft26.\n')
(DST/'AUTHOR_ACTIONS.txt').write_text('Required author input: current title and affiliation, correspondence email, funding/grant numbers, conflicts of interest. Requested in chat; no no-conflict or no-funding statement invented.\nDecisions requiring author/editor coordination: approve sending the unsent length/scope inquiry, and accept the resulting manuscript scope. Do not contact the editor without explicit messaging approval.\nPublic release requires curated handling of flagged machine paths and source rights. The package has passed only known-secret-pattern screening; no public tag created.\nScientific limitations cannot be cured by prose: supply/validate propulsion map, sections/stall, structural properties and physical inertia before accepted modes or flight claims.\n')
(DST/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(dict(figures_preserved=18,tables_preserved=23,numbered_references=44,web_sources_relocated=2,body_shortened=False,identical_layout_body=True,reference_order_pass=True,compile='pending'),indent=2)+'\n')
print(json.dumps(dict(status='draft26 source prepared',text_files_scanned=count,credential_pattern_hits=len(hits),files_with_local_paths=len(localpaths))))
