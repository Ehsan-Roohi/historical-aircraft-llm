# Data and code availability for the aircraft-LLM study

Author: Ehsan Roohi. Current public research tag: `aircraft-ast-2026-09-28-g5`
in [`Ehsan-Roohi/historical-aircraft-llm`](https://github.com/Ehsan-Roohi/historical-aircraft-llm/tree/aircraft-ast-2026-09-28-g5).
The earlier R5 snapshot is preserved in `research_evidence.zip` and
`MANIFEST.json`; those two files **do not** purport to index all later V10--V11b
additions. Later paths have their own frozen manifests, source indexes and
response hashes. A Git tag identifies a fixed commit. No DOI is claimed.

## What the public archive contains

| Research material | Public path (R5 ZIP where applicable; later additions are direct repository paths) | Use and interpretation |
|---|---|---|
| Original historical packet and initial prompts | `analysis/prompts_v0/` | Actual supplied text; a source-date restriction, not a model-training cutoff. |
| Initial V0 outputs and model-authored drawings | `received_2026-09-24/astra_fable_opus_designs/`, plus preserved raw records in `analysis/results/` | Original proposals, including inconsistencies. |
| Clarification prompts and V1 returns | `analysis/prompts_v1/`, `analysis/raw_v1/`, `analysis/results/` | Complete recovered attempts and separate truncation/failure records where retained. |
| Revision prompts and V2 returns | `analysis/prompts_v2/`, `analysis/prompts_v2_retrim/`, `received_v2_64942345/prompts/`, `received_v2_64942345/responses/`, `analysis/results/received_v2_audit01/` | Model-authored revisions, not automatically verified designs. |
| Later model feedback exchanges | `received_v5_64962376/responses/`, `design_revision_v6_attempt01/responses/`, `unity_jobs/`, `analysis/results/` | Archived subsystem/revision attempts; do not silently treat them as a new integrated flightworthy aircraft. |
| Integrated dynamic redesign feedback | `analysis/prompts_v9_integrated_dynamics/`, `received_v9_65007436/`, `received_v9_retry_65009709/`, `unity_jobs/`, `analysis/results/v9_integrated_response_audit.json` | Three complete V3 returns with the original token-truncated Fable/Opus attempts retained separately. The audit verifies response/prompt hashes and mass arithmetic, not flight dynamics or flightworthiness. |
| V10 corrected geometry/power responses | `received_v10_65011353/`, `received_v10_astra_retry_65011846/`, `received_v10_astra_postbilling_65012338/`, `analysis/prompts_v10_geometry_power/`, `paper/v10_response_gate01.md`, `paper/v10_astra_postbilling_gate01.md` | Direct post-R5 paths. They retain quota failure and later completed Astra response separately; no V10 output validates flight. |
| V11a/V11b design-candidate cycle | `v11_design_candidate_attempt01/`, `v11b_design_candidate_attempt01/`, `analysis/prompts_v11_design_candidate/`, `analysis/prompts_v11b_context_restored/`, `analysis/results/v11_feedback_audit01.json`, `analysis/results/v11b_engineering_gate01.json`, `paper/v11_design_candidate_gate01.md` | Direct post-R5 paths. V11a's omitted source texts and all three HOLD responses are retained. V11b restores full sources; Fable's conditional seat/gear candidate and both remaining HOLDs are independently screened. |
| Geometry and figure source/output | `output/stage_threeviews/`, `output/figures_v2/`, `output/overleaf/scientific_reports_aircraft_2026_09_28_release03/figures/`, `analysis/` | Original and evaluator drawings have distinct provenance. Figure 7 uses the archived numerical results; Fable's values are model claims. |
| Numerical inputs and outputs | `analysis/results/`, `output/overleaf/scientific_reports_aircraft_2026_09_28_release07/audit_data/` | Includes accepted and failed cases, mesh checks, residuals, both failed and completed rate-derivative runs, the reduced dynamic gate, and the limited V3 mass/force arithmetic audit. |
| Analysis and manuscript source | `analysis/`, `paper/`, `output/overleaf/scientific_reports_aircraft_2026_09_28_release07/` | Human-auditable code, TeX, supplement, references, and selected source records; the full-mode assembler is not run on incomplete V2/V3 data. |

## Journal data-statement mapping

For the current Aerospace Science and Technology target, the submission must
give a truthful research-data statement pointing to the frozen public inputs,
raw model outputs, figure sources, code, and independent checks. Elsevier's
[data-statement guidance](https://www.elsevier.com/researcher/author/tools-and-resources/research-data/data-statement)
explains that availability and reasons for restrictions should be declared;
the journal-specific Guide for Authors should be rechecked at submission.
The earlier Scientific Reports mapping remains relevant only if that venue is
reconsidered.

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
- The V1 rate-derivative rerun and V1/V2 sign comparison are recorded in
  `analysis/results/v1_rate_derivative_screen01/` and
  `analysis/results/v1_v2_pitch_gate_comparison01.json`. V1 uses one panel
  mesh only and is a qualified numerical comparison, not independent
  whole-aircraft dynamic validation.
- The integrated V3 calls and separate high-token retries are recorded in
  `received_v9_65007436/` and `received_v9_retry_65009709/`. The final
  Fable and Opus responses ended normally; their earlier 20,000-token
  attempts did not. The three mass ledgers close arithmetically, and Fable's
  stated nominal lift and moment sums close only for its assumed forces.
  No V3 model supplies independently verified trim, installed unsteady
  derivatives or full dynamic modes. Source and interpretation are detailed
  in `paper/v9_integrated_response_gate.md`.
- No wind-tunnel, structure-load, engine-propeller-map or crewed-flight data
  were generated. The archive does not certify construction or flight safety.
- A Git tag is a fixed source identifier, but a DOI-backed repository deposit
  would improve long-term preservation. No DOI or journal acceptance is implied.

## Suggested manuscript statement

The recovered prompts, historical input packet, language-model outputs,
versioned geometry, figure source data, analysis inputs and outputs, and code
supporting this study are openly available at the fixed repository tag above.
The earlier R5 consolidated archive and checksum manifest remain available;
later V10--V11b exchanges are provided as individually hashed repository paths.
Known unrecovered transport details are documented rather than reconstructed.
Third-party publications and privately supplied teaching materials are cited
but not redistributed. No physical flight, wind-tunnel or installed
engine--propeller measurement dataset exists for the generated aircraft.
