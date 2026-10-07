#!/usr/bin/env python3
"""L5-002 exploratory (not pre-registered): when do the last survivor and the first death split apart?

For every (intervention, phase) edge bracket (coarse + bisection), step both runs 400 steps
after the edit. Report the first step at which their mass, occupied area or gyradius
differ by more than 1% (relative). That step is the earliest any bulk morphometric could
separate the two outcomes.

    .venv/bin/python research/experiments/L5-002-survival-predictor/divergence.py
"""
import csv
import importlib.util
import os
import sys
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure as M  # noqa: E402  (loads Lane 4's run.py as M.l4)

F, l4 = M.F, M.l4
STEPS, TOL = 400, 0.01


def series(args):
    iv, s, t0 = args
    step = l4.engine("ref", 128, l4.R, l4.T)
    A, prev = l4.warm("ref", 128, t0)
    A = l4.disturb.INTERVENTIONS[iv](A, l4.get_frame(A, prev), s, l4.R)
    out = []
    for k in range(STEPS + 1):
        if k:
            A = step(A)
        if A.sum() > 0:
            c = F.centroid(A)
            out.append((F.mass(A, 13), F.occupied_area(A, 0.1, 13), F.gyradius(A, c, 13)))
        else:
            out.append((0.0, 0.0, 0.0))
    return np.array(out)


def main():
    l4.set_cond("base")
    rows = list(csv.DictReader(open(os.path.join(HERE, "features.csv"))))
    g = defaultdict(list)
    for r in rows:
        g[(r["intervention"], int(r["t0"]))].append(r)
    pairs = []
    for key, rs in sorted(g.items()):
        rs.sort(key=lambda r: float(r["strength"]))
        j = next(i for i, r in enumerate(rs) if r["label_survive"] == "0")
        pairs.append((key, float(rs[j - 1]["strength"]), float(rs[j]["strength"])))
    jobs = [(iv, s, t0) for (iv, t0), so, sf in pairs for s in (so, sf)]
    l4.set_cond("base")
    with Pool(os.cpu_count()) as p:
        res = p.map(series, jobs)
    lines = ["| intervention | t0 | s survive | s die | first 1% split: mass | area | gyradius (steps) |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for n, ((iv, t0), so, sf) in enumerate(pairs):
        a, b = res[2 * n], res[2 * n + 1]
        rel = np.abs(a - b) / np.maximum(np.abs(a), 1e-12)
        first = [int(np.argmax(rel[:, j] > TOL)) if np.any(rel[:, j] > TOL) else -1 for j in range(3)]
        lines.append(f"| {iv} | {t0} | {so:.6g} | {sf:.6g} | {first[0]} | {first[1]} | {first[2]} |")
    out = "\n".join(lines)
    print(out)
    open(os.path.join(HERE, "divergence.md"), "w").write(
        "First step after the edit at which the edge pair differs by >1% (exploratory).\n\n" + out + "\n")


if __name__ == "__main__":
    main()
