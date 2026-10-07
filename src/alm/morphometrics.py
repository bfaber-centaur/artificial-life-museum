"""Interpretable morphometric and behavioural features of a Lenia state.

Lane 5 (Morphometrics / Behaviour). Every function here is pure: it takes numpy
arrays (and plain numbers) and returns numbers or arrays. Nothing steps the
simulator, so Lane 2's runner, Lane 4's assay and Lane 3's cross-checks can all
call the same definitions. It deliberately does not import the simulator or
Lane 2's ``alm.measure`` trace-column registry; a thin ``@register`` adapter
there can expose :func:`snapshot` as a feature set.

Conventions
-----------
* A state ``A`` is a 2-D array indexed ``A[y, x]`` (rows = y, columns = x, image
  y-down), values in [0, 1], on a **periodic torus** of shape ``(Ny, Nx)``.
* Positions are ``(y, x)`` pairs in cell units. Lengths are in cells unless a
  function takes ``R`` (kernel radius), in which case the result is in units
  of R (the upstream Lenia convention, e.g. mass ``sum(A) / R**2``).
* Time is in simulator steps unless a function takes ``T`` (steps per unit
  time); then it is in Lenia time units (``t = step / T``).
* Spatial features are measured about the periodic centroid using
  minimum-image offsets, so they assume the organism spans less than half the
  grid in each direction. :func:`wrap_extent` reports when that fails.

The set is deliberately small (charter Lane 5): mass, centroid, velocity,
radius / second moment, anisotropy, rotational harmonics, occupied area,
dominant period and recovery time.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np

__all__ = [
    "mass",
    "centroid",
    "min_image",
    "offsets",
    "displacement",
    "velocity",
    "second_moment",
    "gyradius",
    "anisotropy",
    "rotational_harmonics",
    "symmetry_order",
    "occupied_area",
    "wrap_extent",
    "dominant_period",
    "recovery_time",
    "snapshot",
]


# --- size -------------------------------------------------------------------


def mass(A: np.ndarray, R: float = 1.0) -> float:
    """Total mass ``sum(A) / R**2`` (upstream ``m`` units when R is the kernel radius)."""
    return float(np.sum(A)) / R**2


def occupied_area(A: np.ndarray, threshold: float = 0.1, R: float = 1.0) -> float:
    """Number of cells with value strictly above ``threshold``, divided by ``R**2``.

    The threshold is a fixed convention, not a fit; 0.1 is the default so that
    faint numerical haze does not count as body.
    """
    return float(np.count_nonzero(A > threshold)) / R**2


# --- position on the torus --------------------------------------------------


def min_image(d, n: float):
    """Map a coordinate difference to the minimum image in ``[-n/2, n/2)``."""
    return (np.asarray(d, dtype=float) + n / 2) % n - n / 2


def _circular_mean(weights: np.ndarray, n: int) -> float:
    ang = 2 * np.pi * np.arange(n) / n
    z = np.sum(weights * np.exp(1j * ang))
    return (np.angle(z) % (2 * np.pi)) * n / (2 * np.pi)


def centroid(A: np.ndarray, iterations: int = 3) -> tuple[float, float]:
    """Mass centroid ``(cy, cx)`` on the periodic grid, in cells, in ``[0, N)``.

    Starts from the circular mean of each axis' marginal (robust to wrapping),
    then refines with the linear centroid of minimum-image offsets about that
    estimate. The refinement removes the circular mean's bias for asymmetric
    bodies; it is exact for any organism narrower than half the grid.

    Raises ``ValueError`` on an empty state.
    """
    A = np.asarray(A, dtype=float)
    total = A.sum()
    if not total > 0:
        raise ValueError("centroid of an empty state is undefined")
    ny, nx = A.shape
    py, px = A.sum(axis=1), A.sum(axis=0)
    cy, cx = _circular_mean(py, ny), _circular_mean(px, nx)
    iy, ix = np.arange(ny), np.arange(nx)
    for _ in range(iterations):
        cy = cy + np.sum(py * min_image(iy - cy, ny)) / total
        cx = cx + np.sum(px * min_image(ix - cx, nx)) / total
    return float(cy % ny), float(cx % nx)


def offsets(shape: Sequence[int], center: Sequence[float]):
    """Minimum-image offset grids ``(dy, dx)`` of every cell from ``center``."""
    ny, nx = shape
    dy = min_image(np.arange(ny)[:, None] - center[0], ny)
    dx = min_image(np.arange(nx)[None, :] - center[1], nx)
    return np.broadcast_to(dy, shape), np.broadcast_to(dx, shape)


def displacement(c0: Sequence[float], c1: Sequence[float], shape: Sequence[int]):
    """Minimum-image displacement ``(dy, dx)`` from centroid ``c0`` to ``c1``."""
    return (float(min_image(c1[0] - c0[0], shape[0])), float(min_image(c1[1] - c0[1], shape[1])))


def velocity(
    centroids: Sequence[Sequence[float]],
    shape: Sequence[int],
    every: int = 1,
    T: float = 1.0,
    R: float = 1.0,
) -> np.ndarray:
    """Per-interval velocity from a sequence of centroids sampled every ``every`` steps.

    Returns an array of shape ``(len(centroids) - 1, 2)`` holding ``(vy, vx)``
    in units of ``R`` per Lenia time unit (with the defaults: cells per step).
    Speed is ``np.hypot(vy, vx)``; heading is ``np.degrees(np.arctan2(vy, vx))``
    (from +x toward +y, image y-down).

    The sampling interval must keep the true displacement per sample below
    half the grid, otherwise the minimum image aliases (see the S001 dossier:
    ``--every 250`` gave a wrong speed).
    """
    c = np.asarray(centroids, dtype=float)
    if c.ndim != 2 or c.shape[1] != 2:
        raise ValueError("centroids must be a sequence of (cy, cx) pairs")
    d = np.stack(
        [min_image(np.diff(c[:, 0]), shape[0]), min_image(np.diff(c[:, 1]), shape[1])],
        axis=1,
    )
    return d / R / (every / T)


# --- shape ------------------------------------------------------------------


def second_moment(A: np.ndarray, center: Sequence[float] | None = None, R: float = 1.0) -> np.ndarray:
    """Mass-weighted 2x2 covariance ``[[Iyy, Iyx], [Ixy, Ixx]]`` about ``center``.

    ``center`` defaults to :func:`centroid`. Units: (cells / R)**2.
    """
    A = np.asarray(A, dtype=float)
    if center is None:
        center = centroid(A)
    total = A.sum()
    if not total > 0:
        raise ValueError("second moment of an empty state is undefined")
    dy, dx = offsets(A.shape, center)
    iyy = np.sum(A * dy * dy) / total
    ixx = np.sum(A * dx * dx) / total
    ixy = np.sum(A * dx * dy) / total
    return np.array([[iyy, ixy], [ixy, ixx]]) / R**2


def gyradius(A: np.ndarray, center: Sequence[float] | None = None, R: float = 1.0) -> float:
    """Radius of gyration ``sqrt(trace(second_moment))``, in units of R."""
    return float(math.sqrt(np.trace(second_moment(A, center, R))))


def anisotropy(A: np.ndarray, center: Sequence[float] | None = None) -> tuple[float, float]:
    """Elongation of the mass distribution from its second moment.

    Returns ``(e, angle)``. ``e = 1 - lambda_min / lambda_max`` is 0 for an
    isotropic body and approaches 1 for a line. ``angle`` is the major axis
    direction in degrees in ``[0, 180)``, measured from +x toward +y like the
    heading in :func:`velocity`.
    """
    M = second_moment(A, center)
    # eigh on [[xx, xy], [xy, yy]] so the eigenvector is (x, y).
    w, v = np.linalg.eigh(np.array([[M[1, 1], M[0, 1]], [M[0, 1], M[0, 0]]]))
    lo, hi = w
    e = 0.0 if hi <= 0 else 1.0 - lo / hi
    major = v[:, 1]
    angle = math.degrees(math.atan2(major[1], major[0])) % 180.0
    return float(e), float(angle)


def rotational_harmonics(
    A: np.ndarray, center: Sequence[float] | None = None, kmax: int = 8
) -> np.ndarray:
    """Radius-weighted angular Fourier amplitudes of the mass distribution about ``center``.

    ``a[k] = |sum(A r exp(i k theta))| / sum(A r)`` for ``k = 0..kmax``, where
    ``r, theta`` are each cell's polar coordinates about the centroid. ``a[0]``
    is 1, and ``a[1]`` is 0 about the centroid by construction. Small ``a[k]``
    for every ``k >= 2`` means near rotational symmetry. A body with exact
    k-fold symmetry has ``a[j] = 0`` for every j that is not a multiple of k.
    The values are orientation-free, so they do not track heading.

    The ``r`` weight suppresses the coarse angular sampling of the few cells
    nearest the centre. Without it, a sampled isotropic Gaussian picks up
    lattice harmonics of up to 0.02-0.08 (Lane 7 HR-003). With it, an
    isotropic Gaussian of sd >= 3 cells stays below 0.03, and a hard-edged disk
    of radius 8 stays below 0.04. See :data:`SYMMETRY_FLOOR`.
    """
    A = np.asarray(A, dtype=float)
    if center is None:
        center = centroid(A)
    if not A.sum() > 0:
        raise ValueError("harmonics of an empty state are undefined")
    dy, dx = offsets(A.shape, center)
    w = A * np.hypot(dx, dy)
    theta = np.arctan2(dy, dx)
    ks = np.arange(kmax + 1)
    if not w.sum() > 0:   # all mass on the centroid cell: no angular structure
        return np.eye(1, kmax + 1).ravel()
    z = np.exp(1j * ks[:, None] * theta.ravel()[None, :]) @ w.ravel()
    return np.abs(z) / w.sum()


# Largest radius-weighted harmonic (k = 2..8) seen on lattice-sampled
# rotationally symmetric controls at random sub-pixel centres: Gaussians with
# sd 3-8 cells (< 0.03) and hard disks of radius 8 (< 0.04). A harmonic below
# this floor is not evidence of angular structure.
SYMMETRY_FLOOR = 0.05


def symmetry_order(harmonics: np.ndarray, kmin: int = 2, floor: float = SYMMETRY_FLOOR) -> int:
    """The ``k >= kmin`` with the largest rotational harmonic, which is the dominant angular mode.

    Returns 0 ("no detectable angular structure") when no harmonic reaches
    ``floor``. Without the floor, the lattice's own 4- and 8-fold harmonics
    would be reported for an isotropic body.
    """
    h = np.asarray(harmonics)[kmin:]
    if not h.size or h.max() < floor:
        return 0
    return int(kmin + np.argmax(h))


def wrap_extent(A: np.ndarray, center: Sequence[float] | None = None, threshold: float = 1e-3) -> float:
    """Largest minimum-image distance (cells) of any cell above ``threshold`` from the centroid,
    as a fraction of half the smaller grid side.

    Values near or above 1 mean the body (or debris) reaches the far side of the
    torus, so centroid-based features are no longer trustworthy.
    """
    A = np.asarray(A, dtype=float)
    if center is None:
        center = centroid(A)
    dy, dx = offsets(A.shape, center)
    mask = A > threshold
    if not mask.any():
        return 0.0
    return float(max(np.abs(dy[mask]).max(), np.abs(dx[mask]).max()) / (min(A.shape) / 2))


# --- time series ------------------------------------------------------------


def dominant_period(series: Sequence[float], every: float = 1.0) -> float:
    """Period of the strongest non-DC peak in the power spectrum of ``series``.

    The series is mean-removed and Hann-windowed; the peak bin is refined by
    parabolic interpolation on log power, so the result is sub-bin accurate for
    a clean oscillation. ``every`` is the sampling interval, and the period is
    returned in the same unit (steps by default). Returns ``nan`` for a
    constant or too-short series.

    Note: for a gliding organism a mass period may be a lattice artifact, not an
    intrinsic oscillation (S001 dossier, lattice-heading observation).
    """
    x = np.asarray(series, dtype=float)
    n = len(x)
    if n < 4:
        return float("nan")
    x = x - x.mean()
    if not np.any(x):
        return float("nan")
    p = np.abs(np.fft.rfft(x * np.hanning(n))) ** 2
    p[0] = 0.0
    k = int(np.argmax(p))
    if k == 0:
        return float("nan")
    shift = 0.0
    if 0 < k < len(p) - 1 and p[k - 1] > 0 and p[k + 1] > 0:
        a, b, c = np.log(p[k - 1]), np.log(p[k]), np.log(p[k + 1])
        denom = a - 2 * b + c
        if denom != 0:
            shift = 0.5 * (a - c) / denom
    return float(n * every / (k + shift))


def recovery_time(
    series: Sequence[float],
    reference: float,
    tolerance: float,
    start: int = 0,
    hold: int = 1,
    every: float = 1.0,
) -> float:
    """Time from sample ``start`` until ``series`` re-enters and stays in the band.

    The band is ``|series - reference| <= tolerance``. Recovery is the first
    sample index ``i >= start`` after which the band holds for at least ``hold``
    consecutive samples **and** for every remaining sample. Returns
    ``(i - start) * every`` (0 if it never left), or ``inf`` if the series has not
    recovered by its end (including when fewer than ``hold`` in-band samples
    remain).

    ``reference`` and ``tolerance`` must be fixed before looking at the
    perturbed run (e.g. the unperturbed mean and a multiple of its sd), so the
    threshold is not chosen after seeing the answer.
    """
    x = np.asarray(series, dtype=float)[start:]
    ok = np.abs(x - reference) <= tolerance
    if not ok.size:
        return float("inf")
    bad = np.flatnonzero(~ok)
    i = 0 if bad.size == 0 else int(bad[-1]) + 1
    if ok.size - i < max(hold, 1):
        return float("inf")
    return float(i * every)


# --- convenience ------------------------------------------------------------


def snapshot(A: np.ndarray, R: float = 1.0, threshold: float = 0.1, kmax: int = 6) -> dict:
    """All single-state features in one dict, for trace rows.

    Keys: ``mass``, ``cy``, ``cx`` (cells), ``gyradius`` (R), ``anisotropy``,
    ``major_axis_deg``, ``area`` (R**2), ``symmetry_order``, ``harmonic_k`` for
    k = 2..kmax, and ``wrap_extent``. An empty state returns mass 0 and NaN for
    the rest.
    """
    A = np.asarray(A, dtype=float)
    out = {"mass": mass(A, R), "area": occupied_area(A, threshold, R)}
    if not A.sum() > 0:
        nan = float("nan")
        out.update(cy=nan, cx=nan, gyradius=nan, anisotropy=nan, major_axis_deg=nan,
                   symmetry_order=nan, wrap_extent=nan)
        out.update({f"harmonic_{k}": nan for k in range(2, kmax + 1)})
        return out
    c = centroid(A)
    e, ang = anisotropy(A, c)
    h = rotational_harmonics(A, c, kmax)
    out.update(
        cy=c[0],
        cx=c[1],
        gyradius=gyradius(A, c, R),
        anisotropy=e,
        major_axis_deg=ang,
        symmetry_order=symmetry_order(h),
        wrap_extent=wrap_extent(A, c),
    )
    out.update({f"harmonic_{k}": float(h[k]) for k in range(2, kmax + 1)})
    return out


def snapshots(states: Iterable[np.ndarray], **kw) -> list[dict]:
    """:func:`snapshot` over an iterable of states."""
    return [snapshot(A, **kw) for A in states]
