"""L6-010 runner (protocol.md in this directory; fixed before any run).

    python research/experiments/L6-010-orbium-ring-boundary/run.py
"""
import csv
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "L6-007-attractor-geography"))
from run import cells, place, run_batch, same_up_to_shift  # noqa: E402  (L6-007)

R, T, SIGMA, N, HORIZON, CPS = 13, 10, 0.020, 128, 1000, (250, 500, 1000)


def main():
    orb, ring = place(cells("orbium", R), N), place(cells("ring", R), N)
    fine = [round(x, 3) for x in np.arange(0.100, 0.2505, 0.001)] + \
           [round(x, 3) for x in np.arange(0.500, 0.6005, 0.001)]
    coarse = [round(x, 3) for x in np.arange(0.100, 0.2505, 0.005)] + \
             [round(x, 3) for x in np.arange(0.500, 0.6005, 0.005)]
    starts, meta = [], []
    for i, lam in enumerate(fine):
        A = (1 - lam) * orb + lam * ring
        starts.append(A)
        meta.append(("fine", lam))
    for i, lam in enumerate(fine):
        A = (1 - lam) * orb + lam * ring
        sup = ndimage.binary_dilation(A > 0, iterations=3)
        xi = np.random.default_rng(10000 + i).uniform(-1, 1, A.shape)
        starts.append(np.clip(A + 1e-12 * xi * sup, 0, 1))
        meta.append(("twin", lam))
    for i, lam in enumerate(coarse):
        A = (1 - lam) * orb + lam * ring
        sup = ndimage.binary_dilation(A > 0, iterations=3)
        xi = np.random.default_rng(20000 + i).uniform(-1, 1, A.shape)
        starts.append(np.clip(A + 0.01 * xi * sup, 0, 1))
        meta.append(("noisy", lam))
    t0 = time.time()
    res = run_batch(starts, R, T, SIGMA, HORIZON, CPS, chunk=40, tag="l6010")
    rows = []
    for (sl, lam), (cls, d, F) in zip(meta, res):
        rows.append({"slice": sl, "lambda": lam, **{f"class_{c}tu": x for c, x in zip(CPS, cls)},
                     "mass": round(float(d["mass_mean"]), 5),
                     "is_S103": bool(cls[-1] == "STATIC" and same_up_to_shift(ring, F))})
    with open(HERE / "scan.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    np.savez_compressed(HERE / "finals.npz", final=np.array([r[2] for r in res], dtype=np.float32))
    print("wrote scan.csv", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
