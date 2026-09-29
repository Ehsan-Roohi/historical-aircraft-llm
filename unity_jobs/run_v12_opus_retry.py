"""One reviewed Opus V12 continuation at 48k after a 32k max-token stop.

The prior partial response is immutable and never spliced into this response.
"""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


MODEL = "claude-opus-5-5"
STAGE = "v12_opus_reviewed_completion_attempt01"
LIMIT = 48000


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def write_json_new(path, data):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def prepare(source, target):
    target.mkdir(exist_ok=False)
    for name in ("prompts", "parents", "baselines"):
        (target / name).mkdir()
    prompt = (source / "prompts" / (MODEL + ".prompt.txt")).read_bytes()
    instruction = (source / "prompts" / "instructions.txt").read_bytes()
    parent = (source / "parents" / (MODEL + ".response.json")).read_bytes()
    baseline = (source / "baselines" / (MODEL + ".response.json")).read_bytes()
    prior_case = source / "responses" / MODEL
    prior_response = (prior_case / "response.json").read_bytes()
    prior_outcome = (prior_case / "outcome.json").read_bytes()
    outcome = json.loads(prior_outcome)
    wrapper = json.loads(prior_response)
    if (outcome.get("status") != "incomplete"
            or outcome.get("stop_reason") != "max_tokens"
            or outcome.get("response_sha256") != sha(prior_response)
            or wrapper.get("usage", {}).get("output_tokens") != 32000):
        raise ValueError("prior incomplete max-token response not established")
    (target / "prompts" / (MODEL + ".prompt.txt")).write_bytes(prompt)
    (target / "prompts" / "instructions.txt").write_bytes(instruction)
    (target / "parents" / (MODEL + ".response.json")).write_bytes(parent)
    (target / "baselines" / (MODEL + ".response.json")).write_bytes(baseline)
    (target / "prior.response.json").write_bytes(prior_response)
    (target / "prior.outcome.json").write_bytes(prior_outcome)
    runner = (source / "run_v12_installation.py").read_bytes()
    (target / "run_v12_installation.py").write_bytes(runner)
    wrapper_script = Path(__file__).read_bytes()
    (target / "run_v12_opus_retry.py").write_bytes(wrapper_script)
    write_json_new(target / "manifest.json", {
        "stage": STAGE, "status": "FROZEN_UNSENT",
        "reason": "prior model output stopped at 32000 max_tokens",
        "instructions_sha256": sha(instruction),
        "runner_sha256": sha(runner),
        "retry_wrapper_sha256": sha(wrapper_script),
        "prior_response_sha256": sha(prior_response),
        "prior_outcome_sha256": sha(prior_outcome),
        "maximum_output_tokens": LIMIT, "reasoning_effort": "low",
        "records": [{"model": MODEL,
                     "prompt_file": MODEL + ".prompt.txt",
                     "prompt_sha256": sha(prompt),
                     "parent_file": MODEL + ".response.json",
                     "parent_sha256": sha(parent),
                     "baseline_sha256": sha(baseline),
                     "maximum_calls": 1}],
    })
    print(target.name)


def run(target, transport_dir):
    manifest = json.loads((target / "manifest.json").read_bytes())
    if (manifest["stage"] != STAGE or manifest["status"] != "FROZEN_UNSENT"
            or manifest["maximum_output_tokens"] != LIMIT
            or manifest["retry_wrapper_sha256"] != sha(Path(__file__).read_bytes())
            or manifest["prior_response_sha256"] != sha((target / "prior.response.json").read_bytes())
            or manifest["prior_outcome_sha256"] != sha((target / "prior.outcome.json").read_bytes())):
        raise ValueError("reviewed retry source mismatch")
    prior = json.loads((target / "prior.outcome.json").read_bytes())
    response = json.loads((target / "prior.response.json").read_bytes())
    if (prior.get("status") != "incomplete" or prior.get("stop_reason") != "max_tokens"
            or response.get("usage", {}).get("output_tokens") != 32000):
        raise ValueError("prior attempt was not the reviewed max-token stop")
    sys.path.insert(0, str(target))
    import run_v12_installation as frozen_runner
    frozen_runner.STAGE = STAGE
    frozen_runner.MAX_OUTPUT_TOKENS = LIMIT
    return frozen_runner.run_one(target, transport_dir, MODEL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-source", type=Path)
    parser.add_argument("--attempt-dir", type=Path, required=True)
    parser.add_argument("--transport-dir", type=Path)
    args = parser.parse_args()
    if args.prepare_source:
        prepare(args.prepare_source.resolve(), args.attempt_dir.resolve())
        return 0
    if not args.transport_dir:
        parser.error("--transport-dir required for run")
    return run(args.attempt_dir.resolve(), args.transport_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
