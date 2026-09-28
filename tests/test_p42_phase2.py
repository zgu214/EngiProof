import importlib.util, json, math, subprocess, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.isolation import run_runner_for_test
spec=importlib.util.spec_from_file_location("p42_api_phase2",ROOT/"papers/P42/tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

class P42Phase2Tests(unittest.TestCase):
    def test_lay_angles_from_geometry(self):
        s=api.phase2_analytical_stress_summary()["nominal_geometry"]
        self.assertAlmostEqual(s["inner_lay_angle_deg"],24.909154258031112,places=9)
        self.assertAlmostEqual(s["outer_lay_angle_deg"],24.940498991073344,places=9)

    def test_fig20_transverse_amplitude_kappa_0p06(self):
        a=api.phase2_analytical_stress_summary()["analytical_amplitudes_at_kappa_0p06"]
        self.assertAlmostEqual(a["inner_transverse_MPa"],84.0946241557556,places=9)
        self.assertAlmostEqual(a["outer_transverse_MPa"],84.10310644651963,places=9)

    def test_fig22_normal_amplitude_kappa_0p06(self):
        a=api.phase2_analytical_stress_summary()["analytical_amplitudes_at_kappa_0p06"]
        self.assertAlmostEqual(a["inner_normal_MPa"],21.31548104332173,places=9)
        self.assertAlmostEqual(a["outer_normal_MPa"],21.293816001267295,places=9)

    def test_analytical_curves_do_not_depend_on_Fz(self):
        s=api.phase2_analytical_stress_summary()["figure21_23_model_form_check"]
        self.assertEqual(s["analytical_Fz_dependence"],"NONE_IN_EQS_36_39")
        self.assertEqual(s["published_FP_RUC_Fz_dependence"],"PRESENT")

    def test_eq34_eq35_continuity_at_transition(self):
        args=dict(mu_i=0.12,p_i_MPa=2.0,mu_o=0.12,p_o_MPa=1.5,r_mm=132.0,t_mm=5.0,alpha_deg=25.0)
        ns=35.0
        slip=api.equation34_slip_stress_MPa(ns,**args)
        stick=api.equation35_stick_stress_MPa(ns,ns,210000.0,132.0,25.0,0.06,0.12,2.0,0.12,1.5,5.0)
        self.assertAlmostEqual(slip,stick,places=10)

    def test_eq32_minimum_at_90_degrees(self):
        vals=[]
        for nu in (30.0,45.0,60.0,90.0):
            vals.append(api.equation32_critical_curvature_per_m(nu,0.12,2.0,0.12,1.5,210000.0,5.0,25.0))
        self.assertEqual(min(vals),vals[-1])

    def test_manifest_records_model_form_difference(self):
        m=json.loads((ROOT/"engiproof/studies/P42/study.json").read_text(encoding="utf-8"))
        d=next(x for x in m["discrepancies"] if x["id"]=="P42-D001")
        self.assertEqual(d["classification_hint"],"MODEL_FORM_KINEMATICS_DIFFERENCE")
        self.assertEqual(d["status"],"OBSERVED")

    def test_runner_writes_phase2_artifacts(self):
        p,SB=run_runner_for_test(self,ROOT,"papers/P42/run_calculation.py")
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue((SB/"papers/P42/results/phase2_analytical_stress_curves.csv").is_file())
        v=json.loads((SB/"papers/P42/results/engiproof_verification.json").read_text())
        self.assertTrue(v["checks"]["phase2_analytical_curves_regenerated"])

if __name__=="__main__": unittest.main()
