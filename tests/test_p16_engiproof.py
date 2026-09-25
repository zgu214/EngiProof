import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.core import evidence_snapshot, invoke_tool, load_manifest, validate_study_manifest

class P16EngiProofTests(unittest.TestCase):
    def test_runner_preserves_comparison(self):
        p=subprocess.run([sys.executable,str(ROOT/"papers/P16/run_calculation.py")],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        v=json.loads((ROOT/"papers/P16/results/engiproof_verification.json").read_text(encoding="utf-8"))
        self.assertEqual(v["status"],"COMPARED")
        self.assertEqual(v["reference_curve_points"],261)
        self.assertLess(v["comparison"]["maximum_absolute_discrepancy_mm"],1.0)
    def test_table2_arithmetic(self):
        out=invoke_tool("P16","table2_cumulative_displacement_mm",{"cycle":6})
        self.assertAlmostEqual(out["result"],406.4,places=10)
        d=invoke_tool("P16","figure5_table2_discrepancy_mm",{"cycle":6})
        self.assertAlmostEqual(d["result"],0.9172453015464725,places=10)
    def test_evidence_boundary(self):
        m=load_manifest("P16")
        self.assertEqual(validate_study_manifest(m),[])
        self.assertEqual(m["evidence_status"],"COMPARED")
        self.assertEqual(m["qualification"],"NOT_GRANTED")
        self.assertTrue(any("No independent pipeline-walking solver" in x for x in m["limitations"]))
        self.assertFalse((ROOT/"papers/P16/source.pdf").exists())
        self.assertIn("D-P16",{n["id"] for n in evidence_snapshot("P16")["graph"]["nodes"]})
if __name__=="__main__": unittest.main()
