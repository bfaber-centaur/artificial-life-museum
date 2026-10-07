"""Lane 6 field-exploration engine: many classic Lenia worlds stepped together.

Semantics are ALM's (``alm.lenia``): the kernel is built by ``alm.lenia.kernel``
and growth by ``alm.lenia.growth``, Euler + clip, float64, periodic torus. The
only difference from ``alm.lenia.Lenia`` is that a stack of worlds sharing one
kernel radius is stepped in one batched FFT, with mu/sigma allowed to differ per
world. ``tests`` in this directory check it against ``alm.lenia.Lenia`` bitwise.

Per world we record mass and unwrapped periodic centroid every step, and a
morphology snapshot (gyradius, anisotropy, principal-axis angle, component
count, occupied area) every ``snap_every`` steps.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage

from alm.lenia import Rule, growth, kernel


def wrap(d, n):
    return (np.asarray(d) + n / 2) % n - n / 2


def centroids(B):
    """Periodic centroids (cx, cy) of a (W, ny, nx) stack; NaN for empty worlds."""
    W, ny, nx = B.shape
    phx = np.exp(2j * np.pi * np.arange(nx) / nx)
    phy = np.exp(2j * np.pi * np.arange(ny) / ny)
    zx = B.sum(1) @ phx
    zy = B.sum(2) @ phy
    cx = (np.angle(zx) % (2 * np.pi)) * nx / (2 * np.pi)
    cy = (np.angle(zy) % (2 * np.pi)) * ny / (2 * np.pi)
    empty = B.sum((1, 2)) <= 0
    cx[empty] = np.nan
    cy[empty] = np.nan
    return cx, cy


def components(A, threshold=0.1):
    """Connected components of A > threshold on the torus (8-connectivity)."""
    mask = A > threshold
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if n == 0:
        return 0
    parent = list(range(n + 1))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[a] = b

    ny, nx = A.shape
    for s in (-1, 0, 1):  # wrap columns and rows, including diagonal neighbours
        l, r = lab[:, -1], np.roll(lab[:, 0], s)
        for a, b in zip(l, r):
            if a and b:
                union(a, b)
        t, btm = lab[-1, :], np.roll(lab[0, :], s)
        for a, b in zip(t, btm):
            if a and b:
                union(a, b)
    return len({find(i) for i in range(1, n + 1)})


def morph(A, R):
    """Snapshot morphology of one world (lengths in R)."""
    ny, nx = A.shape
    m = A.sum()
    if m <= 0:
        return dict(gyr=np.nan, aniso=np.nan, axis=np.nan, ncomp=0, area=0.0)
    cx, cy = centroids(A[None])
    dx = wrap(np.arange(nx)[None, :] - cx[0], nx)
    dy = wrap(np.arange(ny)[:, None] - cy[0], ny)
    sxx = (A * dx * dx).sum() / m
    syy = (A * dy * dy).sum() / m
    sxy = (A * dx * dy).sum() / m
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    disc = np.sqrt(max(tr * tr / 4 - det, 0.0))
    l1, l2 = tr / 2 + disc, tr / 2 - disc
    return dict(
        gyr=float(np.sqrt(tr)) / R,
        aniso=float(1 - l2 / l1) if l1 > 0 else 0.0,
        axis=float(0.5 * np.degrees(np.arctan2(2 * sxy, sxx - syy))),
        ncomp=components(A),
        area=float((A > 0.1).mean()),
    )


@dataclass
class Batch:
    R: int
    T: float
    mu: np.ndarray
    sigma: np.ndarray
    kernel_name: str = "poly"
    growth_name: str = "poly"

    def __post_init__(self):
        self.mu = np.asarray(self.mu, dtype=np.float64)
        self.sigma = np.asarray(self.sigma, dtype=np.float64)

    def rule(self, i) -> Rule:
        return Rule(R=self.R, T=self.T, mu=float(self.mu[i]), sigma=float(self.sigma[i]),
                    kernel=self.kernel_name, growth=self.growth_name)

    def run(self, A0, steps, snap_every=100, snap_from=0, keep=()):
        """Step a (W, ny, nx) stack. Returns a dict of per-world series.

        ``keep``: steps at which to store full states."""
        B = np.array(A0, dtype=np.float64, copy=True)
        W, ny, nx = B.shape
        khat = np.fft.rfft2(kernel((ny, nx), self.rule(0)))
        mu = self.mu[:, None, None]
        sg = self.sigma[:, None, None]
        dt = 1.0 / self.T
        R2 = self.R**2
        mass = np.empty((steps + 1, W))
        pos = np.empty((steps + 1, W, 2))
        cx, cy = centroids(B)
        last = np.stack([cx, cy], 1)
        cur = last.copy()
        mass[0] = B.sum((1, 2)) / R2
        pos[0] = cur
        snaps, states = [], {}
        if 0 in keep:
            states[0] = B.copy()
        for t in range(1, steps + 1):
            U = np.fft.irfft2(np.fft.rfft2(B) * khat, s=(ny, nx))
            B = np.clip(B + growth(self.growth_name, U, mu, sg) * dt, 0.0, 1.0)
            cx, cy = centroids(B)
            c = np.stack([cx, cy], 1)
            ok = ~np.isnan(c[:, 0]) & ~np.isnan(last[:, 0])
            d = np.zeros_like(c)
            d[ok, 0] = wrap(c[ok, 0] - last[ok, 0], nx)
            d[ok, 1] = wrap(c[ok, 1] - last[ok, 1], ny)
            cur = cur + d
            last = np.where(np.isnan(c), last, c)
            mass[t] = B.sum((1, 2)) / R2
            pos[t] = cur
            if t >= snap_from and t % snap_every == 0:
                snaps.append((t, [morph(B[i], self.R) for i in range(W)]))
            if t in keep:
                states[t] = B.copy()
        return dict(mass=mass, pos=pos, snaps=snaps, final=B, states=states)


def summarize(res, R, T, window):
    """Per-world summary over the last ``window`` steps."""
    mass, pos, snaps = res["mass"], res["pos"], res["snaps"]
    n, W = mass.shape[0] - 1, mass.shape[1]
    w0 = n - window
    out = []
    S001_MASS = 0.4358
    for i in range(W):
        m = mass[w0:, i]
        fin = res["final"][i]
        sn = [s[i] for t, s in snaps if t >= w0]
        last = sn[-1] if sn else morph(fin, R)
        d = dict(mass_mean=float(m.mean()), mass_rsd=float(m.std() / m.mean()) if m.mean() > 0 else np.nan,
                 mass_final=float(mass[-1, i]))
        p = pos[w0:, i]
        disp = p[-1] - p[0]
        d["speed"] = float(np.hypot(*disp) / R / (window / T))  # net, R per time unit
        steps_len = np.hypot(*np.diff(p, axis=0).T).sum()
        d["path_speed"] = float(steps_len / R / (window / T))
        d["straightness"] = float(np.hypot(*disp) / steps_len) if steps_len > 0 else np.nan
        d["heading"] = float(np.degrees(np.arctan2(disp[1], disp[0])))
        for k in ("gyr", "aniso", "ncomp", "area"):
            d[k] = last[k]
        d["ncomp_max"] = max((s["ncomp"] for s in sn), default=last["ncomp"])
        d["ncomp_min"] = min((s["ncomp"] for s in sn), default=last["ncomp"])
        # turning rate of the 1-time-unit velocity (deg per time unit) and its spread
        lag = max(1, int(round(T)))
        if len(p) > 2 * lag:
            v = p[lag:] - p[:-lag]
            sp = np.hypot(*v.T)
            if sp.min() > 1e-6:
                ang = np.unwrap(np.arctan2(v[:, 1], v[:, 0]))
                d["turn_rate"] = float(np.degrees(ang[-1] - ang[0]) / ((len(ang) - 1) / T))
            else:
                d["turn_rate"] = np.nan
        else:
            d["turn_rate"] = np.nan
        # principal-axis rotation rate (deg per time unit), mod-180 unwrapped. Sampled every
        # snap_every steps, so it aliases for anything turning faster than 90 deg per snapshot.
        ax = np.array([s["axis"] for s in sn])
        if len(ax) > 2 and not np.isnan(ax).any():
            un = np.degrees(np.unwrap(np.radians(ax) * 2) / 2)
            d["axis_rate"] = float((un[-1] - un[0]) / ((len(ax) - 1) * (snaps[1][0] - snaps[0][0]) / T))
        else:
            d["axis_rate"] = np.nan
        # fate
        if d["mass_final"] < 0.01:
            fate = "died"
        elif d["area"] > 0.25 or d["mass_final"] > 30 * S001_MASS:
            fate = "filled"
        else:
            fate = "localized"
        d["fate"] = fate
        out.append(d)
    return out
