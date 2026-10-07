#!/usr/bin/env python3
"""L5-003: estimate edge-pair directions and project every disturbed state onto them.

    .venv/bin/python research/experiments/L5-003-edge-direction/project.py

Pass 1 rebuilds the final edge bracket (highest survivor, lowest death) for every
(disturbance, phase), for I001-I005. At each lag it builds the direction u_k for every
leave-one-out fold over I001-I004 ("-I00x") and for all four together ("all").
Pass 2 rebuilds every run (L4-001 coarse + bisect, I005 coarse + bisect) and writes the
coordinate on each direction plus the null coordinate to coords.csv. directions.json
holds the cosine diagnostics. See PREREGISTRATION.md.
"""
import csv
import itertools
import json
import os
import sys
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
L502 = os.path.join(HERE, "..", "L5-002-survival-predictor")
L4R = os.path.join(ROOT, "research", "experiments", "L4-001-disturbance-battery", "results")
sys.path.insert(0, L502)
import measure as M  # noqa: E402

F, l4 = M.F, M.l4
LAGS = (0, 5, 10, 20, 30)
IVS = ("I001", "I002", "I003", "I004")
N = 128


def comoving(A):
    """Exact periodic Fourier shift putting the centroid at (64, 64)."""
    cy, cx = F.centroid(A)
    ky = np.fft.fftfreq(N)[:, None]
    kx = np.fft.fftfreq(N)[None, :]
    ph = np.exp(-2j * np.pi * (ky * (N / 2 - cy) + kx * (N / 2 - cx)))
    return np.real(np.fft.ifft2(np.fft.fft2(A) * ph))


def lagged(iv, s, t0):
    """{lag: comoving state or None if empty} for a disturbed run (s=None: control)."""
    step = l4.engine("ref", N, l4.R, l4.T)
    A, prev = l4.warm("ref", N, t0)
    if s is not None:
        A = l4.disturb.INTERVENTIONS[iv](A, l4.get_frame(A, prev), s, l4.R)
    out = {}
    for k in range(LAGS[-1] + 1):
        if k:
            A = step(A)
        if k in LAGS:
            out[k] = comoving(A) if A.sum() > 0 else None
    return out


def load_runs():
    srcs = [os.path.join(L4R, "coarse.csv"), os.path.join(L4R, "bisect.csv"),
            os.path.join(L502, "i005-runs.csv"), os.path.join(HERE, "i005-bisect.csv")]
    return [r for p in srcs for r in csv.DictReader(open(p))]


def edge_pairs(runs):
    g = defaultdict(list)
    for r in runs:
        g[(r["intervention"], int(r["t0"]))].append(r)
    pairs = {}
    for key, rs in g.items():
        surv = [float(r["strength"]) for r in rs if r["class"] == "RECOVERED"]
        die = [float(r["strength"]) for r in rs if r["class"] != "RECOVERED"]
        s_ok = max(s for s in surv if s < min(die))
        pairs[key] = (s_ok, min(die))
    return pairs


def _pair_job(args):
    (iv, t0), (so, sf) = args
    a, b = lagged(iv, so, t0), lagged(iv, sf, t0)
    return {k: (None if a[k] is None or b[k] is None else (b[k] - a[k]).ravel()) for k in LAGS}


def _ctrl_job(t0):
    return t0, lagged(None, None, t0)


DIRS = None
CTRL = None


def _init(dirs, ctrl):
    global DIRS, CTRL
    DIRS, CTRL = dirs, ctrl


def _run_job(r):
    iv, s, t0 = r["intervention"], float(r["strength"]), int(r["t0"])
    st = lagged(iv, s, t0)
    out = {"run_id": r["run_id"], "intervention": iv, "strength": s, "t0": t0,
           "label_survive": int(r["class"] == "RECOVERED")}
    for k in LAGS:
        c = CTRL[t0][k]
        if st[k] is None:
            for name in list(DIRS[k]) + ["null"]:
                out[f"{name}_k{k}"] = float("nan")
            continue
        d = (st[k] - c).ravel()
        for name, u in DIRS[k].items():
            out[f"{name}_k{k}"] = float(d @ u)
        out[f"null_k{k}"] = float(d @ (c.ravel() / np.linalg.norm(c)))
    return out


def main():
    l4.set_cond("base")
    runs = load_runs()
    pairs = edge_pairs(runs)
    keys = sorted(pairs)
    with Pool(os.cpu_count()) as p:
        diffs = dict(zip(keys, p.map(_pair_job, [(k, pairs[k]) for k in keys])))
        ctrl = dict(p.map(_ctrl_job, l4.PHASES))

    dirs, diag = {}, {}
    for k in LAGS:
        unit = {key: d / np.linalg.norm(d) for key, d in ((key, diffs[key][k]) for key in keys)
                if d is not None and np.linalg.norm(d) > 0}
        per_iv = {}
        for iv in IVS + ("I005",):
            vs = [v for (j, _), v in unit.items() if j == iv]
            if vs:
                m = np.mean(vs, axis=0)
                per_iv[iv] = m / np.linalg.norm(m)
        dirs[k] = {}
        for fold in ("all",) + tuple(f"-{iv}" for iv in IVS):
            train = IVS if fold == "all" else tuple(i for i in IVS if i != fold[1:])
            vs = [v for (j, _), v in unit.items() if j in train]
            m = np.mean(vs, axis=0)
            dirs[k][fold.replace("-", "u_minus_") if fold != "all" else "u_all"] = m / np.linalg.norm(m)
        # Exploratory (added after the pre-registered result and Lane 7's HR-008): directions
        # from the two disturbances with a measured unstable edge state only.
        for name, train in (("x_I001I003", ("I001", "I003")), ("x_onlyI001", ("I001",)),
                            ("x_onlyI003", ("I003",))):
            m = np.mean([v for (j, _), v in unit.items() if j in train], axis=0)
            dirs[k][name] = m / np.linalg.norm(m)
        cos = {f"{a}~{b}": float(per_iv[a] @ per_iv[b])
               for a, b in itertools.combinations(sorted(per_iv), 2)}
        within = {}
        for iv in per_iv:
            vs = [v for (j, _), v in unit.items() if j == iv]
            within[iv] = float(np.mean([a @ b for a, b in itertools.combinations(vs, 2)])) if len(vs) > 1 else None
        diag[k] = {"between_disturbances": cos, "within_disturbance_mean": within}
        print(f"lag {k}: within {', '.join(f'{i} {v:.2f}' for i, v in within.items() if v is not None)}")
        print("        between " + ", ".join(f"{p_} {v:.2f}" for p_, v in cos.items()))

    with Pool(os.cpu_count(), initializer=_init, initargs=(dirs, ctrl)) as p:
        res = p.map(_run_job, runs, chunksize=4)
    cols = list(res[0])
    with open(os.path.join(HERE, "coords.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in res:
            w.writerow({k: (f"{v:.9g}" if isinstance(v, float) else v) for k, v in r.items()})
    with open(os.path.join(HERE, "directions.json"), "w") as f:
        json.dump({"edge_pairs": {f"{a}@{b}": v for (a, b), v in pairs.items()}, "cosines": diag}, f, indent=1)
    np.savez_compressed(os.path.join(HERE, "directions.npz"),
                        **{f"{name}_k{k}": u.reshape(N, N) for k in LAGS for name, u in dirs[k].items()})


if __name__ == "__main__":
    main()
