"""Callable, source-bounded tools for P12 (Zhang, Duan & Guedes Soares, 2018).

The paper's Table 4 values are treated as published source data. The functions
below expose the printed Eq. (22) dependence and the independently fitted
Table-4 surface. They do not claim an independent FE/contact prediction.
"""
from __future__ import annotations

import math
import numpy as np

BETAS = np.array([0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0], dtype=float)
CLEARANCES_MM = np.array([2.,4.,8.,12.,16.,20.,24.], dtype=float)
FC_TABLE4_MN = np.array([
    [3.37,3.09,2.89,2.71,2.66,2.62,2.60],
    [2.67,2.41,2.29,2.17,2.13,2.11,2.08],
    [2.23,2.02,1.91,1.83,1.80,1.78,1.76],
    [1.94,1.76,1.66,1.61,1.58,1.57,1.55],
    [1.72,1.58,1.50,1.45,1.42,1.41,1.40],
    [1.57,1.45,1.37,1.33,1.31,1.29,1.28],
    [1.44,1.34,1.26,1.24,1.21,1.20,1.19],
    [1.35,1.25,1.18,1.16,1.14,1.13,1.12],
], dtype=float)
EQ22_COEFF = np.array([0.321, -0.0739, 0.129], dtype=float)
DEFAULT_DO_M = 0.3556
DEFAULT_TO_M = 0.0111
DEFAULT_DI_M = 0.2731


def annular_radial_clearance_mm(
    Do_m: float = DEFAULT_DO_M,
    to_m: float = DEFAULT_TO_M,
    Di_m: float = DEFAULT_DI_M,
) -> float:
    """Outer-pipe inside radius minus inner-pipe outside radius [mm]."""
    if Do_m <= 0 or to_m <= 0 or Di_m <= 0:
        raise ValueError("Diameters and thickness must be > 0.")
    inside_diameter = Do_m - 2.0 * to_m
    if inside_diameter <= Di_m:
        raise ValueError("Geometry gives zero/negative annular radial clearance.")
    return (inside_diameter / 2.0 - Di_m / 2.0) * 1000.0


def eq22_shape_term(beta: float, clearance_mm: float, delta_r_mm: float | None = None) -> float:
    """Return the printed Eq. (22) functional term before common dimensional scale.

    In the reproduction, one common scale is fitted because the printed table
    and equation are compared through coefficient ratios. The returned value is
    therefore not presented as an independently predicted force in MN.
    """
    if beta <= 0 or clearance_mm <= 0:
        raise ValueError("beta and clearance_mm must be > 0.")
    if delta_r_mm is None:
        delta_r_mm = annular_radial_clearance_mm()
    if delta_r_mm <= 0:
        raise ValueError("delta_r_mm must be > 0.")
    return float(EQ22_COEFF[0]/beta + EQ22_COEFF[1]*math.log(clearance_mm/delta_r_mm) + EQ22_COEFF[2])


def fit_table4_surface() -> dict:
    """Independently fit Fc=a/beta+b*ln(r0/Delta_r)+c to printed Table 4."""
    delta = annular_radial_clearance_mm()
    X=[]; y=[]
    for i,beta in enumerate(BETAS):
        for j,r0 in enumerate(CLEARANCES_MM):
            X.append([1.0/beta, math.log(r0/delta), 1.0])
            y.append(FC_TABLE4_MN[i,j])
    X=np.asarray(X,float); y=np.asarray(y,float)
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    scale=float((coef@EQ22_COEFF)/(EQ22_COEFF@EQ22_COEFF))
    return {
        'delta_r_mm': float(delta),
        'direct_fit_coefficients_MN': [float(x) for x in coef],
        'eq22_coefficients': [float(x) for x in EQ22_COEFF],
        'common_scale_MN': scale,
    }


def table4_fit_force_MN(beta: float, clearance_mm: float) -> float:
    """Return the independently fitted Table-4 regression surface [MN]."""
    if beta <= 0 or clearance_mm <= 0:
        raise ValueError("beta and clearance_mm must be > 0.")
    fit=fit_table4_surface(); a,b,c=fit['direct_fit_coefficients_MN']; delta=fit['delta_r_mm']
    return float(a/beta + b*math.log(clearance_mm/delta) + c)


def eq22_scaled_force_MN(beta: float, clearance_mm: float) -> float:
    """Return Eq. (22) shape term times the reproduction's common fitted scale [MN]."""
    fit=fit_table4_surface()
    return float(fit['common_scale_MN'] * eq22_shape_term(beta, clearance_mm, fit['delta_r_mm']))
