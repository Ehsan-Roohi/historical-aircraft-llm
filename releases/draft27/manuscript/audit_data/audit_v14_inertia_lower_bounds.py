"""Parallel-axis inertia contributions from latest complete mass ledgers.

Each intrinsic component tensor is unknown unless a verified mass distribution
exists. The assembled matrix is only a positive-semidefinite lower matrix
bound on the true tensor, not a physical inertia input for modal analysis.
"""

from pathlib import Path
import hashlib
import json
import math


ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / "v13_fable_arithmetic_attempt01/responses/claude-fable-5-1/response.json"
OPUS = ROOT / "v12_opus_retry_attempt01/responses/claude-opus-5-5/response.json"
OUT = ROOT / "analysis/results/v14_inertia_lower_bounds01.json"


def load_payload(path):
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    if wrapper["status"] != "completed":
        raise ValueError(f"Noncomplete response: {path}")
    return json.loads(wrapper["response"])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix(rows):
    m = sum(row[0] for row in rows)
    if m <= 0 or not math.isfinite(m):
        raise ValueError("Positive finite total mass required")
    cg = [sum(mass * xyz[i] for mass, xyz in rows) / m for i in range(3)]
    j = [[0.0] * 3 for _ in range(3)]
    for mass, xyz in rows:
        d = [xyz[i] - cg[i] for i in range(3)]
        r2 = sum(v * v for v in d)
        for i in range(3):
            for k in range(3):
                j[i][k] += mass * ((r2 if i == k else 0) - d[i] * d[k])
    return {"mass_kg": round(m, 6), "cg_xyz_m": [round(v, 6) for v in cg],
            "parallel_axis_tensor_kg_m2": [[round(v, 6) for v in row] for row in j],
            "Ixx_centroid_only_lower_bound_kg_m2": round(j[0][0], 6),
            "Iyy_centroid_only_lower_bound_kg_m2": round(j[1][1], 6),
            "Izz_centroid_only_lower_bound_kg_m2": round(j[2][2], 6),
            "interpretation": "Conditional on the model's point-mass/centroid ledger: J_true = J_parallel + sum(J_intrinsic_i); the missing sum is positive semidefinite. Off-diagonal elements are not individually bounded by the printed parallel-axis values. Tensor off-diagonal convention is -sum(m*d_i*d_j)."}


def rows_from(data, key, id_key, excluded):
    rows = []
    for entry in data[key]:
        if entry[id_key] in excluded:
            continue
        mass = float(entry["mass_kg"])
        xyz = [float(v) for v in entry["centroid_xyz_m"]]
        if mass <= 0 or len(xyz) != 3 or not all(math.isfinite(v) for v in xyz):
            raise ValueError(f"Invalid mass/centroid: {entry[id_key]}")
        rows.append((mass, xyz))
    return rows


def main():
    fable = load_payload(FABLE)
    opus = load_payload(OPUS)
    f_rows = rows_from(fable, "full_mass_ledger_rows", "ID", {"SUM"})
    o_rows = rows_from(opus, "mass_ledger_rows", "id", {"LEDGER_AUDIT"})
    assert len(f_rows) == 26 and len(o_rows) == 30
    f_result = matrix(f_rows)
    o_result = matrix(o_rows)
    assert abs(f_result["mass_kg"] - 354.3) < 1e-6
    assert abs(o_result["mass_kg"] - 340.3) < 1e-6
    assert abs(f_result["cg_xyz_m"][0] - 1.530739) < 1e-6
    assert abs(o_result["cg_xyz_m"][0] - 0.703552) < 1e-6
    result = {"scope": "nominal centroid-only parallel-axis tensor, not physical inertia",
              "fable_v13": {"source_sha256": sha(FABLE), "component_rows": len(f_rows), **f_result},
              "opus_v12": {"source_sha256": sha(OPUS), "component_rows": len(o_rows), **o_result},
              "astra_v12": "No adopted installed V12 aircraft ledger/tensor",
              "modal_acceptance": "NOT ASSESSED: intrinsic tensors and installed derivatives missing"}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUT.name)


if __name__ == "__main__":
    main()
