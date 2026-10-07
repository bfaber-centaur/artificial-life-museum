#!/usr/bin/env python3
"""L5-003: bisect the I005 (rear deletion) edge per phase with Lane 4's runner and classifier.

    .venv/bin/python research/experiments/L5-003-edge-direction/bisect_i005.py

Starts from the L5-002 coarse brackets (i005-runs.csv). Bisects to a width of 1/256 in s, stopping
early when no pixel lies between the two radii (Lane 4's I002 rule). Writes i005-bisect.csv.
"""
import csv
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
L502 = os.path.join(HERE, "..", "L5-002-survival-predictor")
sys.path.insert(0, L502)
import measure as M  # noqa: E402  (Lane 4's run.py as M.l4; registers I005)

l4 = M.l4


def bracket_job(args):
    t0, lo, hi = args
    A, prev = l4.warm("ref", 128, t0)
    f = l4.get_frame(A, prev)
    px, py = f.cx - 0.5 * l4.R * f.hx, f.cy - 0.5 * l4.R * f.hy
    dx, dy = l4.disturb.offsets(A.shape, px, py)
    dist = np.sqrt(dx ** 2 + dy ** 2) / l4.R
    rows = []
    while hi - lo > l4.BISECT_WIDTH:
        if not np.any((dist >= lo) & (dist < hi)):
            break
        mid = round((lo + hi) / 2, 6)
        r = l4.run("I005", mid, t0, 128, "ref")
        r["template_corr"] = float("nan")
        rows.append(r)
        if r["class"] == "RECOVERED":
            lo = mid
        else:
            hi = mid
    return rows


def main():
    l4.set_cond("base")
    coarse = list(csv.DictReader(open(os.path.join(L502, "i005-runs.csv"))))
    jobs = []
    for t0 in l4.PHASES:
        rs = sorted((r for r in coarse if int(r["t0"]) == t0), key=lambda r: float(r["strength"]))
        j = next(i for i, r in enumerate(rs) if r["class"] != "RECOVERED")
        jobs.append((t0, float(rs[j - 1]["strength"]), float(rs[j]["strength"])))
    with Pool(len(jobs)) as p:
        res = p.map(bracket_job, jobs)
    rows = [r for rs in res for r in rs]
    l4.write_rows(os.path.join(HERE, "i005-bisect.csv"), rows)
    for (t0, lo, hi), rs in zip(jobs, res):
        print(t0, lo, hi, [(r["strength"], r["class"][0]) for r in rs])


if __name__ == "__main__":
    main()
