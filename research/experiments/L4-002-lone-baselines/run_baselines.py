#!/usr/bin/env python3
"""L4-002: lone-S001 baselines matched to L6-008 (see protocol.md next to this file).

    .venv/bin/python research/experiments/L4-002-lone-baselines/run_baselines.py

Writes lone-baselines.csv next to this file. Deterministic; the run ID reproduces a run.
"""
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
L4 = os.path.join(HERE, "..", "L4-001-disturbance-battery")
sys.path.insert(0, L4)
import run  # noqa: E402  (L4-001 runner: engine, warm-up, CSV helpers)
from alm import disturb  # noqa: E402

PHASES = (3000, 3001, 3002, 3003, 3004)
HORIZON = 3000  # 300 tu
WINDOW = 1000  # last 100 tu
GRIDS = {
    "none": [0.0],
    "I001": [round(0.02 * i, 4) for i in range(1, 11)],
    "I004": [round(0.05 * i, 4) for i in range(1, 13)],
    "I003": [round(0.1 * i, 4) for i in range(1, 11)],
}
M1 = 0.4358  # one Orbium, L6-008 units
R, T = run.R, run.T


def run_id(iv, s, t0):
    return f"L4-002-{iv}-s{s:.6f}-t{t0}-N128-ref"


def one(job):
    iv, s, t0 = job
    step = run.engine("ref", 128, R, T)
    A, prev = run.warm("ref", 128, t0)
    frame = disturb.frame_from(A, prev)
    M0 = A.sum()
    if iv != "none":
        A = disturb.INTERVENTIONS[iv](A, frame, s, R)
    M1e = A.sum()
    c = disturb.periodic_centroid(A)
    disp = np.zeros(2)
    win_mass, win_gyr, cum = [], [], {}
    for k in range(1, HORIZON + 1):
        A = step(A)
        cn = disturb.periodic_centroid(A)
        disp += (disturb.wrap(cn[0] - c[0], 128), disturb.wrap(cn[1] - c[1], 128))
        c = cn
        if k % 10 == 0:
            cum[k] = disp.copy()
            if k > HORIZON - WINDOW:
                win_mass.append(A.sum() / R ** 2)
                win_gyr.append(disturb.gyradius(A, *c) / R)
    final_mass = A.sum() / R ** 2
    net = np.hypot(*(cum[HORIZON] - cum[HORIZON - WINDOW])) / R / (WINDOW / T)
    blocks = [np.hypot(*(cum[b + 100] - cum[b])) / R / 10 for b in range(HORIZON - WINDOW, HORIZON, 100)]
    wspeed = float(np.mean(blocks))
    mmean = float(np.mean(win_mass))
    if final_mass < 0.01:
        n = "0"
    elif net > 0.2 and abs(mmean - M1) <= 0.05 * M1:
        n = "1"
    else:
        n = "other"
    cls = disturb.classify(win_mass, win_gyr, wspeed, final_mass)
    return {"run_id": run_id(iv, s, t0), "intervention": iv, "strength": s, "t0": t0,
            "achieved_dmass_frac": (M1e - M0) / M0, "final_mass": final_mass,
            "win_mass_mean": mmean, "net_speed": net, "n_units": n, "l4_class": cls}


def main():
    jobs = [(iv, s, t0) for iv, g in GRIDS.items() for s in g for t0 in PHASES]
    with Pool(os.cpu_count()) as p:
        rows = p.map(one, jobs, chunksize=1)
    keys = list(rows[0])
    with open(os.path.join(HERE, "lone-baselines.csv"), "w") as f:
        f.write(",".join(keys) + "\n")
        for r in rows:
            f.write(",".join(f"{r[k]:.6g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n")


if __name__ == "__main__":
    main()
