import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.core import discrepancy_snapshot, invoke_tool, load_manifest, validate_study_manifest

class P29EngiProofTests(unittest.TestCase):
    def test_runner_preserves_surface(self):
        p=subprocess.run([sys.executable,str(ROOT/"papers/P29/run_calculation.py")],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        v=json.loads((ROOT/"papers/P29/results/engiproof_verification.json").read_text(encoding="utf-8"))
        self.assertEqual(v["status"],"CONDITIONAL")
        self.assertEqual(v["surface_points"],7442)
        self.assertLess(v["max_surface_relative_difference"],1e-10)
    def test_independent_crosscheck(self):
        s=invoke_tool("P29","positive_frequency_integral",{"mass_ratio":0.853,"gamma":0.2,"zeta_t":0.1})
        q=invoke_tool("P29","direct_transfer_quadrature",{"mass_ratio":0.853,"gamma":0.2,"zeta_t":0.1})
        self.assertAlmostEqual(s["result"],0.008639625177147149,places=12)
        self.assertLess(abs(q["result"]/s["result"]-1.0),1e-10)
        tw=invoke_tool("P29","two_sided_integral",{"mass_ratio":0.853,"gamma":0.2,"zeta_t":0.1})
        self.assertAlmostEqual(tw["result"],2*s["result"],places=14)
    def test_factor_two_discrepancy_is_open(self):
        m=load_manifest("P29")
        self.assertEqual(validate_study_manifest(m),[])
        self.assertEqual(m["evidence_status"],"CONDITIONAL")
        self.assertEqual(m["qualification"],"NOT_GRANTED")
        d=discrepancy_snapshot("P29")["discrepancies"]
        self.assertTrue(any(x["id"]=="P29-D001" and x["status"]=="OPEN" for x in d))
        self.assertFalse((ROOT/"papers/P29/source.pdf").exists())
if __name__=="__main__": unittest.main()
