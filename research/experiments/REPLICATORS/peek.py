"""Quick contact sheet: python peek.py STEM IDX N TU NFRAMES out.png"""
import sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import found_entry, nd, count_bodies
stem, idx, N, TU, NF, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
e = found_entry(stem, idx)
params, A = nd.entry_state(e, 2, N)
w = nd.NDLenia(params, A)
steps = int(round(TU / w.dt)); marks = set(np.linspace(0, steps, NF).round().astype(int))
fr = []
for s in range(steps + 1):
    if s in marks:
        fr.append((s * w.dt, w.A.copy()))
    if s < steps: w.step()
cols = min(NF, 6); rows = (NF + cols - 1) // cols
fig, ax = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
for a, (t, X) in zip(np.ravel(ax), fr):
    img = X.transpose(1, 2, 0) if X.shape[0] == 3 else X.sum(0) if X.shape[0] > 1 else X[0]
    a.imshow(np.clip(img, 0, 1), cmap=None if img.ndim == 3 else "inferno", vmin=0, vmax=1)
    a.set_title(f"t={t:.0f} n={count_bodies(X)[0]}", fontsize=9); a.axis("off")
plt.tight_layout(); plt.savefig(out, dpi=60)
