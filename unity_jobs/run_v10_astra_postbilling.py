"""One post-billing Astra V10 call with frozen sources and no auto-retry.

Both earlier failed attempts are retained separately. A minimal billing probe
has accepted the same credential, but this run does not assume design validity.
"""

import argparse
import hashlib
import json
import os
import re
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def diagnostic(error):
    # Keep the HTTP status/constraint while not archiving a possible credential.
    message = str(error)
    message = re.sub(r"(?i)(sk-[A-Za-z0-9_-]{12,})", "[REDACTED_KEY]", message)
    message = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._-]+", r"\1[REDACTED]", message)
    return message[:800]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-dir", type=Path, required=True)
    parser.add_argument("--transport-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    directory = args.attempt_dir.resolve()
    manifest_bytes = (directory / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest["stage"] != "v10_astra_postbilling_attempt01"
            or manifest["maximum_output_tokens"] != 20000
            or manifest["model"] != "gpt-6-astra"
            or manifest["maximum_calls"] != 1):
        raise ValueError("unexpected post-billing manifest")
    prompt = (directory / "prompt.txt").read_bytes()
    instructions = (directory / "instructions.txt").read_bytes()
    parent = (directory / "parent.response.json").read_bytes()
    prior = (directory / "prior.outcome.json").read_bytes()
    probe = (directory / "billing_probe.json").read_bytes()
    for field, value in (("prompt_sha256", prompt),
                         ("instructions_sha256", instructions),
                         ("parent_response_sha256", parent),
                         ("prior_outcome_sha256", prior),
                         ("billing_probe_sha256", probe)):
        if sha(value) != manifest[field]:
            raise ValueError(f"{field} mismatch")
    prior_status = json.loads(prior)
    if (prior_status["status"] != "error_or_uncertain"
            or prior_status["error_type"] != "RuntimeError"
            or "credit_balance_exhausted" not in prior_status.get("diagnostic_redacted", "")):
        raise ValueError("prior attempt must be the archived quota error")
    probe_status = json.loads(probe)
    if (probe_status.get("http_status") != 200
            or probe_status.get("model") != "gpt-6-astra"
            or probe_status.get("status") != "completed"):
        raise ValueError("billing probe did not establish accepted Astra access")
    metadata = {
        "stage": manifest["stage"], "model_requested": manifest["model"],
        "prompt_sha256": sha(prompt), "instructions_sha256": sha(instructions),
        "parent_response_sha256": sha(parent),
        "prior_outcome_sha256": sha(prior),
        "billing_probe_sha256": sha(probe),
        "manifest_sha256": sha(manifest_bytes),
        "maximum_output_tokens": 20000, "reasoning_effort": "low",
        "maximum_calls": 1, "timeout_seconds": 5400,
        "engineering_validation": "not_evaluated",
    }
    if args.dry_run:
        print(json.dumps({**metadata, "dry_run": True, "prompt_bytes": len(prompt)}))
        return 0
    if args.transport_dir is None or not hasattr(signal, "SIGALRM"):
        raise RuntimeError("Linux transport and timeout required")
    transport = args.transport_dir.resolve() / "frontier_wright_eval.py"
    metadata["transport_sha256"] = sha(transport.read_bytes())
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OpenAI credential absent; no request sent")
    sys.path.insert(0, str(transport.parent))
    from frontier_wright_eval import generate

    response_dir = directory / "response"
    response_dir.mkdir(exist_ok=False)
    metadata.update(started_utc=datetime.now(timezone.utc).isoformat(),
                    slurm_job_id=os.environ.get("SLURM_JOB_ID"))
    write_new(response_dir / "request.json", metadata)
    (response_dir / "prompt.txt").write_bytes(prompt)
    (response_dir / "instructions.txt").write_bytes(instructions)

    def expired(signum, frame):
        raise TimeoutError("bounded call expired")

    signal.signal(signal.SIGALRM, expired)
    signal.alarm(5400)
    try:
        result = generate("gpt-6-astra", prompt.decode("utf-8"), 20000, key,
                          reasoning_effort="low", instructions=instructions.decode("utf-8"))
        write_new(response_dir / "response.json", result)
        complete = result.get("status") == "completed" and bool(result.get("response"))
        outcome = {
            "status": "completed" if complete else "incomplete",
            "stop_reason": result.get("stop_reason"),
            "model_returned": result.get("model_returned"),
            "response_sha256": sha((response_dir / "response.json").read_bytes()),
            "automatic_retry": False,
        }
    except Exception as error:
        complete = False
        outcome = {"status": "error_or_uncertain", "error_type": type(error).__name__,
                   "diagnostic_redacted": diagnostic(error), "automatic_retry": False}
    finally:
        signal.alarm(0)
    outcome["finished_utc"] = datetime.now(timezone.utc).isoformat()
    outcome["engineering_validation"] = "not_evaluated"
    write_new(response_dir / "outcome.json", outcome)
    print("gpt-6-astra", outcome["status"], flush=True)
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
