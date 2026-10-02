import json,hashlib
from pathlib import Path
root=Path(__file__).parent/'fable_v16_surface_retrim01'
summary=json.loads((root/'summary.json').read_text())
assert len(summary['cases'])==8
qS=.5*1.225*13**2*42
checks=[]
for i,r in enumerate(summary['cases']):
    p=root/f'case_{i:02d}'
    for name,key in [('aircraft.avl','input_sha256'),('forces.txt','forces_sha256'),('stability.txt','stability_sha256')]:
        assert hashlib.sha256((p/name).read_bytes()).hexdigest()==r[key]
    assert -16<=r['absolute_tail_deg']<=8
    assert r['CLa']>0 and r['Cma']<0
    assert abs(r['surface_SM_percent']+100*r['Cma']/r['CLa'])<1e-12
    residual=qS*r['trim']['CLtot']-r['case']['mass_kg']*9.80665
    assert abs(residual)<.9 and abs(r['trim']['Cmtot'])<2e-4
    checks.append({'case':i,'lift_minus_weight_N_from_printed_output':residual,'Cm_from_printed_output':r['trim']['Cmtot']})
out=dict(status='PASS_WITHIN_SURFACE_MODEL_ONLY',cases=checks,
    SM_percent_range=[min(r['surface_SM_percent'] for r in summary['cases']),max(r['surface_SM_percent'] for r in summary['cases'])],
    max_abs_lift_residual_N=max(abs(c['lift_minus_weight_N_from_printed_output']) for c in checks),
    target_note='3 percent is exploratory, not a safety standard.',
    limitations=summary['scope'],six_component_installed_trim=False,dynamic_modes=False,flight_proven=False)
(root/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
