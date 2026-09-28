"""Static integrity checks for release05; does not compile or proof TeX."""
from pathlib import Path
import re
import zipfile
from PIL import Image

root = Path(__file__).resolve().parents[1]
package = root / "output/overleaf/scientific_reports_aircraft_2026_09_28_release05"
main = (package/"main.tex").read_text(encoding="utf-8")
supp = (package/"supplementary.tex").read_text(encoding="utf-8")
refs = (package/"references_scientific_reports.tex").read_text(encoding="utf-8")
assert main.count(r"\begin{figure}") == 7
assert main.count(r"\begin{table}") == 2
assert supp.count(r"\begin{figure}") == 6
assert supp.count(r"\begin{table}") == 9
assert r"\label{eq:reduced_dynamic_screen}" in main
assert r"\label{tab:reduceddynamic}" in supp
assert "The analysis presently confirms" in main
assert "aircraft-sr-2026-09-28-r3" in main
for body in (main, supp):
    for graphic in re.findall(r"\\includegraphics\[[^]]*\]\{([^}]+)\}", body):
        assert (package/graphic.replace(r"\figdir", "figures")).is_file(), graphic
    for group in re.findall(r"\\cite\{([^}]+)\}", body):
        for key in group.split(","):
            assert rf"\bibitem{{{key.strip()}}}" in refs, key
for required in ("v2_dynamic_gate.json", "flight_dynamics_gate_v2.py"):
    assert (package/"audit_data"/required).is_file()
with Image.open(package/"figures/v2_force_moment_comparison.png") as im:
    assert im.size == (3600, 2460)
    assert im.info["dpi"][0] >= 300
zip_path = root/"output/delivery/scientific_reports_aircraft_overleaf_release05.zip"
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert "audit_data/v2_dynamic_gate.json" in z.namelist()
print("release05 static checks passed; TeX compilation and visual proof remain untested")
