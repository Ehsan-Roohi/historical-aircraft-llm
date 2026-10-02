"""Explicit hollow rectangular wood beam trade plus mass/CG re-trim.

An equivalent closed box requires unverified joints; this is a researcher
screen, NOT build instructions, proof of strength, or a period-authentic design.
"""
import itertools,json
from pathlib import Path
import v15_fable_tail_trade as trade
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_tail_spar_mass_loop01'
E=10.8e9
RHO=448.
G=9.80665
L=4.025

def section(b,h,t):
    assert b>2*t and h>2*t
    area=b*h-(b-2*t)*(h-2*t)
    ix=(b*h**3-(b-2*t)*(h-2*t)**3)/12
    iz=(h*b**3-(h-2*t)*(b-2*t)**3)/12
    return area,ix,iz

def main():
    OUT.mkdir(exist_ok=False)
    loads=json.loads((ROOT/'analysis/results/v15_tail_strip_loads01/beam_demands.json').read_text())
    half=next(c for c in loads['cases'] if c['case']=='enlarged')['halves'][0]
    baseK=abs(half['lift_minus_weight_tip_deflection_times_EI_Nm3'])
    baseM=abs(half['lift_minus_weight_root_bending_Nm'])
    candidates=[]
    for b,h,t in itertools.product((.04,.06,.08,.10,.12,.16),(.04,.06,.08,.10,.12,.14,.16),(.003,.004,.006,.008,.010)):
        area,ix,iz=section(b,h,t)
        mass=RHO*area*L
        # Added beam weight distributed uniformly, not silently omitted.
        moment=baseM+mass*G*L/2
        k=baseK+mass*G*L**3/8
        candidates.append(dict(b_m=b,h_m=h,t_m=t,area_m2=area,I_bending_m4=ix,I_other_m4=iz,
             one_half_added_mass_kg=mass,EI_Nm2=E*ix,tip_deflection_m=k/(E*ix),
             root_bending_Nm=moment,bending_stress_Pa=moment*h/(2*ix)))
    selected={}
    for mm in (10,20,40):
        eligible=[c for c in candidates if c['tip_deflection_m']<=mm/1000]
        selected[str(mm)]=min(eligible,key=lambda c:c['one_half_added_mass_kg']) if eligible else None
    report=dict(scope='Equivalent wood box stiffness/mass screen with fully effective joints assumed, not structural approval',
       material=dict(species='Sitka spruce',E_Pa=E,rho_kg_m3=RHO,
          source='https://research.fs.usda.gov/download/treesearch/62244.pdf',table='5-3a, printed page 5-8',
          provenance='12% moisture average clear-wood E=10800 MPa and specific gravity .40; density computed as .40*1000*1.12',
          source_strength_not_allowable=True),
       geometry_note='Geometric section trade; hollow-box fabrication, bond/shear transfer, period availability, fit and attachment are NOT verified',
       number_of_candidates=len(candidates),selected_by_exploratory_deflection_mm=selected,
       assumptions=['Two added beams; original tail mass retained to avoid unsubstantiated mass credit',
                    'Hinge/bearing/rib/cover load sharing and additional fitting mass unresolved',
                    'Steady tail loading only; no actual design load envelope','No numerical stress allowable adopted; reported stress is not a pass'],
       candidates=candidates)
    (OUT/'section_trade.json').write_text(json.dumps(report,indent=2)+'\n')
    # 20 mm is a disclosed intermediate sensitivity, not approved clearance.
    c=selected['20']
    if c is None:raise ValueError('No 20mm candidate in stated grid')
    d=json.loads(json.loads(trade.SOURCE.read_text(encoding='utf-8'))['response'])
    m=c['one_half_added_mass_kg'];area=c['area_m2']
    mean_z2=c['I_bending_m4']/area;mean_x2=c['I_other_m4']/area
    for sign in (-1,1):
        d['section_3_mass_ledger']['rows'].append(dict(ID=f'EVAL_BOX_{sign}',mass_kg=m,
          centroid=[5.65,sign*(.55+L/2),.775],I_intr=[m*(L*L/12+mean_z2),m*(mean_z2+mean_x2),m*(L*L/12+mean_x2)],
          tag='ADDITIVE EVALUATOR BEAM MASS; UNVERIFIED JOINTS/FIT'))
    trade.OUT=OUT
    r=trade.one(d,1.75,(65,.35,0),'coarse','added_box20mm')
    report=dict(scope='Mass-feedback surface re-trim for one explicitly assumed beam candidate, not aircraft acceptance',
           selected_deflection_parameter_mm=20,section=c,retrim=r,
           total_added_beam_mass_kg=2*m,next='Recompute loads for this new trim; joint/fit/strength and actual deflection limit remain open',accepted_aircraft_modes=False)
    (OUT/'mass_feedback.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='retrim'},indent=2))

if __name__=='__main__':main()
