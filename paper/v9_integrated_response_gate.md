# Integrated V3 design returns: provenance and first independent gate

Author: Ehsan Roohi. Date: 28 September 2026. These are **model-authored,
researcher-assisted proposals**, not accepted aircraft designs. The original
historical source cutoff applies to V0, not to this modern feedback round.

## Archived requests and completion

The frozen V9 request was sent to GPT-6 Astra, Claude Fable 5.1, and Claude
Opus 5.5. Astra completed in Unity array 65007436. Fable and Opus hit the
caller-imposed 20,000-output-token limit, which counts their reasoning tokens;
those truncated responses remain archived. An independent full-prompt retry
of only Fable and Opus, with a 48,000-token cap and concise-output instruction,
completed in array 65009709. These are *retries*, not additional independent
model samples or evidence of design improvement. No incomplete response was
silently spliced into a complete one. The three selected responses, their
requests, prompts, instructions, outcome manifests and SHA-256 checksums are
under `received_v9_65007436/` and `received_v9_retry_65009709/`.

The reproducible auditor is `analysis/audit_v9_integrated_responses.py`; its
machine-readable result is `analysis/results/v9_integrated_response_audit.json`.
It verifies each response against its archived outcome hash, each prompt and
instruction against its request hash, the returned model identifier, response
completion, and the embedded structured block. It **does not** treat model
text as a measurement or independently solve flight mechanics.

## Recomputed mass bookkeeping

For component masses $m_i$ and stated three-dimensional centroids
$(x_i,y_i,z_i)$, the auditor independently evaluates
$M=\sum_i m_i$ and $\mathbf{x}_{CG}=\sum_i m_i\mathbf{x}_i/M$.
The native coordinate origins and longitudinal signs differ by model; their
numerical $x_{CG}$ values are **not directly comparable**.

| Model-reported version | Ledger rows | Recomputed mass (kg) | Recomputed CG (m, native frame) | Arithmetic result |
|---|---:|---:|---:|---|
| Astra V3-I | 16 | 333.0 | $(-0.150889,0,0.218445)$ | Matches reported rounded ledger |
| Fable V3 | 23 | 309.5 | $(1.556656,0,0.765670)$ | Matches reported rounded ledger |
| Opus V3 | 27 | 361.3 | $(0.622676,0,0.460036)$ | Matches reported rounded ledger |

This test establishes internal arithmetic only. Component masses, material
distributions, fuel state, installed hardware, clearances and the inertia
tensors have not been independently measured. A shape-based inertia estimate
is not a measured tensor.

## Force, moment and dynamic-evidence gate

Fable gives a nominal *conditional* longitudinal balance at 13 m/s. Its
stated wing lift $3245$ N plus tail lift $-209$ N equals its quoted weight
$3036$ N. The ledger weight is $309.5\times9.81=3036.195$ N, a $-0.195$ N
rounding difference. Its four quoted pitching-moment terms also sum to zero:
$-1329+436-14+907=0$ N m. The claimed tail moment has approximately the
expected magnitude for a $209$ N downward force acting about $4.34$ m aft
of the quoted CG. These equalities are **not independent predictions of lift,
drag or power**: the forces and coefficients remain assumed/model supplied.
The reported aft-CG static-margin estimate of 0.05 is likewise conditional;
installed body, slipstream, thrust and aeroelastic derivatives are absent.

Astra explicitly marks actual powered and glide trim solutions and both
sets of modal roots `UNKNOWN`. Opus says the evaluator must solve trim per
state and marks its dynamic verdict `NOT_ASSESSED`. Fable gives reduced
short-period/phugoid estimates but explicitly declines a full modal verdict.
None supplies a verified installed derivative set (including the needed
$\dot\alpha$ terms), measured inertia, or complete longitudinal and
lateral eigenvalues across the declared CG/speed/power envelope. Therefore
**no V3 aircraft passes a whole-aircraft dynamic-stability or flight gate**.
No static-margin number, reduced two-state calculation or mass-closure result
may be promoted into such a conclusion.

The next evaluator work is a geometric/clearance audit and independent
powered/power-off trim with uncertainty; a measured or appropriately
validated installed derivative set is required before the four-state modes
can be computed honestly. Fable's claimed tail and drivetrain clearances
especially need independent geometric and loaded-actuation checks. Any
material redesign reopens mass, CG, drag, trim and stability calculations.

## Comparative interpretation

These returns show a useful design *process*--specific responses to feedback,
explicit mass schedules, proposed tests and conditional redesign branches--
not demonstrated success. Fable has the most explicit nominal force/moment
arithmetic in this V3 set, while Astra and Opus more clearly leave trim
unsolved. That is a difference in what the models **reported**, not a ranking
of achievable flight. On the older, independently retrimmed V2 screen Astra
still has the larger conditional longitudinal/power margins among the two
screened designs; the V3 responses have not superseded those evaluator results.
No defensible overall winner or superiority to the historically flown Wright
Flyer I can be declared from the present evidence.
