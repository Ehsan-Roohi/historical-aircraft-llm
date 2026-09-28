"""Strict linear flight-mode assembler for future *complete* aircraft inputs.

Inputs are DIMENSIONAL derivatives in the stated equations, including
installed propulsion. No coefficient is silently defaulted to zero. The
solver is not invoked for current V2 aircraft because their inputs are
incomplete. Eigenvalues describe a supplied mathematical model, not proof of
physical fidelity or safe flight.
"""
from __future__ import annotations

import math
import numpy as np

G = 9.80665


def _numbers(data: dict, keys: tuple[str, ...]) -> list[float]:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"Missing required dynamic inputs: {', '.join(missing)}")
    values = [float(data[key]) for key in keys]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Non-finite dynamic input")
    return values


def longitudinal_matrix(data: dict) -> np.ndarray:
    """Return A for states [u, alpha, pitch_rate, pitch_angle].

    Dimensional equations (perturbations about a steady trim):
      udot = Xu*u + Xa*alpha - g*cos(theta)*theta
      U*alphadot - U*q = Zu*u + Za*alpha + Zadot*alphadot
                           + Zq*q - g*sin(theta)*theta
      qdot = Mu*u + Ma*alpha + Madot*alphadot + Mq*q
      thetadot = q.
    The derivatives must include installed aerodynamic and propulsive effects.
    """
    keys = ("U", "theta", "Xu", "Xa", "Zu", "Za", "Zadot",
            "Zq", "Mu", "Ma", "Madot", "Mq")
    U, theta, Xu, Xa, Zu, Za, Zadot, Zq, Mu, Ma, Madot, Mq = _numbers(data, keys)
    if U <= 0 or U-Zadot <= 0:
        raise ValueError("Invalid speed or alpha-rate mass term")
    E = np.array([[1, 0, 0, 0], [0, U-Zadot, 0, 0],
                  [0, -Madot, 1, 0], [0, 0, 0, 1]], dtype=float)
    F = np.array([[Xu, Xa, 0, -G*math.cos(theta)],
                  [Zu, Za, U+Zq, -G*math.sin(theta)],
                  [Mu, Ma, Mq, 0], [0, 0, 1, 0]], dtype=float)
    return np.linalg.solve(E, F)


def lateral_matrix(data: dict) -> np.ndarray:
    """Return A for states [sideslip, roll_rate, yaw_rate, bank_angle].

    Y terms are force/mass derivatives; L and N terms are raw moment
    derivatives. Ixz is defined by the cross-inertia convention in
    Ixx*pdot - Ixz*rdot=L, Izz*rdot - Ixz*pdot=N. Supply all terms, even
    measured zeros, explicitly. A near-zero geometry-omitted AVL Cnb is not
    an acceptable installed-aircraft yaw derivative.
    """
    keys = ("U", "theta", "Ixx", "Izz", "Ixz", "Yb", "Yp", "Yr",
            "Lb", "Lp", "Lr", "Nb", "Np", "Nr")
    U, theta, Ixx, Izz, Ixz, Yb, Yp, Yr, Lb, Lp, Lr, Nb, Np, Nr = _numbers(data, keys)
    if U <= 0 or Ixx <= 0 or Izz <= 0 or Ixx*Izz-Ixz**2 <= 0:
        raise ValueError("Invalid speed or lateral inertia submatrix")
    E = np.array([[U, 0, 0, 0], [0, Ixx, -Ixz, 0],
                  [0, -Ixz, Izz, 0], [0, 0, 0, 1]], dtype=float)
    F = np.array([[Yb, Yp, Yr-U, G*math.cos(theta)],
                  [Lb, Lp, Lr, 0], [Nb, Np, Nr, 0], [0, 1, 0, 0]], dtype=float)
    return np.linalg.solve(E, F)


def roots(matrix: np.ndarray) -> list[dict]:
    """Return poles with damping only when a complex conjugate mode exists."""
    if matrix.shape != (4, 4) or not np.isfinite(matrix).all():
        raise ValueError("Expected finite four-state matrix")
    values = sorted(np.linalg.eigvals(matrix), key=lambda z: (z.real, z.imag))
    result = []
    for value in values:
        omega = abs(value)
        result.append({"real_per_s": float(value.real),
                       "imag_per_s": float(value.imag),
                       "natural_frequency_rad_s": float(omega),
                       "damping_ratio": float(-value.real/omega) if omega else None,
                       "mathematically_stable": bool(value.real < 0)})
    return result
