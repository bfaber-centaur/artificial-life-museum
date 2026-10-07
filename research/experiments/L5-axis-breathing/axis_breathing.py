#!/usr/bin/env python3
"""L5 follow-up to Lane 7 HR-006: what S001's shape does when it travels along a grid axis.

Run from repo root:

    .venv/bin/python research/experiments/L5-axis-breathing/axis_breathing.py

S001 (poly/poly, mu=0.15, sigma=0.015, T=10) stepped on Lane 2's alm.Lenia. The
catalog cells are zoomed to R (bilinear) and rotated (bilinear) the same way as
Lane 7's H001 initial_state; the grid is round(128 R / 13) rounded up to even.
Start rotation 0 lands on the 68.2 deg plateau, and start rotations near 70 land
on the axis-locked plateau. Each run is 8000 steps. Statistics cover steps
2000-7999 (6000 samples), with every step sampled.

For each (R, rotation) it reports heading, speed, and the mean, sd, min and max
of anisotropy. It also gives anisotropy's dominant period (steps and time units)
and the sd of the per-step heading. Writes results.csv next to this script.
"""
import csv
import os
import sys
from multiprocessing import Pool

import numpy as np
import scipy.ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from alm import Lenia, specimens  # noqa: E402
from alm import morphometrics as F  # noqa: E402
from alm.lenia import Rule  # noqa: E402

SPEC = specimens.load("S001")
STEPS, BURN = 8000, 2000
CASES = [(13, 0), (13, 70), (20, 0), (20, 70), (26, 0), (26, 67)]


def grid_size(R):
    n = int(round(128 * R / 13))
    return n + (n % 2)


def start_state(R, rot, n):
    c = SPEC.cells / 255.0
    if R != 13:
        c = np.clip(scipy.ndimage.zoom(c, R / 13, order=1), 0, 1)
    if rot:
        c = np.clip(scipy.ndimage.rotate(c, rot, order=1, reshape=True), 0, 1)
    A = np.zeros((n, n))
    h, w = c.shape
    A[(n - h) // 2:(n - h) // 2 + h, (n - w) // 2:(n - w) // 2 + w] = c
    return A


def measure(case):
    R, rot = case
    n = grid_size(R)
    r0 = SPEC.rule
    sim = Lenia(Rule(R=R, T=r0.T, mu=r0.mu, sigma=r0.sigma, beta=r0.beta,
                     kernel=r0.kernel, growth=r0.growth), start_state(R, rot, n))
    cs, an = [], []
    for t in range(STEPS):
        sim.step()
        if t >= BURN:
            c = F.centroid(sim.A)
            cs.append(c)
            an.append(F.anisotropy(sim.A, c)[0])
    an = np.array(an)
    v = F.velocity(cs, (n, n))
    vm = v.mean(axis=0)
    hd = np.degrees(np.arctan2(v[:, 0], v[:, 1]))
    hd_mean = np.degrees(np.arctan2(vm[0], vm[1]))
    period = F.dominant_period(an)
    return {
        "R": R, "rotation_deg": rot, "grid": n,
        "alive": int(sim.A.sum() > 1e-10),
        "heading_deg": hd_mean,
        "heading_sd_deg": float(np.std((hd - hd_mean + 180) % 360 - 180)),
        "speed_R_per_time": float(np.hypot(*v.T).mean() * r0.T / R),
        "aniso_mean": float(an.mean()), "aniso_sd": float(an.std()),
        "aniso_min": float(an.min()), "aniso_max": float(an.max()),
        "aniso_period_steps": period, "aniso_period_time": period / r0.T,
    }


def main():
    with Pool(min(len(CASES), os.cpu_count() or 1)) as p:
        rows = p.map(measure, CASES)
    with open(os.path.join(HERE, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    for r in rows:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)


if __name__ == "__main__":
    main()
