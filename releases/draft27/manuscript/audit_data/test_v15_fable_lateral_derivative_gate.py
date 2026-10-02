"""Invariant checks for the Fable V15 lateral derivative screen."""

import unittest

from v15_fable_lateral_derivative_gate import build_gate


class LateralGateTests(unittest.TestCase):
    def test_geometry_change_requires_retrim(self):
        gate = build_gate()
        self.assertLess(gate["geometry_sensitivity"]["split_tip_CL_change"], -0.04)
        self.assertGreater(gate["retrim"]["alpha_deg"], 6.5)

    def test_qualified_yaw_slope_not_a_mode(self):
        gate = build_gate()
        cn_beta = gate["finite_difference_derivatives"]["Cntot"]["beta"]
        self.assertGreater(cn_beta["fine_per_rad"], 0)
        self.assertLess(cn_beta["relative_mesh_difference_percent_of_fine"], 3)
        self.assertFalse(gate["acceptance"]["accepted_lateral_modes"])

    def test_roll_sideslip_slope_mesh_sensitive(self):
        gate = build_gate()
        cl_beta = gate["finite_difference_derivatives"]["Cltot"]["beta"]
        self.assertGreater(cl_beta["relative_mesh_difference_percent_of_fine"], 10)
        self.assertFalse(gate["acceptance"]["validated_lateral_derivatives"])


if __name__ == "__main__":
    unittest.main()
