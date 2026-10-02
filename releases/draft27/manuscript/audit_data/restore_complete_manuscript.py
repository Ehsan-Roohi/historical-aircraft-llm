"""Restore one-file reading access to all draft19 article and supplement content."""
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'output/overleaf/aircraft_joa_2026_09_29_draft19'
DST = ROOT / 'output/overleaf/aircraft_complete_restored_draft20'

def main():
    if DST.exists() and '--resume-build' not in sys.argv:
        raise FileExistsError('Preserve existing restored package')
    if not DST.exists():
        shutil.copytree(SRC, DST)
    article = (SRC/'main.tex').read_text(encoding='utf-8')
    supp = (SRC/'supplementary.tex').read_text(encoding='utf-8')
    # Inline every local input, including the reference list, into one main source.
    article = re.sub(r'\\input\{([^}]+)\}', lambda m: (SRC/m[1]).read_text(encoding='utf-8'), article)
    fig_labels = ['wrightthree','astra','fable','opus','wright','pitch']
    table_labels = ['interpolated','loads','residual','stability','architecture','v2','stage','derivativegate','reduceddynamic','v1v2dynamic','v3returns']
    for i, label in reversed(list(enumerate(fig_labels, 1))):
        article = re.sub(r'Supplementary Fig\.~S'+str(i)+r'(?!\d)', lambda _: r'Figure~\ref{fig:'+label+'}', article)
    for i, label in reversed(list(enumerate(table_labels, 1))):
        article = re.sub(r'Supplementary Table~S'+str(i)+r'(?!\d)', lambda _: r'Table~\ref{tab:'+label+'}', article)
    # Extract whole plates WITH their readable component keys.
    figs, tables = supp.split(r'\section*{Supplementary tables}', 1)
    figs = figs.split(r'\section*{Supplementary figures}', 1)[1]
    pattern = r'(?:\\begin\{landscape\}\s*)?\\begin\{figure\}.*?\\end\{figure\}(?:\s*\\end\{landscape\})?'
    matches = list(re.finditer(pattern, figs, re.S))
    chunks = []
    for i, m in enumerate(matches):
        end = matches[i+1].start() if i+1 < len(matches) else len(figs)
        chunk = figs[m.start():end].strip()
        label = re.search(r'\\label\{([^}]+)\}', chunk)[1]
        chunks.append((label, chunk))
    # Attach enlarged details to their original plate, preserving both keys.
    grouped = {}
    for label, chunk in chunks:
        parent = label.replace('detail','')
        grouped[parent] = grouped.get(parent,'') + '\n\n' + chunk
    placements = []
    for label, chunk in grouped.items():
        token = r'\ref{'+label+'}'
        at = article.find(token)
        if at < 0:
            raise ValueError('Missing figure discussion '+label)
        boundary = article.find('\n\n', at)
        article = article[:boundary]+'\n\n'+chunk+article[boundary:]
        placements.append(label)
    tables = tables.replace(r'\end{document}', '').strip()
    matches = list(re.finditer(r'\\begin\{table\}.*?\\end\{table\}', tables, re.S))
    previous = 0
    extra = []
    for m in matches:
        chunk = tables[previous:m.end()].strip()
        previous = m.end()
        label = re.search(r'\\label\{([^}]+)\}', m[0])[1]
        at = article.find(r'\ref{'+label+'}')
        if at < 0:
            extra.append(chunk)
        else:
            boundary = article.find('\n\n', at)
            article = article[:boundary]+'\n\n'+chunk+article[boundary:]
        placements.append(label)
    if tables[previous:].strip():
        extra.append(tables[previous:].strip())
    if extra:
        marker = r'\section{Limitations and Reproducibility}'
        article = article.replace(marker, r'\subsection{Detailed integrated design-return records}'+'\n\n'+'\n\n'.join(extra)+'\n\n'+marker)
    # Remove accidental double landscape wrappers inherited by V2 views.
    article = re.sub(r'(\\begin\{landscape\}\s*){2}', lambda _: '\\begin{landscape}\n', article)
    article = re.sub(r'(\\end\{landscape\}\s*){2}', lambda _: '\\end{landscape}\n\n', article)
    old = ROOT/'output/overleaf/aircraft_journal_figures_expanded_2026_09_27/main.tex'
    old_images = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{\\figdir/([^}]+)\}', old.read_text(encoding='utf-8'))
    current_images = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{\\figdir/([^}]+)\}', article)
    for name in sorted(set(old_images)-set(current_images)):
        shutil.copy2(old.parent/'figures'/name,DST/'figures'/name)
        plate = '\n'+r'\subsection{Retained earlier configuration comparison}'+'\n'+r'This earlier V1 comparison plate is retained alongside the updated presentation to preserve the complete drawing record. It does not describe the latest V15 installation.'+'\n'+r'\begin{landscape}\begin{figure}[H]\centering'+'\n'+r'\includegraphics[width=.96\linewidth,height=.76\textheight,keepaspectratio]{\figdir/'+name+'}\n'+r'\caption{Earlier V1 configuration-comparison plate retained from the complete September 27 manuscript.}\label{fig:earliercomparison}'+'\n'+r'\end{figure}\end{landscape}'+'\n'
        article=article.replace(r'\section{Limitations and Reproducibility}',plate+'\n'+r'\section{Limitations and Reproducibility}')
    article=article.replace(r'\usepackage{url}',r'\usepackage{xurl}')
    article=article.replace(r'\includegraphics[width=.96\linewidth]{\figdir/configuration_comparison_v3.png}',r'\includegraphics[width=.96\linewidth,height=.74\textheight,keepaspectratio]{\figdir/configuration_comparison_v3.png}')
    article=article.replace('The diagonal $(J_{xx},J_{yy},\nJ_{zz})$ contributions are $(282.406,522.525,668.278)$ kg m$^2$ for Fable\nand $(131.713,914.293,782.580)$ kg m$^2$ for Opus.', 'The diagonal contributions, in kg m$^2$, are\n'+r'\begin{align*}'+'\n'+r'\text{Fable:}\quad (J_{xx},J_{yy},J_{zz})&=(282.406,522.525,668.278),\\'+'\n'+r'\text{Opus:}\quad (J_{xx},J_{yy},J_{zz})&=(131.713,914.293,782.580).'+ '\n'+r'\end{align*}')
    # The full reading version and JoA review version contain identical content.
    review = article
    reading = article.replace(r'\documentclass[10pt,letterpaper]{article}', r'\documentclass[11pt,a4paper]{article}')
    reading = reading.replace(r'\usepackage[margin=1in]{geometry}', r'\usepackage[margin=22mm]{geometry}')
    reading = reading.replace(r'\linespread{1.667}\selectfont', r'\linespread{1.08}\selectfont')
    (DST/'main.tex').write_text(reading, encoding='utf-8')
    (DST/'main_joa_review.tex').write_text(review, encoding='utf-8')
    # Preserve the earlier complete source for an explicit recovery trail.
    archive = DST/'recovery_sources'
    archive.mkdir(exist_ok=True)
    shutil.copy2(SRC/'main.tex', archive/'draft19_main_before_integration.tex')
    shutil.copy2(SRC/'supplementary.tex', archive/'draft19_supplement_before_integration.tex')
    shutil.copy2(old, archive/'expanded_27sep_original.tex')
    labels = re.findall(r'\\label\{([^}]+)\}', reading)
    assert len(labels) == len(set(labels)), 'Duplicate labels'
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', reading)
    assert not set(refs)-set(labels), set(refs)-set(labels)
    images = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{\\figdir/([^}]+)\}', reading)
    assert all((DST/'figures'/name).exists() for name in images)
    old_images = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{\\figdir/([^}]+)\}', old.read_text(encoding='utf-8'))
    missing_old = sorted(set(old_images)-set(images))
    assert not missing_old, missing_old
    # Every supplementary figure/table and key must occur verbatim in master.
    assert all(chunk.strip() in article for _,chunk in chunks)
    assert all(m[0] in article for m in matches)
    audit = {'status':'COMPLETE_READING_MASTER_NOT_SUBMISSION_APPROVED',
             'figures_in_single_main':len(images), 'tables_in_single_main':len(matches)+len(re.findall(r'\\begin\{table\}', (SRC/'main.tex').read_text(encoding='utf-8')))+2,
             'all_11_earlier_figure_assets_retained':not missing_old,
             'all_supplementary_plates_keys_tables_preserved':True,
             'undefined_refs':[], 'duplicate_labels':[], 'placements':placements,
             'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SRC/'main.tex',SRC/'supplementary.tex',old]},
             'pdf_compiled':False}
    audit['tables_in_single_main']=len(re.findall(r'\\begin\{table\}',reading))
    (DST/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    (DST/'README.md').write_text('''# Complete restored aircraft manuscript - draft20

Open **main.tex** for the complete integrated article. All 17 figures, detailed component keys, design-stage discussion, numerical tables, Wright history and V15 screens are in ONE document. No separate supplement is needed to read them. This is an A4 reading layout; **main_joa_review.tex** contains the same content in the longer double-spaced US-letter review layout. Page count therefore differs, but content is identical.

Earlier source files are retained under recovery_sources. The independent supplementary.tex is retained only for provenance and optional separate export. Do not select it as the main document. V0, V1, V2 and V15 evidence retain their version labels; drawings of V2 are not claimed as V15 drawings. The complete reading master is not yet submission-approved or a flightworthiness demonstration. Data-release and technical limitations remain explicit in the text.

CONTENT_RECOVERY_AUDIT.json records figure/table restoration and reference checks. PDF compile status will be recorded separately after testing.
''',encoding='utf-8')
    records=[]
    for path in sorted(DST.rglob('*')):
        if path.is_file() and path.name!='MANIFEST.json':
            records.append({'path':path.relative_to(DST).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
    (DST/'MANIFEST.json').write_text(json.dumps({'status':'COMPLETE_READING_MASTER_NOT_SUBMISSION_APPROVED','files':records},indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(DST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DST.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(DST).as_posix())
    print(json.dumps(audit,ensure_ascii=True))

if __name__=='__main__': main()
