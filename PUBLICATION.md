# Public research snapshot

## 28 September 2026 V3 power gate and V10 correction returns

The source-hashed power screen and its tests are published as
`paper/v3_power_necessity_gate01.md` and
`analysis/audit_v3_power_necessity.py`. Three case-specific V10 feedback
requests, frozen instructions/manifest, one-call Slurm runner, raw
request/response/outcome records and a separate one-time Astra retry
are included as individual repository paths. Fable and Opus completed;
their parent hashes and selected mass/power/ground-contact arithmetic
were independently checked in `analysis/results/v10_response_audit01.json`.
Astra returned no design: the first call recorded only `RuntimeError`,
and the reviewed lower-cap retry identified API HTTP 429 insufficient
quota. No further call was made. Model-authored corrections do not
establish measured engine capability, installed trim, stability modes
or flight clearance. The fixed `research_evidence.zip` remains the
prior r5 snapshot; these newer direct files are not claimed to be in it.

## 28 September 2026 V3 geometry/loading gate 01

The directly browsable `paper/v3_geometry_loading_gate01.md`,
`analysis/audit_v3_geometry_loading.py`, its tests and JSON result record a
limited independent arithmetic/conditional-geometry check of all three
V3 model replies. Fable's 65/85 kg pilot CG-percent claims fail recomputation
from its ledger, while Opus's reported 13-degree fin/ground gap is contingent
on an aft-skid contact pivot. Necessary whole-aircraft vertical-force
coefficients are requirements, not achieved lift or trim. All three designs
remain on HOLD before independent V3 trim. No flight-capability claim is made.
The `research_evidence.zip` is the prior fixed r5 snapshot; the new gate
files are available individually and not misrepresented as inside that ZIP.

## 28 September 2026 integrated-feedback return

Fixed tag `aircraft-sr-2026-09-28-r5` adds complete V3 model responses, separately retained 20,000-token Fable/Opus truncations, the 48,000-token retries, a hash-and-mass-arithmetic audit, and Overleaf release07 with Supplementary Table S11. The archive includes all five raw V9 response records with prompts, request metadata, outcomes and checksums. The three V3 mass ledgers close arithmetically; Fable's model-supplied nominal force and moment sums also close. No installed propulsion, full trim, unsteady derivatives, dynamic modes, structure or flightworthiness has been validated. V3 three-view drawings remain pending independent coordinate and clearance checks. The paper continues to identify Opus as strongest only among initial V1 proposals on its restricted screen, and Astra as strongest only in the conditional V2 longitudinal comparison.

The reviewed `research_evidence.zip` contains 2,852 selected paths and excludes third-party PDFs, course scans, credentials and solver binaries. `MANIFEST.json` provides per-file SHA-256 hashes. The Overleaf ZIP is `scientific_reports_aircraft_overleaf_release07.zip`; static package checks passed, but local TeX compilation and visual proof were unavailable at publication time. No DOI, journal acceptance, aircraft construction or flight approval is claimed.

## 28 September 2026 tagged revision

The updated fixed tag `aircraft-sr-2026-09-28-r4` adds the reduced dynamics sign audit, its explicitly limited manuscript discussion, a strict but not-yet-applied full-mode matrix assembler, case-specific integrated-redesign prompts, and Overleaf release06. The reviewed `research_evidence.zip` contains 2,815 selected paths and is accompanied by a per-file SHA-256 manifest and a ZIP checksum. Included are all locally recovered prompts and model outputs in the listed project directories, plus later archived feedback attempts, code, figure data, accepted calculations and failed runs. It excludes copyrighted course/book PDFs, credentials and external solver binaries. No DOI, physical flight demonstration or journal acceptance is claimed.

The force/moment figure gives conditional Astra/Opus V2 values but marks Fable V2's values as model claims. A quasi-steady AVL run at two meshes provides restricted Astra/Opus pitch-rate derivatives; the original memory-allocation failure is archived. Both pass an omission-based two-state pitch sign test. This is **not** a physical short-period, phugoid or lateral stability result. Angle-of-attack-rate derivatives remain unavailable without an unsteady/downwash-delay model, and incomplete structure, inertia and control inputs prevent a dynamic-stability verdict. Unity array 65007436 was submitted with one bounded V9 redesign request per model; at this snapshot it was queued for account CPU capacity, so no V9 responses are represented as completed.

The r4 addition tests the archived V1 trim inputs with the same AVL rate-derivative command. Astra V1 has positive static pitch slope yet passes only the deliberately reduced two-state sign algebra; Opus V1 also passes that narrow algebra. No full dynamic modes are claimed, and Fable remains outside the admissible trim screen. The V1 calculation has one panel mesh and is labelled accordingly in the paper and supplement.

Published with explicit author approval to Ehsan-Roohi/historical-aircraft-llm, 27 September 2026.

The release02 evidence archive contains 1,248 selected files (4,178,034 bytes). Its Git blob SHA was verified against the local archive: b543559b2ff0a3ae9fbcfe23744d2e2077addcd8. The accompanying SHA-256 file and per-file MANIFEST support independent checking.

Seven source-hashed three-view sheets cover Astra/Fable/Opus V1 and V2 plus the partial Wright Flyer I reference reconstruction. Four drawing tests and two four-aircraft postprocessing tests passed. Key current scripts and reports are browsable; the complete selected record is in the ZIP. Extract it to restore source paths.

Earlier dated publication-status notes inside the immutable archive record historical blocks, not current publication status. No book/PDF scans, solver executables, credentials or personal files are included. This is a work-in-progress research snapshot, not proof of flight capability or a final journal submission.
