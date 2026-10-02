"""Separate the effect of tip-panel splitting from fin/rudder addition in AVL."""

import hashlib
import json
from pathlib import Path
import subprocess

from avl_reference_gate import parse
from v15_fable_lateral_screen import ROOT, EXE, TRIM


OUT = ROOT / "analysis/results/v15_fable_lateral_geometry_probe01"
BASE = ROOT / "analysis/results/v15_fable_avl_verify01/aircraft.avl"
FINE = ROOT / "analysis/results/v15_fable_lateral_screen01/fine/aircraft.avl"
SECTION = ROOT / "analysis/results/v15_fable_avl_verify01/section.dat"
RESULT = OUT / "summary.json"


def run(name: str, geometry: str, pitch_control: int) -> dict:
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "aircraft.avl").write_text(geometry, encoding="ascii")
    (folder / "section.dat").write_bytes(SECTION.read_bytes())
    cmd = (f"load aircraft.avl\noper\na a {TRIM['alpha_deg']:.10f}\n"
           f"d{pitch_control} d{pitch_control} {TRIM['tail_delta_deg']:.10f}\n"
           "x\nft\nforces.txt\n\nquit\n")
    (folder / "commands.txt").write_text(cmd, encoding="ascii")
    process = subprocess.run([str(EXE)], input=cmd, cwd=folder,
                             capture_output=True, text=True, timeout=180,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    (folder / "stdout.txt").write_text(process.stdout, encoding="utf-8")
    (folder / "stderr.txt").write_text(process.stderr, encoding="utf-8")
    if process.returncode:
        raise RuntimeError(f"AVL failed in {name}: {process.returncode}")
    raw = (folder / "forces.txt").read_text(encoding="utf-8")
    return {
        "CLtot": parse(raw, "CLtot"),
        "Cmtot": parse(raw, "Cmtot"),
        "CDind": parse(raw, "CDind"),
        "geometry_sha256": hashlib.sha256(geometry.encode("ascii")).hexdigest(),
    }


def main() -> None:
    old = BASE.read_text(encoding="ascii")
    expanded = FINE.read_text(encoding="ascii")
    marker = "SURFACE\nfin_fixed\n"
    assert expanded.count(marker) == 1
    split, vertical = expanded.split(marker, 1)
    vertical = marker + vertical
    OUT.mkdir(parents=True, exist_ok=False)
    data = {
        "scope": "Power-off AVL geometry decomposition at old wing/tail candidate; neither case is the installed aircraft nor a retrim",
        "old_point": {key: TRIM[key] for key in ("alpha_deg", "tail_delta_deg", "CL_model", "Cm_model")},
        "split_tip_only": run("split_tip_only", split, 2),
        "original_wing_plus_vertical": run("original_wing_plus_vertical", old.rstrip() + "\n" + vertical, 1),
        "expanded_tip_and_vertical": {
            key: json.loads((ROOT / "analysis/results/v15_fable_lateral_screen01/fine_summary.json").read_text(encoding="utf-8"))["cases"]["neutral"][key]
            for key in ("CLtot", "Cmtot", "CDind")
        },
    }
    RESULT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("Fable V15 geometry decomposition complete; no flight or trim verdict")


if __name__ == "__main__":
    main()
