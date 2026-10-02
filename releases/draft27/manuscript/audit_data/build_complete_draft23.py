"""Preserve draft22 and append the audited structural loop and vector diagram."""
from pathlib import Path
import shutil,json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'output/overleaf/aircraft_complete_loading_draft22'
DST=ROOT/'output/overleaf/aircraft_complete_structural_draft23'
def main():
    skip={'main.pdf','main.log','main_joa_review.pdf','main_joa_review.log','MANIFEST.json','PDF_QA.json','CONTENT_RECOVERY_AUDIT.json'}
    shutil.copytree(SRC,DST,ignore=lambda d,n:[v for v in n if Path(d)==SRC and v in skip])
    section=(ROOT/'paper/v15_structural_loop_update.tex').read_text(encoding='utf-8')
    for name in ('main.tex','main_joa_review.tex'):
        s=(SRC/name).read_text(encoding='utf-8')
        marker=r'\section{Discussion: What the Wright Comparison Actually Shows}'
        assert s.count(marker)==1
        s=s.replace(marker,section+'\n'+marker)
        s=s.replace(r'\end{thebibliography}',r'''\bibitem{ref46} Senalik, C. A., and Farber, B., ``Mechanical Properties of Wood,'' Chapter 5 in \emph{Wood Handbook: Wood as an Engineering Material}, General Technical Report FPL-GTR-282, U.S. Department of Agriculture, Forest Service, Forest Products Laboratory, Madison, WI, 2021. \url{https://research.fs.usda.gov/download/treesearch/62244.pdf}.
\end{thebibliography}''')
        (DST/name).write_text(s,encoding='utf-8')
    shutil.copy2(ROOT/'paper/v15_structural_loop_update.tex',DST)
    for ext in ('pdf','svg','png'):
        shutil.copy2(ROOT/f'analysis/results/v15_braced_tail_figure01/braced_tail_concept.{ext}',DST/'figures')
    data=DST/'audit_data'
    for dirname in ('v15_tail_strip_loads01','v15_tail_spar_mass_loop01'):
        shutil.copytree(ROOT/'analysis/results'/dirname,data/dirname)
    shutil.copy2(ROOT/'analysis/results/v15_braced_tail_candidate01.json',data)
    for name in ('v15_tail_strip_loads.py','audit_v15_tail_beam_demands.py','v15_tail_spar_mass_loop.py','v15_braced_tail_candidate.py','figure_braced_tail.py','build_complete_draft23.py'):
        shutil.copy2(ROOT/'analysis'/name,data)
    (DST/'README.md').write_text('# Complete structural-loop draft23\n\nComplete draft22 text and figures retained. Added strip-load/beam-demand audit, an unsuccessful additive-spar mass feedback experiment, and a clearly labelled researcher braced-tail concept with a vector three-view figure. No structural or flight acceptance is asserted.\n\nCompilation/visual QA pending. main.tex is the complete reading master; main_joa_review.tex is the same content in a separate, uncompiled review layout. Post-G8 public deposition remains pending.\n',encoding='utf-8')
    (DST/'JOURNAL_READINESS.md').write_text('# Working draft23\n\nNot submission-approved. Reading PDF QA pending; separate review-layout source not compiled. Structural mass budget, joint design, installed aerodynamics/propulsion and full dynamic modes remain open. Modern wood-property averages are not aircraft allowables or original historical-model inputs.\n')
    print(json.dumps({'package':DST.name}))
if __name__=='__main__':main()
