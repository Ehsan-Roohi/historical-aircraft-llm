"""Audit Fable's V13 ledger repair and distinguish paper power from output."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "v13_fable_arithmetic_attempt01"
MODEL = "claude-fable-5-1"


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def main():
    manifest_bytes = (ATTEMPT / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    row, = manifest["records"]
    prompt = (ATTEMPT / "prompts" / row["prompt_file"]).read_bytes()
    parent = (ATTEMPT / "parents" / row["parent_file"]).read_bytes()
    baseline = (ATTEMPT / "baselines" / row["parent_file"]).read_bytes()
    instruction = (ATTEMPT / "prompts" / "instructions.txt").read_bytes()
    case = ATTEMPT / "responses" / MODEL
    request = load(case / "request.json")
    outcome = load(case / "outcome.json")
    wrapper_bytes = (case / "response.json").read_bytes()
    wrapper = json.loads(wrapper_bytes)
    parent_text = json.loads(parent)["response"]
    checks = {
        "prompt_hash": sha(prompt) == row["prompt_sha256"],
        "parent_hash": sha(parent) == row["parent_sha256"],
        "baseline_hash": sha(baseline) == row["baseline_sha256"],
        "instructions_hash": sha(instruction) == manifest["instructions_sha256"],
        "parent_text_in_prompt": parent_text.encode("utf-8") in prompt,
        "request_prompt_hash": request["prompt_sha256"] == sha(prompt),
        "request_parent_hash": request["parent_response_sha256"] == sha(parent),
        "request_manifest_hash": request["manifest_sha256"] == sha(manifest_bytes),
        "response_hash": outcome.get("response_sha256") == sha(wrapper_bytes),
        "completed": outcome.get("status") == "completed" and wrapper.get("status") == "completed",
    }
    data = json.loads(wrapper["response"])
    old = json.loads(parent_text)
    old_rows = {r["ID"]: r for r in old["mass_ledger_rows"] if r["ID"] != "SUM"}
    rows = [r for r in data["full_mass_ledger_rows"] if r["ID"] != "SUM"]
    row_ids = {r["ID"] for r in rows}
    checks["same_component_ids"] = row_ids == set(old_rows)
    checks["unchanged_masses_centroids"] = all(
        float(r["mass_kg"]) == float(old_rows[r["ID"]]["mass_kg"])
        and list(map(float, r["centroid_xyz_m"])) ==
        list(map(float, old_rows[r["ID"]]["centroid_xyz_m"]))
        for r in rows)
    mass = sum(float(r["mass_kg"]) for r in rows)
    first = [sum(float(r["mass_kg"]) * float(r["centroid_xyz_m"][i])
                 for r in rows) for i in range(3)]
    cg = [v / mass for v in first]
    cases = []
    for state in data["revised_loading_cases"]["cases"]:
        title = state["case"]
        pilot_mass = float(title.split(" kg")[0])
        seat = float(title.split("seat ")[1].split()[0].rstrip(","))
        empty = "empty" in title
        active = []
        for item in rows:
            if empty and item["ID"] == "P07b":
                continue
            if item["ID"] == "P05":
                active.append((pilot_mass, [seat, 0, 0.75]))
            else:
                active.append((float(item["mass_kg"]),
                               list(map(float, item["centroid_xyz_m"]))))
        m = sum(item[0] for item in active)
        xyz = [sum(item[0] * item[1][i] for item in active) / m for i in range(3)]
        cases.append({"state": title, "mass_kg": round(m, 6),
                      "reported_mass_kg": state["mass_kg"],
                      "cg_xyz_m": [round(v, 6) for v in xyz],
                      "reported_cg_xyz_m": state["cg_xyz_m"],
                      "rounded_pass": abs(m - state["mass_kg"]) < 0.01 and
                      max(abs(xyz[i] - state["cg_xyz_m"][i])
                          for i in range(3)) < 0.001})
    p_e = 19500.0
    eta = 0.95
    req = float(data["corrected_power_chain"]["requirement_after_corrected_ledger_D"]["x1.15_W"])
    result = {
        "scope": "provenance, ledger arithmetic and assumed drive-chain necessity; no measured engine, flight or stability",
        "manifest_sha256": sha(manifest_bytes),
        "response_sha256": sha(wrapper_bytes),
        "source_checks": checks,
        "source_pass": all(checks.values()),
        "disposition": data["disposition"],
        "row_count_excluding_SUM": len(rows),
        "mass_kg": round(mass, 6),
        "first_moment_kg_m": [round(v, 6) for v in first],
        "cg_xyz_m": [round(v, 6) for v in cg],
        "loading_cases": cases,
        "all_loading_arithmetic_pass": all(c["rounded_pass"] for c in cases),
        "retained_target_engine_W": p_e,
        "assumed_drive_efficiency": eta,
        "prop_shaft_target_after_loss_W": p_e * eta,
        "high_case_15pct_requirement_W": req,
        "shortfall_W": req - p_e * eta,
        "minimum_engine_side_target_W": round(req / eta, 3),
        "measured_available_engine_power": "UNKNOWN",
        "measured_propeller_map": "UNKNOWN",
    }
    output = ROOT / "analysis" / "results" / "v13_fable_gate01.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(output.name)


if __name__ == "__main__":
    main()
