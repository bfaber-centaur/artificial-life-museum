"""G068: every therapy run (therapy.jsonl): burden and resistant share over time, by dose.

  python chart_therapy.py OUT.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = [json.loads(l) for l in open(Path(__file__).with_name("therapy.jsonl"))]
ks = sorted({r["kappa"] for r in R if r["kappa"] is not None})
col = {"none": "#9a9a9a", "constant": "#E69F00", "adaptive": "#0072B2"}
plt.rcParams.update({"font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, len(ks), figsize=(13.5, 6.2), sharex=True, sharey="row")
for j, k in enumerate(ks):
    for arm in ("none", "constant", "adaptive"):
        for r in R:
            if r["arm"] != arm or (arm != "none" and r["kappa"] != k):
                continue
            T = np.array(r["trace"])
            ax[0, j].plot(T[:, 0], T[:, 1], color=col[arm], lw=1.1, alpha=0.85,
                          label=arm if r["seed"] == 0 else None)
            if arm != "none":
                share = np.where(T[:, 1] > 0, T[:, 3], np.nan)
                ax[1, j].plot(T[:, 0], share, color=col[arm], lw=1.1, alpha=0.85)
            else:
                ax[1, j].plot(T[:, 0], T[:, 3], color=col[arm], lw=1.1, alpha=0.85)
    ax[0, j].set_ylim(0, 2.8)
    ax[0, j].axhline(1.25, color="#555", ls=":", lw=0.9)
    ax[0, j].axhline(0.5, color="#bbb", ls=":", lw=0.8)
    ax[0, j].set_title(f"drug strength κ = {k}", loc="left", fontsize=11)
    ax[1, j].set_xlabel("time since treatment began (tu)")
ax[0, 0].set_ylabel("tumour burden (× start)")
ax[1, 0].set_ylabel("share that is resistant\n(genome < 0.4)")
fig.legend(*ax[0, 0].get_legend_handles_labels(), frameon=False, fontsize=10, loc="upper right", ncol=3)
ax[0, 0].text(30, 1.32, "progression", fontsize=8.5, color="#555")
fig.suptitle("Four seeds per line colour. Lines that drop to zero: tumour eradicated.", x=0.01, ha="left", fontsize=10, color="#555")
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=110)
