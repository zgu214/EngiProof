"""Callable source-bounded tools for EngiProof study P41."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location("p41_mechanics",HERE/"mechanics.py")
_m=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)


def steel_area_m2(D_mm: float, t_mm: float) -> float:
    return _m.steel_area_m2(float(D_mm)/1000.0,float(t_mm)/1000.0)


def axial_stiffness_N(D_mm: float, t_mm: float, E_Pa: float) -> float:
    return _m.axial_stiffness_N(float(D_mm)/1000.0,float(t_mm)/1000.0,E_Pa)


def equation6_deltaS_inner_N_per_m(fS_N_per_m: float, EA_inner_N: float, EA_outer_N: float) -> float:
    return _m.equation6_deltaS_inner_N_per_m(fS_N_per_m,EA_inner_N,EA_outer_N)


def equation7_deltaS_outer_N_per_m(fS_N_per_m: float, EA_inner_N: float, EA_outer_N: float) -> float:
    return _m.equation7_deltaS_outer_N_per_m(fS_N_per_m,EA_inner_N,EA_outer_N)


def equation8_total_deltaS_N_per_m(deltaS_inner_N_per_m: float, deltaS_outer_N_per_m: float) -> float:
    return _m.equation8_total_deltaS_N_per_m(deltaS_inner_N_per_m,deltaS_outer_N_per_m)


def independent_table1_to_table2_summary() -> dict:
    src=json.loads((HERE/"inputs"/"table1.json").read_text(encoding="utf-8"))
    inner=src["pipes"]["inner"]; outer=src["pipes"]["outer"]
    with (HERE/"reference"/"table2.csv").open(encoding="utf-8",newline="") as f:
        ref={r["quantity"]:r for r in csv.DictReader(f)}
    out=_m.independent_load_share_from_geometry(
        float(ref["f_s"]["inner"]),
        inner["D_mm"]/1000.0,inner["t_mm"]/1000.0,inner["E_Pa"],
        outer["D_mm"]/1000.0,outer["t_mm"]/1000.0,outer["E_Pa"],
    )
    published={
        "A_inner_m2":float(ref["A_s"]["inner"]),
        "A_outer_m2":float(ref["A_s"]["outer"]),
        "EA_inner_N":float(ref["EA_s"]["inner"]),
        "EA_outer_N":float(ref["EA_s"]["outer"]),
        "deltaS_inner_extracted_N_per_m":float(ref["deltaS"]["inner"]),
        "deltaS_outer_N_per_m":float(ref["deltaS"]["outer"]),
        "fS_N_per_m":float(ref["f_s"]["inner"]),
    }
    return {
        "calculated":out,
        "published_extracted":published,
        "comparisons":{
            "A_inner_relative_percent":100.0*(out["A_inner_m2"]-published["A_inner_m2"])/published["A_inner_m2"],
            "A_outer_relative_percent":100.0*(out["A_outer_m2"]-published["A_outer_m2"])/published["A_outer_m2"],
            "EA_inner_relative_percent":100.0*(out["EA_inner_N"]-published["EA_inner_N"])/published["EA_inner_N"],
            "EA_outer_relative_percent":100.0*(out["EA_outer_N"]-published["EA_outer_N"])/published["EA_outer_N"],
            "deltaS_inner_minus_extracted_N_per_m":out["deltaS_inner_N_per_m"]-published["deltaS_inner_extracted_N_per_m"],
            "deltaS_outer_minus_published_N_per_m":out["deltaS_outer_N_per_m"]-published["deltaS_outer_N_per_m"],
        },
        "source_review":{
            "table2_inner_deltaS":"VISUALLY_CONFIRMED_153_N_PER_M",
            "interpretation":"The original PDF visibly reports 153 N/m. Eqs. (6)-(8) and the published stiffnesses give about 158.8 N/m; the published components 153+312 sum to 465 N/m rather than fS=471 N/m. This is retained as a published-reference mismatch without tuning.",
        },
        "evidence_boundary":"Geometry/EA arithmetic is INDEPENDENT. Eqs. (6)-(8) are PUBLISHED methods reconstructed from the selected source targets. No FE reproduction is claimed."
    }

def equation9_required_internal_friction_N_per_m(
    fS_N_per_m: float,
    EA_inner_N: float,
    EA_outer_N: float,
    gamma_f: float = 1.0,
) -> float:
    return _m.equation9_required_internal_friction_N_per_m(
        fS_N_per_m, EA_inner_N, EA_outer_N, gamma_f
    )


def classify_axial_bonding(fI_N_per_m: float, f_required_N_per_m: float) -> str:
    return _m.classify_axial_bonding(fI_N_per_m, f_required_N_per_m)


def dry_internal_friction_N_per_m(dry_weight_N_per_m: float, friction_coefficient: float) -> float:
    return _m.dry_internal_friction_N_per_m(dry_weight_N_per_m, friction_coefficient)


def equation10_end_expansion_m(
    S0_total_N: float,
    fS_N_per_m: float,
    EA_inner_N: float,
    EA_outer_N: float,
) -> float:
    return _m.equation10_end_expansion_m(S0_total_N, fS_N_per_m, EA_inner_N, EA_outer_N)


def table3_bonding_summary(gamma_f: float = 1.0) -> dict:
    with (HERE/"reference"/"table2.csv").open(encoding="utf-8",newline="") as f:
        ref2={r["quantity"]:r for r in csv.DictReader(f)}
    with (HERE/"reference"/"table3.csv").open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    EAi=float(ref2["EA_s"]["inner"])
    EAo=float(ref2["EA_s"]["outer"])
    fS=float(ref2["f_s"]["inner"])
    req=_m.equation9_required_internal_friction_N_per_m(fS,EAi,EAo,gamma_f)
    cases=[]
    for r in rows:
        fi=float(r["fI_N_per_m"])
        predicted=_m.classify_axial_bonding(fi,req)
        cases.append({
            "case":int(r["case"]),
            "fI_N_per_m":fi,
            "published_type":r["published_type"],
            "predicted_type":predicted,
            "published_end_expansion_m":float(r["end_expansion_m"]),
            "classification_matches":predicted==r["published_type"],
        })
    dry=_m.dry_internal_friction_N_per_m(1195.0,0.3)
    inferred_S0=_m.equation10_required_S0_N(1.305,fS,EAi,EAo)
    return {
        "gamma_f":float(gamma_f),
        "equation9_required_internal_friction_N_per_m":req,
        "cases":cases,
        "dry_weight_model":{
            "dry_weight_N_per_m":1195.0,
            "friction_coefficient":0.3,
            "calculated_fI_N_per_m":dry,
            "published_rounded_fI_N_per_m":358.0,
        },
        "equation10":{
            "status":"CONDITIONAL_INPUT_INCOMPLETE",
            "published_full_bond_end_expansion_m":1.305,
            "inferred_S0_total_N_from_published_delta":inferred_S0,
            "note":"Eq. (10) is implemented, but S0_total cannot be independently recreated from explicit numerical source inputs without assumptions. The inferred S0 value is an inversion, not an independent validation."
        },
        "evidence_boundary":"Eq. (9) and Eq. (10) are PUBLISHED methods. Table 3 bonding classification is an INDEPENDENT check. No FE reproduction is claimed."
    }



def second_moment_annulus_m4(D_mm: float, t_mm: float) -> float:
    return _m.second_moment_annulus_m4(float(D_mm)/1000.0,float(t_mm)/1000.0)


def bending_stiffness_Nm2(D_mm: float, t_mm: float, E_Pa: float) -> float:
    return _m.bending_stiffness_Nm2(float(D_mm)/1000.0,float(t_mm)/1000.0,E_Pa)


def equation14_design_moment(M_f: float, gamma_f: float, gamma_C: float) -> float:
    return _m.equation14_design_moment(M_f,gamma_f,gamma_C)


def phase3_global_buckling_summary() -> dict:
    src=json.loads((HERE/"inputs"/"table1.json").read_text(encoding="utf-8"))
    obs=json.loads((HERE/"reference"/"phase3_source_observations.json").read_text(encoding="utf-8"))
    inner=src["pipes"]["inner"]; outer=src["pipes"]["outer"]
    EI_inner=_m.bending_stiffness_Nm2(inner["D_mm"]/1000.0,inner["t_mm"]/1000.0,inner["E_Pa"])
    EI_outer=_m.bending_stiffness_Nm2(outer["D_mm"]/1000.0,outer["t_mm"]/1000.0,outer["E_Pa"])
    return {
        "independent_bending_stiffness":{
            "EI_inner_Nm2":EI_inner,
            "EI_outer_Nm2":EI_outer,
            "outer_to_inner_ratio":EI_outer/EI_inner,
            "engineering_interpretation":"Outer elastic EI exceeds inner EI, independently supporting the qualitative larger outer bending share. This does not reproduce nonlinear Figure 10 curves."
        },
        "equation14_examples":{
            "gamma_f":1.0,
            "gamma_C_1p0_factor":_m.equation14_design_moment(1.0,1.0,1.0),
            "gamma_C_0p8_factor":_m.equation14_design_moment(1.0,1.0,0.8)
        },
        "published_source_observations":obs,
        "evidence_boundary":"Figures 8-10 are source-observation evidence only; no curve digitization or FE reproduction is claimed. EI is an INDEPENDENT elastic check. Eq. (14) is PUBLISHED."
    }
