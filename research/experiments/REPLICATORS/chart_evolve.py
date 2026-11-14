"""G061: mean genome over time for every evolve.jsonl run, one panel per starting genome.
Coral = genome sets the rule (selected), grey = genome only a neutral marker. One y-axis (genome 0-1)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path(sys.argv[1])
runs = [json.loads(l) for l in open(Path(__file__).with_name("evolve.jsonl"))]
panels = [(0.1, 512, "start 0.1, 512² world"), (0.3, 256, "start 0.3, 256² world"), (0.7, 256, "start 0.7, 256² world")]
SEL, NEU, INK, MUTED, BG = "#e8735a", "#9a9a9a", "#e8e8ea", "#8a8a90", "#0b0b10"
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True, gridspec_kw=dict(width_ratios=[3, 1, 1]))
fig.patch.set_facecolor(BG)
for ax, (g0, N, title) in zip(axes, panels):
    ax.set_facecolor(BG)
    for r in runs:
        if r["g0"] != g0 or r["N"] != N:
            continue
        t = [x["t"] for x in r["trace"] if "gmean" in x]; g = [x["gmean"] for x in r["trace"] if "gmean" in x]
        ax.plot(t, g, color=NEU if r["neutral"] else SEL, lw=1.5, alpha=0.95)
    ax.axhline(g0, color=MUTED, lw=0.6, ls=":")
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    ax.set_ylim(0, 1); ax.set_xlabel("time units", color=MUTED)
    ax.tick_params(colors=MUTED, labelsize=9); ax.grid(axis="y", color="#2a2a30", lw=0.6)
    for sp in ax.spines.values():
        sp.set_visible(False)
axes[0].set_ylabel("mean genome (0 = 'well', 1 = 'uncontrolled')", color=MUTED)
axes[0].text(6000, 0.71, "genome sets the rule", color=INK, ha="right", fontsize=10)
axes[0].text(6000, 0.25, "genome only a marker", color=INK, ha="right", fontsize=10)
from matplotlib.lines import Line2D  # noqa: E402
fig.legend([Line2D([], [], color=SEL, lw=2), Line2D([], [], color=NEU, lw=2)], ["selected", "neutral marker"],
           loc="upper right", frameon=False, labelcolor=INK, ncol=2, fontsize=10)
plt.tight_layout(rect=(0, 0, 1, 0.93)); plt.savefig(out, dpi=120, facecolor=BG)
