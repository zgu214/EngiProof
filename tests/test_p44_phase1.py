import importlib.util
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("p44_api",ROOT/"papers/P44/tool_api.py")
api=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(api)


class P44Phase1Tests(unittest.TestCase):
    def test_table1_geometry(self):
        s=api.phase1_contact_validation_summary()["table1_independent_geometry_check"]
        self.assertAlmostEqual(s["computed_cross_area_ft2"],0.0366291377451424,places=12)
        self.assertAlmostEqual(s["computed_I_ft4"],0.0006881345680941783,places=15)
        self.assertLess(abs(s["I_relative_difference_percent"]),0.03)

    def test_equation1_printed_arithmetic(self):
        s=api.phase1_contact_validation_summary()["equation1_validation"]
        self.assertAlmostEqual(s["printed_arithmetic_reproduction_lb"],429.09867,places=5)
        self.assertAlmostEqual(s["published_equilibrium_force_lb"],429.098,places=3)

    def test_equation1_exact_matches_FEM(self):
        s=api.phase1_contact_validation_summary()["equation1_validation"]
        self.assertAlmostEqual(s["exact_sine60_independent_lb"],429.1112574481704,places=9)
        self.assertLess(abs(s["exact_vs_FEM_relative_difference_percent"]),0.001)

    def test_time_slice(self):
        s=api.phase1_contact_validation_summary()["time_discretization_check"]
        self.assertAlmostEqual(s["computed_spacing_s"],0.58,places=12)

    def test_penalty_scale(self):
        s=api.phase1_contact_validation_summary()["contact_penalty_diagnostic"]
        self.assertAlmostEqual(s["elastic_penetration_in_at_reference_force"],0.00514932,places=8)

    def test_source_time_mismatch_preserved(self):
        s=api.phase1_contact_validation_summary()["P44_D001_probe"]
        self.assertEqual(s["paragraph_times_s"],[4.06,2.32])
        self.assertEqual(s["figure7_caption_time_s"],0.58)
        self.assertEqual(s["figure8_caption_time_s"],1.74)

    def test_runner(self):
        p=subprocess.run([sys.executable,str(ROOT/"papers/P44/run_calculation.py")],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue((ROOT/"papers/P44/results/phase1_contact_validation_summary.json").is_file())

if __name__=="__main__":
    unittest.main()
