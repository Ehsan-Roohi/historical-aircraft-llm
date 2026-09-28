# V10 targeted geometry/power feedback: first return gate

**Historical status of this first-return gate.** A later, separately archived
post-billing Astra V10 response completed as Unity job `65012338`. See
`paper/v10_astra_postbilling_gate01.md`; the earlier failed attempts below
remain unaltered and were not spliced into that response.

Author: Ehsan Roohi. Date: 28 September 2026. This is a modern,
researcher-assisted correction round, **not** a fresh historical-cutoff
trial, independent aircraft design, installed propulsion test or flight
clearance. The three requests are source-hashed under
`analysis/prompts_v10_geometry_power/`. Slurm array `65011353` ran once
per model on Unity; complete raw request/response/outcome records are
preserved at `received_v10_65011353/`. The independent parser and
selected arithmetic checks are `analysis/audit_v10_responses.py` and
`analysis/results/v10_response_audit01.json`. No partial output is
spliced into a complete one.

## Transport and provenance

| Model | First V10 call | Source and arithmetic disposition |
|---|---|---|
| Astra | `error_or_uncertain`, `RuntimeError`; no response body | Parent, prompt and instruction hashes pass. The first runner retained only the exception class. A separately archived, one-time retry at the previously successful 20,000-output-token cap (job `65011846`) also failed, now with sanitized `HTTP 429 (credit_balance_exhausted, insufficient_quota)`. Thus the lower cap did not resolve the problem; the account/API quota, not a demonstrated design failure, prevented a V10 Astra answer. No further call was made. |
| Fable | Completed, `end_turn` | Response SHA-256 `bcd804a80087d451c8c9dac07d2f8a1118ba1487826ed32ec4a6420e49ea3324`; parent/prompt/model hashes pass. Selected revised loading and shaft-power arithmetic matches independent recomputation within reported rounding. |
| Opus | Completed, `end_turn` | Response SHA-256 `100027bc62931728bbcc8b041caff043d6031938ebd388c329e0129f896ce04e`; parent/prompt/model hashes pass. Selected revised loading, 12.994617° rigid tail-skid contact and high-case power arithmetic match independent recomputation. |

The two complete outputs are **model-authored correction patches**, not
accepted geometry or evidence of flight. Raw parent V3 answers remain
unaltered. The audit verifies arithmetic and provenance only; it does not
verify physical engine power, aerodynamic coefficients, structure,
control authority, full trim or dynamic eigenmodes.

## Technical reading of the corrections

Fable acknowledges its erroneous 65/85 kg pilot CG percentages and now
reports 36.73% chord for the 65 kg aft/full state and 28.59% for the
85 kg forward/full state; the corresponding empty-fuel values are 36.90%
and 28.32%. Those numbers match the archived 23-row ledger. It relabels
the wheel coordinates as *ground-contact points*, but wheel radius and
axle coordinates remain unknown; thus the landing gear is still not a
complete geometrical definition. Its propeller-to-body nominal gap is
0.050 m, while runout, deformation and tolerances remain unknown. The
nominal lower control-horn gap is revised to about 0.037 m, with the
loaded swept gap still unknown. Fable reconciles its nominal shaft
requirement as 11.076 kW under assumed `D=426 N`, `V=13 m/s` and
efficiency 0.50. It proposes a **new, unverified 12.2 kW target**;
its own illustrative worse drag/efficiency case requires about 14.8 kW.
Neither target nor requirement demonstrates available engine power. The
proposed seat restriction to avoid an aft CG is an *assumed operating
constraint*, not a validated static margin; neutral point, slipstream
and control/hinge capability are still unknown. Its reported 0.027 aft
margin is a reduced estimator, not an independent installed result.

Opus makes no adopted mass or geometry change. It correctly relabels
the claimed 13° ground clearance: under its rigid aft-skid pivot, the
tail-skid reaches ground at 12.994617°, and the ventral-fin gap there is
approximately 0.22111 m. This is a useful internally consistent
rotation-stop model but cannot settle loaded skid deflection or the
ventral-fin/brace interface. It retains, rather than conceals, the
conditional 0.700 kW shortfall of the assumed high-drag demand relative
to its unverified 13 kW target. Its hypothetical heavier engine is
explicitly *not adopted*; no engine curve, installed propeller map,
powered/glide trim or mode result was supplied.

## Gate decision

The completed Fable and Opus patches improve the audit trail and correct
specific arithmetic or labeling errors, but **neither crosses the V3
independent trim/flight gate**. In particular, a corrected CG percentage
does not establish a positive static margin, and a nominal positive
clearance does not establish loaded control travel. Astra remains at its
prior V3 status because both V10 transport attempts failed without a design
response; the retry's quota rejection is audited and no further call is
scheduled. The next evaluator
work is to freeze a mechanically admissible geometry and obtain bounded
installed lift, drag, pitching-moment, thrust and torque inputs; only then
can powered and power-off trim be solved and dynamic derivatives/modes
tested. The absence of CFD does not make an assumed force table valid.
