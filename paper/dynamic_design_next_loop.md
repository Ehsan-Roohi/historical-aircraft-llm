# Flight-dynamics design loop after V2

Author: Ehsan Roohi. Status: engineering work plan, **not** flight approval.

The privately supplied Flight Dynamics II notes (CH4, pp. 54--65 and 72--84)
form the checklist for the evaluator. They were not part of the pre-1899
information supplied in the initial language-model experiment. Do not upload
the copyrighted scans to the public research archive.

## Evidence already computed

| Candidate | Frozen input | Result | What it does not establish |
|---|---|---|---|
| Astra V2 | Independent 18 m/s conditional trim, lifting-surface derivatives at two meshes | $C_{m_\alpha}=-0.8130$ per rad, $C_{m_q}=-4.7059$, reduced $\alpha$--$q$ sign test conditional pass | Physical short-period mode, phugoid, installed directional stability, pilot response, flight |
| Opus V2 | Independent 15 m/s conditional trim, same method | $C_{m_\alpha}=-0.2864$ per rad, $C_{m_q}=-6.6458$, reduced sign test conditional pass | Same missing whole-aircraft evidence |
| Fable V2 | Model claims and partial later subsystem outputs | No admissible independent full-aircraft trim or dynamic screen | All dynamic modes |

A separate later check of the initial V1 trims found Astra
$C_{m_\alpha}=+0.3483$ per rad and $C_{m_q}=-5.7865$, while Opus has
$-0.1921$ and $-6.5909$, respectively. Thus Astra V1 has the wrong local
static pitch-slope sign, but the deliberately reduced two-state Hurwitz
sign test still passes there; a negative $C_{m_q}$ can offset that slope
in the simplified algebra. This does not establish full dynamic stability.
Fable V1 cannot be screened at its mechanically conflicting trim. The
versioned comparison is in
`analysis/results/v1_v2_pitch_gate_comparison01.json`; its V1 AVL rate
run is single-mesh, not a convergence study.

The sign screen is precisely `analysis/flight_dynamics_gate_v2.py` and its
machine-readable result is `analysis/results/v2_dynamic_gate01.json`. The
calculation intentionally has no eigenvalue or damping-ratio output. Complete
pitch inertia is unknown; centroid-only parallel-axis values are lower bounds,
not usable substitutes for the full tensor. Small or zero AVL yaw derivatives
arise in a lifting-surface model missing the fin and body and must not be
interpreted as measured installed-aircraft directional stability.

`analysis/linear_mode_solver.py` implements the four-state longitudinal and
lateral matrix algebra with strict required-field checks. Its tests use
synthetic arithmetic fixtures only. It is deliberately **not run on V2**:
supplying guessed zeros for unmeasured derivatives would generate attractive
but physically uninterpretable eigenvalues. For later use, the input variables
are dimensional and their governing equations are in the module docstrings;
normalization from measured or independently modeled coefficients must be
audited before calling the solver.

## Next frozen design return required from each model

1. **One integrated revision**, with explicit parent version, changed parts,
   orthographic three views, source coordinates, units, and no invented
   equivalence between later subsystem attempts and a complete V3 aircraft.
   For Fable, reconcile the tail sweep, fuel-box/centroid and propeller/brace
   topology before aerodynamic evaluation.
2. **Mass and inertia ledger:** all component masses, *three-dimensional
   material distributions or calculable primitive shapes*, position/orientation,
   loaded/fuel-extreme CGs and component intrinsic inertia tensors. Supply
   uncertainties. A mass centroid alone cannot determine $I_{xx},I_{yy},I_{zz}$
   or $I_{xz}$. Recompute the summed inertia tensor about each CG.
3. **Installed geometry and controls:** complete vertical surfaces and body,
   pilot, propeller disks and shafts, finite control surfaces and their hinges,
   throws, rate limits, linkage sense, stops, clearances and load paths.
   Avoid claiming control authority from a visual arrow.
4. **Power and trim:** engine torque--speed curve, propeller pitch/diameter/rpm
   and efficiency or test map, installation losses, drag build-up and uncertainty.
   Demonstrate both power-on and power-off trim across specified speeds and CG
   limits, with force/moment residuals, stall/ground clearance and control
   limits checked at each state.
5. **Derivative data contract:** at each trim, retain perturbation size, axis,
   sign, held controls, units, full-aircraft $C_{X_u}, C_{X_\alpha},
   C_{Z_u},C_{Z_\alpha},C_{Z_q},C_{Z_{\dot\alpha}},C_{m_u},
   C_{m_\alpha},C_{m_q},C_{m_{\dot\alpha}}$; lateral
   $C_{Y_\beta},C_{Y_p},C_{Y_r},C_{l_\beta},C_{l_p},C_{l_r},
   C_{n_\beta},C_{n_p},C_{n_r}$; and each installed control and propulsion
   derivative. A steady vortex-lattice result does not fill unsteady fields.
6. **Independent evaluator computation:** with validated inputs, assemble
   dimensional longitudinal and lateral equations and compute eigenvalues,
   natural frequencies, damping, real-pole time constants and mode shapes.
   Check power-on/off, minimum/nominal/maximum speed, forward/aft CG and
   aerodynamic/propulsion uncertainty. Investigate any unstable mode against
   control effectiveness, rate, delay, saturation and pilot workload; do not
   hide it by quoting a static margin.
7. **Material change requires another loop.** A larger fin, tail, ballast,
   engine or altered control linkage changes mass, drag, trim, inertia and/or
   derivatives. Re-run all coupled checks on the revised frozen geometry.

## Decision rule

The paper may report a *conditional numerical dynamic screen* when its
assumptions and input uncertainty are explicit. A claim that a complete
aircraft meets the flight-dynamics requirements needs independently checked
longitudinal and lateral modes across a declared envelope and usable controls
under realistic limits. Flightworthiness additionally needs physical
structural, engine/propeller and staged flight-test evidence under competent
safety oversight. A language model's own assurance is not such evidence.

External methodological sources: [MIT AVL User Primer](https://web.mit.edu/drela/Public/web/avl/AVL_User_Primer.pdf)
(quasi-steady solver scope), [FAA AC 23-8C](https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/1019676)
(flight-test interpretation of dynamic stability), and
[FAA AC 90-89C](https://www.faa.gov/airports/resources/advisory_circulars/index.cfm/go/document.information/documentID/1041650)
(individualized experimental flight-test plans). These modern resources are
evaluation guidance, not historical model inputs or approval of this design.
