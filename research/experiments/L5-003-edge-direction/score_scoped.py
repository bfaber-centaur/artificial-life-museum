#!/usr/bin/env python3
"""L5-003 exploratory (NOT pre-registered): the edge direction built only from I001 and I003.

Added after the pre-registered result and Lane 7's HR-008. Lane 7 measured a single unstable
edge state only for I001 (attenuation) and I003 (frontal addition). I002, I004 and I005 are
pixel-quantized edits with no approach to an edge state at R = 13.
  (a) I001 <-> I003 cross-prediction: u and the cut come from one, and are tested on the other.
  (b) u and the cut come from I001+I003, then transfer to I002, I004 and I005.
Near-edge balanced accuracy (all runs). The null coordinate is shown alongside.

    .venv/bin/python research/experiments/L5-003-edge-direction/score_scoped.py
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "L5-002-survival-predictor"))
from analyze import bal_acc, fit_stump, near_edge, pred_stump  # noqa: E402

rows = list(csv.DictReader(open(os.path.join(HERE, "coords.csv"))))
bis = {r["run_id"] for p in (os.path.join(ROOT, "research/experiments/L4-001-disturbance-battery/results/bisect.csv"),
                              os.path.join(HERE, "i005-bisect.csv")) for r in csv.DictReader(open(p))}
ne = set(near_edge(rows, bis).tolist())
y = np.array([int(r["label_survive"]) for r in rows])
iv = np.array([r["intervention"] for r in rows])
col = lambda name: np.array([float(r[name]) if r[name] != "" else np.nan for r in rows])  # noqa: E731
out = {}
lines = []


def score(xname, train, test):
    x = col(xname)
    tr = np.isin(iv, train)
    m = fit_stump(x[tr], y[tr])
    p = pred_stump(m, x)
    res = {}
    for t in test:
        te = iv == t
        te_ne = np.array([i for i in np.flatnonzero(te) if i in ne])
        res[t] = (bal_acc(y[te_ne], p[te_ne]), bal_acc(y[te], p[te]), int(np.sum(p[te_ne] != y[te_ne])), len(te_ne))
    return res


for k in (20, 30):
    for label, xname, train, test in [
        ("I001 -> I003", f"x_onlyI001_k{k}", ["I001"], ["I003"]),
        ("I003 -> I001", f"x_onlyI003_k{k}", ["I003"], ["I001"]),
        ("I001+I003 -> others", f"x_I001I003_k{k}", ["I001", "I003"], ["I002", "I004", "I005"]),
    ]:
        for kind, xn in (("edge", xname), ("null", f"null_k{k}")):
            r = score(xn, train, test)
            out[f"k{k} {label} {kind}"] = r
            lines.append(f"k={k} {label:<20} {kind:<4} " + "  ".join(
                f"{t}: {a:.2f} ({b:.2f}), {e}/{n} near-edge errors" for t, (a, b, e, n) in r.items()))
print("\n".join(lines))
json.dump(out, open(os.path.join(HERE, "results-scoped-exploratory.json"), "w"), indent=1)
