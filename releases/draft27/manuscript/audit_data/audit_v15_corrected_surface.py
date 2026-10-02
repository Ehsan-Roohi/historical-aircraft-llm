"""Check frame consistency and numerical sensitivity of corrected AVL cases."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'analysis/results/v15_fable_corrected_surface02'

def main():
    reports={mesh:json.loads((BASE/mesh/'summary.json').read_text()) for mesh in ['coarse','fine']}
    consistency={}
    for mesh,r in reports.items():
        a=math.radians(r['trim']['Alpha'])
        fd=r['slopes_per_rad']['beta']['1.5'];st=r['AVL_stability_derivatives_raw_labels']
        rotated={'CYb':fd['CYtot'],'Clb':fd['Cltot']*math.cos(a)+fd['Cntot']*math.sin(a),'Cnb':-fd['Cltot']*math.sin(a)+fd['Cntot']*math.cos(a)}
        errors={key:abs(value-st[key]) for key,value in rotated.items()}
        assert max(errors.values())<2e-4, errors
        assert len(r['cases'])==13
        assert abs(r['trim']['CLtot']-r['target_CL'])<2e-4
        assert abs(r['trim']['Cmtot'])<2e-4
        consistency[mesh]={'body_to_stability_axis_beta_slopes':rotated,'max_absolute_difference_from_ST_per_rad':max(errors.values())}
    sensitivity={}
    for var,steps in [('beta',['3.0','1.5']),('tip',['4.0','2.0']),('rudder',['5.0','2.5'])]:
        sensitivity[var]={}
        for coeff in ['CYtot','Cltot','Cntot']:
            c=reports['coarse']['slopes_per_rad'][var][steps[1]][coeff]
            f=reports['fine']['slopes_per_rad'][var][steps[1]][coeff]
            large=reports['fine']['slopes_per_rad'][var][steps[0]][coeff]
            sensitivity[var][coeff]={'coarse_small_step':c,'fine_small_step':f,'mesh_absolute_difference':abs(c-f),'fine_step_absolute_difference':abs(f-large)}
    rates={k:{m:reports[m]['AVL_stability_derivatives_raw_labels'][k] for m in reports} for k in ['CLa','Cma','Cmq','CLq','CYp','CYr','Clp','Clr','Cnp','Cnr']}
    result={'scope':'Numerical corrected-model audit only; no experimental or installed-aircraft validation', 'source_hashes':{m:hashlib.sha256((BASE/m/'summary.json').read_bytes()).hexdigest() for m in reports},'checks_passed':['13 cases per mesh','conditional CL and Cm residuals','body/stability-axis finite-difference consistency'],'frame_consistency':consistency,'derivative_sensitivity':sensitivity,'stability_axis_derivatives':rates,'trim':{m:reports[m]['trim'] for m in reports},'apparent_surface_only_margin_percent':{m:-100*reports[m]['AVL_stability_derivatives_raw_labels']['Cma']/reports[m]['AVL_stability_derivatives_raw_labels']['CLa'] for m in reports},'acceptance':{'installed_six_component_trim':False,'validated_unsteady_derivatives':False,'aircraft_eigenmodes':False},'supersedes':'Numerical conclusions of the old split-tip/vertical input in v15_fable_lateral_derivative_gate01.json; earlier files are retained.'}
    (BASE/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
