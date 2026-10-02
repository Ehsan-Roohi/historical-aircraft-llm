"""Researcher braced-tail concept: tension-only wires and first-order beam.

Explicitly NOT a verified structure. Material variability, joints, aerodynamic
changes, panel bill of materials and second-order buckling remain unresolved.
"""
import json,math
from pathlib import Path
from audit_v15_tail_beam_demands import strips
from v15_tail_spar_mass_loop import section
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_braced_tail_candidate01.json'
E=10.8e9;RHO=448.;G=9.80665

def kernel(a,x):
    return x*x*(3*a-x)/6 if x<=a else a*a*(3*x-a)/6

def solve(multiplier=1.):
    length=4.025;height=.35;b=.12;h=.10;t=.004
    area,ix,iz=section(b,h,t);ei=E*ix
    dia=.004;wire_area=math.pi*dia**2/4
    wire_E=200e9;wire_rho=7850. # explicit evaluator assumptions, not certified wire properties
    # Beam starts at y=.55, but mast is on centerline y=0: wire span is longer.
    wire_span=.55+length
    l0=math.hypot(wire_span,height)
    rows=strips((ROOT/'analysis/results/v15_tail_strip_loads01/enlarged/strips.txt').read_text())[0][1]
    loads=[(abs(r['y'])-.55,multiplier*(-r['lift_N']+7*G*r['area']/length)) for r in rows]
    free=sum(f*kernel(a,length) for a,f in loads)/ei
    flexibility=length**3/(3*ei)
    def wire(w):
        lu=math.hypot(wire_span,height+w);ll=math.hypot(wire_span,height-w)
        tu=max(0.,wire_E*wire_area*(lu-l0)/l0)
        tl=max(0.,wire_E*wire_area*(ll-l0)/l0)
        support=tu*(height+w)/lu-tl*(height-w)/ll
        compression=tu*wire_span/lu+tl*wire_span/ll
        return support,compression,tu,tl
    lo=0.;hi=free
    assert hi>0
    for _ in range(100):
        mid=(lo+hi)/2
        if mid+wire(mid)[0]*flexibility>free:hi=mid
        else:lo=mid
    w=(lo+hi)/2;support,compression,tu,tl=wire(w)
    assert abs(w+support*flexibility-free)<1e-10
    xs=sorted(set([j*length/1000 for j in range(1001)]+[a for a,f in loads]))
    moments=[sum(f*max(a-x,0) for a,f in loads)-support*(length-x) for x in xs]
    disps=[(sum(f*kernel(a,x) for a,f in loads)-support*kernel(length,x))/ei for x in xs]
    maximum=max(abs(m) for m in moments)
    weak=min(ix,iz)
    return dict(load_multiplier=multiplier,
      geometry=dict(half_span_m=length,wire_horizontal_span_m=wire_span,mast_half_height_m=height,box_b_m=b,box_h_m=h,wall_m=t,wire_diameter_m=dia),
      assumptions=dict(wood_E_Pa=E,wood_density_kg_m3=RHO,wire_E_Pa=wire_E,wire_density_kg_m3=wire_rho,
                       prestress_N=0,uniform_half_panel_mass_budget_kg=7),
      one_half_support_up_N=support,one_half_root_vertical_reaction_N=sum(f for a,f in loads)-support,
      root_bending_Nm=moments[0],max_abs_bending_Nm=maximum,
      unbraced_tip_deflection_m=free,braced_tip_deflection_m=w,max_abs_deflection_m=max(abs(d) for d in disps),
      upper_wire_tension_N=tu,lower_wire_tension_N=tl,wire_required_stress_Pa=max(tu,tl)/wire_area,
      spar_compression_N=compression,spar_max_linear_combined_stress_Pa=maximum*h/(2*ix)+compression/area,
      ideal_Euler_Pcr_N_by_effective_length_factor={str(k):math.pi**2*E*weak/(k*length)**2 for k in (1,2)},
      mass=dict(two_box_spars_kg=2*RHO*area*length,four_wires_kg=4*l0*wire_area*wire_rho,
                solid_square_40mm_mast_kg=RHO*.04**2*2*height),
      EI_Nm2=ei)

def main():
    cases=[solve(1),solve(3)]
    masses=cases[0]['mass'];known=sum(masses.values())
    report=dict(status='RESEARCHER_CONCEPT_NOT_ACCEPTED_STRUCTURE',
      material_source='https://research.fs.usda.gov/download/treesearch/62244.pdf',
      material_scope='Modern clear-wood average values used only by evaluator, not supplied as pre-1899 knowledge or design allowables',
      cases=cases,calculated_member_mass_kg=known,remaining_of_14kg_tail_budget_kg=14-known,
      remaining_mass_note='Unallocated ceiling for ribs, fabric, fittings, bearings, horns and fasteners; not a verified bill of materials. Original 14kg must not be overwritten as closed.',
      limitations=['3x means scaled current static strip loads and weight, NOT a derived maneuver/gust load case',
        'No prestress; lower wire slack under downward load. Load reversal, backlash and flutter unresolved',
        'First-order beam response; axial beam-column effects and local wall/joint buckling not solved',
        'Euler effective-length values are idealized bounds for diagnostic comparison, not acceptance',
        'Mast, attachment stress, bearing/crush/shear, fabric/ribs, fatigue and wood/wire allowables unresolved',
        'Wire drag, tail thickness/shape changes and occupied-volume swept clearance not integrated',
        'Mast intended to rotate with all-moving tail; compatibility with fuselage/control mechanism unverified'],
      accepted_aircraft_modes=False,structural_acceptance=False)
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
