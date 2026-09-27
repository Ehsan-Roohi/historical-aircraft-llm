# Flyer I (1903), Astra, Fable and Opus: comparison with explicit evidence levels

Author: Ehsan Roohi. 27 September 2026.

## What the comparison can answer

The historical comparator is the **1903 Wright Flyer I**, not the 1902 glider, 1905 Flyer or a modified modern replica. Its actual flight is independently documented in the [Library of Congress first-flight records](https://www.loc.gov/collections/wilbur-and-orville-wright-papers/articles-and-essays/collection-highlights/first-flight/). The three AI proposals have no corresponding flight demonstration. A restoring moment slope in a simplified calculation does not reverse this evidential difference.

The AI source packet ends on 31 December 1898. Flyer I incorporates the Wrights' subsequent experiments; it is therefore a later achievement benchmark, not a design produced with an identical information budget. Modern model training may contain later knowledge despite prompt restrictions. The V2 proposals also received modern evaluator feedback, explicitly outside the historical packet.

## Calculation method

The new executable postprocessor is `analysis/wright_fourway_assessment.py`; its source-hashed output is `analysis/results/four_aircraft_comparison01/summary.json`. It uses the existing 20 selected, audited Wright-reconstruction outputs, specifically the four refined zero-canard-incidence cases for the dimensional table. No additional solver run, historical CG identification or empirical validation is claimed in this step.

For density rho, speed V, area S and reference chord c:

    q = rho V^2 / 2
    L = q S CL;  D_ind = q S CD_ind;  M_ref = q S c Cm
    W = m g;  CL_required = W / (q S)  [zero vertical thrust assumption]
    K = -Delta(Cm) / Delta(CL)

K describes the slope about the chosen moment reference. A historical static margin requires the actual CG, appropriate normal-force derivative and complete moment model. For moving the reference from r_old to r_new, use the vector transfer M_new = M_old + (r_old-r_new) cross F in a consistent right-handed frame; merely renaming the reference as CG is invalid.

AI trim uses coupled force and moment balance, including its stated thrust-line offset:

    L + T sin(alpha) - W = 0
    T cos(alpha) - D = 0
    M_aero + (z_CG-z_thrust) T = 0

These equations do not prove that a physical engine/propeller supplies the computed T. The archived V2 trim report specifies the drag and efficiency omissions.

## Wright dimensional screening—not reconstructed flight conditions

Use an explicitly selected V=12 m/s, rho=1.225 kg/m3 and provisional loaded mass 750 lb = 340.194 kg. The solver uses S=47.38055 m2 (510 ft2), c=1.9812 m, and moment reference x=z=0.59436 m. The nominal source's separate 518 ft2 statistic is preserved, not silently substituted. Thus q=88.2 Pa, W=3336.166 N and CL_required=0.79832 without vertical thrust.

| Canard section assumption | Alpha | Lift, N | L-W, N | Moment about reference, N m | Induced drag only, N |
|---|---:|---:|---:|---:|---:|
| Flat proxy | 0 deg | 2369.85 | -966.32 | -364.87 | 104.19 |
| Flat proxy | 4 deg | 3401.43 | +65.26 | +84.95 | 217.32 |
| Eiffel 10 proxy | 0 deg | 2418.91 | -917.26 | -22.02 | 111.25 |
| Eiffel 10 proxy | 4 deg | 3449.36 | +113.19 | +427.05 | 229.09 |

Enough lift at a sampled angle is not simultaneous trim: the aerodynamic moment is not zero and propulsive moments are unresolved. Induced-drag power is only 2.608–2.749 kW at the two 4-deg points; this excludes substantial non-induced drag and is **not** the Flyer's engine-power requirement. Individual wing/canard loads were not recorded in these selected total-force outputs, so their partition is not invented.

Over alpha=0–4 deg, the two refined canard assumptions give CL secants 3.532–3.536 per radian and Cm secants **+0.7769 to +0.7782 per radian**. Their K values are about **-22.0%**, indicating a destabilizing aerodynamic slope at the stipulated reference. This is not an established historical CG-based static margin. Digitized replica-test curves separately have a positive fitted Cm-versus-CL trend; they are not used to tune or validate this unmatched reconstruction. See `paper/wright_validation_gate_v1.md`.

## Four-aircraft evidence table

| Item | Wright Flyer I reference | Astra V2 | Fable V2 | Opus V2 |
|---|---|---|---|---|
| Layout | Biplane, forward biplane elevator | Monoplane, aft tail | Biplane, split aft tail | Biplane, aft tail |
| Propulsion arrangement | Two rear propellers, chain drive | Single tractor, short shaft | Two rear propellers, proposed geared shafts | Single pusher, chain drive |
| Mass used in this study | 340.19 kg, provisional historical statistic | 320 kg ledger | 295 kg ledger | 360 kg ledger |
| Current equilibrium evidence | Sampled reconstruction loads; full powered trim unresolved | Conditional replayed trim at 18 m/s | Geometry gate open | Conditional replayed trim at 15 m/s |
| Vertical / pitch residual | Not a trimmed test case | -0.063 N / +0.065 N m | Not established | -0.025 N / approximately zero at output precision |
| Aerodynamic slope descriptor | About -22% at stipulated reference, 0–4 deg secant | +19.47%, local fixed-control ratio | Not independently established | +7.76%, local fixed-control ratio |
| Dynamic stability | Historical analyses report instability and demanding pilot control | Not established | Not established | Not established |
| Demonstrated flight | Yes, historical evidence | No | No | No |

The slope row is **not a leaderboard**: derivative intervals, operating points, geometry certainty and reference locations differ. The reconstruction is not the original aircraft, and none of these inviscid calculations is a structural or flight-safety certificate.

## Why the configurations differ

**Canard versus aft tail.** The Wright configuration must be understood through its experimental development, not as a failed attempt at a modern stable trainer. Culick and Jex distinguish control authority from intrinsic pitch/roll stability and analyze the pilot's stabilizing task. Our aft-tail V2 designs seek a restoring fixed-control slope, but that design choice alone does not establish manageable controls or dynamic stability. A canard is not inherently unstable; mass distribution, lifting-surface derivatives and interference matter. [Culick and Jex](https://authors.library.caltech.edu/records/vea6k-35x13), [Papachristodoulou and Culick](https://authors.library.caltech.edu/records/0vz83-2z634).

**Propulsion.** The Flyer used rear propellers and chain transmission; its propellers were developed as rotating wings from aerodynamic research. Counter-rotation reduces the net reaction-torque burden when the two propeller torques balance; it does not erase all asymmetric or gyroscopic effects. Fable resembles this twin-pusher arrangement but its drive/bracing conflicts remain unresolved. Opus's single pusher and Astra's single tractor require explicit reaction-torque and lateral-control evaluation, absent from the present longitudinal model. [Smithsonian Flyer record](https://airandspace.si.edu/collection-objects/wright-1903-flyer/nasm_A19610048000), [Smithsonian propeller record](https://airandspace.si.edu/collection-objects/wright-brothers-propeller-fixed-pitch-1903-wright-flyer/nasm_A19830381000).

**Pilot, structure and controls.** The Flyer's prone pilot and hip-cradle control belonged to an integrated drag/control/structure arrangement; attributing the choice to only one motive would be excessive. Wing warping needs torsional compliance, whereas a rigid lifting-surface calculation does not represent that mechanism. Its rudder/warp coupling addressed control interaction. The AI proposals specify timber/wire frames and moving control surfaces, but unverified joints, cable forces, material allowables and member-mass reconciliation prevent a strength or control-load comparison. Replica structural proof loads must not be assigned to the original machine. [Smithsonian technical drawing](https://howthingsfly.si.edu/media/wright-1903-flyer-0), [Culick and Jex](https://authors.library.caltech.edu/records/vea6k-35x13), [replica structural testing](https://www.wrightflyerproject.org/structural-testing).

**Design cycle.** The Wrights combined literature, kites, gliders, aerodynamic experiments, propulsion development and piloted trials. Our sequence is prompt → proposal → geometry/mass audit → independent numerical feedback → model revision → independent retrim. This is a documented iterative design experiment, but its numerical feedback is not equivalent to wind-tunnel or flight experience. V2 model revisions and evaluator-selected trim settings remain separately attributed. [Smithsonian research history](https://airandspace.si.edu/explore/stories/researching-wright-way).

## Figures and publication boundary

The original coordinate-generated [Flyer reference three-view](../output/stage_threeviews/Wright/wright-flyer-1903.svg) uses the same metric drawing scale as the AI sheets. It shows only reconstructed lifting surfaces; rudders, propellers, structure, tip droop and fabric shape are explicitly omitted rather than assigned guessed coordinates. Its red cross denotes the moment reference, not historical CG. This is a transparent intermediate geometry figure, not a complete Flyer blueprint. Attribution to the source drawing tradition is retained; source scans/PDFs are not republished.

Next gate: resolve historical CG and matched test geometry/conditions; add sourced nonlifting geometry; compare total drag/propulsion and loaded structure. Until then, the defensible conclusion is conditional numerical progress for two AI designs—not that they outperform or even replicate the demonstrated achievement of Flyer I.
