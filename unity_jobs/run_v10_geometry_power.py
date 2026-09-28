"""Single bounded, provenance-checked V10 correction call per model."""

import argparse
import hashlib
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path


MODELS = ("gpt-6-astra", "claude-fable-5-1", "claude-opus-5-5")
STAGE = "v10_geometry_power_feedback"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--attempt-dir", type=Path, required=True)
    parser.add_argument("--transport-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    directory = args.attempt_dir.resolve()
    prompt_dir = directory / "prompts"
    manifest_bytes = (prompt_dir / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest["stage"] != STAGE or manifest["status"] != "FROZEN_UNSENT"
            or manifest["maximum_output_tokens"] != 32000):
        raise ValueError("unexpected frozen request manifest")
    rows = [row for row in manifest["records"] if row["model_requested"] == args.model]
    if len(rows) != 1 or rows[0]["sent"] is not False:
        raise ValueError("expected one frozen unsent request")
    row = rows[0]
    prompt = (prompt_dir / row["prompt_file"]).read_bytes()
    instructions = (prompt_dir / "instructions.txt").read_bytes()
    parent = (directory / "parents" / (args.model + ".response.json")).read_bytes()
    if (sha(prompt) != row["prompt_sha256"]
            or sha(instructions) != manifest["instructions_sha256"]
            or sha(parent) != row["parent_response_sha256"]):
        raise ValueError("prompt, instruction or parent SHA-256 mismatch")
    audit_dir = directory / "audits"
    if (sha((audit_dir / "v3_geometry_loading_gate01.json").read_bytes())
            != manifest["evaluator_geometry_audit_sha256"]
            or sha((audit_dir / "v3_power_necessity_gate01.json").read_bytes())
            != manifest["evaluator_power_audit_sha256"]):
        raise ValueError("evaluator audit SHA-256 mismatch")
    metadata = {
        "stage": STAGE,
        "model_requested": args.model,
        "parent_response_sha256": sha(parent),
        "prompt_sha256": sha(prompt),
        "instructions_sha256": sha(instructions),
        "manifest_sha256": sha(manifest_bytes),
        "maximum_output_tokens": 32000,
        "reasoning_effort": "low",
        "maximum_calls": 1,
        "timeout_seconds": 5400,
        "engineering_validation": "not_evaluated",
    }
    if args.dry_run:
        print(json.dumps({**metadata, "dry_run": True, "prompt_bytes": len(prompt)}))
        return 0
    if args.transport_dir is None or not hasattr(signal, "SIGALRM"):
        raise RuntimeError("Linux transport and bounded timeout required")
    transport = args.transport_dir.resolve() / "frontier_wright_eval.py"
    metadata["transport_sha256"] = sha(transport.read_bytes())
    key_name = "OPENAI_API_KEY" if args.model == MODELS[0] else "ANTHROPIC_API_KEY"
    key = os.environ.get(key_name)
    if not key:
        raise RuntimeError("required API credential absent; no request sent")
    sys.path.insert(0, str(transport.parent))
    from frontier_wright_eval import generate

    responses = directory / "responses"
    responses.mkdir(exist_ok=True)
    case = responses / args.model
    case.mkdir(exist_ok=False)
    metadata.update(started_utc=datetime.now(timezone.utc).isoformat(),
                    slurm_job_id=os.environ.get("SLURM_JOB_ID"))
    write_json_new(case / "request.json", metadata)
    (case / "prompt.txt").write_bytes(prompt)
    (case / "instructions.txt").write_bytes(instructions)

    def expire(signum, frame):
        raise TimeoutError("bounded model call expired")

    signal.signal(signal.SIGALRM, expire)
    signal.alarm(5400)
    try:
        response = generate(args.model, prompt.decode("utf-8"), 32000, key,
                            reasoning_effort="low",
                            instructions=instructions.decode("utf-8"))
        write_json_new(case / "response.json", response)
        complete = response.get("status") == "completed" and bool(response.get("response"))
        outcome = {
            "status": "completed" if complete else "incomplete",
            "stop_reason": response.get("stop_reason"),
            "model_returned": response.get("model_returned"),
            "response_sha256": sha((case / "response.json").read_bytes()),
            "engineering_validation": "not_evaluated",
            "automatic_retry": False,
        }
    except Exception as error:
        complete = False
        outcome = {"status": "error_or_uncertain", "error_type": type(error).__name__,
                   "automatic_retry": False, "engineering_validation": "not_evaluated"}
    finally:
        signal.alarm(0)
    outcome["finished_utc"] = datetime.now(timezone.utc).isoformat()
    write_json_new(case / "outcome.json", outcome)
    print(args.model, outcome["status"], flush=True)
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
