"""L6 reference check: behaviour signatures of catalogued creatures near the search box.

    python research/experiments/L6-field/catalog_neighbours.py

Every entry of the pinned upstream catalog (Chakazul/Lenia@adfc542
Python/animals.json, sha256-checked against alm.specimens.ANIMALS_SHA256) with a
single-shell kernel (b = 1) and mu in [0.09, 0.21], sigma in [0.006, 0.030] is
run under its own catalog rule (own R, T, kernel/growth families as upstream
executes them) for 500 time units on a torus ~10 R wide per creature size, and
summarised with the same measures as the sweeps. Writes catalog-neighbours.csv.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from field import Batch, summarize  # noqa: E402

from alm import rle, specimens  # noqa: E402

raw = specimens.ANIMALS_JSON.read_bytes()
import hashlib  # noqa: E402
assert hashlib.sha256(raw).hexdigest() == specimens.ANIMALS_SHA256, "animals.json is not the pinned file"
entries = json.loads(raw)
rows = []
seen = set()
for e in entries:
    p = e.get("params")
    if not p or str(p.get("b")) != "1":
        continue
    if not (0.09 <= p["m"] <= 0.21 and 0.006 <= p["s"] <= 0.030):
        continue
    key = (e["code"], p["R"], p["T"], p["m"], p["s"])
    if key in seen:
        continue
    seen.add(key)
    # Built directly (not via from_catalog): some codes, e.g. O2v, appear twice.
    cells = rle.decode(e["cells"])
    R = int(p["R"])
    N = int(max(128 * R / 13, 2 * max(cells.shape) + 2 * R))
    N += N % 2
    A0 = np.zeros((N, N))
    h, w = cells.shape
    A0[(N - h) // 2 : (N - h) // 2 + h, (N - w) // 2 : (N - w) // 2 + w] = cells / 255.0
    kn = specimens._CATALOG_KERNEL[p.get("kn", 1)]
    gn = specimens._CATALOG_GROWTH[p.get("gn", 1)]
    T = float(p["T"])
    steps = int(round(500 * T)) if T <= 40 else int(round(100 * T))
    window = steps // 5
    b = Batch(R=R, T=T, mu=[p["m"]], sigma=[p["s"]], kernel_name=kn, growth_name=gn)
    res = b.run(A0[None], steps, snap_every=max(1, int(T * 5)), snap_from=steps - window)
    d = summarize(res, R, T, window)[0]
    rows.append({"code": e["code"], "name": e.get("name", ""), "R": R, "T": T, "mu": p["m"], "sigma": p["s"],
                 "kernel": kn, "growth": gn, "N": N, **d})
    print(e["code"], e.get("name"), d["fate"], round(d["mass_mean"], 4), round(d["speed"], 4), flush=True)
with open(HERE / "catalog-neighbours.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
