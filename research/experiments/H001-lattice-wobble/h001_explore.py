#!/usr/bin/env python3
"""H001 exploratory follow-up (NOT preregistered): is S001's heading pinned by the lattice?

In the preregistered heading sweep (e2.csv), 16 initial rotations collapsed onto a handful of
headings (6° and 9° gave identical velocities to 4 digits). In an isotropic continuum the heading
is a neutral direction, so a rotated start should give a rotated heading. This script measures
heading in 1000-step windows over a long run for a fine grid of start rotations, at two
resolutions.

Usage (repo root):
    .venv/bin/python research/experiments/H001-lattice-wobble/h001_explore.py 13 1 > .../x1_R13.csv
    .venv/bin/python research/experiments/H001-lattice-wobble/h001_explore.py 26 3 > .../x1_R26.csv
    .venv/bin/python research/experiments/H001-lattice-wobble/h001_explore.py 26 1 > .../x2_R26_fine.csv
(argv: R, rotation step in degrees; rotations 0..45.)
"""
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h001  # noqa: E402

STEPS, WIN = 8000, 1000


def headings(args):
    R, rot = args
    N = h001.grid_size(R)
    A = h001.initial_state(R, rot, N)
    kfft, _ = h001.rc.make_kernel_fft(N, R, [1.0], "poly")
    cs = []
    for t in range(STEPS):
        A, _ = h001.rc.step(A, kfft, h001.MU, h001.SIGMA, h001.T, "poly")
        cs.append(h001.centroid(A, N))
    cs = np.array(cs)
    d = np.diff(np.unwrap(cs * 2 * np.pi / N, axis=0), axis=0) * N / (2 * np.pi)
    out = []
    for w in range(STEPS // WIN):
        vx, vy = d[w * WIN:(w + 1) * WIN - 1].mean(0)
        out.append((np.degrees(np.arctan2(vy, vx)), np.hypot(vx, vy) / R * h001.T))
    return R, rot, int(A.sum() > 1), out


if __name__ == "__main__":
    R = int(sys.argv[1])
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    rots = list(range(0, 46, step))
    with Pool() as p:
        res = p.map(headings, [(R, r) for r in rots])
    wins = [f"w{w}" for w in range(STEPS // WIN)]
    print("R,rot,alive," + ",".join(f"heading_{w}" for w in wins) + ",speed_R_per_time_last")
    for R, rot, alive, out in res:
        print(f"{R},{rot},{alive}," + ",".join(f"{h:.3f}" for h, _ in out) + f",{out[-1][1]:.5f}")
