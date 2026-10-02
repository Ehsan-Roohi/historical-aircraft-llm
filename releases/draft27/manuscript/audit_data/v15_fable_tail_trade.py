"""Evaluator tail-span trade, NOT an LLM revision or flight-approved design.

Span extensions carry constant assumed areal mass. New reinforcement mass is
unknown, not claimed zero; this is a conditional aerodynamic trade only.
"""
import argparse
import copy
import json
from pathlib import Path
from v15_fable_loading_gate import ledger
from v15_fable_corrected_surface_screen import run,parse_st,sha
from avl_reference_gate import parse

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'output/received_v15_65023104/claude-fable-5-1/response.json'
OUT=ROOT/'analysis/results/v15_fable_tail_trade01'
CASES=[(75,.30,8),(75,.35,8),(75,.25,8),(75,.30,0),
       (65,.35,8),(65,.35,0),(85,.25,8),(85,.25,0)]

def candidate_rows(design,scale,pilot,seat,fuel):
    rows=copy.deepcopy(design['section_3_mass_ledger']['rows'])
    for r in rows:
        if r['ID'] in ('P11L','P11R'):
            length=2.3*scale;m=4*scale
            r['mass_kg']=m
            r['centroid'][1]=(1 if r['ID']=='P11R' else -1)*(.55+length/2)
            r['I_intr']=[m*length**2/12,m/12,m*(length**2+1)/12]
        if r['ID']=='P05':
            r['mass_kg']=pilot;r['centroid'][0]=seat
            r['I_intr']=[v*pilot/75 for v in r['I_intr']]
        if r['ID']=='P07b':
            r['mass_kg']=fuel;r['I_intr']=[v*fuel/8 for v in r['I_intr']]
    return rows

def one(design,scale,case,mesh,phase):
    pilot,seat,fuel=case
    folder=OUT/f'{phase}_s{scale:.2f}_p{pilot}_x{seat:.2f}_f{fuel}_{mesh}'
    folder.mkdir(parents=True,exist_ok=False)
    rows=candidate_rows(design,scale,pilot,seat,fuel)
    mass,cg,inertia,pxz=ledger(rows)
    src=ROOT/f'analysis/results/v15_fable_corrected_surface02/{mesh}'
    geom=(src/'aircraft.avl').read_text()
    lines=geom.splitlines();lines[4]=' '.join(f'{v:.10f}' for v in cg)
    geom='\n'.join(lines)+'\n'
    pre,tail=geom.split('SURFACE\ntail_halves\n')
    block,post=tail.split('SURFACE\nfin_fixed\n')
    assert block.count('2.850000')==1
    block=block.replace('2.850000',f'{.55+2.3*scale:.6f}')
    geom=pre+'SURFACE\ntail_halves\n'+block+'SURFACE\nfin_fixed\n'+post
    (folder/'aircraft.avl').write_text(geom,encoding='ascii')
    (folder/'section.dat').write_bytes((src/'section.dat').read_bytes())
    (folder/'assumed_mass_ledger.json').write_text(json.dumps(rows,indent=2)+'\n')
    target=mass*9.80665/(.5*1.225*13**2*42)
    run(folder,f'load aircraft.avl\noper\na a 5.8\nd2 d2 -4\na c {target:.12f}\nd2 pm 0\nx\nft\nforces.txt\nst\nstability.txt\n\nquit\n')
    trim={k:parse((folder/'forces.txt').read_text(),k) for k in ('Alpha','pitch','CLtot','Cmtot','CDind')}
    assert abs(trim['CLtot']-target)<2e-4 and abs(trim['Cmtot'])<2e-4
    st=parse_st((folder/'stability.txt').read_text())
    absolute=trim['pitch']-4
    r=dict(phase=phase,scale=scale,tail_area_m2=4.6*scale,tail_outer_y_m=.55+2.3*scale,
           pilot_kg=pilot,seat_x_m=seat,fuel_kg=fuel,mesh=mesh,mass_kg=mass,cg_m=cg,
           assumed_inertia_diagonal_kgm2=inertia,centroid_only_Pxz_kgm2=pxz,
           trim=trim,absolute_tail_deg=absolute,within_declared_tail_travel=-16<=absolute<=8,
           surface_SM=-st['Cma']/st['CLa'],Cma=st['Cma'],CLa=st['CLa'],Cmq=st['Cmq'],
           input_sha256=sha(folder/'aircraft.avl'),forces_sha256=sha(folder/'forces.txt'),stability_sha256=sha(folder/'stability.txt'))
    (folder/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ('phase','scale','pilot_kg','fuel_kg','mesh','surface_SM','mass_kg','absolute_tail_deg')}),flush=True)
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['trade','trade_extended','envelope','fine']);a=ap.parse_args()
    d=json.loads(json.loads(SOURCE.read_text(encoding='utf-8'))['response'])
    OUT.mkdir(exist_ok=True)
    if a.phase=='trade':
        results=[one(d,s,(65,.35,8),'coarse','trade') for s in (1.15,1.30,1.50)]
        eligible=[r for r in results if r['surface_SM']>=.03 and r['within_declared_tail_travel']]
        selected=min((r['scale'] for r in eligible),default=None)
    elif a.phase=='trade_extended':
        previous=json.loads((OUT/'trade.json').read_text())
        assert previous['selected_scale'] is None
        results=previous['cases']+[one(d,1.75,(65,.35,8),'coarse','trade_extended')]
        eligible=[r for r in results if r['surface_SM']>=.03 and r['within_declared_tail_travel']]
        selected=min((r['scale'] for r in eligible),default=None)
    else:
        selection=OUT/'trade_extended.json'
        if not selection.exists():selection=OUT/'trade.json'
        selected=json.loads(selection.read_text())['selected_scale']
        if selected is None:raise ValueError('No candidate met exploratory 3% screen')
        cases=CASES if a.phase=='envelope' else [CASES[4],CASES[5]]
        results=[one(d,selected,c,'coarse' if a.phase=='envelope' else 'fine',a.phase) for c in cases]
    report=dict(scope='Evaluator-generated aerodynamic trade only; not model-authored, not structural design closure, not flight approval',
      source_sha256=sha(SOURCE),selected_scale=selected,exploratory_target_SM=.03,
      target_note='3% is an evaluator screening target, not a safety standard or validated uncertainty margin',
      assumptions=['Constant assumed tail areal mass, thin rectangular half-plates; root and hinge fixed',
                   'Other component masses retained; reinforcement and control-system redesign mass UNKNOWN, not asserted zero',
                   'No vertices rotate with tail command in AVL; clearance and mechanism sweep unverified',
                   'No installed propulsion, body/gear aerodynamics, stall, flexibility or dynamic-mode validation'],cases=results)
    (OUT/f'{a.phase}.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
