"""Periodic measurements (feature functions) for traces.

A feature function takes ``(A, sim)`` and returns a dict of named floats. The
runner calls every selected feature at each sampling step and writes one CSV
column per key. Lane 5 adds morphometrics with ``@register("name")``.

Units: mass and growth are normalised by R^2 (upstream ``m``/``g``); lengths
are in kernel radii R unless the column name ends in ``_cells``.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

FeatureFn = Callable[[np.ndarray, object], dict]
REGISTRY: dict[str, FeatureFn] = {}
DEFAULT = ("basic",)

ALIVE_MASS = 1e-10  # upstream survival floor on raw mass


def register(name: str):
    def deco(fn: FeatureFn) -> FeatureFn:
        if name in REGISTRY and REGISTRY[name] is not fn:
            raise ValueError(f"feature {name!r} already registered")
        REGISTRY[name] = fn
        return fn

    return deco


def periodic_centroid(A: np.ndarray) -> tuple[float, float]:
    """Centroid on the torus via the circular mean of each axis, in cells.

    Returns (cx, cy) in [0, N). NaN when the state is empty."""
    ny, nx = A.shape
    total = A.sum()
    if total <= 0:
        return float("nan"), float("nan")
    phx = np.exp(2j * np.pi * np.arange(nx) / nx)
    phy = np.exp(2j * np.pi * np.arange(ny) / ny)
    cx = (np.angle(A.sum(0) @ phx) % (2 * np.pi)) * nx / (2 * np.pi)
    cy = (np.angle(A.sum(1) @ phy) % (2 * np.pi)) * ny / (2 * np.pi)
    return float(cx), float(cy)


def wrap(d: np.ndarray | float, n: int):
    """Minimal-image displacement on a ring of length n."""
    return (np.asarray(d) + n / 2) % n - n / 2


@register("basic")
def basic(A: np.ndarray, sim) -> dict:
    R = sim.rule.R
    ny, nx = A.shape
    raw = float(A.sum())
    cx, cy = periodic_centroid(A)
    if raw > ALIVE_MASS:
        dx = wrap(np.arange(nx) - cx, nx)
        dy = wrap(np.arange(ny) - cy, ny)
        r2 = (A.sum(0) @ dx**2 + A.sum(1) @ dy**2) / raw
        gyr = float(np.sqrt(r2)) / R
    else:
        gyr = 0.0
    return {
        "mass": raw / R**2,
        "peak": float(A.max()),
        "area": float((A > 0.1).sum()) / R**2,
        "gyradius": gyr,
        "cx_cells": cx,
        "cy_cells": cy,
        "alive": int(raw > ALIVE_MASS),
    }


def compute(names, A, sim) -> dict:
    out = {}
    for n in names:
        try:
            fn = REGISTRY[n]
        except KeyError:
            raise KeyError(f"unknown feature set {n!r}; known: {sorted(REGISTRY)}") from None
        out.update(fn(A, sim))
    return out
