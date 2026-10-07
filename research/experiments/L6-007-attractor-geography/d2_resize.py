"""D2 check (exploratory, added after pre-registration; see protocol Amendments).

Lane 3 (C047, PR #18 s102_resize_check.py) found that S102 at its registered rule
(mu 0.155, sigma 0.020, T 10) survives at R 26 and 39 from block, nearest and cubic
seeds and dies only from the bilinear seed, in alm_check. This reruns the same
eight seeds in Lane 6's engine (field.py, alm.lenia semantics): S102 cells
resized by R/13 with np.kron (block) or scipy.ndimage.zoom order 0/1/3, clipped
to [0, 1], centred on a 128*(R/13) torus, 1000 tu.

    python research/experiments/L6-007-attractor-geography/d2_resize.py
"""
import csv
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "L6-field"))
from field import Batch, summarize  # noqa: E402
from tables import phenotype  # noqa: E402

from alm import specimens  # noqa: E402

c0 = specimens.load("S102").cells / 255.0
rows = []
for R in (26, 39):
    k = R // 13
    N = 128 * k
    starts, names = [], []
    for method in ("block", "nearest", "bilinear", "cubic"):
        if method == "block":
            c = np.kron(c0, np.ones((k, k)))
        else:
            c = np.clip(ndimage.zoom(c0, R / 13, order={"nearest": 0, "bilinear": 1, "cubic": 3}[method]), 0, 1)
        A = np.zeros((N, N))
        h, w = c.shape
        A[(N - h) // 2 : (N - h) // 2 + h, (N - w) // 2 : (N - w) // 2 + w] = c
        starts.append(A)
        names.append(method)
    res = Batch(R, 10, [0.155] * 4, [0.020] * 4).run(np.array(starts), 10000, snap_every=50, snap_from=9000)
    for m, d, mass in zip(names, summarize(res, R, 10, 1000), res["mass"].T):
        dead = np.flatnonzero(mass < 0.01)
        cls = d["fate"].upper() if d["fate"] != "localized" else phenotype({k_: str(v) for k_, v in d.items()})
        rows.append({"R": R, "method": m, "class_1000tu": cls,
                     "died_at_tu": dead[0] / 10 if len(dead) else "", "mass_last100": round(d["mass_mean"], 4),
                     "path_speed": round(d["path_speed"], 4), "net_speed": round(d["speed"], 4)})
        print(rows[-1], flush=True)
with open(HERE / "d2-resize.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
