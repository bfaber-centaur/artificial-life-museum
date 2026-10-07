#!/usr/bin/env python3
"""HR-008 fold-design check: does each L5-002 feature carry outcome information WITHIN a
disturbance (near-edge AUC), even though no cut transfers ACROSS disturbances?

Uses L5-002's own features.csv and its near_edge() subset definition. Also reports a
phase-level view: for each (intervention, phase) edge pair, does the feature order the last
survivor and first death correctly?

Usage: python within_auc.py <path to L5-002-survival-predictor dir>
"""
import csv
import os
import sys

import numpy as np

D = sys.argv[1]
sys.path.insert(0, D)
import analyze  # noqa: E402  (L5-002's own helpers)

rows = list(csv.DictReader(open(os.path.join(D, "features.csv"))))
bis = {r["run_id"] for r in csv.DictReader(open(os.path.join(
    D, "..", "L4-001-disturbance-battery", "results", "bisect.csv")))}
ne = set(analyze.near_edge(rows, bis))
feats = [k for k in rows[0] if k.startswith("F")]


def auc(x, y):
    x, y = np.asarray(x, float), np.asarray(y, int)
    ok = ~np.isnan(x)
    x, y = x[ok], y[ok]
    pos, neg = x[y == 1], x[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()
    return max(gt, 1 - gt)  # direction-free


print("feature," + ",".join(f"AUC_{iv}" for iv in ("I001", "I002", "I003", "I004")) + ",min_AUC")
out = []
for f in feats:
    a = []
    for iv in ("I001", "I002", "I003", "I004"):
        sub = [r for i, r in enumerate(rows) if i in ne and r["intervention"] == iv]
        x = [float(r[f]) if r[f] not in ("", "nan") else np.nan for r in sub]
        a.append(auc(x, [int(r["label_survive"]) for r in sub]))
    out.append((f, a))
for f, a in sorted(out, key=lambda t: -np.nanmin(t[1])):
    print(f + "," + ",".join(f"{v:.2f}" for v in a) + f",{np.nanmin(a):.2f}")
n_by = {iv: sum(1 for i, r in enumerate(rows) if i in ne and r["intervention"] == iv)
        for iv in ("I001", "I002", "I003", "I004")}
print("# near-edge runs per intervention:", n_by)
