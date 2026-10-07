#!/usr/bin/env python3
"""Lane 5 baseline: alm.morphometrics on S001 (Orbium O2u), and which features depend on heading.

Run from repo root after ./scripts/bootstrap.sh:

    .venv/bin/python research/experiments/L5-baseline/measure_s001.py

Stepping path: Lane 2's simulator (alm.Lenia with the S001 rule from
alm.specimens: poly/poly, R=13, T=10, mu=0.15, sigma=0.015, Euler + clip,
float64, 128x128 torus). The first version of this experiment stepped Lane 1's
reference transcription instead; the two agree (see README).

For start rotations 0, 23 and 45 degrees (bilinear, as in Lane 1's
lattice_heading.py) it steps 4000 steps, records alm.morphometrics.snapshot every
step, and summarises steps 1000..4000. Writes per-step traces and summary.csv
next to this script.
"""
import csv
import os
import sys

import numpy as np
import scipy.ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from alm import Lenia, specimens  # noqa: E402
from alm import morphometrics as F  # noqa: E402

SPEC = specimens.load("S001")
N, R, T = 128, SPEC.rule.R, SPEC.rule.T
STEPS, BURN = 4000, 1000
ROTATIONS = (0, 23, 45)
FEATURES = ["mass", "gyradius", "anisotropy", "area", "harmonic_1", "harmonic_2", "harmonic_3"]


def start_state(rot):
    cells = SPEC.cells / 255.0
    z = cells if rot == 0 else np.clip(scipy.ndimage.rotate(cells, rot, order=1, reshape=True), 0, 1)
    A = np.zeros((N, N))
    h, w = z.shape
    A[(N - h) // 2:(N - h) // 2 + h, (N - w) // 2:(N - w) // 2 + w] = z
    return A


def run(rot):
    sim = Lenia(SPEC.rule, start_state(rot))
    rows = []
    for t in range(STEPS + 1):
        if t:
            sim.step()
        A = sim.A
        s = F.snapshot(A, R=R)
        s["step"] = t
        rows.append(s)
    return rows, A


def summarise(rot, rows):
    tail = rows[BURN:]
    cs = [(r["cy"], r["cx"]) for r in tail]
    v = F.velocity(cs, (N, N))                      # cells/step
    vm = v.mean(axis=0)
    out = {
        "rotation_deg": rot,
        "alive": int(rows[-1]["mass"] > 1e-10),
        "speed_cells_per_step": float(np.hypot(*v.T).mean()),
        "speed_R_per_time": float(np.hypot(*v.T).mean() * T / R),
        "heading_deg": float(np.degrees(np.arctan2(vm[0], vm[1])) % 360),
        "max_wrap_extent": max(r["wrap_extent"] for r in tail),
    }
    for k in FEATURES:
        x = np.array([r[k] for r in tail])
        out[f"{k}_mean"] = float(x.mean())
        out[f"{k}_sd"] = float(x.std())
        out[f"{k}_period"] = F.dominant_period(x)
    # Major axis relative to heading: is the body elongated along or across its motion?
    rel = np.array([(r["major_axis_deg"] - out["heading_deg"]) % 180 for r in tail])
    out["major_axis_minus_heading_deg"] = float(np.degrees(np.angle(np.exp(2j * np.radians(rel)).mean())) / 2)   # signed, in (-90, 90]
    return out


def main():
    summaries = []
    for rot in ROTATIONS:
        rows, final = run(rot)
        path = os.path.join(HERE, f"trace-rot{rot:02d}.csv")
        keys = ["step"] + [k for k in rows[0] if k != "step"]
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({k: (f"{r[k]:.9g}" if isinstance(r[k], float) else r[k]) for k in keys})
        s = summarise(rot, rows)
        summaries.append(s)
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in s.items()}, flush=True)
    with open(os.path.join(HERE, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0]))
        w.writeheader()
        for s in summaries:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in s.items()})


if __name__ == "__main__":
    main()
