import hashlib,json,unittest
from pathlib import Path
import numpy as np
from draw_stage_threeviews import ROOT,OUT,avl,MODELS

class StageViews(unittest.TestCase):
    def test_six_sheets_and_source_hashes(self):
        rows=json.loads((OUT/'manifest.json').read_text())
        self.assertEqual(len(rows),7)
        self.assertEqual({(r['stage'],r['model']) for r in rows},{(s,m) for s in ['V1','V2'] for m in MODELS}|{('Wright','wright-flyer-1903')})
        for row in rows:
            for src in row['sources']:
                self.assertEqual(hashlib.sha256((ROOT/src['path']).read_bytes()).hexdigest(),src['sha256'])
            self.assertTrue((ROOT/row['figure']).exists())
    def test_astra_metric_span_and_cg(self):
        p=ROOT/'analysis/results/v2_trim_solve01/gpt-6-astra/c14_s72_verify/aircraft.avl'
        polys,cg=avl(p);pts=np.concatenate([v for n,v in polys if n=='main'])
        self.assertAlmostEqual(np.ptp(pts[:,1]),12)
        self.assertAlmostEqual(cg[0],0,places=6)
    def test_fable_unresolved_label(self):
        text=(OUT/'V2/claude-fable-5-1.svg').read_text()
        self.assertIn('geometry unresolved',text)
        self.assertIn('NOT reconstructed',text)
    def test_wright_reference_not_cg(self):
        text=(OUT/'Wright/wright-flyer-1903.svg').read_text()
        self.assertIn('moment reference (not CG)',text)
        self.assertIn('1903',text)

if __name__=='__main__':unittest.main()
