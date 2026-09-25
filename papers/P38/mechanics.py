"""P38 published equations and an independent work-balance check.
Author: Zhiqiang Gu | Zhiqiang.gu214@gmail.com
SI for dimensional functions; ratios are dimensionless. Not an FE solver.
"""
from __future__ import annotations
import math


def checked_ratios(d: float, r: float, s: float) -> tuple[float,float,float]:
    d,r,s=map(float,(d,r,s))
    if not all(math.isfinite(v) for v in (d,r,s)) or not 0 <= d < 1 or r < 0 or s <= 0:
        raise ValueError('Require finite 0 <= Di/Do < 1, ti/to >= 0, sigma_i/sigma_o > 0.')
    return d,r,s


def equation6b(d: float, r: float, s: float) -> float:
    """P38 Eq. (6b), flexural + circumferential membrane idealization (mode A)."""
    d,r,s=checked_ratios(d,r,s)
    return (1+s*r*r)/(1-d*d/4)


def equation12a(d: float, r: float, s: float) -> float:
    """P38 Eq. (12a), Kyriakides/Vogler empirical law; originally thick carriers."""
    d,r,s=checked_ratios(d,r,s)
    return 1+1.095*s**0.4*d*r*r


def equation12b(d: float, r: float, s: float) -> float:
    """P38 Eq. (12b), Gong/Li empirical law; originally thick carriers."""
    d,r,s=checked_ratios(d,r,s)
    return 1+.970*s**.8*d**.3*r*r


def equation16(d: float, r: float, s: float, mode: str) -> float:
    """Published fitted mode laws: coefficients are frozen, NOT refitted here.
    Mode must be supplied from evidence; this function cannot predict mode selection.
    """
    d,r,s=checked_ratios(d,r,s)
    if mode not in ('A','B') or d==0:
        raise ValueError('Equation 16 requires explicit A/B mode and Di/Do > 0.')
    a,b=(1.047,.4) if mode=='A' else (.596,-.8)
    return 1+a*s**.2*d**b*r**2.4


def equation1(D: float,t: float,sy: float) -> float:
    if not all(math.isfinite(v) and v>0 for v in (D,t,sy)) or 2*t>=D:
        raise ValueError('Require a physical positive hollow circular section.')
    return 3*math.pi/2.515*sy*(t/D)**2


def work_balance(Do:float,to:float,Di:float,ti:float,so:float,si:float) -> dict[str,float]:
    """Solve Eq. (4) directly from dimensional work terms in Eqs. (5a-c).
    Independent of the implemented normalized Eq. (6b). Unit axial length.
    At Di=ti=0, this gives the exact-constant single-pipe limit.
    """
    if not all(math.isfinite(v) for v in (Do,to,Di,ti,so,si)):
        raise ValueError('Non-finite work-balance input.')
    if not (Do>2*to>0 and so>0 and si>0 and Di>=0 and ti>=0 and Di<Do-2*to):
        raise ValueError('Nonphysical dimensions/materials or no annular clearance.')
    if (Di==0 and ti!=0) or (Di>0 and not 0<2*ti<Di):
        raise ValueError('Require absent inner pipe or physical inner hollow section.')
    ro,ri=Do/2,Di/2
    area=math.pi*ro*ro
    dlo=(2*math.pi-4*math.sqrt(2))*ro
    dli=(2*math.pi-4*math.sqrt(2))*ri
    compliance_area=ro*dlo+ri*dli
    flexure=3*math.pi*(so*to*to/4+si*ti*ti/4)
    if area<=compliance_area:raise ValueError('Nonpositive work-balance denominator.')
    p=flexure/(area-compliance_area)
    return {'pressure_Pa':p,'area_reduction_m2':area,'flexural_work_N':flexure,
            'membrane_work_N':p*compliance_area,'external_work_N':p*area,
            'relative_work_residual':(p*area-flexure-p*compliance_area)/(p*area)}
