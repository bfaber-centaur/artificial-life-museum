"""SOUP: parameter-embedded Flow-Lenia, an open-ended evolution world.

Flow-Lenia (Plantec et al. 2023) moves matter up the gradient of an affinity field and conserves
total mass. In its "parameter embedding" variant each cell also carries the parameters of the
local rule, and the parameters travel with the matter. Here every cell carries a genome
g(x) = the K growth weights h_k(x) of a fixed set of K kernels:

  U_k   = K_k * A                                        (shared kernels, FFT on a torus)
  Aff   = sum_k  h_k~(x) (2 exp(-(U_k - m_k)^2 / 2 s_k^2) - 1)
  F     = (1 - alpha) grad Aff - alpha grad A,   alpha = clip((A/theta)^n, 0, 1)
  A'    = reintegration tracking of A along dt F (Moroz 2020): conserves mass
  Q'    = the same transport applied to Q = A g        (genomes ride with their matter)
  g'    = Q' / A'                                      (inherit="blend": genomes average by mass)
  or g' = genome of the largest single incoming parcel   (inherit="dominant": no averaging)

h~ is the genome smoothed by a Gaussian of width `halo` (mass-weighted: blur(Q) / blur(A)), so that
the empty cells around a body feel that body's rule. Mutation: every `mut_every` steps one random
body-sized disc (radius `mut_r`) centred on matter gets g <- clip(g + N(0, mut_sd), 0, 1), the
same random vector for the whole disc. Matter is never created or destroyed, so bodies compete for
a fixed amount of mass.

This is an independent numpy implementation written from the paper's description; it is not the
authors' code. The kernel construction follows research/experiments/WINGS/flow_lenia.py.
"""
from __future__ import annotations

import numpy as np


def signed_dist(n):
    f = np.fft.fftfreq(n, 1.0 / n)
    Y, X = np.meshgrid(f, f, indexing="ij")
    return np.sqrt(X ** 2 + Y ** 2)


def sobel(A):
    def r(a, dy, dx):
        return np.roll(a, (dy, dx), axis=(-2, -1))
    gx = (r(A, 1, -1) + 2 * r(A, 0, -1) + r(A, -1, -1) - r(A, 1, 1) - 2 * r(A, 0, 1) - r(A, -1, 1)) / 8
    gy = (r(A, -1, 1) + 2 * r(A, -1, 0) + r(A, -1, -1) - r(A, 1, 1) - 2 * r(A, 1, 0) - r(A, 1, -1)) / 8
    return gy, gx


class Kernels:
    """K shared kernels: sums of 3 Gaussian rings, as FlowRule.random in WINGS/flow_lenia.py."""

    def __init__(self, rng, K=10, R=13.0):
        self.K, self.R = K, R
        self.r = rng.uniform(0.2, 1.0, K)
        self.a = rng.uniform(0, 1, (K, 3))
        self.b = rng.uniform(0.001, 1, (K, 3))
        self.w = rng.uniform(0.01, 0.5, (K, 3))
        self.m = rng.uniform(0.05, 0.5, K)
        self.s = rng.uniform(0.001, 0.18, K)
        self.h = rng.uniform(0.01, 1.0, K)  # the rule's own weights: a natural founder genome

    def fields(self, n):
        D = signed_dist(n) / (self.R * self.r[:, None, None])
        Kf = (self.b[:, :, None, None] * np.exp(-((D[:, None] - self.a[:, :, None, None]) ** 2)
                                               / (2 * self.w[:, :, None, None] ** 2))).sum(1)
        Kf = Kf * (D < 1)
        return Kf / Kf.sum(axis=(1, 2), keepdims=True)


class Soup:
    def __init__(self, kern: Kernels, A, G, *, dt=0.2, sigma=0.65, dd=5, theta=2.0, npow=2.0,
                 halo=4.0, mut_every=50, mut_r=10, mut_sd=0.15, seed=0, inherit="blend"):
        n = A.shape[0]
        self.n, self.kern = n, kern
        self.A = np.asarray(A, np.float64).copy()
        self.G = np.asarray(G, np.float64).copy()  # (K, n, n) genome, values in [0, 1]
        self.dt, self.sigma, self.dd, self.theta, self.npow = dt, sigma, dd, theta, npow
        self.mut_every, self.mut_r, self.mut_sd = mut_every, mut_r, mut_sd
        assert inherit in ("blend", "dominant")
        self.inherit = inherit
        self.rng = np.random.default_rng(seed)
        self.t = 0
        self.khat = np.fft.rfft2(kern.fields(n))
        d2 = signed_dist(n) ** 2
        g = np.exp(-d2 / (2 * halo ** 2)); g /= g.sum()
        self.hhat = np.fft.rfft2(g)
        iy, ix = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
        self.iy, self.ix = iy, ix
        self.disc = d2 <= mut_r ** 2  # centred at (0, 0), rolled into place
        self.log = []  # mutation events: (t, y, x, delta)

    def genome_smooth(self):
        Q = self.A[None] * self.G
        bq = np.fft.irfft2(np.fft.rfft2(Q) * self.hhat, s=self.A.shape)
        ba = np.fft.irfft2(np.fft.rfft2(self.A) * self.hhat, s=self.A.shape)
        return bq / np.maximum(ba, 1e-9)[None]

    def affinity(self):
        k = self.kern
        U = np.fft.irfft2(np.fft.rfft2(self.A)[None] * self.khat, s=self.A.shape)
        Gk = 2 * np.exp(-((U - k.m[:, None, None]) ** 2) / (2 * k.s[:, None, None] ** 2)) - 1
        return (self.genome_smooth() * Gk).sum(0)

    def step(self):
        A = self.A
        Aff = self.affinity()
        gU = np.stack(sobel(Aff)); gA = np.stack(sobel(A))
        alpha = np.clip((A / self.theta) ** self.npow, 0, 1)
        F = (1 - alpha) * gU - alpha * gA
        lim = self.dd - self.sigma
        disp = np.clip(self.dt * F, -lim, lim)
        s, n = self.sigma, self.n
        base = np.rint(disp)
        Kc = self.G.shape[0]
        src = np.concatenate([A[None], A[None] * self.G]).reshape(Kc + 1, -1)  # mass, then mass*genome
        out = np.zeros((Kc + 1, n * n))
        if self.inherit == "dominant":
            best = np.zeros(n * n); bestg = self.G.reshape(Kc, -1).copy()
        for j in (-1, 0, 1):
            oy = base[0] + j
            wy = np.clip(0.5 + s - np.abs(oy - disp[0]), 0, min(1, 2 * s)) / (2 * s)
            ty = (self.iy + oy.astype(np.int64)) % n
            for i in (-1, 0, 1):
                ox = base[1] + i
                wx = np.clip(0.5 + s - np.abs(ox - disp[1]), 0, min(1, 2 * s)) / (2 * s)
                tx = (self.ix + ox.astype(np.int64)) % n
                tgt = (ty * n + tx).ravel()
                w = (wy * wx).ravel()
                part = np.stack([np.bincount(tgt, weights=src[c] * w, minlength=n * n) for c in range(Kc + 1)])
                out += part
                if self.inherit == "dominant":
                    # the genome of the largest single incoming parcel wins the cell
                    win = part[0] > best
                    best = np.where(win, part[0], best)
                    bestg[:, win] = part[1:, win] / part[0, win]
        out = out.reshape(Kc + 1, n, n)
        self.A = out[0]
        live = self.A > 1e-9
        if self.inherit == "dominant":
            self.G = np.where(live[None], np.clip(bestg.reshape(Kc, n, n), 0, 1), self.G)
        else:
            self.G = np.where(live[None], out[1:] / np.where(live, self.A, 1.0)[None], self.G)
        self.t += 1
        if self.mut_every and self.t % self.mut_every == 0:
            self.mutate()
        return self.A

    def mutate(self):
        p = self.A.ravel() / self.A.sum()
        c = self.rng.choice(self.n * self.n, p=p)
        y, x = divmod(int(c), self.n)
        delta = self.rng.normal(0, self.mut_sd, self.G.shape[0])
        m = np.roll(self.disc, (y, x), axis=(0, 1))
        self.G[:, m] = np.clip(self.G[:, m] + delta[:, None], 0, 1)
        self.log.append((self.t, y, x, delta.round(4).tolist()))
