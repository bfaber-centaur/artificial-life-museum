"""Exploratory (not preregistered): does S001 survive at very small timesteps (T >= 500)?

Kojima reports Orbium vanishing at dt = 0.002 (T = 500); Chan runs it to T = 2560.
Runs S001 (catalog cells, R 13, 128^2) for 300 time units at T = 640, 1280, 2560.

    .venv/bin/python research/experiments/L3-002-property-persistence/s001_small_dt.py
"""

from multiprocessing import Pool

import numpy as np

from alm_check.lenia import Rule, World, load_orbium, periodic_centroid, place

HORIZON = 300


def go(T):
    w = World(place(load_orbium(), 128), Rule(T=T))
    n, prev, disp, mass = 128, periodic_centroid(w.A), np.zeros(2), []
    for s in range(1, HORIZON * T + 1):
        w.step()
        if s % T == 0:
            m = w.A.sum() / 169
            mass.append(m)
            if m < 0.01:
                return T, f"died at t = {s // T}"
            c = periodic_centroid(w.A)
            if s // T > 100:
                disp += [(c[i] - prev[i] + n / 2) % n - n / 2 for i in (0, 1)]
            prev = c
    sp = np.hypot(*disp) / (HORIZON - 100) / 13
    return T, f"alive at t = {HORIZON}; mass {np.mean(mass[100:]):.4f}, speed {sp:.4f} R/tu"


if __name__ == "__main__":
    with Pool(3) as p:
        for r in p.map(go, [640, 1280, 2560]):
            print(r)
