"""Audit existing speed runs and substitute induced drag, without rerunning AVL."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'fable_v16_speed_screen01'
RAW = Path.cwd() / 'output/received_v16_fable_65061669/claude-fable-5-1/response.json'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    summary = json.loads((OUT/'summary.json').read_text())
    parent = HERE/'fable_v16_surface_retrim01/case_06/result.json'
    assert sha(parent) == summary['source_result_sha256']
    assert sha(HERE/'fable_v16_speed_screen.py') == summary['script_sha256']
    assert sha(RAW) == '6dae3f48195d8b446f517fac08936fb69d87a8b59a44f618bdc8faccc198dbc1'
    section = json.loads(json.loads(RAW.read_text(encoding='utf-8'))['response'])['section_6_drag_and_propulsion']
    assert len(summary['cases']) == 2
    rows = []
    for result in summary['cases']:
        v = result['speed_mps']
        folder = OUT/f'V{v}'
        for filename, field in [('aircraft.avl','geometry_sha256'),('forces.txt','forces_sha256'),('stability.txt','stability_sha256')]:
            assert sha(folder/filename) == result[field]
        claim = next(c for c in section['cases'] if c['id'] == f'H{v}W')
        assert claim['kg'] == result['mass_kg']
        qs = .5*1.225*v*v*42
        lift_error = qs*result['trim']['CLtot'] - result['mass_kg']*9.80665
        assert abs(lift_error) < .1 and abs(result['trim']['Cmtot']) < 2e-4
        assert -16 <= result['absolute_tail_deg'] <= 8
        assert abs(result['surface_SM_percent'] + 100*result['Cma']/result['CLa']) < 1e-9
        eta = claim['D_N']*v/claim['P_req_W']
        drag = claim['D_N'] + qs*(result['trim']['CDind']-claim['CDi'])
        power = drag*v/eta
        available = section['P_out_available_W']['value']
        rows.append(dict(speed_mps=v, mass_kg=result['mass_kg'],
                         surface_lift_residual_N=lift_error,
                         alpha_deg=result['trim']['Alpha'],
                         surface_CL=result['trim']['CLtot'],
                         surface_SM_percent=result['surface_SM_percent'],
                         printed_CDi=claim['CDi'], AVL_CDi=result['trim']['CDind'],
                         inferred_efficiency=eta, hybrid_drag_N=drag,
                         hybrid_shaft_power_W=power, assumed_available_W=available,
                         reserve_fraction=available/power-1,
                         absolute_power_headroom_W=available-power,
                         margin_above_1p15_required_W=available-1.15*power,
                         minimum_efficiency_for_1p15_reserve=1.15*drag*v/available))
    assert rows[0]['margin_above_1p15_required_W'] > 0
    assert rows[1]['absolute_power_headroom_W'] < 0
    report = dict(status='AUDITED_CONDITIONAL_SENSITIVITY', cases=rows,
                  raw_response_sha256=sha(RAW), summary_sha256=sha(OUT/'summary.json'),
                  script_sha256=sha(Path(__file__)),
                  validation='Six raw file hashes, parent and script hashes, matched mass, two lift/moment residuals, tail limits and SM formulas passed.',
                  method='Replace only printed induced drag coefficient with same-speed, same-mass AVL surface coefficient; retain printed drag baseline and infer its efficiency from D,V,P. No double counting of induced drag.',
                  limitations=['Rigid surface-only quasi-steady AVL, unvalidated section; no installed propulsion or body interaction.',
                               '12 m/s CL near 0.993 and alpha near 9.09 deg do not establish attached flow or stall margin.',
                               'Engine availability, other drag and propeller efficiency remain unmeasured assumptions.',
                               'No Reynolds-dependent section data; speed changes target lift, not viscous validity.',
                               '15 percent reserve is exploratory, not an airworthiness standard.',
                               'Not a coupled six-component trim, dynamic-mode or flight acceptance.'],
                  flight_acceptance=False)
    (OUT/'power_audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
