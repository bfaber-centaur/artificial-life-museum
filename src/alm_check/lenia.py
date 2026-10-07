"""Minimal classic 2-D Lenia with two convolution paths.

Semantics (upstream LeniaND.py @ adfc542, as executed):
  r       = |x - x0| / R, kernel nonzero only for r < 1
  shell   = core((B*r) mod 1) * b[floor(B*r)], normalised to sum 1
  U       = K * A                                (circular or zero-padded)
  A'      = clip(A + G(U) / T, 0, 1)             (explicit Euler)

Paths:
  "fft"     periodic torus via rfft2 of a wrap-distance kernel (no fftshift).
  "direct"  real-space correlation with a (2R+1)^2 stencil, using
            scipy.ndimage; boundary "wrap" (torus) or "constant" (dead
            zero-padded edge). No FFT anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
from scipy import ndimage

REPO = Path(__file__).resolve().parents[2]
ORBIUM_RLE = (
    "7.MD6.qL$6.pKqEqFURpApBRAqQ$5.VqTrSsBrOpXpWpTpWpUpCrQ$4.CQrQsTsWsApITNPpGqGvL$"
    "3.IpIpWrOsGsBqXpJ4.LsFrL$A.DpKpSpJpDqOqUqSqE5.ExD$qL.pBpTT2.qCrGrVrWqM5.sTpP$"
    ".pGpWpD3.qUsMtItQtJ6.tL$.uFqGH3.pXtOuR2vFsK5.sM$.tUqL4.GuNwAwVxBwNpC4.qXpA$"
    "2.uH5.vBxGyEyMyHtW4.qIpL$2.wV5.tIyG3yOxQqW2.FqHpJ$2.tUS4.rM2yOyJyOyHtVpPMpFqNV$"
    "2.HsR4.pUxAyOxLxDxEuVrMqBqGqKJ$3.sLpE3.pEuNxHwRwGvUuLsHrCqTpR$"
    "3.TrMS2.pFsLvDvPvEuPtNsGrGqIP$4.pRqRpNpFpTrNtGtVtStGsMrNqNpF$"
    "5.pMqKqLqRrIsCsLsIrTrFqJpHE$6.RpSqJqPqVqWqRqKpRXE$8.OpBpIpJpFTK!"
)


def decode_rle(rle: str) -> np.ndarray:
    """Decode a 2-D Lenia RLE string to integer levels 0..255 (rows = y)."""
    rows, row, count, prefix = [], [], "", ""
    for ch in rle.rstrip("!") + "$":
        if ch.isdigit():
            count += ch
        elif ch in "pqrstuvwxy":
            prefix = ch
        elif ch == "$":
            rows.append(row)
            rows.extend([[]] * (int(count) - 1 if count else 0))
            row, count, prefix = [], "", ""
        else:
            if ch == ".":
                v = 0
            elif prefix:
                v = (ord(prefix) - ord("p")) * 24 + (ord(ch) - ord("A") + 25)
            else:
                v = ord(ch) - ord("A") + 1
            row.extend([v] * (int(count) if count else 1))
            count, prefix = "", ""
    width = max(len(r) for r in rows)
    return np.array([r + [0] * (width - len(r)) for r in rows], dtype=np.int64)


def load_orbium() -> np.ndarray:
    """S001 Orbium cells as floats in [0, 1] (20 x 20)."""
    return decode_rle(ORBIUM_RLE) / 255.0


def place(cells: np.ndarray, n: int, dtype=np.float64) -> np.ndarray:
    """Centre ``cells`` on an n x n zero world (upstream Board.add offset)."""
    a = np.zeros((n, n), dtype=dtype)
    h, w = cells.shape
    y0, x0 = (n - h) // 2, (n - w) // 2
    a[y0 : y0 + h, x0 : x0 + w] = cells
    return a


def kernel_core(r: np.ndarray, kind: str) -> np.ndarray:
    r = np.asarray(r, dtype=np.float64)
    if kind == "poly":
        return (4.0 * r * (1.0 - r)) ** 4
    if kind == "exp":
        out = np.zeros_like(r)
        m = (r > 0) & (r < 1)
        out[m] = np.exp(4.0 - 1.0 / (r[m] * (1.0 - r[m])))
        return out
    raise ValueError(kind)


def growth(u: np.ndarray, mu: float, sigma: float, kind: str) -> np.ndarray:
    if kind == "poly":
        return 2.0 * np.maximum(0.0, 1.0 - (u - mu) ** 2 / (9.0 * sigma**2)) ** 4 - 1.0
    if kind == "exp":
        return 2.0 * np.exp(-((u - mu) ** 2) / (2.0 * sigma**2)) - 1.0
    raise ValueError(kind)


@dataclass(frozen=True)
class Rule:
    R: float = 13
    T: float = 10
    mu: float = 0.15
    sigma: float = 0.015
    b: tuple = (1.0,)
    core: str = "poly"
    growth: str = "poly"

    def with_(self, **kw) -> "Rule":
        return replace(self, **kw)


def shell(dist: np.ndarray, rule: Rule) -> np.ndarray:
    r = dist / rule.R
    B = len(rule.b)
    br = B * r
    idx = np.minimum(np.floor(br).astype(int), B - 1)
    bs = np.asarray(rule.b, dtype=np.float64)[idx]
    return (r < 1) * kernel_core(np.minimum(br % 1, 1), rule.core) * bs


@dataclass
class World:
    """A Lenia world. ``path`` is "fft" or "direct"; ``boundary`` is "wrap" or "constant"."""

    A: np.ndarray
    rule: Rule
    path: str = "fft"
    boundary: str = "wrap"
    t: int = 0
    _K: np.ndarray = field(default=None, repr=False)

    def __post_init__(self):
        n0, n1 = self.A.shape
        if self.path == "fft":
            if self.boundary != "wrap":
                raise ValueError("fft path is periodic only")
            dy = np.minimum(np.arange(n0), n0 - np.arange(n0))[:, None]
            dx = np.minimum(np.arange(n1), n1 - np.arange(n1))[None, :]
            k = shell(np.sqrt(dx**2 + dy**2), self.rule)
            k /= k.sum()
            self._K = np.fft.rfft2(k)
        elif self.path == "direct":
            rr = int(np.ceil(self.rule.R))
            d = np.arange(-rr, rr + 1)
            k = shell(np.sqrt(d[None, :] ** 2 + d[:, None] ** 2), self.rule)
            self._K = (k / k.sum()).astype(self.A.dtype)
        else:
            raise ValueError(self.path)

    def potential(self) -> np.ndarray:
        if self.path == "fft":
            K = self._K.astype(np.complex64) if self.A.dtype == np.float32 else self._K
            return np.fft.irfft2(np.fft.rfft2(self.A) * K, s=self.A.shape).astype(self.A.dtype)
        return ndimage.correlate(self.A, self._K, mode=self.boundary, cval=0.0)

    def field(self) -> np.ndarray:
        r = self.rule
        return growth(self.potential(), r.mu, r.sigma, r.growth).astype(self.A.dtype)

    def step(self) -> np.ndarray:
        """Advance one Euler step; returns the growth field used."""
        G = self.field()
        dt = self.A.dtype.type(1.0 / self.rule.T)
        self.A = np.clip(self.A + dt * G, 0, 1)
        self.t += 1
        return G


# ---------------------------------------------------------------- metrics


def periodic_centroid(A: np.ndarray) -> tuple[float, float]:
    """(cy, cx) as circular means; robust to wrapping."""
    out = []
    for axis in (0, 1):
        n = A.shape[axis]
        w = A.sum(axis=1 - axis)
        th = 2 * np.pi * np.arange(n) / n
        c, s = (w * np.cos(th)).sum(), (w * np.sin(th)).sum()
        out.append((np.arctan2(s, c) % (2 * np.pi)) * n / (2 * np.pi))
    return out[0], out[1]


def gyradius(A: np.ndarray, cy: float, cx: float) -> float:
    n0, n1 = A.shape
    dy = (np.arange(n0) - cy + n0 / 2) % n0 - n0 / 2
    dx = (np.arange(n1) - cx + n1 / 2) % n1 - n1 / 2
    d2 = dy[:, None] ** 2 + dx[None, :] ** 2
    m = A.sum()
    return float(np.sqrt((A * d2).sum() / m)) if m > 0 else float("nan")


def recentre(A: np.ndarray) -> np.ndarray:
    """Roll the world so the periodic centroid sits on the middle cell."""
    cy, cx = periodic_centroid(A)
    n0, n1 = A.shape
    return np.roll(A, (n0 // 2 - int(round(cy)), n1 // 2 - int(round(cx))), (0, 1))


def run(
    world: World,
    steps: int,
    every: int = 1,
    keep_states: tuple = (),
) -> dict:
    """Step ``world`` and record a trace. Metrics use upstream units (per R^2, R, time)."""
    R, T = world.rule.R, world.rule.T
    n0, n1 = world.A.shape
    rows = []
    states = {}
    cy, cx = periodic_centroid(world.A)
    prev = (cy, cx)
    rows.append(dict(step=0, mass=world.A.sum() / R**2, growth=np.nan,
                     gyradius=gyradius(world.A, cy, cx) / R, cy=cy, cx=cx,
                     vy=np.nan, vx=np.nan, alive=1))
    if 0 in keep_states:
        states[0] = world.A.copy()
    for s in range(1, steps + 1):
        G = world.step()
        if s in keep_states:
            states[s] = world.A.copy()
        if s % every:
            continue
        A = world.A
        m = A.sum()
        alive = int(m / R**2 > 1e-10)
        if alive:
            cy, cx = periodic_centroid(A)
            dy = (cy - prev[0] + n0 / 2) % n0 - n0 / 2
            dx = (cx - prev[1] + n1 / 2) % n1 - n1 / 2
            prev = (cy, cx)
            g = gyradius(A, cy, cx) / R
        else:
            cy = cx = dy = dx = g = np.nan
        rows.append(dict(step=s, mass=m / R**2, growth=np.maximum(G, 0).sum() / R**2,
                         gyradius=g, cy=cy, cx=cx, vy=dy / every, vx=dx / every, alive=alive))
        if not alive:
            break
    cols = {k: np.array([r[k] for r in rows], dtype=float) for k in rows[0]}
    cols["speed"] = np.hypot(cols["vx"], cols["vy"]) * T / R  # R per unit time
    cols["states"] = states
    return cols
