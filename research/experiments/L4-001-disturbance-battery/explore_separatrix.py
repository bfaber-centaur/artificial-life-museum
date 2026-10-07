#!/usr/bin/env python3
"""Exploratory (not pre-registered): approach the I001 transition at t0 = 1000 to ~1e-12
and record how long the creature survives just above the threshold.

A saddle-type threshold predicts a transient that lengthens like log(1 / (s - s*)).
Output: results/separatrix-I001-t1000.csv (s, died, death_step, min_mass_before_death).
With --scan: a linear scan just below s*, results/separatrix-scan-I001-t1000-<engine>.csv.
Engine from L4_ENGINE (ref by default; alm = Lane 2's src/alm simulator).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402
from alm import disturb  # noqa: E402

IV, T0, H = "I001", 1000, 1500
ENGINE = os.environ.get("L4_ENGINE", "ref")  # "alm" needs Lane 2's simulator (see run.py)


def trial(s):
    step = run.engine(ENGINE, 128, run.R, run.T)
    A, prev = run.warm(ENGINE, 128, T0)
    A = disturb.INTERVENTIONS[IV](A, disturb.frame_from(A, prev), s, run.R)
    masses = []
    for k in range(1, H + 1):
        A = step(A)
        m = A.sum() / run.R ** 2
        masses.append(m)
        if m < 0.01:
            return True, k, masses
    return False, None, masses


def main():
    import csv
    with open(os.path.join(HERE, "results", "bisect-brackets.csv")) as f:
        b = next(r for r in csv.DictReader(f) if r["intervention"] == IV and int(r["t0"]) == T0)
    lo, hi = float(b["s_ok"]), float(b["s_fail"])
    rows = []
    while hi - lo > 1e-12:
        mid = (lo + hi) / 2
        died, k, masses = trial(mid)
        # time spent near the baseline mass before collapse
        rows.append((mid, int(died), k if died else "", min(masses)))
        print(f"s={mid:.13f} died={died} death_step={k}", flush=True)
        if died:
            hi = mid
        else:
            lo = mid
    out = os.path.join(HERE, "results", f"separatrix-{IV}-t{T0}.csv")
    with open(out, "w") as f:
        f.write("strength,died,death_step,min_mass\n")
        for r in rows:
            f.write("%.13f,%d,%s,%.6f\n" % r)


def scan(s_star=0.10109887614125, lo=-4e-7, n=41):
    """Linear scan of s* + d, d in [lo, 0], to map survival islands below the threshold."""
    out = os.path.join(HERE, "results", f"separatrix-scan-{IV}-t{T0}-{ENGINE}.csv")
    with open(out, "w") as f:
        f.write("strength,offset,died,death_step\n")
        for d in np.linspace(lo, 0, n):
            died, k, _ = trial(s_star + d)
            f.write(f"{s_star + d:.15f},{d:+.3e},{int(died)},{k if died else ''}\n")
            print(f"{d:+.2e} {'D' if died else 'R'}", flush=True)


if __name__ == "__main__":
    if "--scan" in sys.argv:
        scan()
    else:
        main()
