import json
import unittest
from v15_fable_tail_trade import SOURCE,candidate_rows
from v15_fable_loading_gate import ledger

class TailTradeTests(unittest.TestCase):
    def setUp(self):
        self.d=json.loads(json.loads(SOURCE.read_text(encoding='utf-8'))['response'])

    def test_added_mass_and_aft_shift(self):
        a=ledger(candidate_rows(self.d,1,65,.35,8))
        b=ledger(candidate_rows(self.d,1.5,65,.35,8))
        self.assertAlmostEqual(b[0]-a[0],4)
        self.assertGreater(b[1][0],a[1][0])

    def test_symmetric_tail(self):
        rr=candidate_rows(self.d,1.5,65,.35,8)
        tail=[r for r in rr if r['ID'] in ('P11L','P11R')]
        self.assertAlmostEqual(sum(r['mass_kg']*r['centroid'][1] for r in tail),0)
        self.assertAlmostEqual(abs(tail[0]['centroid'][1]),.55+2.3*1.5/2)

    def test_original_unchanged(self):
        before=json.dumps(self.d,sort_keys=True)
        candidate_rows(self.d,1.5,65,.35,0)
        self.assertEqual(before,json.dumps(self.d,sort_keys=True))

if __name__=='__main__':unittest.main()
