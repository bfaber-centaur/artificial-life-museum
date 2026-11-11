"""WINGS: Flow-Lenia (Plantec, Hamon, Etcheverry, Oudeyer, Moulin-Frier & Chan 2023), one channel.

Lenia's growth field is reinterpreted as an *affinity* U; matter flows up its gradient and is moved
by reintegration tracking (Moroz 2020), so total mass is conserved exactly in real arithmetic:

  U   = sum_k h_k G_k(K_k * A)                    (K_k: sums of Gaussian rings, G_k: Gaussian bump)
  alpha = clip((A / theta_A)^n, 0, 1)
  F   = (1 - alpha) grad U - alpha grad A         (Sobel gradients, torus)
  mu  = x + clip(dt F, -(dd - s), dd - s)         destination of the mass at cell x
  A'(y) = sum_x A(x) * overlap([mu - s, mu + s]^2, cell y) / (2 s)^2

The paper's defaults: dt 0.2, s 0.65, dd 5, theta_A 2, n 2. This file is an independent numpy
implementation written from the paper's equations; it is not the authors' code.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def signed_dist(shape):
    y = np.fft.fftfreq(shape[0], 1.0 / shape[0])
    x = np.fft.fftfreq(shape[1], 1.0 / shape[1])
    Y, X = np.meshgrid(y, x, indexing="ij")
    return np.sqrt(X ** 2 + Y ** 2)


def sobel(A):
    """(d/dy, d/dx) with periodic boundary, Sobel 3x3 (unnormalised / 8 -> unit slope)."""
    def r(a, dy, dx):
        return np.roll(a, (dy, dx), axis=(0, 1))
    gx = (r(A, 1, -1) + 2 * r(A, 0, -1) + r(A, -1, -1) - r(A, 1, 1) - 2 * r(A, 0, 1) - r(A, -1, 1)) / 8
    gy = (r(A, -1, 1) + 2 * r(A, -1, 0) + r(A, -1, -1) - r(A, 1, 1) - 2 * r(A, 1, 0) - r(A, 1, -1)) / 8
    return gy, gx


@dataclass
class FlowRule:
    R: float
    r: np.ndarray  # (K,) relative radius
    a: np.ndarray  # (K, 3) ring centres in [0, 1]
    b: np.ndarray  # (K, 3) ring heights
    w: np.ndarray  # (K, 3) ring widths
    m: np.ndarray  # (K,)
    s: np.ndarray  # (K,)
    h: np.ndarray  # (K,)
    dt: float = 0.2
    sigma: float = 0.65
    dd: int = 5
    theta: float = 2.0
    n: float = 2.0

    @classmethod
    def random(cls, rng: np.random.Generator, K: int = 10, R: float = 13.0) -> "FlowRule":
        return cls(R=R, r=rng.uniform(0.2, 1.0, K), a=rng.uniform(0, 1, (K, 3)), b=rng.uniform(0.001, 1, (K, 3)),
                   w=rng.uniform(0.01, 0.5, (K, 3)), m=rng.uniform(0.05, 0.5, K), s=rng.uniform(0.001, 0.18, K),
                   h=rng.uniform(0.01, 1.0, K))

    def to_dict(self) -> dict:
        d = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in self.__dict__.items()}
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FlowRule":
        return cls(**{k: (np.asarray(v) if isinstance(v, list) else v) for k, v in d.items()})


def kernels(shape, rule: FlowRule) -> np.ndarray:
    D = signed_dist(shape) / (rule.R * rule.r[:, None, None])  # (K, H, W)
    K = (rule.b[:, :, None, None] * np.exp(-((D[:, None] - rule.a[:, :, None, None]) ** 2)
                                             / (2 * rule.w[:, :, None, None] ** 2))).sum(1)
    K = K * (D < 1)
    return K / K.sum(axis=(1, 2), keepdims=True)


@dataclass
class FlowLenia:
    rule: FlowRule
    A: np.ndarray
    conserve: bool = True  # False: classic Lenia update A <- clip(A + dt U) with the same kernels
    _khat: np.ndarray = field(default=None, repr=False)

    def __post_init__(self):
        self.A = np.asarray(self.A, dtype=np.float64).copy()
        self._khat = np.fft.rfft2(kernels(self.A.shape, self.rule))
        sh = self.A.shape
        self._cells = np.stack(np.meshgrid(np.arange(sh[0]), np.arange(sh[1]), indexing="ij")).astype(np.float64)

    def affinity(self, A=None):
        A = self.A if A is None else A
        U = np.fft.irfft2(np.fft.rfft2(A)[None] * self._khat, s=A.shape)
        ru = self.rule
        G = 2 * np.exp(-((U - ru.m[:, None, None]) ** 2) / (2 * ru.s[:, None, None] ** 2)) - 1
        return (ru.h[:, None, None] * G).sum(0)

    def flow(self, A=None):
        A = self.A if A is None else A
        ru = self.rule
        U = self.affinity(A)
        gU = np.stack(sobel(U))
        gA = np.stack(sobel(A))
        alpha = np.clip((A / ru.theta) ** ru.n, 0, 1)
        return (1 - alpha) * gU - alpha * gA

    def step(self):
        ru = self.rule
        if not self.conserve:
            self.A = np.clip(self.A + ru.dt * self.affinity(), 0, 1)
            return self.A
        F = self.flow()
        lim = ru.dd - ru.sigma
        disp = np.clip(ru.dt * F, -lim, lim)  # (2, H, W) displacement of each cell's mass
        s = ru.sigma
        A = self.A
        H, W = A.shape
        base = np.rint(disp)
        out = np.zeros(H * W)
        iy = self._cells[0].astype(np.int64)
        ix = self._cells[1].astype(np.int64)
        for j in (-1, 0, 1):
            oy = base[0] + j
            wy = np.clip(0.5 + s - np.abs(oy - disp[0]), 0, min(1, 2 * s)) / (2 * s)
            ty = (iy + oy.astype(np.int64)) % H
            for i in (-1, 0, 1):
                ox = base[1] + i
                wx = np.clip(0.5 + s - np.abs(ox - disp[1]), 0, min(1, 2 * s)) / (2 * s)
                tx = (ix + ox.astype(np.int64)) % W
                out += np.bincount((ty * W + tx).ravel(), weights=(A * wy * wx).ravel(), minlength=H * W)
        out = out.reshape(H, W)
        self.A = out
        return out
