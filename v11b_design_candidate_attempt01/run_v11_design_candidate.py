"""Freeze and run one bounded V11 model feedback request per design.

The local prepare action only creates new provenance files. The remote run action
checks every frozen input before it contacts a model API; there is no retry.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path


STAGE = "v11b_design_candidate_context_restored"
MODELS = ("gpt-6-astra", "claude-fable-5-1", "claude-opus-5-5")
PARENT_PATHS = {
    MODELS[0]: "received_v10_astra_postbilling_65012338/response.json",
    MODELS[1]: "received_v10_65011353/claude-fable-5-1/response.json",
    MODELS[2]: "received_v10_65011353/claude-opus-5-5/response.json",
}
MAX_OUTPUT_TOKENS = 24000
BASELINE_PATHS = {
    MODELS[0]: "received_v9_65007436/gpt-6-astra/response.json",
    MODELS[1]: "received_v9_retry_65009709/claude-fable-5-1/response.json",
    MODELS[2]: "received_v9_retry_65009709/claude-opus-5-5/response.json",
}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def write_json_new(path, data):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def prepare(root, attempt, prompt_directory):
    attempt.mkdir(exist_ok=False)
    (attempt / "prompts").mkdir()
    (attempt / "parents").mkdir()
    (attempt / "baselines").mkdir()
    prompts = prompt_directory
    instructions = (prompts / "instructions.txt").read_bytes()
    (attempt / "prompts" / "instructions.txt").write_bytes(instructions)
    records = []
    for model in MODELS:
        prompt_name = model + ".prompt.txt"
        prompt = (prompts / prompt_name).read_bytes()
        parent = (root / PARENT_PATHS[model]).read_bytes()
        baseline = (root / BASELINE_PATHS[model]).read_bytes()
        parent_name = model + ".response.json"
        (attempt / "prompts" / prompt_name).write_bytes(prompt)
        (attempt / "parents" / parent_name).write_bytes(parent)
        (attempt / "baselines" / parent_name).write_bytes(baseline)
        records.append({"model": model, "prompt_file": prompt_name,
                        "prompt_sha256": digest(prompt), "parent_file": parent_name,
                        "parent_sha256": digest(parent),
                        "baseline_sha256": digest(baseline), "maximum_calls": 1})
    script = Path(__file__).read_bytes()
    (attempt / "run_v11_design_candidate.py").write_bytes(script)
    write_json_new(attempt / "manifest.json", {
        "stage": STAGE, "status": "FROZEN_UNSENT",
        "instructions_sha256": digest(instructions),
        "runner_sha256": digest(script),
        "maximum_output_tokens": MAX_OUTPUT_TOKENS,
        "reasoning_effort": "low", "records": records,
    })
    print(str(attempt / "manifest.json").encode("ascii", "backslashreplace").decode())


def diagnostic(error):
    message = str(error)
    message = re.sub(r"(?i)sk-[A-Za-z0-9_-]{12,}", "[REDACTED_KEY]", message)
    message = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._-]+", r"\1[REDACTED]", message)
    return message[:800]


def run_one(attempt, transport_dir, model):
    manifest_bytes = (attempt / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest["stage"] != STAGE or manifest["status"] != "FROZEN_UNSENT"
            or manifest["maximum_output_tokens"] != MAX_OUTPUT_TOKENS
            or manifest["runner_sha256"] != digest(Path(__file__).read_bytes())):
        raise ValueError("frozen manifest mismatch")
    row, = [record for record in manifest["records"] if record["model"] == model]
    prompt = (attempt / "prompts" / row["prompt_file"]).read_bytes()
    parent = (attempt / "parents" / row["parent_file"]).read_bytes()
    baseline = (attempt / "baselines" / row["parent_file"]).read_bytes()
    instructions = (attempt / "prompts" / "instructions.txt").read_bytes()
    if (digest(prompt) != row["prompt_sha256"] or digest(parent) != row["parent_sha256"]
            or digest(baseline) != row["baseline_sha256"]
            or digest(instructions) != manifest["instructions_sha256"]):
        raise ValueError("frozen source hash mismatch")
    if not hasattr(signal, "SIGALRM"):
        raise RuntimeError("Linux timeout required")
    key_name = "OPENAI_API_KEY" if model == MODELS[0] else "ANTHROPIC_API_KEY"
    key = os.environ.get(key_name)
    if not key:
        raise RuntimeError("required API credential absent")
    transport = transport_dir / "frontier_wright_eval.py"
    metadata = {
        "stage": STAGE, "model_requested": model,
        "prompt_sha256": digest(prompt), "parent_response_sha256": digest(parent),
        "baseline_response_sha256": digest(baseline),
        "instructions_sha256": digest(instructions),
        "manifest_sha256": digest(manifest_bytes),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "transport_sha256": digest(transport.read_bytes()),
        "maximum_output_tokens": MAX_OUTPUT_TOKENS,
        "reasoning_effort": "low", "maximum_calls": 1,
        "automatic_retry": False, "timeout_seconds": 5400,
        "engineering_validation": "not_evaluated",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    }
    case = attempt / "responses" / model
    case.mkdir(parents=True, exist_ok=False)
    write_json_new(case / "request.json", metadata)
    (case / "prompt.txt").write_bytes(prompt)
    (case / "instructions.txt").write_bytes(instructions)
    sys.path.insert(0, str(transport_dir))
    from frontier_wright_eval import generate

    def expire(_signal, _frame):
        raise TimeoutError("bounded model call expired")

    signal.signal(signal.SIGALRM, expire)
    signal.alarm(5400)
    try:
        response = generate(model, prompt.decode("utf-8"), MAX_OUTPUT_TOKENS,
                            key, reasoning_effort="low",
                            instructions=instructions.decode("utf-8"))
        write_json_new(case / "response.json", response)
        complete = response.get("status") == "completed" and bool(response.get("response"))
        outcome = {
            "status": "completed" if complete else "incomplete",
            "stop_reason": response.get("stop_reason"),
            "model_returned": response.get("model_returned"),
            "response_sha256": digest((case / "response.json").read_bytes()),
        }
    except Exception as error:
        complete = False
        outcome = {"status": "error_or_uncertain",
                   "error_type": type(error).__name__,
                   "diagnostic_redacted": diagnostic(error)}
    finally:
        signal.alarm(0)
    outcome.update(finished_utc=datetime.now(timezone.utc).isoformat(),
                   automatic_retry=False, engineering_validation="not_evaluated")
    write_json_new(case / "outcome.json", outcome)
    print(model, outcome["status"], flush=True)
    return 0 if complete else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-root", type=Path)
    parser.add_argument("--prompt-directory", type=Path)
    parser.add_argument("--attempt-dir", type=Path, required=True)
    parser.add_argument("--transport-dir", type=Path)
    parser.add_argument("--model", choices=MODELS)
    args = parser.parse_args()
    if args.prepare_root:
        if not args.prompt_directory:
            parser.error("--prompt-directory is required for prepare")
        prepare(args.prepare_root.resolve(), args.attempt_dir.resolve(),
                args.prompt_directory.resolve())
        return 0
    if not args.model or not args.transport_dir:
        parser.error("--model and --transport-dir are required for a run")
    return run_one(args.attempt_dir.resolve(), args.transport_dir.resolve(), args.model)


if __name__ == "__main__":
    raise SystemExit(main())
