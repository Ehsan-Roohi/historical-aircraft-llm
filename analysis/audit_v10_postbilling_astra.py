"""Audit the completed, post-billing Astra V10 correction patch.

This verifies transport and selected arithmetic only. It does not validate
installed geometry, propulsion, trim, dynamics or flight.
"""

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "v10_astra_postbilling_attempt01"
RECEIVED = ROOT / "received_v10_astra_postbilling_65012338"
PRIOR = ROOT / "received_v10_astra_retry_65011846" / "outcome.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected, tolerance):
    return isinstance(actual, (int, float)) and abs(actual - expected) <= tolerance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads((ATTEMPT / "manifest.json").read_text(encoding="utf-8"))
    request = json.loads((RECEIVED / "request.json").read_text(encoding="utf-8"))
    outcome = json.loads((RECEIVED / "outcome.json").read_text(encoding="utf-8"))
    wrapper = json.loads((RECEIVED / "response.json").read_text(encoding="utf-8"))
    blocks = re.findall(r"```json\s*(.*?)```", wrapper["response"], re.DOTALL)
    if len(blocks) != 1:
        raise ValueError(f"expected one Astra JSON block, found {len(blocks)}")
    patch = json.loads(blocks[0])

    provenance = {
        "manifest_matches_request": sha(ATTEMPT / "manifest.json") == request["manifest_sha256"],
        "prompt_matches_manifest_and_request": sha(RECEIVED / "prompt.txt")
        == manifest["prompt_sha256"] == request["prompt_sha256"],
        "instructions_matches_manifest_and_request": sha(RECEIVED / "instructions.txt")
        == manifest["instructions_sha256"] == request["instructions_sha256"],
        "parent_matches_manifest_request_patch": sha(ATTEMPT / "parent.response.json")
        == manifest["parent_response_sha256"] == request["parent_response_sha256"]
        == patch["parent_sha256"],
        "prior_quota_outcome_matches": sha(PRIOR) == manifest["prior_outcome_sha256"]
        == request["prior_outcome_sha256"],
        "probe_receipt_matches": sha(ATTEMPT / "billing_probe.json")
        == manifest["billing_probe_sha256"] == request["billing_probe_sha256"],
        "response_matches_outcome": sha(RECEIVED / "response.json") == outcome["response_sha256"],
        "transport_completed": outcome["status"] == wrapper["status"] == "completed",
        "model_matches": request["model_requested"] == outcome["model_returned"]
        == wrapper["model_returned"] == "gpt-6-astra",
    }

    propulsion = patch["propulsion_requirement"]
    high = next(row for row in propulsion["cases"] if row["drag_N"] == 520)
    required = 520 * 18 / (0.55 * 0.95)
    radius = math.hypot(1.2, 0.04 * math.cos(0.35))
    clearance = patch["contact_and_clearance"]["rigid_checks"]
    states = {row["id"]: row for row in patch["mass_loading_states"]["states"]}
    expected_x = {
        "N": (-68.44616 + 75 * 0.2 + 1.6 * 2) / 333,
        "A": (-68.44616 + 60 * -0.1) / 310,
        "F": (-68.44616 + 90 * 0.4 + 1.6 * 2) / 348,
        "N_HALF_SYMMETRIC": (-68.44616 + 75 * 0.2 + 1.6) / 329,
        "N_ONE_TANK_FULL": (-68.44616 + 75 * 0.2 + 1.6) / 329,
    }
    arithmetic = {
        "high_drag_required_engine_W": required,
        "model_high_drag_requirement_matches": close(high["required_engine_power_W"], required, 0.001),
        "model_high_drag_margin_matches": close(18000 - required,
            patch["disputed_claims"][0]["target_minus_requirement_W"], 0.001),
        "target_supported_drag_matches": close(propulsion["target_supported_drag_N"],
            18000 * 0.55 * 0.95 / 18, 0.001),
        "rigid_prop_swept_radius_m": radius,
        "model_swept_radius_matches": close(
            patch["disputed_claims"][1]["maximum_swept_radius_m"], radius, 0.000001),
        "model_level_rigid_gap_matches": close(clearance["level_propeller_clearance_m"],
            1.6 - radius, 0.000001),
        "loading_xcg_matches": {name: close(states[name]["CG_m_approx"][0], value, 0.000002)
                                for name, value in expected_x.items()},
        "one_tank_lateral_cg_magnitude_matches": close(
            abs(float(states["N_ONE_TANK_FULL"]["CG_m_approx"][1].lstrip("±"))),
            2.4 / 329, 0.000002),
    }
    scope = {
        "physical_component_changes": patch["correction_patch"]["physical_component_changes"],
        "drawing_status": patch["correction_patch"]["drawing_status"],
        "powered_trim": patch["trim_input_status"]["powered_trim"],
        "glide_trim": patch["trim_input_status"]["glide_trim"],
        "installed_derivatives": patch["dynamics_input_status"]["installed_derivatives"],
        "flight_verdict": patch["flight_verdict"]["status"],
        "fin_elevator_surface_bound_independently_checked": False,
        "loaded_clearance_independently_checked": False,
        "installed_power_independently_checked": False,
    }
    result = {
        "stage": "v10_astra_postbilling_attempt01",
        "slurm_job_id": "65012338",
        "response_sha256": sha(RECEIVED / "response.json"),
        "outcome_sha256": sha(RECEIVED / "outcome.json"),
        "provenance": provenance,
        "all_provenance_pass": all(provenance.values()),
        "selected_arithmetic": arithmetic,
        "selected_arithmetic_pass": all(value for key, value in arithmetic.items()
                                        if key.endswith("_matches"))
        and all(arithmetic["loading_xcg_matches"].values()),
        "scope": scope,
        "independent_flight_validation": False,
    }
    serialized = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
