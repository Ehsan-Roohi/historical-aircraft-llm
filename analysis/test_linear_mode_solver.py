import unittest

from linear_mode_solver import lateral_matrix, longitudinal_matrix, roots


class LinearModeSolverTests(unittest.TestCase):
    def test_missing_longitudinal_term_is_not_zero_filled(self):
        with self.assertRaisesRegex(ValueError, "Missing required"):
            longitudinal_matrix({"U": 18})

    def test_full_synthetic_longitudinal_matrix(self):
        # Synthetic arithmetic fixture; explicitly not an aircraft prediction.
        data = dict(U=18, theta=0, Xu=-.1, Xa=0, Zu=0, Za=-4,
                    Zadot=-.2, Zq=-1, Mu=0, Ma=-2, Madot=-.1, Mq=-3)
        matrix = longitudinal_matrix(data)
        self.assertEqual(matrix.shape, (4, 4))
        self.assertAlmostEqual(matrix[1, 0], 0)
        self.assertAlmostEqual(matrix[1, 1], -4/18.2)
        self.assertEqual(len(roots(matrix)), 4)

    def test_missing_lateral_term_and_bad_inertia_fail(self):
        with self.assertRaisesRegex(ValueError, "Missing required"):
            lateral_matrix({"U": 15})
        data = dict(U=15, theta=0, Ixx=1, Izz=1, Ixz=2,
                    Yb=-1, Yp=0, Yr=0, Lb=1, Lp=-1, Lr=0,
                    Nb=1, Np=0, Nr=-1)
        with self.assertRaisesRegex(ValueError, "Invalid speed or lateral inertia"):
            lateral_matrix(data)


if __name__ == "__main__":
    unittest.main()
