# G8 figure-readability draft gate

The G8 delta adds three eight-marker, researcher-created V0 mechanism details
to the immutable G7 research record. The model-authored full plates and their
SHA-256 values are unchanged. `analysis/audit_joa_release_g8.py` checks each
source/detail SHA, packaged SVG and PNG, caption/key placement, ZIP integrity,
V14 `FROZEN_UNSENT` status and the existing provenance/credential screen.
The machine-readable result is `analysis/results/joa_release_g8_gate01.json`.

The detail views hide archival prose and crop the existing coordinate drawing;
they are **not** new model answers, repaired control mechanisms or installed
V12/V13 geometry. Their eight numerical markers map to adjacent prose. The
full V0 plates remain in the supplement and public source archive, including
their small original labels. All nine supplementary line-art rasters pass a
600-ppi width screen, but actual TeX placement and page readability still
require PDF proof. Bibliographic, image-rights and scientific acceptance
gates from G7 remain open. No candidate is demonstrated flight-capable.

For a package-level reproducibility check, the six included Node/Sharp
renderers were run from `figure_sources` with a separate output directory.
All 15 resulting PNGs matched the packaged figure PNGs byte-for-byte by
SHA-256 in this environment. This checks deterministic rendering here, not
cross-platform font substitution or compiled-page appearance.
