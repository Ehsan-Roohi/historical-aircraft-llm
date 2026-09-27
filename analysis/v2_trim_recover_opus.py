"""Declared capacity recovery: original Opus 14x72 exceeds AVL NVMAX=5000.

Use 12x50 (4800 panels) instead of 14x72 (8064) for eight mirrored patches.
Both directions are refined relative to 10x48 (3840). Preserve failed run.
Same physics/tolerance/4-step bound, initial point from successful coarse trim.
"""
import json
import v2_trim_solve as solver

if __name__=='__main__':
    old=solver.OUT
    r=json.loads((old/'claude-opus-5-5/summary.json').read_text())[0]['trim']
    solver.OUT=old.parent/'v2_trim_opus_capacity_recovery01'
    solver.OUT.mkdir(exist_ok=False)
    result=solver.solve('claude-opus-5-5',[(12,50)],[r['alpha_deg'],r['elevator_TE_down_deg']])
    (solver.OUT/'summary.json').write_text(json.dumps({'scope':__doc__,'results':[result]},indent=2))
    print(json.dumps(result['meshes'][0].get('trim'),indent=2))
