import unittest
from engiproof.discrepancy import classify_discrepancy, discrepancy_audit, discrepancy_gate

class DiscrepancyAutomationTests(unittest.TestCase):
    def test_bounded_precision_does_not_block(self):
        d={"id":"DX-1","target":"graph/table precision","status":"BOUNDED","observation":"bounded graphical precision residual","engineering_interpretation":"consistent with digitization precision"}
        a=classify_discrepancy(d); self.assertEqual(a["promotion_effect"],"NONE"); self.assertEqual(a["review_priority"],"LOW")
    def test_open_structured_reference_mismatch_blocks(self):
        d={"id":"DX-2","target":"published ratio","status":"OPEN","observation":"calculation differs from published table","engineering_interpretation":"retain without tuning","classification_hint":"PUBLISHED_REFERENCE_MISMATCH","metrics":{"reference_value":0.66,"reproduced_value":0.7056664056684557,"reference_decimals":2},"automation":{"independent_support":"CORROBORATES_REPRODUCTION"}}
        a=classify_discrepancy(d); self.assertEqual(a["category"],"PUBLISHED_REFERENCE_MISMATCH"); self.assertTrue(a["rounding_check"]["beyond_rounding_band"]); self.assertEqual(a["promotion_effect"],"BLOCK_PROMOTION"); self.assertEqual(a["review_priority"],"HIGH")
    def test_p40_is_first_real_blocking_case(self):
        a=discrepancy_audit("P40"); self.assertEqual(a["promotion_blocker_count"],1); item=a["assessments"][0]; self.assertEqual(item["discrepancy_id"],"P40-D001"); self.assertEqual(item["category"],"PUBLISHED_REFERENCE_MISMATCH"); self.assertEqual(item["promotion_effect"],"BLOCK_PROMOTION"); g=discrepancy_gate("P40"); self.assertFalse(g["ready"]); self.assertEqual(g["blocking_discrepancy_ids"],["P40-D001"])

if __name__=="__main__": unittest.main()
