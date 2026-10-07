"""Does S001's heading lock to lattice directions?

Rotate the catalog cells by a sweep of angles (bilinear), run each on the
baseline rule, and measure the travel heading in early and late windows. A
continuum creature would give heading = heading0 - angle (a straight line);
lattice locking shows up as plateaus at low-order rational directions.

    .venv/bin/python -m alm_check.heading [--R 13] [--horizon 800]
"""

from __future__ import annotations

import argparse
import csv
import os
from fractions import Fraction
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

from .lenia import REPO, Rule, World, periodic_centroid, place
from .sweeps import OUT, R0, scaled_orbium

EVERY = 5


def rotated_cells(angle: float, R: float) -> np.ndarray:
    cells = scaled_orbium(R, order=1 if R != R0 else 0)
    pad = np.pad(cells, cells.shape[0] // 2)
    return np.clip(ndimage.rotate(pad, angle, reshape=True, order=1), 0, 1)


def headings(job):
    angle, R, horizon = job
    rule = Rule(R=R)
    n = 2 * int(round(64 * R / R0))
    w = World(place(rotated_cells(angle, R), n), rule)
    steps = int(horizon * rule.T)
    pos = np.zeros((steps // EVERY + 1, 2))
    prev = np.array(periodic_centroid(w.A))
    acc = np.zeros(2)
    for s in range(1, steps + 1):
        w.step()
        if s % EVERY == 0:
            if w.A.sum() / R**2 < 1e-10:
                return dict(angle=angle, R=R, n=n, alive=0)
            c = np.array(periodic_centroid(w.A))
            acc += (c - prev + n / 2) % n - n / 2
            prev = c
            pos[s // EVERY] = acc
    tu = np.arange(len(pos)) * EVERY / rule.T

    def head(t0, t1):
        i0, i1 = np.searchsorted(tu, [t0, t1])
        d = pos[min(i1, len(pos) - 1)] - pos[i0]
        return float(np.degrees(np.arctan2(d[0], d[1]))), float(np.hypot(*d) / (tu[min(i1, len(pos) - 1)] - tu[i0]) / R)

    early, v_e = head(100, 200)
    late, v_l = head(horizon - 100, horizon)
    frac = Fraction(np.tan(np.radians(late))).limit_denominator(8) if abs(late) < 89 else None
    return dict(angle=angle, R=R, n=n, alive=1, heading_early=early, heading_late=late,
                drift_deg=late - early, speed_late=v_l,
                nearest_rational_slope=str(frac) if frac is not None else "inf",
                rational_heading=float(np.degrees(np.arctan(float(frac)))) if frac is not None else 90.0)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=float, default=13)
    ap.add_argument("--horizon", type=float, default=800)
    ap.add_argument("--step", type=float, default=2.5)
    a = ap.parse_args(argv)
    angles = np.arange(0, 90 + 1e-9, a.step)
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    with Pool(os.cpu_count()) as p:
        rows = p.map(headings, [(float(x), a.R, a.horizon) for x in angles], chunksize=1)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"heading-R{a.R:g}.csv"
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, list(dict.fromkeys(k for r in rows for k in r)))
        wr.writeheader()
        for r in rows:
            wr.writerow({k: (f"{v:.5g}" if isinstance(v, float) else v) for k, v in r.items()})
    print(f"wrote {path.relative_to(REPO)}")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
