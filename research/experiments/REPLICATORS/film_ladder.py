"""G030: one founder cell (213/84's cells) under four rules on the line well -> uncontrolled.

Panels lam 0, 0.2, 0.5, 1 (interp.mix), 256^2 torus each, every 2 tu to TU. Each panel shows the
field (inferno, linear [0, 1]) and a bar with its occupancy (as in growth.py).
usage: film_ladder.py TU OUTDIR
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from common import found_entry, nd, state_hash
from interp import mix

TU, out = float(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
LAMS = [0.0, 0.2, 0.5, 1.0]
LABEL = {0.0: "λ 0  'division well'", 0.2: "λ 0.2", 0.5: "λ 0.5", 1.0: "λ 1  'division uncontrolled'"}
N, BAR = 256, 14
cmap = matplotlib.colormaps["inferno"]
worlds, h0 = [], []
for lam in LAMS:
    _, A = nd.entry_state(found_entry("213", 84), 2, N)
    w = nd.NDLenia(mix(lam), A); worlds.append(w); h0.append(state_hash(w.A))
try:
    font = ImageFont.truetype("DejaVuSans.ttf", 13)
except OSError:
    font = ImageFont.load_default()
W, H = 2 * N, 2 * (N + BAR + 18)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W * 2}x{H * 2}",
                       "-r", "30", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow", str(out / "ladder.mp4")],
                      stdin=subprocess.PIPE)
steps = int(round(TU / worlds[0].dt)); every = int(round(2 / worlds[0].dt))
occ_trace = {lam: [] for lam in LAMS}
last = None
for s in range(steps + 1):
    if s % every == 0:
        canvas = Image.new("RGB", (W, H), (11, 11, 16)); d = ImageDraw.Draw(canvas)
        for k, (lam, w) in enumerate(zip(LAMS, worlds)):
            S = w.A.sum(0)
            oc = float((ndimage.gaussian_filter(S, 4.0, mode="wrap") > 0.05).mean())
            occ_trace[lam].append((round(s * w.dt, 1), round(oc, 4)))
            ox, oy = (k % 2) * N, (k // 2) * (N + BAR + 18)
            canvas.paste(Image.fromarray((cmap(np.clip(S, 0, 1))[..., :3] * 255).astype(np.uint8)), (ox, oy + 18))
            d.text((ox + 6, oy + 2), LABEL[lam], fill=(230, 230, 230), font=font)
            d.rectangle([ox + 6, oy + 18 + N + 3, ox + 6 + int((N - 12) * oc), oy + 18 + N + BAR - 3], fill=(250, 200, 80))
            d.rectangle([ox + 6, oy + 18 + N + 3, ox + N - 6, oy + 18 + N + BAR - 3], outline=(120, 120, 120))
        d.text((W - 80, 2), f"t = {s * worlds[0].dt:4.0f}", fill=(200, 200, 200), font=font)
        img = canvas.resize((W * 2, H * 2), Image.NEAREST)
        ff.stdin.write(np.asarray(img).tobytes()); last = img
    if s < steps:
        for w in worlds:
            w.step()
ff.stdin.close(); ff.wait()
last.save(out / "ladder-final.png")
rec = dict(lams=LAMS, N=N, tu=TU, initial_sha=h0, final_sha=[state_hash(w.A) for w in worlds],
           occupancy_every_20=[{str(l): occ_trace[l][::10]} for l in LAMS])
(out / "ladder.json").write_text(json.dumps(rec))
print("done", [occ_trace[l][-1] for l in LAMS])
