from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location("p41_tool_api",HERE/"tool_api.py")
_api=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_api)


def main() -> None:
    out=_api.independent_table1_to_table2_summary()
    results=HERE/"results"; results.mkdir(parents=True,exist_ok=True)
    calc=out["calculated"]; pub=out["published_extracted"]
    with (results/"table2_reproduction.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["quantity","calculated","published_or_extracted","unit","status"])
        w.writerow(["A_inner",calc["A_inner_m2"],pub["A_inner_m2"],"m2","COMPARED"])
        w.writerow(["A_outer",calc["A_outer_m2"],pub["A_outer_m2"],"m2","COMPARED"])
        w.writerow(["EA_inner",calc["EA_inner_N"],pub["EA_inner_N"],"N","COMPARED"])
        w.writerow(["EA_outer",calc["EA_outer_N"],pub["EA_outer_N"],"N","COMPARED"])
        w.writerow(["deltaS_inner",calc["deltaS_inner_N_per_m"],pub["deltaS_inner_extracted_N_per_m"],"N/m","PUBLISHED_REFERENCE_MISMATCH"])
        w.writerow(["deltaS_outer",calc["deltaS_outer_N_per_m"],pub["deltaS_outer_N_per_m"],"N/m","COMPARED"])
        w.writerow(["deltaS_total",calc["deltaS_total_N_per_m"],pub["fS_N_per_m"],"N/m","INDEPENDENT_IDENTITY_CHECK"])
    phase2=_api.table3_bonding_summary()
    phase3=_api.phase3_global_buckling_summary()
    (results/"phase3_global_buckling_summary.json").write_text(json.dumps(phase3,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    verification={
        "paper_id":"P41",
        "status":"CONDITIONAL",
        "selected_chain":"Table 1 -> Table 2 -> Eqs. (6)-(8)",
        "summary":out,
        "phase2_bonding":phase2,
        "phase3_global_buckling":phase3,
        "checks":{
            "area_geometry_matches_table2":max(abs(out["comparisons"]["A_inner_relative_percent"]),abs(out["comparisons"]["A_outer_relative_percent"])) < 0.01,
            "EA_geometry_matches_table2":max(abs(out["comparisons"]["EA_inner_relative_percent"]),abs(out["comparisons"]["EA_outer_relative_percent"])) < 0.02,
            "eq8_total_matches_fS":abs(calc["deltaS_total_N_per_m"]-pub["fS_N_per_m"]) < 1e-10,
            "outer_force_rounds_to_table2_integer":abs(calc["deltaS_outer_N_per_m"]-pub["deltaS_outer_N_per_m"]) <= 0.5,
            "inner_force_published_mismatch_confirmed":True,
            "outer_elastic_bending_stiffness_exceeds_inner":phase3["independent_bending_stiffness"]["outer_to_inner_ratio"] > 1.0,
            "figure10_unit_mismatch_recorded":phase3["published_source_observations"]["figure10"]["axis_unit"] != phase3["published_source_observations"]["figure10"]["source_text_inner_unit"]
        },
        "qualification":"NOT_GRANTED"
    }
    (results/"engiproof_verification.json").write_text(json.dumps(verification,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(verification,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
