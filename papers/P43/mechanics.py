from __future__ import annotations

import math
import numpy as np


def _positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def dimensionless_alpha_beta(
    *,
    weight_lb_per_ft: float,
    outer_area_ft2: float,
    inner_area_ft2: float,
    sea_water_weight_density_lb_per_ft3: float,
    mud_weight_density_lb_per_ft3: float,
    length_ft: float,
    youngs_modulus_psi: float,
    second_moment_in4: float,
    bottom_pull_lb: float,
) -> dict:
    '''P43 source dimensionless parameters alpha and beta.

    Source unit convention:
    w [lb/ft], areas [ft^2], weight densities [lb/ft^3],
    L [ft], E [psi], I [in^4], FB [lb].
    The source includes the 144 in^2/ft^2 conversion explicitly.
    '''
    w = float(weight_lb_per_ft)
    Ap = _positive("outer_area_ft2", outer_area_ft2)
    Ai = _positive("inner_area_ft2", inner_area_ft2)
    rw = _positive("sea_water_weight_density_lb_per_ft3", sea_water_weight_density_lb_per_ft3)
    rm = _positive("mud_weight_density_lb_per_ft3", mud_weight_density_lb_per_ft3)
    L = _positive("length_ft", length_ft)
    E = _positive("youngs_modulus_psi", youngs_modulus_psi)
    I = _positive("second_moment_in4", second_moment_in4)
    FB = float(bottom_pull_lb)
    if not math.isfinite(w) or not math.isfinite(FB):
        raise ValueError("weight and bottom pull must be finite")

    EI = E * I
    alpha = (w - Ap * rw + Ai * rm) * L**3 * 144.0 / EI
    beta = (FB + L * Ap * rw - L * Ai * rm) * L**2 * 144.0 / EI
    return {"alpha": alpha, "beta": beta}


def omega_from_lambda(
    lambda_value: float,
    *,
    youngs_modulus_psi: float,
    second_moment_in4: float,
    participating_mass_slug_per_ft: float,
    length_ft: float,
) -> float:
    '''Invert P43 lambda^4 = m omega^2 L^4 144 / (EI).'''
    lam = _positive("lambda_value", lambda_value)
    E = _positive("youngs_modulus_psi", youngs_modulus_psi)
    I = _positive("second_moment_in4", second_moment_in4)
    m = _positive("participating_mass_slug_per_ft", participating_mass_slug_per_ft)
    L = _positive("length_ft", length_ft)
    return lam**2 * math.sqrt(E * I / (144.0 * m * L**4))


def period_from_lambda(lambda_value: float, **kwargs) -> float:
    omega = omega_from_lambda(lambda_value, **kwargs)
    return 2.0 * math.pi / omega


def equation10_approximate_lambda(mode: int, alpha: float, beta: float) -> float:
    '''P43 Eq. (10).

    lambda_i = i*pi * [1 + (beta + alpha/2)/(i^2*pi^2)]^(1/4)
    '''
    i = int(mode)
    if i < 1:
        raise ValueError("mode must be >= 1")
    a = float(alpha)
    b = float(beta)
    inside = 1.0 + (b + 0.5 * a) / (i * i * math.pi**2)
    if inside <= 0.0:
        raise ValueError("Eq. (10) radicand must be positive")
    return i * math.pi * inside**0.25


def _hermite_shape(xi: float, Le: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    '''Cubic Hermite displacement, first derivative and second derivative.'''
    x = float(xi)
    L = float(Le)
    N = np.array([
        1.0 - 3.0 * x * x + 2.0 * x**3,
        L * (x - 2.0 * x * x + x**3),
        3.0 * x * x - 2.0 * x**3,
        L * (-x * x + x**3),
    ], dtype=float)
    dN_dxi = np.array([
        -6.0 * x + 6.0 * x * x,
        L * (1.0 - 4.0 * x + 3.0 * x * x),
        6.0 * x - 6.0 * x * x,
        L * (-2.0 * x + 3.0 * x * x),
    ], dtype=float)
    d2N_dxi2 = np.array([
        -6.0 + 12.0 * x,
        L * (-4.0 + 6.0 * x),
        6.0 - 12.0 * x,
        L * (-2.0 + 6.0 * x),
    ], dtype=float)
    return N, dN_dxi / L, d2N_dxi2 / (L * L)


def solve_dimensionless_eigenproblem(
    alpha: float,
    beta: float,
    *,
    elements: int = 80,
    modes: int = 5,
    return_modes: bool = False,
) -> dict:
    '''Independent Hermite-FE solution of P43 Eq. (8).

    Equation:
        d4Y/dzeta4 - d/dzeta[(beta + alpha*zeta) dY/dzeta] - lambda^4 Y = 0

    Pinned/ball-joint ends:
        Y(0)=Y(1)=0; bending moment is naturally zero at the ends.

    Weak form:
        integral(d2v*d2Y) + integral(P*dv*dY) = lambda^4 integral(v*Y)

    This is independent of the paper's Eq. (9) power-series implementation.
    '''
    a = float(alpha)
    b = float(beta)
    ne = int(elements)
    nm = int(modes)
    if ne < 4:
        raise ValueError("elements must be >= 4")
    if nm < 1:
        raise ValueError("modes must be >= 1")

    nn = ne + 1
    nd = 2 * nn
    Le = 1.0 / ne
    K = np.zeros((nd, nd), dtype=float)
    M = np.zeros((nd, nd), dtype=float)
    gp, gw = np.polynomial.legendre.leggauss(5)

    for e in range(ne):
        x0 = e * Le
        ke = np.zeros((4, 4), dtype=float)
        me = np.zeros((4, 4), dtype=float)
        for eta, wgt in zip(gp, gw):
            xi = (eta + 1.0) / 2.0
            jac = Le / 2.0
            zeta = x0 + xi * Le
            N, B1, B2 = _hermite_shape(xi, Le)
            P = b + a * zeta
            ke += wgt * jac * (np.outer(B2, B2) + P * np.outer(B1, B1))
            me += wgt * jac * np.outer(N, N)
        ids = [2 * e, 2 * e + 1, 2 * (e + 1), 2 * (e + 1) + 1]
        K[np.ix_(ids, ids)] += ke
        M[np.ix_(ids, ids)] += me

    constrained = {0, 2 * ne}
    free = [i for i in range(nd) if i not in constrained]
    Kr = K[np.ix_(free, free)]
    Mr = M[np.ix_(free, free)]

    Lc = np.linalg.cholesky(Mr)
    invL = np.linalg.inv(Lc)
    A = invL @ Kr @ invL.T
    eigvals, eigvecs = np.linalg.eigh((A + A.T) / 2.0)
    pos = np.where(eigvals > 1e-10)[0][:nm]
    mu = eigvals[pos]
    lambdas = mu**0.25

    out = {
        "alpha": a,
        "beta": b,
        "elements": ne,
        "lambda": [float(x) for x in lambdas],
        "eigenvalue_lambda4": [float(x) for x in mu],
    }

    if return_modes:
        reduced = np.linalg.solve(Lc.T, eigvecs[:, pos])
        full = np.zeros((nd, len(pos)), dtype=float)
        full[free, :] = reduced
        for j in range(full.shape[1]):
            disp = full[0::2, j]
            scale = np.max(np.abs(disp))
            if scale > 0.0:
                full[:, j] /= scale
            nz = np.where(np.abs(full[0::2, j]) > 1e-6)[0]
            if len(nz) and full[2 * nz[0], j] < 0.0:
                full[:, j] *= -1.0
        out["_mode_dofs"] = full
    return out


def sample_mode_shape(
    alpha: float,
    beta: float,
    mode: int,
    *,
    elements: int = 120,
    points: int = 401,
) -> dict:
    if mode < 1:
        raise ValueError("mode must be >= 1")
    solved = solve_dimensionless_eigenproblem(
        alpha, beta, elements=elements, modes=mode, return_modes=True
    )
    dofs = solved["_mode_dofs"][:, mode - 1]
    ne = int(elements)
    Le = 1.0 / ne
    zetas = np.linspace(0.0, 1.0, int(points))
    y, slope, curvature = [], [], []
    for z in zetas:
        if z >= 1.0:
            e, xi = ne - 1, 1.0
        else:
            e = min(int(z / Le), ne - 1)
            xi = (z - e * Le) / Le
        ids = [2 * e, 2 * e + 1, 2 * (e + 1), 2 * (e + 1) + 1]
        N, B1, B2 = _hermite_shape(xi, Le)
        q = dofs[ids]
        y.append(float(N @ q))
        slope.append(float(B1 @ q))
        curvature.append(float(B2 @ q))

    inflections = []
    c = np.asarray(curvature)
    x = np.asarray(zetas)
    for i in range(1, len(x) - 2):
        if c[i] == 0.0:
            inflections.append(float(x[i]))
        elif c[i] * c[i + 1] < 0.0:
            x0, x1 = x[i], x[i + 1]
            c0, c1 = c[i], c[i + 1]
            inflections.append(float(x0 - c0 * (x1 - x0) / (c1 - c0)))

    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "mode": int(mode),
        "lambda": solved["lambda"][mode - 1],
        "zeta": [float(v) for v in zetas],
        "Y_normalized": y,
        "slope": slope,
        "curvature": curvature,
        "interior_inflection_zeta": inflections,
        "distance_below_top": [1.0 - v for v in inflections],
    }
