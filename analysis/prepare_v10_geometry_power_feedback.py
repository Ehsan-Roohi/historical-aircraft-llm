"""Freeze case-specific V10 correction requests from archived V3 evidence.

V10 is a modern, researcher-assisted geometry/power clarification round.
Generating requests is not submitting them or accepting model claims.
"""

import hashlib
import json
import re
from pathlib import Path

from audit_v3_geometry_loading import SOURCES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/prompts_v10_geometry_power"
MODEL_IDS = {
    "astra": "gpt-6-astra",
    "fable": "claude-fable-5-1",
    "opus": "claude-opus-5-5",
}
SPECIFIC = {
    "astra": """Your declared 18 m/s high-drag case (D=520 N) needs 17,913.876 W at eta_prop=0.55 and eta_drive=0.95, leaving only 86.124 W against an UNVERIFIED 18,000 W engine target. Provide a defensible *conditional* design response: either a quantified lower-drag/greater-power revision with updated mass/CG/geometry and source label, or explicitly retain the unresolved high-case power gate. Nominal prop-ground gap is 0.400 m, but loaded prop/gear/controls clearance is UNKNOWN. Supply exact swept-envelope definitions, positive/negative pitch travel and critical rigid clearance calculations; do not invent loaded deflections or material properties. Actual powered and glide trim, installed derivatives and modes are UNKNOWN. State precisely what measured/component data and subsequent independent calculations would resolve them.""",
    "fable": """The independent recomputation from your 23-row ledger gives the 65 kg pilot at aft seat x=0.50 m: xCG=1.629499 m = 36.730% of lower-deck chord with full fuel (36.896% empty), not your 35.4%. The 85 kg pilot at forward seat x=0.20 m gives xCG=1.478983 m = 28.594% chord with full fuel (28.320% empty), not your 30.2%. Correct the figures or specify an explicit changed mass/seat/ballast ledger and recompute all extremes. Your three wheel coordinates are at z=-0.75 m, equal to the rest ground plane; define whether they are centres or contacts, give wheel radii and a consistent ground-contact geometry. The nominal prop/body gap is only 0.050 m and your lower horn/longeron gap is 0.040 m; supply a geometric swept/tolerance budget, not an unsupported safety claim. Your engine table calls 10.700 kW the required shaft power, but D=426 N at V=13 m/s and eta=0.50 gives 11.076 kW (rounded to 11.080 in your drag table). Reconcile both fields and leave actual engine availability UNKNOWN unless independently evidenced. Re-evaluate the claimed aft static-margin case at the corrected extreme; do not assert a validated margin or trim.""",
    "opus": """Your declared x-aft,z-up schedule has a ventral-fin aft-lower corner at (5.60,0.25) m, flat skid ending at x=1.60 m and tail-skid tip at (5.50,0) m over rest ground z=-0.90 m. Rigid 13-degree nose-up rotation about the aft-skid contact gives ventral gap 0.220721 m, reproducing your 0.221 m; the tail-skid tip reaches ground at 12.994617 degrees. Wheel-pivot-only rotation at x=0.45 m would intersect ground. Specify the physically intended wheel-to-skid-to-tail-skid contact sequence, load path and rotation limit; separate rigid geometry from UNKNOWN loaded deflection/brace clearance. Your unverified 13 kW engine target is 0.700 kW below your own 13.700 kW high-drag shaft demand at 15 m/s. Either supply a *conditional* revised engine/drag/efficiency design with mass/CG consequences, or explicitly retain that failure; do not fabricate an engine curve or propeller map. Actual powered/glide trim and modes remain UNKNOWN.""",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    geometry_audit = ROOT / "analysis/results/v3_geometry_loading_gate01.json"
    power_audit = ROOT / "analysis/results/v3_power_necessity_gate01.json"
    geometry_bytes = geometry_audit.read_bytes()
    power_bytes = power_audit.read_bytes()
    OUT.mkdir(exist_ok=False)
    instructions = (
        "You are responding to a modern engineering feedback round. Be concise and factual. "
        "Do not claim physical flight, construction clearance, measured data, validated trim, "
        "or stable modes without actual independent evidence. Do not silently change the "
        "historical V0 record. Output one JSON fenced block with the requested schema.\n"
    )
    (OUT / "instructions.txt").write_text(instructions, encoding="utf-8")
    records = []
    for case, model_id in MODEL_IDS.items():
        source = SOURCES[case]
        wrapper = json.loads(source.read_text(encoding="utf-8"))
        blocks = re.findall(r"```json\s*(.*?)```", wrapper["response"], re.DOTALL)
        if len(blocks) != 1:
            raise ValueError(f"Expected one V3 JSON block for {case}")
        parent = json.loads(blocks[0])
        source_hash = sha(source.read_bytes())
        core = (
            f"You authored this archived {case.upper()} V3 proposal. "
            f"Its immutable response.json SHA-256 is {source_hash}. "
            "Do not revise the parent file; propose a V3R correction patch only. "
            "The common historical source cutoff applied to V0, not to this modern feedback round.\n\n"
            "INDEPENDENT EVALUATOR FINDINGS (not new model-authored measurements):\n"
            + SPECIFIC[case] + "\n\n"
            "TASK: First identify each disputed parent claim and its corrected arithmetic. "
            "Then provide the smallest viable coordinate/mass/propulsion change, if any, "
            "that makes the drawing internally consistent. Give all changed component "
            "IDs, native-frame XYZ coordinates, dimensions, masses, CG for nominal and "
            "pilot/fuel extremes, and the exact contact/swept-clearance equations used. "
            "If an interface cannot be specified from the record, mark UNKNOWN and give "
            "a measurement/CAD test; do not assign an arbitrary positive clearance. "
            "Keep unmodified parent items explicitly unchanged by ID. For propulsion, "
            "separate required power, target power and measured available power. State "
            "whether the assumed worst case passes the assumed target, and what evidence "
            "would be needed for installed power. Provide a compact, staged test plan for "
            "powered and power-off whole-aircraft trim and dynamics, without claiming "
            "that tests have been done. Avoid CFD and avoid full manuscript prose.\n\n"
            "Return one fenced JSON object with keys: version, parent_sha256, "
            "coordinate_frame, disputed_claims, correction_patch, unchanged_item_ids, "
            "mass_loading_states, contact_and_clearance, propulsion_requirement, "
            "trim_input_status, dynamics_input_status, unresolved, tests_next, "
            "flight_verdict. Use numeric values with units in field names where possible; "
            "UNKNOWN must remain a string. Keep your prose outside JSON under 500 words.\n\n"
            "ARCHIVED PARENT STRUCTURED DATA:\n"
            + json.dumps(parent, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
        prompt = core.encode("utf-8")
        filename = model_id + ".prompt.txt"
        (OUT / filename).write_bytes(prompt)
        records.append({
            "case": case,
            "model_requested": model_id,
            "parent_response_sha256": source_hash,
            "prompt_file": filename,
            "prompt_sha256": sha(prompt),
            "prompt_bytes": len(prompt),
            "sent": False,
        })
    manifest = {
        "stage": "v10_geometry_power_feedback",
        "status": "FROZEN_UNSENT",
        "maximum_output_tokens": 32000,
        "reasoning_effort": "low",
        "maximum_calls_per_model": 1,
        "instructions_sha256": sha((OUT / "instructions.txt").read_bytes()),
        "evaluator_geometry_audit_sha256": sha(geometry_bytes),
        "evaluator_power_audit_sha256": sha(power_bytes),
        "records": records,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "records": records}, indent=2))


if __name__ == "__main__":
    main()
