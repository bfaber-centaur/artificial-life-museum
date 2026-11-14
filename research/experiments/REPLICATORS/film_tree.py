"""Film + family tree from a record.py run.

usage: film_tree.py RUN.npz OUTDIR TITLE [SCALE] [FRAME_EVERY]
Writes OUTDIR/<stem>.mp4, <stem>-final.png, <stem>-tree.png, <stem>-tree.json
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import tree as T

run, out, title = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
scale = int(sys.argv[4]) if len(sys.argv) > 4 else 2
fe = int(sys.argv[5]) if len(sys.argv) > 5 else 2
out.mkdir(parents=True, exist_ok=True)
z = np.load(run)
S8, times = z["S"], z["t"]
N = S8.shape[1]
S = lambda f: S8[f].astype(np.float64) / 255.0  # noqa: E731
P = [T.peaks(S(f)) for f in range(len(S8))]
tracks = T.link(P, N)
segs, keep = T.build_tree(tracks, len(S8))
stem = run.stem

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{N * scale}x{N * scale}", "-r", "30", "-i", "-", "-c:v", "libx264",
                       "-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow", str(out / f"{stem}.mp4")], stdin=subprocess.PIPE)
K = np.ones((scale, scale, 1), dtype=np.uint8)
for f in range(0, len(S8), fe):
    img = T.colorize(S(f), T.segments_at(segs, tracks, f), N)
    ff.stdin.write(np.kron(img, K).tobytes())
ff.stdin.close(); ff.wait()
last = len(S8) - 1
plt.imsave(out / f"{stem}-final.png", np.kron(T.colorize(S(last), T.segments_at(segs, tracks, last), N), K))

ndiv = sum(1 for s in segs if s.get("end_kind") == "division")
nvan = sum(1 for s in segs if s.get("end_kind") == "vanished")
alive = [len(T.segments_at(segs, tracks, f)) for f in range(len(S8))]
maxgen = max(s["gen"] for s in segs)
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw=dict(height_ratios=[4, 1]), sharex=True)
bg = "#0b0b10"; fig.patch.set_facecolor(bg)
for a in (ax, ax2):
    a.set_facecolor(bg); a.tick_params(colors="#bbb")
    for sp in a.spines.values():
        sp.set_color("#444")
for s in segs:
    m = s["y"]; c = T.hue_rgb(s["hue"])
    t0, t1 = times[s["start"]], times[min(s["end"], last)]
    ax.plot([t0, t1], [m, m], color=c, lw=0.9)
    if s["parent"] is not None:
        pm = segs[s["parent"]]["y"]
        ax.plot([t0, t0], [pm, m], color=c, lw=0.6, alpha=0.8)
    if s.get("end_kind") == "vanished":
        ax.plot(t1, m, "o", color="#eee", ms=1.6)
ax.set_ylim(1.02, -0.02); ax.set_yticks([])
ax.set_ylabel("lineage", color="#bbb")
ax.set_title(f"{title}: {ndiv} divisions, {nvan} disappearances, {maxgen} generations deep", color="#eee")
ax2.plot(times, alive, color="#eee", lw=0.8); ax2.set_ylabel("cells", color="#bbb"); ax2.set_xlabel("time units", color="#bbb")
plt.tight_layout(); plt.savefig(out / f"{stem}-tree.png", dpi=120, facecolor=bg)
rec = dict(run=str(run.name), N=int(N), frames=len(S8), initial_sha=str(z["initial_sha"]), final_sha=str(z["final_sha"]),
           params=dict(SIG=T.SIG, THR=T.THR, LINK=T.LINK, GAP=T.GAP, BIRTH=T.BIRTH, MINLIFE=T.MINLIFE),
           divisions=ndiv, vanished=nvan, max_gen=maxgen, alive_end=alive[-1],
           alive_every_50=alive[::50], flicker_births_dropped=sum(1 for k in keep if not k))
(out / f"{stem}-tree.json").write_text(json.dumps(rec, indent=1))
print(json.dumps({k: v for k, v in rec.items() if k != "alive_every_50"}))
