import unittest
from v2_trim_solve import residual


class TrimTests(unittest.TestCase):
    def test_zero_alpha_balanced(self):
        s={'V':10,'S':10,'mass':100,'c':1,'arm':0,'CD0':.05}
        q=.5*1.225*100
        r=residual({'CLtot':980.665/(q*10),'CDind':.02,'Cmtot':0},s,0)
        self.assertAlmostEqual(r['Rz_N'],0)
        self.assertAlmostEqual(r['Rx_N'],0)
        self.assertAlmostEqual(r['My_Nm'],0)

    def test_inclined_thrust_and_arm(self):
        s={'V':10,'S':10,'mass':100,'c':1,'arm':-.4,'CD0':.05}
        r=residual({'CLtot':1,'CDind':.02,'Cmtot':0},s,5)
        self.assertGreater(r['Tvertical_N'],0)
        self.assertAlmostEqual(r['My_Nm'],-.4*r['T_N'])
        self.assertAlmostEqual(r['Rx_N'],0)


if __name__=='__main__':unittest.main()
