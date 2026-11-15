"""G066: a mutant against the neutral marker at the same place (C116-C118).

  python neutral_plot.py OUT.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).parent
rep = {(r["mutant"], r["placement"]): r for r in map(json.loads, open(HERE / "replay.jsonl"))}
neu = {(r["place_of_mutant"], r["placement"]): r for r in map(json.loads, open(HERE / "neutral.jsonl"))}
keys = sorted(rep)
rm = np.array([rep[k]["mutant_mass"][-1] / rep[k]["mutant_mass"][0] for k in keys])
rn = np.array([neu[k]["marker_mass"][-1] / neu[k]["marker_mass"][0] for k in keys])
FLOOR = 1e-3
Lm, Ln = np.log10(np.maximum(rm, FLOOR)), np.log10(np.maximum(rn, FLOOR))
gen = np.array([k[0] for k in keys])

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw=dict(width_ratios=[1, 1.25]))
a.axhline(0, color="#bbb", lw=0.8); a.axvline(0, color="#bbb", lw=0.8)
a.plot([-3.2, 1], [-3.2, 1], color="#888", ls=":", lw=1)
hi = np.isin(gen, [4, 8])
a.scatter(Ln[~hi], Lm[~hi], s=26, color="#9a9a9a", alpha=0.8, label="other mutants")
a.scatter(Ln[gen == 4], Lm[gen == 4], s=46, color="#D55E00", label="mutant 4")
a.scatter(Ln[gen == 8], Lm[gen == 8], s=46, color="#0072B2", label="mutant 8")
ticks = [-3, -2, -1, 0, 1]
a.set_xticks(ticks, ["≤×0.001", "×0.01", "×0.1", "×1", "×10"])
a.set_yticks(ticks, ["≤×0.001", "×0.01", "×0.1", "×1", "×10"])
a.set_xlabel("neutral marker at this place (growth over 500 tu)")
a.set_ylabel("mutant at the same place")
a.set_title("Same place, two patches (72 places)", loc="left", fontsize=11.5)
a.legend(frameon=False, loc="lower right", fontsize=9)
a.text(-3.1, 0.75, "above the dotted line:\nmutant beat neutral", fontsize=9, color="#555")

D = (Lm - Ln).reshape(12, 6)
order = np.argsort(np.median(D, 1))[::-1]
for i, k in enumerate(order):
    c = "#D55E00" if k == 4 else "#0072B2" if k == 8 else "#555"
    b.scatter(np.full(6, i) + np.linspace(-0.18, 0.18, 6), D[k], s=20, color=c, alpha=0.85)
    b.plot([i - 0.3, i + 0.3], [np.median(D[k])] * 2, color=c, lw=2)
    grew = int((rm.reshape(12, 6)[k] > 1).sum())
    b.text(i, -3.55, f"{grew}/6", ha="center", fontsize=8.5, color=c)
b.axhline(0, color="#bbb", lw=0.8)
b.set_xticks(range(12), [str(k) for k in order])
b.set_xlabel("mutant genome, sorted by median advantage\n(small numbers: replays it grew in, judged without the baseline)")
b.set_ylabel("advantage over neutral (log10 ratio)")
b.set_ylim(-3.8, 3.4)
b.set_title("Fitness measured against luck", loc="left", fontsize=11.5)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=110)
