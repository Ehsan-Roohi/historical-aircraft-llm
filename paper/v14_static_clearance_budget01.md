# Latest-candidate nominal installation-gap screen

This evaluator-only screen uses the complete Fable V12 occupied-geometry record and the separate complete Opus V12 replay. Fable V13 explicitly says **no component mass, centroid or bounding box changed**, so its V12 geometry is the relevant parent. The exact response SHA-256 identifiers, numeric outputs and rerunnable code are in `analysis/results/v14_static_clearance_budget01.json` and `analysis/audit_v14_static_clearance_budget.py`.

From Fable's specified coordinate intervals, six *one-axis rigid* separations were independently recomputed:

| Fable V12/V13 pair or interface | Nominal separation (m) | Calculation |
|---|---:|---|
| Pilot aft envelope to engine forward envelope | 0.150 | $0.85-0.70$ along $x$ |
| Engine side to frame side | 0.020 | $0.40-0.38$ along $|y|$ |
| Tank top to upper longeron | **0.010** | $1.20-1.19$ along $z$ |
| Upper longeron to cooling-box bottom | 0.020 | $1.22-1.20$ along $z$ |
| Inboard propeller swept-disc edge to frame side | 0.050 | $1.60-1.15-0.40$ along $|y|$ |
| Wing trailing-edge station to propeller-disc plane | 0.200 | $3.00-2.80$ along $x$ |

These arithmetic gaps only hold for the model's nominal, undeformed coordinates and proposed component envelopes. The **10 mm** tank/longeron gap is not a safety allowance: material thickness, assembly tolerance, thermal motion, bracing deflection, engine vibration, blade flex, wheel compression and control motion have not been budgeted. A positive distance along one coordinate also does not verify every other nearby component or the swept volume through a full motion cycle. To prove a particular gap survives, the sum of the relevant adverse displacements and tolerances must be demonstrably less than that gap; no such data were provided.

Opus V12 **reports**, but the evaluator has not recreated from a complete member-resolved solid model, selected gaps of 10 mm at an intended engine-to-output-shaft interface, 15 mm at a bearer/wing fitting, 27.5 mm near the front struts/shaft, 40 mm at a wheel/skid lateral interface and 50 mm at an aft node/elevator hinge. The first two involve intended interfaces rather than a free-clearance claim. These values cannot be put on the same evidentiary footing as the Fable one-axis recomputations and do not establish loaded or swept clearance. The result is a targeted request for solid/member coordinates, tolerance and deflection bounds, not an acceptance or a ranking between aircraft.
