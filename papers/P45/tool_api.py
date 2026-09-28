"""Callable, source-bounded P45 tools - Safai (1983), Nonlinear dynamic analysis of deep water risers.

Evidence classes are stated per function. No function reproduces the paper's
nonlinear time-domain riser response: the source does not give the integration
parameters, damping, iteration tolerance or discretisation needed for that.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
REF = HERE / "reference"
_spec = importlib.util.spec_from_file_location("p45_mechanics", HERE / "mechanics.py")
M = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(M)

EVIDENCE_BOUNDARY = ("Source-bounded checks of the published tables, formulations and figure statements. "
                     "The nonlinear dynamic riser responses of Figures 4-9 and 11 are NOT reproduced: the source "
                     "does not give theta/beta/lambda, the iteration tolerance, structural damping, the "
                     "discretisation of cases 1-6, or the float properties and tension unit of the 1200 m example.")


def _ref(name: str) -> dict[str, Any]:
    return json.loads((REF / name).read_text(encoding="utf-8"))


def _r(x: float, n: int = 12) -> float:
    return float(round(x, n))


# ------------------------------------------------------------ PUBLISHED tools
def appendix1_stiffness_coefficients(F_N: float, EI_Nm2: float, L_m: float, GA_shear_N: float | None = None) -> dict[str, float]:
    """PUBLISHED Appendix 1: k1, k2, k3 [N m] for axial force F (tension > 0)."""
    out = M.stiffness_coefficients(float(F_N), float(EI_Nm2), float(L_m), math.inf if GA_shear_N is None else float(GA_shear_N))
    return {k: (float(v) if not isinstance(v, str) else v) for k, v in out.items()}


def eq7_theta_coefficients(theta: float, beta: float, lam: float, dt_s: float) -> dict[str, float]:
    """PUBLISHED Eq. (7): coefficients a1..a6 and tau = theta dt."""
    return {k: float(v) for k, v in M.theta_method_coefficients(float(theta), float(beta), float(lam), float(dt_s)).items()}


def example1200_head_displacement_m(t_s: float) -> float:
    """PUBLISHED (p. 222 text): Y = 7.70 sin(2 pi t / 9) [m]. The printed equation shows '/g'; the text states 9 s (P45-D004)."""
    return 7.70 * math.sin(2.0 * math.pi * float(t_s) / 9.0)


def example1200_head_tension_printed(t_s: float) -> float:
    """PUBLISHED (p. 222): T = 298 (1 + 0.2 sin(2 pi t / 9)). The source gives NO unit (P45-D003); the value is returned as printed."""
    return 298.0 * (1.0 + 0.2 * math.sin(2.0 * math.pi * float(t_s) / 9.0))


def example1200_current_speed_m_per_s(depth_m: float) -> float:
    """PUBLISHED labels of Figure 10 (0 m: 0.25, 200 m: 0.50, 600 m: 0.50, bottom 1200 m: 0), straight segments as drawn."""
    d = float(depth_m)
    if not 0.0 <= d <= 1200.0:
        raise ValueError("depth_m must lie in [0, 1200]")
    return float(np.interp(d, [0.0, 200.0, 600.0, 1200.0], [0.25, 0.50, 0.50, 0.0]))


def cases_current_speed_m_per_s(height_above_ball_joint_m: float, water_depth_m: float) -> float:
    """PUBLISHED Table 2 item 17: linear from 0.256 m/s at the free surface to zero at the ball joint (9.144 m above the sea bottom)."""
    z, h = float(height_above_ball_joint_m), float(water_depth_m)
    top = h - 9.144
    if not 0.0 <= z <= top:
        raise ValueError("height must lie between the ball joint and the free surface")
    return 0.256 * z / top


# ------------------------------------------------------------ INDEPENDENT checks
def table2_geometry_check() -> dict[str, Any]:
    """INDEPENDENT: riser length = depth + 15.24 - 9.144 and static offset = 3% of depth, against Table 2 B."""
    t = _ref("table2_parameters.json")["B_depth_dependent"]
    rows = []
    for h, L, off in zip(t["water_depth_m"], t["riser_length_m"], t["static_offset_m"]):
        Lc, oc = h + 15.24 - 9.144, 0.03 * h
        rows.append({"depth_m": h, "riser_length_printed_m": L, "riser_length_computed_m": _r(Lc, 6),
                     "static_offset_printed_m": off, "static_offset_computed_m": _r(oc, 6),
                     "within_print_rounding": abs(Lc - L) <= 0.005 + 1e-9 and abs(oc - off) <= 0.005 + 1e-9})
    return {"rows": rows, "all_within_print_rounding": all(r["within_print_rounding"] for r in rows),
            "basis": "riser from ball joint (9.144 m above bottom) to head (15.24 m above free surface); offset/depth = 0.03"}


def imperial_origin_check() -> dict[str, Any]:
    """INDEPENDENT: Table 1/2 values against round imperial quantities (the API 2J comparison basis, ref. 2)."""
    t2 = _ref("table2_parameters.json")["A_depth_independent"]
    items = [
        ("free surface to head", t2["1_free_surface_to_riser_head_m"] / M.FT, "ft", 50),
        ("bottom to ball joint", t2["2_sea_bottom_to_ball_joint_m"] / M.FT, "ft", 30),
        ("riser OD", t2["3_riser_OD_cm"] / 100 / M.INCH, "in", 16),
        ("riser ID", t2["4_riser_ID_cm"] / 100 / M.INCH, "in", 14.75),
        ("choke/kill OD", t2["5_choke_OD_cm"] / 100 / M.INCH, "in", 4),
        ("choke/kill ID", t2["6_choke_ID_cm"] / 100 / M.INCH, "in", 2.7),
        ("buoyant material OD", t2["9_buoyant_material_OD_cm"] / 100 / M.INCH, "in", 24),
        ("E", t2["10_E_dN_per_m2"] * M.DN / 6.894757293168e3 / 1e6, "Mpsi", 30),
        ("wave height", t2["18_wave_height_m"] / M.FT, "ft", 20),
        ("head displacement 'amplitude'", t2["20_amplitude_of_prescribed_head_displacement_m"] / M.FT, "ft", 4),
        ("current at surface", 0.256 / M.KNOT, "knot", 0.5),
        ("water depth 1", 152.40 / M.FT, "ft", 500), ("water depth 2", 457.20 / M.FT, "ft", 1500), ("water depth 3", 914.40 / M.FT, "ft", 3000),
        ("bending-stress axis 6.90 dN/mm²", 6.90 * 1e7 / M.KSI, "ksi", 10),
    ]
    rows = [{"quantity": q, "converted": _r(v, 6), "unit": u, "round_value": r, "relative_deviation": _r(abs(v - r) / r, 8)} for q, v, u, r in items]
    tension = [{"case": c["case"], "tension_printed": c["tension_printed"], "kips": _r(c["tension_dN"] * M.DN / M.KIP, 4)}
               for c in _ref("table1_cases.json")["cases"]]
    return {"table2_and_axes": rows, "max_relative_deviation": max(r["relative_deviation"] for r in rows), "table1_tension_in_kips": tension}


def table1_tension_plausibility() -> dict[str, Any]:
    """INDEPENDENT: head axial stress and tension-to-submerged-weight ratio implied by the printed Table 1 tensions (P45-D002)."""
    t2 = _ref("table2_parameters.json")
    A = t2["A_depth_independent"]
    B = t2["B_depth_dependent"]
    As = M.annulus_area(A["3_riser_OD_cm"] / 100, A["4_riser_ID_cm"] / 100)
    wp = A["16_element_weight_per_15.24m_dN"]["wp_in_water"]
    rows = []
    for c in _ref("table1_cases.json")["cases"]:
        i = B["water_depth_m"].index(c["depth_m"])
        L = B["riser_length_m"][i]
        buoyed = c["depth_m"] == 914.40  # 'Only the riser of 914.40 m has buoyant material attached.'
        w_line = (wp["buoyed"] if buoyed else wp["unbuoyed"]) / 15.24  # dN/m, as tabulated
        stress = c["tension_dN"] * M.DN / As / 1e6
        rows.append({"case": c["case"], "tension_printed": c["tension_printed"], "head_axial_stress_MPa_riser_pipe": _r(stress, 4),
                     "tension_over_tabulated_submerged_weight": _r(c["tension_dN"] / (w_line * L), 4),
                     "ten_times_smaller_stress_MPa": _r(stress / 10, 4)})
    return {"riser_steel_area_m2": _r(As, 10), "rows": rows,
            "note": "Stress uses the 40.64/37.46 cm riser pipe only (choke/kill lines do not contribute to stiffness per Table 2). "
                    "Submerged weight uses the tabulated w_p over the riser length, without internal mud."}


def table2_buoyancy_consistency() -> dict[str, Any]:
    """INDEPENDENT: Table 2 buoyed vs unbuoyed element weights against the buoyant-material geometry (P45-D001)."""
    A = _ref("table2_parameters.json")["A_depth_independent"]
    w = A["16_element_weight_per_15.24m_dN"]
    rho = A["11_water_density_kg_per_m3"]
    d_air = w["wa_in_air"]["buoyed"] - w["wa_in_air"]["unbuoyed"]
    d_water = w["wp_in_water"]["buoyed"] - w["wp_in_water"]["unbuoyed"]
    implied_buoyancy_dN = d_air - d_water
    implied_volume = implied_buoyancy_dN * M.DN / (rho * M.G)
    Lh = 15.24
    annulus = M.annulus_area(A["9_buoyant_material_OD_cm"] / 100, A["3_riser_OD_cm"] / 100) * Lh
    lines = 2 * math.pi / 4 * (A["5_choke_OD_cm"] / 100) ** 2 * Lh
    geom_volume = annulus - lines
    expected_d_water = d_air - geom_volume * rho * M.G / M.DN
    return {"added_weight_in_air_dN": d_air, "change_in_water_weight_dN": d_water,
            "implied_added_buoyancy_dN": _r(implied_buoyancy_dN, 6), "implied_displaced_volume_m3": _r(implied_volume, 8),
            "implied_density_of_added_material_kg_per_m3": _r(d_air * M.DN / M.G / implied_volume, 4),
            "geometric_buoyant_volume_m3": _r(geom_volume, 8),
            "expected_change_in_water_weight_dN": _r(expected_d_water, 4),
            "assumption": "Buoyant material fills the annulus from the 40.64 cm riser to the 60.96 cm OD, less the two 10.16 cm choke/kill lines (Figure 3 cross-section), over the 15.24 m element; g = 9.80665 m/s²."}


def airy_depth_regime() -> dict[str, Any]:
    """INDEPENDENT: Airy dispersion for T = 9 s at all four water depths; validity of the 'infinite depth' wave model (Table 2 footnote)."""
    rows = []
    L0 = M.G * 81.0 / (2 * math.pi)
    for h in (152.40, 457.20, 914.40, 1200.0):
        k = M.airy_wavenumber(9.0, h)
        rows.append({"depth_m": h, "wavelength_m": _r(2 * math.pi / k, 8), "kh": _r(k * h, 8),
                     "one_minus_tanh_kh": 1 - math.tanh(k * h), "depth_over_wavelength": _r(h * k / (2 * math.pi), 8)})
    omega = 2 * math.pi / 9.0
    return {"deep_water_wavelength_m": _r(L0, 8), "rows": rows,
            "surface_orbital_velocity_amplitude_m_per_s": {"cases_H_6.096m": _r(omega * 6.096 / 2, 10), "example_1200m_H_6m": _r(omega * 3.0, 10)},
            "infinite_depth_error_max": max(r["one_minus_tanh_kh"] for r in rows)}


def example1200_weight_and_tension_units() -> dict[str, Any]:
    """INDEPENDENT: Table 3 effective weight of the 1200 m riser vs the printed tension '298' under candidate units (P45-D003)."""
    t = _ref("table3_1200m.json")
    D, e = t["D_cm"] / 100, t["e_wall_cm"] / 100
    Di = D - 2 * e
    steel = t["rho_riser_kg_per_m3"] * M.annulus_area(D, Di)
    mud = t["rho_mud_kg_per_m3"] * math.pi / 4 * Di ** 2
    disp = t["rho_water_kg_per_m3"] * math.pi / 4 * D ** 2
    per_m = steel + mud - disp
    float_max = t["rho_water_kg_per_m3"] * M.annulus_area(0.60, D)
    W = per_m * 1200 * M.G
    W_float = (per_m - float_max) * 1200 * M.G
    cands = {"N": 1.0, "dN": 10.0, "kN": 1e3, "tonne-force": 1000 * M.G, "10 kN": 1e4}
    rows = []
    for u, f in cands.items():
        Tm = 298 * f
        rows.append({"unit": u, "mean_tension_MN": _r(Tm / 1e6, 8), "min_tension_MN": _r(0.8 * Tm / 1e6, 8),
                     "mean_over_weight_without_floats": _r(Tm / W, 6), "mean_over_weight_with_ideal_floats": _r(Tm / W_float, 6),
                     "min_over_weight_with_ideal_floats": _r(0.8 * Tm / W_float, 6)})
    return {"mass_per_m_kg": {"steel": _r(steel, 6), "mud": _r(mud, 6), "displaced_water": _r(disp, 6), "net": _r(per_m, 6)},
            "effective_weight_MN_without_floats": _r(W / 1e6, 8),
            "ideal_float_net_buoyancy_kg_per_m": _r(float_max, 6),
            "effective_weight_MN_with_ideal_floats": _r(W_float / 1e6, 8),
            "candidate_units": rows,
            "assumptions": "Mud-filled riser (text); 'ideal floats' = massless 60 cm floats over the full length (an upper bound on float benefit; coverage and mass are not given); g = 9.80665 m/s²."}


def head_envelope_interpretation() -> dict[str, Any]:
    """INDEPENDENT: measured head envelopes of Figures 4(a)-9(a) vs the Table 2 head motion read as single or peak-to-peak amplitude (P45-D005)."""
    dig = _ref("figure4_9_head_envelopes.json")
    B = _ref("table2_parameters.json")["B_depth_dependent"]
    a = _ref("table2_parameters.json")["A_depth_independent"]["20_amplitude_of_prescribed_head_displacement_m"]
    depth_of_case = {1: 152.40, 2: 152.40, 3: 457.20, 4: 457.20, 5: 914.40, 6: 914.40}
    rows = []
    for f in dig["figures"]:
        off = B["static_offset_m"][B["water_depth_m"].index(depth_of_case[f["case"]])]
        lo, hi, u = f["head_envelope_min_m"], f["head_envelope_max_m"], f["uncertainty_m"]
        width = hi - lo
        rows.append({"figure": f["figure"], "case": f["case"], "static_offset_m": off,
                     "measured_min_m": lo, "measured_max_m": hi, "uncertainty_m": u,
                     "measured_centre_m": _r((lo + hi) / 2, 4), "centre_minus_offset_m": _r((lo + hi) / 2 - off, 4),
                     "measured_width_m": _r(width, 4),
                     "width_if_single_amplitude_m": _r(2 * a, 4), "width_if_peak_to_peak_m": a,
                     "consistent_with_peak_to_peak": abs(width - a) <= 2 * u + 0.1,
                     "consistent_with_single_amplitude": abs(width - 2 * a) <= 2 * u + 0.1})
    return {"rows": rows,
            "all_peak_to_peak": all(r["consistent_with_peak_to_peak"] for r in rows),
            "any_single_amplitude": any(r["consistent_with_single_amplitude"] for r in rows),
            "acceptance": "width within 2 x (tick residual + line width) + 0.1 m reading allowance"}


def figure11_linear_vs_nonlinear() -> dict[str, Any]:
    """INDEPENDENT: arithmetic of the Figure 11 extreme labels against the '~15%' statement (P45-D006)."""
    f = _ref("figure11_extremes.json")
    lin, non = f["attribution"]["linear"], f["attribution"]["nonlinear"]

    def metrics(lin, non):
        pl, pn = max(abs(lin["max"]), abs(lin["min"])), max(abs(non["max"]), abs(non["min"]))
        rl, rn = lin["max"] - lin["min"], non["max"] - non["min"]
        return {
            "max_envelope_linear_vs_nonlinear_percent": _r(100 * (lin["max"] / non["max"] - 1), 6),
            "min_envelope_linear_vs_nonlinear_percent": _r(100 * (lin["min"] / non["min"] - 1), 6),
            "peak_abs_linear_dN_per_mm2": pl, "peak_abs_nonlinear_dN_per_mm2": pn,
            "peak_abs_underestimate_relative_to_nonlinear_percent": _r(100 * (1 - pl / pn), 6),
            "peak_abs_nonlinear_excess_relative_to_linear_percent": _r(100 * (pn / pl - 1), 6),
            "range_underestimate_relative_to_nonlinear_percent": _r(100 * (1 - rl / rn), 6),
        }
    alt_lin = {"max": non["max"], "min": lin["min"]}
    alt_non = {"max": lin["max"], "min": non["min"]}
    return {"attribution_as_recorded": metrics(lin, non), "alternative_max_attribution": metrics(alt_lin, alt_non),
            "attribution_confidence": f["attribution"]["confidence"],
            "claim": "about 15% underestimate near the riser head",
            "unit_note": "1 dN/mm² = 10 MPa; the peak |stress| of 31.40 dN/mm² is 314 MPa"}


def appendix1_independent_checks() -> dict[str, Any]:
    """INDEPENDENT: identities, limits, buckling points and an independent FE solution for the Appendix 1 coefficients."""
    EI, L = 1.0, 1.0
    identity = []
    cont = []
    for delta in (0.0, 0.05):
        GA = math.inf if delta == 0 else EI / (L * L * delta)
        z = M.stiffness_coefficients(0.0, EI, L, GA)
        for sgn, name in ((-1, "compression"), (1, "tension")):
            diffs = []
            for x in (0.2, 0.1, 0.05):
                F = sgn * x * x * EI / L**2 if math.isinf(GA) else sgn * x * x * EI / (1 - sgn * x * x * EI / GA)
                k = M.stiffness_coefficients(F, EI, L, GA)
                identity.append(abs(k["k3"] - k["k1"] - k["k2"]) / abs(k["k3"]))
                diffs.append(abs(k["k1"] - z["k1"]))
            cont.append({"delta": delta, "branch": name, "zero_branch_k1": _r(z["k1"], 12),
                         "k1_difference_at_alphaL_0.2_0.1_0.05": diffs,
                         "convergence_ratios": [diffs[0] / diffs[1], diffs[1] / diffs[2]]})
    kpi = M.stiffness_coefficients(-math.pi**2 * EI / L**2, EI, L)
    kpp = M.stiffness_coefficients(-(2 * math.pi - 1e-4) ** 2 * EI / L**2, EI, L)
    fe = []
    for F in (-9.0, -2.0, 3.0, 25.0):
        a = M.stiffness_coefficients(F, EI, L)
        b = M.hermite_beam_column_end_stiffness(F, EI, L, 400)
        fe.append({"F_over_EI_per_L2": F, "k1_published": a["k1"], "k1_fe": b["k1"],
                   "k2_published": a["k2"], "k2_fe": b["k2"],
                   "k3_over_L_published": a["k3"] / L, "fe_transverse_reaction": b["shear_at_rotated_end"],
                   "max_relative_difference": max(abs(a["k1"] - b["k1"]) / abs(a["k1"]), abs(a["k2"] - b["k2"]) / abs(a["k2"]), abs(a["k3"] / L - b["shear_at_rotated_end"]) / abs(a["k3"]))})
    Kchk = M.stiffness_coefficients(5.0, 2.0, 3.0, 1e3)
    K = M.element_linear_stiffness(10.0, 1.5, 3.0, Kchk["k1"], Kchk["k2"], Kchk["k3"])
    Kbad = M.element_linear_stiffness(10.0, 1.5, 3.0, Kchk["k1"], Kchk["k2"], 1.01 * Kchk["k3"])
    null = lambda A: int(np.sum(np.abs(np.linalg.eigvalsh(A)) < 1e-9 * np.abs(np.linalg.eigvalsh(A)).max()))
    return {
        "k3_equals_k1_plus_k2_max_relative_residual": max(identity),
        "continuity_at_zero_axial_force": cont,
        "euler_pinned_pinned_x_pi": {"k1": kpi["k1"], "k2": kpi["k2"], "k1_minus_k2": kpi["k1"] - kpi["k2"]},
        "fixed_fixed_approach_x_2pi_minus_1e-4": {"k1": _r(kpp["k1"], 4), "note": "stiffness grows without bound as the denominator -x sin x + 2(1 - cos x) -> 0 at x = 2 pi"},
        "independent_fe_comparison": fe,
        "rigid_body_nullity_of_K": null(K), "rigid_body_residual": float(np.abs(K @ M.rigid_body_modes(3.0)).max()),
        "rigid_body_nullity_if_k3_perturbed_1pct": null(Kbad),
        "K_symmetric": bool(np.abs(K - K.T).max() == 0.0),
    }


def eq7_independent_checks() -> dict[str, Any]:
    """INDEPENDENT: Eq. (7) reductions and stability of the reconstructed theta scheme (theta is not given in the source)."""
    tau = 1.0
    wil = M.theta_method_coefficients(1.0, 1.0 / 6.0, 0.5, tau)
    wilson_expected = {"a1": 3 / tau, "a2": -2.0, "a3": -tau / 2, "a4": 6 / tau**2, "a5": -6 / tau, "a6": -2.0}
    avg = M.theta_method_coefficients(1.0, 0.25, 0.5, tau)
    avg_expected = {"a1": 2 / tau, "a2": -1.0, "a3": 0.0, "a4": 4 / tau**2, "a5": -4 / tau, "a6": -1.0}
    dev = lambda got, exp: max(abs(got[k] - v) for k, v in exp.items())
    grid = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.55, 0.6, 1.0, 2.0, 5.0, 10.0, 100.0]
    radius = {str(th): [M.spectral_radius(th, g) for g in grid] for th in (1.0, 1.2, 1.37, 1.4, 2.0)}
    lo, hi = 0.1, 2.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if M.spectral_radius(1.0, mid) <= 1 + 1e-12 else (lo, mid)
    T = 2 * math.pi
    r = M.sdof_theta_response(1.0, 0.0, 1.0, lambda t: 0.0, 1.0, 0.0, T / 200, 200, theta=1.4)
    return {
        "linear_acceleration_reduction_max_deviation": dev(wil, wilson_expected),
        "average_acceleration_reduction_max_deviation": dev(avg, avg_expected),
        "spectral_radius_dt_over_T_grid": grid, "spectral_radius_by_theta": radius,
        "theta_1_critical_dt_over_T": lo,
        "theta_1.37_unconditionally_stable_on_grid": all(v <= 1 + 1e-9 for v in radius["1.37"]),
        "free_vibration_one_period_error_theta_1.4_dt_T_over_200": abs(r["u"][-1] - 1.0),
        "reconstruction_note": "The t+tau -> t+dt step is not printed in the source; standard Wilson-theta/Newmark relations are used.",
        "example_1200m_dt_over_excitation_period": _r(0.1 / 9.0, 10),
    }


def appendix2_independent_checks() -> dict[str, Any]:
    """INDEPENDENT: Appendix 2 C-factors as linear/Hermite interpolation at segment midpoints; B_i as the transverse projector."""
    worst = {"C1_plus_C3": 0.0, "hermite_translation_partition": 0.0, "hermite_shape_match": 0.0}
    for n in (1, 2, 5, 10, 40):
        for q in range(1, n + 1):
            c = M.segment_factors(n, q)
            xi = (q - 0.5) / n
            worst["C1_plus_C3"] = max(worst["C1_plus_C3"], abs(c["C1"] + c["C3"] - 1))
            worst["hermite_translation_partition"] = max(worst["hermite_translation_partition"], abs(c["C1"]**2 * c["C2"] + c["C3"]**2 * c["C4"] - 1))
            N1, N3 = 1 - 3 * xi**2 + 2 * xi**3, 3 * xi**2 - 2 * xi**3
            N2, N4 = xi * (1 - xi) ** 2, -xi**2 * (1 - xi)
            worst["hermite_shape_match"] = max(worst["hermite_shape_match"], abs(c["C1"]**2 * c["C2"] - N1), abs(c["C3"]**2 * c["C4"] - N3),
                                               abs(c["C3"] * c["C1"]**2 - N2), abs(-c["C1"] * c["C3"]**2 - N4))
    rng = np.random.default_rng(45)
    proj = 0.0
    for _ in range(20):
        e = rng.normal(size=3); e /= np.linalg.norm(e)
        B = M.added_mass_Bi(1.0, 1.0, 1.0, 1.0, e)
        proj = max(proj, float(np.abs(B - (np.eye(3) - np.outer(e, e))).max()), float(np.abs(B @ e).max()))
    return dict(worst) | {"Bi_equals_transverse_projector_max_deviation": proj,
            "dimension_note": "S(i,q) is printed 3x6 (translations only) and Q(i,q) 12x3, so M_ma as written maps the 6 translational accelerations to 12 element forces; rotational accelerations carry no added mass."}


def phase1_summary() -> dict[str, Any]:
    """Complete Phase 1 evidence summary (runner output)."""
    return {
        "schema_version": "engiproof.p45.phase1/1.0",
        "paper_id": "P45",
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "table2_geometry_check": table2_geometry_check(),
        "imperial_origin_check": imperial_origin_check(),
        "P45_D001_buoyancy_probe": table2_buoyancy_consistency(),
        "P45_D002_tension_probe": table1_tension_plausibility(),
        "P45_D003_tension_unit_probe": example1200_weight_and_tension_units(),
        "P45_D005_head_amplitude_probe": head_envelope_interpretation(),
        "P45_D006_figure11_probe": figure11_linear_vs_nonlinear(),
        "airy_depth_regime": airy_depth_regime(),
        "appendix1_checks": appendix1_independent_checks(),
        "eq7_checks": eq7_independent_checks(),
        "appendix2_checks": appendix2_independent_checks(),
        "qualification": "NOT_GRANTED",
    }
