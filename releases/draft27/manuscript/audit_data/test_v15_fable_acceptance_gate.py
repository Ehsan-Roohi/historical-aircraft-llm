"""Regression checks for the Fable V15 evidence gate."""

import unittest

from v15_fable_acceptance_gate import build_gate


class AcceptanceGateTests(unittest.TestCase):
    def test_partial_balance_is_not_full_trim(self):
        report = build_gate()
        self.assertLess(abs(report["independent_arithmetic"]["wing_tail_lift_minus_assumed_weight_N"]), 1.0)
        self.assertLess(abs(report["independent_arithmetic"]["wing_tail_pitch_moment_about_nominal_CG_Nm"]), 1.0)
        self.assertEqual(report["six_component_residuals"]["Fx"]["status"], "UNKNOWN")
        self.assertEqual(report["six_component_residuals"]["Fy"]["status"], "UNKNOWN")
        self.assertEqual(report["six_component_residuals"]["Mx_CG"]["status"], "UNKNOWN")
        self.assertEqual(report["six_component_residuals"]["Mz_CG"]["status"], "UNKNOWN")
        self.assertFalse(report["acceptance"]["full_six_component_trim"])

    def test_unknown_unsteady_derivatives_block_modes(self):
        report = build_gate()
        self.assertEqual(report["static_and_dynamic_stability"]["C_m_alpha_dot"], "UNKNOWN")
        self.assertEqual(report["static_and_dynamic_stability"]["validated_longitudinal_and_lateral_modes"], "NOT_CALCULABLE")
        self.assertFalse(report["acceptance"]["accepted_modes"])

    def test_high_speed_power_case_remains_failed(self):
        report = build_gate()
        self.assertGreater(report["propulsion_and_structure"]["H16W_assumed_shaft_deficit_W"], 4000)
        self.assertEqual(report["acceptance"]["flightworthiness"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
