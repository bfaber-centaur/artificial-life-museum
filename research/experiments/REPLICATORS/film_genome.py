"""Films for the genome experiments (G045, G046). Colour = genome on coolwarm (blue g 0 'well' -> red g 1
'uncontrolled'), brightness = field value.

usage: film_genome.py evolve SEED TU OUTDIR    (selected | neutral side by side, one 213 #84 cell at g 0.3, mutation 0.03)
       film_genome.py invasion SEED TU OUTDIR  (well tissue | uncontrolled tissue, no mutation)
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
from PIL import Image, ImageDraw, ImageFont

from common import found_entry, nd, state_hash
from genome import GenomeLenia

kind, seed, TU, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), Path(sys.argv[4])
out.mkdir(parents=True, exist_ok=True)
cmap = matplotlib.colormaps["coolwarm"]
try:
    font = ImageFont.truetype("DejaVuSans.ttf", 13)
except OSError:
    font = ImageFont.load_default()


def paint(w):
    v = np.clip(w.A, 0, 1)[..., None]
    rgb = cmap(w.g)[..., :3] * (0.1 + 0.9 * v) * (v > 0.01)
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def gmean(w):
    return float((w.A * w.g).sum() / max(w.A.sum(), 1e-9))


if kind == "evolve":
    N = 256
    _, A = nd.entry_state(found_entry("213", 84), 2, N)
    worlds = [GenomeLenia(A[0], np.full((N, N), 0.3), mut_amp=0.03, seed=seed),
              GenomeLenia(A[0], np.full((N, N), 0.3), mut_amp=0.03, seed=seed, rule_g=0.3)]
    labels = ["genome sets the rule", "neutral marker (rule fixed at 0.3)"]
    H, W = N, N
else:
    import invasion  # noqa: E402  (tissues)
    L, Rt = invasion.tissue(("213", 84), 2000, seed), invasion.tissue(("213", 83), 400, seed)
    A = np.concatenate([L, Rt], 1)
    worlds = [GenomeLenia(A, np.concatenate([np.zeros_like(L), np.ones_like(Rt)], 1))]
    labels = ["left: 'division well' tissue    right: 'division uncontrolled' tissue"]
    H, W = A.shape
h0 = [state_hash(np.stack([w.A, w.g])) for w in worlds]
PADT, PLOT = 20, 70
CW = W * len(worlds)
CH = H + PADT + PLOT
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{CW * 2}x{CH * 2}",
                       "-r", "30", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow",
                       str(out / f"{kind}.mp4")], stdin=subprocess.PIPE)
dt = worlds[0].dt
steps = int(round(TU / dt)); every = int(round(4 / dt))
hist = [[] for _ in worlds]
last = None
cols = [(250, 140, 110), (180, 180, 180)]
for s in range(steps + 1):
    if s % every == 0:
        canvas = Image.new("RGB", (CW, CH), (11, 11, 16)); d = ImageDraw.Draw(canvas)
        for k, w in enumerate(worlds):
            hist[k].append(gmean(w))
            canvas.paste(Image.fromarray(paint(w)), (k * W, PADT))
            d.text((k * W + 6, 3), labels[k], fill=(230, 230, 230), font=font)
        # mean-genome plot across the bottom: y from 0 (bottom) to 1 (top)
        y0, y1 = CH - 6, PADT + H + 8
        d.line([(30, y0), (CW - 10, y0)], fill=(90, 90, 90)); d.text((4, y1 - 4), "1", fill=(150, 150, 150), font=font)
        d.text((4, y0 - 12), "0", fill=(150, 150, 150), font=font)
        for k in range(len(worlds)):
            pts = [(30 + (CW - 40) * i / (steps / every), y0 - (y0 - y1) * h) for i, h in enumerate(hist[k])]
            if len(pts) > 1:
                d.line(pts, fill=cols[k], width=2)
        d.text((CW - 190, CH - PLOT + 4), f"mean genome   t = {s * dt:4.0f}", fill=(200, 200, 200), font=font)
        img = canvas.resize((CW * 2, CH * 2), Image.NEAREST)
        ff.stdin.write(np.asarray(img).tobytes()); last = img
    if s < steps:
        for w in worlds:
            w.step()
ff.stdin.close(); ff.wait()
last.save(out / f"{kind}-final.png")
rec = dict(kind=kind, seed=seed, tu=TU, labels=labels, initial_sha=h0, final_sha=[state_hash(np.stack([w.A, w.g])) for w in worlds],
           gmean_every_40=[[round(x, 4) for x in h[::10]] for h in hist])
(out / f"{kind}.json").write_text(json.dumps(rec))
print(kind, [round(h[-1], 3) for h in hist])
