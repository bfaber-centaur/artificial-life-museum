"""S103 block-replicated to R26 (np.kron 2x2, N256 -> N512): is it still an exact fixed point?

C048 says the block seed "settles static at mass 0.380599"; whether that body is an exact
fixed point was not tested. This matters for the §9 R26 check, whose S-alone control
starts from exactly this kind of state.

    python research/experiments/REEF-numerics/s103/s103_r26_block.py   # writes s103_r26_block.csv/.json
"""
import csv, hashlib, json
from pathlib import Path
import numpy as np
from alm.lenia import Lenia, Rule
from alm.measure import periodic_centroid
from alm.specimens import load

HERE = Path(__file__).resolve().parent
sha = lambda A: hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()
A0 = np.kron(load("S103").place(256), np.ones((2, 2)))
w = Lenia(Rule(R=26, T=10, mu=.155, sigma=.020), A0)
G = w.growth_field()
full, empty = A0 == 1, A0 == 0
info = {"initial_sha256": sha(A0), "min_G_full": float(G[full].min()), "max_G_empty": float(G[empty].max()),
        "full_cells_G_lt_0": int((G[full] < 0).sum()), "empty_cells_G_gt_0": int((G[empty] > 0).sum())}
rows, prev = [], A0.copy()
c0 = np.array(periodic_centroid(A0))
for tu in range(1, 301):
    for _ in range(10):
        w.step()
    c = np.array(periodic_centroid(w.A))
    rows.append({"tu": tu, "mass_R2": w.A.sum() / 26**2, "max_abs_dA_per_tu": float(np.abs(w.A - prev).max()),
                 "support_cells_gt_0.01": int((w.A > 0.01).sum()), "centroid_shift_cells": float(np.hypot(*(c - c0)))})
    prev = w.A.copy()
info.update(final_sha256=sha(w.A), bitwise_fixed_by_300tu=bool(rows[-1]["max_abs_dA_per_tu"] == 0),
            mass_R2_tu200_300=[min(r["mass_R2"] for r in rows[199:]), max(r["mass_R2"] for r in rows[199:])],
            max_abs_dA_per_tu_tu200_300=[min(r["max_abs_dA_per_tu"] for r in rows[199:]), max(r["max_abs_dA_per_tu"] for r in rows[199:])],
            max_centroid_shift_cells=max(r["centroid_shift_cells"] for r in rows))
with open(HERE / "s103_r26_block.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
(HERE / "s103_r26_block.json").write_text(json.dumps(info, indent=1) + "\n")
print(json.dumps(info, indent=1))
