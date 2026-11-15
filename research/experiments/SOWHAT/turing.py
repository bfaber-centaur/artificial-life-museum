"""One chemistry, many patterns: a Gray-Scott feed/kill atlas.

Same equations and diffusion constants as WINGS's GrayScott (Pearson 1993, Du 0.2, Dv 0.1,
dt 1, 5-point Laplacian, torus), run as a batch: every world gets its own feed rate F and kill
rate k and nothing else differs. Each world starts at u 1, v 0 with the same eight seeded
squares (u 0.5, v 0.25, plus 1% noise), as in Pearson's single central square but scattered so
the pattern fills the world sooner.

  python turing.py atlas OUT.npz OUT.jsonl     10 x 10 grid, F 0.010-0.070, k 0.045-0.069
  python turing.py label OUT.npz OUT.jsonl     recompute the labels from a saved atlas
"""
import json
import sys

import numpy as np
from scipy import ndimage

F_GRID = np.round(np.linspace(0.010, 0.070, 10), 4)
K_GRID = np.round(np.linspace(0.045, 0.069, 10), 4)
SIZE, STEPS, CHECK = 128, 10000, 9000


def lap(a):
    return (np.roll(a, 1, -1) + np.roll(a, -1, -1) + np.roll(a, 1, -2) + np.roll(a, -1, -2)
            - 4 * a)


def initial(n, rng, squares=8, half=6):
    u = np.ones((n, n))
    v = np.zeros((n, n))
    for _ in range(squares):
        y, x = rng.integers(0, n, 2)
        ys, xs = np.arange(y - half, y + half) % n, np.arange(x - half, x + half) % n
        u[np.ix_(ys, xs)] = 0.5
        v[np.ix_(ys, xs)] = 0.25
    u += 0.01 * rng.standard_normal((n, n))
    v += 0.01 * rng.standard_normal((n, n))
    return u, v


def run(F, k, u0, v0, steps, check, Du=0.2, Dv=0.1, dt=1.0):
    """F, k broadcast against the batch axis. Returns v at `check` and at the end."""
    u = np.broadcast_to(u0, F.shape[:1] + u0.shape).copy()
    v = np.broadcast_to(v0, F.shape[:1] + v0.shape).copy()
    F = F[:, None, None]
    k = k[:, None, None]
    snap = None
    for t in range(1, steps + 1):
        uvv = u * v * v
        u, v = (u + dt * (Du * lap(u) - uvv + F * (1 - u)),
                v + dt * (Dv * lap(v) + uvv - (F + k) * v))
        if t == check:
            snap = v.copy()
    return snap, v


def describe(v_end, v_check, thr=0.2):
    """Simple shape numbers for one world's final v field (periodic labelling not needed for
    the classes we report; a body cut by the seam just counts twice)."""
    mask = v_end > thr
    lab, n = ndimage.label(mask)
    sizes = np.bincount(lab.ravel())[1:] if n else np.array([0])
    cover = float(mask.mean())
    change = float(np.mean(np.abs(v_end - v_check) > 0.05))
    if cover == 0:
        kind = "empty"
    elif change > 0.05:
        kind = "moving"
    elif n >= 8 and sizes.max() < 0.02 * mask.size:
        kind = "spots"
    elif sizes.max() >= 0.2 * mask.size and cover < 0.85:
        kind = "connected"
    elif cover >= 0.85 and float(v_end.std()) < 0.01:
        kind = "uniform"
    elif cover >= 0.85:
        kind = "holes"
    else:
        kind = "other"
    return dict(cover=cover, parts=int(n), largest=float(sizes.max() / mask.size),
                change=change, std=float(v_end.std()), kind=kind)


def label(npz_path, jsonl_path):
    """Rewrite atlas.jsonl from a saved atlas.npz (no re-simulation)."""
    z = np.load(npz_path)
    with open(jsonl_path, "w") as f:
        for i in range(z["v"].shape[0]):
            row = dict(F=float(z["F"][i]), k=float(z["k"][i]), size=SIZE, steps=STEPS,
                       check=CHECK, seed=[2026, 11, 15, 2],
                       **describe(z["v"][i].astype(np.float64), z["v_check"][i].astype(np.float64)))
            f.write(json.dumps(row) + "\n")


def atlas(npz_path, jsonl_path):
    rng = np.random.default_rng([2026, 11, 15, 2])
    u0, v0 = initial(SIZE, rng)
    FF, KK = np.meshgrid(F_GRID, K_GRID, indexing="ij")
    snap, v = run(FF.ravel(), KK.ravel(), u0, v0, STEPS, CHECK)
    np.savez_compressed(npz_path, v=v.astype(np.float32), v_check=snap.astype(np.float32),
                        F=FF.ravel(), k=KK.ravel())
    with open(jsonl_path, "w") as f:
        for i in range(v.shape[0]):
            row = dict(F=float(FF.ravel()[i]), k=float(KK.ravel()[i]), size=SIZE, steps=STEPS,
                       check=CHECK, seed=[2026, 11, 15, 2], **describe(v[i], snap[i]))
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "atlas":
        atlas(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "label":
        label(sys.argv[2], sys.argv[3])
