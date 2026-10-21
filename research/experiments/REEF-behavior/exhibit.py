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


def main(run_dir, frames, score_json, out, times=None, labels=None, rows_names=None, title=None):
    man = json.load(open(f"{run_dir}/manifest.json"))
    sc = json.load(open(score_json))
    fr = np.load(frames)
    S0 = np.load(f"{run_dir}/checkpoints.npz")["S_00000"]
    tr = np.load(f"{run_dir}/trace.npz")
    R, T, N = man["rule"]["R"], man["rule"]["T"], man["world"]["N"]
    tc = sc["t_c"]
    if times is None:
        times = [0.0] + [tc + d for d in (0, 5, 10, 20)]
        labels = ["t = 0", f"t_c = {tc:g}", "t_c + 5", "t_c + 10", "t_c + 20"]
    plt.rcParams.update({"font.size": 8, "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": GRID})
    fig = plt.figure(figsize=(9.2, 8.4), facecolor="white")
    gs = fig.add_gridspec(4, 5, height_ratios=[1, 1, 1, 1.05], hspace=0.28, wspace=0.06)
    names = rows_names or ("Encounter E", "Glider alone", "Ring alone (S103)")
    rows = [(names[0], lambda k: fr["E"][k]), (names[1], lambda k: fr["G"][k]), (names[2], lambda k: S0)]
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
    ax.semilogy(t, tr["mass_G"] + tr["mass_S"], color=SERIES[1], lw=2, ls=(0, (4, 2)) if sc["t_c"] is None else "-")
    ax.text(t[-1] + 0.5, tr["mass_E"][-1], "encounter", color=INK, va="center", fontsize=8)
    ax.text(t[-1] + 0.5, (tr["mass_G"] + tr["mass_S"])[-1] * (0.8 if sc["t_c"] is None else 1), names[1].lower() + "\n+ ring alone", color=INK, va="top" if sc["t_c"] is None else "center", fontsize=8)
    for name, x, ls in (("t_kr", sc["t_kr"], ":"), ("t_int", sc["t_int"], "--"), ("t_c", tc, "-"), ("window end", sc["observables"]["t_end"], "-.")):
        if x is not None:
            ax.axvline(x, color=MUTED, lw=1, ls=ls)
            ha = "left" if name == "t_c" else "right"
            ax.text(x, 150, f" {name} ", rotation=90, va="top", ha=ha, fontsize=7, color=MUTED)
    ax.set_xlim(0, t[-1] + 7)
    ax.set_ylim(0.2, 200)
    ax.set_xlabel("time (tu; 1 tu = 10 steps)")
    ax.set_ylabel("total mass (ΣA / R²)")
    ax.grid(True, axis="y", color=GRID, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    g = man["inputs"].get("geometry", {})
    fig.suptitle(title or f"{man['run_id']}: glider meets ring; contact ignites an expanding colony", fontsize=10, x=0.02, ha="left")
    flags = ", ".join(sc["flags"]) or "none"
    fig.text(0.02, 0.012,
             (f"Class {sc['class']} (flags: {flags}); finite horizon: scored on the t_c + 20 tu window, shown to 50 tu (after ~27 tu the colony "
              f"meets its own periodic images on the {N}² torus).\n" if sc["t_c"] is not None else
              f"Class {sc['class']} (flags: {flags}); finite horizon 50 tu, no contact within the 30 tu timeout.\n") +
             f"Rule: poly/poly, μ 0.155, σ 0.020, R {R}, T {T}, Euler + clip, float64, periodic N {N} ({N / R:.1f} R). "
             f"Snapshot {man['inputs']['glider']['snapshot']}, b/R {g.get('b_R_realized', g.get('b_R_requested', float('nan'))):+.2f}. "
             f"Controls: lockstep {names[1].lower()} and ring alone; frames sha256 {man['outputs']['frames.npz']['sha256'][:12]}…",
             fontsize=6.5, color=MUTED, va="bottom")
    fig.savefig(out, dpi=150, bbox_inches="tight")


def strip(items, out, title):
    """One encounter per column at its own t_c + 20 tu. items: (label, run_dir, frames, score_json)."""
    plt.rcParams.update({"font.size": 8, "text.color": INK})
    fig, axs = plt.subplots(1, len(items), figsize=(1.55 * len(items), 2.3), facecolor="white")
    for ax, (label, run_dir, frames, score_json) in zip(axs, items):
        sc = json.load(open(score_json))
        man = json.load(open(f"{run_dir}/manifest.json"))
        T, R, N = man["rule"]["T"], man["rule"]["R"], man["world"]["N"]
        k = int(round(sc["observables"]["t_end"] * T))
        ax.imshow(np.load(frames)["E"][k], cmap=FIELD, vmin=0, vmax=1, interpolation="nearest")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(GRID)
        ax.set_title(f"{label}\n{man['run_id']}", fontsize=7)
        ax.set_xlabel(f"t_c {sc['t_c']:g} → {sc['observables']['t_end']:g} tu\n{sc['observables']['n_bodies']} bodies", fontsize=6.5, color=MUTED)
    axs[0].plot([10, 10 + 5 * R], [N - 12, N - 12], color=INK, lw=2, solid_capstyle="butt")
    axs[0].text(10 + 2.5 * R, N - 18, "5 R", ha="center", va="bottom", fontsize=6.5)
    fig.suptitle(title, fontsize=9, x=0.01, ha="left")
    fig.text(0.01, -0.06, "Each frame is the encounter at the end of its scoring window (t_c + 20 tu). Finite horizon; N 256 (19.7 R), R 13, T 10, "
             "μ 0.155, σ 0.020, poly/poly, Euler + clip, float64. All classes FISSION + PROLIFERATION; matched controls stayed in class.",
             fontsize=6.3, color=MUTED, wrap=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")


ROUTES = (("alm", "reference (alm)"), ("chkfft", "checkpointed FFT"), ("direct", "direct convolution"),
          ("N512", "N 512, R 13"), ("T20", "T 20 (dt halved)"), ("R26", "R 26 (2×2, N 512)"))
TC_TOL, MASS_TOL = 0.5, 0.01  # PROTOCOL §9 frozen tolerances (numerics MATRIX.md); ignition and front have none


def check_matrix(matrix_json, out, r26=None, source=""):
    """Panel F: numerics route x {class, t_c, ignition (D-017), front speed, E mass t20} for P2 and P3.

    matrix_json: REEF-numerics checks/matrix.json. r26: {"P2": score.json, ...} from the D-010
    rescore; it replaces the R26 class cell (the frozen bitwise S rule is not used at R26).
    Solid orange box: outside the frozen §9 tolerance. Dashed: shifted, no frozen tolerance."""
    m = json.load(open(matrix_json))
    plt.rcParams.update({"font.size": 8, "text.color": INK})
    encs = list(m)
    cols = ["class", "t_c (tu)", "ignition (tu)", "front (R/tu)", "E mass t20"]
    x0, w = 1.9, 1.2
    fig, axs = plt.subplots(1, len(encs), figsize=(6.6 * len(encs), 3.0), facecolor="white")
    for ax, e in zip(np.atleast_1d(axs), encs):
        ref = m[e]["alm"]
        ax.set_xlim(0, x0 + w * len(cols))
        ax.set_ylim(len(ROUTES) + 0.1, -1)
        ax.axis("off")
        ax.text(0.03, -0.72, e, fontsize=10, fontweight="bold", va="center")
        for j, c in enumerate(cols):
            ax.text(x0 + w * (j + 0.5), -0.2, c, ha="center", va="center", fontsize=7.5, color=MUTED)
        for i, (key, name) in enumerate(ROUTES):
            row = m[e][key]
            y = i + 0.5
            cls = row["class"]
            if key == "R26":
                cls = "pending D-010"
                if r26 and e in r26:  # (D-010 primary, D-024 mass-band variant)
                    cls = "\n".join(json.load(open(f))["class"].replace("CONTROL_FAILURE", "CONTROL FAIL") + mark
                                     for f, mark in zip(r26[e], ("*", "†")))
            dt, di = row["t_c"] - ref["t_c"], row["ignition_t"] - ref["ignition_t"]
            dm = row["mass_E_t20"] / ref["mass_E_t20"] - 1
            vals = [cls, f"{row['t_c']:g}" + (f" ({dt:+.2g})" if abs(dt) > 1e-9 else ""),
                    f"{row['ignition_t']:.1f}" + (f" ({di:+.1f})" if abs(di) > 1e-9 else ""),
                    f"{row['front_R_per_tu']:.3f}", f"{row['mass_E_t20']:.2f}" + (f" ({dm:+.0%})" if abs(dm) > 1e-6 else "")]
            box = [None, "solid" if abs(dt) > TC_TOL + 1e-9 else None, "dashed" if abs(di) > 1e-9 else None,
                   None, "solid" if abs(dm) > MASS_TOL else None]
            if i % 2 == 0:
                ax.add_patch(plt.Rectangle((0, i), x0 + w * len(cols), 1, color="#f4f3ef", lw=0))
            ax.text(0.05, y, name, va="center", fontsize=8)
            for j, v in enumerate(vals):
                if box[j]:
                    ax.add_patch(plt.Rectangle((x0 + w * j + 0.04, i + 0.12), w - 0.08, 0.76, fill=False,
                                               ec=SERIES[1], lw=1.2, ls="-" if box[j] == "solid" else (0, (3, 2))))
                ax.text(x0 + w * (j + 0.5), y, v, ha="center", va="center", fontsize=6.5 if "\n" in v else 8, color=SERIES[1] if box[j] else INK)
    fig.suptitle("Panel F. Numerical checks of P2 and P3: FISSION survives every route (R 26 judged against its own control, D-010); "
                 "timing and mass do not survive T 20 or R 26", fontsize=9.5, x=0.01, ha="left")
    fig.text(0.01, -0.12,
             "* R 26 primary label (applying D-010, ruling D-024): the R 26 ring is judged against its own R 26 ring-alone control, never bitwise; "
             "the control is valid if it stays one STATIC body (< 0.02 R/tu) through the window; it does (0.0003 R/tu), and E is FISSION + PROLIFERATION.\n"
             "† Disclosed variant: also requiring ring-alone mass in 0.378–0.383 (the 200–300 tu range) gives CONTROL_FAILURE, because the ring-alone "
             "dips to 0.376 at 4–11 tu as the 2×2-block seed relaxes, before contact. R 26 class cells are scored from float64 checkpoints at 1-tu cadence\n"
             "(t_c 7.0 at that cadence; the per-step t_c in the t_c column is the numerics lane's). Solid orange box: outside the frozen §9 tolerance "
             "(t_c within 0.5 tu, masses within 1%). Dashed: ignition shifted; ignition and front speed have no frozen tolerance.\n"
             "Ignition (D-017): first time E mass ≥ 2 × (glider alone + ring alone) and ≥ 5 bodies. Front: colony edge speed. Reference: N 256 (19.7 R), "
             "R 13, T 10, μ 0.155, σ 0.020, poly/poly, Euler + clip, float64; finite horizon, scored on the t_c + 20 tu window. " + source,
             fontsize=6.5, color=MUTED, va="top")
    fig.savefig(out, dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    main(*sys.argv[1:5])
