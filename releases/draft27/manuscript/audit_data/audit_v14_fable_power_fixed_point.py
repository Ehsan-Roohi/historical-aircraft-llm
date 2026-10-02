"""Independent arithmetic screen of Fable V13's *assumed* power spiral.

This is a scenario calculation, not an engine or propeller validation.
Input numbers come from the complete source-hashed V13 response. The reported
mass-specific-power relation is deliberately treated as an assumption.
"""

from pathlib import Path
import hashlib
import json
import math


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "v13_fable_arithmetic_attempt01/responses/claude-fable-5-1/response.json"
OUT = ROOT / "analysis/results/v14_fable_power_fixed_point01.json"


def main():
    raw = SOURCE.read_bytes()
    wrapper = json.loads(raw)
    if wrapper["status"] != "completed":
        raise ValueError("Fable V13 response incomplete")
    model = json.loads(wrapper["response"])
    chain = model["corrected_power_chain"]
    targets = chain["retained_target_chain_D"]
    requirements = chain["requirement_after_corrected_ledger_D"]
    cases = model["revised_loading_cases"]["cases"]
    heaviest = next(case for case in cases if case["case"].startswith("85 kg, seat 0.25, full"))
    base_mass_kg = heaviest["mass_kg"]
    base_engine_W = targets["P_e_W"]
    assumed_drive_efficiency = targets["P_out_W"] / base_engine_W
    assumed_specific_mass_kg_per_kW = 5.1
    assumed_V_m_s = 13.0
    assumed_q_Pa = 103.51
    assumed_area_m2 = 42.0
    assumed_oswald = 0.70
    assumed_aspect_ratio = 6.2
    assumed_CD0 = 0.08
    assumed_extra_drag_N = 10.0
    assumed_propulsive_efficiency = 0.45
    assumed_reserve_factor = 1.15
    g_m_s2 = 9.81
    drag_cases = model["corrected_drag_power_cases"]
    formula = drag_cases["formula"]
    for fragment in ("S 42", "e 0.70", "AR 6.2", "V13", "CD0 0.08", "eta 0.45"):
        if fragment not in formula and fragment not in str(drag_cases["cases_D"]):
            raise ValueError(f"Source assumption missing: {fragment}")
    if not (base_mass_kg == 364.3 and base_engine_W == 19500 and
            math.isclose(assumed_drive_efficiency, 0.95)):
        raise ValueError("Frozen Fable V13 baseline changed")

    def budget(engine_W, couple_engine_mass):
        delta_engine_kg = (engine_W - base_engine_W) * assumed_specific_mass_kg_per_kW / 1000 if couple_engine_mass else 0.0
        mass_kg = base_mass_kg + delta_engine_kg
        weight_N = mass_kg * g_m_s2
        CL = weight_N / (assumed_q_Pa * assumed_area_m2)
        CDi = CL * CL / (math.pi * assumed_oswald * assumed_aspect_ratio)
        drag_N = (assumed_CD0 + CDi) * assumed_q_Pa * assumed_area_m2 + assumed_extra_drag_N
        propeller_required_W = drag_N * assumed_V_m_s / assumed_propulsive_efficiency
        shaft_required_W = assumed_reserve_factor * propeller_required_W
        engine_required_W = shaft_required_W / assumed_drive_efficiency
        return {"engine_mass_delta_kg": delta_engine_kg, "mass_kg": mass_kg,
                "weight_N": weight_N, "CL": CL, "CDi": CDi, "drag_N": drag_N,
                "propeller_required_W": propeller_required_W,
                "propeller_required_with_reserve_W": shaft_required_W,
                "engine_required_W": engine_required_W}

    uncoupled = budget(base_engine_W, False)
    if not (abs(uncoupled["propeller_required_W"] - requirements["P_req_worst_heaviest_W"]) < 5 and
            abs(uncoupled["propeller_required_with_reserve_W"] - requirements["x1.15_W"]) < 5 and
            abs(uncoupled["engine_required_W"] - requirements["min_P_e_for_15pct_W"]) < 5):
        raise ValueError("Independent base-case recomputation disagrees with frozen response")
    lo, hi = base_engine_W, 30000.0
    if budget(lo, True)["engine_required_W"] <= lo or budget(hi, True)["engine_required_W"] >= hi:
        raise ValueError("Power fixed point not bracketed")
    for _ in range(100):
        mid = (lo + hi) / 2
        if budget(mid, True)["engine_required_W"] > mid:
            lo = mid
        else:
            hi = mid
    coupled_engine_W = (lo + hi) / 2
    coupled = budget(coupled_engine_W, True)
    retained_reserve = targets["P_out_W"] / uncoupled["propeller_required_W"] - 1
    drive_efficiency_needed_at_retained_engine = uncoupled["propeller_required_with_reserve_W"] / base_engine_W
    fuel_kg = 20.0
    assumed_sfc_kg_per_kWh = 0.31
    endurance_min = fuel_kg / (assumed_sfc_kg_per_kWh * base_engine_W / 1000) * 60
    result = {
        "scope": "Evaluator-only arithmetic under unmeasured model assumptions; not an installed power or flight acceptance",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "assumptions": {"V_m_s": assumed_V_m_s, "q_Pa": assumed_q_Pa,
                        "S_m2": assumed_area_m2, "e": assumed_oswald,
                        "AR": assumed_aspect_ratio, "CD0": assumed_CD0,
                        "extra_drag_N": assumed_extra_drag_N,
                        "eta_prop": assumed_propulsive_efficiency,
                        "eta_drive": assumed_drive_efficiency,
                        "reserve_factor": assumed_reserve_factor,
                        "incremental_engine_mass_kg_per_kW": assumed_specific_mass_kg_per_kW,
                        "engine_mass_rule": "base 364.3 kg at 19.5 kW; add 5.1 kg per additional kW only"},
        "independent_uncoupled": uncoupled,
        "coupled_fixed_point": {"engine_target_W": coupled_engine_W,
                                "budget": coupled,
                                "equation_residual_W": coupled_engine_W - coupled["engine_required_W"]},
        "retained_19_5kW_target": {"propeller_shaft_available_W": targets["P_out_W"],
                                    "reserve_fraction": retained_reserve,
                                    "reserve_shortfall_W": uncoupled["propeller_required_with_reserve_W"] - targets["P_out_W"],
                                    "required_eta_drive_if_engine_target_unchanged": drive_efficiency_needed_at_retained_engine},
        "fuel_sfc_arithmetic_only": {"fuel_kg": fuel_kg, "assumed_sfc_kg_per_kWh": assumed_sfc_kg_per_kWh,
                                     "at_target_power_min": endurance_min,
                                     "note": "This contradiction does not verify actual endurance or fuel flow"},
        "disposition": "HOLD: the corrected paper target is not an available engine curve; propeller absorption, torque, thermal and mass assumptions are unmeasured"
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUT.name, round(coupled_engine_W, 1))


if __name__ == "__main__":
    main()
