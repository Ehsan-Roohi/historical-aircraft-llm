"""Freeze one source-hashed Fable correction call after V12 audit failure."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis" / "prompts_v13_fable_arithmetic"
ATTEMPT = ROOT / "v13_fable_arithmetic_attempt01"
STAGE = "v13_fable_arithmetic_power_chain"
MODEL = "claude-fable-5-1"
LIMIT = 24000


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    ATTEMPT.mkdir(exist_ok=False)
    for name in ("prompts", "parents", "baselines"):
        (ATTEMPT / name).mkdir()
    parent = (ROOT / "v12_installation_attempt01/responses/claude-fable-5-1/response.json").read_bytes()
    previous = json.loads(parent)
    if previous.get("status") != "completed":
        raise ValueError("V12 Fable parent must be complete")
    baseline = (ROOT / "received_v9_retry_65009709/claude-fable-5-1/response.json").read_bytes()
    core = (SOURCE / (MODEL + ".prompt.txt")).read_bytes()
    prompt = (core.decode("utf-8") +
              f"\n--- BEGIN V12 PARENT; wrapper SHA-256 {sha(parent)} ---\n" +
              previous["response"] + "\n--- END V12 PARENT ---\n").encode("utf-8")
    instruction = (SOURCE / "instructions.txt").read_bytes()
    (ATTEMPT / "prompts" / (MODEL + ".prompt.txt")).write_bytes(prompt)
    (ATTEMPT / "prompts" / "instructions.txt").write_bytes(instruction)
    (ATTEMPT / "parents" / (MODEL + ".response.json")).write_bytes(parent)
    (ATTEMPT / "baselines" / (MODEL + ".response.json")).write_bytes(baseline)
    template_path = ROOT / "v12_installation_attempt01/run_v12_installation.py"
    template = template_path.read_text(encoding="utf-8")
    assert template.count('STAGE = "v12_installation_candidate"') == 1
    template = template.replace('STAGE = "v12_installation_candidate"',
                                f'STAGE = "{STAGE}"')
    assert template.count("MAX_OUTPUT_TOKENS = 32000") == 1
    template = template.replace("MAX_OUTPUT_TOKENS = 32000", f"MAX_OUTPUT_TOKENS = {LIMIT}")
    runner = template.encode("utf-8")
    (ATTEMPT / "run_v13_fable.py").write_bytes(runner)
    manifest = {
        "stage": STAGE, "status": "FROZEN_UNSENT",
        "reason": "independent 0.5kg ledger and 0.502kW drive-chain deficits",
        "instructions_sha256": sha(instruction), "runner_sha256": sha(runner),
        "parent_text_sha256": sha(previous["response"].encode("utf-8")),
        "maximum_output_tokens": LIMIT, "reasoning_effort": "low",
        "records": [{"model": MODEL, "prompt_file": MODEL + ".prompt.txt",
                     "prompt_sha256": sha(prompt),
                     "parent_file": MODEL + ".response.json",
                     "parent_sha256": sha(parent),
                     "baseline_sha256": sha(baseline), "maximum_calls": 1}],
    }
    with (ATTEMPT / "manifest.json").open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
    print(ATTEMPT.name)


if __name__ == "__main__":
    main()
