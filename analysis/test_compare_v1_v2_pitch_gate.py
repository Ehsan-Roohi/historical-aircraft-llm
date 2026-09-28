import json
import unittest
from pathlib import Path


class VersionedPitchGateTests(unittest.TestCase):
    def test_static_and_reduced_dynamic_are_not_conflated(self):
        path = Path(__file__).parent/'results/v1_v2_pitch_gate_comparison01.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        records = {(row['model'], row['version']): row for row in data['records']}
        astra_initial = records['astra', 'V1']
        self.assertGreater(astra_initial['Cma_per_rad'], 0)
        self.assertFalse(astra_initial['static_pitch_restoring_in_lifting_model'])
        self.assertTrue(astra_initial['conditional_reduced_pitch_hurwitz'])
        self.assertEqual(astra_initial['dynamic_flight_acceptance'], 'NOT_ASSESSED')
        self.assertTrue(records['opus', 'V1']['static_pitch_restoring_in_lifting_model'])
        self.assertTrue(records['astra', 'V2']['static_pitch_restoring_in_lifting_model'])


if __name__ == '__main__':
    unittest.main()
