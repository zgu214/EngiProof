from __future__ import annotations

import math


def annulus_section_properties_from_diameters(OD_in: float, ID_in: float) -> dict:
    """Independent circular-section area and second moment."""
    Do=float(OD_in); Di=float(ID_in)
    if not (math.isfinite(Do) and math.isfinite(Di) and Do > Di > 0):
        raise ValueError("require finite OD > ID > 0")
    area_in2=math.pi/4.0*(Do**2-Di**2)
    I_in4=math.pi/64.0*(Do**4-Di**4)
    return {
        "area_in2":area_in2,
        "area_ft2":area_in2/144.0,
        "I_in4":I_in4,
        "I_ft4":I_in4/(12.0**4),
    }


def equation1_contact_force_lbf(
    length_ft: float,
    unit_weight_lb_per_ft: float,
    floating_factor: float,
    inclination_deg: float,
) -> float:
    """P44 Eq. (1): F = L f FF sin(theta)."""
    L=float(length_ft); f=float(unit_weight_lb_per_ft); FF=float(floating_factor); th=float(inclination_deg)
    if not all(math.isfinite(x) for x in (L,f,FF,th)):
        raise ValueError("inputs must be finite")
    if L <= 0 or f < 0 or FF < 0:
        raise ValueError("invalid physical input")
    return L*f*FF*math.sin(math.radians(th))


def equation1_printed_arithmetic_lbf(
    length_ft: float,
    unit_weight_lb_per_ft: float,
    floating_factor: float,
    printed_sine: float,
) -> float:
    """Reproduce the arithmetic printed explicitly beneath P44 Eq. (1)."""
    return float(length_ft)*float(unit_weight_lb_per_ft)*float(floating_factor)*float(printed_sine)


def time_slice_spacing_s(wave_period_s: float, slice_count: int) -> float:
    T=float(wave_period_s); n=int(slice_count)
    if T <= 0 or n <= 0:
        raise ValueError("period and slice count must be positive")
    return T/n


def penalty_penetration_in(force_lbf: float, stiffness_lbf_per_ft: float) -> float:
    """Independent diagnostic: elastic penetration = force / penalty stiffness."""
    F=abs(float(force_lbf)); K=float(stiffness_lbf_per_ft)
    if not math.isfinite(F) or not math.isfinite(K) or K <= 0:
        raise ValueError("invalid force/stiffness")
    return F/K*12.0


def contact_stiffness_state(normal_displacement_ft: float, gap_ft: float, K1_lbf_per_ft: float=1.0e6) -> dict:
    """Source-bounded state classifier for the P44 gap spring.

    The paper states K0 is negligible and K1 is activated after displacement reaches the gap.
    This function reports state/stiffness only; it does not invent the unpublished exact transition-force law.
    """
    u=abs(float(normal_displacement_ft)); g=float(gap_ft); K1=float(K1_lbf_per_ft)
    if g < 0 or K1 <= 0:
        raise ValueError("gap must be non-negative and K1 positive")
    active=u >= g
    return {
        "contact_active":active,
        "stiffness_lbf_per_ft":K1 if active else 0.0,
        "penetration_ft":max(0.0,u-g),
        "evidence_boundary":"K0 treated as zero only for state reporting because source calls it negligible but gives no numeric value."
    }
