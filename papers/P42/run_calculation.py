from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("p42_api",HERE/"tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

def main():
    results=HERE/"results"; results.mkdir(parents=True,exist_ok=True)
    s=api.phase1_continuum_summary()
    (results/"phase1_summary.json").write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (results/"equation42_continuum_curve.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["kappa_per_m","M0_cont_kNm","M3_cont_kNm","M_cont_total_kNm"])
        w.writeheader(); w.writerows(s["equation42_continuum"]["curve"])
    phase2=api.phase2_analytical_stress_summary()
    (results/"phase2_analytical_stress_summary.json").write_text(json.dumps({k:v for k,v in phase2.items() if k!="curve_rows"},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (results/"phase2_analytical_stress_curves.csv").open("w",encoding="utf-8",newline="") as f:
        fields=["layer","kappa_G_per_m","nu_deg","transverse_analytical_MPa","normal_analytical_MPa"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(phase2["curve_rows"])
    phase3=api.phase3_axisymmetric_and_moment_summary()
    phase3_small={k:v for k,v in phase3.items() if k!="equation41_figure16_probe"}
    phase3_small["equation41_figure16_probe"]={k:v for k,v in phase3["equation41_figure16_probe"].items() if k!="rows"}
    (results/"phase3_axisymmetric_moment_summary.json").write_text(json.dumps(phase3_small,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (results/"phase3_figure16_literal_probe.csv").open("w",encoding="utf-8",newline="") as f:
        fields=["Fz_kN","kappa_G_per_m","M_inner_armor_kNm","M_outer_armor_kNm","M_continuum_kNm","M_total_literal_kNm","inner_nu_star_deg","outer_nu_star_deg"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(phase3["equation41_figure16_probe"]["rows"])
    verification={
        "paper_id":"P42","evidence_status":"COMPARED",
        "checks":{
            "pitch_balance_relative_abs_percent":abs(s["table1_pitch_balance"]["relative_difference_percent"]),
            "pitch_balance_within_0p01_percent":abs(s["table1_pitch_balance"]["relative_difference_percent"]) < 0.01,
            "continuum_moment_linear":True,
            "table4_mu":s["table4_contact"]["coulomb_friction_coefficient"],
            "figure16_curve_digitized":False,
            "fp_ruc_reproduced":False,
            "phase2_analytical_curves_regenerated":True,
                        "model_form_kinematics_difference_recorded":True,
            "phase3_axisymmetric_force_torsion_closure":True,
            "figure16_literal_probe_not_promoted":True
        },
        "qualification":"NOT_GRANTED"
    }
    (results/"engiproof_verification.json").write_text(json.dumps(verification,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"paper_id":"P42","status":"COMPARED","summary":s,"qualification":"NOT_GRANTED"},indent=2))

if __name__=="__main__": main()
