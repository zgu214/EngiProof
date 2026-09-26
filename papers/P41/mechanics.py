"""P41 source-bounded axial load-sharing mechanics.

Lengths may use any consistent unit for geometry. Areas are returned in m^2
when diameters/thicknesses are supplied in metres. Forces/stiffnesses use SI.

The selected published chain is:
  Table 1 -> steel areas / EA -> Eq. (6) / Eq. (7) -> Eq. (8)

No global-buckling FE model is reproduced here.
"""
from __future__ import annotations

import math


def _positive(name: str, value: float) -> float:
    x=float(value)
    if not math.isfinite(x) or x <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return x


def steel_area_m2(D_m: float, t_m: float) -> float:
    """Independent annulus-area calculation from Table 1 OD and wall thickness."""
    D=_positive("D_m",D_m); t=_positive("t_m",t_m)
    if 2.0*t >= D:
        raise ValueError("wall thickness must be less than radius")
    return float(math.pi/4.0*(D**2-(D-2.0*t)**2))


def axial_stiffness_N(D_m: float, t_m: float, E_Pa: float) -> float:
    """Independent EA from Table 1 geometry and Young's modulus."""
    return float(steel_area_m2(D_m,t_m)*_positive("E_Pa",E_Pa))


def equation6_deltaS_inner_N_per_m(fS_N_per_m: float, EA_inner_N: float, EA_outer_N: float) -> float:
    """Published Eq. (6): inner-pipe share of available soil-friction increment."""
    f=_positive("fS_N_per_m",fS_N_per_m); ei=_positive("EA_inner_N",EA_inner_N); eo=_positive("EA_outer_N",EA_outer_N)
    return float(f*ei/(ei+eo))


def equation7_deltaS_outer_N_per_m(fS_N_per_m: float, EA_inner_N: float, EA_outer_N: float) -> float:
    """Published Eq. (7): outer-pipe share of available soil-friction increment."""
    f=_positive("fS_N_per_m",fS_N_per_m); ei=_positive("EA_inner_N",EA_inner_N); eo=_positive("EA_outer_N",EA_outer_N)
    return float(f*eo/(ei+eo))


def equation8_total_deltaS_N_per_m(deltaS_inner_N_per_m: float, deltaS_outer_N_per_m: float) -> float:
    """Published Eq. (8): total effective-force increment equals sum of pipe shares."""
    di=float(deltaS_inner_N_per_m); do=float(deltaS_outer_N_per_m)
    if not math.isfinite(di) or not math.isfinite(do):
        raise ValueError("force increments must be finite")
    return float(di+do)


def independent_load_share_from_geometry(
    fS_N_per_m: float,
    D_inner_m: float,
    t_inner_m: float,
    E_inner_Pa: float,
    D_outer_m: float,
    t_outer_m: float,
    E_outer_Pa: float,
) -> dict:
    """Independent Table-1 -> area -> EA -> Eqs. (6)-(8) calculation."""
    Ai=steel_area_m2(D_inner_m,t_inner_m)
    Ao=steel_area_m2(D_outer_m,t_outer_m)
    EAi=Ai*_positive("E_inner_Pa",E_inner_Pa)
    EAo=Ao*_positive("E_outer_Pa",E_outer_Pa)
    dSi=equation6_deltaS_inner_N_per_m(fS_N_per_m,EAi,EAo)
    dSo=equation7_deltaS_outer_N_per_m(fS_N_per_m,EAi,EAo)
    return {
        "A_inner_m2":Ai,
        "A_outer_m2":Ao,
        "EA_inner_N":EAi,
        "EA_outer_N":EAo,
        "deltaS_inner_N_per_m":dSi,
        "deltaS_outer_N_per_m":dSo,
        "deltaS_total_N_per_m":equation8_total_deltaS_N_per_m(dSi,dSo),
    }

def equation9_required_internal_friction_N_per_m(
    fS_N_per_m: float,
    EA_inner_N: float,
    EA_outer_N: float,
    gamma_f: float = 1.0,
) -> float:
    """Published Eq. (9): internal axial-friction requirement for full bonding."""
    f=_positive("fS_N_per_m",fS_N_per_m)
    ei=_positive("EA_inner_N",EA_inner_N)
    eo=_positive("EA_outer_N",EA_outer_N)
    g=_positive("gamma_f",gamma_f)
    return float(g*f*ei/(ei+eo))


def classify_axial_bonding(fI_N_per_m: float, f_required_N_per_m: float) -> str:
    """Classify no-friction / partial-bonding / full-bonding response."""
    fi=float(fI_N_per_m)
    req=_positive("f_required_N_per_m",f_required_N_per_m)
    if not math.isfinite(fi) or fi < 0.0:
        raise ValueError("fI_N_per_m must be finite and non-negative")
    if abs(fi) <= 1e-15:
        return "NO_FRICTION"
    if fi < req:
        return "PARTIAL_BONDING"
    return "FULL_BONDING"


def dry_internal_friction_N_per_m(dry_weight_N_per_m: float, friction_coefficient: float) -> float:
    """Simple dry-weight friction model described in P41."""
    w=_positive("dry_weight_N_per_m",dry_weight_N_per_m)
    eta=float(friction_coefficient)
    if not math.isfinite(eta) or eta < 0.0:
        raise ValueError("friction_coefficient must be finite and non-negative")
    return float(w*eta)


def equation10_end_expansion_m(
    S0_total_N: float,
    fS_N_per_m: float,
    EA_inner_N: float,
    EA_outer_N: float,
) -> float:
    """Published Eq. (10): full-bonding end expansion."""
    s=float(S0_total_N)
    if not math.isfinite(s):
        raise ValueError("S0_total_N must be finite")
    f=_positive("fS_N_per_m",fS_N_per_m)
    ei=_positive("EA_inner_N",EA_inner_N)
    eo=_positive("EA_outer_N",EA_outer_N)
    return float((s*s)/(2.0*f*(ei+eo)))


def equation10_required_S0_N(
    end_expansion_m: float,
    fS_N_per_m: float,
    EA_inner_N: float,
    EA_outer_N: float,
) -> float:
    """Independent inversion of Eq. (10) for diagnostic use only."""
    delta=_positive("end_expansion_m",end_expansion_m)
    f=_positive("fS_N_per_m",fS_N_per_m)
    ei=_positive("EA_inner_N",EA_inner_N)
    eo=_positive("EA_outer_N",EA_outer_N)
    return float(math.sqrt(2.0*delta*f*(ei+eo)))



def second_moment_annulus_m4(D_m: float, t_m: float) -> float:
    D=_positive("D_m",D_m); t=_positive("t_m",t_m)
    d=D-2.0*t
    if d <= 0.0:
        raise ValueError("wall thickness must be less than radius")
    return float(math.pi/64.0*(D**4-d**4))


def bending_stiffness_Nm2(D_m: float, t_m: float, E_Pa: float) -> float:
    return float(_positive("E_Pa",E_Pa)*second_moment_annulus_m4(D_m,t_m))


def equation14_design_moment(M_f: float, gamma_f: float, gamma_C: float) -> float:
    M=float(M_f); gf=float(gamma_f); gc=float(gamma_C)
    if not all(math.isfinite(x) for x in (M,gf,gc)):
        raise ValueError("M_f, gamma_f and gamma_C must be finite")
    if gf <= 0.0 or gc <= 0.0:
        raise ValueError("gamma_f and gamma_C must be positive")
    return float(M*gf*gc)
