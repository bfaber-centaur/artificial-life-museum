"""Figure for L3-002: each property's deviation from its Δt → 0 limit, and from R = 39."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1] / "traces" / "lane3" / "L3-002" / "labels.csv"
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
NAMES = {"mass": "mass", "gyradius": "gyradius", "net_speed": "speed", "turning_rate": "turning rate",
         "path_speed": "path speed"}

rows = [r for r in csv.DictReader(open(LAB)) if r["property"] in NAMES]
specs = ["S001", "S101", "S102", "S103"]
fig, axs = plt.subplots(1, 4, figsize=(13, 3.6), dpi=130, sharey=True)
for ax, sp in zip(axs, specs):
    i = 0
    for r in rows:
        if r["specimen"] != sp:
            continue
        lim = float(r["x_inf_T"])
        dts = [1 / 10, 1 / 20, 1 / 40, 1 / 80]
        ys = [100 * (float(r[k]) / lim - 1) for k in ("B", "T20", "T40", "T80")]
        c = COLORS[i % 4]
        ax.plot(dts, ys, "-o", color=c, lw=2, ms=4, label=NAMES[r["property"]])
        ax.plot([0.1], [100 * (float(r["R39"]) / lim - 1)], "D", mfc="none", mec=c, ms=7)
        i += 1
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_title(sp, loc="left", fontsize=10, color=INK)
    ax.set_xlabel("Δt = 1/T (R = 13)", fontsize=9, color=MUTED)
    ax.grid(color=GRID, lw=0.6)
    ax.tick_params(colors=MUTED, labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
axs[0].set_ylabel("% from Δt → 0 limit", fontsize=9, color=MUTED)
fig.text(0.5, -0.02, "Filled: timestep ladder at R = 13. Hollow diamond: R = 39, T = 10 (sits on the T = 10 point "
         "when the property is resolution-converged).", ha="center", fontsize=8, color=MUTED)
fig.tight_layout()
fig.savefig(HERE / "persistence.png", bbox_inches="tight")
print("wrote", HERE / "persistence.png")
