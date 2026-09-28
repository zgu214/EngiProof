import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from engiproof.core import invoke_tool, load_manifest, validate_study_manifest
from engiproof.isolation import run_runner_for_test

spec = importlib.util.spec_from_file_location("p45_api", ROOT / "papers/P45/tool_api.py")
api = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(api)
M = api.M


class P45Phase1Tests(unittest.TestCase):
    # ----------------------------------------------------------- manifest
    def test_manifest_contract(self):
        m = load_manifest("P45")
        self.assertEqual(validate_study_manifest(m), [])
        self.assertEqual(m["evidence_status"], "CONDITIONAL")
        self.assertEqual(m["qualification"], "NOT_GRANTED")
        self.assertEqual(m["source"]["sha256"], "c10b4938dd3c4de6c027f8494386b43a46fc2c3cb011a69de94612dc52686a0d")
        self.assertEqual({d["id"] for d in m["discrepancies"]}, {f"P45-D00{i}" for i in range(1, 7)})
        self.assertTrue(all(d["status"] == "OPEN" for d in m["discrepancies"]))
        blocked = next(c for c in m["comparisons"] if c["id"] == "P45-C009")
        self.assertEqual(blocked["status"], "BLOCKED")

    def test_no_solver_new_evidence(self):
        self.assertFalse(any(t["evidence_class"] == "SOLVER_NEW" for t in load_manifest("P45")["tools"]))

    # ----------------------------------------------------------- tables
    def test_table2_geometry_reproduced(self):
        s = api.table2_geometry_check()
        self.assertTrue(s["all_within_print_rounding"])
        self.assertAlmostEqual(s["rows"][2]["riser_length_computed_m"], 920.496, places=9)

    def test_imperial_origin(self):
        s = api.imperial_origin_check()
        self.assertLess(s["max_relative_deviation"], 0.005)
        kips = [r["kips"] for r in s["table1_tension_in_kips"]]
        self.assertAlmostEqual(kips[0], 120.048, places=3)
        self.assertAlmostEqual(kips[2], 2901.1594, places=4)

    def test_D001_buoyancy_inconsistency_preserved(self):
        s = api.table2_buoyancy_consistency()
        self.assertEqual((s["added_weight_in_air_dN"], s["change_in_water_weight_dN"]), (350, 338))
        self.assertAlmostEqual(s["implied_added_buoyancy_dN"], 12.0, places=9)
        self.assertLess(s["expected_change_in_water_weight_dN"], -1500)

    def test_D002_tension_magnitude_preserved(self):
        rows = api.table1_tension_plausibility()["rows"]
        self.assertEqual(rows[2]["tension_printed"], "1.290.500 dN")
        self.assertAlmostEqual(rows[0]["head_axial_stress_MPa_riser_pipe"], 27.3762, places=4)
        self.assertAlmostEqual(rows[3]["head_axial_stress_MPa_riser_pipe"], 1140.6751, places=4)

    def test_D003_unit_not_asserted(self):
        s = api.example1200_weight_and_tension_units()
        self.assertAlmostEqual(s["effective_weight_MN_without_floats"], 3.46225918, places=8)
        self.assertAlmostEqual(api.example1200_head_tension_printed(0.0), 298.0)
        units = {r["unit"]: r for r in s["candidate_units"]}
        self.assertLess(units["kN"]["mean_over_weight_with_ideal_floats"], 0.2)
        self.assertGreater(units["tonne-force"]["mean_over_weight_with_ideal_floats"], 1.0)

    # ----------------------------------------------------------- 1200 m inputs
    def test_D004_head_motion_uses_text_period(self):
        self.assertAlmostEqual(api.example1200_head_displacement_m(9.0 / 4), 7.70, places=12)
        self.assertAlmostEqual(api.example1200_head_displacement_m(9.0), 0.0, places=12)

    def test_current_profiles(self):
        self.assertAlmostEqual(api.example1200_current_speed_m_per_s(0), 0.25)
        self.assertAlmostEqual(api.example1200_current_speed_m_per_s(400), 0.50)
        self.assertAlmostEqual(api.example1200_current_speed_m_per_s(900), 0.25)
        self.assertAlmostEqual(api.cases_current_speed_m_per_s(152.40 - 9.144, 152.40), 0.256)

    def test_airy_infinite_depth_valid(self):
        s = api.airy_depth_regime()
        self.assertAlmostEqual(s["deep_water_wavelength_m"], 126.42292264, places=6)
        self.assertLess(s["infinite_depth_error_max"], 1e-6)

    # ----------------------------------------------------------- figures
    def test_D005_head_envelopes_peak_to_peak(self):
        s = api.head_envelope_interpretation()
        self.assertTrue(s["all_peak_to_peak"])
        self.assertFalse(s["any_single_amplitude"])
        self.assertEqual(len(s["rows"]), 6)
        for r in s["rows"]:
            self.assertLess(abs(r["centre_minus_offset_m"]), 0.25)

    def test_D006_figure11_claim(self):
        s = api.figure11_linear_vs_nonlinear()["attribution_as_recorded"]
        self.assertAlmostEqual(s["peak_abs_underestimate_relative_to_nonlinear_percent"], 13.375796, places=5)
        self.assertAlmostEqual(s["peak_abs_nonlinear_excess_relative_to_linear_percent"], 15.441176, places=5)
        self.assertAlmostEqual(s["min_envelope_linear_vs_nonlinear_percent"], -28.503185, places=5)

    # ----------------------------------------------------------- formulations
    def test_appendix1_published_branches(self):
        z = api.appendix1_stiffness_coefficients(0.0, 1.0, 1.0)
        self.assertEqual((z["k1"], z["k2"], z["k3"]), (4.0, 2.0, 6.0))
        c = api.appendix1_stiffness_coefficients(-math.pi ** 2, 1.0, 1.0)
        self.assertAlmostEqual(c["k1"], c["k2"], places=12)
        t = api.appendix1_stiffness_coefficients(3.0, 1.0, 1.0)
        self.assertAlmostEqual(t["k3"], t["k1"] + t["k2"], places=12)

    def test_appendix1_independent_checks(self):
        s = api.appendix1_independent_checks()
        self.assertLess(s["k3_equals_k1_plus_k2_max_relative_residual"], 1e-10)
        for c in s["continuity_at_zero_axial_force"]:
            for r in c["convergence_ratios"]:
                self.assertAlmostEqual(r, 4.0, delta=0.01)
        for f in s["independent_fe_comparison"]:
            self.assertLess(f["max_relative_difference"], 1e-6)
        self.assertEqual((s["rigid_body_nullity_of_K"], s["rigid_body_nullity_if_k3_perturbed_1pct"]), (6, 4))

    def test_eq7(self):
        a = api.eq7_theta_coefficients(1.0, 1.0 / 6.0, 0.5, 1.0)
        self.assertAlmostEqual(a["a4"], 6.0)
        s = api.eq7_independent_checks()
        self.assertAlmostEqual(s["theta_1_critical_dt_over_T"], 0.5513, delta=1e-3)
        self.assertTrue(s["theta_1.37_unconditionally_stable_on_grid"])
        self.assertLess(s["free_vibration_one_period_error_theta_1.4_dt_T_over_200"], 1e-4)

    def test_appendix2(self):
        s = api.appendix2_independent_checks()
        for k in ("C1_plus_C3", "hermite_translation_partition", "hermite_shape_match", "Bi_equals_transverse_projector_max_deviation"):
            self.assertLess(s[k], 1e-12)

    # ----------------------------------------------------------- runtime
    def test_tools_callable_with_evidence(self):
        out = invoke_tool("P45", "example1200_head_tension_printed", {"t_s": 0.0})
        self.assertEqual(out["evidence_class"], "PUBLISHED")
        self.assertIn("no unit", out["evidence_boundary"].lower())

    def test_runner(self):
        p, SB = run_runner_for_test(self, ROOT, "papers/P45/run_calculation.py")
        self.assertEqual(p.returncode, 0, p.stderr)
        v = json.loads((SB / "papers/P45/results/engiproof_verification.json").read_text(encoding="utf-8"))
        self.assertEqual(v["status"], "CONDITIONAL")
        self.assertFalse(v["checks"]["nonlinear_dynamic_response_reproduced"])
        self.assertTrue(all(val for k, val in v["checks"].items() if k != "nonlinear_dynamic_response_reproduced"))


if __name__ == "__main__":
    unittest.main()
