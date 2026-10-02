"""Heavy-load surface-only speed screen. No installed trim or flight acceptance."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'analysis'))
from v15_fable_corrected_surface_screen import run, parse_st, sha
from avl_reference_gate import parse

HERE = Path(__file__).resolve().parent
PARENT = HERE / 'fable_v16_surface_retrim01/case_06'
OUT = HERE / 'fable_v16_speed_screen01'

def main():
    # Exclusive creation prevents an accidental concurrent or repeated run.
    OUT.mkdir(exist_ok=False)
    parent = json.loads((PARENT / 'result.json').read_text())
    assert parent['case']['mass_kg'] == 375.106
    records = []
    for speed in (12, 16):
        folder = OUT / f'V{speed}'
        folder.mkdir()
        for name in ('aircraft.avl', 'section.dat'):
            (folder / name).write_bytes((PARENT / name).read_bytes())
        target = parent['case']['mass_kg'] * 9.80665 / (.5 * 1.225 * speed**2 * 42)
        commands = (f'load aircraft.avl\noper\na a {parent["trim"]["Alpha"]}\n'
                    f'd2 d2 {parent["trim"]["pitch"]}\na c {target:.12f}\nd2 pm 0\nx\n'
                    'ft\nforces.txt\nst\nstability.txt\n\nquit\n')
        run(folder, commands)
        force = (folder / 'forces.txt').read_text()
        trim = {k: parse(force, k) for k in ('Alpha','pitch','CLtot','Cmtot','CYtot','Cltot','Cntot','CDind')}
        st = parse_st((folder / 'stability.txt').read_text())
        assert abs(trim['CLtot'] - target) < 2e-4
        assert abs(trim['Cmtot']) < 2e-4
        record = dict(speed_mps=speed, mass_kg=parent['case']['mass_kg'],
                      target_CL=target, trim=trim,
                      absolute_tail_deg=trim['pitch'] - 4,
                      surface_SM_percent=-100*st['Cma']/st['CLa'],
                      Cma=st['Cma'], CLa=st['CLa'],
                      geometry_sha256=sha(folder/'aircraft.avl'),
                      forces_sha256=sha(folder/'forces.txt'),
                      stability_sha256=sha(folder/'stability.txt'))
        (folder/'result.json').write_text(json.dumps(record, indent=2)+'\n')
        records.append(record)
        print(json.dumps(record), flush=True)
    report = dict(cases=records, source_result_sha256=sha(PARENT/'result.json'),
                  script_sha256=sha(Path(__file__)),
                  scope='Same V16 heavy-load geometry/CG, fine rigid surface AVL. Speed enters target lift only; no Reynolds-dependent measured polar, stall, body, bracing drag, propulsion or installed six-component trim. Whole-tail normal rotation, not rotated vertices.',
                  flight_acceptance=False, dynamic_modes_verified=False)
    (OUT/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    print('COMPLETE 2', flush=True)

if __name__ == '__main__':
    main()
