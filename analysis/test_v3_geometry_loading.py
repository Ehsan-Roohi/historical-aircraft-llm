"""Regression tests for the limited V3 geometry/loading audit."""

import unittest

from audit_v3_geometry_loading import (SOURCES, ledger_state, load_design,
                                       pitch_clearance, required_level_force_coefficient)


class V3GeometryLoadingTests(unittest.TestCase):
    def test_source_designs_have_one_structured_block(self):
        for source in SOURCES.values():
            with self.subTest(source=source.name):
                self.assertIsInstance(load_design(source), dict)

    def test_fable_light_pilot_aft_cg(self):
        design = load_design(SOURCES["fable"])
        state = ledger_state(design["mass_ledger"]["items"], "mass", "centroid",
                             {"P05": (65, [0.5, 0, 0.75])})
        self.assertAlmostEqual(state["mass_kg"], 299.5)
        self.assertAlmostEqual(state["cg_m"][0], 1.629499, places=6)
        self.assertAlmostEqual(100 * (state["cg_m"][0] - 0.95) / 1.85,
                               36.73, places=2)

    def test_opus_rotated_fin_depends_on_pivot(self):
        aft_skid = pitch_clearance(5.6, 0.25, 1.6, -0.9, -0.9, 13)
        wheel = pitch_clearance(5.6, 0.25, 0.45, -0.9, -0.9, 13)
        self.assertAlmostEqual(aft_skid, 0.220721, places=6)
        self.assertLess(wheel, 0)
        self.assertAlmostEqual(pitch_clearance(5.5, 0, 1.6, -0.9, -0.9, 13),
                               -0.000376, places=6)

    def test_pitch_zero_is_nominal_height(self):
        self.assertAlmostEqual(pitch_clearance(5.6, 0.25, 0.45, -0.9,
                                               -0.9, 0), 1.15)

    def test_required_force_coefficient_is_not_trim(self):
        self.assertAlmostEqual(required_level_force_coefficient(309.5, 13, 42.55),
                               0.689111, places=6)


if __name__ == "__main__":
    unittest.main()
