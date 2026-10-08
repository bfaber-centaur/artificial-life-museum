"""Figure D: when together is worse, and the creature that eventually disappears. PROVISIONAL.

(a, b) S101, the bound Orbium pair, under port injury (I004) and frontal mass addition (I003):
every run of Lane 6's L6-008, next to the same partners run alone (L6-008's split baseline) and,
for I003, alone with the full pulse (Lane 7's HR-009 E2 control). (c, d) S102, the circler: the
lifetimes of 37 starts at its registered rule (Lane 6's L6-007 follow-up and HR-009 E1), drawn as
individual lifelines and as a Kaplan-Meier survival estimate with censoring at 5000 tu.

Evidence is read with `git show` at pinned commits (figlib.gitsource): PRs #27, #29 and #30 at their merge commits on main:
Lane 6's PR #27 and Lane 7's PR #30. Nothing is copied into this branch. The new findings are
proposed claims (L6-c, L6-d, L6-f), not ledger entries, so the figure prints no status for them.
Ledger statuses are drawn only for the claims already recorded (C038, C041). Runs no simulation.

Usage (from the repo root):
  git fetch origin claude/night0-field-tmbx06 claude/night0-hostile-review-o3avnq
  .venv/bin/python research/figures/D-pair-and-circler/make_figure.py
"""
import csv
import math
import pathlib
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figlib import ledger as L  # noqa: E402
from figlib import provenance as P  # noqa: E402
from figlib.gitsource import Pinned  # noqa: E402
from figlib.style import GRID, INK, MUTED, OKABE_ITO, figure_style, status_badge  # noqa: E402

OUT = HERE / "figure-D"
PR27 = "7cbf5aedcb8111973c6cffdb4c6bcf5b34f4ae0e"  # Lane 6, L6-007/L6-008: PR #27 merge commit on main
PR30 = "0b9b47f8d7c48847219441cd15152792adbd45de"  # Lane 7, HR-009: PR #30 merge commit on main
PR29 = "20bdff9f3827290cff6646fae6bc8f283e5aa373"  # Lane 3, L3-003: PR #29 merge commit on main; cited for the refinement caveat only
L3_003 = "research/experiments/L3-003-circler-lifetime/README.md"
L8 = "research/experiments/L6-008-pair-coupling/pair-coupling.csv"
L7 = "research/experiments/L6-007-attractor-geography/circler-lifetimes.csv"
E1 = "research/experiments/HR009-l6-review/e1.csv"
E2 = "research/experiments/HR009-l6-review/e2.csv"
HORIZON = 5000.0  # tu; both lifetime studies stop here

EXPECTED = {"C038": "REPRODUCED", "C041": "OBSERVED"}

# survivors: 2 Orbia, 1 Orbium, none, other (non-Orbium body or filled torus)
COUNT_FILL = {"2": OKABE_ITO["blue"], "1": "#9cc8e6", "0": "#f4f4f4", "o": "#d0d0d0"}
COUNT_INK = {"2": "white", "1": INK, "0": MUTED, "o": INK}
DRAG = OKABE_ITO["vermillion"]


def _count(v):
    return "o" if v == "other" else str(int(v))


# ---------------------------------------------------------------- data

def pair_runs(src):
    rows = [r for r in src.csv(L8) if r["disturbance"] in ("I003", "I004")]
    for r in rows:
        r["s"] = float(r["s"])
        r["phase"] = int(r["phase"])
        r["pair"] = _count(r["n_pair"])
        r["split"] = str(int(r["n_port"]) + int(r["n_starboard"]))
    return rows


def full_pulse(src):
    """HR-009 E2: each undisturbed half given the whole I003 pulse; survivors per (s, phase)."""
    out = {}
    for r in src.csv(E2):
        k = (float(r["s"]), int(r["phase"]))
        out[k] = out.get(k, 0) + int(r["n_full"])
    return {k: str(v) for k, v in out.items()}


def lifetimes(l6, l7):
    """One record per start: source, perturbation, lifetime (tu) and whether it died."""
    runs = []
    for r in l6.csv(L7):
        dead = r["death_tu"] != ""
        eps = float(r["eps"])
        runs.append(dict(source="L6" if eps > 0 else "seed", pert=f"ε {eps:g}" if eps > 0 else "none",
                         t=float(r["death_tu"]) if dead else HORIZON, dead=dead))
    ref = None
    for r in l7.csv(E1):
        if r["rep"] == "-1":  # HR-009's rerun of the unperturbed seed: same trajectory, not a new start
            ref = float(r["death_tu"])
            continue
        dead = r["death_tu"] != ""
        runs.append(dict(source="HR009", pert=f"δ {float(r['delta']):.0e}".replace("e-", "e−"),
                         t=float(r["death_tu"]) if dead else HORIZON, dead=dead))
    return runs, ref


def kaplan_meier(runs):
    """Product-limit estimate with Greenwood 95% bands (log-log). Steps only at observed deaths."""
    times = sorted({r["t"] for r in runs if r["dead"]})
    n_at = lambda t: sum(r["t"] >= t for r in runs)
    s, var, out = 1.0, 0.0, [(0.0, 1.0, 1.0, 1.0)]
    for t in times:
        d, n = sum(r["dead"] and r["t"] == t for r in runs), n_at(t)
        s *= 1 - d / n
        var += d / (n * (n - d)) if n > d else 0.0
        if 0 < s < 1:
            se = math.sqrt(var) / abs(math.log(s))
            lo, hi = s ** math.exp(1.96 * se), s ** math.exp(-1.96 * se)
        else:
            lo = hi = s
        out.append((t, s, lo, hi))
    return out


def km_at(km, t):
    return [row for row in km if row[0] <= t][-1]


# ---------------------------------------------------------------- panels

def tile_panel(ax, runs, dist, svals, blocks, full=None):
    """Rows: for each block (pair, partners alone, ...) the five phases; columns: strengths s."""
    sel = {(r["s"], r["phase"]): r for r in runs if r["disturbance"] == dist}
    y, yt, yl = 0, [], []
    for name, key in blocks:
        for ph in range(5):
            for j, s in enumerate(svals):
                r = sel[s, ph]
                v = full[s, ph] if key == "full" else r[key]
                ax.add_patch(Rectangle((j + 0.06, -y - 0.94), 0.88, 0.88, facecolor=COUNT_FILL[v], edgecolor="none",
                                       hatch="////" if v == "o" else None, lw=0))
                ax.text(j + 0.5, -y - 0.5, v, ha="center", va="center", fontsize=5.6, color=COUNT_INK[v])
                if key == "pair" and r["mismatch"] == "True":
                    drag = r["direction"] == "drag-down"
                    ax.add_patch(Rectangle((j + 0.06, -y - 0.94), 0.88, 0.88, fill=False,
                                           edgecolor=DRAG if drag else INK, lw=1.3 if drag else 0.7,
                                           ls="-" if drag else (0, (2, 1.5)), zorder=4))
            y += 1
        yt.append(-y + 2.5)
        yl.append(name)
        y += 0.5
    ax.set_xlim(-0.05, len(svals) + 0.05)
    ax.set_ylim(-y + 0.4, 0.1)
    ax.set_xticks(np.arange(len(svals)) + 0.5, [f"{s:g}" for s in svals])
    ax.set_yticks(yt, yl, fontsize=6.2)
    ax.tick_params(axis="both", length=0)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_visible(False)
    return y


def panel_a(ax, runs):
    svals = sorted({r["s"] for r in runs if r["disturbance"] == "I004"})
    tile_panel(ax, runs, "I004", svals, [("bound pair", "pair"), ("partners alone\n(split baseline)", "split")])
    ax.set_xlabel("port-injury strength s (fraction of the port partner's mass removed)")
    n = sum(1 for r in runs if r["disturbance"] == "I004")
    m = sum(1 for r in runs if r["disturbance"] == "I004" and r["mismatch"] == "True")
    ax.text(0.0, -0.36, f"Pair = partners alone in {n - m} of {n} runs: the uninjured partner survives on its own "
            f"(L6-008 I004: H0). The 2 dashed mismatches at s 0.05 are\nthe split half being fragile; a lone, "
            f"relaxed Orbium survives 0.05 (Lane 4, L4-002).", transform=ax.transAxes, fontsize=6, color=INK,
            va="top")


def panel_b(ax, runs, full):
    svals = sorted({r["s"] for r in runs if r["disturbance"] == "I003"})
    y = tile_panel(ax, runs, "I003", svals, [("bound pair", "pair"), ("partners alone,\ntheir share of pulse\n(L6-008)", "split"),
                                             ("partners alone,\nfull pulse\n(HR-009 E2)", "full")], full=full)
    j = {s: i for i, s in enumerate(svals)}
    ax.add_patch(Rectangle((j[0.2], -y + 0.4), 2, y - 0.3, facecolor="none", edgecolor=MUTED, hatch="\\\\",
                           lw=0, alpha=0.35, zorder=0))
    ax.add_patch(Rectangle((j[0.5], -y + 0.4), len(svals) - j[0.5], y - 0.3, facecolor="white", alpha=0.62,
                           edgecolor="none", zorder=5))
    top = 0.35
    ax.text(j[0.2] + 1, top, "withdrawn: a 128²\nworld-size effect", ha="center", va="bottom", fontsize=6,
            color=DRAG, fontweight="bold")
    ax.text(j[0.4] + 0.5, top, "explained by\nexposure", ha="center", va="bottom", fontsize=6, color=MUTED)
    ax.text((j[0.5] + len(svals)) / 2, top, "not interpreted: no baseline brackets the pair\n"
            "(apparent rescues and filled tori)", ha="center", va="bottom", fontsize=6, color=MUTED)
    ax.set_xlabel("frontal-addition strength s (Gaussian pulse ahead of the pair)")


def panel_c(ax, runs, ref):
    order = [("seed", "unperturbed seed"), ("L6", "Lane 6: ε noise on support"),
             ("HR009", "Lane 7: δ ≪ ε (HR-009 E1)")]
    col = {"seed": INK, "L6": OKABE_ITO["purple"], "HR009": OKABE_ITO["sky"]}
    y, yt, yl = 0, [], []
    for src, lab in order:
        grp = sorted([r for r in runs if r["source"] == src], key=lambda r: (not r["dead"], r["t"]))
        y0 = y
        for r in grp:
            ax.plot([0, r["t"]], [y, y], color=col[src], lw=1.2 if src == "seed" else 0.9, solid_capstyle="butt")
            if r["dead"]:
                ax.plot([r["t"]], [y], marker="x", ms=3.6, mew=1.0, color=DRAG, ls="")
            else:
                ax.plot([r["t"]], [y], marker=">", ms=3.0, color=col[src], ls="")
            y += 1
        yt.append((y0 + y - 1) / 2)
        yl.append(f"{lab}\n{sum(r['dead'] for r in grp)} of {len(grp)} died")
        y += 1.2
    ax.axvline(HORIZON, color=MUTED, lw=0.6, ls=(0, (2, 2)))
    seed = next(r for r in runs if r["source"] == "seed")
    ax.annotate(f"one floating-point trajectory:\ndies at {seed['t']:g} tu (HR-009 rerun: {ref:g})",
                (seed["t"], 0), xytext=(250, -0.9), fontsize=5.8, color=INK, va="bottom",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
    ax.set_ylim(y - 0.6, -3.6)
    ax.set_xlim(0, HORIZON * 1.03)
    ax.set_yticks(yt, yl, fontsize=6.0)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("time (tu)")


def panel_d(ax, runs):
    km = kaplan_meier(runs)
    t = [r[0] for r in km] + [HORIZON]
    s = [r[1] for r in km] + [km[-1][1]]
    lo = [r[2] for r in km] + [km[-1][2]]
    hi = [r[3] for r in km] + [km[-1][3]]
    ax.fill_between(t, lo, hi, step="post", color=OKABE_ITO["purple"], alpha=0.16, lw=0)
    ax.step(t, s, where="post", color=OKABE_ITO["purple"], lw=1.3)
    ax.plot([r["t"] for r in runs if r["dead"]], [0.015] * sum(r["dead"] for r in runs), ls="", marker="|", ms=5,
            mew=0.7, color=DRAG)
    n_cens = sum(not r["dead"] for r in runs)
    for tq in (1000.0, 4999.9):
        _, sv, l, h = km_at(km, tq)
        ax.plot([tq], [sv], marker="o", ms=3, color=OKABE_ITO["purple"])
        early = tq < 3000
        ax.text(tq + 60 if early else tq - 60, sv + 0.02 if early else sv - 0.18,
                f"{sv:.2f} alive at {round(tq):d} tu\n(95% CI {l:.2f}–{h:.2f})", fontsize=5.8,
                color=INK, va="bottom", ha="left" if early else "right")
    ax.axvline(HORIZON, color=MUTED, lw=0.6, ls=(0, (2, 2)))
    ax.set_xlim(0, HORIZON * 1.03)
    ax.set_ylim(0, 1.04)
    ax.set_xlabel("time (tu)")
    ax.set_ylabel("fraction of starts still circling")
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.text(0.02, 0.06, f"{len(runs)} starts: {sum(r['dead'] for r in runs)} deaths (red ticks), {n_cens} still "
            "circling at 5000 tu,\nwhere both studies stop (censored). No curve past 5000 tu.",
            transform=ax.transAxes, fontsize=5.8, color=MUTED)
    return km


# ---------------------------------------------------------------- build

def build():
    l6 = Pinned(PR27, "PR #27 (Lane 6, L6-007/L6-008), merged to main")
    l7 = Pinned(PR30, "PR #30 (Lane 7, HR-009), merged to main")
    l3 = Pinned(PR29, "PR #29 (Lane 3, L3-003), merged to main")
    l3.text(L3_003)  # not plotted: logged so the caveat names exactly what it rests on
    l6.text("research/experiments/L6-008-pair-coupling/README.md")  # L6-009 world-size note, cited for panel b
    l7.text("research/reports/hostile-review.md")  # HR-009c withdrawal, cited for panel b
    led = L.snapshot(EXPECTED)
    status = {cid: c["status"] for cid, c in led["claims"].items()}
    runs = pair_runs(l6)
    full = full_pulse(l7)
    life, ref = lifetimes(l6, l7)

    with figure_style():
        fig = plt.figure(figsize=(7.2, 8.6), layout="constrained")
        fig.suptitle("Figure D. A withdrawn 'together is worse', and a circler that disappears only at R 13, T 10",
                     x=0.005, ha="left", fontsize=9, fontweight="bold")
        sf = fig.subfigures(2, 1, height_ratios=[5.0, 2.9], hspace=0.03)
        sf[0].text(0.005, 0.985, f"PROVISIONAL exhibit: evidence from merged PRs #27 (Lane 6, main @ {PR27[:7]}), #29 and #30 (Lane 7, HR-009). "
                   f"\nThe new findings are proposed claims, not ledger entries. Ledger statuses (C038, C041) "
                   f"checked against research/claims.md @ {led['ledger_commit']}.",
                   transform=sf[0].transSubfigure, ha="left", va="top", fontsize=6.2, color=OKABE_ITO["vermillion"],
                   fontweight="bold")
        sf[0].suptitle(" \n ", fontsize=6.2)
        axa, axb = sf[0].subplots(2, 1, height_ratios=[10.5, 16])
        panel_a(axa, runs)
        panel_b(axb, runs, full)
        axa.set_title("a   S101 under port injury (I004): an ordinary response (cells: Orbia alive at the end)", loc="left", fontsize=7.3, fontweight="bold", pad=4)
        axb.set_title("b   S101 under frontal addition (I003): the 'worse together' window is withdrawn",
                      loc="left", fontsize=7.3, fontweight="bold", pad=56)
        axb.annotate(f"WITHDRAWN. Lane 7's HR-009c (PR #30, main @ {PR30[:7]}) with Lane 6's L6-009: the on-gap pulse splits the pair "
                     "into two\nintact Orbia. On the 128² torus they later collide; zero-padded to 256², all 10 s 0.2–0.3 "
                     "states end as two Orbia.\nThe red-outlined runs are a world-size effect, not coupling. Only an "
                     "off-gap s 0.3 result (L6-009, exploratory) remains open.", xy=(0, 1), xycoords="axes fraction",
                     xytext=(0, 25), textcoords="offset points", ha="left", va="bottom", fontsize=6.2,
                     color=OKABE_ITO["vermillion"], fontweight="bold")
        status_badge(axa, "C041", status["C041"], x=1.0, y=1.0, short=True, in_layout=False)

        axc, axd = sf[1].subplots(1, 2, width_ratios=[1.15, 1])
        panel_c(axc, life, ref)
        km = panel_d(axd, life)
        sf[1].suptitle("c, d   S102 at its registered rule (R 13, T 10 only): a chaotic transient, not one death time"
                       "\n \n \n ", x=0.005, ha="left", fontsize=7.3, fontweight="bold")
        sf[1].text(0.005, 0.925, f"R 13, T 10 ONLY. Lane 3 (PR #29, main @ {PR29[:7]}) reproduces these deaths at R 13, T 10, but "
                   "no copy ends when either knob is refined:\n0 of 29 runs at R 26 and 0 of 3 at R 39 (T 10); 0 of 24 "
                   "at T 20 and 0 of 24 at T 40 (R 13), to 8000 tu. The collapse is\nan effect of the R 13, T 10 "
                   "discretisation, not a lifetime of the rule. Refined runs are censored, not shown to be attractors.",
                   transform=sf[1].transSubfigure, ha="left", va="top", fontsize=6.2, color=OKABE_ITO["vermillion"],
                   fontweight="bold")
        status_badge(axd, "C038", status["C038"], x=1.0, y=1.0, short=True, in_layout=False)

        handles = [Patch(facecolor=COUNT_FILL[k], edgecolor=GRID, hatch="////" if k == "o" else None, label=lab)
                   for k, lab in (("2", "2 Orbia"), ("1", "1 Orbium"), ("0", "none"), ("o", "other body / filled"))]
        handles += [Patch(facecolor="none", edgecolor=DRAG, lw=1.3, label="pair < partners alone (drag-down)"),
                    Patch(facecolor="none", edgecolor=INK, lw=0.7, ls=(0, (2, 1.5)), label="other pair ≠ partners"),
                    Line2D([], [], color=DRAG, marker="x", ls="", ms=4, label="circler died"),
                    Line2D([], [], color=MUTED, marker=">", ls="", ms=4, label="alive at 5000 tu")]
        fig.legend(handles=handles, loc="outside lower center", ncol=4, fontsize=6.2, handlelength=1.4,
                   columnspacing=1.0)

        outs = []
        for ext in ("png", "svg", "pdf"):
            p = OUT.with_suffix(f".{ext}")
            meta = {"png": {"Software": None}, "svg": {"Date": None}, "pdf": {"CreationDate": None}}[ext]
            fig.savefig(p, dpi=300 if ext == "png" else None, metadata=meta)
            outs.append(p)
        plt.close(fig)

    dp = HERE / "figure-D-pair.csv"
    with open(dp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["disturbance", "s", "phase", "pair", "partners_alone_split", "partners_alone_full_pulse",
                    "mismatch", "direction"])
        for r in sorted(runs, key=lambda r: (r["disturbance"], r["s"], r["phase"])):
            w.writerow([r["disturbance"], r["s"], r["phase"], r["pair"], r["split"],
                        full.get((r["s"], r["phase"]), "") if r["disturbance"] == "I003" else "", r["mismatch"],
                        r["direction"]])
    lp = HERE / "figure-D-lifetimes.csv"
    with open(lp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "perturbation", "time_tu", "died"])
        for r in life:
            w.writerow([r["source"], r["pert"], r["t"], r["dead"]])
        w.writerow([])
        w.writerow(["km_time_tu", "km_survival", "ci95_lo", "ci95_hi"])
        for row in km:
            w.writerow([f"{v:.6g}" for v in row])
    outs += [dp, lp]
    inputs = [pathlib.Path(__file__).resolve(), *sorted((HERE.parent / "figlib").glob("*.py"))]
    man = P.manifest("D-pair-and-circler", inputs, outs,
                     ".venv/bin/python research/figures/D-pair-and-circler/make_figure.py", led,
                     ["PROVISIONAL: evidence read from merged PRs #27, #29 and #30 at their merge commits; see pinned_inputs.",
                      "Proposed claims L6-c, L6-d, L6-f are not in the ledger; no status is drawn for them.",
                      "Kaplan-Meier with Greenwood log-log 95% band; HR-009's rerun of the unperturbed seed is not "
                      "counted as a separate start.",
                      "Panels c-d are R 13, T 10 only; PR #29 (L3-003) sees no end at R 26, R 39, T 20 or T 40, so the "
                      "collapse is a discretisation effect. L3-003 is cited, not plotted.",
                      "Panel b's s 0.2-0.3 window is withdrawn: HR-009c (PR #30) and L6-009 (PR #27 L6-008 README) show the "
                      "on-gap pulse frees two Orbia that collide only on 128². Cited, not plotted."],
                     pinned_inputs=l6.manifest() + l7.manifest() + l3.manifest())
    P.write_manifest(HERE / "figure-D.provenance.json", man)


if __name__ == "__main__":
    build()
