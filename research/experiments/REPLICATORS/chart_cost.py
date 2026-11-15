"""G069: adaptive vs constant dosing with and without a cost of resistance (therapy_long.jsonl).

Low dose (kappa 0.3), 6000 tu, four seeds per line colour; rows are the crowding cost
(therapy.crowding_cost) 0, 0.1 and 0.3.

  python chart_cost.py OUT.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = [json.loads(l) for l in open(Path(__file__).with_name("therapy_long.jsonl"))]
costs = sorted({r.get("cost", 0.0) for r in R})
col = {"none": "#9a9a9a", "constant": "#E69F00", "adaptive": "#0072B2"}
name = {0.0: "no cost of resistance", 0.1: "cost 0.1", 0.3: "cost 0.3"}
plt.rcParams.update({"font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(len(costs), 2, figsize=(12.5, 8.4), sharex=True)
for i, c in enumerate(costs):
    for arm in ("none", "constant", "adaptive"):
        for r in R:
            if r.get("cost", 0.0) != c or r["arm"] != arm:
                continue
            T = np.array(r["trace"])
            lab = arm if (i == 0 and r["seed"] == 0) else None
            ax[i, 0].plot(T[:, 0], T[:, 1], color=col[arm], lw=1.0, alpha=0.85, label=lab)
            ax[i, 1].plot(T[:, 0], np.where(T[:, 1] > 0, T[:, 3], np.nan), color=col[arm], lw=1.0, alpha=0.85)
    ax[i, 0].set_ylim(0, 2.8)
    ax[i, 1].set_ylim(-0.03, 1.03)
    ax[i, 0].axhline(1.25, color="#555", ls=":", lw=0.9)
    ax[i, 0].set_title(name.get(c, f"cost {c}"), loc="left", fontsize=11)
    ax[i, 0].set_ylabel("burden (× start)")
    ax[i, 1].set_ylabel("resistant share")
ax[0, 0].text(6000, 1.08, "progression", ha="right", fontsize=8.5, color="#555")
for a in ax[-1]:
    a.set_xlabel("time since treatment began (tu)")
fig.legend(*ax[0, 0].get_legend_handles_labels(), frameon=False, fontsize=10, loc="upper right", ncol=3)
fig.suptitle("Drug strength κ 0.3, four seeds per colour. Resistant = genome below 0.4; lines end where a tumour dies out.",
             x=0.01, ha="left", fontsize=10, color="#555")
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=110)
