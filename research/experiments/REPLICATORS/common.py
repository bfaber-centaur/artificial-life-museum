"""REPLICATORS: shared helpers (blob counting on the torus, loading catalogue replicators)."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "WINGS"))
import nd_lenia as nd  # noqa: E402


def torus_label(mask: np.ndarray):
    """Connected components (full connectivity) on a periodic grid of any dimension."""
    lab, n = ndimage.label(mask, structure=np.ones((3,) * mask.ndim))
    if n == 0:
        return lab, 0
    parent = np.arange(n + 1)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for ax in range(mask.ndim):
        a = np.take(lab, 0, axis=ax)
        b = np.take(lab, -1, axis=ax)
        # neighbours across the seam incl. diagonals along the other axes
        shifts = [0] if a.ndim == 0 else [-1, 0, 1]
        for sh in shifts:
            bb = np.roll(b, sh, axis=0) if a.ndim >= 1 else b
            m = (a > 0) & (bb > 0)
            for x, y in zip(a[m], bb[m]):
                rx, ry = find(x), find(y)
                if rx != ry:
                    parent[max(rx, ry)] = min(rx, ry)
    roots = np.array([find(i) for i in range(n + 1)])
    _, inv = np.unique(roots, return_inverse=True)
    lab = inv[lab]
    return lab, int(inv.max())


def count_bodies(A: np.ndarray, thr: float = 0.1, min_mass: float = 5.0):
    """Number of separate bodies in a (C, *world) state: components of sum_c A > thr with mass >= min_mass."""
    S = A.sum(0) if A.ndim > 2 and A.shape[0] < 8 else A
    lab, n = torus_label(S > thr)
    if n == 0:
        return 0, []
    masses = ndimage.sum(S, lab, index=np.arange(1, n + 1))
    keep = masses >= min_mass
    return int(keep.sum()), sorted(masses[keep].tolist(), reverse=True)


def state_hash(A: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(A, dtype=np.float64).tobytes()).hexdigest()[:16]


def found_entry(stem: str, idx: int):
    return nd.load_found(stem)[idx]
