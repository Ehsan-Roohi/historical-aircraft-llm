"""Loading/inertia bookkeeping and frozen-neutral-point screening, NOT modes."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'output/received_v15_65023104/claude-fable-5-1/response.json'
OUT = ROOT/'analysis/results/v15_fable_loading_gate01.json'

def ledger(rows):
    m = sum(r['mass_kg'] for r in rows)
    cg = [sum(r['mass_kg']*r['centroid'][j] for r in rows)/m for j in range(3)]
    diag = [0., 0., 0.]
    pxz = 0.
    for r in rows:
        x,y,z = [r['centroid'][j]-cg[j] for j in range(3)]
        for j,v in enumerate((y*y+z*z,x*x+z*z,x*x+y*y)):
            diag[j] += r['I_intr'][j]+r['mass_kg']*v
        pxz += r['mass_kg']*x*z
    return m,cg,diag,pxz

def main():
    d=json.loads(json.loads(SOURCE.read_text(encoding='utf-8'))['response'])
    rows=d['section_3_mass_ledger']['rows']
    m0,cg0,i0,p0=ledger(rows)
    assert abs(m0-353.2)<1e-8
    surfaces={}
    for mesh in ('coarse','fine'):
        p=ROOT/f'analysis/results/v15_fable_corrected_surface02/{mesh}/summary.json'
        s=json.loads(p.read_text())
        a=s['AVL_stability_derivatives_raw_labels']
        sm=-a['Cma']/a['CLa']
        surfaces[mesh]={'nominal_SM':sm,'frozen_xNP_m':cg0[0]+1.85*sm,
                        'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    cases=[(75,.30,8),(75,.35,8),(75,.25,8),(75,.30,0),
           (65,.35,8),(65,.35,0),(85,.25,8),(85,.25,0)]
    result=[]
    for pilot,seat,fuel in cases:
        rr=copy.deepcopy(rows)
        for r in rr:
            if r['ID']=='P05':
                r['mass_kg']=pilot;r['centroid'][0]=seat
                r['I_intr']=[v*pilot/75 for v in r['I_intr']]
            if r['ID']=='P07b':
                r['mass_kg']=fuel;r['I_intr']=[v*fuel/8 for v in r['I_intr']]
        m,cg,diag,pxz=ledger(rr)
        assert min(diag)>0 and diag[0]*diag[2]>pxz*pxz
        assert max(diag)<=sum(diag)-max(diag)
        margins={k:(v['frozen_xNP_m']-cg[0])/1.85 for k,v in surfaces.items()}
        result.append(dict(pilot_kg=pilot,seat_x_m=seat,fuel_kg=fuel,mass_kg=m,cg_m=cg,
            assumed_inertia_diagonal_kgm2=diag,assumed_Pxz_kgm2=pxz,
            frozen_NP_SM=margins,needs_independent_retrim=True,
            negative_margin_screen=any(v<0 for v in margins.values())))
    claimed=d['section_3_mass_ledger']['loading_cases_AR']
    for r,c in zip(result,claimed):
        assert abs(r['mass_kg']-c['mass_kg'])<1e-6
        assert max(abs(a-b) for a,b in zip(r['cg_m'],c['cg']))<1e-5
    report=dict(scope='Evaluator-only loading arithmetic and fixed-neutral-point diagnostic; not re-trimmed stability, modes or flight approval',
       source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
       assumptions=['Model-authored mass/centroid/intrinsic inertia retained, not measured',
                    'Pilot intrinsic inertia scales with mass at fixed shape; body-shape variation unknown',
                    'Fuel full or empty only; tank mass retained',
                    'Intrinsic products of inertia not supplied; Pxz includes centroid terms only, not an established complete tensor',
                    'Frozen nominal neutral point and reference chord 1.85 m; height, retrim, drag, propulsion and wake changes excluded'],
       nominal_surfaces=surfaces,cases=result,negative_screen_count=sum(r['negative_margin_screen'] for r in result),
       accepted_aircraft_modes=False,next_action='Re-trim aft/light-pilot cases with corrected geometry and their own weight/CG; then assess derivatives and uncertainty. Do not label the frozen-NP screen a verified static instability.')
    OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':len(result),'negative_screen_count':report['negative_screen_count'],
                      'frozen_NP_m':{k:v['frozen_xNP_m'] for k,v in surfaces.items()},
                      'fine_margin_range_percent':[100*min(r['frozen_NP_SM']['fine'] for r in result),100*max(r['frozen_NP_SM']['fine'] for r in result)]}))

if __name__=='__main__':main()
