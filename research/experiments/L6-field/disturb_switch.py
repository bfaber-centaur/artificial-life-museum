"""L6-005: can a disturbance switch phenotype (glider <-> rotator) under one rule?

    python research/experiments/L6-field/disturb_switch.py [--T 10] [--R 13]

The four Lane 4 disturbances (L4-001 protocol, branch
claude/night0-disturbance-np4adr @ 7bd1a42, src/alm/disturb.py) are
re-implemented here verbatim in a few lines so this script does not depend on
an unmerged branch. Each is applied to a settled creature at two phase
replicates (t0, t0+2) after a 300 time-unit warm-up, then the world runs
500 time units more. Cases:

  control   Orbium seed, S001 rule (mu 0.15, sigma 0.015) - only gliders known here
  orb@coex  Orbium seed, coexistence rule (mu 0.155, sigma 0.020)
  gyr@coex  gyrator seed, coexistence rule
  pair@S001 bound Orbium pair seed (make_seeds.py), S001 rule

Outcome over the last 100 time units: GLIDER (net speed > 0.2 R/tu),
CIRCLER (net speed < 0.1 and path speed > 0.2), STATIC (path speed < 0.02),
DIED (mass < 0.01), FILLED (area > 25 %), else OTHER. The first T=10 run used a
ROTATOR rule on the principal-axis rate instead; that rate aliases (see README),
so the recorded "outcome" column is recomputed by tables.py from net/path speed.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from disturb_helpers import disturb  # noqa: E402
from field import Batch, centroids, summarize  # noqa: E402

from alm import specimens  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--T", type=float, default=10)
ap.add_argument("--R", type=int, default=13)
ap.add_argument("--cases", default="control,orb@coex,gyr@coex")
ap.add_argument("--chunk", type=int, default=48)
ap.add_argument("--coex", default="0.155,0.020")
args = ap.parse_args()
R, T = args.R, args.T
N = int(round(128 * R / 13 / 2)) * 2
cm, cs = (float(x) for x in args.coex.split(","))


GRIDS = {"I001": np.round(np.arange(0.05, 0.951, 0.05), 3), "I002": np.round(np.arange(0.05, 1.001, 0.05), 3),
         "I003": np.round(np.arange(0.05, 1.001, 0.05), 3), "I004": np.round(np.arange(0.05, 0.951, 0.05), 3)}
seeds = {"orbium": specimens.load("S001").cells / 255.0,
         "gyrator": np.loadtxt(HERE / "gyrator-seed-u8.csv", delimiter=",") / 255.0,
         "pair": np.loadtxt(HERE / "pair-seed-u8.csv", delimiter=",") / 255.0}
CASES = {"control": ("orbium", 0.15, 0.015), "orb@coex": ("orbium", cm, cs), "gyr@coex": ("gyrator", cm, cs),
         "pair@S001": ("pair", 0.15, 0.015)}


def place(p):
    if R != 13:
        p = np.clip(ndimage.zoom(p, R / 13, order=1), 0, 1)
    A = np.zeros((N, N))
    h, w = p.shape
    A[(N - h) // 2 : (N - h) // 2 + h, (N - w) // 2 : (N - w) // 2 + w] = p
    return A


def classify(d):
    if d["fate"] != "localized":
        return d["fate"].upper()
    if d["speed"] > 0.2:
        return "GLIDER"
    if d["speed"] < 0.1 and d["path_speed"] > 0.2:
        return "CIRCLER"
    if d["path_speed"] < 0.02:
        return "STATIC"
    return "OTHER"


t0 = int(round(300 * T))
after = int(round(500 * T))
window = int(round(100 * T))
rows = []
started = time.time()
for case in args.cases.split(","):
    seed, mu, sg = CASES[case]
    warm = Batch(R=R, T=T, mu=[mu], sigma=[sg])
    w = warm.run(place(seeds[seed])[None], t0 + 2, snap_every=10**9, keep=(t0, t0 + 2))
    jobs = [(None, 0.0, ph) for ph in (0, 2)]  # undisturbed controls
    jobs += [(k, s, ph) for k, g in GRIDS.items() for s in g for ph in (0, 2)]
    for i in range(0, len(jobs), args.chunk):
        js = jobs[i : i + args.chunk]
        stack = []
        for kind, s, ph in js:
            t = t0 + ph
            A = w["states"][t][0]
            c = w["pos"][t, 0]
            v = w["pos"][t, 0] - w["pos"][t - 10, 0]
            h = v / np.hypot(*v) if np.hypot(*v) > 1e-9 else np.array([1.0, 0.0])
            cc = centroids(A[None])
            stack.append(A.copy() if kind is None else disturb(kind, A, s, (cc[0][0], cc[1][0]), h, R))
        stack = np.array(stack)
        b = Batch(R=R, T=T, mu=[mu] * len(js), sigma=[sg] * len(js))
        res = b.run(stack, after, snap_every=max(1, int(T * 5)), snap_from=after - window)
        for (kind, s, ph), A, d in zip(js, stack, summarize(res, R, T, window)):
            t = t0 + ph
            m0 = w["states"][t][0].sum() / R**2
            rows.append({"case": case, "seed": seed, "mu": mu, "sigma": sg, "T": T, "R": R,
                         "intervention": kind or "none", "s": s, "t0": t, "mass_before": m0,
                         "dmass_frac": (A.sum() / R**2 - m0) / m0, "outcome": classify(d), **d})
        print(f"{case} {i + len(js)}/{len(jobs)} {time.time() - started:.0f}s", flush=True)
tag = f"T{T:g}-R{R}"
if args.cases != "control,orb@coex,gyr@coex":
    tag += "-" + args.cases.replace(",", "+").replace("@", "-")
with open(HERE / f"switch-{tag}.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0]))
    wr.writeheader()
    for r in rows:
        wr.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
print("wrote", tag)
