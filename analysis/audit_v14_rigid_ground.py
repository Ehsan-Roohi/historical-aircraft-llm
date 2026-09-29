"""Independent rigid ground-contact arithmetic on latest complete returns.

This is a geometry/loading screen. It cannot validate tire/skid compliance,
loaded structural deflection, braking response, takeoff, or flight.
"""

from pathlib import Path
import hashlib
import json
import math


ROOT = Path(__file__).resolve().parents[1]
FABLE_V12 = ROOT / "v12_installation_attempt01/responses/claude-fable-5-1/response.json"
FABLE_V13_AUDIT = ROOT / "analysis/results/v13_fable_gate01.json"
OPUS_V12 = ROOT / "v12_opus_retry_attempt01/responses/claude-opus-5-5/response.json"
OUTPUT = ROOT / "analysis/results/v14_rigid_ground_gate01.json"
G = 9.81


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def response(path):
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    assert wrapper["status"] == "completed"
    return json.loads(wrapper["response"])


def fable():
    source = response(FABLE_V12)
    gear = source["occupied_geometry"]["gear"]
    assert "contacts (0.40" in gear and "(3.20,0,-0.75)" in gear
    assert "skids z -0.60 x -0.30(z -0.40 toe)" in gear
    cases = json.loads(FABLE_V13_AUDIT.read_text(encoding="utf-8"))["loading_cases"]
    front_x, rear_x = 0.40, 3.20
    rows = []
    for case in cases:
        mass = case["mass_kg"]
        cg_x, _, cg_z = case["cg_xyz_m"]
        weight = mass * G
        front = weight * (rear_x - cg_x) / (rear_x - front_x)
        rear = weight - front
        rows.append({"state": case["state"], "mass_kg": mass,
                     "cg_x_m": round(cg_x, 6), "cg_z_m": round(cg_z, 6),
                     "weight_N": round(weight, 3),
                     "front_pair_reaction_N": round(front, 3),
                     "rear_reaction_N": round(rear, 3),
                     "all_reactions_positive": front > 0 and rear > 0})
    # Nose-down about the front wheels: the first stated skid point is 0.40 m
    # ahead and 0.15 m above the ground-contact plane.
    skid_angle = math.degrees(math.atan2(0.15, 0.40))
    toe_angle = math.degrees(math.atan2(0.35, 0.70))
    return {"source_v12_response_sha256": sha(FABLE_V12),
            "source_v13_audit_sha256": sha(FABLE_V13_AUDIT),
            "support_points_x_m": [front_x, rear_x],
            "loading_cases": rows,
            "rigid_nose_down_skid_contact_deg": round(skid_angle, 6),
            "rigid_nose_down_toe_contact_deg": round(toe_angle, 6),
            "first_of_these_two_declared_points": "skid at x=0.00 m",
            "limitations": ["three-point static reactions only", "no dynamic braking",
                            "no tire compression or skid compliance",
                            "no loaded structural deflection or full occupied-solid sweep"]}


def opus():
    source = response(OPUS_V12)
    runner = next(row for row in source["revised_components"] if row["id"] == "G1")
    nodes = runner["nodes_m"]["per_skid_underside"]
    nose, pivot, aft = nodes
    assert math.isclose(pivot[0], -1.5) and math.isclose(pivot[2], -0.9)
    assert math.isclose(aft[0], 1.6) and math.isclose(aft[2], -0.9)
    # Positive pitch is nose-up in the model's aft-positive x frame. Here the
    # nose-down angle magnitude rotates the nose runner point toward ground.
    dx = pivot[0] - nose[0]
    dz = nose[2] - pivot[2]
    upturn_angle = math.degrees(math.atan2(dz, dx))
    n1 = next(row for row in source["mass_ledger_rows"] if row["id"] == "N1")
    box = n1["box_m"]
    n1_angle = math.degrees(math.atan2(box["z"][0] - pivot[2],
                                      pivot[0] - box["x"][0]))
    cases = []
    for case in source["loading_cases"]:
        if "case" not in case:
            continue
        cg_x, cg_y, cg_z = case["cg_xyz_m"]
        cases.append({"case": case["case"], "mass_kg": case["mass_kg"],
                      "cg_x_m": cg_x, "cg_z_m": cg_z,
                      "cg_projection_within_flat_skid_x": pivot[0] < cg_x < aft[0],
                      "nose_down_cg_over_front_contact_deg": round(
                          math.degrees(math.atan2(cg_x - pivot[0],
                                                  cg_z - pivot[2])), 6)})
    return {"source_v12_response_sha256": sha(OPUS_V12),
            "front_flat_runner_pivot_xz_m": [pivot[0], pivot[2]],
            "front_upturn_tip_xz_m": [nose[0], nose[2]],
            "rigid_nose_down_upturn_contact_deg": round(upturn_angle, 6),
            "n1_box_front_lower_corner_contact_deg": round(n1_angle, 6),
            "first_of_these_declared_points": "G1 front runner upturn",
            "loading_cases": cases,
            "limitations": ["only selected named rigid points screened",
                            "no complete occupied-solid nose-down sweep",
                            "runner pressure distribution and compliance unknown",
                            "no loaded structural deflection or braking dynamics"]}


def main():
    result = {"scope": "independent rigid ground geometry and support arithmetic",
              "flight_validation": False, "fable_v13": fable(), "opus_v12": opus(),
              "astra_v12": "HOLD: no adopted installed geometry to sweep"}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT.name)


if __name__ == "__main__":
    main()
