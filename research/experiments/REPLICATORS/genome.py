"""GenomeLenia: the 213 #84 -> #83 rule line with a per-pixel 'genome' g(x) in [0, 1] carried by matter.

Our modified rule (not Chan's): for each of the three kernel pairs k,
  U_k(x) = (1 - g(x)) (K_k^well * A)(x) + g(x) (K_k^wild * A)(x)
  A' = clip(A + dt * mean_k G(U_k(x); m_k(g), s_k(g)), 0, 1),   m_k, s_k linear in g
and the genome rides with matter: where a pixel's value falls or stays, its genome is unchanged;
where it grows, the new part takes ghat = (B * (A g)) / (B * A), the mass-weighted genome of the
neighbourhood (B a Gaussian of SIGMA_G px), and the pixel's genome is the mass-weighted mix of old
and new. Empty pixels take ghat. Optional mutation: each MUT_EVERY time units add MUT_AMP * (smooth noise
field, correlation ~ MUT_SCALE px, unit sd) to g, clipped to [0, 1].
Neutral control (rule_g = c): the rule is the constant c everywhere and g is a mere tracer.
At g = 0 everywhere this is exactly Chan's 'division well'; at g = 1 'division uncontrolled'.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from common import found_entry, nd


class GenomeLenia:
    SIGMA_G = 2.0

    def __init__(self, A, g, mut_amp=0.0, mut_every=10.0, mut_scale=8.0, seed=0, rule_g=None):
        self.rule_g = rule_g  # neutral control: the rule uses this constant, g is only carried and mutated
        self.well, self.wild = found_entry("213", 84)["params"], found_entry("213", 83)["params"]
        self.A = np.asarray(A, float).copy(); self.g = np.asarray(g, float).copy()
        N = self.A.shape
        w0 = nd.NDLenia(self.well, self.A[None]); w1 = nd.NDLenia(self.wild, self.A[None])
        self.k0, self.k1 = w0._khat, w1._khat
        self.dt = w0.dt
        self.m0 = np.array([p["m"] for p in self.well]); self.m1 = np.array([p["m"] for p in self.wild])
        self.s0 = np.array([p["s"] for p in self.well]); self.s1 = np.array([p["s"] for p in self.wild])
        self.mut_amp, self.mut_scale = mut_amp, mut_scale
        self.mut_steps = max(1, int(round(mut_every / self.dt)))
        self.rng = np.random.default_rng(seed); self.n = 0

    def step(self):
        A, g = self.A, self.g
        gr = g if self.rule_g is None else self.rule_g
        F = np.fft.rfft2(A)
        D = np.zeros_like(A)
        for k in range(len(self.k0)):
            u0 = np.fft.irfft2(F * self.k0[k], s=A.shape); u1 = np.fft.irfft2(F * self.k1[k], s=A.shape)
            U = (1 - gr) * u0 + gr * u1
            m = (1 - gr) * self.m0[k] + gr * self.m1[k]; s = (1 - gr) * self.s0[k] + gr * self.s1[k]
            D += nd.growth(1, U, m, s)
        An = np.clip(A + self.dt * D / len(self.k0), 0, 1)
        # inheritance: matter that already exists keeps its genome; newly grown matter takes the
        # mass-weighted genome of its neighbourhood (Gaussian SIGMA_G px)
        num = ndimage.gaussian_filter(A * g, self.SIGMA_G, mode="wrap")
        den = ndimage.gaussian_filter(A, self.SIGMA_G, mode="wrap")
        ghat = np.where(den > 1e-6, num / np.maximum(den, 1e-12), g)
        grow = np.maximum(An - A, 0)
        old = An - grow  # = min(A, An): the part of the new value that was already there
        g = np.where(An > 1e-9, (old * g + grow * ghat) / np.maximum(An, 1e-12), ghat)
        self.n += 1
        if self.mut_amp and self.n % self.mut_steps == 0:
            z = ndimage.gaussian_filter(self.rng.standard_normal(A.shape), self.mut_scale, mode="wrap")
            g = g + self.mut_amp * z / z.std()
        self.A, self.g = An, np.clip(g, 0, 1)
        return self.A
