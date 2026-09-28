# Historical aircraft design with language models

**Author: Ehsan Roohi**

Versioned research on three aircraft proposals produced under a documentary cutoff of **31 December 1898**, followed by clarification, independent evaluation and model revision. The model identifiers in the archived runs are `gpt-6-astra`, `claude-fable-5-1` and `claude-opus-5-5`.

The cutoff constrains supplied documents, not the models' training knowledge. Modern evaluator feedback is distinguished from the historical input packet. This repository is a work-in-progress research record, not a journal acceptance or a build/flight authorization.

## 28 September 2026 manuscript and fixed research snapshot

The [revised Scientific Reports-targeted source](paper/article_scientific_reports.tex), [supplement](paper/supplementary_scientific_reports.tex), [Data Availability inventory](paper/DATA_AVAILABILITY.md), and [latest Overleaf ZIP](scientific_reports_aircraft_overleaf_release06.zip) accompany the fixed tag `aircraft-sr-2026-09-28-r4`. The paper distinguishes Astra/Opus independent V2 force and moment balances from Fable's unverified model claim in a [three-case force plate](figures/v2_force_moment_comparison.png). Table 2 is explicitly V1. The two-mesh quasi-steady screen reports [fine](analysis/results/v2_rate_derivatives/fine.json) and [coarse](analysis/results/v2_rate_derivatives/coarse.json) pitch-rate derivatives for Astra and Opus; the first failed memory-allocation attempt is preserved. A [new dynamic gate](analysis/results/v2_dynamic_gate01.json) checks only the signs of a deliberately reduced two-state pitch model. Angle-of-attack-rate derivatives and installed-aircraft eigenmodes remain unresolved.

The `research_evidence.zip` snapshot contains **all locally recovered** prompts, responses, model attempts, code, figures, and selected numerical records in the stated project scope. Its 2,815 paths have per-file SHA-256 hashes in [MANIFEST.json](MANIFEST.json); the ZIP checksum is in [research_evidence.zip.sha256](research_evidence.zip.sha256). The archive does not claim recovery of unrecorded service-side transport or include third-party lecture/book PDFs. No DOI has been assigned.

The [integrated flight-dynamics redesign plan](paper/dynamic_design_next_loop.md) specifies the missing inertia, unsteady derivatives, full longitudinal/lateral modes and control/propulsion gates. [Case-specific prompts](analysis/prompts_v9_integrated_dynamics/manifest.json) were submitted to Astra, Fable and Opus as Unity array `65007436`. At this snapshot the array was queued by `MaxCpuPerAccount`; **there are no V9 model answers or independently accepted V9 designs yet**. These later modern-feedback requests do not alter the original information-cutoff experiment.

The [V1/V2 pitch comparison](analysis/results/v1_v2_pitch_gate_comparison01.json) adds the original-design rate-derivative run. Astra V1 has a destabilizing static pitch slope but passes only the simplified two-state sign test; this is not a full dynamic verdict. Opus V1 also passes that narrow sign test, and Fable has no mechanically admissible independently evaluated trim. The V1 run is single-mesh and is not a physical stability measurement.

## Current result

**The fourth comparator is the original 1903 Wright Flyer I.** Its documented historical flight is distinct from our incomplete numerical reconstruction. The [four-aircraft comparison](paper/four_aircraft_comparison.md) includes dimensional Wright loads, pitch-slope calculations and discussion of configuration, structure, controls and propulsion. [Machine-readable comparison](analysis/results/four_aircraft_comparison01/summary.json).

Independent simplified longitudinal trim was found for Astra and Opus V2. This does **not** demonstrate real flight, complete stability, structural adequacy, engine capability, or superiority over the Wright Flyer. Fable V2 remains geometrically unresolved. See the [trim assessment](paper/v2_trim_assessment.md) and [stage register](paper/stage_registry.md).

## Three-view sheets

These are coordinate-based engineering schematics, not photorealistic illustrations or construction drawings. Unspecified parts are omitted and disclosed. V1 shows evaluator lifting surfaces; V2 adds declared structural chains, fins and propeller discs. Reference geometry is shown at neutral controls; numerical trim settings are recorded separately.

| Model | V1 | V2 |
|---|---|---|
| Astra | [Three views](output/stage_threeviews/V1/gpt-6-astra.svg) | [Three views](output/stage_threeviews/V2/gpt-6-astra.svg) |
| Fable | [Three views](output/stage_threeviews/V1/claude-fable-5-1.svg) | [Unresolved geometry](output/stage_threeviews/V2/claude-fable-5-1.svg) |
| Opus | [Three views](output/stage_threeviews/V1/claude-opus-5-5.svg) | [Three views](output/stage_threeviews/V2/claude-opus-5-5.svg) |
| Wright Flyer I (1903) | [Reference three views](output/stage_threeviews/Wright/wright-flyer-1903.svg) | Historical comparator, not an LLM revision |

![Wright reference reconstruction](output/stage_threeviews/Wright/wright-flyer-1903.png)

![Astra V2](output/stage_threeviews/V2/gpt-6-astra.png)
![Fable V2](output/stage_threeviews/V2/claude-fable-5-1.png)
![Opus V2](output/stage_threeviews/V2/claude-opus-5-5.png)

## Evidence and reproducibility

[Download the complete selected research evidence](research_evidence.zip) and verify its individual files against [MANIFEST.json](MANIFEST.json). Extract at the repository root to restore the recorded paths. The archive includes original V0 drawings, recovered prompts, V1/V2 responses, local analysis code, numerical inputs/outputs, rejected/failed attempts and dated methodological notes. Key current code and reports are also directly browsable. The archived original responses remain unchanged. Earlier notes may be superseded; consult the stage register for current status.

Python 3 with NumPy is required for the current calculations and vector drawings. To reproduce the drawings after extracting the evidence:

```sh
python analysis/draw_stage_threeviews.py
python -m unittest discover -s analysis -p test_stage_threeviews.py
python analysis/v2_trim_report.py
python analysis/wright_fourway_assessment.py
```

The optional Node preview renderer uses Sharp; its current local dependency path is host-specific and must be adapted on another machine. SVGs remain portable vector masters. AVL 3.52 is not redistributed; obtain it separately and set the executable path in the analysis code. Numerical run scripts use exclusive output-directory creation to protect archived runs: choose new output paths rather than overwriting results. Cross-platform solver reproduction is not yet verified.

The Wright sheet depicts reconstructed lifting surfaces, not complete rudder/propeller/airframe geometry. Its red cross marks a moment reference, **not a verified historical CG**. The approximately -22% slope descriptor therefore must not be quoted as the Flyer's established static margin. Positive AI local slope ratios are not proof of superiority over the Flyer.

## Constraints and exclusions

Unknown geometry, drag components, engine curves, material allowables and inertias are explicitly recorded rather than filled with unmarked assumptions. The trim report distinguishes aerodynamic restoring slopes from complete powered-aircraft static margins. No occupied testing is authorized by this work.

Books (including Roskam and Malaek scans), downloaded journal PDFs, personal files, credentials, temporary folders and solver executables are excluded. No general reuse license has yet been assigned; public visibility does not imply unrestricted reuse. Source attribution and rights remain attached to the relevant records.
