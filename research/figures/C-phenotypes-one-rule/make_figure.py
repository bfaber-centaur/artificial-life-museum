"""Figure C: several phenotypes under one rule. PROVISIONAL, built from unmerged PR #11.

Claims illustrated: C038 (glider, circler and static ring under one rule), C039 (the circler
fails at R = 26 at its own rule), C040 (no glider/circler switching under disturbance), C042
(S103 is an exact fixed point), C043 (all three are catalogued species), C044 (the Orbium
μ × σ neighbourhood). Statuses are read from research/claims.md (figlib.ledger), and the
build stops if they no longer match EXPECTED.

Evidence is Lane 6's PR #11, read at a pinned commit with `git show` (figlib.gitsource).
Nothing from that PR is copied into this branch. If the commit is missing locally, run
`git fetch origin claude/night0-field-tmbx06` first. Runs no simulation.

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
PR11 = "f40f303e7a9a71be7cb1ff8038372540f358d53d"  # PR #11 head when Figure C was drawn
D6 = "research/experiments/L6-field"
COEX = (0.155, 0.020)  # registered rule of S102 and S103
S001_RULE = (0.150, 0.015)

EXPECTED = {
    "C038": "REPRODUCED",
    "C039": "NUMERICALLY_FRAGILE",
    "C040": "OBSERVED",
    "C042": "REPRODUCED",
    "C043": "OBSERVED",
    "C044": "OBSERVED",
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


def panel_strips(axs, src, rows_out, status):
    """b: L6-004 σ strips at three numerical settings, three seeds per μ."""
    for ax, (num, fname, horizon) in zip(axs, NUMERICS):
        rows = src.csv(f"{D6}/{fname}")
        have = {float(r["mu"]) for r in rows}
        mus = [0.150, 0.155, 0.160]  # same rows in every panel; a μ not run is labelled, not left out
        y = 0
        yt, yl = [], []
        sig_all = sorted({float(r["sigma"]) for r in rows})
        step = 0.0005
        for mu in mus:
            ys = {}
            if mu not in have:
                for seed, lab in SEEDS:
                    yt.append(y)
                    yl.append(f"μ {mu:.3f} · {lab}")
                    y -= 1
                ax.text(0.0217, y + 2, f"μ {mu:.3f} not run at {num}", ha="center", va="center", fontsize=6,
                        color=MUTED, style="italic")
                y -= 0.8
                continue
            for seed, lab in SEEDS:
                ys[seed] = y
                yt.append(y)
                yl.append(f"μ {mu:.3f} · {lab}")
                for r in rows:
                    if r["seed"] == seed and float(r["mu"]) == mu:
                        ph = phenotype(r)
                        mark(ax, float(r["sigma"]), y, ph, s=20)
                        rows_out.append(["b", f"L6-004 {fname}", seed, mu, float(r["sigma"]), num, ph,
                                         r["mass_mean"], r["speed"], r["path_speed"]])
                y -= 1
            # coexistence: σ samples where Orbium cells glide AND the S102 seed circles at this μ
            by = {(r["seed"], float(r["sigma"])): phenotype(r) for r in rows if float(r["mu"]) == mu}
            for sg in sig_all:
                if by.get(("orbium", sg)) == "GLIDER" and by.get(("gyrator", sg)) == "CIRCLER":
                    ax.add_patch(Rectangle((sg - step * 0.45, ys["gyrator"] - 0.45), step * 0.9,
                                           ys["orbium"] - ys["gyrator"] + 0.9, facecolor="none",
                                           edgecolor=STATUS["NUMERICALLY_FRAGILE"]["color"], hatch="////",
                                           lw=0.9, zorder=1))
            y -= 0.8
        ax.axvline(COEX[1], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=0)
        ax.set_xlim(0.0176, 0.0259)
        ax.set_ylim(y + 0.5, 0.8)
        ax.set_yticks(yt, yl if ax is axs[0] else [""] * len(yl), fontsize=5.8)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_xticks([0.018, 0.020, 0.022, 0.024])
        ax.xaxis.set_major_formatter(lambda v, _: f"{v:.3f}")
        ax.grid(axis="x", color=GRID, lw=0.4, zorder=0)
        ax.set_xlabel("σ")
        ax.set_title(f"{num}  ({horizon})", fontsize=7, loc="left", pad=11)
        if num == "T10 R26":
            status_badge(ax, "C039", status["C039"], x=0.0, y=1.0, ha="left", short=True, in_layout=False)
    status_badge(axs[0], "C038", status["C038"], x=0.0, y=1.0, ha="left", short=True, in_layout=False)


EVIDENCE_COLS = [
    ("T10 R13", "persist"), ("T40 R13", "persist"), ("T10 R26", "persist"),
    ("clean rerun", "rerun"), ("returns after\nI001 attenuation", "return"),
    ("second lane\nreproduces", "second"), ("catalog\nidentity", "catalog"),
]
GROUPS = [("persistence at the coexistence rule (one lane)", 0, 3), ("same lane, stronger tests", 3, 5),
          ("independent", 5, 7)]
SPECIMENS = [("orbium", "glider (Orbium cells)", "GLIDER", None), ("gyrator", "circler S102", "CIRCLER", "S102"),
             ("static", "static ring S103", "STATIC", "S103")]
PASS, FAIL, CHANGED, NONE, UNTESTED = "pass", "fail", "changed", "none", "untested"
CELL_BG = {PASS: "#e3f1ec", FAIL: "#f8e1d5", CHANGED: "#fbefd4", NONE: "#eeeeee", UNTESTED: "#ffffff"}


def evidence(src, ledger_claims, rows_out):
    """The evidence matrix. Every cell cites where its value comes from."""
    cells = {}
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
        cells[seed, "clean rerun"] = (PASS, f"bitwise\n{run}")
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
    cells["static", "return"] = (PASS, "bitwise, ≤ 20%\n(1 phase, dossier)")
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
            k = head if key in ("persist", "rerun") and head in ("T10 R13", "T40 R13", "T10 R26", "clean rerun") else key
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
    for cid in ("C038", "C039", "C040", "C042", "C043"):
        t = status_badge(ax, cid, status[cid], x=x, y=nrow + 1.12, ha="left", short=True, in_layout=False)
        t.set_transform(ax.transData)
        x += 1.55
    ax.set_xlim(-2.0, ncol)
    ax.set_ylim(-0.05, nrow + 1.15)
    ax.axis("off")


def build():
    src = Pinned(PR11, "PR #11 (Lane 6), unmerged")
    led = L.snapshot(EXPECTED)
    status = {cid: c["status"] for cid, c in led["claims"].items()}
    rows_out = []
    cells = evidence(src, led["claims"], rows_out)
    with figure_style():
        fig = plt.figure(figsize=(7.2, 9.0), layout="constrained")
        fig.suptitle("Figure C. Several phenotypes under one rule: what is observed, and how far it is checked",
                     x=0.005, ha="left", fontsize=9, fontweight="bold")
        sf = fig.subfigures(3, 1, height_ratios=[2.7, 3.2, 1.75], hspace=0.02)
        sf[0].text(0.005, 0.975, f"PROVISIONAL: evidence from Lane 6's unmerged PR #11 @ {PR11[:7]}; one lane, "
                   f"no second-lane reproduction yet.\nClaim statuses checked against research/claims.md @ "
                   f"{led['ledger_commit']}.",
                   transform=sf[0].transSubfigure, ha="left", va="top", fontsize=6.2, color=OKABE_ITO["vermillion"],
                   fontweight="bold")
        axa = sf[0].subplots(1, 1)
        panel_map(axa, src, rows_out)
        sf[0].suptitle(" \n ", fontsize=6.2)  # reserves the two lines used by the provisional banner
        sf[0].supylabel(" ", fontsize=2)
        status_badge(axa, "C044", status["C044"], x=1.0, y=1.005, short=True)

        axb = sf[1].subplots(1, 3, sharex=True)
        panel_strips(axb, src, rows_out, status)
        sf[1].suptitle("b   Near the coexistence rule: three seeds on a σ strip, at three numerical settings",
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
                              hatch="////", label="glider + circler coexist (location shifts with T, R)"),
                    Line2D([], [], color=MUTED, lw=0.6, ls=(0, (2, 2)), label="σ = 0.020 (coexistence rule)")]
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
                     ["PROVISIONAL: evidence read from unmerged PR #11 at the pinned commit; see pinned_inputs.",
                      "Phenotypes recomputed with Lane 6's tables.py classifier; switch CSV 'outcome' column unused."],
                     pinned_inputs=src.manifest())
    P.write_manifest(HERE / "figure-C.provenance.json", man)


if __name__ == "__main__":
    build()
