"""Make field.png: candidate gallery and the glider/circler coexistence map."""
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gallery import crop  # noqa: E402
from tables import code  # noqa: E402

fin = {}
d = np.load(HERE / "persist-T10-R13.npz")["final"]
for i, k in enumerate(["S001 Orbium\nS001 rule", "S101 pair\nS001 rule", "O4i cells\nS001 rule",
                       "Orbium\ncoex rule", "S102 circler\ncoex rule", "S103 static\ncoex rule"]):
    fin[k] = d[i]

fig = plt.figure(figsize=(12, 6.5))
gs = fig.add_gridspec(2, 6, height_ratios=[1, 1.7])
for j, (k, A) in enumerate(fin.items()):
    ax = fig.add_subplot(gs[0, j])
    ax.imshow(crop(A.astype(float), 22), cmap="magma", vmin=0, vmax=1, interpolation="nearest")
    ax.set_title(k, fontsize=8)
    ax.axis("off")

classes = {".": 0, "#": 1, "G": 2, "C": 3, "S": 4, "?": 5}
cmap = ListedColormap(["#222222", "#bbbbbb", "#2b7bba", "#d9534f", "#5cb85c", "#f0ad4e"])
for n, (name, title) in enumerate([("bistab-T10-R13.csv", "T=10, R=13"), ("bistab-T10-R26.csv", "T=10, R=26"),
                                   ("bistab-T40-R13.csv", "T=40, R=13")]):
    rows = list(csv.DictReader(open(HERE / name)))
    sg = sorted({float(r["sigma"]) for r in rows})
    labels, grid = [], []
    for seed in ("orbium", "gyrator", "OG2g"):
        for m in sorted({r["mu"] for r in rows}, key=float):
            cs = {float(r["sigma"]): code(r) for r in rows if r["seed"] == seed and r["mu"] == m}
            grid.append([classes[cs[s]] for s in sg])
            labels.append(f"{seed} μ={m}")
    ax = fig.add_subplot(gs[1, 2 * n : 2 * n + 2])
    ax.imshow(np.array(grid), cmap=cmap, vmin=0, vmax=5, aspect="auto", interpolation="nearest")
    ax.set_xticks(range(len(sg)), [f"{s * 1e3:.1f}" for s in sg], fontsize=6, rotation=90)
    ax.set_yticks(range(len(labels)), labels if n == 0 else [""] * len(labels), fontsize=6)
    ax.set_xlabel("σ ×10³", fontsize=7)
    ax.set_title(f"phenotype after 500–1000 tu, {title}", fontsize=8)
handles = [plt.Rectangle((0, 0), 1, 1, color=cmap(i)) for i in range(6)]
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.legend(handles, ["died", "filled", "glider", "circler", "static", "other"], loc="lower center",
           fontsize=8, ncol=6)
fig.savefig(HERE / "field.png", dpi=110)
print("wrote field.png")


def previews():
    """research/specimens/S10x-*/preview.png: seed, settled state at T10/R13 and at R26."""
    from alm import specimens

    root = HERE.parents[1] / "specimens"
    r13 = np.load(HERE / "persist-T10-R13.npz")["final"]
    r26 = np.load(HERE / "persist-T10-R26.npz")["final"]
    t40 = np.load(HERE / "persist-T40-R13.npz")["final"]
    for sid, slug, k in (("S101", "orbium-pair", 1), ("S102", "circler", 4), ("S103", "static-ring", 5)):
        s = specimens.load(sid)
        fig, axs = plt.subplots(1, 4, figsize=(8, 2.3))
        panels = [(s.place(64), "seed (levels/255)", 22), (r13[k], "500 tu, T10 R13", 22),
                  (t40[k], "500 tu, T40 R13", 22), (r26[k], "500 tu, T10 R26", 44)]
        for ax, (A, t, h) in zip(axs, panels):
            ax.imshow(crop(A.astype(float), h), cmap="magma", vmin=0, vmax=1, interpolation="nearest")
            ax.set_title(t, fontsize=8)
            ax.axis("off")
        fig.suptitle(f"{sid}: {s.name}", fontsize=9)
        fig.tight_layout()
        fig.savefig(root / f"{sid}-{slug}" / "preview.png", dpi=100)
        plt.close(fig)


previews()
