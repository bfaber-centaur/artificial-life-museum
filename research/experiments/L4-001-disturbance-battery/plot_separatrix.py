#!/usr/bin/env python3
"""Exploratory: mass traces either side of the I001 threshold (t0 = 1000), and the
log-scaling of collapse time. Writes results/separatrix-I001-t1000.png and
states/edge-I001-t1000.npz (the lingering state just above threshold)."""
import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402
from alm import disturb  # noqa: E402

rows = list(csv.DictReader(open(os.path.join(HERE, "results", "separatrix-I001-t1000.csv"))))
s_star_hi = min(float(r["strength"]) for r in rows if r["died"] == "1")
s_star_lo = max(float(r["strength"]) for r in rows if r["died"] == "0")
s_star = (s_star_hi + s_star_lo) / 2

step = run.engine("ref", 128, run.R, run.T)
A0, prev = run.warm("ref", 128, 1000)
fr = disturb.frame_from(A0, prev)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
cmap = plt.get_cmap("coolwarm")
offs = [1e-3, 1e-5, 1e-7, 1e-9, 1e-11]
snap = None
for i, d in enumerate(offs):
    for sign in (+1, -1):
        s = s_star + sign * d
        A = disturb.i001_attenuate(A0, fr, s, run.R)
        ms = []
        for k in range(400):
            A = step(A)
            ms.append(A.sum() / run.R ** 2)
            if sign > 0 and d == 1e-11 and k == 130:
                snap = A.copy()
        a1.plot(ms, color=cmap(0.5 + 0.5 * sign * (1 - i / len(offs))), lw=1,
                label=f"s*{'+' if sign > 0 else '−'}{d:.0e}")
a1.set_xlabel("steps after intervention")
a1.set_ylabel("mass ΣA/R²")
a1.set_title(f"I001 at t0=1000, s* = {s_star:.11f}", fontsize=9)
a1.legend(fontsize=6, ncol=2)
died = [(float(r["strength"]) - s_star, int(r["death_step"])) for r in rows if r["died"] == "1"]
x = np.array([d for d, _ in died])
y = np.array([k for _, k in died])
ok = x > 0
fit = np.polyfit(np.log(x[ok]), y[ok], 1)
a2.semilogx(x[ok], y[ok], "o", ms=4)
xx = np.logspace(np.log10(x[ok].min()), np.log10(x[ok].max()), 50)
a2.semilogx(xx, np.polyval(fit, np.log(xx)), "k--", lw=0.8,
            label=f"death step ≈ {fit[1]:.0f} {fit[0]:+.2f}·ln(s−s*)")
a2.set_xlabel("s − s*")
a2.set_ylabel("step at which mass < 0.01")
a2.legend(fontsize=7)
fig.savefig(os.path.join(HERE, "results", "separatrix-I001-t1000.png"), dpi=110)
os.makedirs(os.path.join(HERE, "states"), exist_ok=True)
np.savez_compressed(os.path.join(HERE, "states", "edge-I001-t1000.npz"), state=snap,
                    s=s_star + 1e-11, step_after_t0=131)
print("s*", s_star, "fit slope (steps per e-fold)", -fit[0], "-> unstable rate per time unit",
      run.T / -fit[0])
