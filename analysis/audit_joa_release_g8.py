"""G8 delta audit over the G7 public-draft provenance screen.

Verifies that numbered display crops are traceable to the immutable V0 SVGs.
It is not a TeX/PDF proof, permissions opinion, or flightworthiness review.
"""

from pathlib import Path
import hashlib
import json
import zipfile

import audit_joa_release_g7 as base


ROOT = Path(__file__).resolve().parents[1]
TAG = "aircraft-joa-2026-09-29-g8-draft"
PACKAGE = ROOT / "aircraft_joa_overleaf_draft17.zip"
OUT = ROOT / "analysis/results/joa_release_g8_gate01.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    figure_gate = json.loads((ROOT / "analysis/results/joa_figure_display_gate01.json").read_text(encoding="utf-8"))
    detail_screen = figure_gate["v0_numbered_detail_marker_upper_bounds"]
    if len(detail_screen) != 3 or any(row["marker_count"] != 8 for row in detail_screen):
        raise ValueError("Three eight-marker detail screens required")
    supplement = (ROOT / "paper/supplementary_scientific_reports.tex").read_text(encoding="utf-8")
    for model in ("astra", "fable", "opus"):
        if supplement.count(model + "_oblique_v0_detail.png") != 1:
            raise ValueError(f"Missing detail placement: {model}")
        if supplement.count(model.capitalize() + " detail key.") != 1:
            raise ValueError(f"Missing detail prose key: {model}")
    source = ROOT / "figures/source_svg"
    details = json.loads((source / "v0_details/MANIFEST.json").read_text(encoding="utf-8"))
    if len(details["rows"]) != 3:
        raise ValueError("Three V0 detail records required")
    with zipfile.ZipFile(PACKAGE) as archive:
        package_details = json.loads(archive.read("figure_sources/v0_details_display_manifest.json"))
        if package_details != details:
            raise ValueError("Package/public detail manifests differ")
        for row in details["rows"]:
            name = row["name"]
            original = (source / (name + ".svg")).read_bytes()
            detail = (source / "v0_details" / (name + "_detail.svg")).read_bytes()
            if sha(original) != row["original_svg_sha256"] or sha(detail) != row["detail_svg_sha256"]:
                raise ValueError(f"V0 source/detail hash mismatch: {name}")
            if detail.count(b'aria-label="component ') != 8:
                raise ValueError(f"Eight detail markers required: {name}")
            if sha(archive.read("figure_sources/" + name + "_detail.svg")) != row["detail_svg_sha256"]:
                raise ValueError(f"Overleaf detail SVG mismatch: {name}")
            if sha(archive.read("figures/" + name + "_detail.png")) != row["detail_png_sha256"]:
                raise ValueError(f"Overleaf detail PNG mismatch: {name}")
    base.TAG = TAG
    base.PACKAGE = PACKAGE
    base.OUT = OUT
    base.SOURCE_NAMES = base.SOURCE_NAMES + tuple(
        "v0_details/" + row["name"] + "_detail.svg" for row in details["rows"]
    ) + ("v0_details/MANIFEST.json",)
    base.main()
    result = json.loads(OUT.read_text(encoding="utf-8"))
    result["v0_researcher_display_details"] = {
        "count": 3,
        "markers_each": 8,
        "original_svg_hashes_match": True,
        "detail_svg_and_png_hashes_match_overleaf_zip": True,
        "original_v0_plates_altered": False,
        "compiled_page_readability_validated": False,
    }
    result["remaining_gates"] = [
        "TeX compilation and page-by-page PDF inspection, including original V0 type",
        "all-reference and image-rights review",
        "installed power and six-component trim",
        "physical intrinsic inertia and full dynamic modes",
    ]
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("G8 detail hashes and package checks passed")


if __name__ == "__main__":
    main()
