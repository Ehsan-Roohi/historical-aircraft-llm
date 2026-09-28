# V3 installed-power necessity gate 01

Author: Ehsan Roohi. Date: 28 September 2026. This is a conditional
arithmetic audit of *model-assumed* drag and efficiency, not an engine,
propeller, aerodynamic or flight test. Reproduce with
`python analysis/audit_v3_power_necessity.py --output analysis/results/v3_power_necessity_gate01.json`
and `python -m unittest discover -s analysis -p test_v3_power_necessity.py -v`.
The JSON embeds each parent response's SHA-256 digest. This gate is
downstream of `paper/v3_geometry_loading_gate01.md` and does not promote
its unresolved configuration to an accepted aircraft.

## What the power equations can and cannot show

For steady level flight with thrust approximately balancing drag along
the flight direction, useful propulsive power is `D V`. Engine power
required is `D V/(eta_prop eta_drive)` where the efficiencies must be
*installed, operating-point values*. The V3 responses do not contain a
measured engine power/torque curve or an installed propeller map. Their
drag values and efficiencies are assumptions or external conditional
calculations. A numerical target margin is therefore a **hypothesis**,
not evidence that the engine can supply it. The thrust-line moment, tail
force, stall, 3-D interference and ground effects are not resolved here.

| Case | Model's conditional demand | Unverified target/other claim | Independent arithmetic finding |
|---|---:|---:|---|
| Astra, 18 m/s, high assumed drag 520 N, prop efficiency 0.55, drive 0.95 | 17.914 kW engine | 18.000 kW target | Just 0.086 kW (0.48% of target) nominal arithmetic margin; minimum prop efficiency 0.54737 if drive stays 0.95 |
| Fable, 13 m/s, assumed drag 426 N and efficiency 0.50 | 11.076 kW shaft (rounded to 11.080 kW in its drag table) | Another engine-table field calls 10.700 kW the shaft-power requirement | 0.376 kW disagreement between fields. If 10.700 kW were a hard cap, efficiency would have to be at least 0.51757; actual available engine power is explicitly unknown |
| Opus, 15 m/s, high assumed drag case | 13.700 kW shaft | 13.000 kW target | 0.700 kW conditional shortfall. At fixed high-case useful power, efficiency would need to rise from the assumed 0.576 to 0.60702; actual map is unknown |

Astra's other two assumed drag cases require 11.024 and 13.780 kW at
the engine. Its high case almost exhausts the target even *before* any
extra uncertainty in drag, efficiency or motor output is assigned.
Fable's 10.700 kW number is **not** silently reinterpreted as measured
power or a cap; the V3 answer labels available power `UNKNOWN`. It is
an internal requirement conflict to be reconciled. Opus's nominal
assumed demand is 11.670 kW, below its target, while its own high-drag
scenario is above that target. Neither proves failure or success of a
physical aircraft.

## Disposition before solving trim

**Installed-power gate: unresolved for all three.** To solve the powered
force and pitch-moment equations rather than merely reproduce model
arithmetic, the evaluator needs installed drag/lift/pitch-moment maps
versus airspeed, angle and control deflection; an engine brake curve;
propeller thrust/torque/efficiency versus airspeed and rpm; drive loss;
thrust-axis and slipstream moments; and stall bounds. For power-off
trim the stopped/windmilling propeller drag and its moment are also
needed. These must carry uncertainty and provenance. A low-order model
or appropriately matched component tests may supply a research screen;
CFD is not a prerequisite for this stage. Without those data, a claimed
V3 `sum F = 0` and `sum M_CG = 0` would still be an assumed balance, not
an independent prediction. No aircraft is flight-cleared.
