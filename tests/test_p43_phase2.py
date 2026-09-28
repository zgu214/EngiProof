import importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("p43_api2",ROOT/"papers/P43/tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)
class P43Phase2Tests(unittest.TestCase):
    def test_full_matrix_count(self):
        s=api.phase2_full_matrix_summary(); self.assertEqual(s["table1_full_matrix"]["row_count"],35); self.assertEqual(s["table1_full_matrix"]["scalar_comparisons"],175)
    def test_full_matrix_ordinary_accuracy(self):
        s=api.phase2_full_matrix_summary(); self.assertLess(s["table1_full_matrix"]["max_abs_FE_difference_excluding_source_mismatches"],0.00051)
    def test_full_table2_accuracy(self):
        s=api.phase2_full_matrix_summary(); self.assertLess(s["table1_full_matrix"]["max_abs_Table2_error_difference_percentage_points_using_independent_FE"],0.011)
    def test_source_anomaly_preserved(self):
        s=api.phase2_full_matrix_summary()["P43_D001_probe"]; self.assertEqual(s["source_cell"]["printed_lambda"],13.221); self.assertGreater(s["independent_FE_lambda"],18.0); self.assertGreater(s["eq10_lambda"],18.0); self.assertEqual(s["published_table2_error_percent"],0.0)
    def test_second_source_anomaly_preserved(self):
        s=api.phase2_full_matrix_summary()["P43_D002_probe"]; self.assertEqual(s["source_cell"]["printed_lambda"],6.554); self.assertAlmostEqual(s["independent_FE_lambda"],6.654,delta=0.001); self.assertEqual(s["published_table2_error_percent"],1.39)
    def test_figures4_5_matrix(self):
        s=api.phase2_full_matrix_summary()["figures4_5_parameter_families"]; self.assertEqual(len(s["rows"]),35); self.assertFalse(s["curve_digitized"])
    def test_figure6_three_modes(self):
        s=api.phase2_full_matrix_summary()["figure6_first_three_modes"]; self.assertEqual(len(s["summary"]),3); self.assertFalse(s["curve_digitized"])
    def test_manifest_has_P43_D001(self):
        m=json.loads((ROOT/"engiproof/studies/P43/study.json").read_text(encoding="utf-8")); d=next(x for x in m["discrepancies"] if x["id"]=="P43-D001"); self.assertEqual(d["classification_hint"],"PUBLISHED_REFERENCE_MISMATCH"); self.assertEqual(d["status"],"OPEN")
if __name__=="__main__": unittest.main()
