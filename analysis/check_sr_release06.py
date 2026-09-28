"""Static release06 integrity check; not TeX compilation."""
from pathlib import Path
import re
import zipfile
from PIL import Image

root=Path(__file__).resolve().parents[1]
p=root/'output/overleaf/scientific_reports_aircraft_2026_09_28_release06'
main=(p/'main.tex').read_text(encoding='utf-8')
supp=(p/'supplementary.tex').read_text(encoding='utf-8')
refs=(p/'references_scientific_reports.tex').read_text(encoding='utf-8')
assert main.count(r'\begin{figure}')==7 and main.count(r'\begin{table}')==2
assert supp.count(r'\begin{figure}')==6 and supp.count(r'\begin{table}')==10
assert r'\label{tab:v1v2dynamic}' in supp
assert 'Supplementary Table~S10' in main
assert 'aircraft-sr-2026-09-28-r4' in main
for body in (main,supp):
    for graphic in re.findall(r'\\includegraphics\[[^]]*\]\{([^}]+)\}',body):
        assert (p/graphic.replace(r'\figdir','figures')).is_file(),graphic
    for group in re.findall(r'\\cite\{([^}]+)\}',body):
        for key in group.split(','):
            assert rf'\bibitem{{{key.strip()}}}' in refs,key
for required in ('v1_rate_derivatives.json','v1_v2_pitch_gate_comparison.json','v2_dynamic_gate.json'):
    assert (p/'audit_data'/required).is_file()
with Image.open(p/'figures/v2_force_moment_comparison.png') as im:
    assert im.size==(3600,2460) and im.info['dpi'][0]>=300
with zipfile.ZipFile(root/'output/delivery/scientific_reports_aircraft_overleaf_release06.zip') as z:
    assert z.testzip() is None
    assert 'audit_data/v1_v2_pitch_gate_comparison.json' in z.namelist()
print('release06 static checks passed; compile and visual proof remain untested')
