"""L6-004: do glider (Orbium) and rotator (gyrator) coexist under one rule?

    python research/experiments/L6-field/bistability.py [--T 10] [--R 13]

Three seeds, each run under every rule on a mu x sigma grid near the Orbium /
Gyrorbium boundary (128^2 torus at R=13; size scales with R):
  orbium   S001 catalog cells (O2u);
  gyrator  gyrator-seed-u8.csv: S001 cells run 20000 steps at mu=0.155,
           sigma=0.022, T=10, R=13, then cropped (made by this lane, see README);
  OG2g     upstream catalog Gyrorbium gyrans cells.
At R != 13 seeds are resized with scipy.ndimage.zoom(order=1).
Writes bistab-T<T>-R<R>.csv and .npz.
"""
import argparse
import csv
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from field import Batch, summarize  # noqa: E402

from alm import rle, specimens  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--T", type=float, default=10)
ap.add_argument("--R", type=int, default=13)
ap.add_argument("--time", type=float, default=1000)
ap.add_argument("--mus", default="0.15,0.155,0.16")
ap.add_argument("--sigmas", default="0.018:0.0255:0.0005")
ap.add_argument("--chunk", type=int, default=48)
args = ap.parse_args()
R, T = args.R, args.T
N = int(round(128 * R / 13 / 2)) * 2

og2g = [e for e in json.loads(specimens.ANIMALS_JSON.read_bytes()) if e.get("code") == "OG2g"][0]
seeds = {
    "orbium": specimens.load("S001").cells / 255.0,
    "gyrator": np.loadtxt(HERE / "gyrator-seed-u8.csv", delimiter=",") / 255.0,
    "OG2g": rle.decode(og2g["cells"]) / 255.0,
}
mus = [float(x) for x in args.mus.split(",")]
a, b_, c = (float(x) for x in args.sigmas.split(":"))
sigmas = list(np.round(np.arange(a, b_ + 1e-9, c), 5))
jobs = list(itertools.product(seeds, mus, sigmas))


def place(p):
    if R != 13:
        p = np.clip(ndimage.zoom(p, R / 13, order=1), 0, 1)
    A = np.zeros((N, N))
    h, w = p.shape
    A[(N - h) // 2 : (N - h) // 2 + h, (N - w) // 2 : (N - w) // 2 + w] = p
    return A


steps = int(round(args.time * T))
window = int(round(200 * T))
rows, finals = [], []
t0 = time.time()
for k in range(0, len(jobs), args.chunk):
    js = jobs[k : k + args.chunk]
    b = Batch(R=R, T=T, mu=[j[1] for j in js], sigma=[j[2] for j in js])
    res = b.run(np.array([place(seeds[j[0]]) for j in js]), steps, snap_every=max(1, int(T * 5)),
                snap_from=steps - window)
    for j, d in zip(js, summarize(res, R, T, window)):
        rows.append({"seed": j[0], "mu": j[1], "sigma": j[2], "T": T, "R": R, **d})
    finals.append(res["final"].astype(np.float32))
    print(f"{k + len(js)}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
tag = f"T{T:g}-R{R}"
with open(HERE / f"bistab-{tag}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
np.savez_compressed(HERE / f"bistab-{tag}.npz", final=np.concatenate(finals))
print("wrote", tag)
