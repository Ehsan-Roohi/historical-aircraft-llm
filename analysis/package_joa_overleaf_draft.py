"""Package the auditable Journal of Aircraft review draft for Overleaf.

The package is a formatting and evidence preview, not submission approval.
"""

from pathlib import Path
import hashlib
import json
import shutil
import zipfile


PROJECT = Path(__file__).resolve().parents[3]
PUBLIC = Path(__file__).resolve().parents[1]
BASELINE = PROJECT / "output/overleaf/aircraft_ast_2026_09_28_release09"
DISPLAY = PROJECT / "output/figures_joa_draft01"
DISPLAY2 = PROJECT / "output/figures_joa_draft02"
DISPLAY3 = PROJECT / "output/figures_joa_draft03"
DISPLAY4 = PROJECT / "output/figures_joa_draft04"
DISPLAY5 = PROJECT / "output/figures_joa_draft05"
DEST = PROJECT / "output/overleaf/aircraft_joa_2026_09_29_draft15"
ARCHIVE = PROJECT / "output/delivery/aircraft_joa_overleaf_draft15.zip"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if DEST.exists() or ARCHIVE.exists():
        raise FileExistsError("Refusing to overwrite a prior frozen package")
    DEST.mkdir(parents=True)
    figures = DEST / "figures"
    figures.mkdir()
    for file in (BASELINE / "figures").iterdir():
        if file.is_file():
            shutil.copy2(file, figures / file.name)
    for file in DISPLAY.glob("*.png"):
        if file.name == "wright_threeview_reconstruction.png" or file.name.endswith("_v2_threeview.png"):
            shutil.copy2(file, figures / file.name)
    for file in DISPLAY2.glob("*.png"):
        shutil.copy2(file, figures / file.name)
    for file in DISPLAY3.glob("*.png"):
        shutil.copy2(file, figures / file.name)
    for folder in (DISPLAY4, DISPLAY5):
        for file in folder.glob("*.png"):
            shutil.copy2(file, figures / file.name)
    sources = DEST / "figure_sources"
    sources.mkdir()
    for file in DISPLAY.glob("*.svg"):
        shutil.copy2(file, sources / file.name)
    for file in DISPLAY2.glob("*.svg"):
        shutil.copy2(file, sources / file.name)
    for file in DISPLAY3.glob("*.svg"):
        shutil.copy2(file, sources / file.name)
    for folder in (DISPLAY4, DISPLAY5):
        for file in folder.glob("*.svg"):
            shutil.copy2(file, sources / file.name)
    shutil.copy2(DISPLAY / "manifest.json", sources / "threeview_display_manifest.json")
    shutil.copy2(DISPLAY2 / "MANIFEST.json", sources / "display_derivatives_manifest.json")
    shutil.copy2(DISPLAY3 / "MANIFEST.json", sources / "v2_force_display_manifest.json")
    shutil.copy2(DISPLAY4 / "MANIFEST.json", sources / "response_plots_display_manifest.json")
    shutil.copy2(DISPLAY5 / "MANIFEST.json", sources / "v0_obliques_display_manifest.json")
    shutil.copy2(PUBLIC / "analysis/render_joa_v2_force_moment.js",
                 sources / "render_joa_v2_force_moment.js")
    shutil.copy2(PUBLIC / "analysis/render_joa_threeviews.js",
                 sources / "render_joa_threeviews.js")
    shutil.copy2(PUBLIC / "analysis/render_joa_supplementary_plots.js",
                 sources / "render_joa_supplementary_plots.js")
    shutil.copy2(PUBLIC / "analysis/render_joa_archival_v0.js",
                 sources / "render_joa_archival_v0.js")
    shutil.copy2(PROJECT / "analysis/draw_v2_force_moment.py",
                 sources / "archived_draw_v2_force_moment.py")
    shutil.copy2(PROJECT / "analysis/results/v2_trim_solve01/compact_report.json",
                 sources / "archived_v2_compact_report.json")
    shutil.copy2(PUBLIC / "paper/article_journal_of_aircraft.tex", DEST / "main.tex")
    shutil.copy2(PUBLIC / "paper/references_journal_of_aircraft.tex",
                 DEST / "references_journal_of_aircraft.tex")
    shutil.copy2(PUBLIC / "paper/supplementary_scientific_reports.tex",
                 DEST / "supplementary.tex")
    shutil.copy2(PUBLIC / "paper/journal_of_aircraft_readiness.md",
                 DEST / "JOURNAL_READINESS.md")
    shutil.copy2(PUBLIC / "paper/v14_rigid_ground_gate01.md",
                 DEST / "V14_RIGID_GROUND_GATE.md")
    shutil.copy2(PUBLIC / "paper/v14_inertia_gate01.md",
                 DEST / "V14_INERTIA_GATE.md")
    shutil.copy2(PUBLIC / "paper/v14_static_clearance_budget01.md",
                 DEST / "V14_STATIC_CLEARANCE_BUDGET.md")
    shutil.copy2(PUBLIC / "paper/v14_fable_power_fixed_point01.md",
                 DEST / "V14_FABLE_POWER_FIXED_POINT.md")
    shutil.copy2(PUBLIC / "paper/joa_editorial_gate01.md",
                 DEST / "JOA_EDITORIAL_GATE.md")
    shutil.copy2(PUBLIC / "paper/joa_figure_gate01.md",
                 DEST / "JOA_FIGURE_GATE.md")
    audit = DEST / "audit_data"
    audit.mkdir()
    shutil.copy2(PUBLIC / "analysis/results/v14_rigid_ground_gate01.json",
                 audit / "v14_rigid_ground_gate01.json")
    shutil.copy2(PUBLIC / "analysis/results/v14_inertia_lower_bounds01.json",
                 audit / "v14_inertia_lower_bounds01.json")
    shutil.copy2(PUBLIC / "analysis/results/v14_static_clearance_budget01.json",
                 audit / "v14_static_clearance_budget01.json")
    shutil.copy2(PUBLIC / "analysis/results/v14_fable_power_fixed_point01.json",
                 audit / "v14_fable_power_fixed_point01.json")
    shutil.copy2(PUBLIC / "analysis/results/joa_editorial_gate01.json",
                 audit / "joa_editorial_gate01.json")
    shutil.copy2(PUBLIC / "analysis/results/joa_figure_display_gate01.json",
                 audit / "joa_figure_display_gate01.json")
    for name in ("audit_v14_rigid_ground.py", "audit_v14_inertia_lower_bounds.py",
                 "audit_v14_static_clearance_budget.py",
                 "audit_v14_fable_power_fixed_point.py",
                 "test_v14_inertia_lower_bounds.py"):
        shutil.copy2(PUBLIC / "analysis" / name, audit / name)
    (DEST / "README.md").write_text(
        "# Journal of Aircraft review-format draft\n\n"
        "Set `main.tex` as Overleaf's main document; compile with pdfLaTeX. "
        "`supplementary.tex` is a separate main document. This is a 10-point, "
        "letter-paper, single-column, double-spaced review draft. It is not "
        "submission-ready: installed propulsion, full trim and dynamic modes "
        "remain unverified; references and all figures require final AIAA "
        "audit, and author funding/conflict declarations remain to be confirmed. "
        "The enhanced three-view and V1 comparison PNGs are typographic "
        "derivatives of frozen SVGs, not V12/V13 geometry; the force-balance "
        "plate is a new evaluator schematic. The V2 force/moment plate was "
        "redrawn for print legibility, preserving the frozen V2 values and "
        "the model-claim distinction; its renderer and archived numerical "
        "inputs are in `figure_sources`. The supplementary response plots "
        "and V0 obliques were re-rasterized from unchanged SVG sources; "
        "the dense V0 text is still too small for print and needs re-layout; "
        "adjacent readable component keys are now included in the supplement. "
        "The ground, clearance, Fable power–mass and centroid-only inertia "
        "audits are included here and in the intended G7 draft research tag; "
        "V14 prompts remain FROZEN_UNSENT.\n",
        encoding="utf-8")
    records = []
    for file in sorted(DEST.rglob("*")):
        if file.is_file():
            records.append({"path": file.relative_to(DEST).as_posix(),
                            "sha256": digest(file), "bytes": file.stat().st_size})
    (DEST / "MANIFEST.json").write_text(json.dumps({
        "status": "DRAFT_NOT_SUBMISSION_READY",
        "source_parent_commit": "7d85e762bd2fa051521d007388149c09ba98913d",
        "intended_release_tag": "aircraft-joa-2026-09-29-g7-draft",
        "files": records}, indent=2) + "\n", encoding="utf-8")
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "x", zipfile.ZIP_DEFLATED) as handle:
        for file in sorted(DEST.rglob("*")):
            if file.is_file():
                handle.write(file, file.relative_to(DEST).as_posix())
    with zipfile.ZipFile(ARCHIVE) as handle:
        if handle.testzip() is not None:
            raise RuntimeError("ZIP integrity check failed")
    print(ARCHIVE.name, ARCHIVE.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
