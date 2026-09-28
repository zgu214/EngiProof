"""P40 published analytical equations and an independent work-balance reconstruction.

All stresses are MPa and all lengths use one consistent length unit. Returned
pressures are kPa. The source PDF remains external to the repository.
"""
from __future__ import annotations

import math


def _positive(name: str, value: float) -> float:
    x=float(value)
    if not math.isfinite(x) or x <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return x


def _nonnegative(name: str, value: float) -> float:
    x=float(value)
    if not math.isfinite(x) or x < 0.0:
        raise ValueError(f"{name} must be non-negative and finite")
    return x


def equation2_pressure_kPa(Do: float, to: float, sigma_Yo_MPa: float) -> float:
    """Published Eq. (2): plane-strain lower-bound single-pipe pressure."""
    Do=_positive("Do",Do); to=_positive("to",to); sy=_positive("sigma_Yo_MPa",sigma_Yo_MPa)
    return float((2.0*math.pi/math.sqrt(3.0))*sy*(to/Do)**2*1000.0)


def equation3_pressure_kPa(
    Do: float,
    to: float,
    ti: float,
    sigma_Yo_MPa: float,
    sigma_Yi_over_sigma_Yo: float,
) -> float:
    """Published Eq. (3): prior PIP propagation-pressure expression."""
    base=equation2_pressure_kPa(Do,to,sigma_Yo_MPa)
    ti=_nonnegative("ti",ti); to=_positive("to",to)
    ratio=_nonnegative("sigma_Yi_over_sigma_Yo",sigma_Yi_over_sigma_Yo)
    return float(base*(1.0+ratio*(ti/to)**2))


def equation6_pressure_kPa(D: float, t: float, sigma_Y_MPa: float) -> float:
    """Published Eq. (6): modified single-pipe lower-bound pressure."""
    D=_positive("D",D); t=_positive("t",t); sy=_positive("sigma_Y_MPa",sigma_Y_MPa)
    return float((3.0*math.pi/2.515)*sy*(t/D)**2*1000.0)


def equation9_pressure_kPa(
    Do: float,
    to: float,
    Di: float,
    ti: float,
    sigma_Yo_MPa: float,
    sigma_Yi_over_sigma_Yo: float,
) -> float:
    """Published P40 Eq. (9): modified PIP propagation pressure.

    Source-text transcription:
      Eq.6_outer
      * [1 + (sigma_Yi/sigma_Yo)*(ti/to)^2]
      * 1/[1 - (Di/(2*Do))^2]
    """
    Do=_positive("Do",Do); to=_positive("to",to)
    Di=_nonnegative("Di",Di); ti=_nonnegative("ti",ti)
    sy=_positive("sigma_Yo_MPa",sigma_Yo_MPa)
    ratio=_nonnegative("sigma_Yi_over_sigma_Yo",sigma_Yi_over_sigma_Yo)
    den=1.0-(Di/(2.0*Do))**2
    if den <= 0.0:
        raise ValueError("Eq. (9) diameter denominator must be positive")
    base=equation6_pressure_kPa(Do,to,sy)
    return float(base*(1.0+ratio*(ti/to)**2)/den)


def independent_work_balance_pressure_kPa(
    Do: float,
    to: float,
    Di: float,
    ti: float,
    sigma_Yo_MPa: float,
    sigma_Yi_over_sigma_Yo: float,
) -> float:
    """Independent reconstruction from P40 Eqs. (8a)-(8d).

    This keeps the printed 0.626 coefficient explicitly rather than using the
    rounded Eq. (9) reduction through 2.515 and the 1/4 diameter term.
    """
    Do=_positive("Do",Do); to=_positive("to",to)
    Di=_nonnegative("Di",Di); ti=_nonnegative("ti",ti)
    syo=_positive("sigma_Yo_MPa",sigma_Yo_MPa)
    ratio=_nonnegative("sigma_Yi_over_sigma_Yo",sigma_Yi_over_sigma_Yo)
    syi=syo*ratio
    den=Do**2*(math.pi-0.626*(1.0+(Di/Do)**2))
    if den <= 0.0:
        raise ValueError("independent work-balance denominator must be positive")
    pressure_MPa=3.0*math.pi*(syo*to**2+syi*ti**2)/den
    return float(pressure_MPa*1000.0)
