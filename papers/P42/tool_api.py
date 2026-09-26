"""Callable source-bounded tools for EngiProof study P42."""
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location("p42_mechanics",HERE/"mechanics.py")
_m=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)

def balanced_pitch_L2_mm(L1_mm: float, n1: float, n2: float) -> float:
    return _m.balanced_pitch_L2_mm(L1_mm,n1,n2)

def equation42_continuum_moment_kNm(kappa_per_m: float, E_MPa: float, r_mid_mm: float, t_mm: float) -> float:
    return _m.equation42_continuum_moment_Nm(kappa_per_m,E_MPa*1e6,r_mid_mm/1000.0,t_mm/1000.0)/1000.0

def equation43_total_moment_kNm(M0_cont_kNm: float, M1_f_kNm: float, M2_f_kNm: float, M3_cont_kNm: float) -> float:
    return _m.equation43_total_moment_Nm(M0_cont_kNm,M1_f_kNm,M2_f_kNm,M3_cont_kNm)

def contact_properties() -> dict:
    return json.loads((HERE/"reference"/"table4_contact.json").read_text(encoding="utf-8"))

def phase1_continuum_summary() -> dict:
    geom=json.loads((HERE/"inputs"/"table1_geometry.json").read_text(encoding="utf-8"))
    mat=json.loads((HERE/"inputs"/"table3_materials.json").read_text(encoding="utf-8"))
    fig=json.loads((HERE/"reference"/"figure16_source_review.json").read_text(encoding="utf-8"))

    a1=geom["layers"]["tensile_armor_1"]
    a2=geom["layers"]["tensile_armor_2"]
    L2_calc=_m.balanced_pitch_L2_mm(a1["pitch_length_mm"],a1["wire_count"],a2["wire_count"])

    radii=_m.nominal_mid_radii_m(
        geom["bore_diameter_mm"],
        geom["layers"]["core"]["thickness_mm"],
        a1["wire_thickness_mm"],a2["wire_thickness_mm"],
        geom["layers"]["outer_sheath"]["thickness_mm"],
    )
    t0=geom["layers"]["core"]["thickness_mm"]/1000.0
    t3=geom["layers"]["outer_sheath"]["thickness_mm"]/1000.0
    E0=mat["core"]["E33_MPa"]*1e6
    E3=mat["outer_sheath"]["E_MPa"]*1e6
    I0=_m.annulus_I_from_mid_radius_m4(radii["core_mid_radius_m"],t0)
    I3=_m.annulus_I_from_mid_radius_m4(radii["outer_sheath_mid_radius_m"],t3)
    EI0=E0*I0; EI3=E3*I3
    curve=[]
    for k in (0.0,0.02,0.04,0.06,0.08,0.10):
        M0=_m.equation42_continuum_moment_Nm(k,E0,radii["core_mid_radius_m"],t0)
        M3=_m.equation42_continuum_moment_Nm(k,E3,radii["outer_sheath_mid_radius_m"],t3)
        curve.append({"kappa_per_m":k,"M0_cont_kNm":M0/1000.0,"M3_cont_kNm":M3/1000.0,"M_cont_total_kNm":(M0+M3)/1000.0})
    return {
        "table1_pitch_balance":{
            "published_L2_mm":a2["pitch_length_mm"],
            "calculated_L2_mm":L2_calc,
            "difference_mm":L2_calc-a2["pitch_length_mm"],
            "relative_difference_percent":100.0*(L2_calc-a2["pitch_length_mm"])/a2["pitch_length_mm"],
        },
        "equation42_continuum":{
            "core_mid_radius_mm":1000.0*radii["core_mid_radius_m"],
            "outer_sheath_mid_radius_mm":1000.0*radii["outer_sheath_mid_radius_m"],
            "I_core_m4":I0,"I_outer_sheath_m4":I3,
            "EI_core_Nm2":EI0,"EI_outer_sheath_Nm2":EI3,
            "EI_total_Nm2":EI0+EI3,
            "curve":curve,
        },
        "table4_contact":contact_properties(),
        "figure16_source_review":fig,
        "evidence_boundary":"Table 1 pitch balance and nominal radii/EI arithmetic are INDEPENDENT. Eqs. (42)-(43) are PUBLISHED methods. Figure 16 is source-reviewed only; no graphical digitization or FE reproduction is claimed."
    }

def helix_lay_angle_deg(r_mm: float, pitch_mm: float) -> float:
    return math.degrees(_m.helix_lay_angle_rad(r_mm/1000.0,pitch_mm/1000.0))


def equation31_preslip_stress_MPa(nu_deg: float, E_MPa: float, r_mm: float, alpha_deg: float, kappa_G_per_m: float) -> float:
    return _m.equation31_preslip_stress_Pa(
        math.radians(nu_deg),E_MPa*1e6,r_mm/1000.0,math.radians(alpha_deg),kappa_G_per_m
    )/1e6


def equation32_critical_curvature_per_m(nu_deg: float, mu_i: float, p_i_MPa: float, mu_o: float, p_o_MPa: float, E_MPa: float, t_mm: float, alpha_deg: float) -> float:
    return _m.equation32_critical_curvature_per_m(
        math.radians(nu_deg),mu_i,p_i_MPa*1e6,mu_o,p_o_MPa*1e6,E_MPa*1e6,t_mm/1000.0,math.radians(alpha_deg)
    )


def equation33_transition_angle_deg(kappa_G_per_m: float, mu_i: float, p_i_MPa: float, mu_o: float, p_o_MPa: float, E_MPa: float, t_mm: float, alpha_deg: float) -> float:
    return math.degrees(_m.equation33_transition_angle_rad(
        kappa_G_per_m,mu_i,p_i_MPa*1e6,mu_o,p_o_MPa*1e6,E_MPa*1e6,t_mm/1000.0,math.radians(alpha_deg)
    ))


def equation34_slip_stress_MPa(nu_deg: float, mu_i: float, p_i_MPa: float, mu_o: float, p_o_MPa: float, r_mm: float, t_mm: float, alpha_deg: float) -> float:
    return _m.equation34_slip_stress_Pa(
        math.radians(nu_deg),mu_i,p_i_MPa*1e6,mu_o,p_o_MPa*1e6,r_mm/1000.0,t_mm/1000.0,math.radians(alpha_deg)
    )/1e6


def equation35_stick_stress_MPa(nu_deg: float, nu_star_deg: float, E_MPa: float, r_mm: float, alpha_deg: float, kappa_G_per_m: float, mu_i: float, p_i_MPa: float, mu_o: float, p_o_MPa: float, t_mm: float) -> float:
    return _m.equation35_stick_stress_Pa(
        math.radians(nu_deg),math.radians(nu_star_deg),E_MPa*1e6,r_mm/1000.0,math.radians(alpha_deg),kappa_G_per_m,
        mu_i,p_i_MPa*1e6,mu_o,p_o_MPa*1e6,t_mm/1000.0
    )/1e6


def phase2_analytical_stress_summary() -> dict:
    geom=json.loads((HERE/"inputs"/"table1_geometry.json").read_text(encoding="utf-8"))
    mat=json.loads((HERE/"inputs"/"table3_materials.json").read_text(encoding="utf-8"))
    src=json.loads((HERE/"reference"/"phase2_source_review.json").read_text(encoding="utf-8"))
    rb=geom["bore_diameter_mm"]/2000.0
    t0=geom["layers"]["core"]["thickness_mm"]/1000.0
    a1=geom["layers"]["tensile_armor_1"]; a2=geom["layers"]["tensile_armor_2"]
    t1=a1["wire_thickness_mm"]/1000.0; t2=a2["wire_thickness_mm"]/1000.0
    r1=rb+t0+t1/2.0
    r2=rb+t0+t1+t2/2.0
    alpha1=_m.helix_lay_angle_rad(r1,a1["pitch_length_mm"]/1000.0)
    alpha2=_m.helix_lay_angle_rad(r2,a2["pitch_length_mm"]/1000.0)
    E=mat["tensile_armor"]["E_MPa"]*1e6
    w=a1["wire_width_mm"]/1000.0

    curves=[]
    for layer,r,alpha in ((1,r1,alpha1),(2,r2,alpha2)):
        for kappa in (0.01,0.02,0.04,0.06,0.08,0.10):
            for nu_deg in range(0,361,5):
                nu=math.radians(nu_deg)
                trans=_m.equation36_transverse_bending_stress_Pa(nu,E,alpha,kappa,w/2.0)/1e6
                normal=_m.equation37_normal_bending_stress_Pa(nu,E,alpha,kappa,t1/2.0)/1e6
                curves.append({
                    "layer":layer,"kappa_G_per_m":kappa,"nu_deg":nu_deg,
                    "transverse_analytical_MPa":trans,
                    "normal_analytical_MPa":normal
                })
    def amp(alpha,kappa):
        tr=abs(_m.equation36_transverse_bending_stress_Pa(math.pi/2,E,alpha,kappa,w/2.0))/1e6
        no=abs(_m.equation37_normal_bending_stress_Pa(0.0,E,alpha,kappa,t1/2.0))/1e6
        return tr,no
    tr1,no1=amp(alpha1,0.06); tr2,no2=amp(alpha2,0.06)
    return {
        "nominal_geometry":{
            "inner_armor_mid_radius_mm":r1*1000.0,
            "outer_armor_mid_radius_mm":r2*1000.0,
            "inner_lay_angle_deg":math.degrees(alpha1),
            "outer_lay_angle_deg":math.degrees(alpha2)
        },
        "analytical_amplitudes_at_kappa_0p06":{
            "inner_transverse_MPa":tr1,
            "outer_transverse_MPa":tr2,
            "inner_normal_MPa":no1,
            "outer_normal_MPa":no2
        },
        "figure21_23_model_form_check":{
            "analytical_Fz_dependence":"NONE_IN_EQS_36_39",
            "published_FP_RUC_Fz_dependence":"PRESENT",
            "classification":"MODEL_FORM_KINEMATICS_DIFFERENCE",
            "source_interpretation":"The paper attributes the difference to sliding interaction and wire-path/kinematic assumptions."
        },
        "curve_rows":curves,
        "source_review":src,
        "evidence_boundary":"Analytical curves are regenerated from PUBLISHED Eqs. (36)-(39) using source geometry/materials plus an INDEPENDENT helix-angle calculation. Eqs. (31)-(35) are callable with explicit contact-pressure inputs. FP-RUC curves are not digitized or reproduced."
    }

def phase3_axisymmetric_and_moment_summary() -> dict:
    geom=json.loads((HERE/"inputs"/"table1_geometry.json").read_text(encoding="utf-8"))
    mat=json.loads((HERE/"inputs"/"table3_materials.json").read_text(encoding="utf-8"))
    contact=json.loads((HERE/"reference"/"table4_contact.json").read_text(encoding="utf-8"))
    review=json.loads((HERE/"reference"/"phase3_source_review.json").read_text(encoding="utf-8"))

    rb=geom["bore_diameter_mm"]/2000.0
    t0=geom["layers"]["core"]["thickness_mm"]/1000.0
    t1=geom["layers"]["tensile_armor_1"]["wire_thickness_mm"]/1000.0
    t2=geom["layers"]["tensile_armor_2"]["wire_thickness_mm"]/1000.0
    t3=geom["layers"]["outer_sheath"]["thickness_mm"]/1000.0
    w1=geom["layers"]["tensile_armor_1"]["wire_width_mm"]/1000.0
    w2=geom["layers"]["tensile_armor_2"]["wire_width_mm"]/1000.0
    a1=t1*w1; a2=t2*w2
    ri1=rb+t0; ro1=ri1+t1; r1=(ri1+ro1)/2.0
    ri2=ro1; ro2=ri2+t2; r2=(ri2+ro2)/2.0
    ri3=ro2; ro3=ri3+t3

    al1=_m.helix_lay_angle_rad(r1,geom["layers"]["tensile_armor_1"]["pitch_length_mm"]/1000.0)
    al2=-_m.helix_lay_angle_rad(r2,geom["layers"]["tensile_armor_2"]["pitch_length_mm"]/1000.0)
    E=mat["tensile_armor"]["E_MPa"]*1e6
    n1=geom["layers"]["tensile_armor_1"]["wire_count"]
    n2=geom["layers"]["tensile_armor_2"]["wire_count"]
    mu=contact["coulomb_friction_coefficient"]

    base_layers=[
        {"name":"inner","n":n1,"area_m2":a1,"E_Pa":E,"r_m":r1,"alpha_rad":al1,
         "r_i_m":ri1,"r_o_m":ro1,"wire_width_m":w1},
        {"name":"outer","n":n2,"area_m2":a2,"E_Pa":E,"r_m":r2,"alpha_rad":al2,
         "r_i_m":ri2,"r_o_m":ro2,"wire_width_m":w2},
    ]
    outer_boundary={
        "P_i_next_Pa":0.0,"P_o_next_Pa":0.0,
        "r_i_next_m":ri3,"r_o_next_m":ro3
    }

    tension_cases=[]
    figure16_rows=[]
    for Fz_kN in (50,100,500,1000,1500,2000,2500,3000):
        ax=_m.solve_axisymmetric_two_layer(Fz_kN*1000.0,0.0,base_layers)
        # Eq. 27-30 recurrence is outer-to-inner.
        outer=dict(base_layers[1]); outer["sigma_AS_Pa"]=ax["sigma_AS_Pa"][1]
        inner=dict(base_layers[0]); inner["sigma_AS_Pa"]=ax["sigma_AS_Pa"][0]
        chain=_m.literal_eq27_30_contact_chain([outer,inner],outer_boundary)
        by_name={x["name"]:x for x in chain}

        tension_cases.append({
            "Fz_kN":Fz_kN,
            "axial_strain":ax["axial_strain"],
            "twist_rate_deg_per_m":math.degrees(ax["twist_rate_rad_per_m"]),
            "sigma_inner_MPa":ax["sigma_AS_Pa"][0]/1e6,
            "sigma_outer_MPa":ax["sigma_AS_Pa"][1]/1e6,
            "force_residual_N":ax["force_residual_N"],
            "torque_residual_Nm":ax["torque_residual_Nm"],
            "literal_contact_inner":{"p_i_MPa":by_name["inner"]["p_i_Pa"]/1e6,"p_o_MPa":by_name["inner"]["p_o_Pa"]/1e6},
            "literal_contact_outer":{"p_i_MPa":by_name["outer"]["p_i_Pa"]/1e6,"p_o_MPa":by_name["outer"]["p_o_Pa"]/1e6},
        })

        for kappa in [round(i*0.002,3) for i in range(0,51)]:
            M1=_m.equation41_armor_moment_Nm(
                kappa,E,r1,t1,al1,by_name["inner"]["fill_factor"],
                mu,by_name["inner"]["p_i_Pa"],mu,by_name["inner"]["p_o_Pa"]
            )
            M2=_m.equation41_armor_moment_Nm(
                kappa,E,r2,t2,abs(al2),by_name["outer"]["fill_factor"],
                mu,by_name["outer"]["p_i_Pa"],mu,by_name["outer"]["p_o_Pa"]
            )
            M0=_m.equation42_continuum_moment_Nm(
                kappa,mat["core"]["E33_MPa"]*1e6,rb+t0/2.0,t0
            )
            M3=_m.equation42_continuum_moment_Nm(
                kappa,mat["outer_sheath"]["E_MPa"]*1e6,ro2+t3/2.0,t3
            )
            Mtot=M0+M1["moment_Nm"]+M2["moment_Nm"]+M3
            figure16_rows.append({
                "Fz_kN":Fz_kN,"kappa_G_per_m":kappa,
                "M_inner_armor_kNm":M1["moment_Nm"]/1000.0,
                "M_outer_armor_kNm":M2["moment_Nm"]/1000.0,
                "M_continuum_kNm":(M0+M3)/1000.0,
                "M_total_literal_kNm":Mtot/1000.0,
                "inner_nu_star_deg":M1["nu_star_deg"],
                "outer_nu_star_deg":M2["nu_star_deg"],
            })

    end_rows=[x for x in figure16_rows if abs(x["kappa_G_per_m"]-0.1)<1e-12]
    max_end=max(x["M_total_literal_kNm"] for x in end_rows)
    source_axis_max=review["figure16_visual_scale"]["large_curvature_axis_moment_max_kNm"]

    return {
        "axisymmetric_equations_24_26":{
            "status":"REPRODUCED_EQUILIBRIUM_CHAIN",
            "cases":tension_cases,
            "source_comparison_note":"The calculated stress/strain/twist trends are linear in Fz and are consistent with the published Figures 12-14. No point digitization is used here."
        },
        "contact_equations_27_30":{
            "status":"CONDITIONAL_IMPLEMENTATION_CONVENTION",
            "boundary":review["literal_reconstruction_boundary"],
            "note":"The recursion is implemented literally with explicit zero outer nominal-pressure boundary. This convention is not silently promoted as the unique source implementation."
        },
        "equation41_figure16_probe":{
            "status":"NOT_REPRODUCED_SOURCE_IMPLEMENTATION_GAP",
            "rows":figure16_rows,
            "literal_max_at_kappa_0p1_kNm":max_end,
            "source_plot_axis_max_kNm":source_axis_max,
            "exceeds_source_plot_axis":max_end > source_axis_max,
            "interpretation":"The literal Eqs.27-30 boundary/mapping convention combined with Eq.41 does not close against the published Figure 16 scale at high tension. Inputs are not tuned. The gap is retained as an implementation/provenance ambiguity, not classified as a paper error."
        },
        "evidence_boundary":"Eqs.24-26 are independently solved with exact force/torsion closure. Eqs.27-30 and Eq.41 are callable and exercised under an explicit boundary convention. Figure16 is not claimed reproduced because the source implementation convention does not close without additional provenance.",
        "qualification":"NOT_GRANTED"
    }

