"""Lane 3 summary figure from research/traces/lane3/*.csv.

    .venv/bin/python -m alm_check.figures
"""

from __future__ import annotations

import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .lenia import REPO  # noqa: E402
from .sweeps import OUT  # noqa: E402

BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
FIG = REPO / "research" / "experiments" / "lane3" / "numerics.png"


def load(name):
    with open(OUT / f"{name}.csv") as f:
        return list(csv.DictReader(f))


def num(rows, k):
    return np.array([float(r[k]) if r.get(k) not in (None, "") else np.nan for r in rows])


def style(ax, title, xlabel, ylabel):
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    ax.set_xlabel(xlabel, fontsize=9, color=MUTED)
    ax.set_ylabel(ylabel, fontsize=9, color=MUTED)
    ax.grid(color=GRID, lw=0.6)
    ax.tick_params(colors=MUTED, labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)


def main():
    fig, axs = plt.subplots(2, 2, figsize=(10, 7.5), dpi=130)
    ts = [r for r in load("timestep") if r["fate"] == "persists"]
    T, dt = num(ts, "T"), 1 / num(ts, "T")
    for ax, k, lab in ((axs[0, 0], "speed", "speed (R per time unit)"),
                       (axs[0, 1], "mass", "mean mass ΣA/R²")):
        ax.plot(dt, num(ts, k), "-o", color=BLUE, lw=2, ms=5)
        i = int(np.where(T == 10)[0][0])
        ax.plot(dt[i], num(ts, k)[i], "o", ms=9, mfc="none", mec=INK)
        ax.annotate("S001 baseline T=10", (dt[i], num(ts, k)[i]), xytext=(8, -12),
                    textcoords="offset points", fontsize=8, color=INK)
        style(ax, f"{k.capitalize()} vs timestep (R=13, 128² torus)", "Δt = 1/T", lab)
    ax = axs[1, 0]
    res = [r for r in load("resolution") if r["fate"] == "persists" and r["zoom_order"] == "0"]
    R, sd = num(res, "R"), num(res, "mass_rel_sd")
    ax.loglog(R, sd, "-o", color=BLUE, lw=2, ms=5)
    ref = sd[R == 13][0] * (R / 13.0) ** -2
    ax.loglog(R, ref, "--", color=MUTED, lw=1)
    ax.annotate("∝ R⁻²", (R[-1], ref[-1]), xytext=(-34, 10), textcoords="offset points", fontsize=8, color=MUTED)
    ax.set_xticks([8, 13, 20, 26, 39, 52], labels=["8", "13", "20", "26", "39", "52"])
    ax.minorticks_off()
    style(ax, "Mass wobble amplitude vs resolution (T=10)", "kernel radius R (cells)", "mass sd / mean")
    ax = axs[1, 1]
    for Rk, c in (("13", BLUE), ("26", ORANGE)):
        h = load(f"heading-R{Rk}")
        a, late = num(h, "angle"), num(h, "heading_late")
        ax.plot(a, late, "-o", color=c, lw=1.5, ms=4, label=f"R = {Rk}")
        if Rk == "26":
            ax.plot(a, late[0] - a, "--", color=MUTED, lw=1, label="no-lattice prediction")
    ax.legend(frameon=False, fontsize=8)
    style(ax, "Travel heading after start rotation (late window)", "start rotation (deg)", "heading (deg)")
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)
    print(f"wrote {FIG.relative_to(REPO)}")


if __name__ == "__main__":
    main()
