#!/usr/bin/env python3
"""HR-005 check (exploratory): are S001's feature means heading-invariant? (attacks Lane 5, PR #4)

Lane 5 tested start rotations 0, 23, 45 deg, which land on the 68.2/40.4/21.8 deg pinned headings.
Lane 3 (PR #8) found an axis-locked plateau near 0 deg at larger start rotations. This runs
6000 steps per start rotation and reports, over steps 2000-5999: heading, speed (R/time), mean
mass (sum A / R^2), mean gyradius (R), mean anisotropy 1 - lmin/lmax, and mass sd/mean.

Usage (repo root):
    .venv/bin/python research/experiments/H001-lattice-wobble/heading_means.py 13 0 27 55 70
    .venv/bin/python research/experiments/H001-lattice-wobble/heading_means.py 26 0 67
"""
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h001  # noqa: E402


def measure(args):
    R, rot = args
    N = h001.grid_size(R)
    A = h001.initial_state(R, rot, N)
    kfft, _ = h001.rc.make_kernel_fft(N, R, [1.0], "poly")
    i = np.arange(N)
    ms, gs, an, cs = [], [], [], []
    for t in range(6000):
        A, _ = h001.rc.step(A, kfft, h001.MU, h001.SIGMA, h001.T, "poly")
        c = h001.centroid(A, N)
        cs.append(c)
        if t >= 2000:
            m = A.sum()
            dx = (i[None, :] - c[0] + N / 2) % N - N / 2
            dy = (i[:, None] - c[1] + N / 2) % N - N / 2
            cx, cy = c[0] + (A * dx).sum() / m, c[1] + (A * dy).sum() / m  # bias-corrected
            dx = (i[None, :] - cx + N / 2) % N - N / 2
            dy = (i[:, None] - cy + N / 2) % N - N / 2
            xx, yy, xy = (A * dx * dx).sum() / m, (A * dy * dy).sum() / m, (A * dx * dy).sum() / m
            w = np.linalg.eigvalsh([[xx, xy], [xy, yy]])
            ms.append(m / R ** 2)
            gs.append(np.sqrt(xx + yy) / R)
            an.append(1 - w[0] / w[1])
    vx, vy = h001.velocity(np.array(cs[2000:]), N)
    return (R, rot, np.degrees(np.arctan2(vy, vx)), np.hypot(vx, vy) / R * h001.T,
            np.mean(ms), np.mean(gs), np.mean(an), np.std(ms) / np.mean(ms))


if __name__ == "__main__":
    R = int(sys.argv[1])
    rots = [float(x) for x in sys.argv[2:]]
    with Pool() as p:
        res = p.map(measure, [(R, r) for r in rots])
    print("R,rot,heading,speed_R_per_time,mass,gyradius,anisotropy,mass_rel_sd")
    for r in res:
        print("%d,%g,%.3f,%.5f,%.5f,%.5f,%.4f,%.3g" % r)
