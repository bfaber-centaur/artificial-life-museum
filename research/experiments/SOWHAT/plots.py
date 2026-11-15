"""SOWHAT charts.

  python plots.py drift OUT.png          (reads moran.jsonl; recomputes the 500 paths of drift.FATES)
  python plots.py atlas ATLAS.npz OUT.png (reads atlas.jsonl for the labels)
  python plots.py threshold OUT.png      (reads epidemic.jsonl and threshold.jsonl)
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import drift  # noqa: E402

HERE = Path(__file__).resolve().parent
OI = dict(orange="#E69F00", sky="#56B4E9", green="#009E73", blue="#0072B2",
          vermillion="#D55E00", purple="#CC79A7", grey="#9a9a9a", ink="#222222")
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#444", "axes.labelcolor": OI["ink"]})


def rows(name):
    return [json.loads(l) for l in (HERE / name).read_text().splitlines() if l.strip()]


def plot_drift(out):
    fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw=dict(width_ratios=[1.25, 1]))
    P = drift.fates_paths()
    fixed = P[-1] == 1
    g = np.arange(P.shape[0])
    for j in np.flatnonzero(~fixed):
        a.plot(g, P[:, j], color=OI["grey"], lw=0.6, alpha=0.5)
    for j in np.flatnonzero(fixed):
        a.plot(g, P[:, j], color=OI["vermillion"], lw=1.3)
    a.set_xlabel("generation")
    a.set_ylabel("share of the population carrying the mutant")
    f = drift.FATES
    a.set_title(f"500 copies of the same good mutation (+{f['s']:.0%} fitness, N = {f['N']})",
                loc="left", fontsize=11.5)
    a.text(0.98, 0.32, f"{fixed.sum()} take over\n{(~fixed).sum()} are lost,\n"
           f"{int((P[20] == 0).sum())} of them within\n20 generations",
           transform=a.transAxes, ha="right", va="top", color=OI["ink"])
    a.set_xlim(0, 800)
    a.set_ylim(0, 1.02)

    R = rows("moran.jsonl")
    for N, c in ((20, OI["orange"]), (200, OI["blue"])):
        rr = [r for r in R if r["N"] == N]
        s = np.array([r["s"] for r in rr])
        sim = np.array([r["sim"] for r in rr])
        se = np.array([r["se_exact"] for r in rr])
        ss = np.linspace(s.min(), s.max(), 300)
        b.plot(ss, [drift.moran_exact(N, x) for x in ss], color=c, lw=1.5,
               label=f"N = {N}: exact formula")
        keep = sim > 0  # 0 of 40,000 cannot be drawn on a log axis (N 200, s -0.05: exact 1.6e-7)
        s, sim, se = s[keep], sim[keep], se[keep]
        b.errorbar(s, sim, yerr=np.minimum(2 * se, 0.95 * sim), fmt="o", ms=5, color=c, mfc="white", mew=1.5,
                   label=f"N = {N}: simulated ({rr[0]['reps']:,} runs each)")
        b.axhline(1 / N, color=c, lw=0.8, ls=":")
    b.axvline(0, color="#bbb", lw=0.8)
    b.set_yscale("log")
    b.set_ylim(1e-5, 0.2)
    b.set_xlabel("selection coefficient s (negative = harmful)")
    b.set_ylabel("chance one new mutant takes over")
    b.set_title("Moran process: simulation vs exact answer", loc="left", fontsize=11.5)
    b.legend(frameon=False, fontsize=9, loc="lower right")
    b.text(-0.049, 0.011, "a harmful mutant (s = -0.05)\nin 20 still wins 3%", fontsize=9, color=OI["orange"])
    fig.tight_layout()
    fig.savefig(out, dpi=110)


def plot_atlas(npz, out):
    z = np.load(npz)
    v, F, k = z["v"], z["F"], z["k"]
    Fs, ks = np.unique(F), np.unique(k)
    n = v.shape[-1]
    lab = {(round(r["F"], 4), round(r["k"], 4)): r["kind"] for r in rows("atlas.jsonl")}
    fig, ax = plt.subplots(figsize=(10.5, 10.8), facecolor="#0b0b0f")
    big = np.full((len(Fs) * (n + 4), len(ks) * (n + 4)), np.nan)
    for i in range(v.shape[0]):
        r = len(Fs) - 1 - int(np.searchsorted(Fs, F[i]))
        c = int(np.searchsorted(ks, k[i]))
        big[r * (n + 4):r * (n + 4) + n, c * (n + 4):c * (n + 4) + n] = v[i]
    cmap = matplotlib.colormaps["magma"].copy()
    cmap.set_bad("#2a2a36")   # the gaps between worlds, so empty (black) worlds stay visible
    ax.imshow(np.ma.masked_invalid(big), cmap=cmap, vmin=0, vmax=0.45, interpolation="nearest")
    ax.set_xticks([c * (n + 4) + n / 2 for c in range(len(ks))], [f"{x:.4f}".rstrip("0") for x in ks],
                  color="#ddd", fontsize=9)
    ax.set_yticks([r * (n + 4) + n / 2 for r in range(len(Fs))],
                  [f"{x:.4f}".rstrip("0") for x in Fs[::-1]], color="#ddd", fontsize=9)
    ax.set_xlabel("kill rate k", color="#ddd")
    ax.set_ylabel("feed rate F", color="#ddd")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors="#888", length=0)
    fig.tight_layout()
    fig.savefig(out, dpi=100, facecolor="#0b0b0f")


def plot_threshold(out):
    fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.6))
    col = dict(mixed=OI["purple"], lattice=OI["sky"], shortcuts=OI["orange"])
    name = dict(mixed="well mixed", lattice="neighbours only", shortcuts="neighbours + 1% far")
    for r in rows("epidemic.jsonl"):
        y = np.array(r["infected"])
        a.plot(np.arange(y.size), 100 * y, color=col[r["world"]], lw=1, alpha=0.8,
               label=name[r["world"]] if r["seed"] == 0 else None)
    a.set_xlabel("time step")
    a.set_ylabel("% of people sick at once")
    a.set_title("Same disease, three contact patterns (10 runs each)", loc="left", fontsize=11.5)
    a.legend(frameon=False)
    a.set_xlim(0, 700)
    T = rows("threshold.jsonl")
    for w in ("mixed", "lattice", "shortcuts"):
        bs = sorted({r["beta"] for r in T})
        for x in bs:
            ys = [100 * r["final_size"] for r in T if r["world"] == w and r["beta"] == x]
            b.scatter([x] * len(ys), ys, s=16, color=col[w], alpha=0.8)
        med = [np.median([r["final_size"] for r in T if r["world"] == w and r["beta"] == x]) for x in bs]
        b.plot(bs, 100 * np.array(med), color=col[w], lw=1.5, label=name[w])
    b.set_xlabel("chance one contact passes it on (beta)")
    b.set_ylabel("% of people ever sick")
    b.set_title("When does it take off? (5 runs per dot column)", loc="left", fontsize=11.5)
    b.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(out, dpi=110)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "drift":
        plot_drift(sys.argv[2])
    elif cmd == "atlas":
        plot_atlas(sys.argv[2], sys.argv[3])
    elif cmd == "threshold":
        plot_threshold(sys.argv[2])
