"""3-D peek: max projection contact sheet. python peek3d.py STEM IDX N TU NFRAMES out.png"""
import sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import found_entry, nd, count_bodies
stem, idx, N, TU, NF, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
e = found_entry(stem, idx)
params, A = nd.entry_state(e, 3, N)
print("shape", A.shape, "mass", A.sum())
w = nd.NDLenia(params, A)
steps = int(round(TU / w.dt)); marks = set(np.linspace(0, steps, NF).round().astype(int))
fr = []
for s in range(steps + 1):
    if s in marks:
        n = count_bodies(w.A[0], thr=0.2)[0]
        fr.append((s * w.dt, w.A[0].max(0), n, w.A.sum())); print(fr[-1][0], n, fr[-1][3], flush=True)
    if s < steps: w.step()
cols = min(NF, 6); rows = (NF + cols - 1) // cols
fig, ax = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
for a, (t, X, n, m) in zip(np.ravel(ax), fr):
    a.imshow(X, cmap="inferno", vmin=0, vmax=1); a.set_title(f"t={t:.0f} n={n} m={m:.0f}", fontsize=9); a.axis("off")
plt.tight_layout(); plt.savefig(out, dpi=60)
