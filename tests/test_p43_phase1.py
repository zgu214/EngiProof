import importlib.util
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("p43_api", ROOT / "papers/P43/tool_api.py")
api = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(api)


class P43Phase1Tests(unittest.TestCase):
    def test_dimensionless_example_parameters(self):
        case = json.loads((ROOT / "papers/P43/inputs/example_case.json").read_text(encoding="utf-8"))
        d = api.dimensionless_parameters(
            weight_lb_per_ft=case["weight_lb_per_ft"],
            outer_area_ft2=case["outer_area_ft2"],
            inner_area_ft2=case["inner_area_ft2"],
            sea_water_weight_density_lb_per_ft3=case["sea_water_weight_density_lb_per_ft3"],
            mud_weight_density_lb_per_ft3=case["mud_weight_density_lb_per_ft3"],
            length_ft=case["length_ft"],
            youngs_modulus_psi=case["youngs_modulus_psi"],
            second_moment_in4=case["second_moment_in4"],
            bottom_pull_lb=case["bottom_pull_lb"],
        )
        self.assertAlmostEqual(d["alpha"], 50.62539449775256, places=9)
        self.assertAlmostEqual(d["beta"], 99.71411265899455, places=9)

    def test_table1_alpha50_beta100(self):
        published = [6.029, 8.969, 11.735, 14.536, 17.401]
        calc = api.independent_eigenvalues(50.0, 100.0, modes=5, elements=100)
        for p, c in zip(published, calc):
            self.assertLess(abs(c - p), 0.001)

    def test_classical_alpha_beta_zero(self):
        calc = api.independent_eigenvalues(0.0, 0.0, modes=5, elements=80)
        for i, c in enumerate(calc, 1):
            self.assertLess(abs(c - i * math.pi), 5e-5)

    def test_eq10_table2_errors(self):
        published = [6.029, 8.969, 11.735, 14.536, 17.401]
        published_error = [0.19, 0.09, 0.04, 0.02, 0.01]
        for i, (p, e) in enumerate(zip(published, published_error), 1):
            a = api.equation10_lambda(i, 50.0, 100.0)
            err = (a - p) / p * 100.0
            self.assertAlmostEqual(err, e, delta=0.006)

    def test_worked_example_periods(self):
        s = api.phase1_eigen_benchmark_summary()["worked_example"]
        self.assertAlmostEqual(s["omega_from_published_lambda_rad_per_s"], 0.815, delta=0.001)
        self.assertAlmostEqual(s["period_from_published_lambda_s"], 7.71, delta=0.01)
        self.assertAlmostEqual(s["eq10_period_s"], 7.68, delta=0.01)

    def test_figure6_inflection(self):
        s = api.phase1_eigen_benchmark_summary()["figure6_independent_mode_shape_check"]
        self.assertAlmostEqual(s["independent_lambda1"], 6.816, delta=0.001)
        self.assertAlmostEqual(s["distance_below_top"], 0.1, delta=0.02)

    def test_runner(self):
        p = subprocess.run(
            [sys.executable, str(ROOT / "papers/P43/run_calculation.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue((ROOT / "papers/P43/results/phase1_eigen_benchmark_summary.json").is_file())


if __name__ == "__main__":
    unittest.main()
