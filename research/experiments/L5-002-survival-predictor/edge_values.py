#!/usr/bin/env python3
"""L5-002 exploratory (not pre-registered): the value of each feature AT each intervention's edge.

For every (intervention, phase), take the last surviving and first dying run by strength
(coarse + bisection) and print the feature at both. A feature that can predict across
disturbances needs these edge intervals to line up across interventions.

    .venv/bin/python research/experiments/L5-002-survival-predictor/edge_values.py
"""
import csv
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FEATS = ["F1_k0", "F3_k0", "F1_k20", "F3_k20", "F6_k20", "F2_k20", "F4_k20"]

rows = list(csv.DictReader(open(os.path.join(HERE, "features.csv"))))
g = defaultdict(list)
for r in rows:
    g[(r["intervention"], int(r["t0"]))].append(r)
edge = defaultdict(lambda: defaultdict(list))
for (iv, t0), rs in g.items():
    rs.sort(key=lambda r: float(r["strength"]))
    first_die = next(i for i, r in enumerate(rs) if r["label_survive"] == "0")
    ok, bad = rs[first_die - 1], rs[first_die]
    for f in FEATS:
        edge[iv][f].append((float(ok[f]) if ok[f] else np.nan, float(bad[f]) if bad[f] else np.nan))

lines = ["| feature | " + " | ".join(sorted(edge)) + " |", "| --- |" + " --- |" * len(edge)]
for f in FEATS:
    cells = []
    for iv in sorted(edge):
        a = np.array(edge[iv][f])
        cells.append(f"{np.nanmean(a[:, 0]):.4f} / {np.nanmean(a[:, 1]):.4f}")
    lines.append(f"| {f} | " + " | ".join(cells) + " |")
out = "\n".join(lines)
print("Feature at last survivor / first death (mean over 5 phases):\n" + out)
open(os.path.join(HERE, "edge_values.md"), "w").write(
    "Feature value at the last surviving / first dying run (mean over 5 phases). Exploratory.\n\n" + out + "\n")
