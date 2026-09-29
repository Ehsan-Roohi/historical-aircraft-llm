"""Audit V11/V11b provenance and summarize machine-readable design claims.

This does not validate aerodynamic, structural or flight performance.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODELS = ("gpt-6-astra", "claude-fable-5-1", "claude-opus-5-5")
ATTEMPTS = ("v11_design_candidate_attempt01",
            "v11b_design_candidate_attempt01")


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def parse_response(text):
    stripped = text.strip()
    if stripped.startswith("```json"):
        stripped = stripped[7:]
    if stripped.startswith("```"):
        stripped = stripped[3:]
    if stripped.endswith("```"):
        stripped = stripped[:-3]
    return json.loads(stripped.strip())


def main():
    results = {}
    for attempt_name in ATTEMPTS:
        folder = ROOT / attempt_name
        manifest_bytes = (folder / "manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        cases = {}
        for row in manifest["records"]:
            model = row["model"]
            assert model in MODELS
            prompt = (folder / "prompts" / row["prompt_file"]).read_bytes()
            parent = (folder / "parents" / row["parent_file"]).read_bytes()
            instruction = (folder / "prompts" / "instructions.txt").read_bytes()
            checks = {
                "prompt_hash": sha(prompt) == row["prompt_sha256"],
                "parent_hash": sha(parent) == row["parent_sha256"],
                "instructions_hash": sha(instruction) == manifest["instructions_sha256"],
            }
            if "baseline_sha256" in row:
                baseline = (folder / "baselines" / row["parent_file"]).read_bytes()
                checks["baseline_hash"] = sha(baseline) == row["baseline_sha256"]
                checks["baseline_text_in_prompt"] = (
                    json.loads(baseline)["response"].encode("utf-8") in prompt)
                checks["parent_text_in_prompt"] = (
                    json.loads(parent)["response"].encode("utf-8") in prompt)
            case = folder / "responses" / model
            request = json.loads((case / "request.json").read_text(encoding="utf-8"))
            outcome = json.loads((case / "outcome.json").read_text(encoding="utf-8"))
            checks.update({
                "request_prompt_hash": request["prompt_sha256"] == sha(prompt),
                "request_parent_hash": request["parent_response_sha256"] == sha(parent),
                "request_manifest_hash": request["manifest_sha256"] == sha(manifest_bytes),
                "case_prompt_hash": sha((case / "prompt.txt").read_bytes()) == sha(prompt),
                "case_instruction_hash": sha((case / "instructions.txt").read_bytes()) == sha(instruction),
            })
            if "baseline_sha256" in row:
                checks["request_baseline_hash"] = (
                    request["baseline_response_sha256"] == row["baseline_sha256"])
            summary = {"provenance_checks": checks,
                       "provenance_pass": all(checks.values()),
                       "outcome_status": outcome["status"]}
            if (case / "response.json").exists():
                response_bytes = (case / "response.json").read_bytes()
                wrapper = json.loads(response_bytes)
                summary["response_sha256"] = sha(response_bytes)
                summary["wrapper_status"] = wrapper.get("status")
                summary["model_returned"] = wrapper.get("model_returned")
                summary["response_hash_pass"] = (
                    outcome.get("response_sha256") == sha(response_bytes))
                try:
                    payload = parse_response(wrapper["response"])
                    summary["json_parse_pass"] = True
                    summary["disposition"] = payload.get("disposition")
                    summary["revision_id"] = payload.get("revision_id")
                    changed = payload.get("changed_components")
                    summary["changed_component_count"] = (
                        len(changed) if isinstance(changed, list) else None)
                    summary["top_level_keys"] = list(payload)
                except (ValueError, TypeError, KeyError) as error:
                    summary["json_parse_pass"] = False
                    summary["json_error"] = type(error).__name__
            cases[model] = summary
        results[attempt_name] = {"manifest_sha256": sha(manifest_bytes),
                                 "cases": cases}
    output = ROOT / "analysis" / "results" / "v11_feedback_audit01.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(str(output).encode("ascii", "backslashreplace").decode())


if __name__ == "__main__":
    main()
