"""Bounded local AVL 3.52 numerical gate; not experimental validation.

Elliptic planar flat wing, AR=10, unswept quarter-chord, +/-2 deg.
Independent comparison is classical elliptic lifting-line (a0=2*pi),
not an exact solution to AVL's finite-chord vortex-lattice discretization.
"""
import hashlib
import argparse
import json
import math
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'analysis/tools/avl/avl352.exe'
OUT=ROOT/'analysis/results/avl_reference_gate_attempt02'


def geometry(nc,ns):
    # Piecewise-linear approximation, separate from solver mesh refinement.
    b=10.0
    s=10.0
    root=4*s/(math.pi*b)
    sections=[]
    samples=[]
    for i in range(9):
        t=(math.pi/2-1e-4)*i/8
        y=b/2*math.sin(t)
        c=root*math.cos(t)
        sections+=['SECTION',f'{-c/4:.10f} {y:.10f} 0 {c:.10f} 0']
        samples.append((y,c))
    area=2*sum((samples[i+1][0]-samples[i][0])*(samples[i+1][1]+samples[i][1])/2 for i in range(8))
    return '\n'.join(['Elliptic AR10 numerical reference','0','0 0 0','10 1 10','0 0 0','0','SURFACE','wing',f'{nc} 1 {ns} 1','YDUPLICATE','0']+sections)+'\n',area


def parse(text,key):
    hits=re.findall(r'\b'+re.escape(key)+r'\s*=\s*([-+0-9.Ee]+)',text)
    if not hits:
        raise ValueError(f'Missing {key}')
    v=float(hits[-1])
    if not math.isfinite(v):
        raise ValueError(f'Nonfinite {key}')
    return v


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=OUT,help='Use a fresh directory to preserve past runs')
    args=parser.parse_args()
    out=args.output.resolve()
    if out.exists():
        raise FileExistsError(f'Use a new --output directory; preserving {out}')
    out.mkdir(parents=True)
    records=[]
    for nc,ns in [(4,20),(8,40),(12,80)]:
        for alpha in [-2,0,2]:
            tag=f'c{nc}_s{ns}_a{alpha:+d}'.replace('+','p').replace('-','m')
            case=out/tag
            case.mkdir(exist_ok=True)
            geom,area=geometry(nc,ns)
            (case/'wing.avl').write_text(geom,encoding='ascii')
            commands=f'load wing.avl\noper\na a {alpha}\nx\nft\nforces.txt\n\nquit\n'
            # Existing output triggers an overwrite prompt; remove ambiguity by
            # using a fresh per-execution directory below in follow-up runs.
            if (case/'forces.txt').exists():
                raise FileExistsError(f'Preserve prior result: {case}')
            (case/'commands.txt').write_text(commands,encoding='ascii')
            p=subprocess.run([str(EXE)],input=commands,cwd=case,capture_output=True,text=True,timeout=25,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            (case/'stdout.txt').write_text(p.stdout,encoding='utf-8')
            (case/'stderr.txt').write_text(p.stderr,encoding='utf-8')
            if p.returncode!=0:
                raise RuntimeError(f'AVL failed {tag}: {p.returncode}')
            txt=(case/'forces.txt').read_text()
            record={'tag':tag,'nc':nc,'ns_per_half':ns,'alpha_deg':alpha,'represented_area_m2':area}
            for key in ['CLtot','CDind','Cmtot','Cltot','CYtot']:
                record[key]=parse(txt,key)
            records.append(record)
            print(record,flush=True)
    finest=[r for r in records if r['nc']==12]
    neg,zero,pos=finest
    a_liftingline=2*math.pi*10/(10+2)
    expected=a_liftingline*math.radians(2)
    medium=next(r for r in records if r['nc']==8 and r['alpha_deg']==2)
    criteria={
        'flat_zero_lift':abs(zero['CLtot'])<1e-5,
        'odd_lift_symmetry':abs(pos['CLtot']+neg['CLtot'])<1e-5,
        'zero_roll_and_sideforce':all(abs(r['Cltot'])<1e-5 and abs(r['CYtot'])<1e-5 for r in records),
        'positive_induced_drag':pos['CDind']>0 and neg['CDind']>0,
        'lift_mesh_change_below_2pct':abs(pos['CLtot']/medium['CLtot']-1)<.02,
        'induced_drag_mesh_change_below_3pct':abs(pos['CDind']/medium['CDind']-1)<.03,
        'liftingline_lift_agreement_within_8pct':abs(pos['CLtot']/expected-1)<.08,
        'elliptic_drag_agreement_within_8pct':abs(pos['CDind']/(pos['CLtot']**2/(math.pi*10))-1)<.08}
    result={'solver_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),'criteria':criteria,'all_passed':all(criteria.values()),'liftingline_CL_at_2deg':expected,'records':records,'scope':'Numerical plausibility/refinement only; not validation of historical flexible, cambered, interacting surfaces or propulsion'}
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(criteria,indent=2))


if __name__=='__main__':
    main()
