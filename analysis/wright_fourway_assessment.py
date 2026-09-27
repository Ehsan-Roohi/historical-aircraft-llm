"""Four-aircraft comparison with explicit historical-reference boundaries.

Postprocess existing audited Wright runs, never pretend a moment reference is
the measured historical CG. No new aerodynamic solver run or fitted geometry.
"""
from pathlib import Path
import hashlib,json,math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/four_aircraft_comparison01'
RHO=1.225;G=9.80665

def dimensional(c,s,chord,v,m):
    q=.5*RHO*v*v
    return {'q_Pa':q,'weight_N':m*G,'lift_N':q*s*c['CLtot'],
            'lift_minus_weight_N_no_vertical_thrust':q*s*c['CLtot']-m*G,
            'induced_drag_N_only':q*s*c['CDind'],
            'induced_drag_power_W_only':q*s*c['CDind']*v,
            'aerodynamic_moment_about_reference_Nm':q*s*chord*c['Cmtot']}

def secant(c0,c1,da=4):
    cl=(c1['CLtot']-c0['CLtot'])/da;cm=(c1['Cmtot']-c0['Cmtot'])/da
    return {'alpha_interval_deg':[0,da],'CL_secant_per_deg':cl,'Cm_secant_per_deg':cm,
            'CL_secant_per_rad':cl*180/math.pi,'Cm_secant_per_rad':cm*180/math.pi,
            'negative_Cm_over_CL_slope_percent':-100*cm/cl,
            'interpretation':'reference-point secant descriptor, NOT historical CG static margin'}

def main():
    paths=['paper/baselines/wright_nominal_v1.json','analysis/results/wright_family_comparison_v1.json',
           'analysis/results/wright_reconstruction_audit_v1.json','analysis/results/wright_reconstruction_family02/definition.json',
           'analysis/results/v2_trim_solve01/compact_report.json','analysis/results/received_v2_audit01/summary.json',
           'analysis/results/wright_props_off_digitized_v1.json']
    data=[json.loads((ROOT/p).read_text(encoding='utf8')) for p in paths]
    nominal,family,coarse,definition,ai,ledger,measured=data
    ref=definition['reference'];s=ref['S_m2'];chord=ref['c_m'];mass=nominal['original_values']['loaded_mass_lb_approx']*.45359237
    v=12 # analyst screening speed, NOT a reconstructed historical flight condition
    fine=family['fine_selected_cases'];wright=[]
    for section in ['flat','eiffel10_raw']:
        rows=sorted([r for r in fine if r['canard_section']==section],key=lambda r:r['alpha_deg'])
        if len(rows)!=2 or [r['alpha_deg'] for r in rows]!=[0,4]:raise ValueError('Missing paired fine cases')
        slopes=secant(*[r['coefficients'] for r in rows])
        wright.append({'canard_proxy':section,'source_cases':[r['case'] for r in rows],'slope':slopes,
                       'loads':[{'alpha_deg':r['alpha_deg'],**dimensional(r['coefficients'],s,chord,v,mass)} for r in rows]})
    latest=[r for r in ai if (r['model']=='gpt-6-astra' and r['mesh']==[14,72]) or (r['model']=='claude-opus-5-5' and r['mesh']==[12,50])]
    result={'scope':__doc__,'inputs':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
            'wright':{'identity':'1903 Flyer I-inspired researcher reconstruction; not matched historical aircraft or tunnel replica',
             'scenario':{'mass_kg':mass,'speed_m_s':v,'density_kg_m3':RHO,'reference':ref,
                         'historical_CG_m':None,'weight_N':mass*G,'CL_required_without_vertical_thrust':mass*G/(.5*RHO*v*v*s),
                         'historical_statistical_area_m2':nominal['original_values']['wing_area_ft2']*.3048**2,
                         'note':'518 ft2 nominal statistics and 510 ft2 solver normalization are distinct; no silent substitution'},
             'fine_proxy_results':wright,'published_graph_descriptor':measured['linear_fit_descriptors_NOT_local_derivatives'],
             'full_powered_trim':'NOT established','historical_flight':'Documented independently; not inferred from this reconstruction'},
            'AI_V2_latest':latest,'fable':{'mass_kg':ledger['claude-fable-5-1']['mass_kg'],'cg_native_m':ledger['claude-fable-5-1']['cg_native_m'],'trim':'not evaluated through unresolved geometry'},
            'comparison_limits':['Wright secants span 0 to 4 deg; AI local derivatives span +/-0.25 deg around separate trim points.',
             'Wright Cm is about a stipulated moment reference, not verified flight-specific CG.',
             'Induced-only drag/power omits viscosity, structure, pilot and propulsion effects.',
             'No structural strength, full dynamic eigenvalues, lateral-directional stability or occupied-flight clearance.',
             'The historical 1903 machine flew; the three AI designs have not demonstrated flight.',
             'No quantitative superiority ranking is justified.']}
    OUT.mkdir(exist_ok=True);(OUT/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result['wright'],indent=2))

if __name__=='__main__':main()
