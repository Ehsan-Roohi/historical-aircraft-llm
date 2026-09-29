"""Conservative source-figure screen at intended maximum JoA widths.

Includes PNG pixel density and a limited explicit-font-size bound for V0 SVGs.
It does not replace compiled-PDF inspection or full line-weight/type auditing.
"""

from pathlib import Path
import json
import re
import struct


PUBLIC = Path(__file__).resolve().parents[1]
PROJECT = PUBLIC.parents[1]
BASELINE = PROJECT / "output/overleaf/aircraft_ast_2026_09_28_release09/figures"
DISPLAY1 = PROJECT / "output/figures_joa_draft01"
DISPLAY2 = PROJECT / "output/figures_joa_draft02"
DISPLAY3 = PROJECT / "output/figures_joa_draft03"
DISPLAY4 = PROJECT / "output/figures_joa_draft04"
DISPLAY5 = PROJECT / "output/figures_joa_draft05"
OUT = PUBLIC / "analysis/results/joa_figure_display_gate01.json"

# Main text: US letter, 1-inch margins, hence 6.5-in portrait and
# 0.96*(11-2) = 8.64-in landscape. Supplement: A4, 22-mm margins,
# 0.96*(297-44)/25.4 = 9.562-in landscape; 166/25.4 = 6.535-in portrait.
FIGURES = [
    ("configuration_comparison_v3.png", 8.64, DISPLAY2, "main landscape"),
    ("astra_v2_threeview.png", 8.64, DISPLAY1, "main landscape"),
    ("fable_v2_threeview.png", 8.64, DISPLAY1, "main landscape"),
    ("opus_v2_threeview.png", 8.64, DISPLAY1, "main landscape"),
    ("force_moment_balance.png", 6.5, DISPLAY2, "main portrait"),
    ("v2_force_moment_comparison.png", 6.5, DISPLAY3, "main portrait"),
]
SUPPLEMENTARY_FIGURES = [
    ("wright_threeview_reconstruction.png", 0.96 * (297-44)/25.4, DISPLAY1, "supplement landscape"),
    ("astra_oblique_v0.png", 0.96 * (297-44)/25.4, DISPLAY5, "supplement landscape"),
    ("fable_oblique_v0.png", 0.96 * (297-44)/25.4, DISPLAY5, "supplement landscape"),
    ("opus_oblique_v0.png", 0.96 * (297-44)/25.4, DISPLAY5, "supplement landscape"),
    ("wright_response_v1.png", 166/25.4, DISPLAY4, "supplement portrait"),
    ("fixed_control_response_v1.png", 166/25.4, DISPLAY4, "supplement portrait"),
]


def png_dimensions(path):
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def main():
    def audit_list(figures):
        rows = []
        for name, width_in, source, placement in figures:
            width_px, height_px = png_dimensions(source / name)
            ppi = width_px / width_in  # lower bound if height cap reduces placed width
            rows.append({"name": name, "placement": placement,
                         "pixels": [width_px, height_px],
                         "maximum_placed_width_in": width_in,
                         "minimum_effective_horizontal_ppi": round(ppi, 1),
                         "meets_600_ppi_line_art_screen": ppi >= 600})
        return rows
    rows = audit_list(FIGURES)
    supplementary_rows = audit_list(SUPPLEMENTARY_FIGURES)
    v0_lettering = []
    max_supplement_landscape_width_in = 0.96 * (297-44)/25.4
    for name in ("astra_oblique_v0", "fable_oblique_v0", "opus_oblique_v0"):
        svg = (DISPLAY5 / (name + ".svg")).read_text(encoding="utf-8")
        viewbox = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', svg)
        sizes = [float(value) for value in re.findall(r'font-size="([0-9.]+)"', svg)]
        if not viewbox or not sizes:
            raise ValueError(f"Cannot screen SVG lettering: {name}")
        min_size = min(sizes)
        upper_pt = min_size / float(viewbox.group(1)) * max_supplement_landscape_width_in * 72
        v0_lettering.append({"name": name, "minimum_explicit_source_font_units": min_size,
                             "maximum_possible_point_size_at_width_cap": round(upper_pt, 2),
                             "below_8pt_even_without_height_cap": upper_pt < 8})
    OUT.write_text(json.dumps({
        "scope": "PNG line-art pixel-density and limited V0 source-lettering screen; not final PDF proof",
        "rows": rows,
        "remaining_main_below_600": [r["name"] for r in rows if not r["meets_600_ppi_line_art_screen"]],
        "supplementary_rows": supplementary_rows,
        "remaining_supplementary_below_600": [r["name"] for r in supplementary_rows if not r["meets_600_ppi_line_art_screen"]],
        "v0_lettering_upper_bounds": v0_lettering,
        "not_screened": ["Wright photographic raster (300-ppi class)", "actual compiled placement, transformed lettering, and line weights"]
    }, indent=2) + "\n", encoding="utf-8")
    print(OUT.name)


if __name__ == "__main__":
    main()
