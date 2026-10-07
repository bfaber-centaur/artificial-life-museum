"""L6-006: do the candidates persist, with the same phenotype, at a second T and R?

    python research/experiments/L6-field/persistence.py --T 10 --R 13 [--time 500]

Candidates (seed -> rule): orbium, pair, O4i (catalog Synorbium ignis cells)
under the S001 rule (mu 0.15, sigma 0.015); orbium, gyrator, static under the
coexistence rule (mu 0.155, sigma 0.020). Seeds are resized by R/13 (bilinear)
at R != 13. Writes persist-T<T>-R<R>.csv and .npz (final states).
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from field import Batch, summarize  # noqa: E402
from tables import phenotype  # noqa: E402

from alm import rle, specimens  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--T", type=float, default=10)
ap.add_argument("--R", type=int, default=13)
ap.add_argument("--time", type=float, default=500)
args = ap.parse_args()
R, T = args.R, args.T
N = int(round(128 * R / 13 / 2)) * 2

cat = {e.get("code"): e for e in json.loads(specimens.ANIMALS_JSON.read_bytes())}
seed = {
    "orbium": specimens.load("S001").cells / 255.0,
    "pair": np.loadtxt(HERE / "pair-seed-u8.csv", delimiter=",") / 255.0,
    "gyrator": np.loadtxt(HERE / "gyrator-seed-u8.csv", delimiter=",") / 255.0,
    "static": np.loadtxt(HERE / "static-seed-u8.csv", delimiter=",") / 255.0,
    "O4i": rle.decode(cat["O4i"]["cells"]) / 255.0,
}
S001, COEX = (0.15, 0.015), (0.155, 0.020)
jobs = [("orbium", S001), ("pair", S001), ("O4i", S001), ("orbium", COEX), ("gyrator", COEX), ("static", COEX)]


def place(p):
    if R != 13:
        p = np.clip(ndimage.zoom(p, R / 13, order=1), 0, 1)
    A = np.zeros((N, N))
    h, w = p.shape
    A[(N - h) // 2 : (N - h) // 2 + h, (N - w) // 2 : (N - w) // 2 + w] = p
    return A


steps = int(round(args.time * T))
window = int(round(100 * T))
t0 = time.time()
b = Batch(R=R, T=T, mu=[j[1][0] for j in jobs], sigma=[j[1][1] for j in jobs])
res = b.run(np.array([place(seed[j[0]]) for j in jobs]), steps, snap_every=max(1, int(T * 5)),
            snap_from=steps - window)
rows = []
for (s, (mu, sg)), d in zip(jobs, summarize(res, R, T, window)):
    ph = d["fate"].upper() if d["fate"] != "localized" else phenotype({k: str(v) for k, v in d.items()})
    rows.append({"seed": s, "mu": mu, "sigma": sg, "T": T, "R": R, "phenotype": ph, **d})
    print(s, mu, sg, ph, round(d["mass_mean"], 4), round(d["gyr"], 4), round(d["speed"], 4),
          round(d["path_speed"], 4), round(d["turn_rate"], 2), flush=True)
tag = f"T{T:g}-R{R}"
with open(HERE / f"persist-{tag}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
np.savez_compressed(HERE / f"persist-{tag}.npz", final=res["final"].astype(np.float32))
print("wrote", tag, f"{time.time() - t0:.0f}s")
