"""Retrim the expanded Fable V15 rigid lifting-surface AVL model, power off."""

import hashlib
import json
from pathlib import Path
import subprocess

from avl_reference_gate import parse
from v15_fable_lateral_screen import ROOT, EXE, TRIM


SOURCE = ROOT / "analysis/results/v15_fable_lateral_screen01/fine"
OUT = ROOT / "analysis/results/v15_fable_expanded_retrim01"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    for name in ("aircraft.avl", "section.dat"):
        (OUT / name).write_bytes((SOURCE / name).read_bytes())
    cl_target = TRIM["CL_target_from_assumed_mass_and_density"]
    commands = (
        "load aircraft.avl\noper\n"
        f"a a {TRIM['alpha_deg']:.10f}\n"
        f"d2 d2 {TRIM['tail_delta_deg']:.10f}\n"
        f"a c {cl_target:.10f}\n"
        "d2 pm 0\n"
        "x\nft\nforces.txt\n\nquit\n"
    )
    (OUT / "commands.txt").write_text(commands, encoding="ascii")
    process = subprocess.run([str(EXE)], input=commands, cwd=OUT,
                             capture_output=True, text=True, timeout=180,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    (OUT / "stdout.txt").write_text(process.stdout, encoding="utf-8")
    (OUT / "stderr.txt").write_text(process.stderr, encoding="utf-8")
    if process.returncode:
        raise RuntimeError(f"AVL return code {process.returncode}")
    text = (OUT / "forces.txt").read_text(encoding="utf-8")
    report = {
        "scope": "Power-off, rigid, inviscid wing/tail/fin/rudder and split-tip surface model; not installed-aircraft six-component trim",
        "geometry_sha256": hashlib.sha256((OUT / "aircraft.avl").read_bytes()).hexdigest(),
        "section_sha256": hashlib.sha256((OUT / "section.dat").read_bytes()).hexdigest(),
        "solver_sha256": hashlib.sha256(EXE.read_bytes()).hexdigest(),
        "CL_target_assumed_mass_density": cl_target,
        "alpha_deg": parse(text, "Alpha"),
        "beta_deg": parse(text, "Beta"),
        "roll_tip_command_deg": parse(text, "roll"),
        "tail_command_deg": parse(text, "pitch"),
        "rudder_command_deg": parse(text, "yaw"),
        "CL_model": parse(text, "CLtot"),
        "Cm_model": parse(text, "Cmtot"),
        "CY_model": parse(text, "CYtot"),
        "Cl_model": parse(text, "Cltot"),
        "Cn_model": parse(text, "Cntot"),
        "CDind_model": parse(text, "CDind"),
        "missing": ["engine and propeller", "body", "gear", "viscous/profile drag", "slipstream", "flexible aeroelastic shape", "measured section polar", "loaded control clearance"],
        "flightworthiness": "NOT_ASSESSED",
    }
    assert abs(report["CL_model"] - cl_target) < 2e-4
    assert abs(report["Cm_model"]) < 2e-4
    assert -16 <= report["tail_command_deg"] <= 8
    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Expanded Fable V15 surface retrim completed; no full-aircraft acceptance")


if __name__ == "__main__":
    main()
