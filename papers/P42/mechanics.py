"""Source-bounded mechanics for EngiProof P42 Phase 1."""
from __future__ import annotations
import math

def _positive(name: str, value: float) -> float:
    x=float(value)
    if not math.isfinite(x) or x <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return x

def balanced_pitch_L2_mm(L1_mm: float, n1: float, n2: float) -> float:
    L1=_positive("L1_mm",L1_mm)
    n1=_positive("n1",n1); n2=_positive("n2",n2)
    return L1*n2/n1

def annulus_I_from_mid_radius_m4(r_mid_m: float, t_m: float) -> float:
    r=_positive("r_mid_m",r_mid_m); t=_positive("t_m",t_m)
    ri=r-t/2.0; ro=r+t/2.0
    if ri < 0.0:
        raise ValueError("inner radius must be non-negative")
    return math.pi/4.0*(ro**4-ri**4)

def equation42_continuum_moment_Nm(kappa_per_m: float, E_Pa: float, r_mid_m: float, t_m: float) -> float:
    k=float(kappa_per_m)
    if not math.isfinite(k):
        raise ValueError("kappa_per_m must be finite")
    E=_positive("E_Pa",E_Pa)
    return k*E*annulus_I_from_mid_radius_m4(r_mid_m,t_m)

def equation43_total_moment_Nm(M0_cont_Nm: float, M1_f_Nm: float, M2_f_Nm: float, M3_cont_Nm: float) -> float:
    vals=[float(x) for x in (M0_cont_Nm,M1_f_Nm,M2_f_Nm,M3_cont_Nm)]
    if not all(math.isfinite(x) for x in vals):
        raise ValueError("moment contributions must be finite")
    return sum(vals)

def nominal_mid_radii_m(bore_diameter_mm: float, t0_mm: float, t1_mm: float, t2_mm: float, t3_mm: float) -> dict:
    rb=_positive("bore_diameter_mm",bore_diameter_mm)/2000.0
    t0=_positive("t0_mm",t0_mm)/1000.0
    t1=_positive("t1_mm",t1_mm)/1000.0
    t2=_positive("t2_mm",t2_mm)/1000.0
    t3=_positive("t3_mm",t3_mm)/1000.0
    return {
        "core_mid_radius_m":rb+t0/2.0,
        "outer_sheath_mid_radius_m":rb+t0+t1+t2+t3/2.0,
    }

def helix_lay_angle_rad(r_m: float, pitch_m: float) -> float:
    """Independent helix-geometry relation: tan(alpha)=2*pi*r/L."""
    r=_positive("r_m",r_m); L=_positive("pitch_m",pitch_m)
    return math.atan2(2.0*math.pi*r,L)


def equation31_preslip_stress_Pa(
    nu_rad: float,
    E_Pa: float,
    r_m: float,
    alpha_rad: float,
    kappa_G_per_m: float,
) -> float:
    """P42 Eq. (31): pre-slip friction stress."""
    E=_positive("E_Pa",E_Pa); r=_positive("r_m",r_m)
    a=float(alpha_rad); nu=float(nu_rad); k=float(kappa_G_per_m)
    if not all(math.isfinite(x) for x in (a,nu,k)):
        raise ValueError("alpha, nu and kappa must be finite")
    return E*r*k*(math.cos(a)**2)*math.cos(nu)


def equation32_critical_curvature_per_m(
    nu_rad: float,
    mu_i: float,
    p_i_Pa: float,
    mu_o: float,
    p_o_Pa: float,
    E_Pa: float,
    t_m: float,
    alpha_rad: float,
) -> float:
    """P42 Eq. (32): critical curvature at circumferential angle nu."""
    E=_positive("E_Pa",E_Pa); t=_positive("t_m",t_m)
    vals=[float(mu_i),float(p_i_Pa),float(mu_o),float(p_o_Pa),float(alpha_rad),float(nu_rad)]
    if not all(math.isfinite(x) for x in vals):
        raise ValueError("inputs must be finite")
    if vals[0] < 0 or vals[2] < 0 or vals[1] < 0 or vals[3] < 0:
        raise ValueError("friction coefficients and pressures must be non-negative")
    denom=E*t*(math.cos(vals[4])**2)*math.sin(vals[4])*math.sin(vals[5])
    if abs(denom) <= 1e-18:
        return math.inf
    return (vals[0]*vals[1]+vals[2]*vals[3])/denom


def equation33_transition_angle_rad(
    kappa_G_per_m: float,
    mu_i: float,
    p_i_Pa: float,
    mu_o: float,
    p_o_Pa: float,
    E_Pa: float,
    t_m: float,
    alpha_rad: float,
) -> float:
    """P42 Eq. (33), first-quadrant transition angle nu*."""
    k=_positive("kappa_G_per_m",kappa_G_per_m)
    E=_positive("E_Pa",E_Pa); t=_positive("t_m",t_m)
    a=float(alpha_rad)
    cap=float(mu_i)*float(p_i_Pa)+float(mu_o)*float(p_o_Pa)
    denom=E*t*(math.cos(a)**2)*math.sin(a)*k
    if denom <= 0:
        raise ValueError("Eq. (33) denominator must be positive")
    x=cap/denom
    if x < 0 or x > 1:
        raise ValueError("No real transition angle for the supplied parameters; require 0 <= argument <= 1")
    return math.asin(x)


def equation34_slip_stress_Pa(
    nu_rad: float,
    mu_i: float,
    p_i_Pa: float,
    mu_o: float,
    p_o_Pa: float,
    r_m: float,
    t_m: float,
    alpha_rad: float,
) -> float:
    """P42 Eq. (34), first-quadrant slip-region friction stress."""
    r=_positive("r_m",r_m); t=_positive("t_m",t_m)
    a=float(alpha_rad); nu=float(nu_rad)
    cap=float(mu_i)*float(p_i_Pa)+float(mu_o)*float(p_o_Pa)
    return cap*r/(t*math.sin(a))*(math.pi/2.0-nu)


def equation35_stick_stress_Pa(
    nu_rad: float,
    nu_star_rad: float,
    E_Pa: float,
    r_m: float,
    alpha_rad: float,
    kappa_G_per_m: float,
    mu_i: float,
    p_i_Pa: float,
    mu_o: float,
    p_o_Pa: float,
    t_m: float,
) -> float:
    """P42 Eq. (35), first-quadrant stick-region friction stress."""
    E=_positive("E_Pa",E_Pa); r=_positive("r_m",r_m); t=_positive("t_m",t_m)
    a=float(alpha_rad); nu=float(nu_rad); nus=float(nu_star_rad); k=float(kappa_G_per_m)
    cap=float(mu_i)*float(p_i_Pa)+float(mu_o)*float(p_o_Pa)
    return (
        E*r*k*(math.cos(a)**2)*(math.cos(nu)-math.cos(nus))
        + cap*r/(t*math.sin(a))*(math.pi/2.0-nus)
    )


def equation38_delta_kappa2_per_m(nu_rad: float, alpha_rad: float, kappa_G_per_m: float) -> float:
    """P42 Eq. (38): loxodromic transverse local curvature increment."""
    nu=float(nu_rad); a=float(alpha_rad); k=float(kappa_G_per_m)
    return -math.cos(a)*(1.0+math.sin(a)**2)*math.sin(nu)*k


def equation39_delta_kappa3_per_m(nu_rad: float, alpha_rad: float, kappa_G_per_m: float) -> float:
    """P42 Eq. (39): loxodromic normal local curvature increment."""
    nu=float(nu_rad); a=float(alpha_rad); k=float(kappa_G_per_m)
    return (math.cos(a)**4)*math.cos(nu)*k


def equation36_transverse_bending_stress_Pa(
    nu_rad: float,
    E_Pa: float,
    alpha_rad: float,
    kappa_G_per_m: float,
    X3_m: float,
) -> float:
    """P42 Eq. (36) evaluated with Eq. (38)."""
    E=_positive("E_Pa",E_Pa)
    return -E*equation38_delta_kappa2_per_m(nu_rad,alpha_rad,kappa_G_per_m)*float(X3_m)


def equation37_normal_bending_stress_Pa(
    nu_rad: float,
    E_Pa: float,
    alpha_rad: float,
    kappa_G_per_m: float,
    X2_m: float,
) -> float:
    """P42 Eq. (37) evaluated with Eq. (39)."""
    E=_positive("E_Pa",E_Pa)
    return -E*equation39_delta_kappa3_per_m(nu_rad,alpha_rad,kappa_G_per_m)*float(X2_m)

def solve_axisymmetric_two_layer(
    Fz_N: float,
    M_Nm: float,
    layers: list[dict],
) -> dict:
    """Solve P42 Eqs. (24)-(26) for two counter-wound armor layers.

    Each layer dict requires:
      n, area_m2, E_Pa, r_m, alpha_rad

    alpha_rad is signed so opposite winding directions are represented.
    Unknowns are axial pipe strain eps=DeltaL/L and twist rate tau=DeltaTheta/L.
    """
    if len(layers) != 2:
        raise ValueError("This bounded P42 implementation requires exactly two armor layers")
    F=float(Fz_N); M=float(M_Nm)
    if not math.isfinite(F) or not math.isfinite(M):
        raise ValueError("Fz_N and M_Nm must be finite")

    A11=A12=A21=A22=0.0
    for layer in layers:
        n=_positive("n",layer["n"])
        area=_positive("area_m2",layer["area_m2"])
        E=_positive("E_Pa",layer["E_Pa"])
        r=_positive("r_m",layer["r_m"])
        a=float(layer["alpha_rad"])
        if not math.isfinite(a):
            raise ValueError("alpha_rad must be finite")
        c=math.cos(a); s=math.sin(a)
        A11 += n*area*E*c**3
        A12 += n*area*E*r*s*c**2
        A21 += n*area*E*r*s*c**2
        A22 += n*area*E*r*r*s*s*c

    det=A11*A22-A12*A21
    if abs(det) <= 1e-30:
        raise ValueError("axisymmetric system is singular")
    eps=(F*A22-A12*M)/det
    tau=(A11*M-A21*F)/det

    stresses=[]
    force_sum=0.0
    torque_sum=0.0
    for layer in layers:
        n=float(layer["n"]); area=float(layer["area_m2"])
        E=float(layer["E_Pa"]); r=float(layer["r_m"]); a=float(layer["alpha_rad"])
        c=math.cos(a); s=math.sin(a)
        sigma=E*(c*c*eps+r*s*c*tau)
        stresses.append(sigma)
        force_sum += n*sigma*area*c
        torque_sum += n*sigma*area*s*r

    return {
        "axial_strain":float(eps),
        "twist_rate_rad_per_m":float(tau),
        "sigma_AS_Pa":[float(x) for x in stresses],
        "force_closure_N":float(force_sum),
        "torque_closure_Nm":float(torque_sum),
        "force_residual_N":float(force_sum-F),
        "torque_residual_Nm":float(torque_sum-M),
    }


def equation27_inner_layer_pressure_Pa(
    P_i_next_Pa: float,
    r_i_next_m: float,
    r_i_m: float,
    n: float,
    sigma_AS_Pa: float,
    area_m2: float,
    alpha_rad: float,
) -> float:
    """P42 Eq. (27), kept explicit so boundary conventions remain visible."""
    ri=_positive("r_i_m",r_i_m)
    rin=_positive("r_i_next_m",r_i_next_m)
    n=_positive("n",n); area=_positive("area_m2",area_m2)
    s=float(sigma_AS_Pa); a=float(alpha_rad)
    return float(
        float(P_i_next_Pa)*rin/ri
        + n*s*area*math.sin(a)*math.tan(a)/(2.0*math.pi*ri*ri)
    )


def equation28_outer_layer_pressure_Pa(
    P_o_next_Pa: float,
    r_o_next_m: float,
    r_o_m: float,
    n: float,
    sigma_AS_Pa: float,
    area_m2: float,
    alpha_rad: float,
) -> float:
    """P42 Eq. (28), kept explicit so boundary conventions remain visible."""
    ro=_positive("r_o_m",r_o_m)
    ron=_positive("r_o_next_m",r_o_next_m)
    n=_positive("n",n); area=_positive("area_m2",area_m2)
    s=float(sigma_AS_Pa); a=float(alpha_rad)
    return float(
        float(P_o_next_Pa)*ron/ro
        + n*s*area*math.sin(a)*math.tan(a)/(2.0*math.pi*ro*ro)
    )


def equation29_fill_factor(
    n: float,
    wire_width_m: float,
    r_m: float,
    alpha_rad: float,
) -> float:
    """P42 Eq. (29)."""
    n=_positive("n",n); w=_positive("wire_width_m",wire_width_m); r=_positive("r_m",r_m)
    c=math.cos(float(alpha_rad))
    if c <= 0.0:
        raise ValueError("cos(alpha) must be positive for the present armor geometry")
    return float(n*w/(2.0*math.pi*r*c))


def equation30_wire_contact_pressure_Pa(P_layer_Pa: float, fill_factor: float) -> float:
    """P42 Eq. (30): local wire pressure from nominal layer pressure."""
    ff=_positive("fill_factor",fill_factor)
    return float(P_layer_Pa)/ff


def literal_eq27_30_contact_chain(
    layers_outer_to_inner: list[dict],
    outer_boundary: dict,
) -> list[dict]:
    """Literal Eqs. (27)-(30) recursion under an explicit boundary convention.

    This function deliberately exposes the boundary values instead of hiding them.
    It is a reproducibility probe, not an engineering qualification of the convention.
    """
    Pi_next=float(outer_boundary["P_i_next_Pa"])
    Po_next=float(outer_boundary["P_o_next_Pa"])
    ri_next=_positive("outer_boundary.r_i_next_m",outer_boundary["r_i_next_m"])
    ro_next=_positive("outer_boundary.r_o_next_m",outer_boundary["r_o_next_m"])
    out=[]
    for layer in layers_outer_to_inner:
        Pi=equation27_inner_layer_pressure_Pa(
            Pi_next,ri_next,layer["r_i_m"],layer["n"],layer["sigma_AS_Pa"],
            layer["area_m2"],layer["alpha_rad"]
        )
        Po=equation28_outer_layer_pressure_Pa(
            Po_next,ro_next,layer["r_o_m"],layer["n"],layer["sigma_AS_Pa"],
            layer["area_m2"],layer["alpha_rad"]
        )
        ff=equation29_fill_factor(layer["n"],layer["wire_width_m"],layer["r_m"],abs(layer["alpha_rad"]))
        pi=equation30_wire_contact_pressure_Pa(Pi,ff)
        po=equation30_wire_contact_pressure_Pa(Po,ff)
        row=dict(layer)
        row.update({
            "P_i_Pa":Pi,"P_o_Pa":Po,"fill_factor":ff,
            "p_i_Pa":pi,"p_o_Pa":po
        })
        out.append(row)
        Pi_next,Po_next=Pi,Po
        ri_next,ro_next=layer["r_i_m"],layer["r_o_m"]
    return out


def equation41_armor_moment_Nm(
    kappa_G_per_m: float,
    E_Pa: float,
    r_m: float,
    t_m: float,
    alpha_rad: float,
    fill_factor: float,
    mu_i: float,
    p_i_Pa: float,
    mu_o: float,
    p_o_Pa: float,
) -> dict:
    """P42 Eq. (41), including stick/slip transition from Eq. (33).

    For kappa <= kappa_cr(pi/2), nu_star=pi/2 corresponds to the all-stick limit.
    """
    k=float(kappa_G_per_m)
    if not math.isfinite(k) or k < 0.0:
        raise ValueError("kappa_G_per_m must be finite and non-negative")
    E=_positive("E_Pa",E_Pa); r=_positive("r_m",r_m); t=_positive("t_m",t_m)
    a=abs(float(alpha_rad)); ff=_positive("fill_factor",fill_factor)
    cap=float(mu_i)*float(p_i_Pa)+float(mu_o)*float(p_o_Pa)
    if cap < 0.0:
        raise ValueError("combined friction capacity must be non-negative")

    denom_base=E*t*(math.cos(a)**2)*math.sin(a)
    kcrit=cap/denom_base if denom_base>0.0 else math.inf
    if k == 0.0 or k <= kcrit:
        nu_star=math.pi/2.0
        regime="ALL_STICK"
    else:
        arg=max(0.0,min(1.0,cap/(denom_base*k)))
        nu_star=math.asin(arg)
        regime="PARTIAL_OR_FULL_SLIP"

    term1=(
        0.5*E*r**3*t*k*(math.cos(a)**2)
        *(math.sin(nu_star)*math.cos(nu_star)+nu_star)
    )
    term2=(cap*r**3/math.sin(a))*math.cos(nu_star)
    M=4.0*(math.cos(a)**2)*ff*(term1+term2)
    return {
        "moment_Nm":float(M),
        "nu_star_rad":float(nu_star),
        "nu_star_deg":float(math.degrees(nu_star)),
        "critical_curvature_per_m":float(kcrit),
        "regime":regime,
        "combined_friction_capacity_Pa":float(cap),
    }

