"""Figure C: several phenotypes under one rule. Single-lane evidence (Lane 6, PR #11).

Claims illustrated: C038 (glider, circler and static ring under one rule), C039 (the circler
fails at R = 26 at its own rule: REFUTED as worded; only the bilinearly resized seed dies),
C047 (block, nearest and cubic seeds circle at R 26 and 39), C048 (S103 block-scaled to R 26), C040 (no glider/circler switching under disturbance), C042
(S103 is an exact fixed point), C043 (all three are catalogued species), C044 (the Orbium
μ × σ neighbourhood). Statuses are read from research/claims.md (figlib.ledger), and the build
stops if they no longer match EXPECTED.

Resolution and resize method are kept apart. All of Lane 6's R 26 runs start from bilinearly
resized seeds (ndimage.zoom order=1). The R 26 death at the circler's own rule is a resize
effect (C047: Lane 3, with a matching Lane 6 rerun), so it is not drawn as a resolution effect. The R 26 band shift in
panel b was measured only from bilinear seeds, and the figure says so.

Evidence is Lane 6's PR #11, read with `git show` (figlib.gitsource) at the commit that merged
it into main, so the figure names exactly which revision of the data it plotted. Runs no
simulation.

The phenotype labels re-apply Lane 6's own classifier (tables.py: net speed > 0.2 R/tu
glider; net < 0.1 and path > 0.2 circler; path < 0.02 static; fate died/filled otherwise)
to the recorded speeds. The stale `outcome` column of switch-T10-R13.csv ("ROTATOR") is
not used, following Lane 6's own correction note.

Usage (from the repo root):
  .venv/bin/python research/figures/C-phenotypes-one-rule/make_figure.py
"""
import csv
import pathlib
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figlib import ledger as L  # noqa: E402
from figlib import provenance as P  # noqa: E402
from figlib.gitsource import Pinned  # noqa: E402
from figlib.style import (GRID, INK, MUTED, OKABE_ITO, OUTCOME, PHENOTYPE, STATUS,  # noqa: E402
                          figure_style, status_badge)

OUT = HERE / "figure-C"
PR11 = "f72db9ef9584fffc10af0fcbbc6491c8f22a6d9c"  # merge of PR #11 into main (its data equals the f40f303 head Figure C was first drawn from)
D6 = "research/experiments/L6-field"
L6_D2 = ("7a4ea3b963fbfc3c952fadb2eb25193f4b1be207",  # merge of PR #23: Lane 6 field.py rerun of the four resizes
         "research/experiments/L6-007-attractor-geography/d2-resize.csv")
L3_002 = "56ae4210a225a9dc0c7d38cee9c833b48096307f"  # merge of PR #18 (Lane 3) into main; same blobs as its 4998d03 head
L3_RESIZE = "research/experiments/L3-002-property-persistence/s102_resize_check.txt"
L3_LABELS = "research/traces/lane3/L3-002/labels.csv"
COEX = (0.155, 0.020)  # registered rule of S102 and S103
S001_RULE = (0.150, 0.015)

EXPECTED = {
    "C038": "REPRODUCED",
    "C039": "REFUTED",
    "C040": "OBSERVED",
    "C042": "REPRODUCED",
    "C043": "OBSERVED",
    "C044": "OBSERVED",
    "C047": "INDEPENDENTLY_CHECKED",  # for the eight seeds tested only
    "C048": "OBSERVED",
}
NUMERICS = [("T10 R13", "bistab-T10-R13.csv", "1000 tu"), ("T10 R26", "bistab-T10-R26.csv", "500 tu"),
            ("T40 R13", "bistab-T40-R13.csv", "500 tu")]
SEEDS = [("orbium", "Orbium cells"), ("gyrator", "S102 seed"), ("OG2g", "catalog OG2g cells")]


def phenotype(r):
    """Lane 6's motion class (tables.py), from recorded fate and speeds."""
    if r["fate"] != "localized":
        return r["fate"]
    net, path = float(r["speed"]), float(r["path_speed"])
    if net > 0.2:
        return "GLIDER"
    if net < 0.1 and path > 0.2:
        return "CIRCLER"
    if path < 0.02:
        return "STATIC"
    return "OTHER"


def mark(ax, x, y, ph, s=16, z=3):
    st = PHENOTYPE[ph]
    size = s * st.get("size", 1.0) * (0.6 if ph == "died" else 1.0)
    ax.scatter([x], [y], s=size, marker=st["marker"], color=st["color"], linewidths=0, zorder=z)


# ---------------------------------------------------------------- panels

def panel_map(ax, src, rows_out):
    """a: L6-001, 441 rules seeded with Orbium cells (T10 R13, 500 tu)."""
    rows = src.csv(f"{D6}/musigma-T10.csv")
    for r in rows:
        ph = phenotype(r)
        mu, sg = float(r["mu"]), float(r["sigma"])
        mark(ax, sg, mu, ph, s=13)
        rows_out.append(["a", "L6-001 musigma-T10.csv", "orbium", mu, sg, "T10 R13", ph, r["mass_mean"],
                         r["speed"], r["path_speed"]])
    # zoom box of panel b (σ range sampled there, μ 0.150–0.160)
    ax.add_patch(Rectangle((0.0177, 0.1475), 0.0258 - 0.0177, 0.015, fill=False, ec=INK, lw=0.7, ls=(0, (3, 2)),
                           zorder=4))
    ax.text(0.0258, 0.1635, "panel b", fontsize=5.8, ha="right", va="bottom", color=INK)
    for (mu, sg), lab, dx in ((S001_RULE, "S001 rule", -0.0007), (COEX, "coexistence rule", -0.0007)):
        ax.scatter([sg], [mu], s=70, facecolors="none", edgecolors=INK, linewidths=0.8, zorder=5)
    ax.annotate("S001 rule", (0.015, 0.150), xytext=(0.0105, 0.139), fontsize=6, arrowprops=dict(arrowstyle="-",
                lw=0.5, color=INK), ha="center")
    ax.annotate("coexistence rule\n(S102, S103)", (0.020, 0.155), xytext=(0.0255, 0.178), fontsize=6,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=INK), ha="center", bbox=dict(fc="white", ec="none", pad=1))
    ax.annotate("circler, then fills the\nworld at ≈ 850 tu (transient)", (0.018, 0.135), xytext=(0.0245, 0.118),
                fontsize=5.8, arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED), ha="center", color=MUTED,
                bbox=dict(fc="white", ec="none", pad=1))
    ax.annotate("circler ≥ 2000 tu (= OG2g)", (0.022, 0.155), xytext=(0.0255, 0.196), fontsize=5.8,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED), ha="center", color=MUTED)
    ax.set_xlim(0.0073, 0.0287)
    ax.set_ylim(0.0965, 0.2035)
    ax.set_xlabel("σ (growth width)")
    ax.set_ylabel("μ (growth centre)")
    ax.set_xticks(np.arange(0.008, 0.0281, 0.004))
    ax.set_yticks(np.arange(0.10, 0.201, 0.02))
    ax.set_title("Orbium cells in 441 rules (T10 R13, 500 tu): a grid of samples, one run each",
                 fontsize=6.6, loc="left")
    counts = {}
    for r in rows:
        counts[phenotype(r)] = counts.get(phenotype(r), 0) + 1
    ax.text(0.012, 0.975, "Of 441 rules: " + ", ".join(f"{counts.get(k, 0)} {PHENOTYPE[k]['label']}" for k in
                                     ("GLIDER", "CIRCLER", "STATIC", "died", "filled")),
            transform=ax.transAxes, ha="left", va="top", fontsize=6, color=INK,
            bbox=dict(fc="white", ec=GRID, pad=2, lw=0.5), zorder=6)


NUM_LABEL = {"T10 R13": "T10 R13 (base)", "T10 R26": "R 26 (bilinear seed)", "T40 R13": "T 40: step 4× finer"}


def panel_strips(axs, src, rows_out, status):
    """b: L6-004 σ strips. One axis per μ; for each seed, the base run directly above its
    resolution (R 26) and timestep (T 40) re-runs, so shifts read vertically."""
    data = {}
    for num, fname, _ in NUMERICS:
        for r in src.csv(f"{D6}/{fname}"):
            data[num, r["seed"], float(r["mu"]), float(r["sigma"])] = r
    step = 0.0005
    for ax, mu in zip(axs, (0.150, 0.155)):
        y, yt, yl, ycol = 0, [], [], []
        for seed, lab in SEEDS:
            for num, fname, horizon in NUMERICS:
                yt.append(y)
                yl.append(f"{lab} · {NUM_LABEL[num]}")
                ycol.append(num)
                for (n, sd, m, sg), r in data.items():
                    if (n, sd, m) == (num, seed, mu):
                        ph = phenotype(r)
                        mark(ax, sg, y, ph, s=20)
                        rows_out.append(["b", f"L6-004 {fname}", seed, mu, sg, num, ph, r["mass_mean"], r["speed"],
                                         r["path_speed"]])
                if (num, seed) == ("T10 R26", "gyrator") and mu == COEX[0]:
                    ax.scatter([COEX[1]], [y], s=120, facecolors="none", edgecolors=OKABE_ITO["vermillion"],
                               linewidths=1.0, zorder=5)
                    ax.annotate("bilinear seed dies;\nother resizes circle\n(C039 refuted, C047)",
                                (COEX[1], y), xytext=(0.0236, y),
                                fontsize=5.8, color=OKABE_ITO["vermillion"], fontweight="bold", va="center",
                                arrowprops=dict(arrowstyle="-", lw=0.6, color=OKABE_ITO["vermillion"]),
                                bbox=dict(fc="white", ec="none", pad=1), zorder=6)
                y -= 1
            y -= 0.6
        # coexistence rows: σ where Orbium cells glide AND the S102 seed circles, per numerics
        y -= 0.2
        for num, _, _ in NUMERICS:
            yt.append(y)
            yl.append(f"glider + circler coexist · {NUM_LABEL[num]}")
            ycol.append(num)
            sigmas = sorted({sg for (n, sd, m, sg) in data if n == num and m == mu})
            for sg in sigmas:
                g = data.get((num, "orbium", mu, sg))
                c = data.get((num, "gyrator", mu, sg))
                if g and c and phenotype(g) == "GLIDER" and phenotype(c) == "CIRCLER":
                    ax.add_patch(Rectangle((sg - step * 0.45, y - 0.4), step * 0.9, 0.8, facecolor="none",
                                           edgecolor=STATUS["NUMERICALLY_FRAGILE"]["color"], hatch="////", lw=0.9,
                                           zorder=2))
                else:
                    ax.plot([sg], [y], marker="|", ms=4, mew=0.8, color="#a8a8a8", ls="", zorder=1)
            y -= 1
        ax.axvline(COEX[1], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=0)
        ax.set_xlim(0.0176, 0.0259)
        ax.set_ylim(y + 0.4, 0.7)
        ax.set_yticks(yt, yl if ax is axs[0] else [""] * len(yl), fontsize=5.8)
        if ax is axs[0]:
            for t, num in zip(ax.get_yticklabels(), ycol):
                if num == "T10 R26":
                    t.set_fontweight("bold")
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_xticks([0.018, 0.019, 0.020, 0.021, 0.022, 0.023, 0.024, 0.025])
        ax.xaxis.set_major_formatter(lambda v, _: f"{v:.3f}")
        ax.tick_params(axis="x", labelsize=5.8)
        ax.grid(axis="x", color=GRID, lw=0.4, zorder=0)
        ax.set_xlabel("σ")
        ax.set_title(f"μ = {mu:.3f}" + ("  (the coexistence rule's μ)" if mu == COEX[0] else ""), fontsize=7,
                     loc="left", pad=11)
    for (n, sd, m, sg), r in sorted(data.items()):  # μ 0.160 (T10 R13 only): kept in the data CSV, not drawn
        if m not in (0.150, 0.155):
            rows_out.append(["b (not drawn)", f"L6-004 {dict((x[0], x[1]) for x in NUMERICS)[n]}", sd, m, sg, n,
                             phenotype(r), r["mass_mean"], r["speed"], r["path_speed"]])
    status_badge(axs[0], "C038", status["C038"], x=0.0, y=1.0, ha="left", short=True, in_layout=False)
    status_badge(axs[1], "C039", status["C039"], x=0.0, y=1.0, ha="left", short=True, in_layout=False)
    status_badge(axs[1], "C047", status["C047"], x=1.0, y=1.0, ha="right", short=True, in_layout=False)


EVIDENCE_COLS = [
    ("T10 R13", "persist"), ("R 26,\nbilinear seed", "T10 R26"), ("R 26, block /\nnearest / cubic", "resize"),
    ("T40 R13", "persist"),
    ("clean rerun", "rerun"), ("returns after\nI001 attenuation", "return"),
    ("second lane\nreproduces", "second"), ("catalog\nidentity", "catalog"),
]
GROUPS = [("persistence at the coexistence rule", 0, 4), ("same lane, stronger tests", 4, 6),
          ("independent", 6, 8)]
SPECIMENS = [("orbium", "glider (Orbium cells)", "GLIDER", None), ("gyrator", "circler S102", "CIRCLER", "S102"),
             ("static", "static ring S103", "STATIC", "S103")]
PASS, FAIL, CHANGED, NONE, UNTESTED = "pass", "fail", "changed", "none", "untested"
CELL_BG = {PASS: "#e3f1ec", FAIL: "#f8e1d5", CHANGED: "#fbefd4", NONE: "#eeeeee", UNTESTED: "#ffffff"}


def evidence(src, ledger_claims, rows_out, l6d2, l3):
    """The evidence matrix. Every cell cites where its value comes from."""
    cells = {}
    # R 26 from other seed resizes (C047, C048): Lane 3, and Lane 6's field.py rerun (PR #23)
    d2 = [r for r in l6d2.csv(L6_D2[1])]
    l3txt = l3.text(L3_RESIZE)
    for r in d2:
        alive = r["class_1000tu"] == "CIRCLER"
        l3line = next(l for l in l3txt.splitlines() if l.startswith(f"({r['R']}, '{r['method']}'"))
        assert ("alive" in l3line) == alive, (r, l3line)  # both engines agree on every resize
        rows_out.append(["c", "L6-007 d2-resize.csv @ 7a4ea3b", f"gyrator ({r['method']})", COEX[0], COEX[1],
                         f"T10 R{r['R']}", r["class_1000tu"] if alive else "died", r["mass_last100"],
                         r["net_speed"], r["path_speed"]])
    others = [r for r in d2 if r["method"] != "bilinear"]
    assert others and all(r["class_1000tu"] == "CIRCLER" for r in others)
    cells["gyrator", "resize"] = (PASS, "circler, all 3,\nR 26 and 39\n(Lane 3; Lane 6\nrerun matches)")
    cells["orbium", "resize"] = (UNTESTED, "not run")
    lab = {r["property"]: r for r in l3.csv(L3_LABELS) if r["specimen"] == "S103"}
    assert lab["fixed_point"]["R26"] == "False"
    cells["static", "resize"] = (CHANGED, f"static, block seed\nm {float(lab['mass']['R26']):.3f}, ≠ seed\n"
                                          f"(Lane 3, C048)")
    rows_out.append(["c", "L3-002 labels.csv @ 56ae421", "static (block)", COEX[0], COEX[1], "T10 R26", "STATIC",
                     lab["mass"]["R26"], "", ""])
    for num in ("T10 R13", "T40 R13", "T10 R26"):
        fname = f"persist-{num.replace(' ', '-')}.csv"
        rows = {r["seed"]: r for r in src.csv(f"{D6}/{fname}")
                if (float(r["mu"]), float(r["sigma"])) == COEX}
        for seed, _, ph0, _ in SPECIMENS:
            r = rows[seed]
            ph = phenotype(r)
            m = float(r["mass_mean"])
            if ph == ph0:
                cells[seed, num] = (PASS, f"{ph.lower()}\nm {m:.3f}")
            elif ph == "died":
                cells[seed, num] = (FAIL, "died")
            else:
                cells[seed, num] = (CHANGED, f"→ {ph.lower()}\nm {m:.3f}")
            rows_out.append(["c", f"L6-006 {fname}", seed, COEX[0], COEX[1], num, ph, r["mass_mean"], r["speed"],
                             r["path_speed"]])
    # clean-process reruns: trace directories in PR #11 (bitwise second process per the L6 README table)
    cells["orbium", "clean rerun"] = (UNTESTED, "no trace at\nthis rule")
    readme = src.text(f"{D6}/README.md")
    for seed, run in (("gyrator", "S102-5bfac8f95f"), ("static", "S103-1d8c158cdd")):
        src.text(f"research/traces/{run}/summary.json")  # the trace exists at the pinned commit
        line = next(l for l in readme.splitlines() if f"`{run}`" in l and "final sha256" in l)
        assert "| identical |" in line, line  # Lane 6's table: second process, same config
        cells[seed, "clean rerun"] = (PASS, "bitwise\n" + run.replace("-", "-\n"))
    # recovery after I001 (both phases keep the phenotype), from L6-005; S103 from its dossier table
    sw = src.csv(f"{D6}/switch-T10-R13.csv")
    for seed, case in (("orbium", "orb@coex"), ("gyrator", "gyr@coex")):
        ph0 = dict((s[0], s[2]) for s in SPECIMENS)[seed]
        best, first_fail = 0.0, None
        for s in sorted({float(r["s"]) for r in sw if r["case"] == case and r["intervention"] == "I001"}):
            rs = [r for r in sw if r["case"] == case and r["intervention"] == "I001" and float(r["s"]) == s]
            ok = all(phenotype(r) == ph0 for r in rs)
            for r in rs:
                rows_out.append(["c", "L6-005 switch-T10-R13.csv", seed, COEX[0], COEX[1], f"I001 s={s} t0={r['t0']}",
                                 phenotype(r), r["mass_mean"], r["speed"], r["path_speed"]])
            if ok and s > 0:
                best = s
            if not ok and s > 0:
                first_fail = (s, sum(phenotype(r) == ph0 for r in rs), len(rs))
                break
        if best > 0:
            cells[seed, "return"] = (PASS, f"≤ {best:.0%}\n(2 phases)")
        else:
            s, k, n = first_fail
            cells[seed, "return"] = (FAIL, f"at {s:.0%}: kept in\n{k} of {n} phases")
    dossier = src.text("research/specimens/S103-static-ring.md")
    assert "I001 attenuation 0.05–0.20 | returns **bitwise**" in dossier
    cells["static", "return"] = (PASS, "bitwise, ≤ 20%\n(1 phase,\ndossier)")
    # second lane: read from the ledger's own status text for C038 / C042
    for seed, cid in (("orbium", "C038"), ("gyrator", "C038"), ("static", "C042")):
        txt = ledger_claims[cid]["status_text"]
        cells[seed, "second"] = (NONE, "not yet") if "not yet reproduced by a second lane" in txt else (PASS, "yes")
    for seed, name in (("orbium", "Orbium"), ("gyrator", "OG2g"), ("static", "C0la")):
        cells[seed, "catalog"] = (NONE, name)
    return cells


def panel_matrix(ax, cells, status):
    """c: what each phenotype's evidence is, separated into persistence and stronger tests."""
    ncol, nrow = len(EVIDENCE_COLS), len(SPECIMENS)
    for j, (head, key) in enumerate(EVIDENCE_COLS):
        ax.text(j + 0.5, nrow + 0.08, head, ha="center", va="bottom", fontsize=6.0, color=INK)
        for i, (seed, label, _, _) in enumerate(SPECIMENS):
            y = nrow - 1 - i
            k = head if key in ("persist", "rerun") and head in ("T10 R13", "T40 R13", "clean rerun") else key
            if key == "rerun":
                k = "clean rerun"
            kind, txt = cells[seed, k]
            hatch = "////" if kind == CHANGED else None
            ax.add_patch(Rectangle((j + 0.04, y + 0.06), 0.92, 0.88, facecolor=CELL_BG[kind], edgecolor=GRID,
                                   hatch=hatch, lw=0.5))
            col = {PASS: INK, FAIL: OUTCOME["DIED"]["color"], CHANGED: "#8a5a00", NONE: MUTED, UNTESTED: MUTED}[kind]
            ax.text(j + 0.5, y + 0.5, txt, ha="center", va="center", fontsize=5.8, color=col,
                    fontweight="bold" if kind in (FAIL, CHANGED) else "normal", linespacing=1.15)
    for i, (seed, label, ph, _) in enumerate(SPECIMENS):
        y = nrow - 1 - i + 0.5
        ax.text(-0.12, y, label, ha="right", va="center", fontsize=6.4, color=INK)
        mark(ax, -0.05, y, ph, s=22)
    for title, a, b in GROUPS:
        ax.plot([a + 0.06, b - 0.06], [nrow + 0.62, nrow + 0.62], color=INK, lw=0.6)
        ax.text((a + b) / 2, nrow + 0.68, title, ha="center", va="bottom", fontsize=6.0, color=INK, fontweight="bold")
    # every claim this panel draws on, statuses as read from the ledger
    x = -2.0
    for cid in ("C038", "C039", "C040", "C042", "C043", "C048", "C047"):
        t = status_badge(ax, cid, status[cid], x=x, y=nrow + 1.12, ha="left", short=True, in_layout=False)
        t.set_transform(ax.transData)
        x += 1.42
    ax.set_xlim(-2.0, ncol)
    ax.set_ylim(-0.05, nrow + 1.15)
    ax.axis("off")


def build():
    src = Pinned(PR11, "PR #11 (Lane 6), merged to main")
    l6d2 = Pinned(L6_D2[0], "PR #23 (Lane 6 L6-007 D2 rerun), merged to main")
    l3 = Pinned(L3_002, "PR #18 (Lane 3 L3-002), merged to main")
    led = L.snapshot(EXPECTED)
    status = {cid: c["status"] for cid, c in led["claims"].items()}
    rows_out = []
    cells = evidence(src, led["claims"], rows_out, l6d2, l3)
    with figure_style():
        fig = plt.figure(figsize=(7.2, 9.6), layout="constrained")
        fig.suptitle("Figure C. Several phenotypes under one rule: what is observed, and how far it is checked",
                     x=0.005, ha="left", fontsize=9, fontweight="bold")
        sf = fig.subfigures(3, 1, height_ratios=[2.5, 3.6, 1.75], hspace=0.02)
        sf[0].text(0.005, 0.975, f"ONE LANE: evidence from Lane 6 (PR #11, merged @ {src.commit[:7]}); "
                   f"no second-lane reproduction of the coexistence yet.\nClaim statuses checked against "
                   f"research/claims.md @ {led['ledger_commit']} (C039 refuted, D2).",
                   transform=sf[0].transSubfigure, ha="left", va="top", fontsize=6.2, color=OKABE_ITO["vermillion"],
                   fontweight="bold")
        axa = sf[0].subplots(1, 1)
        panel_map(axa, src, rows_out)
        sf[0].suptitle(" \n ", fontsize=6.2)  # reserves the two lines used by the one-lane banner
        sf[0].supylabel(" ", fontsize=2)
        status_badge(axa, "C044", status["C044"], x=1.0, y=1.005, short=True)

        axb = sf[1].subplots(1, 2, sharex=True)
        panel_strips(axb, src, rows_out, status)
        sf[1].suptitle("b   Timestep and resolution checks: the coexistence band moves. Every R 26 row starts "
                       "from a bilinearly resized seed",
                       x=0.005, ha="left", fontsize=7.3,
                       fontweight="bold")

        axc = sf[2].subplots(1, 1)
        panel_matrix(axc, cells, status)
        sf[2].suptitle("c   At the coexistence rule (μ 0.155, σ 0.020): persistence is not the same as a "
                       "verified attractor", x=0.005, ha="left", fontsize=7.3, fontweight="bold")

        phs = ["GLIDER", "CIRCLER", "STATIC", "died", "filled"]
        handles = [Line2D([], [], ls="", marker=PHENOTYPE[k]["marker"], color=PHENOTYPE[k]["color"],
                          ms=4.5 * PHENOTYPE[k].get("size", 1) ** 0.5 if k != "died" else 5, label=PHENOTYPE[k]["label"])
                   for k in phs]
        handles += [Rectangle((0, 0), 1, 1, facecolor="none", edgecolor=STATUS["NUMERICALLY_FRAGILE"]["color"],
                              hatch="////", label="glider + circler coexist (σ location moves with the numerics)"),
                    Line2D([], [], color=MUTED, lw=0.6, ls=(0, (2, 2)), label="σ = 0.020 (coexistence rule)"),
                    Line2D([], [], ls="", marker="|", ms=5, mew=0.8, color="#a8a8a8",
                           label="sampled σ without coexistence")]
        fig.legend(handles=handles, loc="outside lower center", ncol=4, fontsize=6.3, handlelength=1.6,
                   columnspacing=1.2)
        axa.set_title("a   Orbium cells in 441 rules (T10 R13, 500 tu): every marker is one run; no interpolation",
                      fontsize=7.3, loc="left", fontweight="bold")

        outs = []
        for ext in ("png", "svg", "pdf"):
            p = OUT.with_suffix(f".{ext}")
            meta = {"png": {"Software": None}, "svg": {"Date": None}, "pdf": {"CreationDate": None}}[ext]
            fig.savefig(p, dpi=300 if ext == "png" else None, metadata=meta)
            outs.append(p)
        plt.close(fig)

    dp = HERE / "figure-C-data.csv"
    with open(dp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["panel", "source", "seed", "mu", "sigma", "condition", "phenotype", "mass_mean", "speed",
                    "path_speed"])
        w.writerows(rows_out)
    mp = HERE / "figure-C-matrix.csv"
    with open(mp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["specimen", "column", "verdict", "text"])
        for (seed, col), (kind, txt) in sorted(cells.items()):
            w.writerow([seed, col, kind, txt.replace("\n", " ")])
    outs += [dp, mp]
    inputs = [pathlib.Path(__file__).resolve(), *sorted((HERE.parent / "figlib").glob("*.py"))]
    man = P.manifest("C-phenotypes-one-rule", inputs, outs,
                     ".venv/bin/python research/figures/C-phenotypes-one-rule/make_figure.py", led,
                     ["Single-lane evidence: Lane 6 data read at the PR #11 merge commit; see pinned_inputs.",
                      "Resize evidence (C047, C048) read at the PR #23 (Lane 6) and PR #18 (Lane 3) merge commits.",
                      "Phenotypes recomputed with Lane 6's tables.py classifier; switch CSV 'outcome' column unused."],
                     pinned_inputs=src.manifest() + l6d2.manifest() + l3.manifest())
    P.write_manifest(HERE / "figure-C.provenance.json", man)


if __name__ == "__main__":
    build()
