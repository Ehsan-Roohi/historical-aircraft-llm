"""Package V1/V2 derivative comparison with the previous reviewed figures."""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'output/overleaf/scientific_reports_aircraft_2026_09_28_release05'
OUT = ROOT / 'output/overleaf/scientific_reports_aircraft_2026_09_28_release06'
ZIP = ROOT / 'output/delivery/scientific_reports_aircraft_overleaf_release06.zip'


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(ROOT/'paper/article_scientific_reports.tex', OUT/'main.tex')
    shutil.copy2(ROOT/'paper/supplementary_scientific_reports.tex', OUT/'supplementary.tex')
    shutil.copy2(OLD/'references_scientific_reports.tex', OUT/'references_scientific_reports.tex')
    shutil.copytree(OLD/'figures', OUT/'figures')
    shutil.copytree(OLD/'audit_data', OUT/'audit_data')
    shutil.copy2(ROOT/'analysis/results/v1_rate_derivative_screen01/summary.json',
                 OUT/'audit_data/v1_rate_derivatives.json')
    shutil.copy2(ROOT/'analysis/results/v1_v2_pitch_gate_comparison01.json',
                 OUT/'audit_data/v1_v2_pitch_gate_comparison.json')
    shutil.copy2(ROOT/'paper/DATA_AVAILABILITY.md', OUT/'DATA_AVAILABILITY.md')
    (OUT/'README.md').write_text(
        '# Historical-aircraft LLM manuscript: V1/V2 dynamics comparison\n\n'
        'Compile main.tex and supplementary.tex separately with pdfLaTeX. '
        'The main document has seven figures and two tables; the supplement '
        'has six figures and ten tables. New Table S10 distinguishes V1/V2 '
        'static pitch slope from the omission-based two-state sign screen. '
        'No full-aircraft eigenmodes or physical flight capability are claimed. '
        'The V1 rate run is single-mesh; V2 uses two meshes. The full research '
        'record is at tag aircraft-sr-2026-09-28-r4. The author should compile '
        'and visually proof both TeX documents before journal submission.\n',
        encoding='utf-8')
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP,'x',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():z.write(path,path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(ZIP) as z:assert z.testzip() is None
    print(f'package={OUT.name} zip_bytes={ZIP.stat().st_size}')


if __name__=='__main__':main()
