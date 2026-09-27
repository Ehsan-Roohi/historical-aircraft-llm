# Fable V2: evaluator feedback for a prospective correction

Prepared 2026-09-27. NOT SENT. This document is evaluator feedback, not a changed model design. No new API request is authorized or claimed by this file.

Parent response SHA256: 9ce7f3f7bb6629d710b99e93ff9d92ad458a5f6247a2a1e061d53334bc888431.

Preserve V2 and give an explicit change log. Return corrected geometry with a single authoritative coordinate/rotation definition; do not report successful flight or fabricated measurements.

1. P07 fuel/tank centroid z=0.90 m lies outside its declared bounding interval z=[0.95,1.15] m. Explain which value is intended, correct it and recompute the complete mass ledger/CG. Do not change a number merely to preserve the current CG.
2. P06 engine bounds x=[0.95,1.75], y=[-0.35,0.35], z=[0.45,1.15] overlap P07 bounds x=[1.4,1.75], y=[-0.30,0.30], z=[0.95,1.15]. Envelope overlap does not prove solid collision, but 'above engine' is not demonstrated. Supply non-conflicting occupied geometry or documented internal clearance.
3. For tail hinge (5.65, y, 0.775), chord endpoints x=5.40,6.40, incidence -4 deg and control +/-12 deg, the rigid zero-thickness chord reaches approximately z=[0.67062,0.98173], not [0.72,0.93]. State whether station coordinates are before or after rigging. Supply the exact transformation for leading edge, trailing edge and section thickness across all travel. Re-evaluate clearance without silently discarding rigging.
4. A rounded rectangle with two aft-corner radii 0.8 m, span 11.5 m and chord 1.85 m has a planform area determined by that boundary, not by rounding the area to 21.00 m2. Provide the exact tip boundary and distinguish actual area from Sref. Likewise, clarify whether the five supplied section ordinates define a piecewise-linear camber line or samples of an exact circular arc; do not let the evaluator choose silently.
5. The propulsion record still acknowledges unresolved shaft/truss interference. Provide member endpoints/sections and shaft envelopes at crossings, with bearing supports and load paths. Declare unresolved joints or clearances as UNKNOWN.
6. Return component inertias or a derivation based on defined mass distributions; UNKNOWN is preferable to assigning uniform solid boxes to sparse structures. Power, material allowables and propeller capability remain unverified requirements.

Until these items are resolved, a complete geometry-consistent flight validation is not available. No implied collision-free or flight-safe verdict follows from correcting this list.
