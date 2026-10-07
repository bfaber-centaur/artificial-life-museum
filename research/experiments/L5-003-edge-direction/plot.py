#!/usr/bin/env python3
"""L5-003 figure: the edge direction at lag 20 and the coordinate of every near-edge run.

    .venv/bin/python research/experiments/L5-003-edge-direction/plot.py
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
u = np.load(os.path.join(HERE, "directions.npz"))["u_all_k20"]
res = json.load(open(os.path.join(HERE, "results.json")))
cut = res["frozen"]["cut"]
rows = list(csv.DictReader(open(os.path.join(HERE, "coords.csv"))))

fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1.6]})
c = slice(40, 88)
lim = np.abs(u[c, c]).max()
im = ax[0].imshow(u[c, c], cmap="RdBu_r", vmin=-lim, vmax=lim, origin="upper")
ax[0].set_title("Edge direction u, lag 20 steps\nblue: dying run has less mass", fontsize=10)
ax[0].set_xticks([]); ax[0].set_yticks([])
fig.colorbar(im, ax=ax[0], fraction=0.046)

order = ["I001", "I002", "I003", "I004", "I005"]
for j, iv in enumerate(order):
    for r in rows:
        if r["intervention"] != iv or r["u_all_k20"] == "":
            continue
        x = float(r["u_all_k20"])
        if abs(x - cut) > 3:
            continue
        surv = r["label_survive"] == "1"
        ax[1].scatter(x, j + np.random.default_rng(hash(r["run_id"]) % 2**32).uniform(-0.25, 0.25),
                      marker="o" if surv else "x", c="tab:blue" if surv else "tab:red", s=18)
ax[1].axvline(cut, c="k", ls="--", lw=1)
ax[1].set_yticks(range(len(order)))
ax[1].set_yticklabels([o + (" (held out)" if o == "I005" else "") for o in order])
ax[1].set_xlabel("coordinate along u at lag 20 (relative to unperturbed control)")
ax[1].set_title("Runs within ±3 of the frozen cut: o survived, x died")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "edge-direction.png"), dpi=110)
