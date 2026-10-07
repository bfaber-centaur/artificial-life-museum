"""L6-002: random-soup initial conditions under a fixed rule.

    python research/experiments/L6-field/sweep_soup.py --mu 0.15 --sigma 0.015 [--n 96]

Each world starts from one square patch of i.i.d. uniform cells on an empty
128^2 torus; patch side L (in R) and peak level are drawn per world from a
seeded generator. Writes soup-<tag>.csv and soup-<tag>.npz (initial + final).
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

ap = argparse.ArgumentParser()
ap.add_argument("--mu", type=float, default=0.15)
ap.add_argument("--sigma", type=float, default=0.015)
ap.add_argument("--T", type=float, default=10)
ap.add_argument("--R", type=int, default=13)
ap.add_argument("--n", type=int, default=96)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--time", type=float, default=500)
ap.add_argument("--chunk", type=int, default=48)
args = ap.parse_args()

R, T, N = args.R, args.T, 128
rng = np.random.default_rng(args.seed)
L = rng.uniform(1.0, 3.0, args.n)  # patch side in R
peak = rng.uniform(0.5, 1.0, args.n)
A0 = np.zeros((args.n, N, N))
for i in range(args.n):
    s = int(round(L[i] * R))
    y0 = (N - s) // 2
    A0[i, y0 : y0 + s, y0 : y0 + s] = rng.uniform(0, peak[i], (s, s))
steps = int(round(args.time * T))
window = int(round(100 * T))
rows, finals = [], []
t0 = time.time()
for k in range(0, args.n, args.chunk):
    sl = slice(k, min(k + args.chunk, args.n))
    W = sl.stop - sl.start
    b = Batch(R=R, T=T, mu=[args.mu] * W, sigma=[args.sigma] * W)
    res = b.run(A0[sl], steps, snap_every=int(T * 5), snap_from=steps - window)
    for j, d in enumerate(summarize(res, R, T, window)):
        i = sl.start + j
        rows.append({"world": i, "seed": args.seed, "L_R": round(L[i], 4), "peak": round(peak[i], 4),
                     "mu": args.mu, "sigma": args.sigma, "T": T, "R": R, **d})
    finals.append(res["final"].astype(np.float32))
    print(f"{sl.stop}/{args.n} {time.time() - t0:.0f}s", flush=True)
tag = f"mu{args.mu:g}-s{args.sigma:g}-T{T:g}-R{R}-seed{args.seed}"
with open(HERE / f"soup-{tag}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
np.savez_compressed(HERE / f"soup-{tag}.npz", initial=A0.astype(np.float32), final=np.concatenate(finals))
print("wrote", tag)
