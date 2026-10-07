"""Figure A: Orbium (S001) survival boundary under four disturbances.

Claims illustrated: C023 (sharp all-or-nothing edges, INDEPENDENTLY_CHECKED),
C026 (where mass is removed matters, INDEPENDENTLY_CHECKED), C027 (I003/I004 edges
move with the timestep, NUMERICALLY_FRAGILE). Statuses are copied from
research/claims.md, not computed here.

Reads only committed data (Lane 4 L4-001 results and saved states, Lane 3 traces).
Runs no simulation. Writes, next to this file:
  figure-A.png / .svg / .pdf   the figure
  figure-A-edges.csv           every bracket plotted in panels b and d
  figure-A-runs.csv            every run plotted in panel b
  figure-A.provenance.json     inputs (sha256 + last commit), code commit, versions

Usage (from the repo root):
  .venv/bin/python research/figures/A-survival-boundary/make_figure.py
"""
import csv
import math
import pathlib
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figlib import edges as E  # noqa: E402
from figlib import provenance as P  # noqa: E402
from figlib.style import (EDIT, GRID, INK, MUTED, OKABE_ITO, OUTCOME, STATUS,  # noqa: E402
                          UNRESOLVED, figure_style, status_badge)

REPO = P.REPO
L4 = REPO / "research/experiments/L4-001-disturbance-battery"
L3 = REPO / "research/traces/lane3"
OUT = HERE / "figure-A"

# Panel order: by how much mass change kills, smallest first (C026's point).
IVS = ["I002", "I004", "I001", "I003"]
NAMES = {
    "I002": "central disc deletion",
    "I004": "port-side cut",
    "I001": "uniform attenuation",
    "I003": "frontal addition",
}
SIGN = {"I001": -1, "I002": -1, "I004": -1, "I003": +1}
# Bracket ends saved by Lane 4 at t0 = 1000 (states/index.csv): (recovered, died).
STATE_PAIRS = {
    "I001": ("0.100000", "0.103125"),
    "I002": ("0.059375", "0.062500"),
    "I003": ("0.306250", "0.309375"),
    "I004": ("0.081250", "0.084375"),
}
# Ledger statuses (research/claims.md @ main). Edge *values* of I003/I004 are T-fragile (C027).
EDGE_STATUS = {iv: ("C023", "INDEPENDENTLY_CHECKED") for iv in IVS}
FRAGILE = {"I003": ("C027", "NUMERICALLY_FRAGILE"), "I004": ("C027", "NUMERICALLY_FRAGILE")}

# Conditions in panel d, top to bottom: (source, condition, label, files, reader).
CONDITIONS = [
    ("Lane 4 ref", "T10 R13", "Lane 4, ref engine", [L4 / "results/coarse.csv", L4 / "results/bisect.csv"], "l4"),
    ("Lane 3 alm_check", "T10 R13", "Lane 3, own code", [L3 / "disturb-T10-R13.csv"], "l3"),
    ("Lane 3 alm_check", "T10 R26", "Lane 3, R = 26", [L3 / "disturb-T10-R26.csv"], "l3"),
    ("Lane 4 ref", "T10 R26", "Lane 4, R = 26", [L4 / "results/R26/coarse.csv", L4 / "results/R26/bisect.csv"], "l4"),
    ("Lane 4 ref", "T20 R13", "Lane 4, T = 20", [L4 / "results/T20/coarse.csv", L4 / "results/T20/bisect.csv"], "l4"),
    ("Lane 3 alm_check", "T40 R13", "Lane 3, T = 40", [L3 / "disturb-T40-R13.csv"], "l3"),
]
BASELINE = ("Lane 4 ref", "T10 R13")


def load_runs():
    runs, inputs = [], []
    for src, cond, _, files, kind in CONDITIONS:
        for f in files:
            inputs.append(f)
            runs += E.read_lane4(f, src, cond) if kind == "l4" else E.read_lane3(f, src, cond)
    return runs, inputs


def load_state(iv, s):
    p = L4 / f"states/L4-001-{iv}-s{s}-t1000-N128-ref.npz"
    return p, np.load(p)


def load_trace(iv, s):
    p = L4 / f"states/L4-001-{iv}-s{s}-t1000-N128-ref.trace.csv"
    rows = list(csv.DictReader(open(p)))
    return p, np.array([[float(r["step_after_t0"]), float(r["mass"]), float(r["cum_dx"]),
                         float(r["cum_dy"])] for r in rows])


def centred_crop(A, ref, half=22):
    """Roll the torus so ref's circular-mean centroid sits mid-array, then crop."""
    ny, nx = ref.shape
    ang = lambda w, n: np.angle((w * np.exp(2j * np.pi * np.arange(n) / n)).sum()) % (2 * np.pi) * n / (2 * np.pi)
    cx, cy = ang(ref.sum(0), nx), ang(ref.sum(1), ny)
    sx, sy = int(round(nx / 2 - cx)), int(round(ny / 2 - cy))
    B = np.roll(np.roll(A, sy, 0), sx, 1)
    return B[ny // 2 - half: ny // 2 + half, nx // 2 - half: nx // 2 + half]


# ---------------------------------------------------------------- panels

def panel_footprints(axs, inputs):
    """a: where each lethal edit lands on the body (bracket 'died' end, t0 = 1000)."""
    vmax = 0.0
    crops = {}
    for iv in IVS:
        p, st = load_state(iv, STATE_PAIRS[iv][1])
        inputs.append(p)
        before, during = st["before"], st["during"]
        crops[iv] = (centred_crop(before, before), centred_crop(during - before, before))
        vmax = max(vmax, np.abs(crops[iv][1]).max())
    rem = LinearSegmentedColormap.from_list("rem", ["#ffffff00", EDIT["removed"]])
    add = LinearSegmentedColormap.from_list("add", ["#ffffff00", EDIT["added"]])
    for ax, iv in zip(axs, IVS):
        body, d = crops[iv]
        ax.imshow(body, cmap="Greys", vmin=0, vmax=1.15, interpolation="nearest")
        neg = np.where(d < 0, -d, 0)
        pos = np.where(d > 0, d, 0)
        # Per-panel scaling so the footprint is visible; magnitudes are in panel b, not here.
        if neg.max() > 0:
            ax.imshow(neg / neg.max(), cmap=rem, vmin=0, vmax=1, interpolation="nearest")
        if pos.max() > 0:
            ax.imshow(pos / pos.max(), cmap=add, vmin=0, vmax=1, interpolation="nearest")
        # heading arrow from Lane 4's trace of the recovered twin (first 100 steps)
        tp, tr = load_trace(iv, STATE_PAIRS[iv][0])
        inputs.append(tp)
        v = tr[9, 2:4] - tr[0, 2:4]
        v = v / np.hypot(*v)
        n = body.shape[0]
        c = np.array([n - 6.5, 5.5])  # top-right corner: heading key
        ax.add_patch(FancyArrowPatch(tuple(c - 4 * v), tuple(c + 4 * v),
                                     arrowstyle="-|>", mutation_scale=7, color=INK, lw=0.9))
        ax.text(c[0] - 6.5, c[1] - 0.2, "heading", fontsize=5.4, color=MUTED, ha="right", va="center")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(True)
            sp.set_color(GRID)
        dm = st_dm(iv)
        ax.set_title(f"{iv} {NAMES[iv]}", fontsize=7, loc="left", pad=2)
        ax.text(0.03, 0.04, f"ΔM = {dm:+.1%}", transform=ax.transAxes, fontsize=6.3,
                color=EDIT["added"] if dm > 0 else EDIT["removed"], fontweight="bold")
    # 1-R scale bar on the first map (R = 13 cells)
    ax = axs[0]
    n = crops[IVS[0]][0].shape[0]
    ax.plot([n - 16, n - 3], [n - 3, n - 3], color=INK, lw=1.2, solid_capstyle="butt")
    ax.text(n - 9.5, n - 4.5, "R", ha="center", va="bottom", fontsize=6.3)


_index = None


def st_dm(iv):
    """Achieved ΔM/M₀ of the 'died' bracket state (states/index.csv)."""
    global _index
    if _index is None:
        _index = {r["run_id"]: r for r in csv.DictReader(open(L4 / "states/index.csv"))}
    rid = f"L4-001-{iv}-s{STATE_PAIRS[iv][1]}-t1000-N128-ref"
    return float(_index[rid]["achieved_dmass_frac"])


def panel_overview(ax, runs, edges_):
    """b: every Lane 4 baseline run on one signed mass axis, five phases per intervention."""
    lo, hi = -0.16, 0.34
    base = [r for r in runs if (r.source, r.condition) == BASELINE]
    yt, yl = [], []
    off_axis = {}
    for k, iv in enumerate(IVS):
        y0 = -k * 1.0
        yt.append(y0 - 0.0)
        yl.append(f"{iv}\n{NAMES[iv]}")
        ax.axhspan(y0 - 0.42, y0 + 0.42, color="#f4f4f4" if k % 2 == 0 else "white", lw=0, zorder=0)
        for ph in range(5):
            y = y0 + (ph - 2) * 0.16
            eg = next(e for e in edges_ if (e.source, e.condition, e.intervention, e.phase) == (*BASELINE, iv, ph))
            a, b = SIGN[iv] * eg.survive_abs, SIGN[iv] * eg.die_abs
            ax.plot([a, b], [y, y], color=UNRESOLVED, lw=3.2, solid_capstyle="butt", zorder=1)
            for r in base:
                if r.intervention != iv or r.phase != ph:
                    continue
                if not lo <= r.dmass <= hi:
                    off_axis[(iv, r.outcome)] = off_axis.get((iv, r.outcome), 0) + 1
                    continue
                o = OUTCOME[r.outcome]
                ax.scatter(r.dmass, y, s=9 if o["fill"] else 10, marker=o["marker"],
                           facecolors=o["color"] if o["fill"] else o["color"],
                           edgecolors="none" if o["fill"] else None, linewidths=0.7, zorder=3)
        # edge annotation in mass terms (range over phases)
        egs = [e for e in edges_ if (e.source, e.condition, e.intervention) == (*BASELINE, iv)]
        smin, smax = min(e.survive_abs for e in egs), max(e.survive_abs for e in egs)
        dmin, dmax = min(e.die_abs for e in egs), max(e.die_abs for e in egs)
        verb = "added" if SIGN[iv] > 0 else "removed"
        n_out = sum(v for (i, _), v in off_axis.items() if i == iv)
        n_all = sum(1 for r in base if r.intervention == iv)
        txt = (f"recovers at ≤ {fmt_rng(smin, smax)} {verb}\n"
               f"dies at ≥ {fmt_rng(dmin, dmax)} {verb}\n"
               f"{n_all} runs; {n_out} beyond this axis, all died")
        # put the summary in the empty half of the row (right of 0 for losses, left for gains)
        xt_ = 0.035 if SIGN[iv] < 0 else lo + 0.01
        ax.text(xt_, y0, txt, fontsize=6.1, va="center", ha="left", color=INK, linespacing=1.35)
    ax.axvline(0, color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=0)
    ax.text(0.003, 0.52, "no edit", fontsize=6, color=MUTED, ha="left", va="bottom")
    ax.set_xlim(lo, hi)
    ax.set_ylim(-3.5, 0.6)
    ax.set_yticks(yt, yl, fontsize=6.6)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    xt = np.arange(-0.15, 0.31, 0.05)
    ax.set_xticks(xt, [f"{v:+.0%}" if abs(v) > 1e-9 else "0" for v in xt])
    ax.set_xlabel("mass change made by the edit, ΔM/M₀  (each row = one of 5 phase replicates, t0 = 1000…1004)")
    ax.grid(axis="x", color=GRID, lw=0.4, zorder=0)
    return off_axis


def fmt_rng(a, b):
    return f"{a:.1%}" if abs(a - b) < 5e-4 else f"{a:.1%}–{b:.1%}"


def panel_timecourses(axs, inputs):
    """c: mass after the edit for the two bracket ends at t0 = 1000."""
    for ax, iv in zip(axs, IVS):
        for which, s in zip(("RECOVERED", "DIED"), STATE_PAIRS[iv]):
            p, tr = load_trace(iv, s)
            inputs.append(p)
            rid = f"L4-001-{iv}-s{s}-t1000-N128-ref"
            m0 = float(_index[rid]["mass_before"])
            m_edit = float(_index[rid]["mass_after_edit"])
            t = np.concatenate([[0], tr[:, 0]]) / 10.0  # steps -> time units (T = 10)
            m = np.concatenate([[m_edit], tr[:, 1]]) / m0
            o = OUTCOME[which]
            sel = t <= 30
            ax.plot(t[sel], m[sel], color=o["color"], lw=1.0, ls="-" if which == "RECOVERED" else (0, (3, 1.5)),
                    marker=o["marker"], ms=2.2 if which == "RECOVERED" else 2.8, mew=0.6,
                    markevery=1, label=f"{o['label']} (s = {float(s):.4g})")
        ax.axhline(1, color=MUTED, lw=0.5, ls=(0, (2, 2)))
        ax.set_xlim(0, 30)
        ax.set_ylim(-0.05, 1.42)
        ax.set_title(f"{iv}", fontsize=7, loc="left", pad=2)
        ax.grid(color=GRID, lw=0.4)
        ax.set_xticks([0, 10, 20, 30])
    axs[0].set_ylabel("mass / pre-edit mass")
    for ax in axs[1:]:
        ax.tick_params(labelleft=False)


def panel_zoom(axs, edges_):
    """d: the edge in |ΔM/M₀| per condition and phase, both lanes, two discretisations."""
    for ax, iv in zip(axs, IVS):
        y = 0
        yt, yl = [], []
        xs = []
        for src, cond, label, _, _ in CONDITIONS:
            egs = sorted([e for e in edges_ if (e.source, e.condition, e.intervention) == (src, cond, iv)],
                         key=lambda e: e.phase)
            if not egs:
                continue
            fragile_row = iv in FRAGILE and cond.startswith(("T20", "T40"))
            ys = []
            for e in egs:
                ax.plot([e.survive_abs, e.die_abs], [y, y], color=UNRESOLVED, lw=2.4, solid_capstyle="butt")
                ax.scatter([e.survive_abs], [y], s=7, marker="o", color=OUTCOME["RECOVERED"]["color"], zorder=3,
                           edgecolors="none")
                ax.scatter([e.die_abs], [y], s=9, marker="x", color=OUTCOME["DIED"]["color"], zorder=3, linewidths=0.7)
                if not e.monotone:
                    ax.text(e.die_abs, y, " !", color=OKABE_ITO["purple"], fontsize=6, va="center")
                xs += [e.survive_abs, e.die_abs]
                ys.append(y)
                y -= 1
            if fragile_row:
                ax.axhspan(min(ys) - 0.5, max(ys) + 0.5, facecolor="none", edgecolor=STATUS["NUMERICALLY_FRAGILE"]["color"],
                           hatch="////", lw=0, alpha=0.35, zorder=0)
            yt.append(np.mean(ys))
            yl.append(label + (f" ({len(egs)} phases)" if len(egs) > 1 else " (1 phase)"))
            y -= 0.7
        # shared baseline band: Lane 4 T10 R13 envelope
        bl = [e for e in edges_ if (e.source, e.condition, e.intervention) == (*BASELINE, iv)]
        ax.axvspan(min(e.survive_abs for e in bl), max(e.die_abs for e in bl), color=OKABE_ITO["sky"], alpha=0.12,
                   lw=0, zorder=0)
        pad = (max(xs) - min(xs)) * 0.12 + 1e-3
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(y + 0.2, 0.8)
        ax.set_yticks(yt, yl if ax is axs[0] else [""] * len(yl), fontsize=6.2)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.grid(axis="x", color=GRID, lw=0.4)
        ax.xaxis.set_major_formatter(lambda v, _: f"{v:.1%}" if v < 0.2 else f"{v:.0%}")
        ax.locator_params(axis="x", nbins=3)
        verb = "added" if SIGN[iv] > 0 else "removed"
        ax.set_xlabel(f"|ΔM/M₀| {verb}")
        ax.set_title(f"{iv} {NAMES[iv]}", fontsize=7, loc="left", pad=11)
        if iv in FRAGILE:  # edge value moves with dt by more than the phase spread
            fid, fst = FRAGILE[iv]
            status_badge(ax, fid, fst, x=0.0, y=1.0, ha="left")
            # the shift exceeds the T = 10 phase spread: that is what makes C027 fragile


def build():
    runs, inputs = load_runs()
    edges_ = E.edges(runs)
    bad = [e for e in edges_ if not e.monotone]

    with figure_style():
        fig = plt.figure(figsize=(7.2, 9.6), layout="constrained")
        fig.suptitle("Figure A. Orbium (S001) survival boundary under four standardized disturbances",
                     x=0.005, ha="left", fontsize=9, fontweight="bold")
        sf = fig.subfigures(4, 1, height_ratios=[1.25, 2.55, 1.35, 3.05], hspace=0.02)
        axa = sf[0].subplots(1, 4)
        axb = sf[1].subplots(1, 1)
        axc = sf[2].subplots(1, 4, sharey=True)
        axd = sf[3].subplots(1, 4)

        panel_footprints(axa, inputs)
        sf[0].suptitle("a   Where the smallest lethal edit lands on the body", x=0.005, ha="left", fontsize=7.5, fontweight="bold")
        off = panel_overview(axb, runs, edges_)
        sf[1].suptitle("b   Every tested edit on one mass axis: survival flips in a narrow band whose position "
                       "depends on where mass goes", x=0.005, ha="left", fontsize=7.5, fontweight="bold")
        status_badge(axb, "C023 + C026", "INDEPENDENTLY_CHECKED", x=1.0, y=1.005)
        panel_timecourses(axc, inputs)
        sf[2].suptitle("c   All-or-nothing: mass after the edit for the two runs either side of each edge", x=0.005, ha="left", fontsize=7.5, fontweight="bold")
        sf[2].supxlabel("time after edit (time units; T = 10 steps per unit)", fontsize=6.8)
        panel_zoom(axd, edges_)
        sf[3].suptitle("d   Zoom on each edge: a second lane's code agrees; resolution barely moves it; "
                       "a finer timestep moves I003 and I004", x=0.005, ha="left", fontsize=7.5, fontweight="bold")
        status_badge(axd[0], "T10 R13 rows: C023 + C026", "INDEPENDENTLY_CHECKED", x=0.0, y=1.0, ha="left")

        handles = [
            Line2D([], [], ls="", marker="o", color=OUTCOME["RECOVERED"]["color"], ms=3.5, label="recovered (run)"),
            Line2D([], [], ls="", marker="x", color=OUTCOME["DIED"]["color"], ms=4, mew=0.8, label="died (run)"),
            Line2D([], [], color=UNRESOLVED, lw=3, label="unresolved gap between the closest runs"),
            Patch(facecolor=OKABE_ITO["sky"], alpha=0.25, label="Lane 4 baseline envelope (T10 R13, 5 phases)"),
            Patch(facecolor="none", edgecolor=STATUS["NUMERICALLY_FRAGILE"]["color"], hatch="////", lw=0,
                  label="timestep-sensitive value (C027)"),
            Patch(facecolor=EDIT["removed"], label="mass removed"),
            Patch(facecolor=EDIT["added"], label="mass added"),
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=4, fontsize=6.3, handlelength=1.6,
                   columnspacing=1.2)

        outs = []
        for ext in ("png", "svg", "pdf"):
            p = OUT.with_suffix(f".{ext}")
            meta = {"png": {"Software": None}, "svg": {"Date": None}, "pdf": {"CreationDate": None}}[ext]
            fig.savefig(p, dpi=300 if ext == "png" else None, metadata=meta)
            outs.append(p)
        plt.close(fig)

    ep = HERE / "figure-A-edges.csv"
    with open(ep, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["intervention", "source", "condition", "phase", "survive_abs_dM", "die_abs_dM", "survive_run",
                    "die_run", "n_runs", "monotone"])
        for e in edges_:
            w.writerow([e.intervention, e.source, e.condition, e.phase, f"{e.survive_abs:.6f}", f"{e.die_abs:.6f}",
                        e.survive_run, e.die_run, e.n_runs, e.monotone])
    rp = HERE / "figure-A-runs.csv"
    with open(rp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "condition", "intervention", "phase", "strength", "dmass", "outcome", "run_id", "file"])
        for r in runs:
            w.writerow([r.source, r.condition, r.intervention, r.phase, r.strength, f"{r.dmass:.6f}", r.outcome,
                        r.run_id, str(pathlib.Path(r.file).relative_to(REPO))])
    outs += [ep, rp]
    inputs.append(L4 / "states/index.csv")
    inputs += [pathlib.Path(__file__).resolve(), *sorted((HERE.parent / "figlib").glob("*.py"))]  # code as data
    notes = [f"non-monotone groups: {len(bad)}"] + [f"{e.source} {e.condition} {e.intervention} p{e.phase}: "
                                                     f"{e.violations}" for e in bad]
    notes.append("off-axis runs in panel b (all listed in figure-A-runs.csv): "
                 + ", ".join(f"{k[0]} {k[1]}={v}" for k, v in sorted(off.items())))
    man = P.manifest("A-survival-boundary", inputs, outs,
                     ".venv/bin/python research/figures/A-survival-boundary/make_figure.py",
                     {"C023": "INDEPENDENTLY_CHECKED", "C026": "INDEPENDENTLY_CHECKED", "C027": "NUMERICALLY_FRAGILE"},
                     notes)
    P.write_manifest(HERE / "figure-A.provenance.json", man)
    for n in notes:
        print(n)
    return edges_


if __name__ == "__main__":
    build()
