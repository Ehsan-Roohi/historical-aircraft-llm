"""Add loading, tail trade and mass-feedback evidence without shortening the master."""
import json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'output/overleaf/aircraft_complete_corrected_draft21'
DST=ROOT/'output/overleaf/aircraft_complete_loading_draft22'

def main():
    fine=json.loads((ROOT/'analysis/results/v15_fable_tail_trade01/fine.json').read_text())['cases']
    sensitivity=json.loads((ROOT/'analysis/results/v15_tail_reinforcement_sensitivity01/summary.json').read_text())
    extra=sensitivity['retrimmed_case']
    full=next(c for c in fine if c['fuel_kg']==8);empty=next(c for c in fine if c['fuel_kg']==0)
    budget=next(c for c in sensitivity['frozen_NP_budget_screen'] if c['fuel_kg']==0)['added_point_mass_budget_kg']['0.03']
    section=(ROOT/'paper/v15_loading_tail_update.tex').read_text(encoding='utf-8')
    values={'FULL_ALPHA':full['trim']['Alpha'],'FULL_CMA':full['Cma'],'EMPTY_ALPHA':empty['trim']['Alpha'],
            'EMPTY_CMA':empty['Cma'],'MASS_ALPHA':extra['trim']['Alpha'],'MASS_CMA':extra['Cma'],
            'MASS_SM':extra['surface_SM']*100,'BUDGET':budget}
    for k,v in values.items():section=section.replace('@'+k+'@',f'{v:.5f}')
    assert '@' not in section
    skip={'main.pdf','main.log','main_joa_review.pdf','main_joa_review.log','MANIFEST.json','PDF_QA.json','CONTENT_RECOVERY_AUDIT.json'}
    shutil.copytree(SRC,DST,ignore=lambda directory,names: [n for n in names if Path(directory)==SRC and n in skip])
    for name in ('main.tex','main_joa_review.tex'):
        text=(SRC/name).read_text(encoding='utf-8')
        marker=r'\section{Discussion: What the Wright Comparison Actually Shows}'
        assert text.count(marker)==1
        text=text.replace(marker,section+'\n'+marker)
        text=text.replace(r'\end{abstract}',r'Loading-specific re-trim exposes two negative-margin Fable cases. A separately labelled researcher tail enlargement reverses this tendency in the restricted surface model, but added structural mass consumes part of the gain and flight acceptance remains open.'+'\n'+r'\end{abstract}',1)
        marker=r'\section*{Data availability}'
        conclusion=r'''The loading-envelope check further narrows the nominal V15 result: the two light-pilot aft-CG states have negative surface-model margins despite equilibrium. A researcher-generated enlarged tail gives positive margins across eight coarse-grid loading states and two fine-grid critical states, but its structural and control redesign remain unresolved. The explicit added-mass sensitivity shows why aerodynamic restoration cannot be separated from mass and structural closure. This evaluator intervention is not an additional success attributed to Fable, and it does not establish a dynamically acceptable airplane.

'''
        text=text.replace(marker,conclusion+marker,1)
        text=text.replace('The local review ZIP accompanying this draft contains the V15 lateral-screen scripts, inputs, outputs and checksum manifest,','The local review ZIP accompanying this draft contains the V15 lateral-screen, loading-envelope, researcher tail-trade and added-mass sensitivity scripts, inputs, outputs and checksum manifest,')
        assert re.findall(r'\\includegraphics[^\n]+',text)==re.findall(r'\\includegraphics[^\n]+',(SRC/name).read_text(encoding='utf-8'))
        (DST/name).write_text(text,encoding='utf-8')
    (DST/'v15_loading_tail_update.tex').write_text(section,encoding='utf-8')
    data=DST/'audit_data';data.mkdir(exist_ok=True)
    for name in ('v15_fable_aft_retrim01','v15_fable_tail_trade01','v15_tail_reinforcement_sensitivity01'):
        shutil.copytree(ROOT/'analysis/results'/name,data/name)
    shutil.copy2(ROOT/'analysis/results/v15_fable_loading_gate01.json',data)
    for name in ('v15_fable_loading_gate.py','v15_fable_aft_retrim.py','v15_fable_tail_trade.py','v15_tail_reinforcement_sensitivity.py','audit_v15_tail_trade.py','test_v15_loading_gate.py','test_v15_tail_trade.py','build_complete_draft22.py'):
        shutil.copy2(ROOT/'analysis'/name,data/name)
    (DST/'README.md').write_text('# Complete loading-and-tail draft22\n\nOpen main.tex for the complete reading master; main_joa_review.tex retains the same content in a separate review layout. All 17 draft21 figures and prior narrative are preserved. New sections distinguish model-authored V15 from researcher-generated tail enlargement and an explicit two-kilogram sensitivity.\n\nCompilation and visual QA: pending. Not submission-approved; public deposition, structural closure, installed propulsion and dynamic modes remain open.\n',encoding='utf-8')
    (DST/'JOURNAL_READINESS.md').write_text('# Draft22 readiness\n\nComplete content retained. The main reading master will be compiled and visually checked. The separate review-layout source is not yet independently compiled. Added-mass sensitivity is not structural sizing. No accepted dynamic modes or flight claim. Public post-G8 release remains pending.\n',encoding='utf-8')
    print(json.dumps({'package':DST.name,'status':'source_built'}))

if __name__=='__main__':main()
