"""Independently re-trim flagged aft-CG cases; preserve original geometry."""
import json
from pathlib import Path
from v15_fable_corrected_surface_screen import run,parse_st,sha
from avl_reference_gate import parse

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_fable_aft_retrim01'

def main():
    gatepath=ROOT/'analysis/results/v15_fable_loading_gate01.json'
    gate=json.loads(gatepath.read_text())
    OUT.mkdir(exist_ok=False)
    results=[]
    for case in gate['cases']:
        if not case['negative_margin_screen']:continue
        for mesh in ('coarse','fine'):
            src=ROOT/f'analysis/results/v15_fable_corrected_surface02/{mesh}'
            folder=OUT/f'fuel{case["fuel_kg"]}_{mesh}';folder.mkdir()
            lines=(src/'aircraft.avl').read_text().splitlines()
            assert lines[4]=='1.52236 0 0.78455'
            lines[4]=' '.join(f'{v:.10f}' for v in case['cg_m'])
            (folder/'aircraft.avl').write_text('\n'.join(lines)+'\n',encoding='ascii')
            (folder/'section.dat').write_bytes((src/'section.dat').read_bytes())
            target=case['mass_kg']*9.80665/(.5*1.225*13**2*42)
            run(folder,f'load aircraft.avl\noper\na a 5.85\nd2 d2 -4\na c {target:.12f}\nd2 pm 0\nx\nft\nforces.txt\nst\nstability.txt\n\nquit\n')
            t=(folder/'forces.txt').read_text()
            trim={k:parse(t,k) for k in ('Alpha','pitch','CLtot','Cmtot')}
            assert abs(trim['CLtot']-target)<2e-4 and abs(trim['Cmtot'])<2e-4
            st=parse_st((folder/'stability.txt').read_text())
            r=dict(mesh=mesh,pilot_kg=case['pilot_kg'],fuel_kg=case['fuel_kg'],mass_kg=case['mass_kg'],cg_m=case['cg_m'],target_CL=target,trim=trim,
                   absolute_tail_deg=trim['pitch']-4,Cma=st['Cma'],CLa=st['CLa'],surface_SM=-st['Cma']/st['CLa'],
                   geometry_sha256=sha(folder/'aircraft.avl'),forces_sha256=sha(folder/'forces.txt'),stability_sha256=sha(folder/'stability.txt'))
            results.append(r);print(json.dumps(r),flush=True)
    report=dict(scope='Re-trimmed rigid unpowered surface-model prediction only; no installed-aircraft stability or modes',loading_gate_sha256=sha(gatepath),cases=results,
                limitations=['Only mass/CG and operating trim changed; pilot/body geometry omitted','No propulsion, viscous drag, flexibility or unsteady derivatives','Intrinsic inertia remains assumed; no eigenvalues calculated'],
                accepted_aircraft_modes=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
