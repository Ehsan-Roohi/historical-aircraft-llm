"""Static, read-only checks for the Journal of Aircraft draft package."""

from pathlib import Path
import hashlib
import json
import re
import struct
import zipfile


PUBLIC = Path(__file__).resolve().parents[1]
PROJECT = Path(__file__).resolve().parents[3]
PACKAGE = PROJECT / "output/overleaf/aircraft_joa_2026_09_29_draft15"
ZIP = PROJECT / "output/delivery/aircraft_joa_overleaf_draft15.zip"


def extract_braced(text, marker, start=0):
    at = text.index(marker, start) + len(marker)
    depth = 1
    cursor = at
    while depth:
        if cursor >= len(text):
            raise ValueError("Unbalanced braced content")
        if text[cursor] == "{" and text[cursor - 1] != "\\":
            depth += 1
        elif text[cursor] == "}" and text[cursor - 1] != "\\":
            depth -= 1
        cursor += 1
    return text[at:cursor - 1], cursor


def main():
    main_tex = (PACKAGE / "main.tex").read_text(encoding="utf-8")
    supplement = (PACKAGE / "supplementary.tex").read_text(encoding="utf-8")
    for model in ("Astra", "Fable", "Opus"):
        assert supplement.count(r"\paragraph{Readable key to the " + model + " V0 plate.}") == 1
    refs = (PACKAGE / "references_journal_of_aircraft.tex").read_text(encoding="utf-8")
    title, _ = extract_braced(main_tex, r"\title{")
    assert len(title.split()) <= 12
    abstract = main_tex.split(r"\begin{abstract}", 1)[1].split(r"\end{abstract}", 1)[0]
    abstract_words = len(re.findall(r"\b[\w-]+\b", re.sub(r"\\[A-Za-z]+", "", abstract)))
    assert 100 <= abstract_words <= 200
    assert r"\documentclass[10pt,letterpaper]{article}" in main_tex
    assert r"\doublespacing" in main_tex
    assert r"\section*{Acknowledgments and use of artificial intelligence}" in main_tex
    assert "ScholarOne" in main_tex
    assert r"\label{eq:groundreactions}" in main_tex
    assert r"\label{eq:parallelaxis}" in main_tex
    assert "aircraft-joa-2026-09-29-g7-draft" in main_tex
    assert "no V14 model response exists" in main_tex
    assert main_tex.count(r"\begin{landscape}") == main_tex.count(r"\end{landscape}")
    captions = []
    cursor = 0
    while r"\caption{" in main_tex[cursor:]:
        caption, cursor = extract_braced(main_tex, r"\caption{", cursor)
        captions.append(caption)
    assert len(captions) == 10, len(captions)  # 7 figures + 3 tables
    for label in ("fig:wrightphoto", "fig:config", "fig:astrav2",
                  "fig:fablev2", "fig:opusv2", "fig:balance", "fig:v2forces"):
        at = main_tex.index(r"\label{" + label + "}")
        before = main_tex.rfind(r"\caption{", 0, at)
        caption, _ = extract_braced(main_tex, r"\caption{", before)
        assert len(caption.split()) <= 25, (label, len(caption.split()))
    for tex in (main_tex, supplement):
        images = re.findall(r"\{\\figdir/([^}]+)\}", tex)
        assert images
        assert all((PACKAGE / "figures" / name).is_file() for name in images)
    inertia = json.loads((PACKAGE / "audit_data" / "v14_inertia_lower_bounds01.json").read_text(encoding="utf-8"))
    assert inertia["fable_v13"]["component_rows"] == 26
    assert inertia["opus_v12"]["component_rows"] == 30
    assert inertia["modal_acceptance"].startswith("NOT ASSESSED")
    assert (PACKAGE / "V14_INERTIA_GATE.md").is_file()
    clearance = json.loads((PACKAGE / "audit_data" / "v14_static_clearance_budget01.json").read_text(encoding="utf-8"))
    assert clearance["fable_v12_geometry_carried_to_v13"]["minimum_m"] == 0.01
    power = json.loads((PACKAGE / "audit_data" / "v14_fable_power_fixed_point01.json").read_text(encoding="utf-8"))
    assert 20194 < power["coupled_fixed_point"]["engine_target_W"] < 20195
    assert 519 < power["retained_19_5kW_target"]["reserve_shortfall_W"] < 521
    assert abs(power["coupled_fixed_point"]["equation_residual_W"]) < 1e-8
    assert (PACKAGE / "V14_FABLE_POWER_FIXED_POINT.md").is_file()
    assert "No aircraft passes the installed-geometry gate" in main_tex
    figure_gate = json.loads((PACKAGE / "audit_data" / "joa_figure_display_gate01.json").read_text(encoding="utf-8"))
    assert figure_gate["remaining_main_below_600"] == []
    assert figure_gate["remaining_supplementary_below_600"] == []
    assert all(row["below_8pt_even_without_height_cap"] for row in figure_gate["v0_lettering_upper_bounds"])
    for name, expected in (("configuration_comparison_v3.png", 6000),
                           ("force_moment_balance.png", 4800),
                           ("v2_force_moment_comparison.png", 6000),
                           ("wright_threeview_reconstruction.png", 6000)):
        header = (PACKAGE / "figures" / name).read_bytes()[:24]
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">I", header[16:20])[0] == expected
    source_svg = PACKAGE / "figure_sources/v2_force_moment_comparison.svg"
    display_manifest = json.loads((PACKAGE / "figure_sources/v2_force_display_manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(source_svg.read_bytes()).hexdigest() == display_manifest["source_svg_sha256"]
    assert hashlib.sha256((PACKAGE / "figure_sources/archived_draw_v2_force_moment.py").read_bytes()).hexdigest() == display_manifest["frozen_v2_python_source_sha256"]
    assert hashlib.sha256((PACKAGE / "figure_sources/archived_v2_compact_report.json").read_bytes()).hexdigest() == display_manifest["frozen_v2_compact_report_sha256"]
    for manifest_name, hash_key in (("response_plots_display_manifest.json", "source_svg_sha256"),
                                    ("v0_obliques_display_manifest.json", "original_svg_sha256")):
        derivative_manifest = json.loads((PACKAGE / "figure_sources" / manifest_name).read_text(encoding="utf-8"))
        for row in derivative_manifest["rows"]:
            assert hashlib.sha256((PACKAGE / "figure_sources" / (row["name"] + ".svg")).read_bytes()).hexdigest() == row[hash_key]
    editorial = json.loads((PACKAGE / "audit_data" / "joa_editorial_gate01.json").read_text(encoding="utf-8"))
    assert editorial["reference_count"] == 40
    assert editorial["source_reference_order_matches_citation_order"]
    assert editorial["reference_keys_with_et_al_in_list"] == []
    citations = [key.strip() for group in re.findall(r"\\cite\{([^}]+)\}", main_tex)
                 for key in group.split(",")]
    ordered = list(dict.fromkeys(citations))
    items = re.findall(r"\\bibitem\{([^}]+)\}", refs)
    assert items == ordered
    attempt = PUBLIC / "v14_integrated_candidate_attempt01"
    manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "FROZEN_UNSENT"
    assert len(manifest["records"]) == 3
    for row in manifest["records"]:
        prompt = (attempt / "prompts" / row["prompt_file"]).read_bytes()
        parent = (attempt / "parents" / row["parent_file"]).read_bytes()
        assert hashlib.sha256(prompt).hexdigest() == row["prompt_sha256"]
        assert hashlib.sha256(parent).hexdigest() == row["parent_sha256"]
        assert json.loads(parent)["status"] == "completed"
    with zipfile.ZipFile(ZIP) as archive:
        assert archive.testzip() is None
        assert "main.tex" in archive.namelist()
    print("Static JoA draft checks passed; TeX compilation and physical validation not checked")


if __name__ == "__main__":
    main()
