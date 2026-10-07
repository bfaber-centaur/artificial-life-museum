"""L6-001: mu x sigma sweep around S001 with S001's catalog cells as the seed.

    python research/experiments/L6-field/sweep_musigma.py [--T 10] [--steps 5000]

Writes musigma-T<T>.csv (one row per (mu, sigma)) and musigma-T<T>-final.npz.
Grid fixed before running: mu 0.10..0.20 step 0.005, sigma 0.008..0.028 step 0.001,
R=13, 128^2 torus, poly/poly, horizon 500 time units, summary over the last 100.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from field import Batch, summarize  # noqa: E402

from alm import specimens  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--T", type=float, default=10)
ap.add_argument("--time", type=float, default=500, help="horizon in time units")
ap.add_argument("--chunk", type=int, default=48)
args = ap.parse_args()

mus = np.round(np.arange(0.100, 0.2001, 0.005), 4)
sigmas = np.round(np.arange(0.008, 0.0281, 0.001), 4)
grid = [(m, s) for m in mus for s in sigmas]
spec = specimens.load("S001")
A0 = spec.place(128)
T = args.T
steps = int(round(args.time * T))
window = int(round(100 * T))
rows, finals = [], []
t0 = time.time()
for k in range(0, len(grid), args.chunk):
    g = grid[k : k + args.chunk]
    b = Batch(R=13, T=T, mu=[x[0] for x in g], sigma=[x[1] for x in g])
    res = b.run(np.repeat(A0[None], len(g), 0), steps, snap_every=int(T * 5), snap_from=steps - window)
    for (m, s), d in zip(g, summarize(res, 13, T, window)):
        rows.append({"mu": m, "sigma": s, "T": T, **d})
    finals.append(res["final"].astype(np.float32))
    print(f"{k + len(g)}/{len(grid)} {time.time() - t0:.0f}s", flush=True)
out = HERE / f"musigma-T{T:g}.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
np.savez_compressed(HERE / f"musigma-T{T:g}-final.npz", final=np.concatenate(finals),
                    mu=[x[0] for x in grid], sigma=[x[1] for x in grid])
print("wrote", out)
