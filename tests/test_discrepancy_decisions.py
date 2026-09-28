import json, tempfile, unittest
from pathlib import Path
from engiproof.discrepancy import discrepancy_gate, discrepancy_decision_summary, record_discrepancy_decision

class DiscrepancyDecisionWorkflowTests(unittest.TestCase):
    def _root(self, td):
        root=Path(td); (root/"engiproof/studies/PX").mkdir(parents=True)
        (root/"engiproof/studies/PX/study.json").write_text(json.dumps({"paper_id":"PX","evidence_status":"CONDITIONAL","qualification":"NOT_GRANTED","discrepancies":[{"id":"PX-D001","target":"published ratio","status":"OPEN","observation":"calculation differs from published table","engineering_interpretation":"retain without tuning","classification_hint":"PUBLISHED_REFERENCE_MISMATCH","metrics":{"reference_value":0.66,"reproduced_value":0.705,"reference_decimals":2},"automation":{"independent_support":"CORROBORATES_REPRODUCTION"}}]}),encoding="utf-8"); return root
    def test_open_blocks(self):
        with tempfile.TemporaryDirectory() as td: self.assertFalse(discrepancy_gate("PX",root=self._root(td))["ready"])
    def test_unblocking_requires_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            with self.assertRaises(ValueError): record_discrepancy_decision("PX","PX-D001","BOUNDED","Reviewed and bounded discrepancy","Reviewer",[],root=root)
    def test_bounded_unblocks_without_qualification(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); out=record_discrepancy_decision("PX","PX-D001","BOUNDED","Independent check confirms the reproduced result and the residual is explicitly bounded for this evidence use.","Reviewer",["analysis:independent-check","source:table-review"],root=root)
            self.assertEqual(out["decision"]["qualification_effect"],"NONE"); self.assertTrue(discrepancy_gate("PX",root=root)["ready"]); self.assertEqual(discrepancy_decision_summary("PX",root=root)["latest_by_discrepancy"]["PX-D001"]["disposition"],"BOUNDED")
    def test_deferred_still_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); record_discrepancy_decision("PX","PX-D001","DEFERRED","Decision deferred pending additional source provenance review.","Reviewer",[],root=root); self.assertFalse(discrepancy_gate("PX",root=root)["ready"])
if __name__=="__main__": unittest.main()
