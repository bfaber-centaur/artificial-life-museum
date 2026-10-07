#!/usr/bin/env python3
"""L5-003: score the edge-direction coordinate and the null coordinate (see PREREGISTRATION.md).

    .venv/bin/python research/experiments/L5-003-edge-direction/score.py

Uses coords.csv from project.py. In fold "minus I00x", the stump is fitted on the
coordinate along u_minus_I00x for the other three disturbances and tested on I00x's
near-edge subset. The lag is selected by the pre-registered rule, then the "u_all"
model is refit on all I001-I004 and applied frozen to I005. Writes results.json.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
L502 = os.path.join(HERE, "..", "L5-002-survival-predictor")
sys.path.insert(0, L502)
from analyze import bal_acc, fit_stump, near_edge, pred_stump  # noqa: E402

LAGS = (0, 5, 10, 20, 30)
IVS = ("I001", "I002", "I003", "I004")
THRESH = 0.90
BASE_MASS = 0.4358


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "coords.csv"))))
    l4 = [r for r in rows if r["intervention"] in IVS]
    i5 = [r for r in rows if r["intervention"] == "I005"]
    bis = {r["run_id"] for r in csv.DictReader(open(os.path.join(
        ROOT, "research/experiments/L4-001-disturbance-battery/results/bisect.csv")))}
    bis5 = {r["run_id"] for r in csv.DictReader(open(os.path.join(HERE, "i005-bisect.csv")))}
    ne = near_edge(l4, bis)
    ne5 = near_edge(i5, bis5)
    y = np.array([int(r["label_survive"]) for r in l4])
    y5 = np.array([int(r["label_survive"]) for r in i5])
    ivs = np.array([r["intervention"] for r in l4])
    col = lambda rs, name: np.array([float(r[name]) if r[name] != "" else np.nan for r in rs])  # noqa: E731

    out = {"n_runs": len(l4), "n_near_edge": int(len(ne)), "n_i005": len(i5),
           "n_i005_near_edge": int(len(ne5)), "lags": {}}
    print(f"I001-I004: {len(l4)} runs, near-edge {len(ne)}; I005: {len(i5)} runs, near-edge {len(ne5)}")
    for k in LAGS:
        res = {}
        for kind in ("edge", "null"):
            folds = {}
            for iv in IVS:
                x = col(l4, f"u_minus_{iv}_k{k}" if kind == "edge" else f"null_k{k}")
                tr, te = ivs != iv, ivs == iv
                m = fit_stump(x[tr], y[tr])
                p = pred_stump(m, x)
                te_ne = np.intersect1d(np.flatnonzero(te), ne)
                folds[iv] = {"near_edge": bal_acc(y[te_ne], p[te_ne]), "all": bal_acc(y[te], p[te])}
            s = [v["near_edge"] for v in folds.values()]
            res[kind] = {"min": min(s), "mean": float(np.mean(s)), "folds": folds}
        out["lags"][k] = res
        for kind in ("edge", "null"):
            f = "  ".join(f"{iv} {v['near_edge']:.2f}/{v['all']:.2f}" for iv, v in res[kind]["folds"].items())
            print(f"k={k:<3} {kind:<5} min {res[kind]['min']:.3f} mean {res[kind]['mean']:.3f} | {f}")

    sel = next((k for k in LAGS if out["lags"][k]["edge"]["min"] >= THRESH), None)
    out["selected_lag"] = sel
    print("Selected lag:", sel)
    if sel is not None:
        x = col(l4, f"u_all_k{sel}")
        m = fit_stump(x, y)
        x5 = col(i5, f"u_all_k{sel}")
        p5 = pred_stump(m, x5)
        out["frozen"] = {"cut": float(m[0]), "direction": int(m[1])}
        out["i005"] = {"all": bal_acc(y5, p5), "near_edge": bal_acc(y5[ne5], p5[ne5]),
                       "errors": [i5[i]["run_id"] for i in np.flatnonzero(p5 != y5)]}
        xn = col(l4, f"null_k{sel}")
        mn = fit_stump(xn, y)
        pn = pred_stump(mn, col(i5, f"null_k{sel}"))
        out["i005_null"] = {"all": bal_acc(y5, pn), "near_edge": bal_acc(y5[ne5], pn[ne5])}
        print("Frozen model:", out["frozen"])
        print("I005 edge coordinate:", {k_: v for k_, v in out["i005"].items() if k_ != "errors"},
              "errors:", out["i005"]["errors"])
        print("I005 null coordinate:", out["i005_null"])
        # lead time: near-edge dying runs whose mass at the selected lag is in Lane 4's band
        feats = {r["run_id"]: r for r in csv.DictReader(open(os.path.join(
            L502, "features-exploratory-lags.csv" if sel in (30,) else "features.csv")))}
        key = f"mass_k{sel}"
        die = [l4[i]["run_id"] for i in ne if y[i] == 0]
        if all(key in feats[d] for d in die):
            mk = np.array([float(feats[d][key]) for d in die])
            inb = int(np.sum((mk >= 0.8 * BASE_MASS) & (mk <= 1.2 * BASE_MASS)))
            out["lead_time"] = {"lag": sel, "near_edge_die": len(die), "mass_in_band": inb}
            print(f"Lead time: {inb}/{len(die)} near-edge dying runs still have mass within ±20% at lag {sel}")
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
