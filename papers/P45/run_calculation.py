"""P45 Phase 1 runner - Safai (1983), Nonlinear dynamic analysis of deep water risers.

Writes the Phase 1 evidence summary and verification record. Output bytes are
deterministic (LF line endings, sorted structure) so a recomputation on any
platform differs only by floating-point noise from linear algebra.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("p45_api", HERE / "tool_api.py")
api = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(api)


def write(name: str, obj: dict) -> None:
    with (RESULTS / name).open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


summary = api.phase1_summary()
write("phase1_summary.json", summary)

a1, e7, a2 = summary["appendix1_checks"], summary["eq7_checks"], summary["appendix2_checks"]
verification = {
    "schema_version": "engiproof.p45.verification/1.0",
    "paper_id": "P45",
    "status": "CONDITIONAL",
    "checks": {
        "table2_riser_length_and_offset_reproduced": summary["table2_geometry_check"]["all_within_print_rounding"],
        "table_values_are_round_imperial_renderings": summary["imperial_origin_check"]["max_relative_deviation"] < 0.005,
        "appendix1_k3_equals_k1_plus_k2": a1["k3_equals_k1_plus_k2_max_relative_residual"] < 1e-10,
        "appendix1_continuous_at_zero_axial_force": all(abs(r - 4.0) < 0.01 for c in a1["continuity_at_zero_axial_force"] for r in c["convergence_ratios"]),
        "appendix1_matches_independent_fe": all(f["max_relative_difference"] < 1e-6 for f in a1["independent_fe_comparison"]),
        "appendix1_K_has_six_rigid_body_modes": a1["rigid_body_nullity_of_K"] == 6 and a1["rigid_body_nullity_if_k3_perturbed_1pct"] == 4,
        "eq7_reduces_to_wilson_linear_acceleration": e7["linear_acceleration_reduction_max_deviation"] < 1e-12,
        "eq7_theta_1_critical_step_0p551": abs(e7["theta_1_critical_dt_over_T"] - 0.5513) < 1e-3,
        "appendix2_factors_are_hermite_interpolation": max(a2["C1_plus_C3"], a2["hermite_translation_partition"], a2["hermite_shape_match"]) < 1e-12,
        "infinite_depth_airy_valid_all_depths": summary["airy_depth_regime"]["infinite_depth_error_max"] < 1e-6,
        "P45_D001_preserved": summary["P45_D001_buoyancy_probe"]["change_in_water_weight_dN"] > 0,
        "P45_D002_preserved": summary["P45_D002_tension_probe"]["rows"][2]["tension_printed"] == "1.290.500 dN",
        "P45_D005_head_envelopes_peak_to_peak": summary["P45_D005_head_amplitude_probe"]["all_peak_to_peak"],
        "figure11_15pct_claim_reproduced_as_peak_abs_stress": 13.0 <= summary["P45_D006_figure11_probe"]["attribution_as_recorded"]["peak_abs_underestimate_relative_to_nonlinear_percent"] <= 16.0,
        "nonlinear_dynamic_response_reproduced": False,
    },
    "qualification": "NOT_GRANTED",
}
write("engiproof_verification.json", verification)
print(json.dumps(verification, indent=2))
