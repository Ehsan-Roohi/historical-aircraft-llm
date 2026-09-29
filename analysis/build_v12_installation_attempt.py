"""Freeze V12 installation-design prompts with full V3/V10/V11b context."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis" / "prompts_v12_installation"
ATTEMPT = ROOT / "v12_installation_attempt01"
STAGE = "v12_installation_candidate"
OUTPUT_TOKENS = 32000
ROWS = {
    "gpt-6-astra": (
        "received_v9_65007436/gpt-6-astra/response.json",
        "received_v10_astra_postbilling_65012338/response.json",
        "v11b_design_candidate_attempt01/responses/gpt-6-astra/response.json"),
    "claude-fable-5-1": (
        "received_v9_retry_65009709/claude-fable-5-1/response.json",
        "received_v10_65011353/claude-fable-5-1/response.json",
        "v11b_design_candidate_attempt01/responses/claude-fable-5-1/response.json"),
    "claude-opus-5-5": (
        "received_v9_retry_65009709/claude-opus-5-5/response.json",
        "received_v10_65011353/claude-opus-5-5/response.json",
        "v11b_design_candidate_attempt01/responses/claude-opus-5-5/response.json"),
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def write_json_new(path, data):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def main():
    ATTEMPT.mkdir(exist_ok=False)
    for name in ("prompts", "parents", "baselines"):
        (ATTEMPT / name).mkdir()
    instruction = (SOURCE / "instructions.txt").read_bytes()
    (ATTEMPT / "prompts" / "instructions.txt").write_bytes(instruction)
    template = (ROOT / "unity_jobs" / "run_v11_design_candidate.py").read_text(
        encoding="utf-8")
    original = 'STAGE = "v11b_design_candidate_context_restored"'
    assert template.count(original) == 1
    template = template.replace(original, f'STAGE = "{STAGE}"')
    assert template.count("MAX_OUTPUT_TOKENS = 24000") == 1
    template = template.replace("MAX_OUTPUT_TOKENS = 24000",
                                f"MAX_OUTPUT_TOKENS = {OUTPUT_TOKENS}")
    runner = template.encode("utf-8")
    (ATTEMPT / "run_v12_installation.py").write_bytes(runner)
    records = []
    index = {"stage": STAGE, "runner_template_sha256": sha(
        (ROOT / "unity_jobs" / "run_v11_design_candidate.py").read_bytes()),
        "records": []}
    for model, source_paths in ROWS.items():
        name = model + ".prompt.txt"
        base = (SOURCE / name).read_bytes()
        pieces = [base.decode("utf-8"),
                  "\n\nSOURCE CONTEXT: Below are exact prior model response texts, not independently validated aircraft facts. The latest V11b response is your immediate parent.\n"]
        sources = []
        wrappers = []
        for label, path in zip(("V3 baseline", "V10 correction", "V11b immediate parent"),
                               source_paths):
            blob = (ROOT / path).read_bytes()
            wrappers.append(blob)
            response = json.loads(blob)["response"]
            pieces.extend((f"\n--- BEGIN {label}; wrapper SHA-256 {sha(blob)} ---\n",
                           response, f"\n--- END {label} ---\n"))
            sources.append({"label": label, "path": path,
                            "wrapper_sha256": sha(blob),
                            "response_text_sha256": sha(response.encode("utf-8"))})
        prompt = "".join(pieces).encode("utf-8")
        (ATTEMPT / "prompts" / name).write_bytes(prompt)
        parent_name = model + ".response.json"
        (ATTEMPT / "parents" / parent_name).write_bytes(wrappers[2])
        (ATTEMPT / "baselines" / parent_name).write_bytes(wrappers[0])
        records.append({"model": model, "prompt_file": name,
                        "prompt_sha256": sha(prompt), "parent_file": parent_name,
                        "parent_sha256": sha(wrappers[2]),
                        "baseline_sha256": sha(wrappers[0]),
                        "v10_sha256": sha(wrappers[1]), "maximum_calls": 1})
        index["records"].append({"model": model, "base_prompt_sha256": sha(base),
                                 "sources": sources,
                                 "composed_prompt_sha256": sha(prompt),
                                 "composed_prompt_bytes": len(prompt)})
    write_json_new(ATTEMPT / "source_index.json", index)
    write_json_new(ATTEMPT / "manifest.json", {
        "stage": STAGE, "status": "FROZEN_UNSENT",
        "instructions_sha256": sha(instruction), "runner_sha256": sha(runner),
        "maximum_output_tokens": OUTPUT_TOKENS, "reasoning_effort": "low",
        "records": records})
    print(ATTEMPT.name)


if __name__ == "__main__":
    main()
