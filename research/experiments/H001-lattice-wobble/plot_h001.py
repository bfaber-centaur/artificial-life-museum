#!/usr/bin/env python3
"""H001 evidence figure: (a) settled heading vs start rotation at R=13 and R=26;
(b) relative mass-wobble amplitude vs R. Reads the CSVs in this directory.

Usage (repo root): .venv/bin/python research/experiments/H001-lattice-wobble/plot_h001.py
"""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"


def rows(name):
    with open(os.path.join(HERE, name)) as f:
        return list(csv.DictReader(f))


fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1.6, 1]})
for ax in (a, b):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED)
    ax.grid(color="#e6e5e0", lw=0.6)

rot = list(range(46))
a.plot(rot, [68.2 - r for r in rot], ls="--", lw=1, color=MUTED, label="pure rotation (68.2° − rotation)")
for name, R, color, mk in (("x1_R13.csv", 13, BLUE, "o"), ("x2_R26_fine.csv", 26, ORANGE, "s")):
    d = rows(name)
    a.plot([int(r["rot"]) for r in d], [float(r["heading_w7"]) for r in d], mk, ms=5, color=color,
           mec="white", mew=0.8, label=f"R = {R}, heading over steps 7000–8000")
a.set_xlabel("start rotation (degrees)", color=INK)
a.set_ylabel("heading (degrees from +x)", color=INK)
a.set_title("(a) Heading snaps to lattice-preferred directions", loc="left", color=INK, fontsize=11)
a.legend(frameon=False, fontsize=8, labelcolor=INK)

e1 = rows("e1.csv")
Rs = [int(r["R"]) for r in e1]
sd = [float(r["rel_sd"]) for r in e1]
b.plot(Rs, sd, "-o", lw=2, ms=6, color=BLUE, mec="white", mew=0.8)
for R, s in zip(Rs, sd):
    b.annotate(f"{s:.1e}", (R, s), textcoords="offset points", xytext=(6, 4), fontsize=8, color=MUTED)
b.set_yscale("log")
b.set_xticks(Rs)
b.set_xlabel("kernel radius R (cells), same creature zoomed", color=INK)
b.set_ylabel("mass sd / mean, steps 1000–3000", color=INK)
b.set_title("(b) Mass wobble vanishes with resolution", loc="left", color=INK, fontsize=11)

fig.tight_layout()
fig.savefig(os.path.join(HERE, "h001.png"), dpi=130, facecolor="#fcfcfb")
