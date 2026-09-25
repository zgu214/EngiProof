import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results/paper_studies5'
class PaperStudies5(unittest.TestCase):
    def test_p08_coefficient(self):
        s=json.loads((OUT/'p08_summary.json').read_text()); self.assertLess(abs(s['relative_difference_percent']),0.5)
    def test_p12_eq22_recovery(self):
        s=json.loads((OUT/'p12_summary.json').read_text()); self.assertLess(abs(s['ratio_direct_b_over_a']-s['ratio_eq22_b_over_a']),0.002); self.assertLess(abs(s['ratio_direct_c_over_a']-s['ratio_eq22_c_over_a']),0.003)
    def test_p12_table5_source_inconsistency_retained(self):
        s=json.loads((OUT/'p12_summary.json').read_text()); self.assertTrue(s['table5_beta10_duplicates_beta03'])
if __name__=='__main__': unittest.main()
