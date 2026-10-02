"""Evaluator-only induced-drag substitution; not an installed trim model."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = Path.cwd() / 'output/received_v16_fable_65061669/claude-fable-5-1/response.json'
TRIM = HERE / 'fable_v16_surface_retrim01/summary.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def evaluate():
    model = json.loads(json.loads(RAW.read_text(encoding='utf-8'))['response'])
    section = model['section_6_drag_and_propulsion']
    trims = json.loads(TRIM.read_text(encoding='utf-8'))
    assert sha(RAW) == trims['source_sha256']
    available = section['P_out_available_W']['value']
    qS = 0.5 * 1.225 * 13**2 * 42
    results = []
    for name, index in [('N13', 0), ('H13W', 6)]:
        claim = next(c for c in section['cases'] if c['id'] == name)
        trim = trims['cases'][index]
        assert abs(claim['kg'] - trim['case']['mass_kg']) < 1e-9
        # Preserve printed baseline D and P, infer its efficiency explicitly.
        # Replace the printed induced coefficient; never add two induced drags.
        eta = claim['D_N'] * 13 / claim['P_req_W']
        delta_drag = qS * (trim['trim']['CDind'] - claim['CDi'])
        drag = claim['D_N'] + delta_drag
        power = claim['P_req_W'] + delta_drag * 13 / eta
        assert abs(power - drag * 13 / eta) < 1e-8
        assert 0 < eta < 1 and delta_drag > 0
        results.append({
            'case': name, 'trim_index': index,
            'mass_kg': claim['kg'], 'reported_CDi': claim['CDi'],
            'surface_AVL_CDi': trim['trim']['CDind'],
            'reported_drag_N': claim['D_N'], 'reported_power_W': claim['P_req_W'],
            'efficiency_inferred_from_printed_D_V_P': eta,
            'delta_drag_N': delta_drag, 'hybrid_drag_N': drag,
            'hybrid_required_shaft_power_W': power,
            'assumed_available_shaft_power_W': available,
            'reserve_fraction': available / power - 1,
            'headroom_above_required_W': available - power,
            'margin_against_1p15_required_W': available - 1.15 * power,
            'passes_exploratory_15_percent_reserve': available >= 1.15 * power,
            'maximum_additional_drag_before_15_percent_reserve_lost_N':
                (available / 1.15 - claim['P_req_W']) * eta / 13,
        })
    assert results[1]['headroom_above_required_W'] > 0
    assert results[1]['margin_against_1p15_required_W'] < 0
    return {
        'status': 'EVALUATOR_HYBRID_SENSITIVITY_ONLY',
        'source_sha256': sha(RAW), 'trim_summary_sha256': sha(TRIM),
        'script_sha256': sha(Path(__file__)), 'qS_N': qS,
        'method': 'Anchor to printed D/P and replace only printed CDi by matching-mass fine-grid surface AVL CDind at 13 m/s. Efficiency inferred from printed values; all other drag and power assumptions held fixed.',
        'limitations': [
            'Not a coupled installed-aircraft six-component trim calculation.',
            'Surface AVL excludes body, wires, masts, fairings and propulsion; sections unvalidated.',
            'Printed baseline non-induced drag, efficiency and engine power remain model assumptions.',
            '15 percent is an exploratory project criterion, not a safety standard.',
            'Positive absolute headroom does not establish flight or dynamic stability.',
            'No engine resizing or mass feedback performed; no measured data introduced.'
        ],
        'cases': results, 'engineering_acceptance': False,
    }

if __name__ == '__main__':
    result = evaluate()
    destination = HERE / 'fable_v16_power_sensitivity01.json'
    destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
