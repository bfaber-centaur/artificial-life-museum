"""POPGEN E0 tracker validation sheets: for g_r 0, seed 1, each N, frames at t 1000/3000/5000.

Writes two PNGs per frame to $POPGEN_OUT/validate/: the plain field (for the eye count) and the
same field with tree.peaks overlaid (red dots), and prints the peak count.
"""
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "REPLICATORS"))
import tree  # noqa: E402

OUT = Path(os.environ.get("POPGEN_OUT", "/tmp/claude-0/-home-user/1e73a8fc-c1a3-55c2-9798-cc47a6a901a7/scratchpad/popgen"))
V = OUT / "validate"; V.mkdir(exist_ok=True)
for N in (128, 256, 384):
    z = np.load(OUT / f"e0_N{N}_g0.0_s1_tu5000.npz")
    for t in (1000, 3000, 5000):
        i = list(z["snap_t"].round()).index(t)
        S = z["snaps"][i] / 255.0
        P = tree.peaks(S)
        for over in (False, True):
            fig = plt.figure(figsize=(N / 16, N / 16), dpi=80)
            ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(S, cmap="gray", vmin=0, vmax=1); ax.axis("off")
            if over:
                ax.plot(P[:, 1], P[:, 0], "r+", ms=10, mew=2)
            fig.savefig(V / f"N{N}_t{t}{'_peaks' if over else ''}.png"); plt.close(fig)
        print(N, t, "peaks", len(P))
