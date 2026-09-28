"""Callable source-bounded tools for EngiProof study P40."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location("p40_mechanics",HERE/"mechanics.py")
_m=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)


def equation2_pressure_kPa(Do: float, to: float, sigma_Yo_MPa: float) -> float:
    return _m.equation2_pressure_kPa(Do,to,sigma_Yo_MPa)


def equation3_pressure_kPa(Do: float, to: float, ti: float, sigma_Yo_MPa: float, sigma_Yi_over_sigma_Yo: float) -> float:
    return _m.equation3_pressure_kPa(Do,to,ti,sigma_Yo_MPa,sigma_Yi_over_sigma_Yo)


def equation6_pressure_kPa(D: float, t: float, sigma_Y_MPa: float) -> float:
    return _m.equation6_pressure_kPa(D,t,sigma_Y_MPa)


def equation9_pressure_kPa(Do: float, to: float, Di: float, ti: float, sigma_Yo_MPa: float, sigma_Yi_over_sigma_Yo: float) -> float:
    return _m.equation9_pressure_kPa(Do,to,Di,ti,sigma_Yo_MPa,sigma_Yi_over_sigma_Yo)


def independent_work_balance_pressure_kPa(Do: float, to: float, Di: float, ti: float, sigma_Yo_MPa: float, sigma_Yi_over_sigma_Yo: float) -> float:
    return _m.independent_work_balance_pressure_kPa(Do,to,Di,ti,sigma_Yo_MPa,sigma_Yi_over_sigma_Yo)


def table2_reproduction_summary() -> dict:
    """Recompute P40 Table 2 analytical ratios from Table 1 source inputs."""
    table1=json.loads((HERE/"inputs"/"table1.json").read_text(encoding="utf-8"))["cases"]
    with (HERE/"reference"/"table2.csv").open(encoding="utf-8",newline="") as f:
        refs={r["identifier"]:r for r in csv.DictReader(f)}
    rows=[]
    for c in table1:
        ref=refs[c["identifier"]]
        eq2=equation2_pressure_kPa(c["Do_mm"],c["to_mm"],c["sigma_Yo_MPa"])
        eq3=equation3_pressure_kPa(c["Do_mm"],c["to_mm"],c["ti_mm"],c["sigma_Yo_MPa"],c["sigma_Yi_over_sigma_Yo"])
        eq6=equation6_pressure_kPa(c["Do_mm"],c["to_mm"],c["sigma_Yo_MPa"])
        eq9=equation9_pressure_kPa(c["Do_mm"],c["to_mm"],c["Di_mm"],c["ti_mm"],c["sigma_Yo_MPa"],c["sigma_Yi_over_sigma_Yo"])
        indep=independent_work_balance_pressure_kPa(c["Do_mm"],c["to_mm"],c["Di_mm"],c["ti_mm"],c["sigma_Yo_MPa"],c["sigma_Yi_over_sigma_Yo"])
        Pp=float(ref["Pp_kPa"]); Pp2=float(ref["Pp2_kPa"])
        row={
            "identifier":c["identifier"],
            "eq2_ratio":eq2/Pp,
            "eq2_published_ratio":float(ref["eq2_hat_Pp_over_Pp"]),
            "eq3_ratio":eq3/Pp2,
            "eq3_published_ratio":float(ref["eq3_hat_Pp2_over_Pp2"]),
            "eq6_ratio":eq6/Pp,
            "eq6_published_ratio":float(ref["eq6_tilde_Pp_over_Pp"]),
            "eq9_ratio":eq9/Pp2,
            "eq9_published_ratio":float(ref["eq9_tilde_Pp2_over_Pp2"]),
            "independent_work_balance_ratio":indep/Pp2,
            "eq9_vs_independent_percent":100.0*(eq9-indep)/indep,
        }
        row["eq9_ratio_difference"]=row["eq9_ratio"]-row["eq9_published_ratio"]
        rows.append(row)
    p3=next(r for r in rows if r["identifier"]=="PIP-3")
    return {
        "rows":rows,
        "source_table":"P40 Table 2",
        "status":"CONDITIONAL",
        "open_discrepancy":{
            "identifier":"PIP-3",
            "calculated_eq9_ratio":p3["eq9_ratio"],
            "published_eq9_ratio":p3["eq9_published_ratio"],
            "absolute_ratio_difference":abs(p3["eq9_ratio_difference"]),
            "relative_to_published_percent":100.0*abs(p3["eq9_ratio_difference"])/p3["eq9_published_ratio"],
        },
        "evidence_boundary":"Published equations/Table 1/Table 2 are source-bounded; work-balance reconstruction is independent arithmetic/mechanics, not FE reproduction.",
    }
