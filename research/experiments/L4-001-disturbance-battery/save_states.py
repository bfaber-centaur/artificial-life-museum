#!/usr/bin/env python3
"""Protocol step 8: save before/during/after states and traces for representative runs.

For each intervention at phase t0 = 1000: the coarse strengths on either side of the
transition and the two bisection bracket ends. Also renders states/gallery.png.
"""
import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402

OUT = os.path.join(HERE, "states")
T0 = 1000


def main():
    with open(os.path.join(HERE, "results", "bisect-brackets.csv")) as f:
        br = {b["intervention"]: b for b in csv.DictReader(f) if int(b["t0"]) == T0}
    picks = []
    for iv, b in sorted(br.items()):
        lo, hi = float(b["s_ok"]), float(b["s_fail"])
        grid = run.GRIDS[iv]
        c_ok = max(s for s in grid if s <= lo)
        c_fail = min(s for s in grid if s >= hi)
        picks += [(iv, c_ok), (iv, lo), (iv, hi), (iv, c_fail)]
    picks = list(dict.fromkeys(picks))
    rows = []
    for iv, s in picks:
        rows.append(run.run(iv, s, T0, save=OUT))
    run.write_rows(os.path.join(OUT, "index.csv"), rows)

    # gallery: bracket ends only (s_ok, s_fail) for each intervention
    sel = [r for r in rows if any(abs(r["strength"] - float(br[r["intervention"]][k])) < 1e-9
                                   for k in ("s_ok", "s_fail"))]
    fig, axes = plt.subplots(len(sel), 3, figsize=(6.6, 2.2 * len(sel)), constrained_layout=True)
    for row, r in zip(axes, sel):
        z = np.load(os.path.join(OUT, r["run_id"] + ".npz"))
        cy, cx = np.unravel_index(np.argmax(z["before"]), z["before"].shape)
        for ax, key in zip(row, ("before", "during", "after")):
            A = np.roll(z[key], (64 - cy, 64 - cx), axis=(0, 1))[34:94, 34:94] \
                if key != "after" else z[key]
            ax.imshow(A, cmap="viridis", vmin=0, vmax=1, interpolation="nearest")
            ax.set_xticks([]), ax.set_yticks([])
            if key == "before":
                ax.set_ylabel(f"{r['intervention']} s={r['strength']:.4f}\n{r['class']}", fontsize=8)
            ax.set_title({"before": "t0 (pre-edit, 60² crop)", "during": "t0 (post-edit)",
                          "after": "t0+2000 (full 128²)"}[key], fontsize=7)
    fig.savefig(os.path.join(OUT, "gallery.png"), dpi=100)


if __name__ == "__main__":
    main()
