"""Compare coarse/fine Fable V15 lateral AVL slopes at the expanded retrim."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "analysis/results/v15_fable_lateral_screen01"
COARSE = BASE / "coarse_retrim_summary.json"
FINE = BASE / "fine_retrim_summary.json"
RETRIM = ROOT / "analysis/results/v15_fable_expanded_retrim01/summary.json"
GEOMETRY_PROBE = ROOT / "analysis/results/v15_fable_lateral_geometry_probe01/summary.json"
TARGET = ROOT / "analysis/results/v15_fable_lateral_derivative_gate01.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_gate() -> dict:
    coarse, fine, retrim, probe = map(load, (COARSE, FINE, RETRIM, GEOMETRY_PROBE))
    assert coarse["source_response_sha256"] == fine["source_response_sha256"]
    assert fine["geometry_sha256"] == retrim["geometry_sha256"]
    assert fine["section_sha256"] == retrim["section_sha256"]
    assert fine["solver_sha256"] == retrim["solver_sha256"]
    assert abs(fine["cases"]["neutral"]["CLtot"] - retrim["CL_model"]) < 1e-5
    assert abs(fine["cases"]["neutral"]["Cmtot"] - retrim["Cm_model"]) < 1e-5

    derivatives = {}
    for coefficient in ("CYtot", "Cltot", "Cntot"):
        derivatives[coefficient] = {}
        for input_name in ("beta", "roll_tip_command", "rudder_command"):
            c = coarse["slopes_per_rad_at_alpha_and_tail_candidate"][coefficient][input_name]
            f = fine["slopes_per_rad_at_alpha_and_tail_candidate"][coefficient][input_name]
            derivatives[coefficient][input_name] = {
                "coarse_per_rad": c,
                "fine_per_rad": f,
                "absolute_mesh_difference_per_rad": abs(f - c),
                "relative_mesh_difference_percent_of_fine": 100 * abs(f - c) / abs(f) if f else None,
                "status": "PREDICTED_QUASI_STEADY_ONLY",
            }

    original = probe["old_point"]
    expanded = probe["expanded_tip_and_vertical"]
    return {
        "scope": "Evaluator-only AVL rigid/inviscid lateral derivative screen around a conditional power-off surface retrim, not measured or installed-aircraft derivatives",
        "input_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
                         for path in (COARSE, FINE, RETRIM, GEOMETRY_PROBE)},
        "source_response_sha256": fine["source_response_sha256"],
        "reference": {"Sref_m2": 42.0, "Cref_m": 1.85, "Bref_m": 11.5, "alpha_deg": retrim["alpha_deg"],
                      "tail_command_deg": retrim["tail_command_deg"], "speed_m_s": 13.0,
                      "density_kg_m3": 1.225, "power_state": "power-off model; propeller omitted"},
        "geometry_sensitivity": {
            "continuous_upper_deck_CL_at_old_point": original["CL_model"],
            "split_tip_CL_at_old_point": expanded["CLtot"],
            "split_tip_CL_change": expanded["CLtot"] - original["CL_model"],
            "split_tip_Cm_change": expanded["Cmtot"] - original["Cm_model"],
            "adding_vertical_surfaces_at_symmetric_zero_control": "No change in CL/Cm at the printed precision in the diagnostic; split-surface representation causes the difference.",
            "interpretation": "Numerical representation of a hinged spanwise interface, not measured effect of a physical gap or seal; actual gap/elasticity remains unspecified.",
        },
        "retrim": {"alpha_deg": retrim["alpha_deg"], "tail_command_deg": retrim["tail_command_deg"],
                   "CL": retrim["CL_model"], "Cm": retrim["Cm_model"],
                   "coarse_CL_at_fine_retrim": coarse["cases"]["neutral"]["CLtot"],
                   "coarse_Cm_at_fine_retrim": coarse["cases"]["neutral"]["Cmtot"]},
        "finite_difference_derivatives": derivatives,
        "sign_interpretation": {
            "C_n_beta": "Positive in AVL standard moment axes, a restoring weathercock tendency in this surface model only.",
            "roll_tip_yaw_coupling": "The model's roll and yaw responses to the signed tip command oppose a coordinated heading response (adverse-yaw-like); physical hinge gap and control shape are unverified.",
            "C_l_beta": "Near zero and mesh-sensitive; no robust dihedral/spiral conclusion.",
        },
        "missing_for_modes": ["C_l_p", "C_l_r", "C_n_p", "C_n_r", "C_Y_p", "C_Y_r", "full physical inertia", "installed powered aerodynamic map", "unsteady wake and slipstream", "control travel/rate/hinge moments"],
        "acceptance": {"whole_aircraft_six_component_trim": False, "validated_lateral_derivatives": False,
                       "accepted_lateral_modes": False, "flightworthiness": "NOT_ESTABLISHED"},
    }


def main() -> None:
    report = build_gate()
    TARGET.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Fable V15 lateral gate: predicted static/control slopes only; no modes accepted")


if __name__ == "__main__":
    main()
