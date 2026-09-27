import importlib.util, json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.isolation import run_runner_for_test
spec=importlib.util.spec_from_file_location("p42_api",ROOT/"papers/P42/tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

class P42Phase1Tests(unittest.TestCase):
    def test_pitch_balance(self):
        s=api.phase1_continuum_summary()["table1_pitch_balance"]
        self.assertAlmostEqual(s["calculated_L2_mm"],1850.9454545454546,places=9)
        self.assertLess(abs(s["relative_difference_percent"]),0.01)

    def test_equation42_linearity(self):
        s=api.phase1_continuum_summary()["equation42_continuum"]["curve"]
        self.assertAlmostEqual(s[-1]["M_cont_total_kNm"],9.379154574156709,places=9)
        self.assertAlmostEqual(s[3]["M_cont_total_kNm"]/0.06,s[-1]["M_cont_total_kNm"]/0.10,places=9)

    def test_equation43_sum(self):
        self.assertAlmostEqual(api.equation43_total_moment_kNm(2.0,3.0,4.0,5.0),14.0,places=12)

    def test_contact_properties(self):
        c=api.contact_properties()
        self.assertAlmostEqual(c["coulomb_friction_coefficient"],0.12)
        self.assertAlmostEqual(c["absolute_elastic_slip_mm"],0.005)
        self.assertAlmostEqual(c["contact_stiffness_N_per_mm3"],2000.0)

    def test_runner(self):
        p,SB=run_runner_for_test(self,ROOT,"papers/P42/run_calculation.py")
        self.assertEqual(p.returncode,0,p.stderr)
        v=json.loads((SB/"papers/P42/results/engiproof_verification.json").read_text())
        self.assertEqual(v["evidence_status"],"COMPARED")
        self.assertFalse(v["checks"]["fp_ruc_reproduced"])

if __name__=="__main__": unittest.main()
