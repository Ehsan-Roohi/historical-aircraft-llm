"""One hash-checked high-token retry for each truncated Claude design."""
import argparse
import hashlib
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

MODELS = ("claude-fable-5-1", "claude-opus-5-5")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--transport-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    source = here.parent / "dynamic_revision_v9_attempt01"
    manifest_bytes = (here / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest["stage"] != "v9_integrated_dynamics_retry" or manifest["maximum_output_tokens"] != 48000:
        raise ValueError("Unexpected retry manifest")
    rows = [row for row in manifest["records"] if row["model"] == args.model]
    if len(rows) != 1:
        raise ValueError("Expected exactly one retry record")
    row = rows[0]
    source_manifest = json.loads((source / "prompts" / "manifest.json").read_bytes())
    source_rows = [item for item in source_manifest["records"] if item["model_requested"] == args.model]
    if source_manifest["stage"] != manifest["source_stage"] or len(source_rows) != 1:
        raise ValueError("Unexpected original request")
    prompt = (source / "prompts" / (args.model + ".prompt.txt")).read_bytes()
    prior_bytes = (source / "responses" / args.model / "response.json").read_bytes()
    prior = json.loads(prior_bytes)
    instructions = (here / "instructions.txt").read_bytes()
    if sha(prompt) != row["prompt_sha256"] or sha(prompt) != source_rows[0]["prompt_sha256"]:
        raise ValueError("Prompt hash mismatch")
    if sha(prior_bytes) != row["prior_response_sha256"]:
        raise ValueError("Prior response hash mismatch")
    if prior.get("status") != "incomplete" or prior.get("stop_reason") != "max_tokens":
        raise ValueError("Prior response was not truncated at max_tokens")
    meta = {
        "stage": manifest["stage"],
        "model_requested": args.model,
        "prompt_sha256": sha(prompt),
        "instructions_sha256": sha(instructions),
        "manifest_sha256": sha(manifest_bytes),
        "prior_response_sha256": sha(prior_bytes),
        "prior_response_id": prior.get("response_id"),
        "maximum_output_tokens": manifest["maximum_output_tokens"],
        "maximum_calls": 1,
        "reasoning_effort": "low",
        "timeout_seconds": 5400,
        "retry_type": "independent_full_prompt",
    }
    if args.dry_run:
        print(json.dumps({**meta, "dry_run": True, "prompt_bytes": len(prompt)}))
        return 0
    if not hasattr(signal, "SIGALRM"):
        raise RuntimeError("Linux timeout required")
    transport = args.transport_dir.resolve() / "frontier_wright_eval.py"
    meta["transport_sha256"] = sha(transport.read_bytes())
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("Required credential absent; no request sent")
    sys.path.insert(0, str(transport.parent))
    from frontier_wright_eval import generate
    output = here / "responses"
    output.mkdir(exist_ok=True)
    case = output / args.model
    case.mkdir(exist_ok=False)
    meta.update(started_utc=datetime.now(timezone.utc).isoformat(),
                slurm_job_id=os.environ.get("SLURM_JOB_ID"))
    write_new(case / "request.json", meta)
    (case / "prompt.txt").write_bytes(prompt)
    (case / "instructions.txt").write_bytes(instructions)

    def expired(signum, frame):
        raise TimeoutError("Bounded model call expired")

    signal.signal(signal.SIGALRM, expired)
    signal.alarm(5400)
    try:
        result = generate(args.model, prompt.decode("utf-8"), 48000, key,
                          reasoning_effort="low", instructions=instructions.decode("utf-8"))
        write_new(case / "response.json", result)
        complete = result.get("status") == "completed" and bool(result.get("response"))
        outcome = {
            "status": "completed" if complete else "incomplete",
            "stop_reason": result.get("stop_reason"),
            "response_sha256": sha((case / "response.json").read_bytes()),
            "model_returned": result.get("model_returned"),
            "engineering_validation": "not_evaluated",
        }
    except Exception as error:
        outcome = {"status": "error_or_uncertain", "error_type": type(error).__name__,
                   "automatic_retry": False}
        complete = False
    finally:
        signal.alarm(0)
    outcome["finished_utc"] = datetime.now(timezone.utc).isoformat()
    write_new(case / "outcome.json", outcome)
    print(args.model, outcome["status"], flush=True)
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
