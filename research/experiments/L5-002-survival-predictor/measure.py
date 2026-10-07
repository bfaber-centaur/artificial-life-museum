#!/usr/bin/env python3
"""L5-002 step 1: rebuild every L4-001 disturbed state and measure the pre-registered features.

    .venv/bin/python research/experiments/L5-002-survival-predictor/measure.py

Reads Lane 4's results/coarse.csv and results/bisect.csv (base condition, N=128,
ref engine). For each run it rebuilds the disturbed state with Lane 4's own code,
steps it 0/5/10/20 steps on the same engine, and measures alm.morphometrics
features against the unperturbed control at the same t0 and lag. Writes
features.csv next to this script. Stops if any rebuilt post-edit mass differs
from Lane 4's by more than 1e-5 (pre-registered sanity gate).

`--extra FILE` measures runs listed in another L4-format CSV (used for I005).
"""
import argparse
import csv
import importlib.util
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
L4 = os.path.join(ROOT, "research", "experiments", "L4-001-disturbance-battery")
sys.path.insert(0, os.path.join(ROOT, "src"))
from alm import morphometrics as F  # noqa: E402

_spec = importlib.util.spec_from_file_location("l4run", os.path.join(L4, "run.py"))
l4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(l4)

import i005  # noqa: E402,F401  (registers I005 in alm.disturb.INTERVENTIONS)

LAGS = (0, 5, 10, 20)
R = 13


def raw(A):
    c = F.centroid(A)
    return {
        "mass": F.mass(A, R),
        "gyr": F.gyradius(A, c, R),
        "area": F.occupied_area(A, 0.1, R),
        "aniso": F.anisotropy(A, c)[0],
        "h2": float(F.rotational_harmonics(A, c, kmax=2)[2]),
    }


def trajectory(A, step):
    out = {}
    for k in range(LAGS[-1] + 1):
        if k:
            A = step(A)
        if k in LAGS:
            out[k] = raw(A) if A.sum() > 0 else None
    return out


_controls = {}


def control(t0):
    if t0 not in _controls:
        A, _ = l4.warm("ref", 128, t0)
        _controls[t0] = trajectory(A, l4.engine("ref", 128, l4.R, l4.T))
    return _controls[t0]


def measure(row):
    iv, s, t0 = row["intervention"], float(row["strength"]), int(row["t0"])
    step = l4.engine("ref", 128, l4.R, l4.T)
    A, prev = l4.warm("ref", 128, t0)
    frame = l4.get_frame(A, prev)
    A = l4.disturb.INTERVENTIONS[iv](A, frame, s, l4.R)
    m_edit = A.sum() / R**2
    gate = abs(m_edit - float(row["mass_after_edit"]))
    traj, ctrl = trajectory(A, step), control(t0)
    out = {"run_id": row["run_id"], "intervention": iv, "strength": s, "t0": t0,
           "label_survive": int(row["class"] == "RECOVERED"), "class": row["class"],
           "gate_dmass": gate}
    for k in LAGS:
        f, c = traj[k], ctrl[k]
        if f is None:
            for name in ("F1", "F2", "F3", "F4", "F5", "F6"):
                if name != "F6" or k:
                    out[f"{name}_k{k}"] = 0.0 if name in ("F1", "F3", "F6") else float("nan")
            out[f"mass_k{k}"] = 0.0
            continue
        out[f"F1_k{k}"] = f["mass"] / c["mass"]
        out[f"F2_k{k}"] = f["gyr"] / c["gyr"]
        out[f"F3_k{k}"] = f["area"] / c["area"]
        out[f"F4_k{k}"] = f["aniso"] - c["aniso"]
        out[f"F5_k{k}"] = f["h2"] - c["h2"]
        if k:
            out[f"F6_k{k}"] = f["mass"] / traj[0]["mass"]
        # lead-time bookkeeping (not a candidate feature): mass vs Lane 4's baseline band
        out[f"mass_k{k}"] = f["mass"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "features.csv"))
    a = ap.parse_args()
    l4.set_cond("base")
    srcs = [a.extra] if a.extra else [os.path.join(L4, "results", "coarse.csv"),
                                       os.path.join(L4, "results", "bisect.csv")]
    rows = [r for p in srcs for r in csv.DictReader(open(p))]
    with Pool(os.cpu_count()) as p:
        res = p.map(measure, rows, chunksize=4)
    worst = max(r["gate_dmass"] for r in res)
    print(f"{len(res)} runs; max |post-edit mass - Lane 4| = {worst:.2e}")
    if worst > 1e-5:
        sys.exit("sanity gate failed: rebuilt states do not match Lane 4's")
    keys = list(res[0].keys())
    for r in res:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in res:
            w.writerow({k: (f"{v:.9g}" if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
