"""Charts for the therapy toy, round 3 (therapy2.jsonl):

  G070 holiday.png     drug A stopped at 2000 tu: burden and resistant share, costs 0 / 0.1 / 0.3
  G071 thresholds.png  adaptive drug A paused at LOW x B0 (LOW 0.3, 0.5, 0.7, 0.9), cost 0.3
  G072 bind.png        two drugs: outcome of every run, five schedules x two costs

  python chart_round3.py OUT_DIR
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

H = Path(__file__).parent
R = [json.loads(l) for l in open(H / "therapy2.jsonl")]
L = [json.loads(l) for l in open(H / "therapy_long.jsonl")]
out = Path(sys.argv[1])
plt.rcParams.update({"font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False})
ORANGE, BLUE, GREY, PINK, GREEN = "#E69F00", "#0072B2", "#9a9a9a", "#CC79A7", "#009E73"


def tr(r):
    return np.array(r["trace"])


def eradicated(r):
    return next((x[0] for x in r["trace"] if x[1] == 0), None)


# ---- G070 holiday
fig, ax = plt.subplots(3, 2, figsize=(12.5, 8.4), sharex=True)
for i, c in enumerate((0.0, 0.1, 0.3)):
    for r in L:
        if r.get("cost", 0.0) == c and r["arm"] == "constant":
            T = tr(r)
            ax[i, 0].plot(T[:, 0], T[:, 1], color=ORANGE, lw=0.9, alpha=0.45, ls="--",
                          label="drug kept on" if (i == 0 and r["seed"] == 0) else None)
    for r in R:
        if r["exp"] == "holiday" and r["cost"] == c:
            T = tr(r)
            lab = "drug stopped at 2000" if (i == 0 and r["seed"] == 0) else None
            ax[i, 0].plot(T[:, 0], T[:, 1], color=GREEN, lw=1.1, label=lab)
            ax[i, 1].plot(T[:, 0], np.where(T[:, 1] > 0, T[:, 3], np.nan), color=GREEN, lw=1.0)
    for a in ax[i]:
        a.axvline(2000, color="#555", lw=0.8, ls=":")
    ax[i, 0].axhline(1.25, color="#bbb", lw=0.8, ls=":")
    ax[i, 0].set_ylim(0, 2.9); ax[i, 1].set_ylim(-0.03, 1.03)
    ax[i, 0].set_title("no cost of resistance" if c == 0 else f"cost {c}", loc="left", fontsize=11)
    ax[i, 0].set_ylabel("burden (× start)"); ax[i, 1].set_ylabel("resistant share")
for a in ax[-1]:
    a.set_xlabel("time since treatment began (tu)")
fig.legend(*ax[0, 0].get_legend_handles_labels(), frameon=False, loc="upper right", ncol=2)
fig.suptitle("Drug A (κ 0.3) for 2000 tu, then nothing. Four seeds; lines end where a tumour dies out.",
             x=0.01, ha="left", fontsize=10, color="#555")
fig.tight_layout(); fig.savefig(out / "holiday.png", dpi=110); plt.close(fig)

# ---- G071 thresholds
lows = (0.3, 0.5, 0.7, 0.9)
fig, ax = plt.subplots(2, 4, figsize=(13.5, 6.0), sharex=True, sharey="row")
for j, lo in enumerate(lows):
    for r in R:
        if r["exp"] == "threshold" and r["arm"] == f"adaptive{lo}":
            T = tr(r)
            ax[0, j].plot(T[:, 0], T[:, 1], color=BLUE, lw=0.9, alpha=0.85)
            ax[1, j].plot(T[:, 0], np.where(T[:, 1] > 0, T[:, 3], np.nan), color=BLUE, lw=0.9, alpha=0.85)
    ax[0, j].axhline(1.25, color="#555", ls=":", lw=0.9)
    ax[0, j].axhline(lo, color=ORANGE, ls="--", lw=0.9)
    ax[0, j].axhline(1.0, color="#bbb", ls=":", lw=0.8)
    rs = [r for r in R if r["exp"] == "threshold" and r["arm"] == f"adaptive{lo}"]
    n_prog = sum(r["progression"] is not None for r in rs)
    n_res = sum(r["trace"][-1][3] > 0.5 for r in rs if r["trace"][-1][1] > 0)
    ax[0, j].set_title(f"pause at {lo:g}× start\n{n_prog}/4 progressed, {n_res}/4 end mostly resistant",
                       loc="left", fontsize=10.5)
    ax[1, j].set_xlabel("time (tu)")
    ax[0, j].set_ylim(0, 1.6); ax[1, j].set_ylim(-0.03, 1.03)
ax[0, 0].set_ylabel("burden (× start)"); ax[1, 0].set_ylabel("resistant share")
fig.suptitle("Adaptive drug A (κ 0.3), cost 0.3: off when the tumour falls to the orange line, on again at 1×. "
             "Dotted: 1.25× = progression.", x=0.01, ha="left", fontsize=10, color="#555")
fig.tight_layout(); fig.savefig(out / "thresholds.png", dpi=110); plt.close(fig)

# ---- G072 bind outcome grid
arms = [("A", "drug A only (hits fast cells)"), ("B", "drug B only (hits slow cells)"),
        ("A+B", "both, all the time"), ("alternate", "alternate every 100 tu"),
        ("steer", "steer: A; B while mostly resistant")]
fig, ax = plt.subplots(figsize=(12.5, 5.6))
ax.set_xlim(-0.5, 1.5); ax.set_ylim(len(arms) - 0.5, -0.9)
ax.axis("off")
for j, c in enumerate((0.0, 0.3)):
    ax.text(j, -0.75, "no cost of resistance" if c == 0 else "cost of resistance 0.3", ha="center",
            fontsize=11.5, weight="bold")
    for i, (arm, lab) in enumerate(arms):
        rs = sorted((r for r in R if r["exp"] == "bind" and r["arm"] == arm and r["cost"] == c), key=lambda r: r["seed"])
        for k, r in enumerate(rs):
            x = j - 0.33 + 0.1 * k
            e = eradicated(r)
            if e is not None:
                ax.scatter(x, i, s=170, marker="X", color="#222")
            elif r["progression"] is not None:
                ax.scatter(x, i, s=170, color="#D55E00")
            else:
                ax.scatter(x, i, s=170, facecolor="white", edgecolor="#777", lw=1.6)
        ne = sum(eradicated(r) is not None for r in rs)
        npg = sum(r["progression"] is not None and eradicated(r) is None for r in rs)
        da = np.mean([r["drug_A"] / r["tu"] for r in rs]); db = np.mean([r["drug_B"] / r["tu"] for r in rs])
        txt = f"{ne}/4 gone, {npg}/4 progressed\ndrug A {100 * da:.0f}% of the time, B {100 * db:.0f}%"
        ax.text(j + 0.08, i, txt, va="center", fontsize=9.5, color="#333")
        if j == 0:
            ax.text(-0.5, i - 0.32, lab, fontsize=10, color="#555")
ax.scatter([], [], s=120, marker="X", color="#222", label="eradicated")
ax.scatter([], [], s=120, color="#D55E00", label="progressed (passed 1.25× start), not eradicated")
ax.scatter([], [], s=120, facecolor="white", edgecolor="#777", label="held below 1.25× start")
ax.legend(frameon=False, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.08))
fig.suptitle("Two drugs, 4000 tu, four seeds per row (κ 0.3 each). Drug A kills in proportion to the genome g, "
             "drug B to 1 − g.", x=0.01, ha="left", fontsize=10, color="#555")
fig.tight_layout(); fig.savefig(out / "bind.png", dpi=110); plt.close(fig)
print("ok")
