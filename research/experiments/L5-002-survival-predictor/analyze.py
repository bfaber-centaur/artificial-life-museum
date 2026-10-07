#!/usr/bin/env python3
"""L5-002 step 2: fit and score the pre-registered predictors (see PREREGISTRATION.md).

    .venv/bin/python research/experiments/L5-002-survival-predictor/analyze.py [--i005 features-i005.csv]

Leave-one-intervention-out over I001-I004. Each test is scored by balanced accuracy on the
held-out intervention's near-edge subset. A feature's score is the minimum over the four
folds. Prints the ranking and the selected set, and writes results.json. With --i005, the
selected model is refit on all I001-I004 runs and applied unchanged to I005.
"""
import argparse
import csv
import itertools
import json
import math
import os

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
IVS = ("I001", "I002", "I003", "I004")
THRESH = 0.90
BASE_MASS = 0.4358  # Lane 4 / Lane 1 baseline, for the lead-time band


def load(path):
    rows = list(csv.DictReader(open(path)))
    feats = [k for k in rows[0] if k.startswith("F")]
    X = np.array([[float(r[k]) if r[k] != "" else np.nan for k in feats] for r in rows])
    y = np.array([int(r["label_survive"]) for r in rows])
    return rows, feats, X, y


def near_edge(rows, bisect_ids, has_bisect=True):
    """Indices of the near-edge subset: bisection runs + coarse bracket ends per (iv, phase)."""
    idx = set()
    groups = {}
    for i, r in enumerate(rows):
        if r["run_id"] in bisect_ids:
            idx.add(i)
            continue
        groups.setdefault((r["intervention"], r["t0"]), []).append(i)
    for (iv, t0), ii in groups.items():
        ii = sorted(ii, key=lambda i: float(rows[i]["strength"]))
        lab = [int(rows[i]["label_survive"]) for i in ii]
        fails = [j for j, v in enumerate(lab) if v == 0]
        if not fails or fails[0] == 0:
            continue
        j = fails[0]
        idx.update((ii[j - 1], ii[j]))
    return np.array(sorted(idx))


def bal_acc(y, p):
    out = []
    for c in (0, 1):
        m = y == c
        if m.any():
            out.append(np.mean(p[m] == c))
    return float(np.mean(out))


# --- models ------------------------------------------------------------------

def fit_stump(x, y):
    ok = ~np.isnan(x)
    xs, ys = x[ok], y[ok]
    v = np.unique(xs)
    cuts = (v[:-1] + v[1:]) / 2 if len(v) > 1 else v
    best = (-1, 0.0, 1)
    for c in cuts:
        for d in (1, -1):  # d=1: survive if x > c
            p = (d * (xs - c) > 0).astype(int)
            b = bal_acc(ys, p)
            if b > best[0] + 1e-12:
                best = (b, c, d)
    return best[1], best[2]


def pred_stump(model, x):
    c, d = model
    p = (d * (x - c) > 0).astype(int)
    p[np.isnan(x)] = 0  # amendment A1: empty state -> die
    return p


def fit_logit(X, y, lam=1.0):
    ok = ~np.isnan(X).any(axis=1)
    Xs, ys = X[ok], y[ok]
    mu, sd = Xs.mean(0), Xs.std(0)
    sd[sd == 0] = 1
    Z = (Xs - mu) / sd

    def loss(w):
        z = Z @ w[1:] + w[0]
        return np.sum(np.logaddexp(0, z) - ys * z) + 0.5 * lam * np.sum(w[1:] ** 2)

    def grad(w):
        z = Z @ w[1:] + w[0]
        r = 1 / (1 + np.exp(-z)) - ys
        return np.concatenate([[r.sum()], Z.T @ r + lam * w[1:]])

    w = minimize(loss, np.zeros(Z.shape[1] + 1), jac=grad, method="L-BFGS-B").x
    return mu, sd, w


def pred_logit(model, X):
    mu, sd, w = model
    Z = (np.nan_to_num(X) - mu) / sd
    p = ((Z @ w[1:] + w[0]) >= 0).astype(int)
    p[np.isnan(X).any(axis=1)] = 0
    return p


# --- evaluation ----------------------------------------------------------------

def loio(cols, X, y, ivs_of, ne, kind):
    per = {}
    for iv in IVS:
        tr, te = ivs_of != iv, ivs_of == iv
        if kind == "stump":
            m = fit_stump(X[tr, cols[0]], y[tr])
            p = pred_stump(m, X[:, cols[0]])
        else:
            m = fit_logit(X[tr][:, cols], y[tr])
            p = pred_logit(m, X[:, cols])
        te_ne = np.intersect1d(np.flatnonzero(te), ne)
        per[iv] = {"near_edge": bal_acc(y[te_ne], p[te_ne]), "all": bal_acc(y[te], p[te]),
                   "n_near_edge": int(len(te_ne))}
    ne_scores = [v["near_edge"] for v in per.values()]
    return {"min": min(ne_scores), "mean": float(np.mean(ne_scores)), "folds": per}


def lag_of(name):
    return int(name.split("_k")[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--i005", default=None)
    ap.add_argument("--features", default=os.path.join(HERE, "features.csv"))
    ap.add_argument("--tag", default="", help="suffix for the results file (exploratory runs)")
    a = ap.parse_args()
    rows, feats, X, y = load(a.features)
    bis = {r["run_id"] for r in csv.DictReader(open(os.path.join(
        HERE, "..", "L4-001-disturbance-battery", "results", "bisect.csv")))}
    ne = near_edge(rows, bis)
    ivs_of = np.array([r["intervention"] for r in rows])
    print(f"{len(rows)} runs, near-edge subset {len(ne)} "
          f"({', '.join(f'{iv}: {np.sum(ivs_of[ne] == iv)}' for iv in IVS)})")

    singles = []
    for j, f in enumerate(feats):
        s = loio([j], X, y, ivs_of, ne, "stump")
        singles.append((f, s))
    singles.sort(key=lambda t: (-t[1]["min"], lag_of(t[0]), t[0]))
    pairs = []
    for j, k in itertools.combinations(range(len(feats)), 2):
        s = loio([j, k], X, y, ivs_of, ne, "logit")
        pairs.append(((feats[j], feats[k]), s))
    pairs.sort(key=lambda t: (-t[1]["min"], -t[1]["mean"], max(map(lag_of, t[0]))))

    def show(name, s):
        f = "  ".join(f"{iv} {v['near_edge']:.2f}/{v['all']:.2f}" for iv, v in s["folds"].items())
        print(f"  {name:<22} min {s['min']:.3f} mean {s['mean']:.3f} | {f}")

    print("Top single features (LOIO near-edge balanced accuracy; per fold near-edge/all):")
    for f, s in singles[:5]:
        show(f, s)
    print("Trivial baselines:")
    show("F1_k0 (post-edit mass)", dict(singles)["F1_k0"])
    print("Top pairs:")
    for f, s in pairs[:5]:
        show("+".join(f), s)

    if singles[0][1]["min"] >= THRESH:
        sel, kind = [singles[0][0]], "stump"
    elif pairs[0][1]["min"] >= THRESH:
        sel, kind = list(pairs[0][0]), "logit"
    else:
        sel, kind = None, None
    print("Selected:", sel, kind)

    out = {"n_runs": len(rows), "n_near_edge": int(len(ne)),
           "singles": [{"feature": f, **s} for f, s in singles],
           "pairs_top20": [{"features": list(f), **s} for f, s in pairs[:20]],
           "selected": sel, "model": kind}

    if sel:
        cols = [feats.index(f) for f in sel]
        model = fit_stump(X[:, cols[0]], y) if kind == "stump" else fit_logit(X[:, cols], y)
        out["frozen_model"] = ({"cut": float(model[0]), "direction": int(model[1])} if kind == "stump"
                               else {"mu": model[0].tolist(), "sd": model[1].tolist(),
                                     "w": model[2].tolist()})
        print("Frozen model (all I001-I004):", out["frozen_model"])
        # lead time: near-edge die runs whose mass at the lag is still inside Lane 4's +/-20% band
        lag = max(lag_of(f) for f in sel)
        die = ne[y[ne] == 0]
        mk = np.array([float(rows[i][f"mass_k{lag}"]) for i in die])
        inband = int(np.sum((mk >= 0.8 * BASE_MASS) & (mk <= 1.2 * BASE_MASS)))
        out["lead_time"] = {"lag": lag, "near_edge_die": int(len(die)), "mass_in_band": inband}
        print(f"Lead time: {inband}/{len(die)} near-edge die runs still have mass within "
              f"+/-20% of baseline at lag {lag}")
        pf = (pred_stump(model, X[:, cols[0]]) if kind == "stump" else pred_logit(model, X[:, cols]))
        out["in_sample_all"] = bal_acc(y, pf)

        if a.i005:
            r5, f5, X5, y5 = load(a.i005)
            assert f5 == feats
            ne5 = near_edge(r5, set())
            p5 = (pred_stump(model, X5[:, cols[0]]) if kind == "stump"
                  else pred_logit(model, X5[:, cols]))
            out["i005"] = {"n": len(r5), "n_near_edge": int(len(ne5)),
                           "all": bal_acc(y5, p5), "near_edge": bal_acc(y5[ne5], p5[ne5]),
                           "errors": [r5[i]["run_id"] for i in np.flatnonzero(p5 != y5)]}
            print("I005 (unseen):", {k: v for k, v in out["i005"].items() if k != "errors"})
            print("I005 errors:", out["i005"]["errors"])

    name = "results" + a.tag + ("-with-i005" if a.i005 else "") + ".json"
    with open(os.path.join(HERE, name), "w") as f:
        json.dump(out, f, indent=1, default=float)


if __name__ == "__main__":
    main()
