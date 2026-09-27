# V2 simultaneous longitudinal trim: conditional numerical result

Date: 2026-09-27. Study author: Ehsan Roohi.

## What is being solved

The model-authored V2 geometry is unchanged. At its selected speed (Astra 18 m/s, Opus 15 m/s), solve for angle of attack and elevator deflection; eliminate thrust analytically with T=D/cos(alpha). The equations are L+T sin(alpha)=W, T cos(alpha)=D, and Maero+(zCG-zthrust)T=0. The reference axes, moment sign and thrust-line height are preserved explicitly. Controls are held fixed for subsequent +/-0.25 degree alpha probes.

Acceptance targets, declared in code before execution: |Rz|/W and |My|/(W Cref) <=0.001, with horizontal balance by elimination. Four Newton steps maximum per mesh, 0.2 degree finite differences, alpha bounded [-3,12] degrees and elevator [-15,15] degrees. These are numerical tolerances, not physical safety margins. Successful points are replayed in a separate solver invocation, and individual surface contributions are summed independently within output rounding bounds.

## Results and interpretation

Astra reaches a replayed trim on 10x48 and 14x72 meshes. On 14x72, alpha=-0.10311 deg, elevator=-0.32972 deg (TE-down-positive convention), and required thrust=245.519 N. Main-wing lift is approximately 3444.338 N and tail lift -305.772 N; summed printed components differ slightly from the higher precision total. Total aerodynamic lift=3138.507 N, thrust vertical component=-0.442 N, weight=3138.128 N; residual=-0.0632 N. Maero=-36.7629 N m, Mthrust=36.8278 N m; residual=0.0650 N m.

Astra's effective slope margin is 19.09% on 10x48 and 19.47% on 14x72. The elevator trim shifts by 0.23518 deg between meshes, so full convergence is not established. This is a local restoring-slope diagnostic, not dynamic stability or a universal neutral-point result.

Opus reaches a replayed trim on 10x48 at alpha=6.37109 deg and elevator=-3.37178 deg, with thrust=446.223 N. Aerodynamic lift=3480.898 N plus upward thrust=49.516 N balances W=3530.394 N to 0.0207 N. Maero=195.8801 N m and Mthrust=-195.9404 N m leave -0.0603 N m. The effective slope margin is 7.70% on this mesh.

The originally requested Opus 14x72 mesh failed during geometry loading: 'Vortex array overflow', NVMAX=5000. The eight mirrored surface patches would require 8064 panels. This is an evaluator capacity failure, not model design failure; logs are preserved. A separately recorded 12x50 recovery uses 4800 panels, increasing both resolutions relative to 10x48. This recovery completed successfully, including the independent replay and fixed-control slope probes.

On Opus 12x50, alpha=6.34680 deg, elevator=-3.16843 deg, and thrust=446.085 N. Lower-wing lift=1663.965 N, upper-wing lift=1894.806 N, and total tail lift=-77.715 N. The higher precision total aerodynamic lift=3481.056 N plus upward thrust=49.313 N balances W=3530.394 N with residual=-0.0254 N. Maero=195.8801 N m and Mthrust=-195.8798 N m close within the precision of printed solver coefficients; the computed residual is 0.00031 N m and should not be interpreted as physical accuracy at that scale. Surface lift and moment sums pass the output-rounding closure checks for all four accepted meshes.

Opus's effective slope margin changes from 7.70% to 7.76%; alpha shifts -0.02429 deg, elevator +0.20335 deg, and required thrust -0.138 N between meshes. This limited mesh sensitivity check does not establish asymptotic convergence, particularly for elevator deflection. Fine-mesh useful power is 6.650 kW, or 11.084 kW at the propeller shaft if the assumed efficiency 0.60 holds, before drive losses.

### Latest accepted operating points

| Quantity | Astra (14x72) | Opus (12x50) |
|---|---:|---:|
| Airspeed, m/s | 18 | 15 |
| Alpha, deg | -0.1031 | 6.3468 |
| Elevator, deg (TE-down positive) | -0.3297 | -3.1684 |
| Vertical force residual, N | -0.063 | -0.025 |
| Pitch moment residual, N m | 0.065 | approximately 0 at printed precision |
| Aerodynamic slope ratio -Cm_alpha/CL_alpha, % | 19.47 | 7.76 |

The slope ratio is evaluated with fixed elevator and is an aerodynamic restoring-slope diagnostic. It is not a complete powered-aircraft static margin: thrust response and omitted moments are not included in its derivative. Horizontal balance is imposed algebraically, not independently evidence that an actual propeller can supply the required thrust. The trim changes here were made by the numerical evaluator, not by another LLM revision.

## Limits that prevent a flight verdict

- Astra's parasite model includes only its 125 N aggregate 'other drag' at nominal speed; wing/tail profile drag is absent. Its power number cannot be presented as a validated power requirement or margin. The missing drag's application points can also change trim.
- Opus uses assumed CD0=0.05 at CG. At coarse trim useful power is 6.652 kW; dividing by an assumed propeller efficiency 0.60 gives 11.087 kW at the propeller shaft. Drive losses and an actual engine curve are not established. A 13 kW target is not evidence of available power.
- No validated viscous/stall, propwash, body-moment, ground-effect, flexibility, structural-strength or dynamic-inertia model. No lateral-directional or propeller reaction-torque equilibrium is demonstrated.
- Fixed-control restoring slope does not establish all-mode stability, control-force adequacy, stall recovery, launch feasibility or pilot workload.
- Fable is not retrimmed through unresolved geometry. Prospective feedback is in paper/fable_v2_geometry_feedback.md and has NOT been sent.

## Evidence and reproduction

Code: analysis/v2_trim_solve.py; capacity recovery: analysis/v2_trim_recover_opus.py; surface bookkeeping: analysis/v2_trim_report.py. Use the bundled Python with NumPy. Original and recovery runs are in separate immutable directories under analysis/results. Six local unit tests passed across test_received_v2.py and test_v2_trim_solve.py. No API call, Unity submission, manuscript compilation or public publication was performed in this step.

Conclusion: independently located numerical longitudinal equilibria now exist for Astra and Opus within stated simplified assumptions. They are stronger evidence than model-authored force ledgers, but do not certify flight or superiority over Wright.
