"""Check V3 model-supplied drag/power arithmetic without assuming it is measured.

There is no installed engine curve or propeller map in these three responses.
The computations below are conditional requirements, not a propulsion pass.
"""

import argparse
import hashlib
import json
from pathlib import Path

from audit_v3_geometry_loading import SOURCES, load_design


ROOT = Path(__file__).resolve().parents[1]


def required_engine_power(drag_n, speed_m_s, prop_eff, drive_eff=1.0):
    if min(drag_n, speed_m_s, prop_eff, drive_eff) <= 0:
        raise ValueError("positive drag, speed and efficiencies required")
    if prop_eff > 1 or drive_eff > 1:
        raise ValueError("efficiencies cannot exceed unity")
    return drag_n * speed_m_s / (prop_eff * drive_eff)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    a, f, o = (load_design(SOURCES[name]) for name in SOURCES)
    result = {
        "scope": "arithmetic of model-assumed drag, efficiency and unverified power targets only",
        "source_sha256": {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in SOURCES.items()},
        "rho_or_drag_validation": "NONE",
        "measured_installed_engine_curve": False,
        "measured_installed_propeller_map": False,
        "cases": {},
    }

    ap = a["propulsion"]
    eta_prop = ap["assumed_efficiencies"]["propeller"]
    eta_drive = ap["assumed_efficiencies"]["drive"]
    target = ap["engine_target_W"]
    astra_rows = []
    for row in ap["requirements_at_18_m_s"]:
        expected = required_engine_power(row["drag_N"], 18, eta_prop, eta_drive)
        astra_rows.append({
            "assumed_drag_N": row["drag_N"],
            "computed_useful_power_W": row["drag_N"] * 18,
            "computed_engine_power_W": round(expected, 3),
            "reported_engine_power_W": row["engine_W"],
            "arithmetic_difference_W": round(expected - row["engine_W"], 3),
            "margin_to_unverified_target_W": round(target - expected, 3),
            "minimum_prop_efficiency_at_target_and_assumed_drive": round(
                row["drag_N"] * 18 / (target * eta_drive), 6),
        })
    result["cases"]["astra"] = {
        "speed_m_s": 18,
        "propeller_efficiency_assumed": eta_prop,
        "drive_efficiency_assumed": eta_drive,
        "engine_target_W_unverified": target,
        "drag_scenarios": astra_rows,
        "verdict": "NOT_VALIDATED: even the highest assumed drag has only a small conditional target margin; actual drag, engine map and installed propeller efficiency are unknown",
    }

    fd = f["propulsion"]["drag_scenario_C"]
    fe = f["propulsion"]["engine"]
    fpower = required_engine_power(fd["D_total_N"], fd["V"], fd["eta_assumed"])
    claimed_fpower = fe["shaft_power_required_W"]
    result["cases"]["fable"] = {
        "speed_m_s": fd["V"],
        "assumed_drag_N": fd["D_total_N"],
        "assumed_efficiency": fd["eta_assumed"],
        "computed_useful_power_W": fd["D_total_N"] * fd["V"],
        "computed_shaft_power_W": round(fpower, 3),
        "reported_drag_scenario_shaft_W": fd["shaft_W"],
        "other_reported_shaft_requirement_W": claimed_fpower,
        "difference_between_computed_and_other_requirement_W": round(fpower - claimed_fpower, 3),
        "minimum_efficiency_if_10700_W_is_a_cap": round(
            fd["D_total_N"] * fd["V"] / claimed_fpower, 6),
        "available_engine_power": fe["power_available"],
        "verdict": "INTERNAL_REQUIREMENT_CONFLICT: 10.7 kW and approximately 11.08 kW do not describe the same drag/speed/efficiency case; engine availability remains unknown",
    }

    op = o["propulsion"]
    op_target = float(op["P_target_W"].split()[0])
    high = op["drag_cases_W"]["high"]
    eta = op["eta_required"]
    result["cases"]["opus"] = {
        "speed_m_s": 15,
        "unverified_engine_target_W": op_target,
        "assumed_overall_efficiency": eta,
        "shaft_demand_W_from_model_scenarios": op["drag_cases_W"],
        "high_drag_shortfall_to_target_W": round(high - op_target, 3),
        "minimum_efficiency_at_target_if_high_case_useful_power_fixed": round(
            high * eta / op_target, 6),
        "engine_curve": op["engine_curve"],
        "propeller_efficiency_map": op["prop_eff"],
        "verdict": "CONDITIONAL_HIGH_DRAG_TARGET_FAIL: high-drag assumed demand exceeds unverified 13 kW target; actual installed capability remains unknown",
    }
    result["gate"] = {
        "whole_aircraft_powered_trim": "NOT_ASSESSED",
        "power_off_trim": "NOT_ASSESSED",
        "installed_propulsion": "NOT_VALIDATED",
        "required_next_inputs": [
            "installed drag versus airspeed, incidence and control deflection, with uncertainty",
            "engine brake power and torque versus rpm",
            "propeller thrust, torque and efficiency versus airspeed, rpm and installation",
            "gearbox/shaft losses, thrust-axis moment and slipstream increments",
            "stall and full-aircraft lift/pitch-moment maps for trim",
        ],
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
