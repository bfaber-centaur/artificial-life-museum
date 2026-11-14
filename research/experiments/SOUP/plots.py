"""Population chart, phylogeny and trait fan for a SOUP run (dark museum style).

  python plots.py <npz> <species.json> <out.png> [title]
  python plots.py compare <blend-stem> <dominant-stem> <diversity.jsonl> <out.png>   (G033)
  python plots.py replay <out.png>                                                  (G051)
"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from viz import PROJ

BG, FG, DIM = "#0b0d12", "#e8e6df", "#8a8f99"


def gcol(c):
    v = 0.5 + 0.5 * np.tanh(PROJ[:, :len(c)] @ (np.asarray(c) - 0.5))
    return tuple(0.15 + 0.85 * v)


def basis(npzs):
    """Principal axis of the mass-weighted genome cloud, pooled over snapshots of all runs given."""
    gs, as_ = [], []
    for p in npzs:
        d = np.load(p); A, G = d["A"], d["G"]
        sub = slice(None, None, max(1, len(A) // 40))
        a = A[sub].astype(np.float32).ravel(); g = (G[sub].astype(np.float32) / 255).transpose(1, 0, 2, 3).reshape(G.shape[1], -1)
        keep = a > 0.05; as_.append(a[keep]); gs.append(g[:, keep])
    a = np.concatenate(as_); g = np.concatenate(gs, 1)
    mu = (g * a).sum(1) / a.sum(); X = (g - mu[:, None]) * np.sqrt(a)
    return mu, np.linalg.svd(X @ X.T)[0][:, :2]


def fan(npz, bins=120, base=None, lims=None):
    d = np.load(npz)
    A, G = d["A"], d["G"]
    mu, u = base if base is not None else basis([npz])
    img = np.zeros((bins, len(A), 3))
    lo, hi = np.inf, -np.inf
    pcs = []
    for s in range(len(A)):
        aa = A[s].astype(np.float32).ravel(); k = aa > 0.05
        gg = G[s].astype(np.float32).reshape(G.shape[1], -1)[:, k] / 255
        p = u.T @ (gg - mu[:, None]); pcs.append((p, aa[k], gg))
        lo = min(lo, np.percentile(p[0], 0.5)); hi = max(hi, np.percentile(p[0], 99.5))
    if lims is not None:
        lo, hi = lims
    for s, (p, w, gg) in enumerate(pcs):
        b = np.clip(((p[0] - lo) / (hi - lo) * bins).astype(int), 0, bins - 1)
        h = np.bincount(b, weights=w, minlength=bins)
        col = np.stack([np.bincount(b, weights=w * c, minlength=bins) for c in (PROJ @ (gg - 0.5))])
        col = 0.5 + 0.5 * np.tanh(col / np.maximum(h, 1e-9))
        img[:, s] = (col * (h / h.max()) ** 0.5).T
    return img[::-1], (lo, hi)


def style(fig):
    for a in fig.axes:
        a.tick_params(colors=DIM)
        for sp_ in a.spines.values():
            sp_.set_color("#333")


def population(ax, spj, label):
    sp = json.load(open(spj)); T = np.array(sp["t"]) * 0.2; S = sp["species"]
    M = np.zeros((len(S), len(T)))
    for s in S:
        for k, v in s["mass"].items():
            M[s["id"], int(k)] = v
    order = np.argsort([s["born"] for s in S])
    ax.stackplot(T, M[order], colors=[gcol(S[i]["centroid"]) for i in order], linewidth=0)
    ax.set_xlim(T[0], T[-1]); ax.set_facecolor(BG)
    ax.set_title(label, color=FG, loc="left", fontsize=12)


def compare(blend, dom, div_jsonl, out):
    """G033: population and genome fan for one seed under both heredities, and spread for all seeds."""
    fig = plt.figure(figsize=(15, 10.5), facecolor=BG)
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.9], hspace=0.38, wspace=0.08)
    base = basis([blend + ".npz", dom + ".npz"])
    fans = [fan(p + ".npz", base=base) for p in (blend, dom)]
    lims = (min(f[1][0] for f in fans), max(f[1][1] for f in fans))
    for c, (p, lab) in enumerate(((blend, "Blending heredity"), (dom, "Particulate heredity"))):
        ax = fig.add_subplot(gs[0, c])
        population(ax, p + "_sp.json", f"{lab}: mass of each species (band colour = genome)")
        if c == 0:
            ax.set_ylabel("mass in bodies", color=FG)
        else:
            ax.set_yticklabels([])
        ax = fig.add_subplot(gs[1, c]); ax.set_facecolor(BG)
        img, _ = fan(p + ".npz", base=base, lims=lims)
        T = np.load(p + ".npz")["t"] * 0.2
        ax.imshow(img, aspect="auto", extent=(T[0], T[-1], lims[0], lims[1]), interpolation="nearest")
        ax.set_title("Genome over time: matter binned along the main genome axis", color=FG, loc="left", fontsize=12)
        if c == 0:
            ax.set_ylabel("genome axis 1", color=FG)
        else:
            ax.set_yticklabels([])
    ax = fig.add_subplot(gs[2, :]); ax.set_facecolor(BG)
    rows = {}
    for l in open(div_jsonl):
        r = json.loads(l); rows[r["name"]] = r
    for name, r in sorted(rows.items()):
        if r["rule"] != 16 or not name[:1] in "BD":
            continue
        col = "#c878ff" if r["inherit"] == "blend" else "#78e6c8"
        ax.plot(np.array(r["t"]) * 0.2, r["spread"], color=col, lw=1.6, alpha=0.9)
    ax.text(0.01, 0.92, "particulate (4 seeds)", color="#78e6c8", transform=ax.transAxes, ha="left", fontsize=11)
    ax.text(0.01, 0.08, "blending (4 seeds)", color="#c878ff", transform=ax.transAxes, ha="left", fontsize=11)
    ax.set_xlim(0, 2400)
    ax.set_xlabel("time (time units)", color=FG); ax.set_ylabel("genome spread", color=FG)
    ax.set_title("Genome diversity in every run: same four starting worlds, two kinds of heredity",
                 color=FG, loc="left", fontsize=12)
    style(fig)
    fig.savefig(out, dpi=110, facecolor=BG, bbox_inches="tight")


def main():
    npz, spj, out = sys.argv[1:4]
    title = sys.argv[4] if len(sys.argv) > 4 else ""
    sp = json.load(open(spj)); T = np.array(sp["t"]); S = sp["species"]; ns = len(T)
    M = np.zeros((len(S), ns))
    for s in S:
        for k, v in s["mass"].items():
            M[s["id"], int(k)] = v
    peak = M.max(1)
    fig = plt.figure(figsize=(14, 9), facecolor=BG)
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1.2, 1], hspace=0.28)
    tu = T * 0.2
    # 1. population: stacked masses, ordered by birth, coloured by genome
    ax = fig.add_subplot(gs[0]); ax.set_facecolor(BG)
    order = np.argsort([s["born"] for s in S])
    ax.stackplot(tu, M[order], colors=[gcol(S[i]["centroid"]) for i in order], linewidth=0)
    ax.set_xlim(tu[0], tu[-1]); ax.set_ylabel("mass in bodies", color=FG)
    ax.set_title("Population: every band is one species (colour = its genome)", color=FG, loc="left", fontsize=11)
    # 2. phylogeny
    ax = fig.add_subplot(gs[1]); ax.set_facecolor(BG)
    big = set(i for i in range(len(S)) if peak[i] >= 30)
    keep = set()
    for i in big:  # keep ancestors of big species
        j = i
        while j is not None and j not in keep:
            keep.add(j); j = S[j]["parent"]
    kids = {}
    for i in sorted(keep):
        kids.setdefault(S[i]["parent"], []).append(i)
    ys = {}; cnt = [0]
    def place(i):
        for c in sorted(kids.get(i, []), key=lambda c: S[c]["born"]):
            place(c)
        if i is not None:
            ys[i] = cnt[0]; cnt[0] += 1
    place(None)
    for i in keep:
        s = S[i]; y = ys[i]; c = gcol(s["centroid"])
        alive = M[i] > 0
        lw = 0.6 + 4 * np.sqrt(peak[i] / peak.max())
        ax.plot([tu[s["born"]], tu[s["last"]]], [y, y], color=c, lw=lw, solid_capstyle="butt", alpha=0.95)
        if s["parent"] is not None and s["parent"] in ys:
            ax.plot([tu[s["born"]]] * 2, [ys[s["parent"]], y], color=c, lw=0.6, alpha=0.6)
    ax.set_xlim(tu[0], tu[-1]); ax.set_yticks([])
    ax.set_title(f"Phylogeny: {len(keep)} lineages that reached mass 30 (of {len(S)} species founded); "
                 "line width = peak mass", color=FG, loc="left", fontsize=11)
    # 3. fan
    ax = fig.add_subplot(gs[2]); ax.set_facecolor(BG)
    img, (lo, hi) = fan(npz)
    ax.imshow(img, aspect="auto", extent=(tu[0], tu[-1], lo, hi), interpolation="nearest")
    ax.set_ylabel("genome axis 1", color=FG); ax.set_xlabel("time (tu)", color=FG)
    ax.set_title("Genome over time: matter binned by the main genome axis (brightness = mass)",
                 color=FG, loc="left", fontsize=11)
    for a in fig.axes:
        a.tick_params(colors=DIM)
        for sp_ in a.spines.values():
            sp_.set_color("#333")
    if title:
        fig.suptitle(title, color=FG, fontsize=14, x=0.125, ha="left")
    fig.savefig(out, dpi=110, facecolor=BG, bbox_inches="tight")


def replay(out):
    """G051: each C078 genome's first trial against six replays at new spots (500 tu, dominant)."""
    from pathlib import Path
    here = Path(__file__).parent
    first = {r["mutant"]: r for r in map(json.loads, open(here / "mutant.jsonl")) if r["mode"] == "dominant"}
    rep = [json.loads(l) for l in open(here / "replay.jsonl")]
    ks = sorted(first); T = rep[0]["every"] * (len(rep[0]["mutant_mass"]) - 1)
    R = {k: [r["mutant_mass"][-1] / r["mutant_mass"][0] for r in rep if r["mutant"] == k] for k in ks}
    o = {k: first[k]["mutant_mass"][T // first[k]["every"]] / first[k]["mutant_mass"][0] for k in ks}
    order = sorted(ks, key=lambda k: -np.median(R[k]))
    fl = 0.01
    GROW, SHRINK, FIRST = "#f0a040", "#7f8a9c", "#e8e6df"
    fig, ax = plt.subplots(figsize=(12, 5.4), facecolor=BG); ax.set_facecolor(BG)
    ax.axhline(1, color="#555", lw=1, zorder=1)
    for i, k in enumerate(order):
        v = np.maximum(R[k], fl); jit = np.linspace(-0.18, 0.18, len(v))
        ax.scatter(i + jit, v, s=60, c=[GROW if x > 1 else SHRINK for x in R[k]], edgecolors=BG, linewidths=1.5, zorder=3)
        ax.plot([i - 0.3, i + 0.3], [np.median(R[k])] * 2, color=FG, lw=2, zorder=2)
        ax.scatter([i + 0.38], [max(o[k], fl)], s=110, marker="D", facecolors="none", edgecolors=FIRST, linewidths=1.8, zorder=4)
    ax.set_yscale("log"); ax.set_ylim(fl * 0.8, 3)
    ax.set_yticks([0.01, 0.1, 0.5, 1, 2]); ax.set_yticklabels(["≤1 %", "×0.1", "×0.5", "×1", "×2"])
    ax.set_xticks(range(len(order))); ax.set_xticklabels([f"mutant {k}" for k in order], rotation=0, fontsize=9)
    ax.set_ylabel("mutant mass after 500 tu (vs. start)", color=FG)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], ls="", marker="o", ms=8, mfc=GROW, mec=BG, label="replay at a new spot: grew"),
         Line2D([], [], ls="", marker="o", ms=8, mfc=SHRINK, mec=BG, label="replay: shrank"),
         Line2D([], [], color=FG, lw=2, label="median of six replays"),
         Line2D([], [], ls="", marker="D", ms=9, mfc="none", mec=FIRST, mew=1.8, label="first trial (C078)")]
    leg = ax.legend(handles=h, loc="upper left", bbox_to_anchor=(0, -0.08), frameon=False, fontsize=10, ncol=4)
    for t in leg.get_texts():
        t.set_color(FG)
    ax.set_title("Twelve mutant genomes, each dropped in six new places. Sorted by how they did on replay.",
                 color=FG, loc="left", fontsize=12)
    style(fig)
    fig.savefig(out, dpi=110, facecolor=BG, bbox_inches="tight")


if __name__ == "__main__":
    if sys.argv[1] == "compare":
        compare(*sys.argv[2:6])
    elif sys.argv[1] == "replay":
        replay(sys.argv[2])
    else:
        main()
