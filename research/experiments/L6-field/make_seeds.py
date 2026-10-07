"""Rebuild the Lane 6 candidate seeds from their recipes (deterministic).

    python research/experiments/L6-field/make_seeds.py

Each seed is the settled state of a recorded run, recentred on its periodic
centroid, cropped to the cells above 1e-6 and quantised to levels 0..255 (the
same convention as S001's initial-cells-u8.csv). Recipes:

  gyrator  S001 cells, mu 0.155, sigma 0.022, 20000 steps (T 10, R 13, 128^2)
  pair     two S001 copies on 192^2 (second shifted -1 R in x, +1 R in y, same
           orientation; sweep_seeds.py pairs world phi=0 dx=-1 dy=1),
           S001 rule, 5000 steps
  static   gyrator seed at mu 0.155, sigma 0.020 for 3002 steps, then Lane 4
           I004 port injury s = 0.15, then 5000 steps
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from disturb_helpers import i004  # noqa: E402
from field import Batch, centroids  # noqa: E402

from alm import specimens  # noqa: E402


def crop_u8(F):
    cx, cy = centroids(F[None])
    n = F.shape[0]
    F = np.roll(F, (n // 2 - int(cy[0]), n // 2 - int(cx[0])), (0, 1))
    ys, xs = np.nonzero(F > 1e-6)
    return np.round(F[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1] * 255).astype(int)


def put(A, p, cy, cx):
    h, w = p.shape
    ys = (np.arange(h) + int(round(cy)) - h // 2) % A.shape[0]
    xs = (np.arange(w) + int(round(cx)) - w // 2) % A.shape[1]
    A[np.ix_(ys, xs)] += p


def run(A, mu, sg, steps):
    return Batch(13, 10, [mu], [sg]).run(A[None], steps, snap_every=10**9)


def save(name, lev):
    np.savetxt(HERE / f"{name}-seed-u8.csv", lev, fmt="%d", delimiter=",")
    print(name, lev.shape, int(lev.sum()))


if __name__ == "__main__":
    S = specimens.load("S001")
    cells = S.cells / 255.0
    g = crop_u8(run(S.place(128), 0.155, 0.022, 20000)["final"][0])
    save("gyrator", g)

    A = np.zeros((192, 192))
    put(A, cells, 96, 96)
    put(A, cells, 96 + 13, 96 - 13)
    save("pair", crop_u8(run(np.clip(A, 0, 1), 0.15, 0.015, 5000)["final"][0]))

    A = np.zeros((128, 128))
    h, w = g.shape
    A[(128 - h) // 2 : (128 - h) // 2 + h, (128 - w) // 2 : (128 - w) // 2 + w] = g / 255.0
    r = Batch(13, 10, [0.155], [0.020]).run(A[None], 3002, snap_every=10**9)
    B = r["final"][0]
    v = r["pos"][3002, 0] - r["pos"][2992, 0]
    cx, cy = centroids(B[None])
    B = i004(B, 0.15, (cx[0], cy[0]), v / np.hypot(*v))
    save("static", crop_u8(run(B, 0.155, 0.020, 5000)["final"][0]))
