"""ZOO: collision harness for catalogued Lenia creatures that share one rule.

A "world" is one classic Lenia rule (alm.lenia.Rule). Every creature in a world lives under
exactly that rule, so two of them can be put on one torus and collided without changing the
physics. The harness:

1. settles each creature alone (``settle``), measuring its mass and velocity;
2. builds a rotated, re-settled copy for every heading it needs (``Body``);
3. places two bodies so that their straight-line paths, in the relative frame, pass at a
   chosen impact parameter ``b`` (in units of R) at a chosen contact time (``place_pair``);
4. runs the collision and classifies the products at a fixed time after contact
   (``classify``).

Everything is deterministic: seeds come from the pinned catalogue, rotations use
scipy.ndimage.rotate(order=1), and the engine is alm.lenia.Lenia (float64 FFT).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage

from alm.lenia import Lenia, Rule
from alm.specimens import from_catalog

THETA = 0.1  # support threshold for components


# --- components on the torus -------------------------------------------------------------


def components(A: np.ndarray, theta: float = THETA, floor: float = 0.0):
    """Connected components of A >= theta on the torus.

    Returns a list of dicts with mass (sum of A over the component, in cells), centroid
    (y, x) on the torus (circular mean), and the cell mask, sorted by mass, heaviest first.
    Components whose mass is below ``floor`` are dropped.
    """
    mask = A >= theta
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if n == 0:
        return []
    # merge labels that touch across the periodic edges
    parent = list(range(n + 1))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    ny, nx = A.shape
    for a_edge, b_edge in ((lab[0, :], lab[-1, :]), (lab[:, 0], lab[:, -1])):
        for shift in (-1, 0, 1):
            bb = np.roll(b_edge, shift)
            m = (a_edge > 0) & (bb > 0)
            for i, j in zip(a_edge[m], bb[m]):
                union(int(i), int(j))
    roots = np.array([find(i) for i in range(n + 1)])
    lab = roots[lab]
    out = []
    yy, xx = np.indices(A.shape)
    for r in np.unique(lab[lab > 0]):
        m = lab == r
        w = A[m]
        mass = float(w.sum())
        if mass < floor:
            continue
        cy = _circ_mean(yy[m], w, ny)
        cx = _circ_mean(xx[m], w, nx)
        out.append({"mass": mass, "c": (cy, cx), "mask": m, "cells": int(m.sum())})
    out.sort(key=lambda d: -d["mass"])
    return out


def _circ_mean(pos, w, n):
    ang = 2 * np.pi * pos / n
    s = np.sum(w * np.sin(ang))
    c = np.sum(w * np.cos(ang))
    return float((np.arctan2(s, c) * n / (2 * np.pi)) % n)


def centroid(A):
    ny, nx = A.shape
    yy, xx = np.indices(A.shape)
    w = A.ravel()
    return _circ_mean(yy.ravel(), w, ny), _circ_mean(xx.ravel(), w, nx)


def torus_delta(p, q, shape):
    """Shortest displacement q - p on the torus, as (dy, dx)."""
    d = []
    for a, b, n in zip(p, q, shape):
        x = (b - a + n / 2) % n - n / 2
        d.append(x)
    return np.array(d)


def sha(A):
    return hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()


# --- creatures ---------------------------------------------------------------------------


def crop(A, c, half):
    """Square patch of side 2*half+1 centred (rounded) on c, wrapping around the torus."""
    cy, cx = int(round(c[0])), int(round(c[1]))
    iy = (np.arange(cy - half, cy + half + 1)) % A.shape[0]
    ix = (np.arange(cx - half, cx + half + 1)) % A.shape[1]
    return A[np.ix_(iy, ix)].copy()


def stamp(A, patch, c):
    """Add a patch centred on c (rounded) into A, wrapping. Returns A (modified)."""
    h, w = patch.shape
    cy, cx = int(round(c[0])), int(round(c[1]))
    iy = (np.arange(h) - h // 2 + cy) % A.shape[0]
    ix = (np.arange(w) - w // 2 + cx) % A.shape[1]
    A[np.ix_(iy, ix)] += patch
    return A


def heading_deg(v):
    """Heading of a (vy, vx) velocity in degrees, counter-clockwise from +x with y down."""
    return float(math.degrees(math.atan2(-v[0], v[1])) % 360)


@dataclass
class Body:
    """A settled creature: its patch (centred), mass, velocity (cells / tu) and heading."""

    world: str
    code: str
    name: str
    rot: float
    patch: np.ndarray = field(repr=False)
    mass: float
    v: tuple
    alive: bool
    note: str = ""

    @property
    def speed(self):
        return float(math.hypot(*self.v))

    @property
    def heading(self):
        return heading_deg(self.v) if self.speed > 0.05 else None


def settle(rule: Rule, A: np.ndarray, tu_settle: float, tu_measure: float = 10.0):
    """Run A alone for tu_settle, then tu_measure more; return (A_final, mass, v, alive)."""
    w = Lenia(rule, A)
    steps = int(round(tu_settle * rule.T))
    for _ in range(steps):
        w.step()
    m0 = float(w.A.sum())
    c0 = centroid(w.A)
    A_mid = w.A.copy()
    for _ in range(int(round(tu_measure * rule.T))):
        w.step()
    c1 = centroid(w.A)
    d = torus_delta(c0, c1, w.A.shape)
    v = (float(d[0] / tu_measure), float(d[1] / tu_measure))
    comps = components(w.A, floor=0.05 * max(m0, 1e-9))
    alive = m0 > 1.0 and len(comps) >= 1
    return w.A, float(w.A.sum()), v, alive, comps


def make_body(world: str, rule: Rule, code: str, patch0: np.ndarray, rot: float, N: int,
              tu_settle: float, half: int, name: str = "") -> Body:
    """Rotate a settled patch by ``rot`` degrees, settle it alone on an N² torus, recrop."""
    p = ndimage.rotate(patch0, rot, reshape=False, order=1, mode="constant") if rot else patch0
    p = np.clip(p, 0, 1)
    A = np.zeros((N, N))
    stamp(A, p, (N // 2, N // 2))
    A, mass, v, alive, comps = settle(rule, A, tu_settle)
    note = ""
    if alive and len(comps) > 1:
        note = f"{len(comps)} components after settling"
    c = comps[0]["c"] if comps else (N // 2, N // 2)
    patch = crop(A, c, half)
    lost = mass - float(patch.sum())
    if lost > 0.02 * mass:
        note += f" crop loses {lost / mass:.1%}"
    return Body(world, code, name, rot, patch, float(patch.sum()), v, alive, note.strip())


# --- pairs -------------------------------------------------------------------------------


def place_pair(A_body: Body, B_body: Body, b_R: float, R: int, N: int, gap_R: float = 2.5,
               t_min: float = 6.0):
    """Initial state with A and B on straight-line paths that pass at impact parameter b.

    Relative velocity w = vB - vA. In the relative frame B starts at r0 = b n - w t_c, where
    n is the unit normal to w (rotated +90 deg) and t_c is the time to closest approach,
    chosen so that the starting surface gap is about gap_R * R. If both bodies are static
    (|w| ~ 0), they are placed side by side at distance ``gap_R`` R plus their sizes.
    Returns (A0, info).
    """
    vA = np.array(A_body.v)
    vB = np.array(B_body.v)
    w = vB - vA
    sizeA = _radius(A_body.patch)
    sizeB = _radius(B_body.patch)
    sep = sizeA + sizeB + gap_R * R  # starting centre distance
    ws = float(np.hypot(*w))
    if ws < 0.2:
        r0 = np.array([0.0, sep])
        tc = None
    else:
        n = np.array([w[1], -w[0]]) / ws  # (vy, vx) -> normal
        b = b_R * R
        along = math.sqrt(max(sep**2 - b**2, 0.0))
        tc = max(along / ws, t_min)
        r0 = b * n - w * tc
    # centre of mass of the pair at the world centre at contact time
    c = np.array([N / 2, N / 2])
    pA = c - 0.5 * r0 - (vA * tc if tc else 0)
    pB = c + 0.5 * r0 - (vA * tc if tc else 0)
    # shift so the midpoint at contact is the world centre
    if tc:
        midc = 0.5 * ((pA + vA * tc) + (pB + vB * tc))
        pA += c - midc
        pB += c - midc
    A0 = np.zeros((N, N))
    stamp(A0, A_body.patch, pA)
    stamp(A0, B_body.patch, pB)
    A0 = np.clip(A0, 0, 1)
    return A0, {"tc": tc, "pA": pA.tolist(), "pB": pB.tolist(), "w": w.tolist(), "sep": sep}


def _radius(patch, theta=THETA):
    ys, xs = np.nonzero(patch >= theta)
    if len(ys) == 0:
        return 0.0
    cy, cx = patch.shape[0] // 2, patch.shape[1] // 2
    return float(np.max(np.hypot(ys - cy, xs - cx)))


# --- outcomes ----------------------------------------------------------------------------

CLASSES = ("ANNIHILATE", "SURVIVOR", "FUSE", "SCATTER", "MISS", "MULTIPLY", "EXPLODE")


def classify(frames, times, mA, mB, R, tc):
    """Classify a collision from a list of states (frames) at times (tu).

    Uses the last frame for products and the last 5 tu to estimate product velocities.
    Masses are compared with the parents' settled masses mA, mB (cells).
    """
    A = frames[-1]
    M = float(A.sum())
    m_tot = mA + mB
    floor = 0.15 * min(mA, mB)
    comps = components(A, floor=floor)
    # merged ever? a single component in some frame between start and end
    merged = False
    for F in frames[1:]:
        cs = components(F, floor=floor)
        if len(cs) <= 1:
            merged = True
            break
    # velocities: match each final component to the nearest component 5 tu earlier
    prev = components(frames[-2], floor=floor) if len(frames) > 1 else []
    dt = times[-1] - times[-2] if len(frames) > 1 else 1.0
    prods = []
    for c in comps:
        v = None
        if prev:
            ds = [torus_delta(p["c"], c["c"], A.shape) for p in prev]
            j = int(np.argmin([np.hypot(*d) for d in ds]))
            d = ds[j]
            if np.hypot(*d) < 3 * R:
                v = (float(d[0] / dt), float(d[1] / dt))
        prods.append({"mass": c["mass"], "c": c["c"], "v": v, "cells": c["cells"]})
    big = max(mA, mB)
    if M < 0.15 * min(mA, mB):
        cls = "ANNIHILATE"
    elif M > 2.0 * m_tot or sum(p["cells"] for p in prods) > 0.25 * A.size:
        cls = "EXPLODE"
    elif len(prods) >= 3:
        cls = "MULTIPLY"
    elif len(prods) == 2:
        cls = "SCATTER" if merged else "MISS"
        # products that are not like the parents count as a transformation
    elif len(prods) == 1:
        p = prods[0]["mass"]
        cls = "FUSE" if p > 1.3 * big else "SURVIVOR"
    else:
        cls = "ANNIHILATE"
    return {"class": cls, "mass_ratio": M / m_tot, "n": len(prods), "merged": merged,
            "products": prods}


def run_collision(rule: Rule, A0: np.ndarray, tu_total: float, every_tu: float = 5.0,
                  film_every_tu: float | None = None):
    """Run and return (frames, times, film) where frames are every ``every_tu``."""
    w = Lenia(rule, A0)
    frames = [w.A.copy()]
    times = [0.0]
    film = [w.A.astype(np.float32)] if film_every_tu else None
    k = int(round(every_tu * rule.T))
    kf = int(round(film_every_tu * rule.T)) if film_every_tu else None
    steps = int(round(tu_total * rule.T))
    for s in range(1, steps + 1):
        w.step()
        if s % k == 0:
            frames.append(w.A.copy())
            times.append(s / rule.T)
        if kf and s % kf == 0:
            film.append(w.A.astype(np.float32))
    return frames, times, film
