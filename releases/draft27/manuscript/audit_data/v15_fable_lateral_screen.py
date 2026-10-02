"""Quasi-steady V15 Fable lateral/control screen; not installed-aircraft data."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from avl_reference_gate import parse
from v15_fable_avl_screen import ROOT, EXE, SOURCE, FOILS, section, surface


OUT = ROOT / "analysis" / "results" / "v15_fable_lateral_screen01"
TRIM = json.loads((ROOT / "analysis/results/v15_fable_avl_verify01/summary.json").read_text(encoding="utf-8"))
CASES = {
    "neutral": (0.0, 0.0, 0.0),
    "beta_plus": (3.0, 0.0, 0.0),
    "beta_minus": (-3.0, 0.0, 0.0),
    "roll_plus": (0.0, 4.0, 0.0),
    "roll_minus": (0.0, -4.0, 0.0),
    "rudder_plus": (0.0, 0.0, 5.0),
    "rudder_minus": (0.0, 0.0, -5.0),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry(design: dict, nc: int, ns: int) -> str:
    geom = design["section_2_three_view_coordinate_schedule"]
    lower = geom["lifting_surfaces"]["P01_lower_deck"]
    upper = geom["lifting_surfaces"]["P02_upper_deck_fixed"]
    tip = geom["lifting_surfaces"]["P03L_P03R_tip_panels"]
    tail = geom["tail_group"]["P11_all_moving_tail"]
    fin = geom["tail_group"]["P12_fin"]
    rudder = geom["tail_group"]["P13_rudder"]
    cg = design["section_3_mass_ledger"]["sums_nominal_AR"]["all_up_75kg_seat0.30_full"]["cg_xyz"]
    ref = design["section_6_evaluator_inputs"]["reference"]
    assert lower["LE_root"][0] == upper["LE_root"][0] == 0.95
    assert tip["hinge_line_x"] == 1.505
    assert fin["area_m2"] == 0.72 and abs(rudder["TE_x"] - rudder["hinge_x"] - 0.90) < 1e-9
    assert rudder["hinge_x"] == fin["TE"][0] == 6.60
    assert tail["area_m2"] == 4.60

    lines = [
        "Fable V15 power-off lateral surface screen; no body/propeller",
        "0", "0 0 0",
        f"{ref['S_ref_m2']} {ref['c_ref_m']} {ref['b_ref_m']}",
        " ".join(str(value) for value in cg), "0",
    ]
    lines += surface("lower", [(0.95, 0, 0, 1.85, 0), (0.95, 5.75, 0, 1.85, 0)], nc, ns, 1, foil=True)
    lines += surface("upper_center", [(0.95, 0, 1.85, 1.85, 0), (0.95, 4.25, 1.85, 1.85, 0)], nc, max(8, round(ns * 4.25 / 5.75)), 2, foil=True)
    lines += ["SURFACE", "upper_tip_pair", f"{nc} 1 {max(8, round(ns * 1.5 / 5.75))} 1", "COMPONENT", "3", "YDUPLICATE", "0"]
    for y in (4.25, 5.75):
        lines += section(0.95, y, 1.85, 1.85, 0, foil=True)
        # A full-tip normal rotation approximates the model's all-moving tip;
        # AVL does not move its vertices or represent the physical x=1.505 hinge.
        lines += ["CONTROL", "roll 1.0 0.0 0 1 0 -1"]
    lines += surface("tail_halves", [(tail["LE_x"], 0.55, 0.775, 1.0, -4.0),
                                      (tail["LE_x"], 2.85, 0.775, 1.0, -4.0)],
                     nc, max(8, ns // 2), 4, tail_control=True)
    # Top-to-bottom vertical ordering follows the AVL manual's yaw-sign convention.
    lines += ["SURFACE", "fin_fixed", f"{nc} 1 {max(8, ns // 4)} 1", "COMPONENT", "5"]
    lines += section(5.40, 0, 1.80, 1.20)
    lines += section(5.40, 0, 1.20, 1.20)
    lines += ["SURFACE", "rudder_all_moving", f"{nc} 1 {max(8, ns // 4)} 1", "COMPONENT", "6"]
    for z in (1.80, 0.80):
        lines += section(6.60, 0, z, 0.90)
        lines += ["CONTROL", "yaw 1.0 0.0 0 0 -1 1"]
    return "\n".join(lines) + "\n"


def foil_text() -> str:
    foil = json.loads(FOILS.read_text(encoding="utf-8"))["fable"]
    coordinates = list(zip(foil["x"], foil["upper"]))[::-1] + list(zip(foil["x"], foil["lower"]))[1:]
    return "Fable V0 inherited candidate section, unvalidated\n" + "\n".join(f"{x} {z}" for x, z in coordinates) + "\n"


def run_mesh(label: str, nc: int, ns: int, design: dict, trim: dict) -> dict:
    target = OUT / label
    target.mkdir(parents=True, exist_ok=True)
    if (target / "aircraft.avl").exists():
        raise FileExistsError(f"Refusing to overwrite an existing AVL case: {label}")
    aircraft = target / "aircraft.avl"
    aircraft.write_text(geometry(design, nc, ns), encoding="ascii")
    (target / "section.dat").write_text(foil_text(), encoding="ascii")
    commands = "load aircraft.avl\noper\n"
    for name, (beta, roll, yaw) in CASES.items():
        commands += (
            f"a a {trim['alpha_deg']:.10f}\n"
            f"b b {beta:.10f}\n"
            f"d1 d1 {roll:.10f}\n"
            f"d2 d2 {trim['tail_delta_deg']:.10f}\n"
            f"d3 d3 {yaw:.10f}\n"
            f"x\nft\n{name}.txt\n"
        )
    commands += "\nquit\n"
    (target / "commands.txt").write_text(commands, encoding="ascii")
    process = subprocess.run([str(EXE)], input=commands, cwd=target,
                             capture_output=True, text=True, timeout=600,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    (target / "stdout.txt").write_text(process.stdout, encoding="utf-8")
    (target / "stderr.txt").write_text(process.stderr, encoding="utf-8")
    if process.returncode:
        raise RuntimeError(f"AVL {label} return code {process.returncode}")
    data = {}
    for name, (beta, roll, yaw) in CASES.items():
        output = target / f"{name}.txt"
        raw = output.read_text(encoding="utf-8")
        row = {key: parse(raw, key) for key in ("Alpha", "Beta", "CLtot", "CDind", "Cmtot", "CYtot", "Cltot", "Cntot")}
        row.update({"beta_command_deg": beta, "roll_command_deg": roll, "rudder_command_deg": yaw, "file_sha256": sha(output)})
        if abs(row["Beta"] - beta) > 1e-5:
            raise ValueError(f"AVL beta mismatch: {name}")
        data[name] = row
    return {"geometry_sha256": sha(aircraft), "section_sha256": sha(target / "section.dat"), "cases": data}


def slope(rows: dict, positive: str, negative: str, degrees: float, key: str) -> float:
    return (rows[positive][key] - rows[negative][key]) / math.radians(2 * degrees)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", choices=("coarse", "fine"), required=True)
    parser.add_argument("--around-retrim", action="store_true")
    args = parser.parse_args()
    wrapper = json.loads(SOURCE.read_text(encoding="utf-8"))
    design = json.loads(wrapper["response"])
    OUT.mkdir(parents=True, exist_ok=True)
    nc, ns = {"coarse": (8, 32), "fine": (12, 64)}[args.mesh]
    label = args.mesh + ("_retrim" if args.around_retrim else "")
    trim = TRIM
    if args.around_retrim:
        trim = json.loads((ROOT / "analysis/results/v15_fable_expanded_retrim01/summary.json").read_text(encoding="utf-8"))
        trim = {"alpha_deg": trim["alpha_deg"], "tail_delta_deg": trim["tail_command_deg"]}
    result = run_mesh(label, nc, ns, design, trim)
    cases = result["cases"]
    result.update({
        "scope": "Power-off rigid AVL prediction only: inherited unvalidated camber, idealized whole-tip normal rotation and all-moving rudder, no body/gear/propeller/slipstream or measured polar; not an accepted installed derivative set",
        "source_response_sha256": sha(SOURCE), "solver_sha256": sha(EXE),
        "evaluation_trim": trim,
        "wing_tip_hinge_note": "Declared x=1.505 hinge is not modelled as moving vertices; CONTROL rotates full-tip panel normals only.",
        "moment_frame_note": "AVL geometry X downstream/Y right/Z up; output moments use AVL standard body X forward/Z down. Preserve this sign convention when comparing to model declarations.",
        "slopes_per_rad_at_alpha_and_tail_candidate": {
            key: {
                "beta": slope(cases, "beta_plus", "beta_minus", 3, key),
                "roll_tip_command": slope(cases, "roll_plus", "roll_minus", 4, key),
                "rudder_command": slope(cases, "rudder_plus", "rudder_minus", 5, key),
            }
            for key in ("CYtot", "Cltot", "Cntot")
        },
        "flightworthiness": "NOT_ASSESSED",
    })
    (OUT / f"{label}_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Fable V15 {label} lateral surface cases: {len(cases)} completed; not whole-aircraft trim")


if __name__ == "__main__":
    main()
