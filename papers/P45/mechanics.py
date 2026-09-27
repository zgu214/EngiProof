"""P45 mechanics: Safai (1983), Nonlinear dynamic analysis of deep water risers.

Two kinds of code live here and are kept separate:

PUBLISHED - transcriptions of formulations printed in the source
    * Appendix 1: beam-column stiffness coefficients k1, k2, k3 (compression,
      tension, zero axial force), the 12x12 'linear' stiffness K and the
      geometric-nonlinearity matrix K_G.
    * Eq. (7): theta-Wilson / Newmark-type relations with parameters theta, beta, lambda.
    * Appendix 2: segment interpolation factors C1..C4 and the added-mass matrix B_i.

INDEPENDENT - checks built for EngiProof, not taken from the source
    * limits, identities and rigid-body properties of the published formulas;
    * an independent Hermite finite-element beam-column solution;
    * an independent single-degree-of-freedom integrator built on Eq. (7)
      (the back-interpolation from t+tau to t+dt is NOT given in the source);
    * Airy dispersion, unit conversions and table arithmetic.

No full nonlinear riser time-domain analysis is attempted: the source does not
give theta, beta, lambda, the iteration tolerance, structural damping or the
element discretisation of the comparison cases.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

G = 9.80665          # m/s², standard gravity (assumption of this implementation; not stated in the source)
DN = 10.0            # N per decanewton (dN), the source's force unit
FT = 0.3048
INCH = 0.0254
KIP = 4448.2216152605  # N
KSI = 6.894757293168e6  # Pa
KNOT = 1852.0 / 3600.0  # m/s


# --------------------------------------------------------------- Appendix 1
def stiffness_coefficients(F: float, EI: float, L: float, GA_shear: float = math.inf) -> dict[str, float]:
    """PUBLISHED (Appendix 1): end-rotation stiffness coefficients of a beam-column.

    F > 0 tension, F < 0 compression, F = 0 zero axial force.
    beta = F/(G A'), alpha² = |F| / (E I (1 + beta)), delta = E I / (L² G A').
    GA_shear = G A' (A' = reduced shear area); math.inf gives the shear-rigid case.
    """
    beta = 0.0 if math.isinf(GA_shear) else F / GA_shear
    delta = 0.0 if math.isinf(GA_shear) else EI / (L * L * GA_shear)
    if F == 0.0:
        d = 1.0 + 12.0 * delta
        k1 = 4.0 * EI / L * (1.0 + 3.0 * delta) / d
        k2 = 2.0 * EI / L * (1.0 - 6.0 * delta) / d
        k3 = 6.0 * EI / L / d
        return {"k1": k1, "k2": k2, "k3": k3, "branch": "zero", "alphaL": 0.0, "beta": 0.0, "delta": delta}
    alpha = math.sqrt(abs(F) / (EI * (1.0 + beta)))
    x = alpha * L
    b1 = 1.0 + beta
    if F < 0.0:  # compression
        den = -b1 * x * math.sin(x) + 2.0 * (1.0 - math.cos(x))
        k1 = EI / L * x * (-b1 * x * math.cos(x) + math.sin(x)) / den
        k2 = EI / L * x * (b1 * x - math.sin(x)) / den
        k3 = EI / L * x * x * b1 * (1.0 - math.cos(x)) / den
        branch = "compression"
    else:        # tension
        den = -b1 * x * math.sinh(x) + 2.0 * (-1.0 + math.cosh(x))
        k1 = EI / L * x * (-b1 * x * math.cosh(x) + math.sinh(x)) / den
        k2 = EI / L * x * (b1 * x - math.sinh(x)) / den
        k3 = EI / L * x * x * b1 * (1.0 - math.cosh(x)) / den
        branch = "tension"
    return {"k1": k1, "k2": k2, "k3": k3, "branch": branch, "alphaL": x, "beta": beta, "delta": delta}


def element_linear_stiffness(EA: float, GJ: float, L: float, k1: float, k2: float, k3: float) -> np.ndarray:
    """PUBLISHED (Appendix 1): 12x12 'linear' stiffness K in local axes.

    DOF order per node: u (axial x'), v (y'), w (z'), theta_x', theta_y', theta_z';
    node i then node j. Upper triangle transcribed from the source; symmetric.
    """
    K = np.zeros((12, 12))
    a, t = EA / L, GJ / L
    s2, s1 = 2.0 * k3 / L**2, k3 / L
    upper = {
        (0, 0): a, (0, 6): -a,
        (1, 1): s2, (1, 5): s1, (1, 7): -s2, (1, 11): s1,
        (2, 2): s2, (2, 4): -s1, (2, 8): -s2, (2, 10): -s1,
        (3, 3): t, (3, 9): -t,
        (4, 4): k1, (4, 8): s1, (4, 10): k2,
        (5, 5): k1, (5, 7): -s1, (5, 11): k2,
        (6, 6): a,
        (7, 7): s2, (7, 11): -s1,
        (8, 8): s2, (8, 10): s1,
        (9, 9): t,
        (10, 10): k1,
        (11, 11): k1,
    }
    for (r, c), v in upper.items():
        K[r, c] = v
        K[c, r] = v
    return K


def geometric_stiffness(EA: float, L: float, rho2: float, rho3: float, F: float) -> np.ndarray:
    """PUBLISHED (Appendix 1): K_G = [[k_G, -k_G], [-k_G, k_G]] with the 6x6 k_G printed in the source."""
    kg = np.zeros((6, 6))
    a = EA / L
    kg[0, 1] = kg[1, 0] = a * rho2
    kg[0, 2] = kg[2, 0] = a * rho3
    kg[1, 1] = a * rho2**2 + F / L
    kg[1, 2] = kg[2, 1] = a * rho2 * rho3
    kg[2, 2] = a * rho3**2 + F / L
    return np.block([[kg, -kg], [-kg, kg]])


def rigid_body_modes(L: float) -> np.ndarray:
    """INDEPENDENT: the six rigid-body modes of a 2-node element on the local x' axis (columns)."""
    m = np.zeros((12, 6))
    for d in range(3):                       # translations
        m[d, d] = m[6 + d, d] = 1.0
    m[3, 3] = m[9, 3] = 1.0                  # rotation about x'
    m[4, 4] = m[10, 4] = 1.0; m[8, 4] = -L   # rotation about y': w = -x theta_y
    m[5, 5] = m[11, 5] = 1.0; m[7, 5] = L    # rotation about z': v = +x theta_z
    return m


def hermite_beam_column_end_stiffness(F: float, EI: float, L: float, n: int = 400) -> dict[str, float]:
    """INDEPENDENT: shear-rigid beam-column end stiffnesses by a Hermite FE model.

    n cubic Hermite elements with the consistent geometric stiffness; imposed
    w(0)=0, theta(0)=1, w(L)=0, theta(L)=0. Returns the end moments (k1 at the
    rotated end, k2 at the far end) and the transverse reaction at the rotated end.
    Independent of Appendix 1: it solves the beam-column problem numerically.
    """
    h = L / n
    ke = EI / h**3 * np.array([[12, 6*h, -12, 6*h], [6*h, 4*h*h, -6*h, 2*h*h], [-12, -6*h, 12, -6*h], [6*h, 2*h*h, -6*h, 4*h*h]])
    kg = F / (30.0 * h) * np.array([[36, 3*h, -36, 3*h], [3*h, 4*h*h, -3*h, -h*h], [-36, -3*h, 36, -3*h], [3*h, -h*h, -3*h, 4*h*h]])
    N = 2 * (n + 1)
    K = np.zeros((N, N))
    for e in range(n):
        idx = [2*e, 2*e + 1, 2*e + 2, 2*e + 3]
        K[np.ix_(idx, idx)] += ke + kg
    u = np.zeros(N)
    fixed = [0, 1, N - 2, N - 1]
    u[1] = 1.0
    free = [i for i in range(N) if i not in fixed]
    u[free] = np.linalg.solve(K[np.ix_(free, free)], -K[np.ix_(free, fixed)] @ u[fixed])
    r = K @ u
    return {"k1": float(r[1]), "k2": float(r[N - 1]), "shear_at_rotated_end": float(r[0]), "elements": n}


# --------------------------------------------------------------- Eq. (7)
def theta_method_coefficients(theta: float, beta: float, lam: float, dt: float) -> dict[str, float]:
    """PUBLISHED (Eq. 7): a1..a6 with tau = theta * dt."""
    tau = theta * dt
    return {
        "a1": lam / (beta * tau), "a2": 1.0 - lam / beta, "a3": tau * (1.0 - lam / (2.0 * beta)),
        "a4": 1.0 / (beta * tau**2), "a5": -1.0 / (beta * tau), "a6": 1.0 - 1.0 / (2.0 * beta),
        "tau": tau,
    }


def _sdof_step(m, c, k, f_tau, u, v, acc, dt, theta, beta, lam):
    a = theta_method_coefficients(theta, beta, lam, dt)
    Khat = k + a["a1"] * c + a["a4"] * m
    Rhat = f_tau - k * u - c * (a["a2"] * v + a["a3"] * acc) - m * (a["a5"] * v + a["a6"] * acc)
    du = Rhat / Khat                                   # Eq. (12) with U^(0) = U_t (exact for a linear system)
    acc_tau = a["a4"] * du + a["a5"] * v + a["a6"] * acc  # Eq. (7), second relation
    acc_new = acc + (acc_tau - acc) / theta            # reconstruction (not in source)
    v_new = v + dt * ((1 - lam) * acc + lam * acc_new)
    u_new = u + dt * v + dt * dt * ((0.5 - beta) * acc + beta * acc_new)
    return u_new, v_new, acc_new


def sdof_theta_response(m: float, c: float, k: float, force, u0: float, v0: float, dt: float, steps: int,
                        theta: float = 1.4, beta: float = 1.0 / 6.0, lam: float = 0.5) -> dict[str, Any]:
    """INDEPENDENT reconstruction: linear SDOF stepped with the source's Eq. (7)/(12)/(13).

    One 'basic iteration' of Eq. (12) with U^(0) = U_t is exact for a linear system.
    The step from t+tau back to t+dt is NOT printed in the source; the standard
    Wilson-theta/Newmark relations are used and labelled as a reconstruction:
      a(t+dt) = a(t) + (a(t+tau) - a(t)) / theta,
      v(t+dt) = v(t) + dt[(1-lam) a(t) + lam a(t+dt)],
      u(t+dt) = u(t) + dt v(t) + dt²[(1/2-beta) a(t) + beta a(t+dt)].
    The load is evaluated directly at t+tau, as Eq. (8) writes R(t+tau, ...).
    """
    tau = theta * dt
    u, v = u0, v0
    acc = (force(0.0) - c * v - k * u) / m
    us = [u]
    for i in range(steps):
        u, v, acc = _sdof_step(m, c, k, force(i * dt + tau), u, v, acc, dt, theta, beta, lam)
        us.append(u)
    return {"u": us, "dt": dt, "theta": theta, "beta": beta, "lambda": lam}


def spectral_radius(theta: float, dt_over_T: float, beta: float = 1.0 / 6.0, lam: float = 0.5, zeta: float = 0.0) -> float:
    """INDEPENDENT: spectral radius of the one-step amplification operator of the reconstructed scheme.

    State (u, v, a) of an SDOF with omega = 1; the operator is built column by column.
    rho <= 1 means the step does not amplify free vibration.
    """
    omega = 1.0
    dt = dt_over_T * 2.0 * math.pi / omega
    A = np.zeros((3, 3))
    for j, state in enumerate(np.eye(3)):
        A[:, j] = _sdof_step(1.0, 2.0 * zeta * omega, omega * omega, 0.0, *state, dt, theta, beta, lam)
    return float(max(abs(np.linalg.eigvals(A))))


# --------------------------------------------------------------- Appendix 2
def segment_factors(n: int, q: int) -> dict[str, float]:
    """PUBLISHED (Appendix 2): C1..C4 for segment q of n."""
    return {"C1": (n - q + 0.5) / n, "C2": 3.0 - 2.0 * (n - q + 0.5) / n, "C3": (q - 0.5) / n, "C4": 3.0 - 2.0 * (q - 0.5) / n}


def added_mass_Bi(rho: float, S: float, dl: float, Cm: float, e: np.ndarray) -> np.ndarray:
    """PUBLISHED (Appendix 2): B_i = rho S dl Cm [[ey²+ez², -ex ey, -ex ez], ...]."""
    ex, ey, ez = e
    return rho * S * dl * Cm * np.array([[ey*ey + ez*ez, -ex*ey, -ex*ez],
                                          [-ey*ex, ex*ex + ez*ez, -ey*ez],
                                          [-ez*ex, -ez*ey, ex*ex + ey*ey]])


# --------------------------------------------------------------- environment
def airy_wavenumber(period_s: float, depth_m: float) -> float:
    """INDEPENDENT: linear (Airy) dispersion omega² = g k tanh(k h), solved by Newton iteration."""
    w = 2.0 * math.pi / period_s
    k = w * w / G
    for _ in range(100):
        f = G * k * math.tanh(k * depth_m) - w * w
        df = G * math.tanh(k * depth_m) + G * k * depth_m / math.cosh(k * depth_m) ** 2
        k_new = k - f / df
        if abs(k_new - k) < 1e-15 * k:
            return k_new
        k = k_new
    return k


def annulus_area(od: float, id_: float) -> float:
    return math.pi / 4.0 * (od * od - id_ * id_)
