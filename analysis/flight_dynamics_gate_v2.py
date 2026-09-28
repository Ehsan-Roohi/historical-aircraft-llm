"""Audit V2 dynamics without substituting missing data by zero.

The two-state sign screen is deliberately narrower than a dynamic-stability
assessment.  It uses the lifting-surface AVL derivatives and a *reduced*
alpha/pitch-rate model only; it reports no physical eigenvalues or flight pass.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RHO = 1.225  # kg/m^3, same fixed evaluation assumption as the V2 trim
CASES = {
    "astra_v2": {"mass_kg": 320.0, "speed_m_s": 18.0,
                 "area_m2": 30.0, "chord_m": 2.5},
    "opus_v2": {"mass_kg": 360.0, "speed_m_s": 15.0,
                "area_m2": 38.0, "chord_m": 1.8},
}


def reduced_pitch_signs(case: dict, derivatives: dict) -> dict:
    """Check signs of the idealized alpha-q subsystem for any positive Iyy.

    Assumptions: frozen controls, steady attached-flow lifting surfaces,
    C_Ldot_alpha=C_mdot_alpha=0 *only inside this hypothetical reduced model*;
    no axial-speed, gravity, thrust, body/fin or pilot dynamics.  The real
    missing derivatives are NOT assigned zero in the acceptance gate.
    """
    m, speed, area, chord = (case[k] for k in
                           ("mass_kg", "speed_m_s", "area_m2", "chord_m"))
    if min(m, speed, area, chord) <= 0:
        raise ValueError("All reference quantities must be positive")
    for key in ("CLa", "Cma", "CLq", "Cmq"):
        if key not in derivatives or not math.isfinite(derivatives[key]):
            raise ValueError(f"Missing or invalid {key}")
    qbar = 0.5 * RHO * speed**2
    # U*alpha_dot = Z_alpha*alpha + (U+Z_q)*pitch_rate.
    z_alpha_over_u = -qbar * area * derivatives["CLa"] / (m * speed)
    z_q_over_u = -qbar * area * chord * derivatives["CLq"] / (2*m*speed**2)
    # Iyy*M_alpha and Iyy*M_q have the signs of the dimensional derivatives.
    m_alpha_times_iyy = qbar * area * chord * derivatives["Cma"]
    m_q_times_iyy = qbar * area * chord**2 * derivatives["Cmq"] / (2*speed)
    # trace = Z_alpha/U + (Iyy*M_q)/Iyy;
    # determinant = ((Z_alpha/U)*(Iyy*M_q)
    #                -(1+Z_q/U)*(Iyy*M_alpha))/Iyy.
    det_times_iyy = (z_alpha_over_u*m_q_times_iyy
                     -(1+z_q_over_u)*m_alpha_times_iyy)
    stable_signs_any_positive_iyy = (z_alpha_over_u < 0
        and m_q_times_iyy < 0 and det_times_iyy > 0)
    return {
        "Zalpha_over_U_per_s": z_alpha_over_u,
        "one_plus_Zq_over_U": 1+z_q_over_u,
        "Malpha_times_Iyy_Nm_per_rad": m_alpha_times_iyy,
        "Mq_times_Iyy_Nm_s": m_q_times_iyy,
        "determinant_times_Iyy_kg_m2_per_s2": det_times_iyy,
        "reduced_model_hurwitz_signs_for_any_positive_Iyy": stable_signs_any_positive_iyy,
        "interpretation": "conditional sign check only; NOT full dynamic acceptance",
        "omitted_from_reduced_model": [
            "C_Ldot_alpha and C_mdot_alpha (unknown in physical aircraft)",
            "axial-speed/gravity coupling and phugoid", "propulsion derivatives",
            "body/fin and propeller-wake effects", "flexibility and pilot/control dynamics"],
    }


def audit() -> dict:
    source = ROOT / "analysis/results/v2_rate_derivative_screen02/summary.json"
    rows = json.loads(source.read_text(encoding="utf-8"))
    by_case = {row["case"]: row for row in rows}
    if set(by_case) != set(CASES):
        raise ValueError("Unexpected or missing V2 derivative case")
    records = []
    for name, case in CASES.items():
        row = by_case[name]
        records.append({
            "case": name, "input_source": str(source.relative_to(ROOT)),
            "reference": case,
            "partial_screen": reduced_pitch_signs(case, row["derivatives"]),
            "full_dynamic_gate": "NOT_ASSESSED",
            "required_before_full_gate": [
                "complete three-axis mass tensor, with component intrinsic inertia and CG range",
                "installed full-aircraft force/moment derivatives including axial and propulsion terms",
                "unsteady C_Ldot_alpha and C_mdot_alpha or a justified frequency-domain model",
                "body, vertical tail, propeller slipstream and control-effectiveness derivatives",
                "power-on and power-off trim over speed/CG/control envelope",
                "longitudinal and lateral state matrices, eigenmodes and uncertainty sweep",
                "pilot/control deflection, hinge load, rate and delay limits",
                "structural and ground/flight test evidence before any flightworthiness claim",
            ],
        })
    records.append({"case": "fable_v2", "partial_screen": "NOT_ASSESSED",
                    "full_dynamic_gate": "NOT_ASSESSED",
                    "blocking_predecessor": "reconcile V2/V8 geometry and obtain independent full-aircraft trim"})
    return {"scope": "V2 evidence gate, not a certificate or full dynamics simulation",
            "course_mapping": "Flight Dynamics II CH4 pp. 54-65 and 72-84: EOM, longitudinal and lateral characteristic roots",
            "records": records, "any_aircraft_dynamically_confirmed": False}


if __name__ == "__main__":
    report = audit()
    target = ROOT / "analysis/results/v2_dynamic_gate01.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
