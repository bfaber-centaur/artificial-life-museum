"""Figure for L3-003: S102 survival curves and mass traces. Reads research/traces/lane3/L3-003/.

    .venv/bin/python research/experiments/L3-003-circler-lifetime/plot.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
TR = HERE.parents[2] / "research" / "traces" / "lane3" / "L3-003"
rows = [r for f in ("lifetimes.csv", "q6.csv", "q7.csv") for r in csv.DictReader(open(TR / f))]


def ends(cond):
    """(end time, died) per run; a run that left the circler state by filling the world counts as
    ended at the first tu with mass > 2."""
    out = []
    for r in rows:
        if r["condition"] != cond:
            continue
        if r["death_tu"]:
            out.append((float(r["death_tu"]), True))
            continue
        rid = r["run_id"].removeprefix("L3-003-")
        m = np.load(TR / f"{rid}.npz")["mass"]
        big = np.flatnonzero(m > 2)
        out.append(((big[0] + 1.0), True) if len(big) else (float(r["steps_run"]) / int(r["T"]), False))
    return out


fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.5))
groups = [("Q6-13", "R13 T10, δ=1e-12 copies (n=24)", "C3"),
          ("A1", "R13 T10, Lane 6 noise ε 0.01/0.03 (n=12)", "C1"),
          ("Q6-26", "R26 T10, δ=1e-12 copies (n=12)", "C0"),
          ("E26", "R26 T10, ε 0.01/0.03 noise (n=12)", "C9"),
          ("Q7-T20", "R13 T20, δ=1e-12 copies (n=24)", "C4"),
          ("Q7-T40", "R13 T40, δ=1e-12 copies (n=24)", "C6")]
for cond, lab, col in groups:
    e = ends(cond)
    t = np.linspace(0, 8000, 801)
    s = [np.mean([not (d and te <= x) for te, d in e]) for x in t]
    hz = max(te for te, d in e if not d) if any(not d for _, d in e) else 8000
    keep = t <= hz
    a.step(t[keep], np.array(s)[keep], where="post", color=col, label=lab)
    a.plot([hz], [s[np.flatnonzero(keep)[-1]]], "|", color=col, ms=12)
a.set_xlabel("time (tu)")
a.set_ylabel("fraction still circling")
a.set_ylim(-0.03, 1.03)
a.set_title("S102 survival; | = horizon (censored beyond)")
a.legend(fontsize=8, loc="lower left")

for rid, col, lab in [("A0", "C3", "R13 T10 unperturbed (dies 3979.9)"),
                      ("Q6-13-e1e-12-r9", "C1", "R13 T10 δ copy r9 (dies 203.6)"),
                      ("Q6-13-e1e-12-r1", "C2", "R13 T10 δ copy r1 (alive 5000)"),
                      ("B26-block", "C0", "R26 T10 block seed (alive 8000)"),
                      ("D40", "C4", "R13 T40 (alive 8000)")]:
    m = np.load(TR / f"{rid}.npz")["mass"]
    b.plot(np.arange(1, len(m) + 1), m, lw=0.4, color=col, label=lab)
b.set_ylim(0.4, 0.58)
b.set_xlim(0, 8000)
b.set_xlabel("time (tu)")
b.set_ylabel("mass ΣA/R² (per tu)")
b.set_title("mass traces")
b.legend(fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig(HERE / "lifetime.png", dpi=130)
