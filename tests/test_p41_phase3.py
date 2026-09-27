import importlib.util, json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.isolation import run_runner_for_test
spec=importlib.util.spec_from_file_location("p41_api_phase3",ROOT/"papers/P41/tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

class P41Phase3Tests(unittest.TestCase):
    def test_outer_bending_stiffness_exceeds_inner(self):
        s=api.phase3_global_buckling_summary()
        b=s["independent_bending_stiffness"]
        self.assertGreater(b["EI_outer_Nm2"],b["EI_inner_Nm2"])
        self.assertAlmostEqual(b["outer_to_inner_ratio"],3.396588258187736,places=12)

    def test_equation14_scaling(self):
        self.assertAlmostEqual(api.equation14_design_moment(100.0,1.0,0.8),80.0,places=12)

    def test_figure10_unit_mismatch_is_recorded(self):
        s=api.phase3_global_buckling_summary()
        f=s["published_source_observations"]["figure10"]
        self.assertEqual(f["axis_unit"],"kNm")
        self.assertEqual(f["source_text_inner_unit"],"MNm")
        m=json.loads((ROOT/"engiproof/studies/P41/study.json").read_text(encoding="utf-8"))
        d=next(x for x in m["discrepancies"] if x["id"]=="P41-D002")
        self.assertEqual(d["metrics"]["literal_unit_scale_factor"],1000)

    def test_source_global_buckle_observations(self):
        s=api.phase3_global_buckling_summary()
        obs=s["published_source_observations"]
        self.assertTrue(any("1500" in x for x in obs["figure8"]["observations"]))
        self.assertTrue(any("3500" in x for x in obs["figure8"]["observations"]))
        self.assertTrue(any("feed-in" in x for x in obs["figure9"]["observations"]))

    def test_runner_writes_phase3_artifact(self):
        p,SB=run_runner_for_test(self,ROOT,"papers/P41/run_calculation.py")
        self.assertEqual(p.returncode,0,p.stderr)
        q=SB/"papers/P41/results/phase3_global_buckling_summary.json"
        self.assertTrue(q.is_file())

if __name__=="__main__": unittest.main()
