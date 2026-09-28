"""Static integrity check for release07; not a substitute for LaTeX compilation."""
from pathlib import Path
import re
import struct
import zipfile

root = Path(__file__).resolve().parents[1]
package = root / "output/overleaf/scientific_reports_aircraft_2026_09_28_release07"
main = (package / "main.tex").read_text(encoding="utf-8")
supp = (package / "supplementary.tex").read_text(encoding="utf-8")
refs = (package / "references_scientific_reports.tex").read_text(encoding="utf-8")
assert main.count(r"\begin{figure}") == 7 and main.count(r"\begin{table}") == 2
assert supp.count(r"\begin{figure}") == 6 and supp.count(r"\begin{table}") == 11
assert r"\label{tab:v3returns}" in supp
assert "Supplementary Table~S11" in main
assert "aircraft-sr-2026-09-28-r5" in main
for body in (main, supp):
    for graphic in re.findall(r"\\includegraphics\[[^]]*\]\{([^}]+)\}", body):
        assert (package / graphic.replace(r"\figdir", "figures")).is_file(), graphic
    for group in re.findall(r"\\cite\{([^}]+)\}", body):
        for key in group.split(","):
            assert rf"\bibitem{{{key.strip()}}}" in refs, key
for required in ("v1_rate_derivatives.json", "v1_v2_pitch_gate_comparison.json",
                 "v2_dynamic_gate.json", "v9_integrated_response_audit.json"):
    assert (package / "audit_data" / required).is_file()
png = (package / "figures/v2_force_moment_comparison.png").read_bytes()
assert png[:8] == b"\x89PNG\r\n\x1a\n"
assert struct.unpack(">II", png[16:24]) == (3600, 2460)
with zipfile.ZipFile(root / "output/delivery/scientific_reports_aircraft_overleaf_release07.zip") as archive:
    assert archive.testzip() is None
    assert "audit_data/v9_integrated_response_audit.json" in archive.namelist()
print("release07 static checks passed; TeX compilation and visual proof remain untested")
