"""Small analytical invariants for the centroid-only inertia assembly."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_v14_inertia_lower_bounds import matrix


class ParallelAxisTests(unittest.TestCase):
    def test_two_unit_points_on_x_axis(self):
        result = matrix([(1, [-1, 0, 0]), (1, [1, 0, 0])])
        self.assertEqual(result["mass_kg"], 2)
        self.assertEqual(result["cg_xyz_m"], [0, 0, 0])
        self.assertEqual(result["parallel_axis_tensor_kg_m2"],
                         [[0, 0, 0], [0, 2, 0], [0, 0, 2]])

    def test_translation_invariance_and_cross_term(self):
        original = matrix([(2, [0, 0, 0]), (1, [3, 0, 4])])
        shifted = matrix([(2, [5, -7, 2]), (1, [8, -7, 6])])
        self.assertEqual(original["parallel_axis_tensor_kg_m2"],
                         shifted["parallel_axis_tensor_kg_m2"])
        tensor = original["parallel_axis_tensor_kg_m2"]
        self.assertAlmostEqual(tensor[0][2], -8)
        self.assertAlmostEqual(tensor[2][0], -8)
        self.assertAlmostEqual(tensor[0][0], 32 / 3, places=6)
        self.assertAlmostEqual(tensor[2][2], 6)

    def test_empty_ledger_rejected(self):
        with self.assertRaises(ValueError):
            matrix([])


if __name__ == "__main__":
    unittest.main()
