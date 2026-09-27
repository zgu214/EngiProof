import csv
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.isolation import run_runner_for_test

def _load(rel,name):
    p=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

api=_load("papers/P41/tool_api.py","p41_api_test")

class P41EngiProofTests(unittest.TestCase):
    def test_geometry_reproduces_table2_area_and_EA(self):
        s=api.independent_table1_to_table2_summary()
        c=s["comparisons"]
        self.assertLess(abs(c["A_inner_relative_percent"]),0.01)
        self.assertLess(abs(c["A_outer_relative_percent"]),0.01)
        self.assertLess(abs(c["EA_inner_relative_percent"]),0.02)
        self.assertLess(abs(c["EA_outer_relative_percent"]),0.02)

    def test_equation8_force_identity(self):
        s=api.independent_table1_to_table2_summary()
        self.assertAlmostEqual(s["calculated"]["deltaS_total_N_per_m"],471.0,places=10)

    def test_outer_force_rounding_agreement(self):
        s=api.independent_table1_to_table2_summary()
        self.assertLessEqual(abs(s["comparisons"]["deltaS_outer_minus_published_N_per_m"]),0.5)

    def test_inner_force_is_visually_confirmed_published_mismatch(self):
        s=api.independent_table1_to_table2_summary()
        self.assertEqual(s["source_review"]["table2_inner_deltaS"],"VISUALLY_CONFIRMED_153_N_PER_M")
        manifest=json.loads((ROOT/"engiproof/studies/P41/study.json").read_text(encoding="utf-8"))
        d=manifest["discrepancies"][0]
        self.assertEqual(d["classification_hint"],"PUBLISHED_REFERENCE_MISMATCH")
        self.assertIn("source-confirmed",d["engineering_interpretation"].lower())

    def test_published_reference_mismatch_blocks_promotion(self):
        sys.path.insert(0,str(ROOT/"src"))
        from engiproof.discrepancy import discrepancy_gate
        gate=discrepancy_gate("P41")
        self.assertFalse(gate["ready"])
        self.assertEqual(gate["blocking_discrepancy_ids"],["P41-D001","P41-D002"])
        self.assertEqual(gate["assessments"][0]["category"],"PUBLISHED_REFERENCE_MISMATCH")

    def test_runner(self):
        p,SB=run_runner_for_test(self,ROOT,"papers/P41/run_calculation.py")
        self.assertEqual(p.returncode,0,p.stderr)
        out=json.loads((SB/"papers/P41/results/engiproof_verification.json").read_text(encoding="utf-8"))
        self.assertEqual(out["status"],"CONDITIONAL")
        self.assertTrue(out["checks"]["eq8_total_matches_fS"])

if __name__=="__main__": unittest.main()
