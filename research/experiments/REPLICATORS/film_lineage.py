"""Film a dividing creature coloured by ancestry, and draw its family tree.

usage: film_lineage.py STEM IDX N TU OUTDIR [SCALE] [BLUR] [THR]
Writes OUTDIR/lineage.mp4, lineage-final.png, tree.png, tree.json.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import colorsys

from common import found_entry, nd, state_hash
from lineage import Tracker

stem, idx, N, TU, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), Path(sys.argv[5])
scale = int(sys.argv[6]) if len(sys.argv) > 6 else 2
out.mkdir(parents=True, exist_ok=True)
e = found_entry(stem, idx)
params, A = nd.entry_state(e, 2, N)
w = nd.NDLenia(params, A)
h0 = state_hash(w.A)
every = int(round(1 / w.dt))
steps = int(round(TU / w.dt))
BLUR = float(sys.argv[7]) if len(sys.argv) > 7 else 3.0
THR = float(sys.argv[8]) if len(sys.argv) > 8 else 0.05
tr = Tracker(thr=THR, blur=BLUR)
fps = 30
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{N * scale}x{N * scale}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
                       "-pix_fmt", "yuv420p", "-crf", "20", str(out / "lineage.mp4")], stdin=subprocess.PIPE)
pop = []
t0 = time.time()
for s in range(steps + 1):
    if s % every == 0:
        t = round(s * w.dt, 3)
        S = w.A.sum(0)
        lab, ids = tr.update(t, S)
        img = tr.colorize(S, lab, ids)
        pop.append((t, len(set(ids.values()))))
        if s % (every * 2) == 0:  # 2 tu per video frame
            ff.stdin.write(np.kron(img, np.ones((scale, scale, 1), dtype=np.uint8)).tobytes())
        if s == steps:
            plt.imsave(out / "lineage-final.png", np.kron(img, np.ones((scale, scale, 1), dtype=np.uint8)))
    if s < steps:
        w.step()
ff.stdin.close(); ff.wait()
tr.finish(TU)
summ = tr.summary()

# family tree: rows = interval midpoints, x = time
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 8), gridspec_kw=dict(height_ratios=[4, 1]), sharex=True)
fig.patch.set_facecolor("#0b0b10")
for a in (ax, ax2):
    a.set_facecolor("#0b0b10"); a.tick_params(colors="#bbb")
    for sp in a.spines.values():
        sp.set_color("#555")
for B in tr.bodies.values():
    c = colorsys.hsv_to_rgb(B.mid, 0.85, 1.0)
    ax.plot([B.born, B.died], [B.mid, B.mid], color=c, lw=1.2)
    if B.parent is not None:
        P = tr.bodies[B.parent]
        ax.plot([B.born, B.born], [P.mid, B.mid], color=c, lw=0.8, alpha=0.8)
    if B.end == "death":
        ax.plot(B.died, B.mid, "x", color="#ddd", ms=3, mew=0.8)
ax.set_ylim(1, 0); ax.set_yticks([]); ax.set_ylabel("lineage (daughters split their mother's row)", color="#bbb")
ax.set_title(f"{e.get('name')} (found/{stem}.json #{idx}): {summ['events'].get('division', 0)} divisions, "
             f"{summ['events'].get('death', 0)} deaths, {summ['events'].get('fusion', 0)} fusions, "
             f"deepest generation {summ['max_gen']}", color="#eee")
pt = np.array(pop)
ax2.plot(pt[:, 0], pt[:, 1], color="#eee", lw=1)
ax2.set_ylabel("bodies", color="#bbb"); ax2.set_xlabel("time units", color="#bbb")
plt.tight_layout(); plt.savefig(out / "tree.png", dpi=110, facecolor=fig.get_facecolor())
rec = dict(blur=BLUR, thr=THR, stem=stem, idx=idx, name=e.get("name"), N=N, tu=TU, dt=w.dt, initial_sha=h0, final_sha=state_hash(w.A),
           summary=summ, population=pop[::10],
           events=[(t, k, p, c) for t, k, p, c in tr.events],
           bodies=[dict(id=B.id, parent=B.parent, gen=B.gen, born=B.born, died=B.died, how=B.how, end=B.end,
                        lo=B.lo, hi=B.hi) for B in tr.bodies.values()])
(out / "tree.json").write_text(json.dumps(rec))
print(json.dumps(summ), f"{time.time() - t0:.0f}s")
