import unittest

from flight_dynamics_gate_v2 import audit, reduced_pitch_signs


class FlightDynamicsGateTests(unittest.TestCase):
    def test_current_cases_are_conditional_only(self):
        result = audit()
        self.assertFalse(result["any_aircraft_dynamically_confirmed"])
        self.assertEqual(len(result["records"]), 3)
        for record in result["records"][:2]:
            self.assertTrue(record["partial_screen"]["reduced_model_hurwitz_signs_for_any_positive_Iyy"])
            self.assertEqual(record["full_dynamic_gate"], "NOT_ASSESSED")
            self.assertGreater(record["partial_screen"]["one_plus_Zq_over_U"], 0)
        self.assertEqual(result["records"][2]["partial_screen"], "NOT_ASSESSED")

    def test_destabilizing_pitch_slope_fails_partial_screen(self):
        case = {"mass_kg": 320, "speed_m_s": 18, "area_m2": 30, "chord_m": 2.5}
        derivatives = {"CLa": 4, "Cma": 100, "CLq": 6, "Cmq": -4}
        self.assertFalse(reduced_pitch_signs(case, derivatives)[
            "reduced_model_hurwitz_signs_for_any_positive_Iyy"])

    def test_missing_derivative_is_error(self):
        case = {"mass_kg": 320, "speed_m_s": 18, "area_m2": 30, "chord_m": 2.5}
        with self.assertRaises(ValueError):
            reduced_pitch_signs(case, {"CLa": 4, "Cma": -1, "CLq": 6})


if __name__ == "__main__":
    unittest.main()
