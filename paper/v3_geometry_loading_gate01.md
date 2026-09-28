# V3 geometry and loading gate 01

Author: Ehsan Roohi. Date: 28 September 2026. This is an **independent
arithmetic and conditional rigid-geometry audit of model-authored V3
proposals**, not a verified aircraft design or flight authorization.

Reproduce with
`python analysis/audit_v3_geometry_loading.py --output analysis/results/v3_geometry_loading_gate01.json`
and `python -m unittest discover -s analysis -p test_v3_geometry_loading.py -v`.
The JSON embeds the SHA-256 digests of all three immutable response wrappers.
This gate follows `paper/v9_integrated_response_gate.md`; it neither edits
those responses nor silently carries V2 trim results into V3.

## Coordinates and nominal geometry

Astra uses x forward, y right and z up. Fable and Opus use x aft, y right
and z up; their longitudinal CG numbers cannot be compared directly with
Astra's. Every clearance below is a rigid, nominal drawing calculation.
Neither blade thickness, structural deflection, ground compression nor
manufacturing tolerance is included.

| Aircraft | Recomputed main reference area | Nominal propeller-to-ground gap | Other directly recomputable gaps | Status |
|---|---:|---:|---|---|
| Astra V3-I | 30.00 m² | 0.400 m | Both wheel bottoms lie at ground z = -1.60 m; tail area 6.00 m² | Drawing arithmetic closes; loaded/swept clearance unknown |
| Fable V3 | 42.55 m² (both biplane decks) | 0.400 m | Disc-to-disc 0.900 m; disc-to-body-side 0.050 m; nominal axial disc-to-wing-TE 0.200 m | 0.050 m side gap and 0.040 m reported horn gap need tolerance, flex and motion tests |
| Opus V3 | 39.60 m² (both biplane decks; prose schedule) | 0.600 m | Propeller plane x = 2.10 m, lower-wing TE plane x = 1.80 m: 0.300 m plane separation | These are not swept solid-body clearances; published 0.220 m blade/wing gap has a different reference |

The Fable three-view schedule lists all three `wheels` at z = -0.75 m,
exactly its rest-ground plane. If those coordinates are wheel *centres*,
any nonzero radius penetrates the ground. If they are contact points, the
field is mislabelled or underspecified. Wheel radii, contact definition and
ground attitude must be supplied before a usable three-view or rotation
clearance can be accepted. This is an **ambiguity**, not proof that a
physical layout cannot be repaired.

Opus states a 0.221 m ventral-fin gap at 13° pitch. A rigid rotation of its
aft-lower fin corner (x = 5.60, z = 0.25 m) over level ground z = -0.90 m
gives

`gap = (z-z_p) cos(theta) - (x-x_p) sin(theta)`

when the pivot lies at ground height `z_p = -0.90 m`. At 13°, pivoting on
the aft end of the stated flat skid (`x_p = 1.60 m`) yields **0.220721 m**,
reproducing the model's claim. Pivoting at the nominal wheel station
(`x_p = 0.45 m`) yields **-0.037972 m**, a geometric ground intersection.
The same aft-skid-pivot model places the tail-skid tip (x = 5.50, z = 0)
at **-0.000376 m** relative to ground at 13°; its first rigid contact is
at **12.994617°**. Thus the published ventral gap is internally consistent
with a tail-skid-limited rotation near 13°, not automatically a collision.
Conversely, wheel-pivot-only rotation cannot persist to that attitude
without ground intersection; load must transfer to the aft skid or the
gear must deform. The actual ground-contact sequence, structural/gear
deflection and available rotation have not been measured, so the reported
0.221 m remains **conditional**, not a validated installed clearance.

## Independent loading-case calculations

Each case substitutes the pilot mass/position and removes or retains fuel
in the archived component ledger, then recomputes `M = sum(m_i)` and
`CG = sum(m_i r_i)/M`. These remain assumed component masses, not weighed
hardware.

| Aircraft/state | M (kg) | xCG (m, native frame) | Check |
|---|---:|---:|---|
| Astra 60 kg pilot at x = -0.10, empty fuel | 310.0 | -0.240149 | Agrees with rounded reported limit |
| Astra 90 kg pilot at x = 0.40, full fuel | 348.0 | -0.084041 | Agrees with rounded reported limit |
| Fable 75 kg pilot forward, full fuel | 309.5 | 1.520307 | 30.827% lower-deck chord |
| Fable 75 kg pilot aft, full fuel | 309.5 | 1.593005 | 34.757% lower-deck chord |
| Fable 65 kg pilot aft, full fuel | 299.5 | 1.629499 | **36.730%** chord, versus model's **35.4%** |
| Fable 65 kg pilot aft, empty fuel | 283.5 | 1.632575 | **36.896%** chord |
| Fable 85 kg pilot forward, full fuel | 319.5 | 1.478983 | **28.594%** chord, versus model's **30.2%** |
| Fable 85 kg pilot forward, empty fuel | 303.5 | 1.473921 | **28.320%** chord |
| Opus 70 kg pilot, empty fuel | 349.3 | 0.626891 | Agrees with rounded reported limit |
| Opus 90 kg pilot, full fuel | 381.3 | 0.542809 | Agrees with rounded reported limit |
| Opus 90 kg pilot, empty fuel | 369.3 | 0.544200 | Agrees with rounded reported limit |

For Fable, the lower-deck root leading edge is x = 0.95 m and its chord is
1.85 m. The two disputed fractions use exactly the model's stated seat
travel (x = 0.20 to 0.50 m), pilot range (65 to 85 kg), nominal ledger and
full-fuel case; the model did not specify fuel state for its 65/85 kg
percentages, so empty-fuel alternatives are also shown. Neither fuel
extreme reproduces those percentages. No unexplained ballast is added.
The aft-CG error is
important because the quoted 5% static-margin estimate is conditional on
the model's loading and unverified neutral point. **Its static margin must
be recomputed at the corrected 36.730% extreme**; one cannot infer a
validated positive or negative margin from this arithmetic alone.

## Necessary vertical-force screen, not trim

For an illustrative steady, level state, the whole aircraft must produce
vertical force `W = mg`. Relative to the stated total wing reference area,
`C_Z,eq = mg/(0.5 rho V² Sref)` with rho = 1.225 kg/m³ and
g = 9.80665 m/s². It is **not** a wing-only lift coefficient or an
achieved aerodynamic result. Tail force, biplane interference, slipstream,
stall, drag, thrust and pitch moment are not solved.

| Aircraft, nominal mass | Speed (m/s) | Required equivalent vertical-force coefficient |
|---|---:|---:|
| Astra 333.0 kg | 15 / 18 / 21 | 0.790 / 0.549 / 0.403 |
| Fable 309.5 kg | 12 / 13 / 16 | 0.809 / 0.689 / 0.455 |
| Opus 361.3 kg | 13 / 15 / 18 | 0.864 / 0.649 / 0.451 |

These values alone cannot determine whether any aircraft reaches its
required force before stall, or whether the necessary tail force and
control deflection are achievable. They should be used as explicit
requirements for the next independent aerodynamic/trim model, never as
evidence that lift has been demonstrated.

## Gate disposition and next calculation

**Status: HOLD for V3 powered/power-off trim.** Source identities and the
limited arithmetic above are reproducible, but the geometry is not yet a
resolved installed-aircraft configuration. The shortest feedback requests
are: (1) Fable must correct its 65/85 kg CG extremes and define wheel
centres/contact points and toleranced tail/propeller gaps; (2) Opus must
specify the skid/wheel contact path through 13° pitch and the ventral
fin-to-brace motion; (3) Astra must provide loaded swept control/propeller
and gear clearances. All three need defensible whole-aircraft aerodynamic
and installed-propulsion inputs before solving `sum F = 0` and
`sum M_CG = 0` across speed, loading and power states. Unknown coefficients
must remain unknown; a model-supplied balanced force table is not an
independent trim prediction. No aircraft is declared flight-capable.
