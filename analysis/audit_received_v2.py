"""Reproduce arithmetic only; never execute model output or certify flight."""
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ledger(items, mass_key, centroid_key):
    total = sum(r[mass_key] for r in items)
    moments = [sum(r[mass_key] * r[centroid_key][j] for r in items) for j in range(3)]
    return {'mass_kg': total, 'first_moments_kg_m': moments,
            'cg_native_m': [v / total for v in moments]}


def audit(model, d):
    if model == 'gpt-6-astra':
        result = ledger(d['mass_items']['items'], 'mass_kg', 'centroid_xyz_m')
        state = d['claimed_flight_state']
        cg = result['cg_native_m']
        forces = state['individual_surface_forces']
        moment = sum((r['application_xyz_m'][0]-cg[0])*r['force_xyz_N'][2]
                     -(r['application_xyz_m'][2]-cg[2])*r['force_xyz_N'][0]
                     +r.get('intrinsic_pitch_moment_Nm', 0) for r in forces)
        moment += cg[2]*400
        result['claimed_load_ledger_recomputed'] = {
            'vertical_residual_N': sum(r['force_xyz_N'][2] for r in forces)-result['mass_kg']*9.80665,
            'horizontal_residual_N': sum(r['force_xyz_N'][0] for r in forces)-125+400,
            'pitch_residual_Nm': moment}
        result['limitations'] = ['Forces and coefficients are model-selected assumptions, not independent aerodynamics.',
                                'Propeller reaction torque is explicitly not balanced.',
                                'Intrinsic inertias, engine capability and structural allowables remain unknown.']
    else:
        fable = model == 'claude-fable-5-1'
        result = ledger(d['mass_items'], 'mass_kg' if fable else 'mass', 'centroid_xyz' if fable else 'centroid')
        summary = d['mass_summary']
        result['claimed_mass_kg'] = summary['total_mass_kg']
        result['claimed_cg_native_m'] = summary['cg_xyz' if fable else 'cg_m']
        result['cg_discrepancy_m'] = [a-b for a,b in zip(result['cg_native_m'], result['claimed_cg_native_m'])]
        state = d['claimed_flight_state']
        alpha = math.radians(state['alpha_deg_body' if fable else 'alpha_deg'])
        thrust = state['thrust_N']['along_body_x'] if fable else state['thrust_N']
        lift = (3061-203) if fable else (1712+1921-150)
        drag = state['drag_N'] if fable else state['drag_N']['total']
        result['claimed_load_ledger_recomputed'] = {
            'vertical_residual_N': lift+thrust*math.sin(alpha)-result['mass_kg']*9.80665,
            'horizontal_residual_N': thrust*math.cos(alpha)-drag,
            'shaft_power_W_assumed_efficiency': thrust*math.cos(alpha)*state['V_m_s' if fable else 'V']/(0.5 if fable else 0.6)}
        result['limitations'] = ['Self-estimated surface loads do not independently validate trim.',
                                'Intrinsic inertias, engine capability and structural allowables remain unknown.']
        if fable:
            result['centroids_outside_declared_boxes'] = [r['id'] for r in d['mass_items']
                if any(not r['bounding'][axis][0] <= r['centroid_xyz'][j] <= r['bounding'][axis][1]
                       for j,axis in enumerate(('x','y','z')))]
            result['tail_sweep_z_m_rigid_chord_including_rigging'] = [
                min(0.775-x*math.sin(math.radians(a)) for x in (-.25,.75) for a in (-16,8)),
                max(0.775-x*math.sin(math.radians(a)) for x in (-.25,.75) for a in (-16,8))]
            result['limitations'] += ['Tail sweep ignores thickness; derived from declared -4 deg rigging and +/-12 deg control.',
                                     'Engine and fuel bounding boxes overlap; envelope overlap alone does not prove solid interference.']
    result['engineering_status'] = 'flight_not_demonstrated; independent aerodynamic and mechanical validation still required'
    return result


def main():
    out = ROOT/'analysis/results/received_v2_audit01'
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for p in sorted((ROOT/'received_v2_64942345/responses').glob('*/response.json')):
        raw = p.read_bytes()
        expected = json.loads((p.parent/'outcome.json').read_text())['response_sha256']
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Response hash mismatch')
        response = json.loads(raw)['response']
        blocks = re.findall(r'```json\s*(.*?)```', response, re.S)
        if len(blocks) != 1:
            raise ValueError('Expected one JSON block')
        design = json.loads(blocks[0])
        model = p.parent.name
        (out/(model+'.design.json')).write_text(json.dumps(design, indent=2, ensure_ascii=False), encoding='utf-8')
        (out/(model+'.response.md')).write_text(response, encoding='utf-8')
        results[model] = dict(response_sha256=expected, **audit(model, design))
    (out/'summary.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
