from pathlib import Path
import shutil, json, re
ROOT=Path.cwd()
HERE=Path(__file__).resolve().parent
SRC=ROOT/'output/overleaf/aircraft_complete_v16_draft24'
DST=ROOT/'output/overleaf/aircraft_complete_v16_power_draft25'
skip={'main.pdf','main.log','main_joa_review.pdf','main_joa_review.log','MANIFEST.json','PDF_QA.json','CONTENT_RECOVERY_AUDIT.json'}
shutil.copytree(SRC,DST,ignore=lambda d,n:[x for x in n if Path(d)==SRC and x in skip])
abstract=r'''Three language models were asked to design piloted, powered aircraft using a shared packet of aviation sources dated no later than 1898. Their proposals and subsequent revisions were independently audited for geometry, mass, force and moment balance, propulsion assumptions, and local stability. Initial concepts exposed destabilizing pitch response, interfering controls, or insufficiently supported power targets. Later feedback and corrected evaluator geometry produced a Fable candidate with positive conditional longitudinal margins of 3.98--10.12\% across eight loading states at 13 m/s. These results describe rigid lifting surfaces, not installed-aircraft trim. Replacing the response's induced-drag estimate with the corresponding surface calculation reduces the heavy-case power reserve at 13 m/s to 11.0\%, below the exploratory 15\% target. At 12 m/s the conditional reserve increases to 22.5\%, but stall margin is unknown; at 16 m/s the assumed power deficit is 5.99 kW. Propeller refinement and engine-assumption checks similarly qualify the other two proposals. No design has demonstrated whole-aircraft balance, validated dynamic modes, or structural adequacy. Comparison with successive Wright aircraft distinguishes observed pilot-controlled flight from passive restoring tendencies and emphasizes evidence-producing iteration rather than plausible geometry.'''
assert 100<=len(abstract.split())<=200
section=r'''
\subsection{V16 speed and power sensitivity after surface re-trim}
\label{sec:v16_power_speed}
The apparent power closure in the Fable response is sensitive to the induced-drag
representation. An evaluator-only sensitivity calculation replaces the response's
printed induced-drag coefficient with the fine-grid surface result at the same
speed and mass. It preserves the response's remaining drag assumptions and infers
its propeller efficiency from the printed drag, speed and shaft demand. Consequently,
this calculation does not add two induced-drag estimates, fit an engine map, or
claim a new installed-aircraft equilibrium. With $D_0$ and $P_0$ denoting the printed
total drag and shaft demand for each case, the substitution is
\begin{equation}
\eta_{p,0}=\frac{D_0 V}{P_0},\qquad
D_h=D_0+\tfrac12\rho V^2 S(C_{D_i,s}-C_{D_i,0}),\qquad
P_h=\frac{D_h V}{\eta_{p,0}}
\end{equation}
Here the subscript $s$ identifies the lifting-surface solution and $h$ identifies
the hybrid sensitivity result. Density is 1.225 kg/m$^3$ and reference area is
42 m$^2$. The inferred heavy-case efficiency is approximately 0.45, not a measured
propeller efficiency. The available shaft power remains the response's assumed
$0.95(21.1)=20.045$ kW. Table~\ref{tab:v16_speed_power} compares the three heavy
cases, each at 375.106 kg and the same mass distribution.

\begin{table}[htbp]
\centering\small
\caption{Heavy-case conditional surface and power results; not an accepted operating envelope.}
\label{tab:v16_speed_power}
\begin{tabular}{rrrrrr}
\hline
$V$ (m/s)&$\alpha$ (deg)&$C_{D_i,s}$&$P_h$ (kW)&Reserve (\%)&Headroom (kW)\\
\hline
12 & 9.094 & 0.079577 & 16.362 & 22.51 & 3.683\\
13 & 6.600 & 0.058103 & 18.053 & 11.03 & 1.992\\
16 & 1.902 & 0.026329 & 26.037 & -23.01 & -5.992\\
\hline
\end{tabular}
\end{table}

Reserve is $20.045/P_h-1$; headroom is $20.045-P_h$ in kW. At 13 m/s,
the response's 17.356 kW increases to 18.053 kW. The resulting 0.716 kW shortfall
against $1.15P_h$ must not be confused with an absolute power deficit: the assumed
available power still exceeds demand by 1.992 kW. The 15\% requirement is an
exploratory project screen, not an airworthiness standard. In the nominal
365.106 kg case at the same speed, the analogous substitution gives 13.607 kW.

Two additional fine-grid surface calculations at 12 and 16 m/s converged in lift
and pitch moment with absolute tail incidences of $-2.239$ and $-0.595$ degrees.
Their local surface margins are 10.850 and 8.713\%, respectively. Printed lift
residuals are less than 0.015 N; raw geometry, force and stability hashes were
checked. Speed enters the lift target, without measured Reynolds-dependent
section data. At 12 m/s, $C_L=0.99302$ and $\alpha=9.094$ degrees do not demonstrate
attached flow or adequate stall margin. Lower speed therefore cannot be declared
a solution simply because the assumed shaft-power budget improves. At 16 m/s,
the hybrid demand exceeds the assumed available power by 5.992 kW even though
the restricted lifting-surface equations balance.

These results expose the remaining coupling problem rather than close it.
Propulsion changes force and moment balance, and a larger engine changes mass,
centroid and required lift. The present substitution performs neither feedback
loop. It also leaves the body and bracing drag assumptions, slipstream, thrust-line
moments, section validity and structural deformation unresolved. An accepted
speed envelope requires these effects and stall/control limits to be reconciled
at common operating points. No dynamic-mode or flight acceptance is inferred.

'''
conclusion=r'''
The latest V16 result changes the conditional Fable assessment, not the historical
record above. All three responses are now complete, but response completion is not
an engineering gate. The revised Fable mass distribution and enlarged braced tail
give positive surface-model margins across eight loading states at 13 m/s. Its
claimed heavy-case power closure is not robust to replacing the induced-drag
estimate with the corresponding fine-grid result: the reserve falls to 11.0\%.
The 12 m/s power screen is more favorable but has unverified stall margin, while
the 16 m/s case retains a substantial assumed-power deficit. Thus Fable is a
candidate for further coupled analysis, not a flightworthy winner. The decisive
remaining inputs are installed propulsion and drag, loaded geometry and structural
properties, physical inertia, and justified unsteady derivatives. Until those
inputs support common powered and glide equilibria, numerical eigenvalues would
not constitute validated aircraft modes.

'''
availability=r'''
\paragraph{Records added through V16.}
The complete local package for this revision additionally includes the three
complete V16 responses and the independent mass, geometric-envelope, loading,
surface-trim, propeller and speed--power audits under \texttt{audit\_data/v16}.
The speed--power additions are in \texttt{audit\_data/v16/power\_speed} and include
the two raw speed runs, audit scripts and source hashes. The earlier G8 tag remains
unchanged; these local additions must not be represented as publicly released at
that tag. The package preserves earlier manuscript versions by reference to the
unchanged local draft24 and records the replaced abstract in its revision audit.
Bundled calculation scripts retain provenance paths and may require path adaptation
and the separately obtained solver; this is an audit archive, not a claim of a
fully self-contained executable environment. Before submission, the author must
approve a fixed public data/code release and reconcile its identifier with this
statement. Third-party redistribution restrictions remain in force.

'''
for name in ('main.tex','main_joa_review.tex'):
    old=(SRC/name).read_text(encoding='utf-8')
    a,b=old.index(r'\begin{abstract}'),old.index(r'\end{abstract}')+len(r'\end{abstract}')
    oldabstract=old[a:b]
    new=old[:a]+r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}'+old[b:]
    new=new.replace(r'\section{Discussion: What the Wright Comparison Actually Shows}',section+r'\section{Discussion: What the Wright Comparison Actually Shows}')
    new=new.replace(r'\section*{Data availability}',conclusion+r'\section*{Data availability}')
    new=new.replace(r'\section*{Code availability}',availability+r'\section*{Code availability}')
    # Preserve the entire prior body in order; only the explicitly updated abstract is replaced.
    cursor=0
    for line in (old[:a]+old[b:]).splitlines():
        if not line.strip(): continue
        p=new.find(line,cursor); assert p>=0,line
        cursor=p+len(line)
    assert re.findall(r'\\includegraphics[^\n]+',old)==re.findall(r'\\includegraphics[^\n]+',new)
    (DST/name).write_text(new,encoding='utf-8')
    (DST/(name+'.previous_abstract.txt')).write_text(oldabstract,encoding='utf-8')
assert (DST/'main.tex').read_text().split(r'\begin{document}',1)[1]==(DST/'main_joa_review.tex').read_text().split(r'\begin{document}',1)[1]
bundle=DST/'audit_data/v16/power_speed';bundle.mkdir()
for name in ('fable_v16_power_sensitivity.py','fable_v16_power_sensitivity01.json','fable_v16_speed_screen.py','audit_fable_v16_speed_power.py','build_draft25.py'):
    shutil.copy2(HERE/name,bundle/name)
shutil.copytree(HERE/'fable_v16_speed_screen01',bundle/'fable_v16_speed_screen01')
(DST/'CONTENT_RECOVERY_AUDIT.json').write_text(json.dumps(dict(all_prior_body_preserved_in_order=True,all_18_figures_preserved=True,abstract_revised=True,previous_abstract_archived=True,identical_reading_and_review_body=True,abstract_words=len(abstract.split()),PDF_QA='pending'),indent=2))
(DST/'JOURNAL_READINESS.md').write_text('Full manuscript draft25, not submission authorization. Official guidance checked 2026-09-30: https://aiaa.org/publications/journals/journal-author/ and AIAA ethical standards. Abstract 100-200 words, one paragraph; full body retained. Both PDF layouts pending QA. Open gates: complete public data release, author funding/conflict and affiliation confirmation, reuse permissions, reference-type compliance (web-only entries), length/editor agreement, installed engineering validation. AI disclosure retained; ScholarOne disclosure still requires author action. No flight or dynamic-mode acceptance.\n')
print('DRAFT25 BUILT',len(abstract.split()))
