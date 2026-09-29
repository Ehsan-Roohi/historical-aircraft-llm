"""Mechanically convert the frozen study text to an AIAA-review-format draft.

This is a formatting build, not an engineering endorsement or a submission.
The source study remains unchanged. Run from any working directory.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "article_scientific_reports.tex"
TARGET = ROOT / "paper" / "article_journal_of_aircraft.tex"
REFERENCES = ROOT / "paper" / "references_journal_of_aircraft.tex"
REFERENCE_SOURCE = REFERENCES  # Frozen reference text in the project tree.

PREAMBLE = r"""% Journal of Aircraft review-format draft. Not yet submission-ready.
% AIAA minimum: US letter, 10-point, single column, double-spaced.
\documentclass[10pt,letterpaper]{article}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage[margin=1in]{geometry}
\usepackage{setspace}
\usepackage{amsmath,amssymb,graphicx,booktabs,tabularx,array,float,pdflscape}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}
\usepackage{url}
\usepackage[font=small,labelfont=bf]{caption}
\doublespacing
\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.16}
\newcommand{\figdir}{figures}
\title{Auditing Historically Constrained Language-Model Aircraft Against the Wright Flyer}
\author{Ehsan Roohi\\
\small Department of Mechanical and Industrial Engineering\\
\small University of Massachusetts Amherst, Amherst, MA 01003, USA\\
\small Corresponding author: \texttt{roohie@umass.edu}}
\date{}
\begin{document}
\maketitle
"""

ABSTRACT = r"""\begin{abstract}
Three language models received the same paraphrased aviation sources dated no later than 1898 and were asked to design a piloted, powered airplane. This study records their initial concepts and subsequent responses to engineering feedback, then independently checks geometry, mass accounting, conditional force and moment balance, power assumptions, and selected local stability derivatives. The three systems produced different configurations; none reproduced the Wright Flyer's complete layout. At the initial evaluable stage, the Opus design had the strongest conditional longitudinal balance, whereas the Astra design had a destabilizing fixed-control pitch slope and the Fable design had an interfering tail mechanism. Later feedback improved some component definitions and reconciled Fable's mass ledger, but did not establish installed engine--propeller performance or full-aircraft dynamic modes. The completed Opus installation response is an analytical candidate, not a validated airplane. No proposed configuration has yet met a whole-aircraft flight-possibility or dynamic-stability gate. The comparison with the historically flown Wright Flyer illustrates why an auditable design-and-test cycle, rather than plausible geometry or isolated equilibrium, is necessary to support a flight claim.
\end{abstract}

\section*{Nomenclature}
\noindent\begin{tabular}{@{}ll@{}}
$C_{m_\alpha}$ & fixed-control pitching-moment slope, rad$^{-1}$\\
$C_{m_q}$ & pitch-rate pitching-moment derivative, nondimensional\\
$D$ & installed aircraft drag, N\\
$L$ & lift, N\\
$P_e$ & engine-side output power, W\\
$P_{\mathrm{shaft}}$ & power at propeller shafts, W\\
$V$ & flight speed, m/s (not a design-version label)\\
$\eta_g$ & engine-to-propeller drive efficiency\\
$\eta_p$ & useful-to-propeller-shaft efficiency\\
\end{tabular}
"""

CAPTIONS = {
    "fig:wrightphoto": "Flyer I during its first flight on 17 December 1903. Photograph by J. T. Daniels; Library of Congress.",
    "fig:config": "Plan views of the three V1 lifting-surface models and a separate Wright reconstruction; markers denote calculated model centers of gravity.",
    "fig:astrav2": "Astra V2 plan, side, and front views at neutral controls. Declared envelopes are shown; the later design is not flight-validated.",
    "fig:fablev2": "Fable V2 three views at neutral controls. Split tail halves address the original fin intersection; installed interfaces remain unresolved.",
    "fig:opusv2": "Opus V2 plan, side, and front views. Only specified surfaces and structural node chains are connected.",
    "fig:balance": "Applied forces and residuals in longitudinal balance. Dashed residual arrows are diagnostic quantities, not additional applied loads.",
    "fig:v2forces": "Conditional V2 longitudinal loads for Astra and Opus, alongside Fable's unverified model-reported loads. Silhouettes and arrow locations are schematic.",
}

AI_ACK = r"""\section*{Acknowledgments and use of artificial intelligence}
The three named language models were the experimental design generators. Their
archived outputs were treated as proposals, not as independent technical
evidence. An OpenAI coding assistant assisted with research organization,
drafting and editing, analysis-code development, and figure production.
Model-assisted prose, calculations, citations, and graphics require author
review; no language model is an author. The human author is responsible for
the submitted scientific claims, source attribution, and figure accuracy.
The same research, writing, and figure uses must also be disclosed in the
ScholarOne submission fields. Funding and conflict-of-interest information
must be confirmed by the author before submission.
"""

GROUND_RESULT = r"""\subsection{Latest-candidate rigid ground-contact screen}
After Fable's V13 mass correction, the V12 nominal ground-load line based on
353.8 kg is superseded. For its declared front-pair and rear contact stations
$x_f=0.40$ and $x_r=3.20$ m, respectively, static equilibrium gives
\begin{equation}\label{eq:groundreactions}
R_f=mg\frac{x_r-x_{CG}}{x_r-x_f},\qquad R_r=mg-R_f
\end{equation}
where $R_f$ is the total front-wheel reaction and $R_r$ the rear reaction.
Independent recomputation of all eight declared V13 mass/CG states gives
positive reactions. The nominal 354.3 kg state gives 2072.079 N at the front
pair and 1403.604 N at the rear; across the cases these range from 1846.975
to 2188.572 N and from 1301.125 to 1418.494 N, respectively. In a rigid
nose-down rotation about the front contact line, the specified skid point
contacts at $20.556^\circ$; this does not cover tire compression, braking,
or an occupied-solid sweep.

For Opus V12, the specified front upturn of the flat runner contacts the
ground at $41.186^\circ$ nose-down in a rigid rotation about the front end
of the flat segment. A specified lower/front nacelle-box corner would reach
ground later, at $79.216^\circ$ under the same idealization, and all four
reported longitudinal CG projections lie between the flat-runner endpoints.
These selected-point checks do not establish the first contact of the entire
occupied, loaded aircraft or the distribution of load along the runner.
Astra V12 supplies no adopted installed geometry for the corresponding test.
The exact source hashes, inputs and all Fable cases are recorded in the frozen
ground-contact audit; none of these ground results is a flight-stability
derivative.

"""

INERTIA_RESULT = r"""\subsection{Centroid-only inertia screen}
For the latest complete Fable V13 and Opus V12 mass ledgers, the evaluator
assembled the parallel-axis contribution
\begin{equation}\label{eq:parallelaxis}
\mathbf J_{\mathrm{parallel}}=\sum_i m_i
\left[(\mathbf d_i\cdot\mathbf d_i)\mathbf I-\mathbf d_i\mathbf d_i^T\right],
\qquad \mathbf d_i=\mathbf r_i-\mathbf r_{CG},
\end{equation}
from declared component-centroid locations. The diagonal $(J_{xx},J_{yy},
J_{zz})$ contributions are $(282.406,522.525,668.278)$ kg m$^2$ for Fable
and $(131.713,914.293,782.580)$ kg m$^2$ for Opus. These are conditional
lower bounds, not measured aircraft inertias. The actual tensor also contains
the unknown intrinsic tensor of every component, including pilot, wings,
engine and propellers. The complete matrices, coordinate convention and
source hashes are in the evaluator's inertia audit. Astra V12 has no adopted
installed ledger. No modal eigenvalues are computed from these incomplete
tensors; aerodynamic rate and unsteady derivatives are also missing.

"""

CLEARANCE_RESULT = r"""\subsection{Nominal installation-gap screen}
Fable V13 explicitly retained the V12 occupied geometry. From its declared
coordinate intervals, six one-axis rigid separations were independently
recomputed; the smallest is only 0.010 m between the tank top and upper
longeron. The engine-to-frame side gap is 0.020 m and the nominal inboard
propeller-disc-to-frame gap is 0.050 m. Opus V12 itself reports selected
0.010--0.050 m gaps near the engine/shaft, bearer/wing, gear and control
interfaces, but these have not been independently reconstructed as complete
three-dimensional solids. A positive nominal gap is not a loaded or swept
clearance: thickness, assembly tolerances, propeller motion, structural
deflection and control travel are unbounded. The source-hashed one-axis
calculations and model-reported values are kept separate in the clearance
audit. No aircraft passes the installed-geometry gate on these data.

"""


def main():
    source = SOURCE.read_text(encoding="utf-8")
    _, body = source.split("\\section{Introduction}", 1)
    body = "\\section{Introduction}" + body
    body = body.replace(
        "\\input{references_scientific_reports.tex}",
        "\\input{references_journal_of_aircraft.tex}")
    for label, short_caption in CAPTIONS.items():
        label_marker = r"\label{" + label + "}"
        if body.count(label_marker) != 1:
            raise ValueError(f"Expected exactly one label for {label}")
        label_at = body.index(label_marker)
        caption_at = body.rfind(r"\caption{", 0, label_at)
        figure_at = body.rfind(r"\begin{figure}", 0, label_at)
        if caption_at < figure_at or figure_at < 0:
            raise ValueError(f"Caption not inside a figure for {label}")
        depth = 1
        cursor = caption_at + len(r"\caption{")
        while depth and cursor < label_at:
            if body[cursor] == "{" and body[cursor - 1] != "\\":
                depth += 1
            elif body[cursor] == "}" and body[cursor - 1] != "\\":
                depth -= 1
            cursor += 1
        if depth or body[cursor:label_at].strip():
            raise ValueError(f"Cannot isolate caption for {label}")
        body = (body[:caption_at] + r"\caption{" + short_caption + "}" +
                body[label_at:])
    for label in ("fig:config", "fig:astrav2", "fig:fablev2", "fig:opusv2"):
        label_at = body.index(r"\label{" + label + "}")
        begin_at = body.rfind(r"\begin{figure}", 0, label_at)
        end_at = body.index(r"\end{figure}", label_at) + len(r"\end{figure}")
        if begin_at < 0:
            raise ValueError(f"Missing figure environment: {label}")
        body = (body[:begin_at] + "\\begin{landscape}\n" +
                body[begin_at:end_at] + "\n\\end{landscape}" + body[end_at:])
    body = body.replace(
        "Opus's first V12 response stopped at the specified output-token limit and is retained as incomplete. One source-identical, separately logged replay with a larger limit returned",
        r"Opus's first V12 response stopped at the specified output-token limit and is retained as incomplete. A separately logged, source-identical 48,000-token replay \emph{completed} and returned")
    body = body.replace(
        "Limited V2 lifting-surface probes exist for Astra and Opus, but they are not a complete matched retrim or validation; Fable's geometry reconciliation remains a prerequisite.",
        "Astra and Opus V2 received independent conditional longitudinal retrims, but not complete six-component whole-aircraft trim or validation; Fable's geometry reconciliation remains a prerequisite.")
    body = body.replace(
        "Figure~\\ref{fig:balance} connects the balance equations to an aircraft silhouette. The left panel shows applied forces; the right panel shows the three \\emph{resulting imbalances}, which are bookkeeping outputs rather than additional physical forces.",
        "Figure~\\ref{fig:balance} connects the balance equations to an aircraft silhouette. The left panel shows applied forces; the right panel shows the three \\emph{resulting imbalances}, which are bookkeeping outputs rather than additional physical forces. Its forward/up force directions do not redefine the model-specific aft-positive station coordinates used for geometry and mass moments.")
    body = body.replace(
        "Figure~\\ref{fig:v2forces} applies the same bookkeeping to the three \\emph{latest} proposed architectures.",
        "Figure~\\ref{fig:v2forces} applies the same bookkeeping to the three \\emph{rendered V2} architectures, not the later V12/V13 candidates.")
    body = body.replace(
        r"\includegraphics[width=\linewidth]{\figdir/configuration_comparison_v3.png}",
        r"\includegraphics[width=.96\linewidth]{\figdir/configuration_comparison_v3.png}")
    body = body.replace(
        "No physical construction, human flight test or journal submission is authorized by these computational results.",
        "These computational results do not authorize physical construction or occupied flight; journal claims must retain the stated evidence limits.")
    marker = r"\subsection{Which generated design is strongest on present evidence?}"
    if body.count(marker) != 1:
        raise ValueError("Could not locate model-comparison section")
    body = body.replace(marker, GROUND_RESULT + CLEARANCE_RESULT + INERTIA_RESULT + marker)
    start = body.index("\\section*{Author contributions and competing interests}")
    end = body.index("\\begingroup\\raggedright", start)
    body = body[:start] + AI_ACK + "\n" + body[end:]
    target = PREAMBLE + "\n" + ABSTRACT + "\n" + body
    abstract = ABSTRACT.split("\\begin{abstract}", 1)[1].split("\\end{abstract}", 1)[0]
    count = len(re.findall(r"\b[\w-]+\b", re.sub(r"\\[A-Za-z]+", "", abstract)))
    if not 100 <= count <= 200:
        raise ValueError(f"Abstract word count outside AIAA range: {count}")
    for caption in CAPTIONS.values():
        if len(caption.split()) > 25:
            raise ValueError(f"Caption exceeds AIAA limit: {caption}")
    source_refs = REFERENCE_SOURCE.read_text(encoding="utf-8")
    entries = re.findall(
        r"(\\bibitem\{([^}]+)\}.*?)(?=\\bibitem\{|\\end\{thebibliography\})",
        source_refs, flags=re.DOTALL)
    mapping = {key: block.strip() for block, key in entries}
    cited = [key.strip() for group in re.findall(r"\\cite\{([^}]+)\}", target)
             for key in group.split(",")]
    ordered = list(dict.fromkeys(cited))
    if set(ordered) != set(mapping) or len(mapping) != len(entries):
        raise ValueError("Reference mismatch or duplicate item")
    refs = ("% Ordered by first citation for AIAA journal style.\n"
            "\\begin{thebibliography}{99}\n" +
            "\n\n".join(mapping[key] for key in ordered) +
            "\n\\end{thebibliography}\n")
    TARGET.write_text(target, encoding="utf-8")
    REFERENCES.write_text(refs, encoding="utf-8")
    print(f"Wrote {TARGET.name}, {REFERENCES.name}; abstract {count} words")


if __name__ == "__main__":
    main()
