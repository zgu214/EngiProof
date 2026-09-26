import importlib.util, json, math, subprocess, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("p42_api_phase3",ROOT/"papers/P42/tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

class P42Phase3Tests(unittest.TestCase):
    def test_axisymmetric_closure(self):
        s=api.phase3_axisymmetric_and_moment_summary()
        cases=s["axisymmetric_equations_24_26"]["cases"]
        for c in cases:
            self.assertLess(abs(c["force_residual_N"]),1e-6)
            self.assertLess(abs(c["torque_residual_Nm"]),1e-6)

    def test_axisymmetric_6000_scaling_by_linearity(self):
        # 3000-kN result doubled should match the source figure scale at 6000 kN.
        s=api.phase3_axisymmetric_and_moment_summary()
        c=next(x for x in s["axisymmetric_equations_24_26"]["cases"] if x["Fz_kN"]==3000)
        self.assertGreater(c["sigma_inner_MPa"]*2.0,950.0)
        self.assertLess(c["sigma_inner_MPa"]*2.0,1000.0)
        self.assertGreater(c["twist_rate_deg_per_m"]*2.0,0.18)
        self.assertLess(c["twist_rate_deg_per_m"]*2.0,0.19)

    def test_inner_contact_exceeds_outer_contact(self):
        s=api.phase3_axisymmetric_and_moment_summary()
        c=next(x for x in s["axisymmetric_equations_24_26"]["cases"] if x["Fz_kN"]==500)
        self.assertGreater(c["literal_contact_inner"]["p_i_MPa"],c["literal_contact_outer"]["p_i_MPa"])

    def test_figure16_probe_is_not_promoted(self):
        s=api.phase3_axisymmetric_and_moment_summary()
        p=s["equation41_figure16_probe"]
        self.assertEqual(p["status"],"NOT_REPRODUCED_SOURCE_IMPLEMENTATION_GAP")
        self.assertTrue(p["exceeds_source_plot_axis"])

    def test_manifest_records_provenance_gap(self):
        m=json.loads((ROOT/"engiproof/studies/P42/study.json").read_text(encoding="utf-8"))
        d=next(x for x in m["discrepancies"] if x["id"]=="P42-D002")
        self.assertEqual(d["classification_hint"],"SOURCE_IMPLEMENTATION_PROVENANCE_GAP")
        self.assertEqual(d["status"],"OPEN")

    def test_runner_writes_phase3_artifacts(self):
        p=subprocess.run([sys.executable,str(ROOT/"papers/P42/run_calculation.py")],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue((ROOT/"papers/P42/results/phase3_axisymmetric_moment_summary.json").is_file())
        self.assertTrue((ROOT/"papers/P42/results/phase3_figure16_literal_probe.csv").is_file())

if __name__=="__main__": unittest.main()
