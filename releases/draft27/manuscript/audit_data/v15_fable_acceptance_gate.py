"""Auditable V15 Fable evidence gate; missing aircraft data remain unknown.

This script evaluates an existing, power-off AVL wing/tail result. It does
not construct missing fuselage, fin, propulsion, or unsteady derivatives.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "analysis" / "results"
INPUTS = {
    "v15_first_pass": RESULTS / "v15_first_pass_65023104.json",
    "direct_avl_candidate": RESULTS / "v15_fable_avl_verify01" / "summary.json",
    "surface_force_split": RESULTS / "v15_fable_avl_force_split01" / "summary.json",
    "static_margin_screen": RESULTS / "v15_fable_static_margin_screen01.json",
}
OUTPUT = RESULTS / "v15_fable_six_axis_acceptance_gate01.json"
RHO_KG_M3 = 1.225
G_M_S2 = 9.80665
V_M_S = 13.0


def read_input(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def build_gate() -> dict:
    read = {name: read_input(path) for name, path in INPUTS.items()}
    inputs = {name: item[0] for name, item in read.items()}
    audit = inputs["v15_first_pass"]
    point = inputs["direct_avl_candidate"]
    split = inputs["surface_force_split"]
    slope = inputs["static_margin_screen"]

    assert audit["job_id"] == "65023104"
    assert point["input_geometry_sha256"] == split["geometry_sha256"]
    assert point["input_section_sha256"] == split["section_sha256"]
    assert point["solver_sha256"] == split["solver_sha256"]
    assert point["input_geometry_sha256"] == slope["source_geometry_sha256"]
    assert point["alpha_deg"] == split["alpha_deg"]
    assert point["tail_delta_deg"] == split["tail_delta_deg"]
    assert abs(split["CL_surface_sum"] - split["CL_total"]) < 5e-5
    assert abs(split["Cm_surface_sum"] - split["Cm_total"]) < 5e-5

    mass = audit["fable"]["mass_kg_recomputed"]
    sref = split["Sref_m2"]
    cref = split["Cref_m"]
    q = 0.5 * RHO_KG_M3 * V_M_S**2
    qs = q * sref
    weight = mass * G_M_S2
    lift = qs * point["CL_model"]
    lift_residual = lift - weight
    pitch_moment = qs * cref * point["Cm_model"]
    induced_drag = qs * point["CDind_model"]
    source_forces = {
        name: {
            "lift_N": qs * values["CL_on_Sref"],
            "pitch_moment_Nm": qs * cref * values["Cm_on_Sref_Cref"],
        }
        for name, values in split["groups"].items()
    }
    margins = [
        case["apparent_static_margin_percent_chord"]
        for case in slope["windows"]["fine"]
    ]

    return {
        "scope": "Independent arithmetic and evidence-status gate for one V15 Fable power-off wing/tail AVL point; not physical or full-aircraft trim",
        "input_sha256": {name: item[1] for name, item in read.items()},
        "case": {
            "speed_m_s": V_M_S,
            "density_kg_m3": RHO_KG_M3,
            "mass_kg_assumed": mass,
            "Sref_m2": sref,
            "Cref_m": cref,
            "alpha_deg": point["alpha_deg"],
            "tail_delta_deg": point["tail_delta_deg"],
            "power_state": "propulsion omitted / power-off lifting surfaces",
        },
        "independent_arithmetic": {
            "q_Pa": q,
            "qS_N": qs,
            "weight_N": weight,
            "wing_tail_lift_N": lift,
            "wing_tail_lift_minus_assumed_weight_N": lift_residual,
            "wing_tail_pitch_moment_about_nominal_CG_Nm": pitch_moment,
            "wing_tail_induced_drag_N": induced_drag,
            "surface_contributions": source_forces,
        },
        "six_component_residuals": {
            "Fx": {"status": "UNKNOWN", "reason": "Induced drag is calculated, but profile/parasite drag, windmilling drag and installed thrust are absent."},
            "Fy": {"status": "UNKNOWN", "reason": "Fin, rudder, body, propulsion and sideslip force map are absent; symmetry is not a full-aircraft test."},
            "Fz": {"status": "PARTIAL_PREDICTION", "wing_tail_lift_minus_weight_N": lift_residual, "reason": "Two wings and tail only, using unvalidated section and assumed mass/density."},
            "Mx_CG": {"status": "UNKNOWN", "reason": "Lateral control surfaces and full-aircraft roll moment map are absent."},
            "My_CG": {"status": "PARTIAL_PREDICTION", "wing_tail_pitch_moment_Nm": pitch_moment, "reason": "Propeller thrust-line, body, gear, flexibility and powered slipstream moments are absent."},
            "Mz_CG": {"status": "UNKNOWN", "reason": "Fin/rudder and differential propeller yaw moments are absent."},
        },
        "static_and_dynamic_stability": {
            "apparent_fixed_control_margin_percent_chord_fine_mesh": {"minimum": min(margins), "maximum": max(margins)},
            "installed_static_margin": "UNKNOWN",
            "C_m_alpha_dot": "UNKNOWN",
            "C_Z_alpha_dot": "UNKNOWN",
            "installed_C_m_q_and_lateral_directional_derivatives": "UNKNOWN",
            "validated_longitudinal_and_lateral_modes": "NOT_CALCULABLE",
        },
        "propulsion_and_structure": {
            "H13W_assumed_shaft_power_required_W": audit["fable"]["H13W_required_shaft_W_model"],
            "assumed_shaft_power_available_W": audit["fable"]["shaft_available_W_assumed"],
            "H16W_assumed_shaft_deficit_W": audit["fable"]["H16W_shaft_deficit_W_on_assumptions"],
            "measured_engine_propeller_map": "ABSENT",
            "measured_loaded_clearances_and_allowables": "ABSENT",
        },
        "acceptance": {
            "full_six_component_trim": False,
            "validated_dynamic_derivative_set": False,
            "accepted_modes": False,
            "flightworthiness": "NOT_ESTABLISHED",
        },
    }


def main() -> None:
    report = build_gate()
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Fable V15 six-axis acceptance: HOLD; partial Fz/My only; {OUTPUT.name}")


if __name__ == "__main__":
    main()
