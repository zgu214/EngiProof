from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("p43_mechanics", HERE / "mechanics.py")
_m = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_m)


def dimensionless_parameters(**kwargs):
    return _m.dimensionless_alpha_beta(**kwargs)


def independent_eigenvalues(alpha: float, beta: float, modes: int = 5, elements: int = 80):
    return _m.solve_dimensionless_eigenproblem(alpha, beta, elements=elements, modes=modes)["lambda"]


def equation10_lambda(mode: int, alpha: float, beta: float):
    return _m.equation10_approximate_lambda(mode, alpha, beta)


def natural_period_s(
    lambda_value: float,
    youngs_modulus_psi: float,
    second_moment_in4: float,
    participating_mass_slug_per_ft: float,
    length_ft: float,
):
    return _m.period_from_lambda(
        lambda_value,
        youngs_modulus_psi=youngs_modulus_psi,
        second_moment_in4=second_moment_in4,
        participating_mass_slug_per_ft=participating_mass_slug_per_ft,
        length_ft=length_ft,
    )


def phase1_eigen_benchmark_summary() -> dict:
    case = json.loads((HERE / "inputs" / "example_case.json").read_text(encoding="utf-8"))
    table1 = json.loads((HERE / "reference" / "table1_selected_rows.json").read_text(encoding="utf-8"))
    table2 = json.loads((HERE / "reference" / "table2_alpha50_beta100.json").read_text(encoding="utf-8"))
    fig6 = json.loads((HERE / "reference" / "figure6_source_review.json").read_text(encoding="utf-8"))

    dim = _m.dimensionless_alpha_beta(
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

    ref50 = next(r for r in table1["rows"] if r["alpha"] == 50.0 and r["beta"] == 100.0)
    fe50 = _m.solve_dimensionless_eigenproblem(50.0, 100.0, elements=100, modes=5)
    comparisons = []
    for i, (pub, calc) in enumerate(zip(ref50["lambda"], fe50["lambda"]), 1):
        comparisons.append({
            "mode": i,
            "published_lambda": pub,
            "independent_FE_lambda": calc,
            "difference": calc - pub,
            "relative_difference_percent": (calc - pub) / pub * 100.0,
        })

    eq10 = []
    for i, pub in enumerate(ref50["lambda"], 1):
        approx = _m.equation10_approximate_lambda(i, 50.0, 100.0)
        eq10.append({
            "mode": i,
            "published_exact_lambda": pub,
            "eq10_lambda": approx,
            "computed_error_percent": (approx - pub) / pub * 100.0,
            "published_table2_error_percent": table2["published_relative_error_percent_by_mode"][i - 1],
        })

    physical = dict(
        youngs_modulus_psi=case["youngs_modulus_psi"],
        second_moment_in4=case["second_moment_in4"],
        participating_mass_slug_per_ft=case["participating_mass_slug_per_ft"],
        length_ft=case["length_ft"],
    )
    omega_pub_lambda = _m.omega_from_lambda(case["published_lambda1"], **physical)
    period_pub_lambda = _m.period_from_lambda(case["published_lambda1"], **physical)
    eq10_l1 = _m.equation10_approximate_lambda(1, 50.0, 100.0)
    period_eq10 = _m.period_from_lambda(eq10_l1, **physical)

    mode1 = _m.sample_mode_shape(250.0, 100.0, 1, elements=160, points=501)
    inflection = mode1["interior_inflection_zeta"][-1] if mode1["interior_inflection_zeta"] else None
    below_top = (1.0 - inflection) if inflection is not None else None

    return {
        "source_example_parameter_check": {
            "computed_from_printed_inputs": dim,
            "published_table_parameters": {"alpha": case["published_alpha"], "beta": case["published_beta"]},
            "interpretation": "Printed example inputs give values close to the discrete Table 1 parameter pair used by the source. No hidden inputs are fitted."
        },
        "table1_independent_FE_comparison": {
            "alpha": 50.0,
            "beta": 100.0,
            "comparisons": comparisons,
            "method": "Independent cubic-Hermite finite-element weak solution of Eq. (8), not the source Eq. (9) power-series implementation."
        },
        "equation10_table2_comparison": {
            "alpha": 50.0,
            "beta": 100.0,
            "comparisons": eq10
        },
        "worked_example": {
            "published_lambda1": case["published_lambda1"],
            "omega_from_published_lambda_rad_per_s": omega_pub_lambda,
            "published_omega_rad_per_s": case["published_omega1_rad_per_s"],
            "period_from_published_lambda_s": period_pub_lambda,
            "published_exact_period_s": case["published_exact_period_s"],
            "eq10_lambda1": eq10_l1,
            "eq10_period_s": period_eq10,
            "published_approx_period_s": case["published_approx_period_s"]
        },
        "figure6_independent_mode_shape_check": {
            "alpha": 250.0,
            "beta": 100.0,
            "independent_lambda1": mode1["lambda"],
            "first_mode_inflection_zeta": inflection,
            "distance_below_top": below_top,
            "published_statement": "approximately 0.1 below the top",
            "curve_digitized": False,
            "source_review": fig6
        },
        "evidence_boundary": "Table values and worked-example values are PUBLISHED. The Eq. (8) Hermite-FE solution and parameter arithmetic are INDEPENDENT. The source power-series implementation is not recreated because its coefficient details are referred to earlier papers. No Figure 6 raster/curve digitization is used.",
        "qualification": "NOT_GRANTED"
    }

def phase2_full_matrix_summary() -> dict:
    table1=json.loads((HERE/"reference"/"table1_full.json").read_text(encoding="utf-8"))
    table2=json.loads((HERE/"reference"/"table2_full.json").read_text(encoding="utf-8"))
    t2={(float(r["alpha"]),float(r["beta"])):r["error_percent"] for r in table2["rows"]}
    rows=[]
    for row in table1["rows"]:
        a=float(row["alpha"]); b=float(row["beta"])
        calc=_m.solve_dimensionless_eigenproblem(a,b,elements=100,modes=5)["lambda"]
        approx=[_m.equation10_approximate_lambda(i,a,b) for i in range(1,6)]
        for i,(pub,fe,ap) in enumerate(zip(row["lambda"],calc,approx),1):
            rows.append({
                "alpha":a,"beta":b,"mode":i,"published_lambda":float(pub),
                "independent_FE_lambda":float(fe),"FE_difference":float(fe-pub),
                "FE_relative_difference_percent":float((fe-pub)/pub*100.0),
                "eq10_lambda":float(ap),
                "eq10_error_from_printed_table1_percent":float((ap-pub)/pub*100.0),
                "eq10_error_from_independent_FE_percent":float((ap-fe)/fe*100.0),
                "published_table2_error_percent":float(t2[(a,b)][i-1]),
            })
    ordinary=[r for r in rows if not ((r["alpha"]==0.0 and r["beta"]==200.0 and r["mode"]==5) or (r["alpha"]==200.0 and r["beta"]==100.0 and r["mode"]==1))]
    max_abs=max(abs(r["FE_relative_difference_percent"]) for r in ordinary)
    max_abs_diff=max(abs(r["FE_difference"]) for r in ordinary)
    max_table2_delta=max(abs(r["eq10_error_from_independent_FE_percent"]-r["published_table2_error_percent"]) for r in rows)
    figures45=[]
    for b in (0.0,100.0,200.0,300.0,400.0):
        for a in (0.0,50.0,100.0,150.0,200.0,250.0,300.0):
            r1=next(r for r in rows if r["alpha"]==a and r["beta"]==b and r["mode"]==1)
            r2=next(r for r in rows if r["alpha"]==a and r["beta"]==b and r["mode"]==2)
            figures45.append({"alpha":a,"beta":b,"published_lambda1":r1["published_lambda"],"independent_lambda1":r1["independent_FE_lambda"],"published_lambda2":r2["published_lambda"],"independent_lambda2":r2["independent_FE_lambda"]})
    shapes=[]; shape_summary=[]
    for mode in (1,2,3):
        s=_m.sample_mode_shape(250.0,100.0,mode,elements=160,points=501)
        for z,y,sl,cu in zip(s["zeta"],s["Y_normalized"],s["slope"],s["curvature"]):
            shapes.append({"mode":mode,"zeta":z,"Y_normalized":y,"slope":sl,"curvature":cu})
        shape_summary.append({"mode":mode,"independent_lambda":s["lambda"],"inflection_zeta":s["interior_inflection_zeta"],"distance_below_top":s["distance_below_top"]})
    typo=next(r for r in rows if r["alpha"]==0.0 and r["beta"]==200.0 and r["mode"]==5)
    typo2=next(r for r in rows if r["alpha"]==200.0 and r["beta"]==100.0 and r["mode"]==1)
    return {
        "table1_full_matrix":{"row_count":len(table1["rows"]),"scalar_comparisons":len(rows),"max_abs_FE_relative_difference_percent_excluding_source_mismatches":max_abs,"max_abs_FE_difference_excluding_source_mismatches":max_abs_diff,"max_abs_Table2_error_difference_percentage_points_using_independent_FE":max_table2_delta,"comparisons":rows},
        "figures4_5_parameter_families":{"status":"REPRODUCED_FROM_TABLE_AND_INDEPENDENT_FE","rows":figures45,"curve_digitized":False},
        "figure6_first_three_modes":{"status":"INDEPENDENT_MODE_SHAPES","summary":shape_summary,"rows":shapes,"curve_digitized":False},
        "P43_D001_probe":{"classification":"PUBLISHED_REFERENCE_MISMATCH","source_cell":{"alpha":0.0,"beta":200.0,"mode":5,"printed_lambda":typo["published_lambda"]},"independent_FE_lambda":typo["independent_FE_lambda"],"eq10_lambda":typo["eq10_lambda"],"published_table2_error_percent":typo["published_table2_error_percent"],"observation":"Table 1 visibly prints lambda5=13.221 at alpha=0, beta=200. Independent Eq.8 FE and Eq.10 both give approximately 18.221, while Table 2 reports zero approximation error for alpha=0. This is retained as a source-internal numerical mismatch.","source_correction_inferred_not_applied":"18.221 is a strongly supported inferred intended value, but the source record remains 13.221 unless an erratum/author source confirms the correction."},
        "P43_D002_probe":{"classification":"PUBLISHED_REFERENCE_MISMATCH","source_cell":{"alpha":200.0,"beta":100.0,"mode":1,"printed_lambda":typo2["published_lambda"]},"independent_FE_lambda":typo2["independent_FE_lambda"],"eq10_lambda":typo2["eq10_lambda"],"published_table2_error_percent":typo2["published_table2_error_percent"],"observation":"Table 1 visibly prints lambda1=6.554 at alpha=200, beta=100. Independent Eq.8 FE gives approximately 6.654, and using 6.654 makes the Eq.10 error approximately 1.39%, matching Table 2. The printed 6.554 is retained as source evidence.","source_correction_inferred_not_applied":"6.654 is a strongly supported inferred intended value, but EngiProof does not replace the printed 6.554 without authoritative confirmation."},
        "evidence_boundary":"Full Table 1/2 transcription is PUBLISHED source evidence. The Hermite-FE matrix and mode shapes are INDEPENDENT. Figures 4-6 are reconstructed from source table mechanics / independent equations without redistributing or digitizing publisher raster curves.",
        "qualification":"NOT_GRANTED"
    }

