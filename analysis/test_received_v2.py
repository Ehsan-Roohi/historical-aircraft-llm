import json
import unittest
from pathlib import Path
from audit_received_v2 import ledger, audit
from v2_independent_probe import geometry

SOURCE=Path(__file__).resolve().parent/'results/received_v2_audit01'


class AuditTests(unittest.TestCase):
    def test_simple_mass(self):
        r=ledger([{'m':2,'p':[0,0,0]},{'m':2,'p':[2,0,0]}],'m','p')
        self.assertEqual(r['cg_native_m'],[1,0,0])

    def test_fable_box(self):
        d=json.loads((SOURCE/'claude-fable-5-1.design.json').read_text(encoding='utf8'))
        r=audit('claude-fable-5-1',d)
        self.assertEqual(r['mass_kg'],295)
        self.assertIn('P07',r['centroids_outside_declared_boxes'])
        self.assertLess(r['tail_sweep_z_m_rigid_chord_including_rigging'][0],.72)

    def test_astra_moment_closure(self):
        d=json.loads((SOURCE/'gpt-6-astra.design.json').read_text(encoding='utf8'))
        r=audit('gpt-6-astra',d)
        self.assertAlmostEqual(r['claimed_load_ledger_recomputed']['pitch_residual_Nm'],0,places=5)

    def test_geometry_reference_and_control_sign(self):
        for name,area,delta in [('gpt-6-astra',30,-.4672699715088987),('claude-opus-5-5',38,-3.4)]:
            g,foil,s=geometry(name,6,24)
            self.assertEqual(float(g.splitlines()[3].split()[0]),area)
            self.assertAlmostEqual(s['delta'],delta,places=4)
            self.assertIn('CONTROL\npitch 1',g)
            self.assertGreater(len(foil.splitlines()),10)


if __name__=='__main__': unittest.main()
