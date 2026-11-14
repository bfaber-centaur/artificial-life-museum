"""Population chart, phylogeny and trait fan for a SOUP run (dark museum style).

  python plots.py <npz> <species.json> <out.png> [title]
  python plots.py compare <blend-stem> <dominant-stem> <diversity.jsonl> <out.png>   (G033)
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


if __name__ == "__main__":
    if sys.argv[1] == "compare":
        compare(*sys.argv[2:6])
    else:
        main()
