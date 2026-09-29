# Journal of Aircraft conversion and flight-dynamics gate

Author: Ehsan Roohi. Working draft dated 29 September 2026. This is not a
submission-ready or flight-approved aircraft study.

## Model-return status, without conflating completion and validation

| Latest return | Transport completion | Engineering disposition |
|---|---|---|
| Astra V12 | Complete response, SHA-256 `89bce11966d0c8b1b2d5059613c878573a34beaf9e213dd8f712dcdf6582de8a` | The model explicitly returned HOLD. A full installed configuration was not adopted. |
| Fable V13 | Complete response, SHA-256 `dae66235761235d241c8773d9af9c9700187d9920db638a17ce6dcda9bc4b379` | The 354.3 kg ledger and eight load cases reconcile; the model retains a 0.520 kW shortfall against its own assumed heavy-case shaft-power reserve. |
| Opus V12 reviewed replay | Complete response, SHA-256 `96e534daf71329dbfadec507a84ad98ac34a0dc2d156de33b4a5e2f137ee25db` | A 340.3 kg analytical installation candidate and selected rigid-contact arithmetic pass. The earlier 32,000-token return was incomplete, but the separate 48,000-token replay was **complete**. The candidate is not aerodynamically or dynamically validated. |

These statuses are based on the frozen `outcome.json` files, response hashes and
the independent V12/V13 audit scripts. A complete *answer* can be a HOLD, and a
complete design *proposal* can still fail a physical gate.

A further evaluator-only inertia screen recomputed the nominal centroid-only
parallel-axis tensors from the complete Fable V13 and Opus V12 mass ledgers.
Their diagonal components are conditional lower bounds, **not** usable
whole-aircraft moments of inertia: each part's intrinsic inertia is missing.
The inputs, tensors, convention and reproducible script are in
`paper/v14_inertia_gate01.md` and `analysis/results/v14_inertia_lower_bounds01.json`.
No dynamic mode or Flight Dynamics II acceptance follows from this result.

A nominal installation-gap screen independently recomputed six Fable V12
one-axis rigid separations retained by V13, with a 10 mm tank-to-longeron
minimum. Selected Opus V12 gaps of 10--50 mm remain model-reported rather
than independently solid-reconstructed. Neither candidate has a tolerance,
deformation or full swept-clearance budget. See
`paper/v14_static_clearance_budget01.md`; these positive nominal numbers are
not installation acceptance.

The new evaluator-only Fable power–mass calculation independently reproduces
the 0.520 kW shaft reserve deficit. Under the model's unmeasured worst-case
drag/efficiency and 5.1 kg/kW incremental engine-mass assumption, its
self-consistent *paper* target is 20.195 kW (3.543 kg more engine mass), not
an installed power capability. The retained target also implies an internally
inconsistent fuel/endurance calculation. See
`paper/v14_fable_power_fixed_point01.md` and its source-hashed JSON; no
engine or propeller map is thereby validated.

Three V14 full-parent feedback prompts and a hashed runner are frozen in
`v14_integrated_candidate_attempt01/`. Their manifest explicitly reads
`FROZEN_UNSENT`. A read-only SSH diagnostic to Unity failed public-key
authentication in the current environment; no V14 model run has been
submitted or silently inferred from these prompt files.

## Required next coupled design spiral

1. Freeze a single full-aircraft geometry per model, including actual occupied
   component solids, propulsion disk and shaft, truss members, pilot envelope,
   control hinges/stops, gear contacts, and material/load paths. Generate
   source-coordinate three views of **that exact version**. The V2 plates in
   the current article cannot stand in for V12/V13 installed designs.
2. Recompute component mass, all load-case centers of gravity and intrinsic
   plus parallel-axis inertia tensors. Every engine, tank, ballast, tail,
   control or structural change reopens this ledger.
3. Test all rigid and loaded ground-clearance/control sweeps. Opus's V12
   aft-skid positive gaps do not establish nose-down or deflected clearance;
   Fable's corrected centroid does not establish a clash-free installation.
4. Obtain a bounded, defensible installed drag/lift/moment model and an
   engine torque--speed/propeller thrust--power operating map. Paper engine
   targets and assumed efficiency are requirements, not available power.
5. Solve powered and power-off six-component trim across minimum, nominal and
   maximum speed and forward/aft CG. Report vertical and axial force and
   three moment residuals, control positions, stall margin, power reserve and
   structural loads. Repeat if the design changes.
6. For each accepted trim, establish full-aircraft static derivatives and
   the Flight Dynamics II longitudinal and lateral/directional rate and
   unsteady derivatives. In particular, do not silently set
   $C_{m_{\dot\alpha}}$ or $C_{Z_{\dot\alpha}}$ to zero; quasi-steady AVL
   output does not identify them. Validate intrinsic inertia and assemble the
   dimensional equations before computing short-period, phugoid, Dutch-roll,
   roll and spiral modes with uncertainty. A static margin or reduced two-state
   sign test is not a substitute.
7. Only after these numerical gates should any claim of a *conditionally
   flight-capable analytical design* be made. Physical airworthiness and
   occupied flight additionally require material tests, engine/propeller
   tests and a qualified staged flight-test program.

The current data do not clear steps 1--6 for any revised design. Therefore
the paper can presently report a rigorous design-audit and feedback study,
not three demonstrated stable flying airplanes. The historically flown Wright
Flyer I remains a different evidence class; its reconstructed numerical
comparator also requires a sourced CG and matched flight condition.

## Journal conversion done in the local draft

`paper/article_journal_of_aircraft.tex` preserves the technical discussion
but uses the AIAA minimum 10-point, US-letter, single-column, double-spaced
review format. Its 9-word title and 176-word self-contained abstract fit the
current author guidance. The seven main-figure captions are at most 25 words;
long mechanism explanations remain in the text. The bibliography has been
mechanically reordered by first citation. A nomenclature, data/code access
statements and a dedicated Acknowledgments/AI-use disclosure are present.
The three V2 three views are presented as landscape figures, and four
typographically enlarged 5400-by-2340-pixel derivatives are archived with
their source hashes. This is *not* a claim that V12/V13 geometry has been
rendered or validated.

## Remaining submission checks

An initial bibliography/length audit is recorded in
`paper/joa_editorial_gate01.md` and `analysis/results/joa_editorial_gate01.json`.
It found 40 citation-ordered entries and about 12,637 words in named main
sections. The 53-author FAIR entry has been expanded, removing the remaining
``et al.'' from the reference list. The three V2 and four Roskam entries noted
there have been partially repaired, not comprehensively cleared.

- Compile and visually inspect every page using a TeX installation or
  Overleaf. No local TeX compiler was available at this stage. The ZIP was
  checked for completeness and integrity, not compiled.
- Audit each reference against AIAA style, complete author lists, publication
  data, first-source status and reliable archiving. Some inherited entries are
  collection/catalog or website records rather than archival research items.
- Reduce the working main text: the editorial source screen finds about 12,637
  English/alphanumeric words in the six named main sections (13,212 including
  other article text), before equivalent space for seven figures and three
  tables, above AIAA's roughly 10,000--12,000-word regular-paper guideline.
  Preserve detailed mechanisms and audit tables in a self-contained
  supplement rather than deleting evidence.
- Check every raster line-art figure at its final placed width. All six main
  line-art figures now pass a conservative 600-ppi source screen at the stated
  widths; the redrawn V2 force/moment plate is about 923 ppi with body text
  approximately 8.2 pt. All nine supplementary line-art PNGs now also pass
  the pixel-density screen after source-SVG re-rasterization, but the dense V0
  oblique plates have some explicit labels capped at 6.31 pt (Astra), 6.88 pt
  (Fable) and 6.02 pt (Opus) even at maximum A4 landscape width, before the
  height cap. The immutable full plates retain these labels; three additional
  researcher-created, numbered detail crops with adjacent readable keys make
  the mechanisms and unknowns inspectable at print size without silently
  revising V0 geometry. Their marker-size screen is only an upper bound.
  See `paper/joa_figure_gate01.md`. All figures require actual
  PDF-page inspection.
- Verify permission and attribution for the Wright photograph and any reused
  source artwork. Verify all funding, conflict and author-affiliation fields;
  the draft deliberately does not invent them.
- The draft data statement points to the G8 research tag, which contains the
  audited calculations and numbered V0 detail assets and clearly marks V14
  `FROZEN_UNSENT`. This fixed
  draft tag is not the final submission deposit; update the statement again
  after the remaining scientific and journal gates are cleared.
- The AIAA policy requires disclosure of research AI and AI-assisted writing
  or figure preparation in the manuscript and ScholarOne. The current draft
  contains an AI statement; the submitting author must make the corresponding
  ScholarOne disclosures. AIAA frames manuscript-writing assistance primarily
  as readability/grammar/language support; the author must critically rewrite
  and verify any AI-drafted scientific argument, not merely approve it by
  silence.

Official guidance consulted: [AIAA Journal Author](https://aiaa.org/publications/journals/journal-author/),
[Journal Scopes and Content](https://aiaa.org/publications/journals/journal-scopes-and-content/),
[Figure and Table Guidelines](https://aiaa.org/publications/journals/journal-author/guidelines-for-journal-figures-and-tables/),
[Reference Style](https://aiaa.org/publications/journals/reference-style-and-format/), and
[Publication Ethics and AI](https://aiaa.org/publications/Publish-with-AIAA/Ethical-Standards-for-Publication-of-Aeronautics-and-Astronautics-Research/).
