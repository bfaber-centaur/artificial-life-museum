"""REEF exhibit panel: an encounter next to its matched isolated controls (behavior lane).

Rows: encounter E, glider alone (G), ring alone (S). Columns: t = 0, t_c, t_c + 5, + 10, + 20 tu.
Below: total mass of E against G + S on a log axis, with t_kr, t_int, t_c and the window end.
Inputs are the field run directory, its frames.npz and this lane's score.json for the run.

    PYTHONPATH=src python research/experiments/REEF-behavior/exhibit.py RUN_DIR FRAMES SCORE_JSON OUT_PNG
"""

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#d9d8d2"
SERIES = ("#2a78d6", "#eb6834")  # categorical slots 1, 2 (validated default palette)
FIELD = LinearSegmentedColormap.from_list("field", ["#ffffff", "#9ec5f4", "#2a78d6", "#104281", "#0d366b"])


def main(run_dir, frames, score_json, out):
    man = json.load(open(f"{run_dir}/manifest.json"))
    sc = json.load(open(score_json))
    fr = np.load(frames)
    S0 = np.load(f"{run_dir}/checkpoints.npz")["S_00000"]
    tr = np.load(f"{run_dir}/trace.npz")
    R, T, N = man["rule"]["R"], man["rule"]["T"], man["world"]["N"]
    tc = sc["t_c"]
    times = [0.0] + [tc + d for d in (0, 5, 10, 20)]
    labels = ["t = 0", f"t_c = {tc:g}", "t_c + 5", "t_c + 10", "t_c + 20"]
    plt.rcParams.update({"font.size": 8, "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": GRID})
    fig = plt.figure(figsize=(9.2, 8.4), facecolor="white")
    gs = fig.add_gridspec(4, 5, height_ratios=[1, 1, 1, 1.05], hspace=0.28, wspace=0.06)
    rows = [("Encounter E", lambda k: fr["E"][k]), ("Glider alone", lambda k: fr["G"][k]), ("Ring alone (S103)", lambda k: S0)]
    for i, (name, get) in enumerate(rows):
        for j, t in enumerate(times):
            k = int(round(t * T))
            ax = fig.add_subplot(gs[i, j])
            ax.imshow(get(k), cmap=FIELD, vmin=0, vmax=1, interpolation="nearest")
            ax.set_xticks([])
            ax.set_yticks([])
            for s in ax.spines.values():
                s.set_color(GRID)
            if i == 0:
                ax.set_title(f"{labels[j]}\n({t:g} tu)", fontsize=8)
            if j == 0:
                ax.set_ylabel(name, fontsize=8)
            if i == 2 and j == 0:  # scale bar: 5 R
                ax.plot([12, 12 + 5 * R], [N - 14, N - 14], color=INK, lw=2, solid_capstyle="butt")
                ax.text(12 + 2.5 * R, N - 22, "5 R", ha="center", va="bottom", fontsize=7)
    ax = fig.add_subplot(gs[3, :])
    t = np.arange(len(tr["mass_E"])) / T
    ax.semilogy(t, tr["mass_E"], color=SERIES[0], lw=2)
    ax.semilogy(t, tr["mass_G"] + tr["mass_S"], color=SERIES[1], lw=2)
    ax.text(t[-1] + 0.5, tr["mass_E"][-1], "encounter", color=INK, va="center", fontsize=8)
    ax.text(t[-1] + 0.5, (tr["mass_G"] + tr["mass_S"])[-1], "glider alone\n+ ring alone", color=INK, va="center", fontsize=8)
    for name, x, ls in (("t_kr", sc["t_kr"], ":"), ("t_int", sc["t_int"], "--"), ("t_c", tc, "-"), ("window end", sc["observables"]["t_end"], "-.")):
        if x is not None:
            ax.axvline(x, color=MUTED, lw=1, ls=ls)
            ha = "left" if name == "t_c" else "right"
            ax.text(x, 150, f" {name} ", rotation=90, va="top", ha=ha, fontsize=7, color=MUTED)
    ax.set_xlim(0, t[-1] + 7)
    ax.set_ylim(0.3, 200)
    ax.set_xlabel("time (tu; 1 tu = 10 steps)")
    ax.set_ylabel("total mass (ΣA / R²)")
    ax.grid(True, axis="y", color=GRID, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    g = man["inputs"].get("geometry", {})
    fig.suptitle(f"{man['run_id']}: glider meets ring; contact ignites an expanding colony", fontsize=10, x=0.02, ha="left")
    flags = ", ".join(sc["flags"]) or "none"
    fig.text(0.02, 0.012,
             f"Class {sc['class']} (flags: {flags}); finite horizon, scored to t_c + 20 tu, shown to 50 tu (after ~27 tu the colony "
             f"meets its own periodic images on the {N}² torus).\n"
             f"Rule: poly/poly, μ 0.155, σ 0.020, R {R}, T {T}, Euler + clip, float64, periodic N {N} ({N / R:.1f} R). "
             f"Snapshot {man['inputs']['glider']['snapshot']}, b/R {g.get('b_R_realized', float('nan')):+.2f}, gap {g.get('gap_R_realized', float('nan')):.2f} R. "
             f"Controls: lockstep glider-alone and ring-alone; frames sha256 {man['outputs']['frames.npz']['sha256'][:12]}…",
             fontsize=6.5, color=MUTED, va="bottom")
    fig.savefig(out, dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    main(*sys.argv[1:5])
