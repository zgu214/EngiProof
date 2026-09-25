"""Independent equation-evaluation tools for P29 (Bi & Hao, 2016).

No FE model is reproduced. The functions evaluate the published 2-DOF
relationships and keep the positive-frequency/two-sided convention explicit.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss

DEFAULT_OMEGA_S = 11.142
DEFAULT_ZETA_S = 0.05

def _check_positive(*values):
    if not all(np.isfinite(v) and float(v) > 0 for v in values):
        raise ValueError("All physical/numerical inputs must be positive finite values.")

def positive_frequency_integral(
    mass_ratio: float,
    gamma: float,
    zeta_t: float,
    omega_s_rad_per_s: float = DEFAULT_OMEGA_S,
    zeta_s: float = DEFAULT_ZETA_S,
) -> float:
    """Positive-frequency integral from an independent state-space covariance solve."""
    _check_positive(mass_ratio,gamma,zeta_t,omega_s_rad_per_s,zeta_s)
    mu=float(mass_ratio); ws=float(omega_s_rad_per_s); wt=float(gamma)*ws
    ct=2.0*mu*float(zeta_t)*wt
    kt=mu*wt**2
    M=np.diag([1.0,mu])
    C=np.array([[2.0*float(zeta_s)*ws+ct,-ct],[-ct,ct]],dtype=float)
    K=np.array([[ws**2+kt,-kt],[-kt,kt]],dtype=float)
    A=np.block([[np.zeros((2,2)),np.eye(2)],[-np.linalg.solve(M,K),-np.linalg.solve(M,C)]])
    if np.max(np.linalg.eigvals(A).real) >= 0:
        raise ValueError("The requested covariance system is not asymptotically stable.")
    B=np.array([0.0,0.0,-1.0,-1.0])
    Q=np.outer(B,B)
    n=A.shape[0]
    L=np.kron(np.eye(n),A)+np.kron(A,np.eye(n))
    P=np.linalg.solve(L,-Q.reshape(-1,order="F")).reshape((n,n),order="F")
    residual=np.linalg.norm(A@P+P@A.T+Q)/np.linalg.norm(Q)
    if not np.isfinite(P[0,0]) or P[0,0] <= 0 or residual > 1e-8:
        raise ArithmeticError("State-space covariance solve failed its residual/positivity check.")
    return float(np.pi*P[0,0])

def two_sided_integral(
    mass_ratio: float,
    gamma: float,
    zeta_t: float,
    omega_s_rad_per_s: float = DEFAULT_OMEGA_S,
    zeta_s: float = DEFAULT_ZETA_S,
) -> float:
    """Two-sided convention retained by EngiProof: exactly 2x positive-frequency value."""
    return 2.0*positive_frequency_integral(mass_ratio,gamma,zeta_t,omega_s_rad_per_s,zeta_s)

def _transfer_sq(omega,mu,gamma,zeta_t,omega_s,zeta_s):
    wt=gamma*omega_s
    Z=mu*(wt**2+2j*zeta_t*wt*omega)/(wt**2-omega**2+2j*zeta_t*wt*omega)
    H=(1.0+Z)/(omega_s**2-omega**2+2j*zeta_s*omega_s*omega-omega**2*Z)
    return np.abs(H)**2

@lru_cache(maxsize=8)
def _gauss_nodes(nodes: int):
    if nodes < 128:
        raise ValueError("nodes must be >= 128 for the infinite-domain quadrature.")
    x,w=leggauss(nodes)
    return x,w

def direct_transfer_quadrature(
    mass_ratio: float,
    gamma: float,
    zeta_t: float,
    omega_s_rad_per_s: float = DEFAULT_OMEGA_S,
    zeta_s: float = DEFAULT_ZETA_S,
    nodes: int = 1024,
) -> float:
    """Independent Gauss-Legendre quadrature of source Eqs. (17)-(18) over [0,inf)."""
    _check_positive(mass_ratio,gamma,zeta_t,omega_s_rad_per_s,zeta_s)
    x,w=_gauss_nodes(int(nodes))
    t=(x+1.0)/2.0
    omega=t/(1.0-t)
    jac=1.0/(1.0-t)**2
    vals=_transfer_sq(omega,float(mass_ratio),float(gamma),float(zeta_t),float(omega_s_rad_per_s),float(zeta_s))
    return float(np.sum((w/2.0)*vals*jac))

def independent_crosscheck(
    mass_ratio: float,
    gamma: float,
    zeta_t: float,
    omega_s_rad_per_s: float = DEFAULT_OMEGA_S,
    zeta_s: float = DEFAULT_ZETA_S,
) -> dict:
    state=positive_frequency_integral(mass_ratio,gamma,zeta_t,omega_s_rad_per_s,zeta_s)
    quad=direct_transfer_quadrature(mass_ratio,gamma,zeta_t,omega_s_rad_per_s,zeta_s)
    return {
        "state_space_positive_frequency_integral":state,
        "direct_transfer_quadrature":quad,
        "relative_difference":abs(quad-state)/state,
        "two_sided_integral":2.0*state,
    }
