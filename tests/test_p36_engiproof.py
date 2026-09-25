import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.core import invoke_tool, load_manifest, validate_study_manifest

class P36EngiProofTests(unittest.TestCase):
    def test_runner_preserves_comparison(self):
        p=subprocess.run([sys.executable,str(ROOT/"papers/P36/run_calculation.py")],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        v=json.loads((ROOT/"papers/P36/results/engiproof_verification.json").read_text(encoding="utf-8"))
        self.assertEqual(v["status"],"COMPARED")
        self.assertEqual(v["comparison"]["reference_markers"],27)
        self.assertAlmostEqual(v["comparison"]["mean_absolute_percent"],1.7485966966417408,places=12)
        self.assertAlmostEqual(v["comparison"]["maximum_absolute_percent"],3.5857415531854886,places=12)
    def test_equation8(self):
        out=invoke_tool("P36","equation8_ratio",{"diameter_ratio":0.6})
        self.assertAlmostEqual(out["result"],1.669601242879337,places=12)
        self.assertEqual(out["evidence_class"],"PUBLISHED")
    def test_graphical_reference_boundary(self):
        m=load_manifest("P36")
        self.assertEqual(validate_study_manifest(m),[])
        self.assertEqual(m["evidence_status"],"COMPARED")
        self.assertEqual(m["qualification"],"NOT_GRANTED")
        self.assertTrue(any("graphical references" in x for x in m["limitations"]))
        self.assertFalse((ROOT/"papers/P36/source.pdf").exists())
if __name__=="__main__": unittest.main()
