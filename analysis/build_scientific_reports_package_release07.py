"""Package the reviewed V3-return disclosure without changing V1/V2 figures."""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "output/overleaf/scientific_reports_aircraft_2026_09_28_release06"
OUT = ROOT / "output/overleaf/scientific_reports_aircraft_2026_09_28_release07"
ZIP = ROOT / "output/delivery/scientific_reports_aircraft_overleaf_release07.zip"


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(ROOT / "paper/article_scientific_reports.tex", OUT / "main.tex")
    shutil.copy2(ROOT / "paper/supplementary_scientific_reports.tex", OUT / "supplementary.tex")
    shutil.copy2(OLD / "references_scientific_reports.tex", OUT / "references_scientific_reports.tex")
    shutil.copytree(OLD / "figures", OUT / "figures")
    shutil.copytree(OLD / "audit_data", OUT / "audit_data")
    shutil.copy2(ROOT / "analysis/results/v9_integrated_response_audit.json",
                 OUT / "audit_data/v9_integrated_response_audit.json")
    shutil.copy2(ROOT / "paper/v9_integrated_response_gate.md", OUT / "V3_RESPONSE_GATE.md")
    shutil.copy2(ROOT / "paper/DATA_AVAILABILITY.md", OUT / "DATA_AVAILABILITY.md")
    (OUT / "README.md").write_text(
        "# Historical-aircraft LLM manuscript: V3 return disclosure\n\n"
        "Compile main.tex and supplementary.tex separately with pdfLaTeX. "
        "The main paper retains seven figures and two tables; the supplement "
        "has six figures and eleven tables. New Table S11 reports only "
        "hash-checked V3 responses, mass arithmetic, and the conditional "
        "Fable force/moment sum. No V3 complete trim or dynamic-mode acceptance "
        "is claimed. No V3 three-view is inserted until coordinate and clearance "
        "checks are complete. The research record is at tag "
        "aircraft-sr-2026-09-28-r5. The author should compile and visually "
        "proof both documents before journal submission.\n",
        encoding="utf-8",
    )
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "x", zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(ZIP) as archive:
        assert archive.testzip() is None
    print(f"package={OUT.name} zip_bytes={ZIP.stat().st_size}")


if __name__ == "__main__":
    main()
