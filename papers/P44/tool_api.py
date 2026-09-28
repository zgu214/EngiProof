from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("p44_mechanics",HERE/"mechanics.py")
_m=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_m)


def drillpipe_section_properties():
    t=json.loads((HERE/"reference"/"table1_drillpipe.json").read_text(encoding="utf-8"))
    return _m.annulus_section_properties_from_diameters(t["OD_in"],t["ID_in"])


def equation1_contact_force_lbf(length_ft: float, unit_weight_lb_per_ft: float, floating_factor: float, inclination_deg: float):
    return _m.equation1_contact_force_lbf(length_ft,unit_weight_lb_per_ft,floating_factor,inclination_deg)


def contact_stiffness_state(normal_displacement_ft: float, gap_ft: float, K1_lbf_per_ft: float=1.0e6):
    return _m.contact_stiffness_state(normal_displacement_ft,gap_ft,K1_lbf_per_ft)


def phase1_contact_validation_summary() -> dict:
    t1=json.loads((HERE/"reference"/"table1_drillpipe.json").read_text(encoding="utf-8"))
    eq=json.loads((HERE/"reference"/"equation1_validation.json").read_text(encoding="utf-8"))
    cm=json.loads((HERE/"reference"/"contact_model.json").read_text(encoding="utf-8"))
    td=json.loads((HERE/"reference"/"time_discretization_and_figure_labels.json").read_text(encoding="utf-8"))
    fr=json.loads((HERE/"reference"/"figures7_9_source_review.json").read_text(encoding="utf-8"))

    section=_m.annulus_section_properties_from_diameters(t1["OD_in"],t1["ID_in"])
    printed=_m.equation1_printed_arithmetic_lbf(
        eq["length_ft"],eq["unit_weight_lb_per_ft"],eq["floating_factor"],eq["published_sin60_used"]
    )
    exact=_m.equation1_contact_force_lbf(
        eq["length_ft"],eq["unit_weight_lb_per_ft"],eq["floating_factor"],eq["inclination_deg"]
    )
    dt=_m.time_slice_spacing_s(td["wave_period_s"],td["time_slice_count"])
    penetration=_m.penalty_penetration_in(eq["published_FEM_force_lb"],cm["K1_lbf_per_ft"])

    return {
        "table1_independent_geometry_check":{
            "published_cross_area_ft2":t1["cross_area_ft2"],
            "computed_cross_area_ft2":section["area_ft2"],
            "cross_area_relative_difference_percent":(section["area_ft2"]-t1["cross_area_ft2"])/t1["cross_area_ft2"]*100.0,
            "published_I_ft4":t1["moment_of_inertia_ft4"],
            "computed_I_ft4":section["I_ft4"],
            "I_relative_difference_percent":(section["I_ft4"]-t1["moment_of_inertia_ft4"])/t1["moment_of_inertia_ft4"]*100.0,
        },
        "equation1_validation":{
            "published_equilibrium_force_lb":eq["published_equilibrium_force_lb"],
            "printed_arithmetic_reproduction_lb":printed,
            "printed_arithmetic_difference_lb":printed-eq["published_equilibrium_force_lb"],
            "exact_sine60_independent_lb":exact,
            "published_FEM_force_lb":eq["published_FEM_force_lb"],
            "exact_vs_FEM_difference_lb":exact-eq["published_FEM_force_lb"],
            "exact_vs_FEM_relative_difference_percent":(exact-eq["published_FEM_force_lb"])/eq["published_FEM_force_lb"]*100.0,
        },
        "time_discretization_check":{
            "wave_period_s":td["wave_period_s"],
            "slice_count":td["time_slice_count"],
            "computed_spacing_s":dt,
            "published_spacing_s":td["published_slice_spacing_s"],
        },
        "contact_penalty_diagnostic":{
            "published_K1_lbf_per_ft":cm["K1_lbf_per_ft"],
            "reference_force_lb":eq["published_FEM_force_lb"],
            "elastic_penetration_in_at_reference_force":penetration,
            "interpretation":"Independent stiffness-scale diagnostic only; not a reproduction of the unpublished nonlinear contact iteration."
        },
        "P44_D001_probe":{
            "classification":"SOURCE_FIGURE_TEXT_MISMATCH",
            "paragraph_times_s":td["paragraph_times_for_figures7_8_s"],
            "figure7_caption_time_s":td["figure7_caption_time_s"],
            "figure8_caption_time_s":td["figure8_caption_time_s"],
            "figure2_times_s":td["figure2_times_s"],
            "observation":"The paragraph introducing Figures 7 and 8 states 4.06 s and 2.32 s, while the figure captions state 0.58 s and 1.74 s. Figure 2 also uses 0.58 s and 1.74 s. EngiProof preserves both source statements without deciding which is intended."
        },
        "source_review":fr,
        "evidence_boundary":"Equation (1), table values, K1 and figure labels are PUBLISHED. Section-property arithmetic, exact-trigonometric Eq1 calculation, time-step arithmetic and penalty-penetration scale are INDEPENDENT. Full nonlinear FE contact-force profiles are not reproduced because the paper does not supply the complete well/riser geometry and time-dependent wall-displacement dataset.",
        "qualification":"NOT_GRANTED"
    }
