"""Pre-publication provenance and file-scope screen for the G7 *draft* tag.

This is not a copyright opinion, bibliography review, TeX proof, or an
airworthiness assessment. It fails closed on known credential signatures,
missing source assets, mismatched prompt hashes and archive corruption.
"""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TAG = "aircraft-joa-2026-09-29-g7-draft"
PACKAGE = ROOT / "aircraft_joa_overleaf_draft15.zip"
OUT = ROOT / "analysis/results/joa_release_g7_gate01.json"
SOURCE_NAMES = (
    "configuration_comparison_v3.svg", "configuration_comparison_v3.json",
    "draw_v2_force_moment.py", "v2_compact_report.json",
    "astra_oblique_v0.svg", "fable_oblique_v0.svg", "opus_oblique_v0.svg",
    "wright_response_v1.svg", "fixed_control_response_v1.svg",
)
RESTRICTED_SUFFIXES = {".pdf", ".rar", ".7z", ".pem", ".key", ".env", ".pfx", ".p12"}
SECRET_SIGNATURES = (
    re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"ghp_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----"),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_byte_match(path):
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(["git", "show", ":" + relative], cwd=ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return hashlib.sha256(result.stdout).hexdigest() == digest(path)


def main():
    source = ROOT / "figures/source_svg"
    assets = []
    for name in SOURCE_NAMES:
        path = source / name
        if not path.is_file():
            raise FileNotFoundError(path)
        if not index_byte_match(path):
            raise ValueError(f"Git index changed source bytes: {name}")
        assets.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                       "bytes": path.stat().st_size})
    attempt = ROOT / "v14_integrated_candidate_attempt01"
    manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "FROZEN_UNSENT" or len(manifest["records"]) != 3:
        raise ValueError("V14 status or model count changed")
    if digest(attempt / "prompts/instructions.txt") != manifest["instructions_sha256"]:
        raise ValueError("V14 instruction hash mismatch")
    if digest(attempt / "run_v14_candidate.py") != manifest["runner_sha256"]:
        raise ValueError("V14 runner hash mismatch")
    for control in (attempt / "manifest.json", attempt / "prompts/instructions.txt",
                    attempt / "run_v14_candidate.py"):
        if not index_byte_match(control):
            raise ValueError(f"Git index changed V14 bytes: {control.name}")
    for row in manifest["records"]:
        prompt = attempt / "prompts" / row["prompt_file"]
        parent = attempt / "parents" / row["parent_file"]
        baseline = attempt / "baselines" / row["parent_file"]
        if digest(prompt) != row["prompt_sha256"] or digest(parent) != row["parent_sha256"]:
            raise ValueError(f"V14 source hash mismatch: {row['model']}")
        if digest(baseline) != row["baseline_sha256"]:
            raise ValueError(f"V14 baseline hash mismatch: {row['model']}")
        if not all(index_byte_match(path) for path in (prompt, parent, baseline)):
            raise ValueError(f"Git index changed V14 bytes: {row['model']}")
        if json.loads(parent.read_text(encoding="utf-8"))["status"] != "completed":
            raise ValueError(f"Incomplete V14 parent: {row['model']}")
    article = (ROOT / "paper/article_journal_of_aircraft.tex").read_text(encoding="utf-8")
    if TAG not in article or "no V14 model response exists" not in article:
        raise ValueError("Manuscript data statement does not identify G7 draft boundary")
    if "No proposed configuration has yet met" not in article:
        raise ValueError("Manuscript flight-status caveat absent")
    editorial = json.loads((ROOT / "analysis/results/joa_editorial_gate01.json").read_text(encoding="utf-8"))
    figure_gate = json.loads((ROOT / "analysis/results/joa_figure_display_gate01.json").read_text(encoding="utf-8"))
    if editorial["reference_count"] != 40 or editorial["reference_keys_with_et_al_in_list"]:
        raise ValueError("Reference-order screen changed")
    if figure_gate["remaining_main_below_600"] or figure_gate["remaining_supplementary_below_600"]:
        raise ValueError("Figure raster screen changed")
    if not all(row["below_8pt_even_without_height_cap"] for row in figure_gate["v0_lettering_upper_bounds"]):
        raise ValueError("Expected V0 lettering caveat missing")
    for name in ("v14_rigid_ground_gate01.json", "v14_inertia_lower_bounds01.json",
                 "v14_static_clearance_budget01.json", "v14_fable_power_fixed_point01.json"):
        json.loads((ROOT / "analysis/results" / name).read_text(encoding="utf-8"))
    checked_text_files = 0
    for folder in (ROOT / "analysis", ROOT / "paper", attempt, source):
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in RESTRICTED_SUFFIXES:
                raise ValueError(f"Restricted file type in release scope: {path.relative_to(ROOT)}")
            if path.suffix.lower() not in {".py", ".js", ".json", ".txt", ".md", ".tex", ".svg"}:
                continue
            content = path.read_bytes()
            if any(pattern.search(content) for pattern in SECRET_SIGNATURES):
                raise ValueError(f"Credential signature in {path.relative_to(ROOT)}")
            checked_text_files += 1
    if not PACKAGE.is_file():
        raise FileNotFoundError(PACKAGE)
    with zipfile.ZipFile(PACKAGE) as archive:
        if archive.testzip() is not None:
            raise ValueError("Overleaf archive checksum failure")
        names = archive.namelist()
        if "main.tex" not in names or "supplementary.tex" not in names:
            raise ValueError("Overleaf source missing")
        if any(Path(name).suffix.lower() in RESTRICTED_SUFFIXES for name in names):
            raise ValueError("Restricted file type inside Overleaf archive")
        package_manifest = json.loads(archive.read("MANIFEST.json"))
        if package_manifest["status"] != "DRAFT_NOT_SUBMISSION_READY" or package_manifest["intended_release_tag"] != TAG:
            raise ValueError("Overleaf release status/tag mismatch")
    result = {
        "status": "DRAFT_RESEARCH_RELEASE_ONLY",
        "intended_tag": TAG,
        "scientific_claim_scope": "Source-hashed evaluator screens only; no flight, full dynamics or journal acceptance",
        "v14_status": manifest["status"],
        "v14_model_count": len(manifest["records"]),
        "public_figure_source_assets": assets,
        "source_and_v14_git_index_bytes_match_worktree": True,
        "text_files_screened_for_known_secret_signatures": checked_text_files,
        "restricted_binary_or_private_file_types_found_in_new_scope": False,
        "overleaf_zip_sha256": digest(PACKAGE),
        "overleaf_zip_bytes": PACKAGE.stat().st_size,
        "journal_submission_ready": False,
        "flight_capability_validated": False,
        "remaining_gates": ["TeX compilation and PDF inspection", "V0 printed lettering",
                            "all-reference and image-rights review", "installed power and six-component trim",
                            "physical intrinsic inertia and full dynamic modes"],
        "limitations": "Automated file/credential patterns and known records only; not a legal clearance or independent full-data review",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUT.name, checked_text_files, "text files screened")


if __name__ == "__main__":
    main()
