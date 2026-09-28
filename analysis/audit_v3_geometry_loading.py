"""Audit reproducible V3 dimensions, loading cases, and conditional clearances.

This intentionally does not predict aerodynamic loads, trim, stability, or
flightworthiness. All geometry is taken from the archived model replies.
"""

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "astra": ROOT / "received_v9_65007436/gpt-6-astra/response.json",
    "fable": ROOT / "received_v9_retry_65009709/claude-fable-5-1/response.json",
    "opus": ROOT / "received_v9_retry_65009709/claude-opus-5-5/response.json",
}


def load_design(path):
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    blocks = re.findall(r"```json\s*(.*?)```", wrapper["response"], re.DOTALL)
    if len(blocks) != 1:
        raise ValueError(f"expected one structured design block: {path}")
    return json.loads(blocks[0])


def ledger_state(items, mass_key, centroid_key, substitutions=None, removals=()):
    """Recompute M and CG after replacing selected (mass, centroid) rows."""
    substitutions = substitutions or {}
    rows = []
    for item in items:
        if item["id"] in removals:
            continue
        mass, centre = substitutions.get(
            item["id"], (float(item[mass_key]), item[centroid_key])
        )
        rows.append((float(mass), [float(v) for v in centre]))
    mass = sum(m for m, _ in rows)
    if mass <= 0:
        raise ValueError("nonpositive aircraft mass")
    centre = [sum(m * xyz[j] for m, xyz in rows) / mass for j in range(3)]
    return {"mass_kg": round(mass, 6), "cg_m": [round(v, 6) for v in centre]}


def pitch_clearance(x, z, pivot_x, pivot_z, ground_z, degrees):
    """Rigid-body ground gap for an aft-positive x and up-positive z frame."""
    angle = math.radians(degrees)
    world_z = pivot_z - (x - pivot_x) * math.sin(angle) + (z - pivot_z) * math.cos(angle)
    return round(world_z - ground_z, 6)


def required_level_force_coefficient(mass, speed, area, rho=1.225, g=9.80665):
    """W/(qS), not a wing CL, stall margin, or trim solution."""
    if min(mass, speed, area, rho, g) <= 0:
        raise ValueError("positive inputs required")
    return round(mass * g / (0.5 * rho * speed * speed * area), 6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    a, f, o = (load_design(SOURCES[name]) for name in SOURCES)
    result = {
        "scope": "V3 model-response geometry/loading arithmetic; no aerodynamic or flight validation",
        "source_sha256": {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in SOURCES.items()},
        "astra": {}, "fable": {}, "opus": {},
        "blocking_unknowns": [],
    }

    # Astra's coordinates are x forward and z up. Check the declared surface
    # extents and both limiting load states directly from its component ledger.
    am = a["geometry"]["main"]
    at = a["geometry"]["horizontal_tail"]
    ag = a["geometry"]["gear"]
    ahub = a["propulsion"]["hub_m"]
    aradius = a["propulsion"]["diameter_m"] / 2
    items = a["mass_model"]["items"]
    result["astra"] = {
        "main_area_m2_recomputed": (am["span_y_m"][1] - am["span_y_m"][0]) * am["chord_m"],
        "tail_area_m2_recomputed": (at["span_y_m"][1] - at["span_y_m"][0]) * at["chord_m"],
        "nominal_prop_ground_gap_m_recomputed": round(ahub[2] - aradius - ag["ground_z_m"], 6),
        "wheel_ground_gaps_m_recomputed": [round(c[2] - ag["wheel_radius_m"] - ag["ground_z_m"], 6)
                                            for c in ag["wheel_centers_m"]],
        "light_empty_fwd_seat": ledger_state(items, "mass_kg", "centroid_m", {
            "M01": (60, [-0.1, 0, 0])}, removals=("M04",)),
        "heavy_full_aft_seat": ledger_state(items, "mass_kg", "centroid_m", {
            "M01": (90, [0.4, 0, 0])}),
        "limits": "Rigid nominal clearances only; loaded gear deflection and swept controls untested",
    }
    result["astra"]["necessary_level_force_coefficient_nominal"] = {
        str(v): required_level_force_coefficient(333, v, 30)
        for v in a["analysis_matrix"]["speeds_m_s"]
    }

    # Fable's x is aft. The model supplies a full ledger and seat/fuel ranges.
    fi = f["mass_ledger"]["items"]
    fs = f["three_view_coordinate_schedule"]
    fp = fs["propellers"]
    fd = f["propulsion"]["propellers"]
    fground = -0.75  # coordinate_convention.frame_B and wheel schedule
    fext = {}
    for pilot_mass, seat_x, fuel, name in (
        (75, 0.20, True, "75kg_forward_full"),
        (75, 0.50, True, "75kg_aft_full"),
        (75, 0.35, False, "75kg_mid_empty"),
        (65, 0.50, True, "65kg_aft_full"),
        (65, 0.50, False, "65kg_aft_empty"),
        (85, 0.20, True, "85kg_forward_full"),
        (85, 0.20, False, "85kg_forward_empty"),
    ):
        state = ledger_state(fi, "mass", "centroid",
                             {"P05": (pilot_mass, [seat_x, 0, 0.75])},
                             removals=() if fuel else ("P07b",))
        state["cg_percent_lower_deck_chord"] = round(
            100 * (state["cg_m"][0] - fs["lower_deck_P01"]["LE_root"][0])
            / (fs["lower_deck_P01"]["TE_root"][0] - fs["lower_deck_P01"]["LE_root"][0]), 3)
        fext[name] = state
    reported = f["mass_ledger"]["summary"]["cg_extremes"]
    result["fable"] = {
        "biplane_projected_area_m2_recomputed": round(2 * 2 * 5.75 * 1.85, 6),
        "prop_ground_gap_m_recomputed": round(fp["hubs"][0][2] - fp["radius"] - fground, 6),
        "prop_disc_to_disc_gap_m_recomputed": round(
            abs(fp["hubs"][1][1] - fp["hubs"][0][1]) - 2 * fp["radius"], 6),
        "prop_disc_to_body_side_gap_m_recomputed": round(
            abs(fp["hubs"][0][1]) - fp["radius"] - 0.40, 6),
        "prop_disc_to_wing_TE_axial_gap_m_recomputed": round(
            fp["disc_plane_x"] - fs["lower_deck_P01"]["TE_root"][0], 6),
        "loading_states": fext,
        "reported_65kg_aft_percent_chord": reported["pilot_65kg_aft"],
        "reported_85kg_forward_percent_chord": reported["pilot_85kg_fwd"],
        "wheel_z_coordinates_m": [row[2] for row in fs["wheels"]],
        "wheel_coordinate_issue": "All three wheel z coordinates equal the ground plane; if these are wheel centres, any positive wheel radius penetrates ground. Their point semantics and radii are unspecified.",
        "limits": "Prop gaps are rigid nominal values without blade thickness, flex, outrigger deflection or tolerance",
    }
    result["fable"]["necessary_level_force_coefficient_nominal"] = {
        str(v): required_level_force_coefficient(309.5, v, 42.55)
        for v in f["analysis_test_matrix"]["states"]["V_m_s"]
    }
    result["fable"]["extreme_cg_claims_match_recomputed"] = (
        abs(fext["65kg_aft_full"]["cg_percent_lower_deck_chord"]
            - float(reported["pilot_65kg_aft"].split()[0])) < 0.1
        and abs(fext["85kg_forward_full"]["cg_percent_lower_deck_chord"]
                - float(reported["pilot_85kg_fwd"].split()[0])) < 0.1
    )

    # Opus only supplies its V3 geometry schedule in prose, not in structured
    # coordinates. These explicitly quoted numbers have the archived response
    # hash above, but cannot constitute a CAD collision test.
    oi = o["mass_items"]
    oext = {
        "70kg_empty": ledger_state(oi, "m", "c", removals=("E3b",)),
        "90kg_full": ledger_state(oi, "m", "c", {"O1": (90, [-0.9, 0, 0.3])}),
        "90kg_empty": ledger_state(oi, "m", "c", {"O1": (90, [-0.9, 0, 0.3])},
                                   removals=("E3b",)),
    }
    # The rectangle extends x=4.8..5.6, z=0.25..0.60; the far-aft lower
    # corner is limiting when the nose rotates upward (aft moves down).
    ventral_x, ventral_z = 5.6, 0.25
    ground, pitch_deg = -0.9, 13
    result["opus"] = {
        "biplane_projected_area_m2_from_prose": 2 * 11 * 1.8,
        "nominal_prop_ground_gap_m_from_prose": round(0.9 - 1.2 - ground, 6),
        "prop_disc_to_lower_wing_TE_plane_m_from_prose": round(2.1 - 1.8, 6),
        "loading_states": oext,
        "ventral_13deg_reported_m": o["clearances_m"]["ventral_ground_13deg"],
        "ventral_13deg_gap_m_if_pivot_at_aft_skid_x1p6": pitch_clearance(
            ventral_x, ventral_z, 1.6, ground, ground, pitch_deg),
        "ventral_13deg_gap_m_if_pivot_at_wheel_x0p45": pitch_clearance(
            ventral_x, ventral_z, 0.45, ground, ground, pitch_deg),
        "tail_skid_tip_gap_m_if_aft_skid_pivot_at_13deg": pitch_clearance(
            5.5, 0, 1.6, ground, ground, pitch_deg),
        "tail_skid_first_contact_deg_if_aft_skid_pivot": round(
            math.degrees(math.atan2(0.9, 5.5 - 1.6)), 6),
        "rotation_pivot_status": "Aft-skid x=1.6 rigid contact reproduces the 0.221 m claim and brings tail-skid tip x=5.5,z=0 to ground at ~12.995 deg. Wheel-pivot-only rotation would intersect ground, so contact must transfer or the structure/gear deform. Actual loaded contact path remains unresolved.",
        "limits": "No solid 3D geometry, skid-contact path, blade sweep, or loaded deflection is supplied",
    }
    result["opus"]["necessary_level_force_coefficient_nominal"] = {
        str(v): required_level_force_coefficient(361.3, v, 39.6)
        for v in o["test_matrix"]["V_m_s"]
    }
    result["necessary_force_coefficient_definition"] = (
        "C_Z,eq = mg/(0.5 rho V^2 Sref), rho=1.225 kg/m3, g=9.80665 m/s2. "
        "This is the required total vertical force normalized by wing reference area "
        "for steady level flight; wing/tail split, incidence, stall, trim and power remain unknown."
    )

    result["blocking_unknowns"] = [
        "Astra: installed surfaces and actuator swept volumes under load; gear and prop deflection",
        "Fable: reconcile light/heavy pilot CG percentages; define wheel centres/radii and measure 0.04-0.05 m critical gaps with tolerance",
        "Opus: resolve active ground-contact pivot versus pitch angle and skid-brace/ventral-fin clearance",
        "All: installed aerodynamic coefficients, drag, propeller map, thrust line effects, stall and validated controls needed before independent trim",
    ]
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
