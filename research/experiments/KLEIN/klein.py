"""Classic Lenia on a Klein bottle, exactly, with the museum's own FFT simulator.

A Klein bottle of width Nx and height Ny is the Nx x Ny rectangle with the left and right edges
glued straight (x ~ x + Nx) and the top and bottom edges glued with a flip ((x, y + Ny) ~ (-x, y)).
Its double cover is the ordinary Nx x 2Ny torus with the glide-reflection symmetry
A[y + Ny, x] = A[y, -x mod Nx]. The radial kernel commutes with that symmetry, so stepping the
doubled torus with alm.lenia and then re-imposing the symmetry (copying the mirrored lower half
over the upper half, which only removes round-off) is classic Lenia on the Klein bottle.

Run on the torus of the same Nx x Ny for the control (`Torus`).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from alm.lenia import Lenia


def mirror_x(A):
    """x -> -x mod Nx on the last axis."""
    return np.roll(A[..., ::-1], 1, axis=-1)


class Klein:
    """Klein bottle Nx x Ny. ``A`` is the fundamental domain (Ny, Nx); ``full`` the double cover."""

    kind = "klein"

    def __init__(self, rule, A):
        A = np.asarray(A, dtype=np.float64)
        self.ny, self.nx = A.shape
        self.L = Lenia(rule, np.vstack([A, mirror_x(A)]))
        self.t = 0

    @property
    def A(self):
        return self.L.A[: self.ny]

    @property
    def full(self):
        return self.L.A

    def step(self):
        self.L.step()
        self.L.A[self.ny:] = mirror_x(self.L.A[: self.ny])
        self.t += 1

    def asymmetry(self):
        return float(np.abs(self.L.A[self.ny:] - mirror_x(self.L.A[: self.ny])).max())


class Torus:
    kind = "torus"

    def __init__(self, rule, A):
        self.L = Lenia(rule, np.asarray(A, dtype=np.float64))
        self.ny, self.nx = self.L.A.shape
        self.t = 0

    @property
    def A(self):
        return self.L.A

    @property
    def full(self):
        return self.L.A

    def step(self):
        self.L.step()
        self.t += 1


def place(cells, shape, yx, k=0, flip=False):
    """Paste S-cells (levels/255) centred at (y, x), rotated by k quarter turns, optionally mirrored."""
    c = np.rot90(cells / 255.0, k)
    if flip:
        c = c[:, ::-1]
    A = np.zeros(shape)
    h, w = c.shape
    ys = (np.arange(h) + int(yx[0]) - h // 2) % shape[0]
    xs = (np.arange(w) + int(yx[1]) - w // 2) % shape[1]
    A[np.ix_(ys, xs)] = np.maximum(A[np.ix_(ys, xs)], c)
    return A


def bodies(A, thr=0.05, min_mass=1.0):
    """Connected bodies on a torus array (periodic in both axes): list of (mask, mass)."""
    lab, n = ndimage.label(A > thr)
    if n == 0:
        return []
    # merge labels across the periodic edges
    parent = list(range(n + 1))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b in ((lab[0], lab[-1]), (lab[:, 0], lab[:, -1])):
        for p, q in zip(a, b):
            if p and q:
                parent[find(p)] = find(q)
    roots = np.array([find(i) for i in range(n + 1)])
    lab = roots[lab]
    out = []
    for r in np.unique(lab):
        if r == 0:
            continue
        m = lab == r
        mm = float(A[m].sum())
        if mm >= min_mass:
            out.append((m, mm))
    return out


def centroid(A, mask=None):
    """Circular-mean centroid (y, x) on a torus array."""
    w = A if mask is None else A * mask
    s = w.sum()
    if s <= 0:
        return None
    out = []
    for ax, n in ((0, A.shape[0]), (1, A.shape[1])):
        ang = 2 * np.pi * np.arange(n) / n
        prof = w.sum(axis=1 - ax)
        z = (prof * np.exp(1j * ang)).sum() / s
        out.append((np.angle(z) % (2 * np.pi)) * n / (2 * np.pi))
    return np.array(out)


def wrap(d, n):
    return (d + n / 2) % n - n / 2


def partners(A, thr=0.5):
    """The two densest cores of a bound pair (S101): list of centroid (y, x), by core mass."""
    out = []
    for m, mm in sorted(bodies(A, thr=thr, min_mass=0.5), key=lambda b: -b[1])[:2]:
        out.append(centroid(A, m))
    return out


def handedness(A, prev_c, c, R=13):
    """Signed stagger of a bound pair, in R: (left core - right core) . heading, where 'left' is
    to the left of the heading in the chart (y down). Mirror images have opposite signs."""
    shape = np.array(A.shape)
    v = wrap(c - prev_c, shape)
    v = v / np.hypot(*v)
    n = np.array([-v[1], v[0]])  # chart-left of heading (y, x)
    ps = partners(A)
    if len(ps) < 2:
        return None
    d = [wrap(p - c, shape) for p in ps]
    left, right = (d[0], d[1]) if d[0] @ n > d[1] @ n else (d[1], d[0])
    return float((left - right) @ v / R)
