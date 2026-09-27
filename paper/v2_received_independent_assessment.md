# V2 received designs: independent first-stage assessment

Date: 2026-09-27. Author of study: Ehsan Roohi.

## Outcome

All three approved V2 calls completed. Their response files were downloaded from Unity job 64942345 and SHA256 verified locally. V2 is researcher-assisted revision, not a blind historical rediscovery. No additional API call or public upload was made during this assessment.

None of the three designs has demonstrated physical flight, complete static/dynamic stability, structural adequacy or historical engine feasibility. This is not proof that they cannot fly. The useful new finding is that Astra changed architecture and its new lifting-surface model has a restoring pitch slope; Opus retains a restoring slope but its proposed operating point still misses simultaneous trim. Fable has unresolved geometric contradictions.

## Changes and arithmetic audit

| Model | V2 change | Recomputed mass | Recomputed CG in model axes |
|---|---|---:|---|
| Astra | Tandem pusher replaced by main wing, aft tail, tractor propeller and separate controls | 320 kg | (0, 0, 0.150000) m, x forward |
| Fable | Split enlarged tail, changed rigging, shifted wing and repaired ledger | 295 kg | (1.560881, 0, 0.753881) m, x aft |
| Opus | Wider boom spacing, skid/rudder changes, proposed speed reduced to 15 m/s | 360 kg | (0.614758, 0, 0.460892) m, x aft |

Native CG values must not be compared without aligning datums and coordinate conventions. Masses remain assumed budgets, not manufactured weights. Opus's stated first-moment sums differ slightly from its rows (0.002 kg m in x and 0.012 kg m in z), while rounded CG values agree closely.

Astra's selected force and moment ledger closes arithmetically to rounding. Fable and Opus force ledgers also approximately close when their assumed loads are used. This demonstrates bookkeeping, not aerodynamic prediction: selecting loads that satisfy equilibrium cannot validate the geometry that is supposed to generate them.

Fable's fuel item P07 has centroid z=0.90 m outside its declared z interval [0.95,1.15] m. Its engine and fuel envelopes overlap; that alone is not proof of solid interference but requires definition. Its stated tail swept z interval [0.72,0.93] m is not recovered from its hinge, chord, -4 degree rigging and +/-12 degree travel: a rigid zero-thickness chord yields approximately [0.67062,0.98173] m. This does not by itself establish collision with the fin. The model separately acknowledges unresolved drive-shaft/truss routing. Do not silently repair these.

## Independent lifting-surface diagnostic

Code: analysis/v2_independent_probe.py. Existing AVL 3.52 executable; solver and geometry hashes retained. Four solver processes generated 12 alpha points: two models, two meshes (6x24 and 10x48 surface settings), three angles each. Proposed pitch controls were fixed; perturbations were +/-0.25 degree. This was not a retrim search and not a mesh-convergence demonstration.

Astra's x axis was reversed into the solver's aft-positive coordinates. Main-wing incidence and cambered section polygon came from V2. Its symmetric tail is represented by its flat camber line. Opus uses V2 wing sections/stations and the split-elevator notch, with TE-up mapped to negative solver pitch. Vertical surfaces were omitted for the symmetric longitudinal diagnostic. No roll/yaw result follows. Fable is deferred pending geometric reconciliation.

| Quantity at proposed state | Astra, finer mesh | Opus, finer mesh |
|---|---:|---:|
| Speed (m/s) | 18 | 15 |
| Alpha (deg) | 0 | 6.1 |
| Elevator, solver TE-down-positive (deg) | -0.46727 | -3.4 |
| Assumed thrust (N) | 400 | 448 |
| Aerodynamic lift (N) | 3165.714 | 3388.520 |
| Thrust vertical component (N) | 0 | 47.606 |
| Weight (N) | 3138.128 | 3530.394 |
| Vertical residual (N) | +27.586 | -94.268 |
| Pitch residual, nose-up-positive (N m) | +77.265 | +15.090 |
| dCL/dalpha, per degree | 0.07266 | 0.06454 |
| dCm/dalpha, per degree | -0.01394 | -0.00484 |
| Effective slope margin -Cm_alpha/CL_alpha | 19.19% Cref | 7.50% Cref |

The coarser effective margins were 18.23% and 6.99%. Pitch residuals were 204.52 and 38.18 N m on the coarser mesh: appreciable mesh dependence remains, especially for Astra. Negative slopes on both meshes indicate a conditional local restoring tendency, not validated neutral points or dynamic modes. Astra's approximately -9.94% V1 diagnostic was from a different architecture and operating point; this is not a controlled one-variable improvement or a general model ranking.

At the finer mesh, normalized |Rz|/W is about 0.00879 (Astra) and 0.02670 (Opus); normalized |My|/(W Cref) is about 0.00985 and 0.00237. Neither proposed point meets the protocol's 0.001 numerical closure targets. No accepted trim point is claimed.

Parasite drag was assumed, applied at CG with no extra pitch moment: Opus CD0=0.05; Astra retains only its stated 125 N 'other drag' at nominal speed. Astra's wing/tail profile drag is therefore not independently supplied and its computed horizontal balance/power cannot establish feasibility. Neither model includes body moments, propwash, separated/viscous flow, flexibility or ground effect. The selected thrust values are not established engine-propeller operating points.

## Next decision gates

1. Preserve these responses and diagnostics, including failures and mesh sensitivity.
2. Obtain model-authored reconciliation of Fable's tank/tail/shaft geometry; do not replace its design with evaluator inventions.
3. Validate V2 geometry/control mappings, then solve simultaneous force/moment trim and repeat at finer discretization. Record any new interpretation explicitly.
4. Supply sourced or measured engine/propeller capability, structural properties and component inertias before claiming power margin, structural sufficiency or dynamic stability.
5. Compare with a sourced Wright baseline under matched assumptions and uncertainty. The current evidence cannot establish superiority over the Wright Flyer.

The distinction is substantive: this iteration produced revised proposals and useful conditional evidence, not yet a verified flyable aircraft.

## Reproduction

Run `python analysis/audit_received_v2.py` to regenerate extracted design JSON, response Markdown and arithmetic summary. Run `python -m unittest discover -s analysis -p test_received_v2.py` (four tests passed). The independent solver script requires a fresh output directory and deliberately refuses to overwrite its archived run. Numerical data: analysis/results/v2_independent_probe01/summary.json.
