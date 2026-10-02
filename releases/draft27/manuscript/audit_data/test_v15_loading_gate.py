import copy
import unittest
from v15_fable_loading_gate import ledger

class LoadingTests(unittest.TestCase):
    def test_symmetric_pair(self):
        rows=[dict(mass_kg=2,centroid=[0,y,0],I_intr=[1,2,3]) for y in (-1,1)]
        m,cg,i,p=ledger(rows)
        self.assertEqual((m,cg,i,p),(4,[0,0,0],[6,4,10],0))

    def test_translation_invariance(self):
        rows=[dict(mass_kg=2,centroid=[1,2,3],I_intr=[1,2,3]),
              dict(mass_kg=3,centroid=[-2,0,1],I_intr=[2,3,4])]
        shifted=copy.deepcopy(rows)
        for r in shifted:r['centroid']=[v+10 for v in r['centroid']]
        a,b=ledger(rows),ledger(shifted)
        for x,y in zip(a[2],b[2]):self.assertAlmostEqual(x,y)
        self.assertAlmostEqual(a[3],b[3])

    def test_product_sign(self):
        rows=[dict(mass_kg=1,centroid=[x,0,x],I_intr=[0,0,0]) for x in (-1,1)]
        self.assertEqual(ledger(rows)[3],2)

if __name__=='__main__':unittest.main()
