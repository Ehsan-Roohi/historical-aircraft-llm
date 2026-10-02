"""Integrate the evaluator correction while retaining the complete article."""
from pathlib import Path
import json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'output/overleaf/aircraft_complete_restored_draft20'
DST=ROOT/'output/overleaf/aircraft_complete_corrected_draft21'
DATA=ROOT/'analysis/results/v15_fable_corrected_surface02'

def main():
    audit=json.loads((DATA/'audit.json').read_text())
    f=json.loads((DATA/'fine/summary.json').read_text());c=json.loads((DATA/'coarse/summary.json').read_text())
    t=f['trim'];sf=f['AVL_stability_derivatives_raw_labels'];sc=c['AVL_stability_derivatives_raw_labels']
    s=r'''\subsection{V15 Fable: corrected surface-model trim and derivative audit}
\label{sec:v15-fable-lateral}

An evaluator-input error was identified after the first lateral screen.
The upper-wing center and its adjoining moving tips had different AVL
\texttt{COMPONENT} identifiers. AVL applies different vortex-core treatment
between components; its manual requires constituent surfaces of one component
to share an identifier \cite{ref22}. At unchanged geometry, mesh, angle of
attack and tail command, changing only the tip identifier from 3 to 2 restored
$C_L$ from 0.74700 to 0.79678 and $C_m$ from 0.00762 to printed zero.
The earlier continuous-wing result was $C_L=0.79677$. Thus the previously
reported lift loss was an evaluator-setting artifact. The associated
$6.662^\circ$ angle of attack, $-3.508^\circ$ tail command and lateral slopes
are retained in the archive as superseded results, not evidence of a physical
hinge-gap effect or a required aircraft redesign.

The corrected model also places the fin and rudder in one component and
aligns their spanwise vortex stations over the common height, $z=1.2$--1.8 m.
The rudder's lower extension, $z=0.8$--1.2 m, is represented separately with
the same command and component identifier. The earlier tail control used
an AVL hinge fraction of 0.25, which denotes an aft-chord flap. The proposal
instead specifies an all-moving horizontal plane. Its aerodynamic command
now rotates normals over the full chord; the physical quarter-chord pivot
is retained as mechanism metadata. This is still a small-disturbance
normal-rotation model: it does not rotate occupied solids, calculate hinge
loads, prove clearance or resolve a real hinge gap. No model-authored
coordinates or mass entries were changed by these evaluator corrections.

Using the assumed mass 353.2 kg, speed 13 m/s, density 1.225 kg/m$^3$ and
reference area 42 m$^2$, the target is $C_L=0.796708$.
'''
    s+=f"The corrected fine-mesh surface balance gives $\\alpha={t['Alpha']:.5f}^\\circ$, tail command ${t['pitch']:.5f}^\\circ$, and absolute tail incidence ${t['tail_absolute_incidence_deg']:.5f}^\\circ$ after adding the $-4^\\circ$ rigging. The printed coefficients are $C_L={t['CLtot']:.5f}$ and $C_m=0$. The corresponding coarse values are $\\alpha={c['trim']['Alpha']:.5f}^\\circ$ and tail command ${c['trim']['pitch']:.5f}^\\circ$. These are separately solved surface-model balances; body, gear, propeller, slipstream and profile drag remain outside the calculation. Lateral zero residuals at the neutral condition follow from symmetry.\n\n"
    s+=r'''Thirteen states on each mesh comprise the neutral point and positive/negative
sideslip, tip-control and rudder perturbations at two amplitudes. Sideslip
steps are 3 and 1.5 deg; tip steps are 4 and 2 deg; rudder steps are 5 and
2.5 deg. Each mesh uses its own corrected trim. The meshes have 8/12 chordwise
panels and 32/64 reference wing spanwise panels, with matched vertical-tail
stations. Therefore mesh comparisons include the small corresponding trim
change. Printed-force finite differences also retain output-rounding error.

\begin{table}[p]\centering\small
\caption{Corrected Fable V15 body-axis finite-difference slopes at each mesh's conditional surface trim. Fine-step difference compares the smaller and larger perturbations on the fine mesh; all entries are per radian.}
\label{tab:v15-fable-lateral}
\begin{tabular}{lrrr}\toprule
Slope & Coarse & Fine & Fine-step absolute difference\\\midrule
'''
    for label,var,coeff in [(r'C_{Y_\beta}','beta','CYtot'),(r'C_{l_\beta}','beta','Cltot'),(r'C_{n_\beta}','beta','Cntot'),(r'C_{l_{\delta_{\rm tip}}}','tip','Cltot'),(r'C_{n_{\delta_{\rm tip}}}','tip','Cntot'),(r'C_{n_{\delta_r}}','rudder','Cntot')]:
        d=audit['derivative_sensitivity'][var][coeff]
        s+=f"${label}$ & ${d['coarse_small_step']:+.6f}$ & ${d['fine_small_step']:+.6f}$ & ${d['fine_step_absolute_difference']:.6f}$\\\\\n"
    s+=r'''\bottomrule\end{tabular}\end{table}

Body and stability axes must not be interchanged. The force-file finite
differences in Table~\ref{tab:v15-fable-lateral} use AVL standard body axes,
whereas its \texttt{ST} matrix reports stability-axis moments and rates.
The conversion used for comparison is
\begin{equation}
\begin{bmatrix}C_{l'}\\C_{n'}\end{bmatrix}=
\begin{bmatrix}\cos\alpha&\sin\alpha\\-\sin\alpha&\cos\alpha\end{bmatrix}
\begin{bmatrix}C_l\\C_n\end{bmatrix}.
\end{equation}
'''
    s+=f"The fine-mesh stability-axis sideslip slopes are $C_{{l'_\\beta}}={sf['Clb']:+.6f}$ and $C_{{n'_\\beta}}={sf['Cnb']:+.6f}$ per radian. The rotation reconciles the finite-difference slopes with the analytic matrix to within $2\\times10^{{-4}}$ per radian on both meshes. A small body-axis rolling slope of opposite sign cannot be used as a contradictory stability verdict.\n\n"
    s+=r'''\begin{table}[p]\centering\small
\caption{Corrected Fable V15 quasi-steady stability-axis derivative predictions. Angle slopes are per radian; rate derivatives use $p'b/(2V)$, $qc/(2V)$ and $r'b/(2V)$. They are not a measured dynamic model.}
\label{tab:fable-corrected-rates}
\begin{tabular}{lrr}\toprule
Derivative & Coarse & Fine\\\midrule
'''
    for key,label in [('CLa',r'C_{L_\alpha}'),('Cma',r'C_{m_\alpha}'),('Cmq',r'C_{m_q}'),('CLq',r'C_{L_q}'),('CYp',r'C_{Y_{p\prime}}'),('CYr',r'C_{Y_{r\prime}}'),('Clp',r'C_{l\prime_{p\prime}}'),('Clr',r'C_{l\prime_{r\prime}}'),('Cnp',r'C_{n\prime_{p\prime}}'),('Cnr',r'C_{n\prime_{r\prime}}')]:
        s+=f"${label}$ & ${sc[key]:+.6f}$ & ${sf[key]:+.6f}$\\\\\n"
    s+=r'''\bottomrule\end{tabular}\end{table}

The negative pitch-, roll- and yaw-rate moment slopes provide predicted
damping tendencies within this surface model. They do not determine the
coupled aircraft modes. The positive directional restoring slope must be
considered together with roll--yaw coupling, inertia, force derivatives,
control authority and propulsion. Neither the sign of one derivative nor
AVL's reduced spiral diagnostic establishes a handling-quality result.
'''
    s+=f"The apparent surface-only longitudinal margin $-C_{{m_\\alpha}}/C_{{L_\\alpha}}$ is {audit['apparent_surface_only_margin_percent']['coarse']:.3f}\\% on the coarse mesh and {audit['apparent_surface_only_margin_percent']['fine']:.3f}\\% on the fine mesh; this small conditional value is not an installed neutral-point measurement.\n\n"
    s+=r'''Full physical inertia, unsteady derivatives such as
$C_{m_{\dot\alpha}}$, installed propulsion and a validated force/moment map
remain missing. Aircraft eigenvalues are therefore not reported. The raw
corrected cases, frame checks, perturbation comparisons and hashes are in
\texttt{v15\_fable\_corrected\_surface02}; the old inputs and correction note
remain available to expose rather than conceal the evaluator error.
'''
    if DST.exists(): raise FileExistsError(DST)
    shutil.copytree(SRC,DST)
    for filename in ['main.tex','main_joa_review.tex']:
        text=(SRC/filename).read_text(encoding='utf-8')
        start=text.index(r'\subsection{V15 Fable: lateral--directional surface-model sensitivity}')
        end=text.index(r'\section{Discussion: What the Wright Comparison Actually Shows}',start)
        text=text[:start]+s+'\n\n'+text[end:]
        text=text.replace('Representing its all-moving tip panels separately changed the predicted lift and required a new surface-only trim; an added fin/rudder model predicted a directional restoring slope and roll--yaw control coupling, but the roll response to sideslip remained small and mesh-sensitive.','An evaluator component-grouping error was identified and corrected before recomputing surface trim, lateral control slopes and quasi-steady rate derivatives on two meshes. The corrected model predicts directional restoring and rate-damping tendencies, with a small conditional longitudinal margin.')
        text=text.replace('Separating its proposed tip panels changes the power-off surface-model balance, and the expanded lateral screen predicts a restoring directional slope with adverse-yaw-like control coupling; neither is a validated whole-aircraft derivative or mode.','The original split-tip lift shift was traced to an evaluator component-grouping error. Correcting this setting, the tail command representation and fin/rudder panel alignment permits a new conditional trim and static/control/rate screen; these predictions still do not establish aircraft modes.')
        marker=r'\subsection{V15 Fable: a two-axis surface balance is not six-component trim}'
        assert marker in text
        text=text.replace(marker,marker+'\n'+r'\noindent\textit{Version note.} The following retained wing--tail calculation precedes the component and all-moving-tail input correction. Its numerical point is historical; the corrected expanded-model result follows in Section~\ref{sec:v15-fable-lateral}.'+'\n')
        (DST/filename).write_text(text,encoding='utf-8')
    (DST/'v15_fable_lateral_screen.tex').write_text(s,encoding='utf-8')
    shutil.copytree(DATA,DST/'audit_data/v15_fable_corrected_surface02')
    for name in ['v15_fable_corrected_surface_screen.py','audit_v15_corrected_surface.py','build_corrected_complete_draft21.py']:
        shutil.copy2(ROOT/'analysis'/name,DST/'audit_data'/name)
    shutil.copy2(ROOT/'paper/DRAFT20_AVL_COMPONENT_CORRECTION.txt',DST/'DRAFT20_AVL_COMPONENT_CORRECTION.txt')
    (DST/'README.md').write_text('# Complete corrected aircraft article - draft21\n\nUse main.tex for the complete reading article. All 17 figure inclusions from draft20 remain. The V15 Fable section explicitly corrects the evaluator input error, retains the superseded history, and adds corrected trim, static/control slopes, rate derivatives and two-mesh/two-step comparisons. main_joa_review.tex has the same scientific content in the review layout. Neither is a flight-validated design.\n\nThe original draft20 remains unchanged. The PDF and manifest must be refreshed after compilation; source completeness is checked against draft20.\n',encoding='utf-8')
    before=re.findall(r'\\includegraphics[^\n]+',(SRC/'main.tex').read_text())
    after=re.findall(r'\\includegraphics[^\n]+',(DST/'main.tex').read_text())
    assert before==after and len(after)==17
    print('draft21 complete content preserved; corrected section and rate table integrated')

if __name__=='__main__':main()
