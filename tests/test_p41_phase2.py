import importlib.util, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("p41_api_phase2",ROOT/"papers/P41/tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

class P41Phase2Tests(unittest.TestCase):
    def test_table2_mismatch_is_visually_confirmed(self):
        s=api.independent_table1_to_table2_summary()
        self.assertEqual(s["source_review"]["table2_inner_deltaS"],"VISUALLY_CONFIRMED_153_N_PER_M")
        self.assertEqual(153+312,465)
        self.assertNotEqual(465,471)

    def test_eq9_threshold_and_table3_classification(self):
        s=api.table3_bonding_summary()
        self.assertAlmostEqual(s["equation9_required_internal_friction_N_per_m"],158.77672746638265,places=9)
        self.assertEqual(
            [c["predicted_type"] for c in s["cases"]],
            ["NO_FRICTION","PARTIAL_BONDING","FULL_BONDING","FULL_BONDING"]
        )
        self.assertTrue(all(c["classification_matches"] for c in s["cases"]))

    def test_dry_weight_friction_reproduces_358_rounding(self):
        s=api.table3_bonding_summary()
        self.assertAlmostEqual(s["dry_weight_model"]["calculated_fI_N_per_m"],358.5,places=12)
        self.assertLess(abs(s["dry_weight_model"]["calculated_fI_N_per_m"]-358.0),1.0)

    def test_eq10_inverse_is_labeled_conditional(self):
        s=api.table3_bonding_summary()
        self.assertEqual(s["equation10"]["status"],"CONDITIONAL_INPUT_INCOMPLETE")
        self.assertGreater(s["equation10"]["inferred_S0_total_N_from_published_delta"],3.0e6)

    def test_manifest_reclassifies_discrepancy(self):
        m=json.loads((ROOT/"engiproof/studies/P41/study.json").read_text(encoding="utf-8"))
        d=m["discrepancies"][0]
        self.assertEqual(d["classification_hint"],"PUBLISHED_REFERENCE_MISMATCH")
        self.assertEqual(d["metrics"]["published_component_sum_N_per_m"],465)

if __name__=="__main__":
    unittest.main()
