"""Verify V10 response provenance and independently test selected arithmetic.

Model-written correction patches are not accepted aircraft or measurements.
"""

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from audit_v3_geometry_loading import SOURCES, ledger_state, load_design, pitch_clearance


ROOT = Path(__file__).resolve().parents[1]
RECEIVED = ROOT / "received_v10_65011353"
PROMPTS = ROOT / "analysis/prompts_v10_geometry_power"
MODEL_IDS = ("gpt-6-astra", "claude-fable-5-1", "claude-opus-5-5")
ASTRA_RETRY = ROOT / "received_v10_astra_retry_65011846"
RETRY_MANIFEST = ROOT / "unity_jobs/v10_astra_retry_manifest.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_block(text):
    blocks = re.findall(r"```json\s*(.*?)```", text, re.DOTALL)
    if len(blocks) != 1:
        raise ValueError(f"expected one JSON block, found {len(blocks)}")
    return json.loads(blocks[0])


def check_loading(states, parent_items, specs, mass_key, centre_key, percent=False):
    checks = []
    for name, substitutions, removals in specs:
        predicted = ledger_state(parent_items, mass_key, centre_key,
                                 substitutions, removals)
        matching = [row for row in states if name in row.get("state", row.get("case", ""))]
        if len(matching) != 1:
            raise ValueError(f"expected one model row matching {name}")
        row = matching[0]
        actual_mass = row.get("mass_kg", row.get("m_kg"))
        actual_cg = row.get("cg_xyz_m", row.get("cg_m"))
        mass_diff = actual_mass - predicted["mass_kg"]
        x_diff = actual_cg[0] - predicted["cg_m"][0]
        record = {
            "state_selector": name,
            "independent_mass_kg": predicted["mass_kg"],
            "model_mass_kg": actual_mass,
            "independent_xcg_m": predicted["cg_m"][0],
            "model_xcg_m": actual_cg[0],
            "mass_difference_kg": round(mass_diff, 6),
            "xcg_difference_m": round(x_diff, 6),
            "arithmetic_matches_rounding": abs(mass_diff) <= 0.05 and abs(x_diff) <= 0.001,
        }
        if percent:
            independent_pct = 100 * (predicted["cg_m"][0] - 0.95) / 1.85
            record.update(independent_percent_chord=round(independent_pct, 3),
                          model_percent_chord=row["pct_chord"],
                          percent_chord_difference=round(row["pct_chord"] - independent_pct, 3))
            record["arithmetic_matches_rounding"] &= abs(row["pct_chord"] - independent_pct) <= 0.15
        checks.append(record)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads((PROMPTS / "manifest.json").read_text(encoding="utf-8"))
    parent_fable = load_design(SOURCES["fable"])
    parent_opus = load_design(SOURCES["opus"])
    output = {
        "stage": "v10_geometry_power_feedback",
        "array_job_id": "65011353",
        "scope": "provenance, response parse and selected ledger/power/clearance arithmetic; no flight or installed trim validation",
        "prompt_manifest_sha256": sha(PROMPTS / "manifest.json"),
        "cases": {},
    }
    for model_id in MODEL_IDS:
        case_dir = RECEIVED / model_id
        row = next(item for item in manifest["records"] if item["model_requested"] == model_id)
        request = json.loads((case_dir / "request.json").read_text(encoding="utf-8"))
        outcome = json.loads((case_dir / "outcome.json").read_text(encoding="utf-8"))
        checks = {
            "model": model_id,
            "request_sha256": sha(case_dir / "request.json"),
            "outcome_sha256": sha(case_dir / "outcome.json"),
            "prompt_hash_matches_manifest": (sha(case_dir / "prompt.txt") == row["prompt_sha256"]
                                             == request["prompt_sha256"]),
            "instructions_hash_matches_manifest": (
                sha(case_dir / "instructions.txt") == manifest["instructions_sha256"]
                == request["instructions_sha256"]),
            "parent_hash_matches_manifest": (row["parent_response_sha256"]
                                              == request["parent_response_sha256"]),
            "manifest_hash_matches_request": (
                sha(PROMPTS / "manifest.json") == request["manifest_sha256"]),
            "transport_status": outcome["status"],
            "error_type_if_any": outcome.get("error_type"),
        }
        if outcome["status"] != "completed":
            checks.update(response_present=(case_dir / "response.json").exists(),
                          diagnostic="RuntimeError recorded, but original runner retained no HTTP/error detail; no automatic retry or engineering result")
            output["cases"][model_id] = checks
            continue
        wrapper = json.loads((case_dir / "response.json").read_text(encoding="utf-8"))
        design = json_block(wrapper["response"])
        checks.update({
            "response_sha256": sha(case_dir / "response.json"),
            "response_hash_matches_outcome": sha(case_dir / "response.json") == outcome["response_sha256"],
            "model_id_matches": wrapper.get("model_returned") == model_id == outcome.get("model_returned"),
            "response_complete": wrapper.get("status") == "completed" and wrapper.get("stop_reason") == "end_turn",
            "parent_sha256_matches_patch": design.get("parent_sha256") == row["parent_response_sha256"],
            "required_patch_fields_present": all(key in design for key in (
                "correction_patch", "mass_loading_states", "contact_and_clearance",
                "propulsion_requirement", "unresolved", "flight_verdict")),
        })
        if model_id == "claude-fable-5-1":
            items = parent_fable["mass_ledger"]["items"]
            specs = [
                ("65kg aft 0.50 full", {"P05": (65, [0.5, 0, 0.75])}, ()),
                ("65kg aft 0.50 empty", {"P05": (65, [0.5, 0, 0.75])}, ("P07b",)),
                ("85kg fwd 0.20 full", {"P05": (85, [0.2, 0, 0.75])}, ()),
                ("85kg fwd 0.20 empty", {"P05": (85, [0.2, 0, 0.75])}, ("P07b",)),
            ]
            checks["loading_checks"] = check_loading(design["mass_loading_states"], items,
                                                       specs, "mass", "centroid", percent=True)
            power = design["propulsion_requirement"]
            checks["power"] = {
                "model_required_shaft_W": power["required_shaft_W_C"],
                "independent_assumed_shaft_W": 426 * 13 / 0.5,
                "arithmetic_match": abs(power["required_shaft_W_C"] - 426 * 13 / 0.5) < 1,
                "new_target_W_is_assumption": power["target_shaft_W_A"],
                "measured_available_W": power["measured_available_W"],
            }
        elif model_id == "claude-opus-5-5":
            items = parent_opus["mass_items"]
            specs = [
                ("70kg pilot, 0 fuel", {}, ("E3b",)),
                ("90kg pilot, 12kg fuel", {"O1": (90, [-0.9, 0, 0.3])}, ()),
                ("90kg pilot, 0 fuel", {"O1": (90, [-0.9, 0, 0.3])}, ("E3b",)),
            ]
            checks["loading_checks"] = check_loading(design["mass_loading_states"], items,
                                                       specs, "m", "c")
            angle = math.degrees(math.atan2(0.9, 3.9))
            gap = pitch_clearance(5.6, 0.25, 1.6, -0.9, -0.9, angle)
            power = design["propulsion_requirement"]
            checks["contact_and_power"] = {
                "independent_tail_skid_contact_deg": round(angle, 6),
                "independent_ventral_gap_at_contact_m": gap,
                "model_ventral_gap_m_in_text": 0.221110,
                "model_high_case_margin_W": power["margin_high_W"],
                "independent_high_case_margin_W": power["P_target_W"] - power["P_required_high_W"],
                "high_case_arithmetic_match": power["margin_high_W"]
                                              == power["P_target_W"] - power["P_required_high_W"],
            }
        checks["engineering_verdict"] = "MODEL_PATCH_NOT_INDEPENDENTLY_VALIDATED"
        output["cases"][model_id] = checks
    output["all_completed_responses_provenance_pass"] = all(
        case["prompt_hash_matches_manifest"] and case["instructions_hash_matches_manifest"]
        and case["parent_hash_matches_manifest"] and case["manifest_hash_matches_request"]
        and (case["response_hash_matches_outcome"] and case["model_id_matches"]
             and case["response_complete"] and case["parent_sha256_matches_patch"]
             and case["required_patch_fields_present"])
        for case in output["cases"].values() if case["transport_status"] == "completed"
    )
    retry_manifest = json.loads(RETRY_MANIFEST.read_text(encoding="utf-8"))
    retry_request = json.loads((ASTRA_RETRY / "request.json").read_text(encoding="utf-8"))
    retry_outcome = json.loads((ASTRA_RETRY / "outcome.json").read_text(encoding="utf-8"))
    output["astra_retry"] = {
        "job_id": "65011846",
        "retry_manifest_sha256": sha(RETRY_MANIFEST),
        "retry_manifest_hash_matches_request": sha(RETRY_MANIFEST) == retry_request["manifest_sha256"],
        "prompt_hash_matches_original_and_retry": (
            sha(ASTRA_RETRY / "prompt.txt") == retry_manifest["prompt_sha256"]
            == retry_request["prompt_sha256"]
            == manifest["records"][0]["prompt_sha256"]),
        "instructions_hash_matches": (
            sha(ASTRA_RETRY / "instructions.txt") == retry_manifest["instructions_sha256"]
            == retry_request["instructions_sha256"]),
        "prior_failed_outcome_hash_matches": (
            sha(RECEIVED / "gpt-6-astra/outcome.json")
            == retry_manifest["prior_outcome_sha256"]
            == retry_request["prior_outcome_sha256"]),
        "maximum_output_tokens": retry_request["maximum_output_tokens"],
        "transport_status": retry_outcome["status"],
        "error_type": retry_outcome.get("error_type"),
        "diagnostic_redacted": retry_outcome.get("diagnostic_redacted"),
        "response_present": (ASTRA_RETRY / "response.json").exists(),
        "outcome_sha256": sha(ASTRA_RETRY / "outcome.json"),
        "further_automatic_retry": False,
        "engineering_verdict": "NO_V10_ASTRA_DESIGN_RESPONSE",
    }
    serialized = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
