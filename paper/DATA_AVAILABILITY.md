# Data and code availability for the aircraft-LLM study

Author: Ehsan Roohi. Public research snapshot: `aircraft-sr-2026-09-28-r3` in
[`Ehsan-Roohi/historical-aircraft-llm`](https://github.com/Ehsan-Roohi/historical-aircraft-llm/tree/aircraft-sr-2026-09-28-r3).
The exact included paths, byte counts and SHA-256 digests are recorded in
`MANIFEST.json`; `research_evidence.zip` is the consolidated downloadable
snapshot. The Git tag identifies a fixed repository commit. No DOI is claimed.

## What the public archive contains

| Research material | Public path in `research_evidence.zip` | Use and interpretation |
|---|---|---|
| Original historical packet and initial prompts | `analysis/prompts_v0/` | Actual supplied text; a source-date restriction, not a model-training cutoff. |
| Initial V0 outputs and model-authored drawings | `received_2026-09-24/astra_fable_opus_designs/`, plus preserved raw records in `analysis/results/` | Original proposals, including inconsistencies. |
| Clarification prompts and V1 returns | `analysis/prompts_v1/`, `analysis/raw_v1/`, `analysis/results/` | Complete recovered attempts and separate truncation/failure records where retained. |
| Revision prompts and V2 returns | `analysis/prompts_v2/`, `analysis/prompts_v2_retrim/`, `received_v2_64942345/prompts/`, `received_v2_64942345/responses/`, `analysis/results/received_v2_audit01/` | Model-authored revisions, not automatically verified designs. |
| Later model feedback exchanges | `received_v5_64962376/responses/`, `design_revision_v6_attempt01/responses/`, `unity_jobs/`, `analysis/results/` | Archived subsystem/revision attempts; do not silently treat them as a new integrated flightworthy aircraft. |
| Integrated dynamic redesign feedback | `analysis/prompts_v9_integrated_dynamics/`, `dynamic_revision_v9_attempt01/responses/` when available | Versioned, case-specific modern feedback. Its presence records a model proposal, not independent acceptance of a new aircraft. |
| Geometry and figure source/output | `output/stage_threeviews/`, `output/figures_v2/`, `output/overleaf/scientific_reports_aircraft_2026_09_28_release03/figures/`, `analysis/` | Original and evaluator drawings have distinct provenance. Figure 7 uses the archived numerical results; Fable's values are model claims. |
| Numerical inputs and outputs | `analysis/results/`, `output/overleaf/scientific_reports_aircraft_2026_09_28_release05/audit_data/` | Includes accepted and failed cases, mesh checks, residuals, both failed and completed rate-derivative runs, and the reduced dynamic gate. |
| Analysis and manuscript source | `analysis/`, `paper/`, `output/overleaf/scientific_reports_aircraft_2026_09_28_release05/` | Human-auditable code, TeX, supplement, references, and selected source records; the full-mode assembler is not run on incomplete V2 data. |

## Scientific Reports policy mapping

The journal requires a Data Availability section at the end of the main text,
before references, that identifies the minimum primary and referenced data
needed to interpret and repeat the results, with links/identifiers and any
access restrictions. Custom code central to the conclusions must be supplied
to editors and reviewers and described under a **Code availability** heading
in Methods. Figure source data should be identified when provided. See the
[journal's editorial policy](https://www.nature.com/srep/journal-policies/editorial-policies)
and [submission guidelines](https://www.nature.com/srep/author-instructions/submission-guidelines).

For this study, the primary data are prompts, responses, model-authored
geometry, frozen solver inputs, evaluator outputs, figure source data and
manifest hashes. The public snapshot is intended to be accessible at
submission, not merely promised for a later date. The paper distinguishes
archived raw outputs from evaluator reconstructions and unvalidated claims.

## Known limits and restrictions

- The archive contains **all locally recovered** prompts, responses and
  attempts in the listed project directories. It cannot certify complete
  recovery of every service-side transport field or an unrecorded earlier
  exchange; gaps are disclosed in the manuscript and provenance notes.
- Third-party books, lecture notes, scanned course material, journal PDFs,
  unreviewed solver executables, credentials, and personal documents are not
  redistributed. The newly supplied Flight Dynamics II RAR is a private
  methodological reference, not study data supplied to the language models.
- AVL is an external solver, not included as an executable. Its input/output
  text and analysis scripts are shared. The first V2 rate-derivative run failed
  during memory allocation, then a rerun succeeded at two meshes for Astra and
  Opus; both outcomes are archived. The quasi-steady $C_{m_q}$ values are
  reported with their restricted model scope. No $C_{m_{\dot\alpha}}$ value is
  available without a downwash-delay/unsteady model; missing derivatives are
  not set to zero.
- The reduced two-state dynamic sign screen and strict matrix-assembly code are
  shared in `analysis/flight_dynamics_gate_v2.py` and
  `analysis/linear_mode_solver.py`. The latter has only synthetic unit tests;
  it has not produced V2 eigenvalues because complete physical inputs are
  unavailable. The private Flight Dynamics II scans were used as an evaluator
  checklist and are not redistributable study data.
- No wind-tunnel, structure-load, engine-propeller-map or crewed-flight data
  were generated. The archive does not certify construction or flight safety.
- A Git tag is a fixed source identifier, but a DOI-backed repository deposit
  would improve long-term preservation. No DOI or journal acceptance is implied.

## Suggested manuscript statement

The recovered prompts, historical input packet, language-model outputs,
versioned geometry, figure source data, analysis inputs and outputs, and code
supporting this study are openly available at the fixed repository tag above;
the consolidated archive is `research_evidence.zip` and checksums are in
`MANIFEST.json`. Known unrecovered transport details are documented rather
than reconstructed. Third-party publications and privately supplied teaching
materials cannot be redistributed and are cited in the paper. No physical
flight or wind-tunnel dataset exists for the generated aircraft.
