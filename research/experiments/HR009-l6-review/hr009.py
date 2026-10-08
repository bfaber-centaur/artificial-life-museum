#!/usr/bin/env python3
"""HR-009 runner (PREREGISTRATION.md in this directory). Needs a checkout of Lane 6's PR #27 head:

    L6=/path/to/checkout  # at 3ccb804
    PYTHONPATH=$L6/src .venv/bin/python research/experiments/HR009-l6-review/hr009.py e1 $L6 > .../e1.csv
    PYTHONPATH=$L6/src .venv/bin/python research/experiments/HR009-l6-review/hr009.py e2 $L6 > .../e2.csv
"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy import ndimage

L6 = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(L6 / "research/experiments/L6-field"))
L6007 = L6 / "research/experiments/L6-007-attractor-geography"
L6008 = L6 / "research/experiments/L6-008-pair-coupling"
from alm.lenia import growth, kernel  # noqa: E402
from field import Batch, Rule, centroids, summarize  # noqa: E402

DELTAS = (1e-14, 1e-12, 1e-10)
REPS = 8


def e1_job(args):
    """Step the circler seed and a list of perturbed copies; return death steps and separations."""
    tags, starts = args
    R, T, MU, SIGMA = 13, 10, 0.155, 0.020
    B = np.array(starts, dtype=np.float64)
    W, ny, nx = B.shape
    rule = Rule(R=R, T=T, mu=MU, sigma=SIGMA, kernel="poly", growth="poly")
    khat = np.fft.rfft2(kernel((ny, nx), rule))
    dt = 1.0 / T
    steps = 5000 * T
    death = [None] * W
    sep = []  # (step, |A_i - A_0| for each i)
    for t in range(1, steps + 1):
        U = np.fft.irfft2(np.fft.rfft2(B) * khat, s=(ny, nx))
        B = np.clip(B + growth("poly", U, MU, SIGMA) * dt, 0.0, 1.0)
        if t % 10 == 0:
            m = B.sum((1, 2)) / R**2
            for i in range(W):
                if death[i] is None and m[i] < 0.01:
                    death[i] = t
            sep.append((t, np.sqrt(((B - B[0]) ** 2).sum((1, 2)))))
    # death_step is the first 10-step sample with mass < 0.01 (resolution 10 steps)
    return tags, death, sep


def e1():
    sys.path.insert(0, str(L6007))  # both lanes name their runner run.py
    from run import cells, place
    base = place(cells("circler", 13), 128)
    support = ndimage.binary_dilation(base > 0, iterations=3)
    pert = []
    for i_d, d in enumerate(DELTAS):
        for k in range(REPS):
            xi = np.random.default_rng(9000 + 100 * i_d + k).uniform(-1, 1, base.shape)
            pert.append(((d, k), np.clip(base + d * xi * support, 0, 1)))
    groups = [pert[g::4] for g in range(4)]
    jobs = [([(0.0, -1)] + [m for m, _ in grp], [base] + [s for _, s in grp]) for grp in groups]
    with Pool(4) as p:
        res = p.map(e1_job, jobs)
    print("delta,rep,death_step,death_tu,growth_rate_per_tu,sep_at_500tu,sep_at_2000tu")
    seen_ref = False
    for tags, death, sep in res:
        ts = np.array([s for s, _ in sep])
        S = np.array([v for _, v in sep])
        for i, (d, k) in enumerate(tags):
            if d == 0.0:
                if seen_ref:
                    continue
                seen_ref = True
                rate = s500 = s2000 = float("nan")
            else:
                y = S[:, i]
                ok = (y > 0) & (y < 1e-3)
                if ok.sum() > 10:
                    # fit only the stretch after the first 50 tu (initial transient of the noise)
                    sel = ok & (ts > 500)
                    rate = np.polyfit(ts[sel] / 10, np.log(y[sel]), 1)[0] if sel.sum() > 10 else float("nan")
                else:
                    rate = float("nan")
                s500, s2000 = y[ts == 5000][0], y[ts == 20000][0]
            ds = death[i]
            print(f"{d:g},{k},{ds if ds else ''},{ds / 10 if ds else ''},{rate:.4g},{s500:.3g},{s2000:.3g}")


def e2():
    from disturb_helpers import disturb, offsets
    sys.path.insert(0, str(L6008))
    from run import MU, PHASES, R, SIGMA, T, WARM, HORIZON, WIN, N, units
    from alm import specimens
    S = specimens.load("S101")
    warm = Batch(R, T, [MU], [SIGMA]).run(S.place(N)[None], WARM + max(PHASES), snap_every=10**9,
                                         keep=tuple(WARM + p for p in PHASES))
    starts, meta = [], []
    for ph in PHASES:
        t = WARM + ph
        A = warm["states"][t][0]
        cx, cy = centroids(A[None])
        c = (cx[0], cy[0])
        v = warm["pos"][t, 0] - warm["pos"][t - 10, 0]
        h = v / np.hypot(*v)
        dx, dy = offsets(A.shape, *c)
        port = (dx * -h[1] + dy * h[0]) > 0
        for s in [round(0.1 * i, 1) for i in range(1, 11)]:
            G = disturb("I003", np.zeros_like(A), s, c, h, R)  # the pulse alone, clipped to [0, 1]
            for side, mask in (("port", port), ("starboard", ~port)):
                starts.append(np.clip(np.where(mask, A, 0.0) + G, 0, 1))
                meta.append((s, ph, side))
    outs = []
    for k in range(0, len(starts), 50):
        B = np.array(starts[k:k + 50])
        res = Batch(R, T, [MU] * len(B), [SIGMA] * len(B)).run(B, HORIZON, snap_every=50, snap_from=HORIZON - WIN)
        outs += [(d, res["final"][i]) for i, d in enumerate(summarize(res, R, T, WIN))]
    print("s,phase,side,n_full,mass_mean,speed,fate")
    for (s, ph, side), (d, F) in zip(meta, outs):
        print(f"{s},{ph},{side},{units(d, F)},{d['mass_mean']:.5g},{d['speed']:.4g},{d['fate']}")


if __name__ == "__main__":
    {"e1": e1, "e2": e2}[sys.argv[1]]()
