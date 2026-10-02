# Draft27: current manuscript and conditional engineering evidence

Published snapshot prepared 2 October 2026. This is a research draft, not a flightworthy design, journal acceptance, or evidence of submission.

## Start here

- [Full reading PDF (67 pages)](manuscript/main.pdf)
- [Double-spaced review PDF (83 pages)](manuscript/main_joa_review.pdf)
- [LaTeX source](manuscript/main.tex)
- [File checksums and exclusions](MANIFEST.json)
- [Rights and provenance](manuscript/RIGHTS_AND_PROVENANCE.txt)

The complete scientific text, 18 figures, 23 tables and 44 numbered references are retained. Figures 5, 8 and 11 now identify components inside their plates. Earlier public tags remain unchanged.

## Evidence map

| Claim | Evidence in this snapshot |
|---|---|
| Completed V14 and V15 responses | `model_runs/received_v14_65021957`, `model_runs/received_v15_65023104` |
| Completed Astra/Opus V16 and first incomplete Fable | `model_runs/received_v16_65049531` |
| Fable timeout, later truncation and completed response | `model_runs/received_v16_fable_65054393`, `received_v16_fable_65056099`, `received_v16_fable_65061669` |
| Eight Fable loading/trim cases | `manuscript/audit_data/v16/fable_v16_surface_retrim01`, loading audit JSON |
| 12/13/16 m/s power sensitivity | `manuscript/audit_data/v16/power_speed`, manuscript section 3.14 |
| Astra radial quadrature and Opus RPM closure | `manuscript/audit_data/v16/v16_astra_propeller_quadrature*`, `v16_opus_rpm_closure*` |
| Tail structural/mass sensitivities | `manuscript/audit_data/v15_tail*` |

## What the results establish

Fable V16 has conditional surface-model static margins of 3.98–10.12% across eight loading cases at 13 m/s. These are rigid, quasi-steady lifting-surface calculations with unvalidated section assumptions, not six-component installed-aircraft trim or validated dynamic modes.

With only induced drag replaced by the corresponding surface calculation and the other response assumptions retained, the heavy-case shaft demands are 16.362, 18.053 and 26.037 kW at 12, 13 and 16 m/s. Against the assumed 20.045 kW supply, the 13 m/s reserve is 11.03%, below an exploratory 15% target; the 16 m/s absolute shortfall is 5.992 kW. Stall margin at 12 m/s is unknown. These are sensitivity calculations, not measured propulsion performance.

None of the designs has demonstrated flight capability, structural adequacy or full installed trim. Historical source restrictions apply to the supplied packet, not model training. Researcher interventions and modern evaluator assumptions are separate from the original model proposals. Unequal retries/output budgets prevent interpreting this as a controlled model ranking.

## Scope and reproduction limits

This release adds the received V14–V16 records and evidence packaged with draft27. It does not claim to contain every local file or every provider-side/transport record. The older `research_evidence.zip` remains an older R5 archive, not the latest dataset.

Raw included response bytes are preserved. The manifest explicitly lists five omitted host-specific scripts, including three audit runners; their numerical outputs remain included. Consequently this is an evidence archive with selected reproducible analyses, not a fully portable one-command reproduction package. No solver binaries, private course scans, reference-book PDFs, private author-action notes or unsent editor correspondence are added. Existing internal package audit hashes refer to their original local inventories; the root manifest describes this curated export.

The original manuscript Data Availability paragraph records its pre-release state and older immutable tags; this README documents the subsequent public addition without silently changing the audited manuscript. No new blanket license over third-party material is asserted.
