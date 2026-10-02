"""Audit the conditional researcher tail trade and write a preservation note."""
import hashlib
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_fable_tail_trade01'

def main():
    selection=json.loads((OUT/'trade_extended.json').read_text())
    envelope=json.loads((OUT/'envelope.json').read_text())
    fine=json.loads((OUT/'fine.json').read_text())
    assert len(envelope['cases'])==8 and len(fine['cases'])==2
    cases=envelope['cases']+fine['cases']
    assert all(c['within_declared_tail_travel'] for c in cases)
    assert all(c['surface_SM']>0 for c in cases)
    for p in OUT.glob('*/result.json'):
        r=json.loads(p.read_text())
        for field,name in [('input_sha256','aircraft.avl'),('forces_sha256','forces.txt'),('stability_sha256','stability.txt')]:
            assert hashlib.sha256((p.parent/name).read_bytes()).hexdigest()==r[field]
    differences=[]
    for r in fine['cases']:
        coarse=next(c for c in envelope['cases'] if c['pilot_kg']==r['pilot_kg'] and c['fuel_kg']==r['fuel_kg'] and c['seat_x_m']==r['seat_x_m'])
        differences.append(dict(fuel_kg=r['fuel_kg'],fine_SM=r['surface_SM'],coarse_SM=coarse['surface_SM'],absolute_mesh_difference=r['surface_SM']-coarse['surface_SM']))
    scale=selection['selected_scale']
    report=dict(status='CONDITIONAL_SURFACE_MODEL_CANDIDATE_ONLY',scale=scale,tail_area_m2=4.6*scale,
       span_including_center_gap_m=2*(.55+2.3*scale),assumed_tail_mass_kg=8*scale,added_tail_mass_kg=8*(scale-1),
       assumed_nominal_mass_kg=353.2+8*(scale-1),coarse_loading_states=8,fine_loading_states=2,
       coarse_SM_range_percent=[100*min(c['surface_SM'] for c in envelope['cases']),100*max(c['surface_SM'] for c in envelope['cases'])],
       fine_results=differences,
       structural_scaling_warning=dict(assumption='Identical uniform load per unit span and unchanged EI; illustrative cantilever scaling, NOT a structural result',
         root_bending_ratio=scale**2,tip_deflection_ratio=scale**4),
       remaining=['Full eight-state fine-grid envelope','Tail spar/root/hinge sizing and added reinforcement mass',
                  'Deflected geometry, control actuation and clearance','Installed propulsion and power after drag/mass changes',
                  'Unsteady derivatives, physical inertia, coupled dynamic modes','Robustness to airfoil/body/propeller model errors'],
       accepted_aircraft_modes=False,flightworthiness=False)
    (OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['RESEARCHER-GENERATED FABLE TAIL TRADE — ADDENDUM TO COMPLETE DRAFT21',
           'Original model-authored V15 and complete draft21 remain unchanged. This is not a new Fable response.',
           '', 'Geometry/mass changes:',
           f'Tail area 4.60 -> {4.6*scale:.3f} m2; outer span including center gap 5.70 -> {report["span_including_center_gap_m"]:.3f} m.',
           f'Assumed tail mass 8.0 -> {8*scale:.1f} kg; nominal all-up mass 353.2 -> {report["assumed_nominal_mass_kg"]:.1f} kg.',
           'Hinge x, root station and chord retained. Intrinsic tail inertia recomputed as uniform thin rectangular half-plates.',
           'Unknown reinforcement/actuator mass is excluded from this conditional trade, NOT asserted zero or closed.',
           '', 'Results:',json.dumps(report['coarse_SM_range_percent'])+' percent coarse-grid range over eight loading states.',
           json.dumps(differences,indent=2),
           '', 'Interpretation:',
           'The selected candidate reverses the negative pitch-stiffness result within the restricted surface model. It does not establish full-aircraft static stability, accepted modes or flyability.',
           'A 3 percent exploratory selection screen is an evaluator choice, not an airworthiness or handling-quality requirement.',
           f'Under the same uniform span load and unchanged EI, a {scale:.2f} span-length factor implies {scale**2:.3f} times root bending and {scale**4:.3f} times tip deflection; actual loads and stiffness must be redesigned.',
           'Thus larger tail area is not a free improvement: structural, mass, power and control closure remains essential.',
           '', 'Next: size/test the revised tail load path and hinge, then feed resulting mass back into trim; compare a less enlarged tail with feasible forward mass redistribution.',
           'Reproducibility: analysis/v15_fable_tail_trade.py, analysis/test_v15_tail_trade.py, analysis/audit_v15_tail_trade.py and analysis/results/v15_fable_tail_trade01/.',
           'Raw original responses preserved. This addendum is not yet merged into the draft21 PDF.']
    (ROOT/'paper/FABLE_RESEARCHER_TAIL_TRADE_ADDENDUM.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    files=list(OUT.rglob('*'))+[ROOT/'analysis'/name for name in (
        'v15_fable_tail_trade.py','test_v15_tail_trade.py','audit_v15_tail_trade.py',
        'v15_fable_loading_gate.py','v15_fable_corrected_surface_screen.py',
        'v15_fable_lateral_screen.py','v15_fable_avl_screen.py','avl_reference_gate.py')]
    files += [ROOT/'paper/FABLE_RESEARCHER_TAIL_TRADE_ADDENDUM.txt',
              ROOT/'analysis/results/v15_fable_loading_gate01.json']
    files=[p for p in files if p.is_file()]
    manifest=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
    zip_path=ROOT/'output/Fable_researcher_tail_trade01_audited.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(ROOT).as_posix())
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2))
        z.writestr('REPRODUCIBILITY.txt','Local audit snapshot, not Overleaf. Existing project dependencies (AVL executable, original V15 response and inherited airfoil/helper inputs) are referenced, not all redistributed here. No flight approval.\n')
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        for item in manifest:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
