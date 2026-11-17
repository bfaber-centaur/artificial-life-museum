"""POPGEN shared model: GenomeLenia with a two-type label and a choice of inheritance.

Each pixel carries a label L in [0, 1] (type 0 = resident, type 1 = mutant). The rule at a pixel is
GenomeLenia's at g = g0 + delta * L (delta = 0: the label is neutral). Inheritance, applied after
every growth step exactly as in REPLICATORS/genome.py:
  - "blend"  (genome.py's rule): new matter takes Lhat, the mass-weighted mean label of its
             neighbourhood (Gaussian SIGMA_G px), and the pixel's label is the mass-weighted mix
             of old and new. Labels become fractions: blending inheritance.
  - "part"   (particulate): new matter takes round(Lhat), the neighbourhood's majority type, and
             the pixel keeps whichever label (its old one or the new one) carries more of its mass.
             Labels stay exactly 0 or 1.
With delta = 0 and mode "blend" this is GenomeLenia with rule_g = g0 and g = L as a tracer.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "REPLICATORS"))
from common import found_entry, nd, state_hash  # noqa: E402,F401
import tree  # noqa: E402,F401


class TwoType:
    SIGMA_G = 2.0

    def __init__(self, A, L, g0, delta=0.0, mode="part"):
        assert mode in ("part", "blend")
        self.mode, self.g0, self.delta = mode, g0, delta
        self.well, self.wild = found_entry("213", 84)["params"], found_entry("213", 83)["params"]
        self.A = np.asarray(A, float).copy(); self.L = np.asarray(L, float).copy()
        w0 = nd.NDLenia(self.well, self.A[None]); w1 = nd.NDLenia(self.wild, self.A[None])
        self.k0, self.k1, self.dt = w0._khat, w1._khat, w0.dt
        self.m0 = np.array([p["m"] for p in self.well]); self.m1 = np.array([p["m"] for p in self.wild])
        self.s0 = np.array([p["s"] for p in self.well]); self.s1 = np.array([p["s"] for p in self.wild])
        self.n = 0

    def step(self):
        A, L = self.A, self.L
        gr = self.g0 + self.delta * L if self.delta else self.g0
        F = np.fft.rfft2(A)
        D = np.zeros_like(A)
        for k in range(len(self.k0)):
            u0 = np.fft.irfft2(F * self.k0[k], s=A.shape); u1 = np.fft.irfft2(F * self.k1[k], s=A.shape)
            U = (1 - gr) * u0 + gr * u1
            m = (1 - gr) * self.m0[k] + gr * self.m1[k]; s = (1 - gr) * self.s0[k] + gr * self.s1[k]
            D += nd.growth(1, U, m, s)
        An = np.clip(A + self.dt * D / len(self.k0), 0, 1)
        num = ndimage.gaussian_filter(A * L, self.SIGMA_G, mode="wrap")
        den = ndimage.gaussian_filter(A, self.SIGMA_G, mode="wrap")
        Lhat = np.where(den > 1e-6, num / np.maximum(den, 1e-12), L)
        grow = np.maximum(An - A, 0); old = An - grow
        if self.mode == "blend":
            L = np.where(An > 1e-9, (old * L + grow * Lhat) / np.maximum(An, 1e-12), Lhat)
        else:
            new = (Lhat > 0.5).astype(float)
            L = np.where(old >= grow, L, new)
            L = np.where(An > 1e-9, L, new)
        self.n += 1
        self.A, self.L = An, np.clip(L, 0, 1)
        return self.A

    # --- measurements ---
    def share(self):
        """Mass share of type 1 (blend: mass-weighted mean label)."""
        return float((self.A * self.L).sum() / max(self.A.sum(), 1e-12))

    def mixed(self):
        m = (self.L > 0.1) & (self.L < 0.9)
        return float(self.A[m].sum() / max(self.A.sum(), 1e-12))


def label_cells(A, p, rng, which=None):
    """Label whole cells: each tree.peaks cell (Voronoi region of its peak, on the torus) is type 1
    with probability p, or exactly the cells with indices in `which`. Returns (L, peaks, chosen)."""
    N = A.shape[0]
    P = tree.peaks(A)
    seeds = np.zeros(A.shape, dtype=int)
    for i, (y, x) in enumerate(P):
        seeds[int(y) % N, int(x) % N] = i + 1
    pad = N // 4
    big = np.pad(seeds, pad, mode="wrap")
    _, (iy, ix) = ndimage.distance_transform_edt(big == 0, return_indices=True)
    near = big[iy, ix][pad:-pad, pad:-pad]
    chosen = np.array(sorted(which)) if which is not None else np.flatnonzero(rng.random(len(P)) < p)
    lab = np.zeros(len(P) + 1); lab[chosen + 1] = 1.0
    return lab[near], P, chosen
