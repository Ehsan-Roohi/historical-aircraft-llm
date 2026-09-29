"""Freeze three complete-parent V14 design-feedback requests; never submit here.

The generated manifest remains FROZEN_UNSENT until a separately reviewed
transport and Unity submission. Previous responses are immutable.
"""

from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "v14_integrated_candidate_attempt01"
STAGE = "v14_installed_candidate_for_independent_dynamics"
LIMIT = 48000
SOURCE = {
    "gpt-6-astra": (
        "v12_installation_attempt01/prompts/gpt-6-astra.prompt.txt",
        "v12_installation_attempt01/responses/gpt-6-astra/response.json",
        "received_v9_65007436/gpt-6-astra/response.json"),
    "claude-fable-5-1": (
        "v12_installation_attempt01/prompts/claude-fable-5-1.prompt.txt",
        "v13_fable_arithmetic_attempt01/responses/claude-fable-5-1/response.json",
        "received_v9_retry_65009709/claude-fable-5-1/response.json"),
    "claude-opus-5-5": (
        "v12_installation_attempt01/prompts/claude-opus-5-5.prompt.txt",
        "v12_opus_retry_attempt01/responses/claude-opus-5-5/response.json",
        "received_v9_retry_65009709/claude-opus-5-5/response.json"),
}

INSTRUCTIONS = """This is a modern researcher-assisted revision of a historical aircraft concept, NOT a new 1898-only result. The full V12 request context and your latest complete response are supplied. Design one fully integrated, internally consistent candidate that can be independently screened; you may replace any component. Identify your parent version and explicit change list. Give SI units, axis signs, coordinate origin, sources of each number, uncertainty and provenance tag [retained assumption], [new assumption], [arithmetic], or [measured]. Nothing unmeasured may be called measured. Do not fabricate an engine curve, propeller coefficients, aerodynamic derivative, material strength, static margin, dynamic mode, or flight test. If you cannot close a required design interface, return HOLD and name the exact missing design choice rather than claiming success. Output one JSON object only, without Markdown. The evaluator, not you, decides flight/dynamic acceptance."""

COMMON = """
Required JSON sections:
1. version, parent hash, disposition and exhaustive change log.
2. One member-resolved three-view coordinate schedule (all lifting, vertical and control surfaces; pilot; engine and cooling; fuel; transmission; propellers/discs; truss nodes/members; gear and ground); true occupied envelopes, hinges, stops and swept clearances, not only equivalent inertia boxes.
3. Exclusive part-by-part mass ledger with centroids and primitive dimensions/orientation adequate for intrinsic Ixx, Iyy, Izz and Ixz; report total, first moments, CG and inertia tensor for nominal and extreme pilot/fuel states. Do not count the same physical object twice.
4. Control topology and load path with sign, travel, rate and stops for pitch, roll, yaw and throttle, including interference tests at extremes.
5. Bounded propulsion design: engine-side target, torque-speed requirement, reduction/drive loss, matched propeller radius/pitch/rpm/torque and thrust requirements, fuel/cooling/clearance. Mark a map UNKNOWN if not available. Show mass--power iteration, including a declared reserve criterion across heavy/high-drag and low-speed cases.
6. For a future independent evaluator, specify trim envelope, CG endpoints, reference area/chord/span, geometry needed for a full-aircraft quasi-steady model, structural load cases, and a table of which longitudinal/lateral derivatives are calculated versus UNKNOWN. Include C_m_alpha, C_m_q, C_m_alpha_dot, C_Z_alpha_dot, C_Y_beta, C_l_beta, C_n_beta and control derivatives, but never assign missing unsteady terms zero. No model-authored stability pass is accepted.
7. A machine-readable uncertainty/verification table with all unresolved quantities and the next physical or low-order test needed. Do not claim flightworthy or dynamically stable without independently validated trim and modes.
"""

SPECIFIC = {
    "gpt-6-astra": "Your complete V12 response returned HOLD without adopting an installed configuration. The user now authorizes a non-minimal replacement, not preservation of V0/V3 architecture. First propose one concrete installed configuration with member nodes, engine/shaft, gear and control interfaces. If a fully specified candidate is impossible, identify the minimal design decisions preventing closure, not an unspecified physical measurement as a generic reason to stop.",
    "claude-fable-5-1": "Your latest complete V13 response fixes mass bookkeeping at 354.3 kg but retains a 0.520 kW shaft-side shortfall to your own 15% heavy-case reserve after 0.95 drive loss. A simple paper engine-target increase is not closure: change the engine/drive/propeller and/or drag, recalculate every part mass, CG, inertia and power case, and recheck the split-tail and drive/brace/gear interfaces. Distinguish assumed engine targets from available measured curves.",
    "claude-opus-5-5": "Your separate 48,000-token V12 replay was complete; do not merge it with the earlier truncated 32,000-token response. Its 340.3 kg ledger and aft-skid rigid contact arithmetic passed selected checks. Preserve or explicitly revise the full installation, but close nose-down contacts, pilot/engine/fuel occupied-solid interference, loaded-clearance assumptions, propeller torque/thrust matching, and the CG change from V3. Do not carry an old neutral point to the new CG.",
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def write_new(path, blob):
    with path.open("xb") as handle:
        handle.write(blob)


def main():
    ATTEMPT.mkdir(exist_ok=False)
    for name in ("prompts", "parents", "baselines"):
        (ATTEMPT / name).mkdir()
    write_new(ATTEMPT / "prompts/instructions.txt", INSTRUCTIONS.encode())
    template = (ROOT / "v12_installation_attempt01/run_v12_installation.py").read_text()
    if template.count('STAGE = "v12_installation_candidate"') != 1:
        raise ValueError("Unexpected runner stage")
    if template.count("MAX_OUTPUT_TOKENS = 32000") != 1:
        raise ValueError("Unexpected runner limit")
    runner = template.replace('STAGE = "v12_installation_candidate"',
                              f'STAGE = "{STAGE}"').replace(
                              "MAX_OUTPUT_TOKENS = 32000",
                              f"MAX_OUTPUT_TOKENS = {LIMIT}").encode()
    write_new(ATTEMPT / "run_v14_candidate.py", runner)
    records = []
    for model, (context_path, parent_path, baseline_path) in SOURCE.items():
        context = (ROOT / context_path).read_bytes()
        parent = (ROOT / parent_path).read_bytes()
        baseline = (ROOT / baseline_path).read_bytes()
        parent_data = json.loads(parent)
        if parent_data.get("status") != "completed" or not parent_data.get("response"):
            raise ValueError(f"Latest parent is not a complete response: {model}")
        composed = ("V14 FEEDBACK. Exact V12 source context follows; earlier text "
                    "is model-authored, not independently validated.\n\n" +
                    SPECIFIC[model] + "\n\n" + COMMON +
                    "\n--- BEGIN FROZEN V12 REQUEST CONTEXT ---\n" +
                    context.decode() +
                    "\n--- END FROZEN V12 REQUEST CONTEXT ---\n" +
                    f"\n--- BEGIN LATEST COMPLETE RESPONSE; wrapper SHA-256 {sha(parent)} ---\n" +
                    parent_data["response"] +
                    "\n--- END LATEST COMPLETE RESPONSE ---\n").encode()
        name = model + ".prompt.txt"
        write_new(ATTEMPT / "prompts" / name, composed)
        write_new(ATTEMPT / "parents" / (model + ".response.json"), parent)
        write_new(ATTEMPT / "baselines" / (model + ".response.json"), baseline)
        records.append({"model": model, "prompt_file": name,
                        "prompt_sha256": sha(composed),
                        "parent_file": model + ".response.json",
                        "parent_sha256": sha(parent),
                        "baseline_sha256": sha(baseline),
                        "v12_context_sha256": sha(context),
                        "maximum_calls": 1})
    manifest = {"stage": STAGE, "status": "FROZEN_UNSENT",
                "scope": "three complete-parent requests; no API call made by builder",
                "instructions_sha256": sha(INSTRUCTIONS.encode()),
                "runner_sha256": sha(runner),
                "maximum_output_tokens": LIMIT,
                "reasoning_effort": "low", "records": records}
    write_new(ATTEMPT / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    print("V14 prompts frozen and UNSENT", [r["model"] for r in records])


if __name__ == "__main__":
    main()
