"""Reproducible provenance and limited arithmetic audit of the V9 model replies.

This is not an aerodynamic, structural, or dynamic-stability validation.
"""

import hashlib
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "astra": ROOT / "received_v9_65007436" / "gpt-6-astra",
    "fable": ROOT / "received_v9_retry_65009709" / "claude-fable-5-1",
    "opus": ROOT / "received_v9_retry_65009709" / "claude-opus-5-5",
}
MODEL_IDS = {
    "astra": "gpt-6-astra",
    "fable": "claude-fable-5-1",
    "opus": "claude-opus-5-5",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, claimed, tolerance):
    return abs(actual - claimed) <= tolerance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="Write the deterministic machine-readable audit to this path")
    args = parser.parse_args()
    output = {"stage": "v9_integrated_dynamics", "audit_scope": [
        "provenance hashes", "response completion", "mass and CG arithmetic",
        "Fable's reported nominal force and pitch-moment arithmetic",
    ], "excluded_from_audit": [
        "aerodynamic coefficients", "installed propulsion", "structural strength",
        "complete six-degree-of-freedom trim", "measured derivatives", "dynamic modal stability",
        "flightworthiness",
    ], "cases": {}}
    for case_name, case_dir in CASES.items():
        outcome = json.loads((case_dir / "outcome.json").read_text(encoding="utf-8"))
        request = json.loads((case_dir / "request.json").read_text(encoding="utf-8"))
        wrapper = json.loads((case_dir / "response.json").read_text(encoding="utf-8"))
        text = wrapper.get("response", "")
        blocks = re.findall(r"```json\s*(.*?)```", text, flags=re.DOTALL)
        if len(blocks) != 1:
            raise ValueError(f"{case_name}: expected exactly one structured JSON block")
        design = json.loads(blocks[0])
        response_hash_ok = sha(case_dir / "response.json") == outcome["response_sha256"]
        prompt_hash_ok = sha(case_dir / "prompt.txt") == request["prompt_sha256"]
        instructions_hash_ok = sha(case_dir / "instructions.txt") == request["instructions_sha256"]
        complete = (outcome["status"] == "completed"
                    and wrapper["status"] == "completed" and bool(text))
        if case_name != "astra":
            complete = complete and wrapper["stop_reason"] == "end_turn"
        model_match = wrapper["model_returned"] == MODEL_IDS[case_name]
        if case_name == "astra":
            items = design["mass_model"]["items"]
            mass_key, centroid_key = "mass_kg", "centroid_m"
            reported = design["mass_model"]["nominal"]
            reported_mass = reported["mass_kg"]
            reported_moments = reported["first_moment_kg_m_approx"]
            reported_cg = reported["CG_m_approx"]
            trim_status = design["drag_and_trim"]["actual_trim_solutions"]
            modal_status = {"longitudinal": design["modal_analysis"]["longitudinal_roots"],
                            "lateral": design["modal_analysis"]["lateral_roots"]}
        elif case_name == "fable":
            items = design["mass_ledger"]["items"]
            mass_key, centroid_key = "mass", "centroid"
            reported = design["mass_ledger"]["summary"]
            reported_mass = reported["total_mass_kg"]
            reported_moments = [reported["sum_mx"], reported["sum_my"], reported["sum_mz"]]
            reported_cg = reported["cg_xyz"]
            trim_status = "conditional estimator, not validated trim"
            modal_status = design["roots_calculation_path"]["gate_statement"]
        else:
            items = design["mass_items"]
            mass_key, centroid_key = "m", "c"
            reported = design["mass_summary"]
            reported_mass = reported["total_kg"]
            reported_moments = [reported["sum_x"], 0, reported["sum_z"]]
            reported_cg = reported["cg"]
            trim_status = design["trim"]["status"]
            modal_status = design["modes"]["verdict"]
        masses = [float(item[mass_key]) for item in items]
        centroids = [item[centroid_key] for item in items]
        if any(m <= 0 or len(c) != 3 for m, c in zip(masses, centroids)):
            raise ValueError(f"{case_name}: invalid mass or centroid row")
        total_mass = sum(masses)
        moments = [sum(m * float(c[axis]) for m, c in zip(masses, centroids))
                   for axis in range(3)]
        cg = [moment / total_mass for moment in moments]
        mass_arithmetic_pass = (close(total_mass, float(reported_mass), 0.05)
                                and all(close(x, float(y), 0.05)
                                        for x, y in zip(moments, reported_moments))
                                and all(close(x, float(y), 0.001)
                                        for x, y in zip(cg, reported_cg)))
        row = {
            "model": MODEL_IDS[case_name],
            "response_sha256": sha(case_dir / "response.json"),
            "response_hash_matches_outcome": response_hash_ok,
            "prompt_hash_matches_request": prompt_hash_ok,
            "instructions_hash_matches_request": instructions_hash_ok,
            "model_id_matches_request": model_match,
            "response_complete": complete,
            "stop_reason": wrapper.get("stop_reason"),
            "ledger_rows": len(items),
            "calculated_mass_kg": round(total_mass, 6),
            "calculated_first_moments_kg_m": [round(x, 6) for x in moments],
            "calculated_cg_m": [round(x, 6) for x in cg],
            "reported_mass_kg": reported_mass,
            "reported_cg_m": reported_cg,
            "mass_arithmetic_pass": mass_arithmetic_pass,
            "trim_evidence": trim_status,
            "modal_evidence": modal_status,
            "engineering_verdict": "NOT_VALIDATED",
        }
        if case_name == "fable":
            trim = design["trim_estimate_C"]
            wing = float(trim["wing_lift_N"])
            tail = float(trim["tail_lift_N"])
            weight = float(trim["weight_N"])
            pitch_terms = [float(value) for value in trim["moments_Nm_about_CG"].values()]
            row["conditional_trim_arithmetic"] = {
                "vertical_force_residual_N": round(wing + tail - weight, 6),
                "weight_vs_ledger_residual_N": round(weight - total_mass * 9.81, 6),
                "pitch_moment_residual_Nm": round(sum(pitch_terms), 6),
                "reported_aft_static_margin_estimate": trim["static_margin_estimate"]["aft_cg"],
                "arithmetic_pass": (abs(wing + tail - weight) < 1
                                    and abs(weight - total_mass * 9.81) < 1
                                    and abs(sum(pitch_terms)) < 1),
                "caveat": "Algebra of assumed loads only; forces, thrust, and derivatives are not measured or independently predicted.",
            }
        output["cases"][case_name] = row
    output["all_provenance_and_ledger_checks_pass"] = all(
        row["response_hash_matches_outcome"]
        and row["prompt_hash_matches_request"]
        and row["instructions_hash_matches_request"]
        and row["model_id_matches_request"]
        and row["response_complete"]
        and row["mass_arithmetic_pass"]
        for row in output["cases"].values())
    serialized = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
