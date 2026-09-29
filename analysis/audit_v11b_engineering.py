"""Independent selected arithmetic screen of full-context V11b responses.

Mass and geometry numbers remain model-proposed; passing arithmetic does not
establish installed lift, power, stability, strength, clearance or flight.
"""

import json
import math
from pathlib import Path

from audit_v3_geometry_loading import ledger_state, load_design


ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "v11b_design_candidate_attempt01"


def payload(model):
    source = ATTEMPT / "responses" / model / "response.json"
    return json.loads(json.loads(source.read_text(encoding="utf-8"))["response"])


def overlap_box(center_a, size_a, center_b, size_b):
    lengths = [max(0.0, min(center_a[i] + size_a[i] / 2,
                            center_b[i] + size_b[i] / 2)
                   - max(center_a[i] - size_a[i] / 2,
                         center_b[i] - size_b[i] / 2)) for i in range(3)]
    return {"intersection_lengths_m": lengths,
            "intersection_volume_m3": math.prod(lengths)}


def main():
    f_baseline = load_design(
        ROOT / "received_v9_retry_65009709/claude-fable-5-1/response.json")
    f = payload("claude-fable-5-1")
    o = payload("claude-opus-5-5")
    a = payload("gpt-6-astra")
    items = list(f_baseline["mass_ledger"]["items"])
    items.append({"id": "P19", "mass": 0.3, "centroid": [0.25, 0, 0.4]})
    checks = []
    for case in f["cg_cases"]:
        if "mass_kg" not in case:
            continue
        state_name = case["state"]
        pilot = int(state_name.split(" kg")[0])
        seat = float(state_name.split("seat ")[1].split()[0])
        full = "empty" not in state_name
        recomputed = ledger_state(
            items, "mass", "centroid", {"P05": (pilot, [seat, 0, 0.75])},
            removals=() if full else ("P07b",))
        reported_cg = case["cg_xyz"]
        mass_gap = recomputed["mass_kg"] - case["mass_kg"]
        cg_gap = [recomputed["cg_m"][i] - reported_cg[i] for i in range(3)]
        checks.append({"state": state_name, "mass_gap_kg": round(mass_gap, 6),
                       "cg_gap_m": [round(v, 6) for v in cg_gap],
                       "pass_rounded": abs(mass_gap) < 0.01 and
                       max(abs(v) for v in cg_gap) < 0.001})
    wheel_mass = 2 * 2 + 2 + 2 * 2.5 + 1
    wheel_mx = 2 * 2 * 0.4 + 2 * 3.2 + 2 * 2.5 * 1.2 + 1 * 4.0
    power_checks = []
    speed_by_case = {"nominal V13": 13, "nominal mass 319.8": 13,
                     "V12": 12, "V16": 16, "optimistic": 13,
                     "previous worst": 13}
    eta_by_case = {"optimistic": 0.55, "previous worst": 0.45}
    for case in f["propulsion_cases"]["cases_D"]:
        label = case["case"]
        prefix = next((k for k in speed_by_case if label.startswith(k)), None)
        if prefix is None:
            continue
        speed = speed_by_case[prefix]
        eta = eta_by_case.get(prefix, 0.5)
        recomputed = case["D_N"] * speed / eta
        power_checks.append({"case": label, "reported_W": case["P_req_W"],
                             "recomputed_from_rounded_D_W": round(recomputed, 3),
                             "difference_W": round(case["P_req_W"] - recomputed, 3)})
    # Opus gives three dimensioned boxes. These are *mass-model envelopes*;
    # overlap is an arithmetic finding, not proof of solid-component collision.
    e1 = ([0.25, 0, 0.28], [0.55, 0.6, 0.5])
    e2 = ([0.3, 0, 0.45], [0.2, 0.7, 0.3])
    e3a = ([0.5, 0, 0.6], [0.2, 0.3, 0.16])
    result = {
        "scope": "selected arithmetic and source-claim screen only",
        "astra": {"disposition": a["disposition"],
                  "no_component_revision": len(a["changed_components"]) == 0},
        "fable": {"disposition": f["disposition"],
                  "mass_cg_checks": checks,
                  "all_mass_cg_rounding_pass": all(c["pass_rounded"] for c in checks),
                  "P14_subitems_mass_kg": wheel_mass,
                  "P14_subitems_xCG_m": wheel_mx / wheel_mass,
                  "power_checks": power_checks,
                  "assumed_target_shaft_W": f["propulsion_cases"]["target_shaft_W_A"]["new"],
                  "measured_available_shaft_power": "UNKNOWN",
                  "loaded_clearance": "UNKNOWN"},
        "opus": {"disposition": o["disposition"],
                 "E1_bounds_x_m": [-0.025, 0.525],
                 "E1_E2_box_proxy_overlap": overlap_box(*e1, *e2),
                 "E1_E3a_box_proxy_overlap": overlap_box(*e1, *e3a),
                 "model_E1_x_bounds_0_to_0p5": "ARITHMETIC ERROR: true x -0.025..0.525",
                 "model_E1_E3a_volume_0p0003_m3":
                 "ARITHMETIC ERROR: true 0.000375 m3 if solid box proxies",
                 "overlap_interpretation":
                 "These are ledger inertia/shell proxies. Intersecting envelopes alone do not establish physical collision without occupied-solid definitions."},
        "flight_gate": "NONE PASSED: no measured installed thrust/drag, six-component trim, loaded swept clearances, validated derivatives/modes or structure",
    }
    output = ROOT / "analysis" / "results" / "v11b_engineering_gate01.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(output.name)


if __name__ == "__main__":
    main()
