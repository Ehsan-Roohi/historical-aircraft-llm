"""Compare initial/revised pitch evidence without equating static and dynamic tests."""
from pathlib import Path
import json

from flight_dynamics_gate_v2 import CASES, reduced_pitch_signs

ROOT = Path(__file__).resolve().parents[1]


def main():
    v1_rates = {row['case']: row for row in json.loads((ROOT/
        'analysis/results/v1_rate_derivative_screen01/summary.json').read_text(encoding='utf-8'))}
    v2_rates = {row['case']: row for row in json.loads((ROOT/
        'analysis/results/v2_rate_derivative_screen02/summary.json').read_text(encoding='utf-8'))}
    v1_trim = {row['model']: row for row in json.loads((ROOT/
        'analysis/results/retrim_v2_attempt01/summary.json').read_text(encoding='utf-8'))['records']}
    records=[]
    for name in ('astra','opus'):
        old = v1_trim[name]
        accepted = next(row for row in old['records'] if row['directory'].endswith('04_independent_verification'))
        case_v1 = {'mass_kg': old['mass_kg'],
                   'speed_m_s': accepted['rebalanced_state']['speed_m_s'],
                   'area_m2': old['Sref_m2'], 'chord_m': old['Cref_m']}
        for version, case, rate in (
            ('V1', case_v1, v1_rates[name+'_v1']),
            ('V2', CASES[name+'_v2'], v2_rates[name+'_v2'])):
            screen = reduced_pitch_signs(case, rate['derivatives'])
            records.append({'model': name, 'version': version,
                            'case': case, 'derivative_source': rate['source'],
                            'Cma_per_rad': rate['derivatives']['Cma'],
                            'Cmq': rate['derivatives']['Cmq'],
                            'static_pitch_restoring_in_lifting_model': rate['derivatives']['Cma']<0,
                            'conditional_reduced_pitch_hurwitz': screen[
                                'reduced_model_hurwitz_signs_for_any_positive_Iyy'],
                            'dynamic_flight_acceptance': 'NOT_ASSESSED',
                            'partial_screen': screen})
    result={'scope':'V1 versus V2 lifting-surface sign screens; unmatched speeds and architectures',
            'critical_distinction':'Positive Cma can coexist with a stable sign test in the omission-based two-state model; neither determines full-aircraft modes.',
            'records':records,
            'fable':'V1 geometric control collision and V2 unresolved integrated geometry prevent a credible independent trim/dynamic comparison'}
    out=ROOT/'analysis/results/v1_v2_pitch_gate_comparison01.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source':str(out.relative_to(ROOT)),
                      'summary':[(r['model'],r['version'],r['Cma_per_rad'],r['Cmq'],
                                  r['static_pitch_restoring_in_lifting_model'],
                                  r['conditional_reduced_pitch_hurwitz']) for r in records]},indent=2))


if __name__=='__main__':main()
