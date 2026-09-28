"""Arithmetic tests for the V3 conditional power screen."""

import unittest

from audit_v3_power_necessity import required_engine_power


class V3PowerNecessityTests(unittest.TestCase):
    def test_astra_high_case(self):
        self.assertAlmostEqual(required_engine_power(520, 18, 0.55, 0.95),
                               17913.875598, places=5)

    def test_fable_nominal_case(self):
        self.assertEqual(required_engine_power(426, 13, 0.5), 11076)

    def test_invalid_efficiency_rejected(self):
        with self.assertRaises(ValueError):
            required_engine_power(400, 15, 1.1)


if __name__ == "__main__":
    unittest.main()
