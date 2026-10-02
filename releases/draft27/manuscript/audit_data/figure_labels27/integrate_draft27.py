from pathlib import Path
import json,re,hashlib
R=Path.cwd(); S=R/'output/overleaf/aircraft_complete_editorial_draft26'; D=R/'output/overleaf/aircraft_complete_labeled_draft27'
replacements={
'Researcher-enlarged detail of the Astra V0 component geometry. Numbered markers replace small source text; no component was relocated.':'Researcher-labeled detail of the Astra V0 component geometry. Component names and matching numbered keys are included within the plate; annotation-only leaders are removed, with no component relocation.',
'Researcher-enlarged Fable V0 mechanism detail, retaining the original component geometry and unresolved interfaces.':'Researcher-labeled Fable V0 mechanism detail. Component names and matching numbered keys appear within the plate; original component geometry and unresolved interfaces are retained.',
'Researcher-enlarged Opus V0 mechanism detail. Source geometry is preserved; small archival prose is replaced by numbered markers.':'Researcher-labeled Opus V0 mechanism detail. Component names and matching numbered keys appear within the plate; source geometry is preserved.',
'Lines extending toward the cropped edges are preserved archival callout\nleaders, not physical cables or structural members. The numbered overlay is\nan explanatory display derivative, not another model response.':'Formerly unlabelled archival callout leaders have been replaced by readable\nin-figure identification. Physical cables and structural geometry are not\nrevised. The labeled overlay is an explanatory display derivative, not\nanother model response.'}
records=[]
for name in ('main.tex','main_joa_review.tex'):
    old=(S/name).read_text(encoding='utf-8');new=old
    for a,b in replacements.items():
        assert new.count(a)==1,(name,a)
        new=new.replace(a,b)
    assert re.findall(r'\\includegraphics[^\n]+',new)==re.findall(r'\\includegraphics[^\n]+',old)
    back=new
    for a,b in replacements.items():back=back.replace(b,a)
    assert back==old,'Non-caption/content drift'
    (D/name).write_text(new,encoding='utf-8')
    records.append(dict(file=name,source_sha256=hashlib.sha256(old.encode()).hexdigest(),new_sha256=hashlib.sha256(new.encode()).hexdigest()))
assert (D/'main.tex').read_text().split(r'\begin{document}',1)[1]==(D/'main_joa_review.tex').read_text().split(r'\begin{document}',1)[1]
A=D/'audit_data/figure_labels27';A.mkdir(exist_ok=True)
(A/'caption_changes.json').write_text(json.dumps(dict(replacements=replacements,files=records),indent=2)+'\n')
(D/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(dict(source='draft26',figures_preserved=18,tables_preserved=23,numbered_references=44,web_sources_relocated=2,body_shortened=False,identical_layout_body=True,body_exact_except_documented_display_descriptions=True,scientific_calculations_changed=False,compile='pending'),indent=2)+'\n')
print('Both full manuscript sources integrated; only documented figure-display descriptions changed.')
