"""WINGS: three non-Lenia continuous worlds, each written from its paper's equations (numpy).

GrayScott  — Pearson 1993 reaction-diffusion, grid units:
               u' = Du lap u - u v^2 + F (1 - u),   v' = Dv lap v + u v^2 - (F + k) v
             5-point Laplacian on a torus, forward Euler, Du 0.2, Dv 0.1, dt 1.
SmoothLife — Rafler 2011: inner disk (radius ri) filling m, annulus (ri..ra) filling n,
             antialiased edges of width 1, transition s(n, m) with sigmoid widths alpha_n,
             alpha_m; "discrete" f <- s(n, m) (Rafler's paper) or "smooth"
             f <- clip(f + dt (2 s - 1), 0, 1).
ParticleLenia — Mordvintsev, Niklasson & Randazzo 2022: particles descend
             E_i = R_i - G(U_i), U(x) = sum_j w_k exp(-((|x - p_j| - mu_k) / sigma_k)^2),
             G(u) = exp(-((u - mu_g) / sigma_g)^2), R_i = c_rep/2 sum_j max(1 - |p_i - p_j|, 0)^2,
             dp/dt = -grad E (analytic gradient), Euler dt 0.1, unbounded plane.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def lap5(a):
    return np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4 * a


@dataclass
class GrayScott:
    F: float
    k: float
    u: np.ndarray
    v: np.ndarray
    Du: float = 0.2
    Dv: float = 0.1
    dt: float = 1.0

    def __post_init__(self):
        self.u = np.asarray(self.u, dtype=np.float64).copy()
        self.v = np.asarray(self.v, dtype=np.float64).copy()

    def step(self):
        u, v = self.u, self.v
        uvv = u * v * v
        self.u = u + self.dt * (self.Du * lap5(u) - uvv + self.F * (1 - u))
        self.v = v + self.dt * (self.Dv * lap5(v) + uvv - (self.F + self.k) * v)
        return self.v


@dataclass
class SmoothLife:
    A: np.ndarray
    ra: float = 21.0
    ri: float | None = None
    b1: float = 0.278
    b2: float = 0.365
    d1: float = 0.267
    d2: float = 0.445
    alpha_n: float = 0.028
    alpha_m: float = 0.147
    dt: float = 0.1
    mode: str = "smooth"  # "smooth": f <- clip(f + dt (2 s - 1)); "discrete": f <- s(n, m)
    _kh: tuple = field(default=None, repr=False)

    def __post_init__(self):
        self.A = np.asarray(self.A, dtype=np.float64).copy()
        if self.ri is None:
            self.ri = self.ra / 3
        H, W = self.A.shape
        y = np.fft.fftfreq(H, 1.0 / H)
        x = np.fft.fftfreq(W, 1.0 / W)
        Y, X = np.meshgrid(y, x, indexing="ij")
        r = np.sqrt(X ** 2 + Y ** 2)
        disk = np.clip(self.ri + 0.5 - r, 0, 1)
        outer = np.clip(self.ra + 0.5 - r, 0, 1)
        ann = outer - disk
        self._kh = (np.fft.rfft2(disk / disk.sum()), np.fft.rfft2(ann / ann.sum()))

    @staticmethod
    def _sig(x, a, w):
        return 1 / (1 + np.exp(-(x - a) * 4 / w))

    def s(self, n, m):
        sg = self._sig
        aliveness = sg(m, 0.5, self.alpha_m)
        lo = self.b1 * (1 - aliveness) + self.d1 * aliveness
        hi = self.b2 * (1 - aliveness) + self.d2 * aliveness
        return sg(n, lo, self.alpha_n) * (1 - sg(n, hi, self.alpha_n))

    def step(self):
        F = np.fft.rfft2(self.A)
        m = np.fft.irfft2(F * self._kh[0], s=self.A.shape)
        n = np.fft.irfft2(F * self._kh[1], s=self.A.shape)
        if self.mode == "discrete":
            self.A = self.s(n, m)
        else:
            self.A = np.clip(self.A + self.dt * (2 * self.s(n, m) - 1), 0, 1)
        return self.A


@dataclass
class ParticleLenia:
    P: np.ndarray  # (N, 2)
    mu_k: float = 4.0
    sigma_k: float = 1.0
    w_k: float = 0.022
    mu_g: float = 0.6
    sigma_g: float = 0.15
    c_rep: float = 1.0
    dt: float = 0.1

    def __post_init__(self):
        self.P = np.asarray(self.P, dtype=np.float64).copy()

    def fields(self, P=None):
        P = self.P if P is None else P
        d = P[:, None, :] - P[None, :, :]  # (N, N, 2) p_i - p_j
        r = np.sqrt((d ** 2).sum(-1)) + 1e-12
        np.fill_diagonal(r, 1e9)  # exclude self from repulsion
        kern = self.w_k * np.exp(-(((r - self.mu_k) / self.sigma_k) ** 2))
        rk = r.copy()
        np.fill_diagonal(rk, 0.0)
        kself = self.w_k * np.exp(-(((0.0 - self.mu_k) / self.sigma_k) ** 2))
        U = kern.sum(1) + kself  # Lenia field at each particle (includes its own kernel at r=0)
        G = np.exp(-(((U - self.mu_g) / self.sigma_g) ** 2))
        dG_dU = G * (-2 * (U - self.mu_g) / self.sigma_g ** 2)
        dk_dr = kern * (-2 * (r - self.mu_k) / self.sigma_k ** 2)  # (N, N)
        unit = d / r[..., None]
        # grad_i of U at p_i (moving the sample point) = sum_j dk_dr(r_ij) * unit_ij
        gradU = (dk_dr[..., None] * unit).sum(1)
        rep = np.maximum(1 - r, 0)
        gradR = (-self.c_rep * rep[..., None] * unit).sum(1)
        E = 0.5 * self.c_rep * (rep ** 2).sum(1) - G
        return E, U, gradR - dG_dU[:, None] * gradU

    def step(self):
        _, _, gE = self.fields()
        self.P = self.P - self.dt * gE
        return self.P

    def field_image(self, extent: float, n: int, P=None):
        """U and E-landscape sampled on an n x n grid over [-extent, extent]^2 (for rendering)."""
        P = self.P if P is None else P
        g = np.linspace(-extent, extent, n)
        X, Y = np.meshgrid(g, g)
        U = np.zeros_like(X)
        for p in P:
            r = np.sqrt((X - p[0]) ** 2 + (Y - p[1]) ** 2)
            U += self.w_k * np.exp(-(((r - self.mu_k) / self.sigma_k) ** 2))
        return U
