"""Screen selected latest-candidate rigid gaps, not loaded collision freedom.

Fable V13 changes arithmetic only, so its occupied-geometry parent is V12.
Opus values listed below are source-reported, not independently recreated
from a complete 3-D solid model. All distances are rigid and nominal.
"""

from pathlib import Path
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / "v12_installation_attempt01/responses/claude-fable-5-1/response.json"
FABLE_V13 = ROOT / "v13_fable_arithmetic_attempt01/responses/claude-fable-5-1/response.json"
OPUS = ROOT / "v12_opus_retry_attempt01/responses/claude-opus-5-5/response.json"
OUT = ROOT / "analysis/results/v14_static_clearance_budget01.json"


def source(path):
    raw = path.read_bytes()
    wrapper = json.loads(raw)
    if wrapper["status"] != "completed":
        raise ValueError(f"Incomplete response: {path}")
    return json.loads(wrapper["response"]), hashlib.sha256(raw).hexdigest()


def endpoints(text, axis):
    match = re.search(rf"\b{axis}\s+(-?\d+\.\d+)\s*(?:\.\.|-)\s*(-?\d+\.\d+)", text)
    if not match:
        raise ValueError(f"Missing {axis} endpoints: {text}")
    return tuple(map(float, match.groups()))


def number_after(text, marker):
    match = re.search(re.escape(marker) + r"[^\d-]*(-?\d+\.\d+)", text)
    if not match:
        raise ValueError(f"Missing number after {marker}: {text}")
    return float(match.group(1))


def main():
    f, f_hash = source(FABLE)
    f13, f13_hash = source(FABLE_V13)
    o, o_hash = source(OPUS)
    if f13["parent_response_sha256"] != f_hash:
        raise ValueError("Fable V13 parent hash does not match frozen V12 geometry")
    if not f13["occupied_geometry_changes"].startswith("NONE. No component mass, centroid or bounding box changed"):
        raise ValueError("Fable V13 no longer preserves parent rigid geometry")
    fg = f["occupied_geometry"]
    pilot_x = endpoints(fg["pilot_box"], "x")
    engine_x = endpoints(fg["engine_box"], "x")
    tank_z = endpoints(fg["tank_box"], "z")
    cooling_z = endpoints(fg["cooling_box"], "z")
    engine_y = number_after(fg["engine_box"], "y ")
    frame_y = number_after(fg["engine_box"], "frame side y ")
    longeron_z = number_after(fg["tank_box"], "upper longeron z ")
    disc = fg["propeller_discs"]
    centre_y = number_after(disc, "centres (")
    radius = number_after(disc, "r ")
    disc_x = number_after(disc, "x ")
    wing_te_x = number_after(disc, "deck TE x ")
    disc_frame_y = number_after(disc, "frame side y ")
    gaps = {
        "pilot_engine_x": engine_x[0] - pilot_x[1],
        "engine_frame_y": frame_y - engine_y,
        "tank_longeron_z": longeron_z - tank_z[1],
        "cooling_longeron_z": cooling_z[0] - longeron_z,
        "disc_inboard_frame_y": centre_y - radius - disc_frame_y,
        "wing_trailing_edge_disc_x": disc_x - wing_te_x,
    }
    if not all(0 < gap < 1 for gap in gaps.values()):
        raise ValueError("Nonpositive or unreasonable nominal gap")
    checks = o["occupied_geometry"]["physical_solid_checks"]
    keep = {"E1-E5", "LowerWing-E4", "E5-S2 front struts", "G2 wheel-skid", "G4 aft node-elevator hinge"}
    opus_selected = [{"pair": row["pair"], "model_reported_gap_m": row["gap_m"],
                      "note": row.get("note", "")}
                     for row in checks if row["pair"] in keep]
    if len(opus_selected) != len(keep):
        raise ValueError("Selected Opus source checks missing")
    result = {
        "scope": "Selected nominal rigid one-axis gaps only; no tolerance, elastic, tire, blade-vibration or control-sweep allowance",
        "fable_v12_geometry_carried_to_v13": {"v12_source_sha256": f_hash, "v13_source_sha256": f13_hash, "evaluator_recomputed_gaps_m": {k: round(v, 6) for k, v in gaps.items()}, "minimum_m": round(min(gaps.values()), 6)},
        "opus_v12_reviewed_replay": {"source_sha256": o_hash, "selected_model_reported_gaps_not_independently_3d_verified": opus_selected},
        "disposition": "HOLD: positive nominal gaps do not demonstrate installed or loaded clearance"
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUT.name)


if __name__ == "__main__":
    main()
