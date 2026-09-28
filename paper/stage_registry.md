# Versioned design and evaluation register

Author: Ehsan Roohi. Updated 28 September 2026.

This is a research archive, not an approved aircraft design. No flight or superiority over the Wright Flyer has been demonstrated.

| Stage | Geometry and three views | Constraints / calculation record | Disposition |
|---|---|---|---|
| V0: initial proposal | Original model-authored SVG/PNG in `received_2026-09-24/astra_fable_opus_designs/` | `analysis/prompts_v0/`, `paper/geometry_consistency_audit_v1.md` | Preserve original inconsistencies; not a unique construction definition |
| V1: clarification | `output/stage_threeviews/V1/`: three evaluator lifting-surface sheets | `analysis/raw_v1/`, `analysis/prompts_v1/`, archived results | These sheets omit airframe and propulsion; not complete aircraft drawings |
| V2: model revision | `output/stage_threeviews/V2/`: three coordinate-based sheets | `received_v2_64942345/`, `analysis/results/received_v2_audit01/` | Astra and Opus evaluated conditionally; Fable geometry unresolved |
| V2: independent trim | Same V2 reference geometry; no new geometry version | `paper/v2_trim_assessment.md`, `analysis/results/v2_trim_solve01/`, `analysis/results/v2_trim_opus_capacity_recovery01/` | Evaluator-selected alpha, elevator and thrust; not a new LLM response |
| V2: dynamic sign screen | Same frozen V2 geometry | `analysis/results/v2_rate_derivative_screen02/`, `analysis/results/v2_dynamic_gate01.json` | Astra/Opus pass a deliberately reduced two-state sign test; no full-aircraft modes or dynamic flight acceptance |
| V1 versus V2 pitch comparison | Both frozen versions, no new geometry | `analysis/results/v1_rate_derivative_screen01/`, `analysis/results/v1_v2_pitch_gate_comparison01.json` | Astra V1 static slope fails but its reduced two-state sign check passes; no full-aircraft dynamic verdict |
| V9: integrated dynamics feedback / model V3 returns | New coordinates and change lists proposed; three-view drawings not yet independently generated or geometry-gated | `analysis/prompts_v9_integrated_dynamics/`, Unity arrays 65007436 and 65009709, `received_v9_65007436/`, `received_v9_retry_65009709/`, `analysis/results/v9_integrated_response_audit.json` | All three complete responses archived; ledger arithmetic closes, Fable's conditional nominal force/moment sums close, but no installed trim or full dynamic modes validated |
| V3 geometry/loading gate 01 | Structured V3 schedules checked; Opus geometry still partly prose and Fable wheel semantics unresolved; no accepted new three views | `analysis/audit_v3_geometry_loading.py`, `analysis/results/v3_geometry_loading_gate01.json`, `paper/v3_geometry_loading_gate01.md` | Fable's extreme-CG fractions fail ledger recomputation; Opus 13° ventral gap is pivot-dependent; nominal area/clearance and necessary vertical-force arithmetic recorded. HOLD before V3 trim. |
| Wright Flyer I (1903): historical comparator | `output/stage_threeviews/Wright/`; independent partial lifting-surface reconstruction | `paper/four_aircraft_comparison.md`, `analysis/results/four_aircraft_comparison01/` | Historical flight documented; model CG/complete trim unresolved; reference-point slopes only |

## Drawing convention

SVG is the vector master and PNG is the preview. All new sheets use 38 drawing units per metre in every orthographic view and every sheet. Source paths and SHA-256 digests are in `output/stage_threeviews/manifest.json`. The common frame is x aft, y right, z up. Astra's native forward x is reversed. Propellers are swept discs, not fabricated blade designs. Only explicitly defined structural chains are depicted. Gaps and ambiguous topology are not silently repaired. Surfaces are chord-plane outlines, not resolved fabric shape or thickness. Reference controls are shown; trim control deflections are recorded numerically in the calculation record, not drawn as manufactured geometry.

Fable's V2 drawing is a station-envelope visualization, not solver-ready geometry: rounded wing tips remain omitted and explicitly labelled. Thus this sheet cannot be used to calculate final area or certify clearances. V1 sheets reconstruct archived evaluator models, not fully specified airframes.

## Required record for every subsequent stage

1. Immutable parent response and prompt; model identifier, run settings and provenance.
2. Geometry change list and source-hashed three views for **each** of the three models. An unchanged geometry may reuse its hashed sheet but must say so.
3. Mass/CG ledger; axes, units, areas, controls, thrust line and all unknown fields.
4. Geometry/clearance checks before an aerodynamic calculation; rejected and failed cases retained.
5. Whole-aircraft force and moment balances, fixed-control derivatives, mesh sensitivity, power assumptions and structural/control limitations.
6. A decision: accepted for the next numerical gate, rejected with specific feedback, or unresolved. Never label numerical trim as proven flight.

## Next scientific gate

Resolve the V3 geometry/loading gate-01 findings in `paper/v3_geometry_loading_gate01.md` before aerodynamic analysis: Fable's pilot-extreme CG fractions and wheel-point semantics, Opus's pitch-dependent ground contact, and all three loaded swept clearances. For Astra and Opus, replace incomplete/assumed drag and propulsive efficiency with defensible bounds, then test how CG, thrust-line and drag-location uncertainty change trim and restoring slopes. For Fable, independently recompute the claimed conditional balance rather than treating its exact arithmetic as a physical prediction. Dynamic modes and structural adequacy require additional installed-aircraft data. The V9 feedback responses and their token-limit retries are documented in `paper/v9_integrated_response_gate.md`; they do not retroactively validate the V2 paper results.

## Public archive boundary

The public package contains our code, prompts, model outputs, figures, calculation inputs/results and methodological notes. It excludes downloaded books and papers, copyrighted scans, solver executables, credentials, temporary folders and manuscript/personal PDFs. Roskam and Malaek sources remain private reference inputs; their full PDFs are not redistributed. Old notes retain their original dates and may describe superseded stages; this register and the V2 trim report identify the latest state.
