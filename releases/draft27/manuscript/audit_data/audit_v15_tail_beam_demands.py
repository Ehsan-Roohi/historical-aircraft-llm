"""Conditional strip-load beam demands; no material or design allowables invented."""
import json,math,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_tail_strip_loads01'
Q=.5*1.225*13**2
G=9.80665

def tip_kernel(force,a,length):
    return force*a*a*(3*length-a)/6

def strips(text):
    result=[]
    for block in re.split(r'\s*Surface #',text)[1:]:
        label=block.splitlines()[0].strip()
        if 'tail_halves' not in label:continue
        expected=float(re.search(r'CLsurf\s*=\s*([-+\d.]+)',block)[1])*Q*42
        table=block.split('C.P.x/c',1)[1]
        rows=[]
        for line in table.splitlines():
            values=line.split()
            if len(values)!=15:continue
            try:v=[float(x) for x in values]
            except ValueError:continue
            assert v[5]>0 and abs(v[4]-1)<1e-6
            rows.append(dict(y=v[2],chord=v[4],area=v[5],cl=v[9],lift_N=Q*v[5]*v[9]))
        assert len(rows)==32
        actual=sum(r['lift_N'] for r in rows)
        assert abs(actual-expected)<max(.5,abs(expected)*.005),(label,actual,expected)
        result.append((label,rows,expected,actual))
    assert len(result)==2
    return result

def main():
    results=[]
    for case in ('original','enlarged','plus2kg'):
        p=OUT/case/'strips.txt';text=p.read_text()
        length=2.3 if case=='original' else 4.025
        halfmass=4 if case=='original' else 7
        halves=[]
        for name,rr,expected,actual in strips(text):
            assert abs(sum(r['area'] for r in rr)-length)<.002
            aero_moment=0;net_moment=0;aero_k=0;net_k=0
            for r in rr:
                a=abs(r['y'])-.55
                assert 0<a<length
                lift=r['lift_N']
                weight=halfmass*G*r['area']/length
                aero_moment+=lift*a;net_moment+=(lift-weight)*a
                aero_k+=tip_kernel(lift,a,length)
                net_k+=tip_kernel(lift-weight,a,length)
            halves.append(dict(half=name,strip_count=len(rr),aerodynamic_lift_N=actual,
                surface_integrated_lift_N=expected,force_crosscheck_error_N=actual-expected,
                aerodynamic_root_bending_Nm=aero_moment,assumed_weight_N=halfmass*G,
                lift_minus_weight_root_bending_Nm=net_moment,
                aero_tip_deflection_times_EI_Nm3=aero_k,
                lift_minus_weight_tip_deflection_times_EI_Nm3=net_k,
                EI_requirement_Nm2_for_exploratory_tip_displacement={str(mm):abs(net_k)/(mm/1000) for mm in (5,10,20)},
                bending_stress_relation='sigma_max = abs(root_bending)/Z; section modulus Z and material allowable UNKNOWN'))
        assert abs(halves[0]['aerodynamic_lift_N']-halves[1]['aerodynamic_lift_N'])<.05
        results.append(dict(case=case,length_m=length,halfmass_kg=halfmass,
             source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),halves=halves))
    # Exact point-load kernel and convergent uniform-load quadrature checks.
    assert abs(tip_kernel(1,2,2)-8/3)<1e-12
    n=10000;length=2.;w=3.
    integrated=sum(tip_kernel(w*length/n,(j+.5)*length/n,length) for j in range(n))
    assert abs(integrated-w*length**4/8)<1e-7
    report=dict(scope='Euler-Bernoulli cantilever requirements from conditional AVL lift strips; NOT a structural pass',
       axes='Lift positive upward in assumed horizontal-flow equilibrium; downward tail weight subtracted',
       assumptions=['Root at absolute y=.55m; clamped half-panel with constant EI, not verified actual load path',
                    'Steady 13m/s aerodynamic state; no gust, maneuver, landing or control-stop envelope',
                    'Uniform assumed half-panel mass; +2kg central hinge point mass does not load the half-panel span',
                    'Only vertical bending; drag, torsion, joint compliance, hinge actuation and buckling excluded',
                    '5/10/20mm displacement values are exploratory parameters, not approved clearance limits'],
       tests=['Strip/surface lift normalization cross-check','Left/right symmetry','Point-load kernel','Uniform-load integration'],
       cases=results,structural_acceptance=False,accepted_aircraft_modes=False)
    (OUT/'beam_demands.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['CONDITIONAL TAIL LOAD / BEAM REQUIREMENT AUDIT',
      'Original V15 and evaluator tail variants remain distinct. Draft22 is unchanged.',
      'These are model-predicted loads at one operating condition, not measured loads or structural design allowables.',
      'Case | one-half lift (N) | net root bending with own weight (Nm) | EI for illustrative 10mm tip displacement (Nm2)']
    for r in results:
        h=r['halves'][0]
        lines.append(f"{r['case']} | {h['aerodynamic_lift_N']:.3f} | {h['lift_minus_weight_root_bending_Nm']:.3f} | {h['EI_requirement_Nm2_for_exploratory_tip_displacement']['10']:.1f}")
    lines+=['','Do not convert required EI to a claimed spar mass without section, material, joint and load-envelope evidence.',
      'The increased tail mass cannot be accepted independently of the previously measured computational margin loss under added aft mass.',
      'Next: establish physically specified spar/root/hinge load paths and material-property evidence, then compare smaller tail plus feasible CG redistribution. Full installed loads, modes and flight approval remain open.']
    (ROOT/'paper/FABLE_TAIL_BEAM_DEMANDS_ADDENDUM.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
if __name__=='__main__':main()
