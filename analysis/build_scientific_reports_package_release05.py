"""Package the main/SI dynamic-gate revision; no TeX compilation claimed."""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "output/overleaf/scientific_reports_aircraft_2026_09_28_release04"
OUT = ROOT / "output/overleaf/scientific_reports_aircraft_2026_09_28_release05"
ZIP = ROOT / "output/delivery/scientific_reports_aircraft_overleaf_release05.zip"


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(ROOT/"paper/article_scientific_reports.tex", OUT/"main.tex")
    shutil.copy2(ROOT/"paper/supplementary_scientific_reports.tex", OUT/"supplementary.tex")
    shutil.copy2(OLD/"references_scientific_reports.tex", OUT/"references_scientific_reports.tex")
    shutil.copytree(OLD/"figures", OUT/"figures")
    shutil.copytree(OLD/"audit_data", OUT/"audit_data")
    shutil.copy2(ROOT/"analysis/results/v2_dynamic_gate01.json",
                 OUT/"audit_data/v2_dynamic_gate.json")
    shutil.copy2(ROOT/"analysis/flight_dynamics_gate_v2.py",
                 OUT/"audit_data/flight_dynamics_gate_v2.py")
    shutil.copy2(ROOT/"paper/DATA_AVAILABILITY.md", OUT/"DATA_AVAILABILITY.md")
    (OUT/"README.md").write_text(
        "# Historical-aircraft LLM manuscript: dynamic-gate revision\n\n"
        "Compile main.tex and supplementary.tex separately with pdfLaTeX. "
        "The main document has seven figures and two tables; the supplement "
        "has six figures and nine tables. The new Table S9 reports a reduced "
        "two-state alpha/pitch-rate sign screen, not installed-aircraft "
        "eigenmodes. The missing full inertia and unsteady/lateral derivatives "
        "are not silently zero-filled. Figure sources are unchanged from "
        "release04.\n\nThe full research record and model-feedback prompts are "
        "versioned in the public project tag aircraft-sr-2026-09-28-r3. "
        "The author should compile and visually proof both documents before "
        "journal submission. No flightworthiness or journal acceptance is "
        "claimed.\n", encoding="utf-8")
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "x", zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
    print(f"package={OUT.name} zip_bytes={ZIP.stat().st_size}")


if __name__ == "__main__":
    main()
