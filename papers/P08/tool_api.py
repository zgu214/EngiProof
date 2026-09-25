"""Callable, source-bounded tools for P08 (Vaz & Patel, 1999).

These functions expose only the analytical relationships already used by the
P08 reproduction. They do not add FE physics or broaden the paper's stated
assumptions.
"""
from __future__ import annotations

import math

DEFAULT_DO_M = 0.168
DEFAULT_DI_M = 0.133
DEFAULT_ALPHA_PER_C = 12e-6
PUBLISHED_EQ11_COEFF_C_M2 = 9476.0
APPENDIX_A_BETA004_COEFF_C_M2 = 2369.0


def section_area_m2(Do_m: float = DEFAULT_DO_M, Di_m: float = DEFAULT_DI_M) -> float:
    if Do_m <= 0 or Di_m < 0 or Di_m >= Do_m:
        raise ValueError("Require Do_m > Di_m >= 0.")
    return math.pi / 4.0 * (Do_m**2 - Di_m**2)


def second_moment_m4(Do_m: float = DEFAULT_DO_M, Di_m: float = DEFAULT_DI_M) -> float:
    if Do_m <= 0 or Di_m < 0 or Di_m >= Do_m:
        raise ValueError("Require Do_m > Di_m >= 0.")
    return math.pi / 64.0 * (Do_m**4 - Di_m**4)


def independent_euler_thermal_coefficient(
    Do_m: float = DEFAULT_DO_M,
    Di_m: float = DEFAULT_DI_M,
    alpha_per_C: float = DEFAULT_ALPHA_PER_C,
) -> float:
    """Return C in dT=C/L^2 from Euler load = restrained thermal load.

    E cancels from 4*pi^2*E*I/L^2 = E*A*alpha*dT.
    """
    if alpha_per_C <= 0:
        raise ValueError("alpha_per_C must be > 0.")
    A = section_area_m2(Do_m, Di_m)
    I = second_moment_m4(Do_m, Di_m)
    return 4.0 * math.pi**2 * I / (A * alpha_per_C)


def critical_temperature_eq11(length_m: float) -> float:
    """Published P08 Eq. (11) case-study relationship, dT=9476/L^2 [degC]."""
    if length_m <= 0:
        raise ValueError("length_m must be > 0.")
    return PUBLISHED_EQ11_COEFF_C_M2 / length_m**2


def critical_temperature_appendix_a(length_m: float, mode_n: int = 1) -> float:
    """P08 Appendix-A beta=0.04 branch used in the Figure 7 reconstruction.

    The half-wave length follows the reproduction convention l=L/(n+1), and
    dT=2369/l^2. This is a source-case reconstruction, not a general soil model.
    """
    if length_m <= 0:
        raise ValueError("length_m must be > 0.")
    if int(mode_n) != mode_n or mode_n < 1:
        raise ValueError("mode_n must be an integer >= 1.")
    l = length_m / (int(mode_n) + 1)
    return APPENDIX_A_BETA004_COEFF_C_M2 / l**2
