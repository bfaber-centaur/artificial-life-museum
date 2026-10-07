"""L6-003: structured initial conditions around Orbium under one fixed rule.

    python research/experiments/L6-field/sweep_seeds.py zoom   [--mu 0.15 --sigma 0.015]
    python research/experiments/L6-field/sweep_seeds.py pairs  [--mu 0.15 --sigma 0.015]

zoom:  S001 cells resized by factor z (bilinear, scipy.ndimage.zoom order=1) and
       scaled in amplitude by a, clipped to [0, 1]; z in 0.6..2.0, a in 0.6..1.4.
pairs: two S001 copies on a 192^2 torus; the second is rotated by phi (multiples
       of 45 deg so no interpolation: np.rot90 / transpose-free 90s, and 45 via
       ndimage.rotate order=1) and offset by (dx, dy) in R from the first.
Writes seeds-<mode>-<tag>.csv and .npz (initial + final states).
"""
import argparse
import csv
import itertools
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from field import Batch, summarize  # noqa: E402

from alm import specimens  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["zoom", "pairs"])
ap.add_argument("--mu", type=float, default=0.15)
ap.add_argument("--sigma", type=float, default=0.015)
ap.add_argument("--T", type=float, default=10)
ap.add_argument("--time", type=float, default=500)
ap.add_argument("--chunk", type=int, default=32)
args = ap.parse_args()
R, T = 13, args.T
cells = specimens.load("S001").cells / 255.0


def put(A, patch, cy, cx):
    """Add patch centred at (cy, cx) on torus A."""
    h, w = patch.shape
    ys = (np.arange(h) + int(round(cy)) - h // 2) % A.shape[0]
    xs = (np.arange(w) + int(round(cx)) - w // 2) % A.shape[1]
    A[np.ix_(ys, xs)] += patch


seeds, meta = [], []
if args.mode == "zoom":
    N = 128
    for z, a in itertools.product(np.round(np.arange(0.6, 2.01, 0.1), 2), np.round(np.arange(0.6, 1.41, 0.1), 2)):
        p = np.clip(ndimage.zoom(cells, z, order=1) * a, 0, 1)
        A = np.zeros((N, N))
        put(A, p, N / 2, N / 2)
        seeds.append(A)
        meta.append({"zoom": z, "amp": a})
else:
    N = 192
    rots = {0: lambda c: c, 90: lambda c: np.rot90(c, 1), 180: lambda c: np.rot90(c, 2),
            270: lambda c: np.rot90(c, 3), 45: lambda c: np.clip(ndimage.rotate(c, 45, order=1), 0, 1)}
    for phi, dx, dy in itertools.product([0, 45, 90, 180, 270], [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
                                         [0.75, 1.0, 1.25, 1.5, 2.0]):
        A = np.zeros((N, N))
        put(A, cells, N / 2, N / 2)
        put(A, rots[phi](cells), N / 2 + dy * R, N / 2 + dx * R)
        seeds.append(np.clip(A, 0, 1))
        meta.append({"phi": phi, "dx_R": dx, "dy_R": dy})
seeds = np.array(seeds)
steps = int(round(args.time * T))
window = int(round(100 * T))
rows, finals = [], []
t0 = time.time()
for k in range(0, len(seeds), args.chunk):
    sl = slice(k, min(k + args.chunk, len(seeds)))
    W = sl.stop - sl.start
    b = Batch(R=R, T=T, mu=[args.mu] * W, sigma=[args.sigma] * W)
    res = b.run(seeds[sl], steps, snap_every=int(T * 5), snap_from=steps - window)
    for j, d in enumerate(summarize(res, R, T, window)):
        i = sl.start + j
        rows.append({"world": i, **meta[i], "mu": args.mu, "sigma": args.sigma, "T": T, "R": R,
                     "init_mass": float(seeds[i].sum()) / R**2, **d})
    finals.append(res["final"].astype(np.float32))
    print(f"{sl.stop}/{len(seeds)} {time.time() - t0:.0f}s", flush=True)
tag = f"mu{args.mu:g}-s{args.sigma:g}-T{T:g}"
with open(HERE / f"seeds-{args.mode}-{tag}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
np.savez_compressed(HERE / f"seeds-{args.mode}-{tag}.npz", initial=seeds.astype(np.float32),
                    final=np.concatenate(finals))
print("wrote", args.mode, tag)
