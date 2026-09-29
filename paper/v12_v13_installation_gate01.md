# V12 installation candidates and V13 Fable arithmetic: independent gate

Author: Ehsan Roohi. Date: 28 September 2026 (Unity completion crossed into
29 September UTC). Modern researcher-assisted feedback only. The historical
V0 proposals and prior model returns are immutable. No conclusion here gives
construction or occupied-flight clearance.

## Source and transport record

The V12 prompts included each model's full V3, V10 and V11b answer; their
source hashes and composed text are frozen at `v12_installation_attempt01/`.
Slurm array `65013298` made one bounded call per model. Astra and Fable
completed at 32,000 maximum output tokens. Opus stopped at that exact limit;
its partial answer and `max_tokens` outcome remain archived unchanged. A
single separately manifested Opus replay at 48,000 maximum tokens, job
`65013467`, completed. It is a new answer, not a splice or continuation of the
partial text. Fable's completed V12 answer then received one exact-source,
arithmetic-specific V13 feedback call, job `65013542`, which completed.
Request metadata, raw prompts, responses, outcomes and Slurm logs for all
five calls are retained. `analysis/audit_v12_installation.py` and
`analysis/audit_v13_fable.py` verify source/response hashes and selected
arithmetic; their JSON results are in `analysis/results/`. They do not test
physical performance.

## Design and arithmetic dispositions

| Model | Latest model response | Independent result | Present gate |
|---|---|---|---|
| Astra | V12 HOLD, no adopted component change | Full context and permission for non-minimal redesign were supplied. The model still did not close a member-resolved truss, controls, engine/shaft, gear and mass ownership in one installation. | No new V12 aircraft geometry to trim or render. |
| Fable | V12 non-minimal engine/gear/seat candidate; V13 arithmetic correction | V12's 26 parts summed to 354.3 kg, not its 353.8 kg headline. V13 preserved all parts and corrected all eight loading cases. Nominal CG is (1.530739, 0, 0.792233) m. The 19.5 kW engine-side target at assumed 0.95 drive efficiency delivers only 18.525 kW to the two propeller shafts, 0.520 kW short of the revised 19.045 kW heavy/worst-case requirement including 15% reserve. | Ledger passes; propulsion reserve fails even as paper targets, and no available engine/propeller map exists. |
| Opus | V12 first response truncated; reviewed complete replay offers a geometry candidate | The 30 physical ledger rows sum to 340.3 kg, first moments (239.41875, 0, 170.5674) kg m, nominal CG (0.703552, 0, 0.501227) m. Four pilot/fuel cases close. Rigid aft-skid pivot gives 12.994617-degree tail-skid contact, 0.221112 m ventral and 0.460962 m aft propeller ground gaps at that stop. An assumed 18 kW engine with 0.97 drive efficiency would have 17.460 kW propeller-shaft target versus 15.755 kW high-case requirement with reserve. | Arithmetic candidate only. Engine and propeller maps, loaded gaps, nose-down contact, structure, trim and stability remain unverified. |

For Fable the exact-source V13 response identifies the mass omission as the
revised P15 row's extra 0.5 kg, which was entered in the V12 row table but
not in its SUM. It does not propose deleting that mass. Our independent sum
and recomputation of all eight pilot/seat/fuel cases now match its rounded
values. The heaviest case at 13 m/s and assumed high drag requires 16.561 kW
at the propeller shafts without reserve and 19.045 kW with 15% reserve. At
assumed 0.95 drive efficiency, the minimum *engine-side target* is therefore
20.047 kW, before a heavier engine changes aircraft weight and drag. The
V13 model notes that this mass--power iteration would need a new ledger;
it does not adopt a paper-only larger engine. Its 19.5 kW target fails the
stated reserve criterion by 0.520 kW. Neither target is measured available
power. Blade power absorption, thrust, cooling and fuel consumption remain
unmeasured; the V13 response also corrects a parent fuel-endurance arithmetic
error (20 kg / (0.31 kg/kWh × 19.5 kW) is about 198, not 20, minutes).

Opus's new ledger and rigid ground-contact arithmetic pass our selected
checks, but only under its assumed occupied-solid geometry and pivot model.
The model's 18 kW is a proposed engine target, not a known continuous output.
Its propeller blade geometry and matched torque/thrust coefficients are
missing; an engine number alone cannot demonstrate that the propeller absorbs
that power or provides required thrust. The CG shifts aft from its V3 claim,
so earlier local pitch-slope or static-margin numbers cannot transfer to V12.
Loaded structural deflections and tire/skid contact require testing. The
model did not evaluate nose-down ground contact. The reported nominal gaps
must not be described as safe loaded clearances.

## Scientific stopping rule

On current evidence, **none of the three designs has passed a whole-aircraft
flight-possibility or dynamic-stability gate**. Fable V13 and Opus V12 are
analytical installation candidates of different completeness, not final
flight designs; Astra remains without a new installed V12 layout. More model
feedback may refine the component records, but cannot create measured
engine--propeller characteristics, installed drag/lift/moment maps, hinge
loads, structural allowables or unsteady derivatives. The next independent
stage is to freeze the candidate geometry, check occupied solids and all
ground/control sweeps, acquire bounded propulsion/aerodynamic inputs, then
solve powered and power-off six-component trim and dynamic modes over the
loading envelope. Only if those gates pass can a comparison with the actual
Flyer I be presented as a defensible flight-capability claim.
