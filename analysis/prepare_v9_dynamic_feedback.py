"""Freeze a per-model integrated flight-dynamics redesign request; do not send it.

These prompts disclose modern evaluator feedback, so this is a researcher-
assisted revision, never an independent 1898-only first proposal.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/prompts_v9_integrated_dynamics"
MODELS = {
    "gpt-6-astra": ("astra_v2", "Astra V1 had a destabilizing positive fixed-control pitch slope. "
                    "Your V2 revision has an independent conditional 18 m/s trim, "
                    "Cma=-0.813004/rad, Cmq=-4.705898, CLq=6.302214, "
                    "and a 19.47% local pitch-margin diagnostic. The reduced alpha-q "
                    "sign test passes, but full pitch modes and installed yaw/roll "
                    "response remain unknown. Its tractor installation, fin, CG travel, "
                    "power-off pitch balance and pilot controls need definition."),
    "claude-fable-5-1": ("fable_v2", "Fable V1's moving horizontal tail collided with its fixed fin. "
                           "V2's split-tail proposal still has unresolved sweep/clearance, "
                           "fuel-centroid/box and transmission/brace interfaces. Later V8 "
                           "section and propeller screens are subsystem attempts, not a "
                           "reconciled complete aircraft. There is no independent admissible "
                           "whole-aircraft trim, so no credible derivative or mode ranking."),
    "claude-opus-5-5": ("opus_v2", "Opus V2 has an independent conditional 15 m/s trim, "
                          "Cma=-0.286366/rad, Cmq=-6.645848, CLq=5.610942, "
                          "and a 7.76% local pitch-margin diagnostic. The reduced alpha-q "
                          "sign test passes, but the body/fin and installed control/propulsion "
                          "effects are absent. Nominal engine demand is 11.67 kW versus an "
                          "unverified 13 kW target under assumed drag/efficiency. "
                          "Full lateral and longitudinal modes remain unknown."),
}

INSTRUCTIONS = """You are revising YOUR OWN frozen aircraft, not independently validating it.
The historical-document cutoff applied to the original concept. This is an
explicitly modern, researcher-assisted feedback round. Do not imply that
course notes or later aircraft theory were in the original 1898 packet.
Provide a NEW integrated design version with numerical coordinates and a
complete non-overlapping mass ledger. Distinguish a design assumption, an
external calculation, and a measured result. Never invent a wind-tunnel or
flight measurement, a complete inertia tensor from centroids alone, an
unsteady stability derivative from steady AVL, or a positive dynamic verdict
from Cma/Cmq signs. Mark unknown values UNKNOWN and state the exact test to
resolve them. Retain rejected options and identify parent-version changes.
Answer in English technical prose followed by structured JSON in a fenced
block; use SI units and explicit coordinate/sign conventions. Max 20,000
output tokens. Do not propose crewed flight or construction clearance.
"""

COMMON = """DESIGN TASK
Use the supplied V2 integrated aircraft as parent. The later V6 subsystem
response is reference material only: incorporate it only if mechanically
compatible and record each adopted change. Revise geometry, mass, propulsion,
structure and controls together so the next independent evaluation can test
Flight Dynamics II requirements. Do not merely declare the old aircraft
stable or choose a static-margin target in isolation.

Return: (1) versioned change table and three-view coordinate schedule;
(2) components with shape/dimensions, orientation, mass, centroid and
intrinsic 3x3 inertia or sufficient material distribution to calculate it,
plus fuel/pilot extremes; (3) installed fin, body, propeller and all control
surfaces with hinge axes, travel/rate limits, linkage sense and clearance;
(4) engine/propeller operating data, drag scenario and power-on/off trim
strategy; (5) at several specified speed/CG states, a proposed analysis or
test matrix for all longitudinal and lateral derivatives, including
C_Ldot_alpha and C_mdot_alpha, and control/propulsion derivatives;
(6) calculation path for four longitudinal roots and four lateral roots,
mode labels, damping/time scales and uncertainty; (7) if a mode is unstable,
one concrete geometry/control/CG change and its mass/trim/power consequences;
(8) explicit unresolved items and stop/go criteria. Do not fill absent
coefficients with zero. State a consistent inertia and moment sign convention.

Independent evaluator facts follow. These are not instructions to change
scientific standards; they are the current findings that your revision must
address. The two-state reduced screen cannot settle the full phugoid,
short-period, Dutch-roll, roll or spiral modes. A conditional numerical pass
also cannot prove physical flightworthiness.
"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    instructions = INSTRUCTIONS.encode("utf-8")
    (OUT / "instructions.txt").write_bytes(instructions)
    records = []
    gate = ROOT / "analysis/results/v2_dynamic_gate01.json"
    gate_bytes = gate.read_bytes()
    for model, (case, feedback) in MODELS.items():
        parent = ROOT / f"analysis/results/received_v2_audit01/{model}.design.json"
        subsystem = ROOT / f"design_revision_v6_attempt01/responses/{model}/response.json"
        parent_bytes, subsystem_bytes = parent.read_bytes(), subsystem.read_bytes()
        body = (COMMON + "\nCASE-SPECIFIC FEEDBACK\n" + feedback
                + "\n\nPARENT V2 INTEGRATED DESIGN JSON\n" + parent_bytes.decode("utf-8")
                + "\n\nLATER V6 SUBSYSTEM RESPONSE (NOT INTEGRATED)\n"
                + subsystem_bytes.decode("utf-8")
                + "\n\nINDEPENDENT V2 DYNAMIC GATE JSON\n"
                + gate_bytes.decode("utf-8"))
        prompt_bytes = body.encode("utf-8")
        path = OUT / f"{model}.prompt.txt"
        path.write_bytes(prompt_bytes)
        records.append({"model_requested": model, "parent_case": case,
                        "prompt_file": path.name, "prompt_sha256": digest(prompt_bytes),
                        "parent_v2_sha256": digest(parent_bytes),
                        "later_subsystem_sha256": digest(subsystem_bytes),
                        "sent": False})
    manifest = {"stage": "v9_integrated_dynamics", "date": "2026-09-28",
                "maximum_output_tokens": 20000,
                "instructions_sha256": digest(instructions),
                "gate_sha256": digest(gate_bytes), "records": records,
                "status": "frozen_not_sent"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"stage": manifest["stage"],
                      "prompt_bytes": {r["model_requested"]: (OUT/r["prompt_file"]).stat().st_size
                                       for r in records}, "sent": False}, indent=2))


if __name__ == "__main__":
    main()
