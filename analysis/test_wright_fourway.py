import unittest
from wright_fourway_assessment import dimensional,secant

class WrightComparison(unittest.TestCase):
    def test_load_scaling(self):
        c={'CLtot':.8,'CDind':.05,'Cmtot':.02}
        a=dimensional(c,40,2,12,340);b=dimensional(c,40,2,24,340)
        self.assertAlmostEqual(b['lift_N'],4*a['lift_N'])
        self.assertAlmostEqual(b['induced_drag_power_W_only'],8*a['induced_drag_power_W_only'])
        self.assertAlmostEqual(b['aerodynamic_moment_about_reference_Nm'],4*a['aerodynamic_moment_about_reference_Nm'])
    def test_reference_descriptor_sign(self):
        s=secant({'CLtot':.56709,'Cmtot':-.04407},{'CLtot':.81394,'Cmtot':.01026})
        self.assertGreater(s['Cm_secant_per_deg'],0)
        self.assertAlmostEqual(s['negative_Cm_over_CL_slope_percent'],-22.0093173992303)
        self.assertIn('NOT historical CG',s['interpretation'])

if __name__=='__main__':unittest.main()
