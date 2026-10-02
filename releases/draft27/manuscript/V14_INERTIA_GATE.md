# Evaluator-only inertia screen for the latest mass ledgers

This is a calculation from **model-declared component masses and centroids**, not a measured moment-of-inertia test or an accepted Flight Dynamics II model. No V14 model response is involved. The source files and SHA-256 identifiers are recorded in `analysis/results/v14_inertia_lower_bounds01.json`; the reproducible calculation is `analysis/audit_v14_inertia_lower_bounds.py`.

For component masses $m_i$, declared centroids $\mathbf r_i$, and the resulting whole-aircraft centroid $\mathbf r_G$, the evaluator forms

$$\mathbf J_{\mathrm{parallel}}=\sum_i m_i\left[(\mathbf d_i\cdot\mathbf d_i)\mathbf I-\mathbf d_i\mathbf d_i^T\right],\qquad \mathbf d_i=\mathbf r_i-\mathbf r_G.$$

The tensor uses axes $(x,y,z)$ in each model's stated coordinate frame, with off-diagonal entries $-\sum_i m_i d_{i,j}d_{i,k}$. The result is invariant to translating the coordinate origin. If the declared centroids and masses are correct, the actual inertia tensor would be $\mathbf J_G=\mathbf J_{\mathrm{parallel}}+\sum_i\mathbf J_{i,\mathrm{intrinsic}}$; the unreported intrinsic-component sum is positive semidefinite. Thus the printed matrix is a **conditional positive-semidefinite matrix lower bound**, not a physical inertia tensor. Its diagonal entries are conditional lower bounds, but its individual off-diagonal entries are not numerical lower bounds on the corresponding actual entries.

| Latest ledger | Mass (kg) | CG $(x,y,z)$ (m) | $J_{xx,\mathrm{parallel}}$ | $J_{yy,\mathrm{parallel}}$ | $J_{zz,\mathrm{parallel}}$ | $J_{xz,\mathrm{parallel}}$ |
|---|---:|---|---:|---:|---:|---:|
| Fable V13, 26 rows | 354.3 | $(1.530739,0,0.792233)$ | 282.406 | 522.525 | 668.278 | $-16.300$ |
| Opus V12, 30 rows | 340.3 | $(0.703552,0,0.501227)$ | 131.713 | 914.293 | 782.580 | $-99.902$ |

Inertia units are kg m$^2$. These values contain only the spread **between** component centroids; for example, the dimensions and mass distributions of wing spars, pilot, engine, propellers, fuel, skids and shafts inside their own component envelopes are not supplied to the precision needed here. The Fable and Opus zero $J_{xy}$ and $J_{yz}$ values reflect their declared laterally symmetric ledger stations, not a measured symmetric aircraft.

Astra V12 returned HOLD and adopted no installed mass ledger, so no corresponding tensor is reported. The inertia screen does not identify the unknown aerodynamic rate/unsteady derivatives, a powered or unpowered six-component trim, or any longitudinal or lateral/directional eigenmode. In particular, substituting these centroid-only tensors into a modal solver would create false precision. The next design revision must provide component geometry and intrinsic inertia estimates with uncertainty, then recompute the ledger and derivatives together; any changed engine, ballast, pilot position or structure invalidates the present conditional numbers.
