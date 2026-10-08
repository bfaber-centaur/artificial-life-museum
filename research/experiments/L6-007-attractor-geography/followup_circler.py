"""L6-007 exploratory follow-up (added after Part A, NOT preregistered).

Part A showed perturbed circlers that were CIRCLER at 500 tu and DIED by 1000 or 2000 tu. This
reruns the unperturbed circler and every eps 0.01 and 0.03 start for 5000 tu at the primary
rule, records the first step with mass < 0.01, and writes circler-lifetimes.csv.

    python research/experiments/L6-007-attractor-geography/followup_circler.py
"""
import csv

import numpy as np
from scipy import ndimage

from run import HERE, MU, REPS, Batch, cells, place

R, T, SIGMA, N, HORIZON = 13, 10, 0.020, 128, 5000
I_S = 1  # SEEDS order: orbium, circler, ring


def main():
    base = place(cells("circler", R), N)
    support = ndimage.binary_dilation(base > 0, iterations=3)
    starts, meta = [base], [(0.0, -1)]
    for i_e, e in enumerate((0.01, 0.03)):
        for k in range(REPS):
            xi = np.random.default_rng(1000 * I_S + 100 * i_e + k).uniform(-1, 1, base.shape)
            starts.append(np.clip(base + e * xi * support, 0, 1))
            meta.append((e, k))
    b = Batch(R=R, T=T, mu=[MU] * len(starts), sigma=[SIGMA] * len(starts))
    res = b.run(np.array(starts), HORIZON * T, snap_every=10**9, snap_from=10**9)
    m = np.asarray(res["mass"])  # (steps+1, worlds), normalised by R^2
    rows = []
    for i, (e, k) in enumerate(meta):
        dead = np.flatnonzero(m[:, i] < 0.01)
        rows.append({"eps": e, "rep": k, "death_tu": dead[0] / T if len(dead) else "",
                     "mass_last_100tu": float(m[-100 * T:, i].mean())})
        print(rows[-1], flush=True)
    with open(HERE / "circler-lifetimes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
