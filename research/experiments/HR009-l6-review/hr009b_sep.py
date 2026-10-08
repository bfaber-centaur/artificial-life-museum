#!/usr/bin/env python3
"""HR-009b (exploratory, NOT preregistered): is S102 still chaotic where Lane 3 (PR #29) sees no deaths?

Twin runs differing by 1e-12 on the dilated support, as in HR-009 E1, at the coexistence rule
(mu 0.155, sigma 0.020 held fixed). Settings: R13 T10 (reference), R26 T10 (block seed, as in
L3-003 Q6-26), R13 T20, R13 T40. Records |A_d - A_0| every tu for 600 tu, prints the growth rate
(log-linear fit over 50 tu .. first time above 1e-3).

    .venv/bin/python research/experiments/HR009-l6-review/hr009b_sep.py > .../hr009b_sep.csv
    .venv/bin/python research/experiments/HR009-l6-review/hr009b_sep.py 26x10 3000 4 > .../hr009b_sep_R26_long.csv
(optional argv: comma-separated RxT settings, horizon in tu, replicates.)
"""
import sys
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

from alm import specimens
from alm.lenia import Lenia, Rule

ARGS = sys.argv[1:]
SETTINGS = [tuple(map(int, s.split("x"))) for s in (ARGS[0] if ARGS else "13x10,26x10,13x20,13x40").split(",")]
REPS = int(ARGS[2]) if len(ARGS) > 2 else 3
HORIZON = int(ARGS[1]) if len(ARGS) > 1 else 600


def job(args):
    R, T, k = args
    cells = specimens.load("S102").cells / 255.0
    if R != 13:
        cells = np.kron(cells, np.ones((R // 13, R // 13)))
    N = 128 * R // 13
    base = np.zeros((N, N))
    h, w = cells.shape
    base[(N - h) // 2:(N - h) // 2 + h, (N - w) // 2:(N - w) // 2 + w] = cells
    support = ndimage.binary_dilation(base > 0, iterations=3 * R // 13)
    xi = np.random.default_rng(9500 + 10 * R + T + k).uniform(-1, 1, base.shape)
    rule = Rule(R=R, T=T, mu=0.155, sigma=0.020, kernel="poly", growth="poly")
    a, b = Lenia(rule, base), Lenia(rule, np.clip(base + 1e-12 * xi * support, 0, 1))
    sep = []
    for t in range(1, HORIZON * T + 1):
        a.step()
        b.step()
        if t % T == 0:
            sep.append(np.sqrt(((a.A - b.A) ** 2).sum()) / R)  # per R so grids compare
    sep = np.array(sep)
    tu = np.arange(1, HORIZON + 1)
    above = np.flatnonzero(sep > 1e-3)
    end = above[0] if len(above) else len(sep)
    sel = (tu >= 50) & (np.arange(len(sep)) < end) & (sep > 0)
    rate = np.polyfit(tu[sel], np.log(sep[sel]), 1)[0] if sel.sum() > 10 else float("nan")
    alive = a.A.sum() / R**2 > 0.01 and b.A.sum() / R**2 > 0.01
    return R, T, k, rate, sep[99], sep[299], sep[599], sep[-1], int(alive)


if __name__ == "__main__":
    with Pool(4) as p:
        res = p.map(job, [(R, T, k) for R, T in SETTINGS for k in range(REPS)])
    print(f"R,T,rep,growth_rate_per_tu,sep_100tu,sep_300tu,sep_600tu,sep_{HORIZON}tu,both_alive_{HORIZON}tu")
    for r in res:
        print("%d,%d,%d,%.4g,%.3g,%.3g,%.3g,%.3g,%d" % r)
