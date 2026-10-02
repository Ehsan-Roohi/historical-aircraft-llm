"""Explicit point-mass sensitivity, not sizing or certification of a tail spar."""
import json
from pathlib import Path
import v15_fable_tail_trade as trade

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_tail_reinforcement_sensitivity01'

def main():
    OUT.mkdir(exist_ok=False)
    baseline=json.loads((ROOT/'analysis/results/v15_fable_tail_trade01/fine.json').read_text())
    rows=[]
    for c in baseline['cases']:
        mass=c['mass_kg'];x=c['cg_m'][0];np=x+1.85*c['surface_SM']
        budgets={}
        for target in (0,.03):
            limit=np-1.85*target
            budgets[str(target)]=mass*(limit-x)/(5.65-limit)
        rows.append(dict(fuel_kg=c['fuel_kg'],frozen_NP_x_m=np,
                         added_point_mass_budget_kg=budgets))
    d=json.loads(json.loads(trade.SOURCE.read_text(encoding='utf-8'))['response'])
    d['section_3_mass_ledger']['rows'].append(dict(ID='EVAL_REINFORCEMENT',name='Illustrative added root hardware mass; not structurally sized',mass_kg=2.,centroid=[5.65,0,.775],I_intr=[0.,0.,0.],tag='EXPLICIT POINT-MASS SENSITIVITY ONLY'))
    trade.OUT=OUT
    # The empty-fuel/light-pilot state had the smaller fine-grid baseline margin.
    result=trade.one(d,1.75,(65,.35,0),'fine','plus2kg')
    report=dict(scope='Conditional two-kilogram point-mass sensitivity; no structural design or modes',
       assumed_added_mass_kg=2.,assumed_location_m=[5.65,0,.775],
       inertia_note='Zero intrinsic inertia is an explicit mathematical point-mass approximation, not a claim about actual reinforcement.',
       frozen_NP_budget_screen=rows,retrimmed_case=result,
       limitations=['Real reinforcement mass/distribution and stiffness unknown','Frozen-NP budgets are screens, not allowable installed masses','Single loading state re-trimmed; other states require verification'],
       accepted_aircraft_modes=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
