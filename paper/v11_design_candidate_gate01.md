# V11 design-candidate feedback: source restoration and independent gate

Author: Ehsan Roohi. Date: 28 September 2026. This is a modern,
researcher-assisted round, not a new historical-cutoff trial. No response is
evidence of flight, construction safety, measured stability or installed power.

## Two attempts, both retained

Unity array `65012607` submitted one bounded call per model. The V11a prompt
specified only the SHA-256 of each earlier response and a short evaluator
summary, but omitted its full component and mass records. All three models
returned `HOLD`; none adopted a physical revision. This was a **prompt-context
failure by the evaluator**, not a design failure of the models. Its prompt,
parent hashes, three raw responses and outcomes are retained at
`v11_design_candidate_attempt01/`. The frozen manifest SHA-256 is
`62f43b4a7d946fdded2f917ee5fde062b7175afcfd6e093003c3ebc9d7ca8f57`.

The corrected V11b request, array `65012688`, included each model's complete
archived V3 baseline response and V10 correction text, plus the targeted V11
engineering question. `analysis/prompts_v11b_context_restored/source_index.json`
maps those source wrappers to hashes; the entire composed prompts, parents,
responses, outcomes and Slurm logs are retained at
`v11b_design_candidate_attempt01/` and `unity_jobs/`. The second manifest hash
is `52b070610b711433e6d84ad2ff45af226b4ff92f108034e7b40eab6e443d9404`.
The response transport statuses were all `completed`. The independent
`analysis/audit_v11_feedback.py` check passes prompt, parent, baseline,
instruction, request and response hashes, confirms that both V3 and V10 text
was actually present in every V11b prompt, and parses all six outputs as JSON.

## Candidate dispositions

| Model | V11b response | Independent reading |
|---|---|---|
| Astra | `HOLD`; no changed component | The source ledger is now available, but truss, bracing, remote controls and gear remain inertia/envelope proxies. A minimal coupling/hinge/skid fix cannot be checked against occupied solids or loaded motion. This is a real geometry-definition gate, not the V11a missing-context problem. |
| Fable | Conditional **candidate**, three changed/defined entries | A proposed 0.3 kg hard seat-stop assembly restricts seat datum to x=0.20--0.30 m, and a new assumed 0.25 m wheel radius plus axle coordinates make the three stated wheel-contact points internally interpretable. Parent gear mass is subdivided without changing its first moment. This is a design assumption, not measured hardware or flight acceptance. |
| Opus | `HOLD`; no changed component | The reply flags unresolved engine-bay occupied geometry, skid endpoints/contact load sharing and a high-case power deficit. It also makes two minor geometric-arithmetic errors described below; its box-overlap claim cannot establish a physical collision if the ledger shapes are inertia proxies. |

Fable's proposed 23-row-parent-plus-stop ledger was independently recomputed
for eight pilot/seat/fuel cases by `analysis/audit_v11b_engineering.py`.
All masses match exactly and each reported CG coordinate differs by less than
0.001 m after rounding. Nominal mass and x-CG become 309.8 kg and 1.5312 m;
the light/aft/empty and heavy/forward/empty limits are 283.8 kg at x=1.5854 m
and 303.8 kg at x=1.4728 m, respectively. The gear subitems sum to 12 kg
and x-CG 1.50 m. This establishes **ledger consistency only**. It does not
establish a measured neutral point: the response's approximate 5.3% aft
static-margin value subtracts its CG from an unvalidated parent estimator.
Seat-stop strength, pilot reach, and loaded propeller/longeron gaps remain
unknown.

Fable's assumed nominal 426 N at 13 m/s and efficiency 0.50 requires
11.076 kW shaft power. The response raises the *unverified design target* to
12.8 kW, just above 1.15 times that nominal requirement (12.737 kW), without
specifying an available engine curve. Its own 14.820 kW sensitivity would need
17.043 kW for the same 15% reserve, so it fails even this assumed target.
Power reconstructed from its rounded D values differs from five reported
cases by at most 8 W, attributable to hidden unrounded drag; the exact raw
drag/efficiency inputs must be published if tighter replication is claimed.
Neither 12.8 kW nor 17.043 kW is measured shaft output.

For Opus, a 0.55 m x-dimension box at x=0.25 m has bounds
**-0.025 to 0.525 m**, not 0 to 0.5 m as the model wrote. Its E1--E3a
box-proxy intersection is 0.000375 m^3, not 0.0003 m^3. E1--E2 box-proxy
overlap is 0.0276 m^3. Those are arithmetic checks on the response's
dimensioned ledger shapes, not proof that solid engine and cooler parts
intersect; the physical occupied solids and allowable nesting were not
defined. The response correctly preserves the unresolved 13.7 kW high-case
shaft demand and states that a 15% reserve would require 15.755 kW **measured**
available output at the required operating point. The assumed 13 kW target
does not meet that case.

## Research gate

The V11b cycle produced one useful, auditable *geometric/loading candidate*
(Fable) and two justified holds, with no whole-aircraft flight acceptance.
It does not supersede V1/V2 numerical trim or supply a new final three-view:
Astra and Opus have no new geometry, while Fable's 0.3 kg stop and axle/radius
specification do not resolve its wing/propulsion/control installation.
No returned design has measured continuous installed engine--propeller power,
total drag, powered and power-off six-component trim, loaded swept clearance,
structural limits, installed neutral point, full derivatives or modes. The
research can document these negative and partial outcomes; it cannot claim
that any LLM aircraft is now demonstrated to fly or match Flyer I stability.

Next, freeze Fable's proposed stop/gear patch as a **candidate** and test
physical seat/gear clearances and pilot reach. For Astra/Opus, a non-minimal
member-resolved geometry is required before a useful interference test. For
all three, independent bounded aerodynamic and installed propulsion inputs
must precede a new trim and dynamic-mode calculation. An LLM's additional
assertion of power or stability cannot substitute for those inputs.
