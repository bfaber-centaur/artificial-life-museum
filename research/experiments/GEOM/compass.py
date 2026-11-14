"""G040: the lattice is the compass. Final S001 headings after 8000 steps vs start rotation, on
the square grid (H001-X1, R 13), the hex lattice and an amorphous glass (GEOM heading.py).

Each rose draws one spoke per run at its last-window heading (bright), plus the spoke's images
under the lattice's symmetry group (faint: D4 for square, D6 for hex; none for glass), so a
locked lattice shows a star of a few directions and an unlocked world a fan.

Usage:  python compass.py   -> research/gallery/exhibits/G040-lattice-compass/
"""
import csv
import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = REPO / "research" / "gallery" / "exhibits" / "G040-lattice-compass"
SRC = {"square": HERE.parent / "H001-lattice-wobble" / "x1_R13.csv",
       "hex": HERE / "heading_hex.csv", "glass": HERE / "heading_glass.csv"}
SIGN = {"square": -1, "hex": 1, "glass": 1}  # direction of the start rotation (see summarize.py)
GROUP = {"square": 4, "hex": 6, "glass": 0}
BG, FG = "#0b0b0f", "#e8e8e8"


def load(name):
    rows = []
    for r in csv.DictReader(open(SRC[name])):
        rows.append((float(r["rot"]), int(r["alive"]), float(r["heading_w7"])))
    return sorted(rows)


def lattice_points(name):
    if name == "square":
        y, x = np.mgrid[-3:4, -3:4]
        return x.ravel(), y.ravel()
    if name == "hex":
        j, i = np.mgrid[-4:5, -4:5]
        x = (i + 0.5 * (j % 2))
        y = j * np.sqrt(3) / 2
        return x.ravel(), y.ravel()
    import geomlenia as g
    w = g.glass_torus(16, 0, n_iter=120)
    xy = w.xy - 8
    k = np.hypot(xy[:, 0], xy[:, 1]) < 3.6
    return xy[k, 0], xy[k, 1]


def main():
    import sys
    sys.path.insert(0, str(HERE))
    OUT.mkdir(parents=True, exist_ok=True)
    names = [n for n in ("square", "hex", "glass") if SRC[n].exists()]
    fig = plt.figure(figsize=(4.2 * len(names), 4.9), facecolor=BG)
    summary = {}
    for k, name in enumerate(names):
        rows = load(name)
        ax = fig.add_subplot(1, len(names), k + 1, projection="polar", facecolor=BG)
        ax.set_ylim(0, 1.05)
        ax.set_yticks([])
        ax.set_xticks(np.radians(np.arange(0, 360, 30)))
        ax.set_xticklabels([f"{a}°" for a in range(0, 360, 30)], color="#777", fontsize=7)
        ax.grid(color="#2a2a33", lw=0.6)
        ax.spines["polar"].set_color("#2a2a33")
        alive = [r for r in rows if r[1]]
        dead = [r for r in rows if not r[1]]
        n = GROUP[name]
        for rot, _, h in alive:
            if n:
                for m in range(n):
                    for sgn in (1, -1):
                        a = np.radians(sgn * h + 360 * m / n)
                        ax.plot([a, a], [0.15, 1.0], color="#f8b33c", lw=0.6, alpha=0.18)
            a = np.radians(h)
            ax.plot([a, a], [0.15, 1.0], color="#fcffa4", lw=1.3, alpha=0.9)
        # start directions (what an isotropic world would keep)
        for rot, _, h in rows:
            a = np.radians(68.198 + SIGN[name] * rot)
            ax.plot([a], [1.03], marker="o", ms=2.2, color="#8c8cff", alpha=0.8)
        hs = sorted(h for _, _, h in alive)
        distinct = []
        for h in hs:
            if distinct and h - distinct[-1][-1] < 0.15:
                distinct[-1].append(h)
            else:
                distinct.append([h])
        summary[name] = {"runs": len(rows), "alive": len(alive), "dead": len(dead),
                         "distinct_final_headings_0.15deg": len(distinct)}
        title = {"square": "square grid", "hex": "hex lattice", "glass": "amorphous glass"}[name]
        ax.set_title(f"{title}\n{len(alive)} of {len(rows)} runs alive, "
                     f"{len(distinct)} distinct final headings", color=FG, fontsize=10, pad=14)
        # lattice inset
        ins = fig.add_axes([0.01 + k / len(names), 0.07, 0.055 * 3 / len(names), 0.13])
        x, y = lattice_points(name)
        ins.scatter(x, y, s=3, c="#9a9aa8")
        ins.set_aspect("equal")
        ins.axis("off")
    fig.text(0.5, 0.94, "Where Orbium ends up heading after 800 tu, from 46 / 31 / 16 start angles (R 13)",
             color=FG, ha="center", fontsize=11)
    fig.text(0.5, 0.012, "bright spokes: final heading of each run · faint: the same headings "
             "under the lattice's rotations and mirrors · blue dots: start headings",
             color="#999", ha="center", fontsize=8)
    fig.subplots_adjust(top=0.78, bottom=0.12, left=0.03, right=0.97, wspace=0.35)
    fig.savefig(OUT / "compass.png", dpi=160, facecolor=BG)
    prov = {"exhibit": "G040", "title": "The lattice is the compass", "media": ["compass.png"],
            "claim": "C087", "sources": {k: str(v.relative_to(REPO)) for k, v in SRC.items()},
            "summary": summary,
            "view": "polar plot of the heading of the centroid velocity over steps 7000-8000; "
                    "this is a chart, not a photograph",
            "command": "PYTHONPATH=src .venv/bin/python research/experiments/GEOM/compass.py"}
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
