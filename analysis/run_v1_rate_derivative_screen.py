"""Apply the same quasi-steady AVL ST screen to accepted V1 trim inputs.

This checks whether the *initial* evaluated designs differ from V2 in rate
derivatives. It still omits body/fin/installed propulsion and gives no full
dynamic eigenvalues. Fable V1 has no mechanically admissible trim and is not
sent through this calculation.
"""
from pathlib import Path
import json
import run_rate_derivative_screen as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'analysis/results/v1_rate_derivative_screen01'
SOURCES = {
    'astra_v1': ROOT/'analysis/results/retrim_v2_attempt01/astra/04_independent_verification',
    'opus_v1': ROOT/'analysis/results/retrim_v2_attempt01/opus/04_independent_verification',
}


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    base.OUT = OUT
    rows = [base.one(name, source) for name, source in SOURCES.items()]
    (OUT/'summary.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
