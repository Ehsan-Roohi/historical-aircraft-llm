"""Provenance and selected independent V12 mass/power arithmetic gate.

Physical geometry, aerodynamics, structure and flight are not validated here.
The first Opus response may be incomplete and remains separate from any retry.
"""

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "v12_installation_attempt01"
MODELS = ("gpt-6-astra", "claude-fable-5-1", "claude-opus-5-5")


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def source_path(relative):
    resolved = (ROOT / relative).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError("source path outside project")
    return resolved


def provenance():
    manifest_bytes = (ATTEMPT / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    index = load(ATTEMPT / "source_index.json")
    result = {}
    for row in manifest["records"]:
        model = row["model"]
        assert model in MODELS
        prompt = (ATTEMPT / "prompts" / row["prompt_file"]).read_bytes()
        parent = (ATTEMPT / "parents" / row["parent_file"]).read_bytes()
        baseline = (ATTEMPT / "baselines" / row["parent_file"]).read_bytes()
        instruction = (ATTEMPT / "prompts" / "instructions.txt").read_bytes()
        source_row, = [r for r in index["records"] if r["model"] == model]
        checks = {
            "prompt_hash": sha(prompt) == row["prompt_sha256"],
            "parent_hash": sha(parent) == row["parent_sha256"],
            "baseline_hash": sha(baseline) == row["baseline_sha256"],
            "instruction_hash": sha(instruction) == manifest["instructions_sha256"],
            "source_index_prompt_hash": sha(prompt) == source_row["composed_prompt_sha256"],
        }
        for source in source_row["sources"]:
            blob = source_path(source["path"]).read_bytes()
            content = json.loads(blob)["response"].encode("utf-8")
            label = source["label"].replace(" ", "_").lower()
            checks[label + "_wrapper_hash"] = sha(blob) == source["wrapper_sha256"]
            checks[label + "_text_hash"] = sha(content) == source["response_text_sha256"]
            checks[label + "_text_in_prompt"] = content in prompt
        case = ATTEMPT / "responses" / model
        if case.exists():
            request = load(case / "request.json")
            outcome = load(case / "outcome.json")
            checks["request_prompt_hash"] = request["prompt_sha256"] == sha(prompt)
            checks["request_parent_hash"] = request["parent_response_sha256"] == sha(parent)
            checks["request_manifest_hash"] = request["manifest_sha256"] == sha(manifest_bytes)
            response_blob = (case / "response.json").read_bytes()
            checks["outcome_response_hash"] = outcome.get("response_sha256") == sha(response_blob)
            wrapper = json.loads(response_blob)
            summary = {"source_checks": checks, "source_pass": all(checks.values()),
                       "outcome": outcome["status"], "stop_reason": outcome.get("stop_reason"),
                       "response_sha256": sha(response_blob),
                       "model_returned": wrapper.get("model_returned"),
                       "wrapper_status": wrapper.get("status")}
            if outcome["status"] == "completed":
                try:
                    payload = json.loads(wrapper["response"])
                    summary["json_complete"] = True
                    summary["disposition"] = payload.get("disposition")
                    summary["ledger_row_count"] = len(payload.get("mass_ledger_rows", []))
                except (ValueError, KeyError, TypeError):
                    summary["json_complete"] = False
            else:
                summary["json_complete"] = False
            result[model] = summary
        else:
            result[model] = {"source_checks": checks,
                             "source_pass": all(checks.values()),
                             "outcome": "NOT_RETURNED"}
    return {"manifest_sha256": sha(manifest_bytes), "models": result}


def fable_screen():
    response = load(ATTEMPT / "responses" / "claude-fable-5-1" / "response.json")
    data = json.loads(response["response"])
    rows = [r for r in data["mass_ledger_rows"] if r["ID"] != "SUM"]
    masses = [float(r["mass_kg"]) for r in rows]
    centres = [list(map(float, r["centroid_xyz_m"])) for r in rows]
    mass = sum(masses)
    first = [sum(m * c[i] for m, c in zip(masses, centres)) for i in range(3)]
    cg = [v / mass for v in first]
    loading = []
    for case in data["loading_cases"]["cases"]:
        title = case["case"]
        pilot_mass = float(title.split(" kg")[0])
        seat = float(title.split("seat ")[1].split()[0].rstrip(","))
        empty = "empty" in title
        active = []
        for row in rows:
            if empty and row["ID"] == "P07b":
                continue
            if row["ID"] == "P05":
                active.append((pilot_mass, [seat, 0.0, 0.75]))
            else:
                active.append((float(row["mass_kg"]),
                               list(map(float, row["centroid_xyz_m"]))))
        m = sum(item[0] for item in active)
        xyz = [sum(item[0] * item[1][i] for item in active) / m
               for i in range(3)]
        loading.append({"case": title, "mass_recomputed_kg": round(m, 5),
                        "reported_mass_kg": case["mass_kg"],
                        "cg_recomputed_m": [round(v, 6) for v in xyz],
                        "reported_cg_m": case["cg_xyz_m"],
                        "rounding_pass": abs(m - case["mass_kg"]) < 0.01 and
                        max(abs(xyz[i] - case["cg_xyz_m"][i])
                            for i in range(3)) < 0.001})
    target = float(data["propulsor_and_engine_target"]["engine_target_A"][
        "shaft_power_W_continuous_measured_at_1200rpm"])
    assumed_drive_efficiency = 0.95
    high_required_prop_shaft = float(data["power_cases"]["cases_D"][3]["P_x1.15_W"])
    delivered = target * assumed_drive_efficiency
    minimum_engine = high_required_prop_shaft / assumed_drive_efficiency
    power_cases = []
    for case in data["power_cases"]["cases_D"]:
        label = case["case"]
        speed = 12 if "V12" in label else 16 if "V16" in label else 13
        efficiency = 0.45 if "worst" in label else 0.55 if "optimistic" in label else 0.5
        computed = case["D_N"] * speed / efficiency
        power_cases.append({"case": label, "reported_W": case["P_req_W"],
                            "from_rounded_drag_W": round(computed, 3),
                            "difference_W": round(case["P_req_W"] - computed, 3)})
    return {
        "ledger_row_count_excluding_SUM": len(rows),
        "mass_kg": round(mass, 6),
        "first_moment_kg_m": [round(v, 6) for v in first],
        "cg_xyz_m": [round(v, 6) for v in cg],
        "loading_cases": loading,
        "all_loading_arithmetic_pass": all(c["rounding_pass"] for c in loading),
        "power_cases": power_cases,
        "drive_chain": {
            "target_at_engine_side_W": target,
            "assumed_drive_efficiency": assumed_drive_efficiency,
            "delivered_prop_shafts_W": delivered,
            "high_case_with_15pct_reserve_W": high_required_prop_shaft,
            "shortfall_W": round(high_required_prop_shaft - delivered, 3),
            "minimum_engine_side_W_at_assumed_efficiency": round(minimum_engine, 3),
            "paper_target_meets_reserve_after_drive": delivered >= high_required_prop_shaft,
            "measured_engine_and_propeller_maps": "NONE"},
        "not_validated": ["occupied-solid clearance under load", "engine output",
                          "propeller Cp/Ct matching", "whole-aircraft trim",
                          "neutral point and dynamic modes", "strength"],
    }


def opus_screen():
    attempt = ROOT / "v12_opus_retry_attempt01"
    manifest_bytes = (attempt / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    row, = manifest["records"]
    case = attempt / "responses" / "claude-opus-5-5"
    outcome = load(case / "outcome.json")
    wrapper_bytes = (case / "response.json").read_bytes()
    wrapper = json.loads(wrapper_bytes)
    prompt = (attempt / "prompts" / row["prompt_file"]).read_bytes()
    parent = (attempt / "parents" / row["parent_file"]).read_bytes()
    prior = load(attempt / "prior.outcome.json")
    prior_bytes = (attempt / "prior.response.json").read_bytes()
    checks = {
        "retry_manifest_stage": manifest["stage"] == "v12_opus_reviewed_completion_attempt01",
        "retry_prompt_hash": sha(prompt) == row["prompt_sha256"],
        "retry_parent_hash": sha(parent) == row["parent_sha256"],
        "retry_baseline_hash": sha((attempt / "baselines" / row["parent_file"]).read_bytes()) == row["baseline_sha256"],
        "prior_response_hash": sha(prior_bytes) == manifest["prior_response_sha256"],
        "prior_outcome_hash": sha((attempt / "prior.outcome.json").read_bytes()) == manifest["prior_outcome_sha256"],
        "prior_max_tokens": prior["status"] == "incomplete" and prior["stop_reason"] == "max_tokens",
        "retry_response_hash": outcome.get("response_sha256") == sha(wrapper_bytes),
        "completed": outcome.get("status") == "completed" and wrapper.get("status") == "completed",
    }
    if not all(checks.values()):
        return {"source_checks": checks, "source_pass": False}
    data = json.loads(wrapper["response"])
    rows = [r for r in data["mass_ledger_rows"] if r["id"] != "LEDGER_AUDIT"]
    mass = sum(float(r["mass_kg"]) for r in rows)
    first = [sum(float(r["mass_kg"]) * float(r["centroid_xyz_m"][i])
                 for r in rows) for i in range(3)]
    cg = [v / mass for v in first]
    cases = []
    for case_row in data["loading_cases"]:
        if "mass_kg" not in case_row:
            continue
        title = case_row["case"]
        heavy = "90 kg" in title
        empty = "0 fuel" in title
        active = []
        for item in rows:
            if empty and item["id"] == "E3b":
                continue
            this_mass = 90.0 if heavy and item["id"] == "O1" else float(item["mass_kg"])
            active.append((this_mass, list(map(float, item["centroid_xyz_m"]))))
        m = sum(item[0] for item in active)
        xyz = [sum(item[0] * item[1][i] for item in active) / m for i in range(3)]
        cases.append({"case": title, "mass_recomputed_kg": round(m, 6),
                      "reported_mass_kg": case_row["mass_kg"],
                      "cg_recomputed_m": [round(v, 6) for v in xyz],
                      "reported_cg_m": case_row["cg_xyz_m"],
                      "rounding_pass": abs(m - case_row["mass_kg"]) < 0.01 and
                      max(abs(xyz[i] - case_row["cg_xyz_m"][i])
                          for i in range(3)) < 0.001})
    engine = data["propulsor_and_engine_target"]["engine"]
    drive = data["propulsor_and_engine_target"]["drive"]
    high = 13700 * 1.15
    theta = math.atan2(0.9, 3.9)
    s, c = math.sin(theta), math.cos(theta)
    return {
        "source_checks": checks, "source_pass": True,
        "response_sha256": sha(wrapper_bytes),
        "disposition": data["disposition"],
        "row_count_excluding_audit": len(rows),
        "mass_kg": round(mass, 6),
        "first_moment_kg_m": [round(v, 6) for v in first],
        "cg_xyz_m": [round(v, 6) for v in cg],
        "loading_cases": cases,
        "all_loading_arithmetic_pass": all(c["rounding_pass"] for c in cases),
        "power_chain": {
            "assumed_engine_target_W": engine["power_target_W"],
            "assumed_drive_efficiency": drive["eta_assumed"],
            "assumed_prop_shaft_target_W": engine["power_target_W"] * drive["eta_assumed"],
            "high_case_15pct_requirement_W": high,
            "paper_target_margin_W": round(engine["power_target_W"] * drive["eta_assumed"] - high, 3),
            "measured_available_power": "UNKNOWN"},
        "selected_rigid_ground_arithmetic": {
            "tail_skid_stop_deg": round(math.degrees(theta), 6),
            "ventral_T5_gap_m": round(-4.0 * s + 1.15 * c, 6),
            "prop_aft_bottom_gap_m": round(-0.55 * s + 0.6 * c, 6),
            "wheel_bottom_gap_m": round(1.15 * s + 0.03 * c, 6),
            "loaded_gap": "UNKNOWN",
            "nose_down_contact": "NOT EVALUATED IN MODEL RESPONSE"},
        "not_validated": ["occupied-solid CAD and loaded clearances", "engine/propeller maps",
                          "whole-aircraft aerodynamics and trim", "neutral point and modes",
                          "structure and cooling"],
    }


def main():
    result = {"scope": "V12 provenance and selected arithmetic; no flight validation",
              "provenance": provenance()}
    if result["provenance"]["models"]["claude-fable-5-1"]["outcome"] == "completed":
        result["fable_screen"] = fable_screen()
    if (ROOT / "v12_opus_retry_attempt01" / "responses" /
            "claude-opus-5-5" / "response.json").exists():
        result["opus_retry_screen"] = opus_screen()
    output = ROOT / "analysis" / "results" / "v12_installation_gate01.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(output.name)


if __name__ == "__main__":
    main()
