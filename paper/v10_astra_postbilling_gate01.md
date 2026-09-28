# V10 Astra return after billing recovery: correction, not flight clearance

Author: Ehsan Roohi. Date: 28 September 2026. This is a modern,
researcher-assisted feedback round, not an independent historical-cutoff trial.
It preserves the frozen Astra V10 prompt and source hashes from the original
array. The earlier failures remain separately archived: array task
`65011353_0` had no response and did not retain its HTTP detail; job
`65011846` had no response and recorded HTTP 429
`credit_balance_exhausted`. After a minimal same-credential Astra probe was
accepted, a single new call was submitted as Unity job `65012338` in the
isolated `v10_astra_postbilling_attempt01/` directory. Slurm reports
`COMPLETED 0:0`; the response wrapper reports `completed` and
`gpt-6-astra`. Its raw SHA-256 is
`4bf91701328a2c9a86e39ddb479f2b6d9abfec0f7ba3bc5872a9559eab872387`.
The raw prompt, request, response, outcome and log are preserved. The
independent audit at `analysis/results/v10_astra_postbilling_audit01.json`
passes all provenance and selected arithmetic checks. No credential is
included in the archive.

## What Astra returned

The response calls itself `ASTRA_V3R_CORRECTION_PATCH_1`, but it adopts
**no physical component, coordinate, dimension, mass or power-target change**.
It corrects interpretations and identifies missing interfaces; it is not a
new installed aircraft geometry or a new three-view drawing.

* The assumed high-drag case remains 520 N at 18 m/s. With the *assumed*
  propeller and drive efficiencies 0.55 and 0.95, respectively, the necessary
  engine output is 17,913.876 W. The 18,000 W engine number remains an
  unverified target, only 86.124 W (0.48% of target) above that requirement.
  Our arithmetic audit reproduces these numbers; neither drag nor available
  continuous engine power has been measured.
* Including the tip chord's tangential extent increases the rigid rotational
  radius from 1.200000 to 1.200588 m. The corresponding *level, rigid* ground
  gap is 0.399412 m under the parent hub-height assumption. Loaded flex,
  wheel motion, runout and construction tolerances remain unknown.
* Astra now says the specified fixed/moving surface mapping meets at the
  hinge partition: the nominal 0.01 m manufactured hinge gap was a
  requirement, not implemented geometry. It also observes an unassigned
  0.3 m axial interval between the declared engine envelope and shaft start;
  output flange, coupling and bearing geometry are absent.
* It reports an approximately 0.246 m *surface-only vertical bound* between
  fin and elevator under its mapped travel. That bound is not independently
  checked here and is not a hardware minimum distance or loaded clearance.
* Under an illustrative rigid main-wheel-axle pitch pivot, the declared
  skid is initially grounded and penetrates the ground plane for positive
  nose-up rotation. That is a contact-model warning, not a measured
  operational rotation limit; another contact sequence needs explicit gear
  kinematics and loaded clearances.
* Recomputed pilot/fuel loading states agree with the supplied rounded mass
  ledger to the precision checked. They do not supply a measured CG or inertia
  tensor.

## Gate decision

The response improves the traceable defect list, but **Astra still does not
pass a whole-aircraft flight gate**. A mechanically resolved installation,
continuous installed power/thrust/torque map, whole-aircraft aerodynamic and
control maps, powered and power-off trim, loaded clearances, structural
limits, and installed dynamic derivatives remain unavailable. A conditional
force or clearance formula must not be promoted into evidence of available
power, safe control travel, positive static margin, stable modes or flight.
The next model feedback should request a measurable, mechanically explicit
patch only after these missing interfaces and bounds are supplied; inventing
numbers to force a pass would weaken the aircraft comparison and paper.
