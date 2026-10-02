# Latest-candidate rigid ground screen

Author: Ehsan Roohi. 29 September 2026. Reproducible calculation:
`analysis/audit_v14_rigid_ground.py`; frozen numerical output:
`analysis/results/v14_rigid_ground_gate01.json`. This is not a claim of
takeoff, loaded clearance, or flight.

The Fable physical gear points are taken from the complete V12 proposal; its
mass and center-of-gravity cases are replaced by the independently reconciled
V13 audit. With the model's front-pair contact at $x_f=0.40$ m, rear contact
at $x_r=3.20$ m, and gravity $g=9.81$ m/s$^2$, static reactions are

\[
R_f=mg\frac{x_r-x_{CG}}{x_r-x_f},\qquad R_r=mg-R_f.
\]

All eight declared V13 loading cases give positive reactions. Nominally,
$m=354.3$ kg and $x_{CG}=1.530739$ m yield $R_f=2072.079$ N for the front
pair and $R_r=1403.604$ N at the rear. Across the declared cases, $R_f$
ranges from 1846.975 to 2188.572 N; $R_r$ ranges from 1301.125 to
1418.494 N. The original V12 nominal ground-load line used the superseded
353.8 kg mass and must not be repeated as if it came from V13. Under a rigid
rotation about the front wheel line, the specified skid point at $x=0.00$
m and $z=-0.60$ m contacts at $\tan^{-1}(0.15/0.40)=20.556^\circ$
nose-down; the declared upturned toe at $(-0.30,-0.40)$ m would contact
later at $26.565^\circ$. No claim is made that these are the first contacts
of a fully occupied or deflected aircraft.

For Opus V12, the declared flat runner begins at $(-1.50,-0.90)$ m and the
front upturn begins at $(-1.90,-0.55)$ m in the model's $(x,z)$ plane. A
rigid pitch about the front end of the flat runner brings the named upturn
to the ground at $\tan^{-1}(0.35/0.40)=41.185925^\circ$ nose-down. The
front/lower corner of the specified nacelle box would contact only at
$79.215702^\circ$ under the same point-contact model, so the named runner
point comes first *among those two*. All four reported CG projections fall
within the flat runner's longitudinal support interval $[-1.50,1.60]$ m.
The support pressure along compliant skids, braking dynamics, component
clearances and structural deflections remain unknown. This calculation does
not override the model's explicit statement that a complete nose-down
contact sweep was not performed.

Astra V12 still provides no adopted installed geometry to screen. The
three-model dynamic/flight gate therefore remains open. These calculations
only eliminate a particular arithmetic ambiguity in the ground-contact
subsystem; they do not provide engine/propeller maps, six-component trim,
intrinsic inertias, unsteady derivatives or full longitudinal and lateral
modes.
