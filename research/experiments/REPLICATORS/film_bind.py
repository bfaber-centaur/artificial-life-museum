"""G073: drug A only, drug B only and steering (A, then a pulse of B when the tumour turns resistant),
side by side, from therapy2.py's "bind" experiment at cost 0.3.

Colour = genome on coolwarm (blue slow, resistant to A; red fast, sensitive to A), brightness = matter,
as G067. Each arm is re-run with therapy2.run for its full length and its final hash is checked
against therapy2.jsonl; frames are taken from the first SHOW tu.

  python film_bind.py SEED OUT_DIR [SHOW]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import therapy as th
import therapy2 as t2
from film_therapy import BG, FS, FT, paint

ARMS = [("A", t2.constant, "drug A only", (230, 159, 0)),
        ("B", t2.only_b, "drug B only", (204, 121, 167)),
        ("steer", t2.steer, "steering: A, then B", (86, 180, 233))]


def main(seed, out, SHOW=1600.0, cost=0.3, scale=3, every=8.0):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in open(Path(__file__).with_name("therapy2.jsonl"))]
    A0, g0, _, B0 = th.grow(seed, 128, cost)
    snaps = {}
    for arm, pol, _, _ in ARMS:
        ref = next(r for r in rows if r["exp"] == "bind" and r["arm"] == arm and r["seed"] == seed and r["cost"] == cost)
        shots = []

        def grab(s, w, a, b, shots=shots):
            t = s * w.dt
            if t <= SHOW and s % int(round(every / w.dt)) == 0:
                shots.append((t, w.A.copy(), w.g.copy(), a, b))
        r = t2.run(A0, g0, seed, B0, ref["tu"], pol, cost, on_step=grab)
        assert r["final_sha"] == ref["final_sha"], f"{arm}: replay differs from therapy2.jsonl"
        snaps[arm] = shots
        print(arm, "replayed", len(shots), "frames", flush=True)
    N = A0.shape[0]
    side, pad, top, ch = N * scale, 14, 36, 150
    W, H = 3 * side + 4 * pad, top + side + 26 + ch + 30
    hist = {a: [] for a, *_ in ARMS}
    frames = []
    for i in range(len(snaps["A"])):
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        for j, (arm, _, title, col) in enumerate(ARMS):
            t, A, g, a, b = snaps[arm][i]
            m = float(A.sum())
            hist[arm].append((m / B0, b))
            x0 = pad + j * (side + pad)
            im.paste(Image.fromarray(paint(A, g, scale)), (x0, top))
            tag = "  (B on)" if (arm == "steer" and b) else ""
            d.text((x0, 10), title + tag, fill=col, font=FT)
            res = float(A[g < th.RESIST].sum() / max(m, 1e-9)) if m > 0 else 0.0
            d.text((x0, top + side + 4), f"burden {m / B0:4.2f} × start   resistant {100 * res:3.0f}%",
                   fill=(200, 200, 210), font=FS)
        cy0, cy1 = top + side + 30, top + side + 26 + ch
        cx0, cx1 = pad + 40, W - pad
        ymax = 2.6
        for k, (_, b) in enumerate(hist["steer"]):
            if b:
                x = cx0 + (cx1 - cx0) * k * every / SHOW
                d.line([(x, cy0), (x, cy1)], fill=(24, 44, 60), width=max(1, int((cx1 - cx0) * every / SHOW) + 1))
        for yv in (0.5, 1.0, 1.25, 2.0):
            yy = cy1 - (cy1 - cy0) * yv / ymax
            d.line([(cx0, yy), (cx1, yy)], fill=(70, 70, 85) if yv == 1.25 else (38, 38, 50))
            d.text((pad - 4, yy - 7), f"{yv:g}×", fill=(150, 150, 165), font=FS)
        for arm, _, _, col in ARMS:
            h = np.array([x[0] for x in hist[arm]])
            xs = cx0 + (cx1 - cx0) * np.arange(h.size) * every / SHOW
            ys = cy1 - (cy1 - cy0) * np.minimum(h, ymax) / ymax
            if h.size > 1:
                d.line(list(zip(xs.tolist(), ys.tolist())), fill=col, width=2)
        d.text((cx0 + 6, cy0 - 2), "tumour burden (× start); 1.25× = progression; shading: steering arm gives drug B",
               fill=(160, 160, 175), font=FS)
        d.text((cx1 - 120, cy1 + 6), f"t = {snaps['A'][i][0]:5.0f} tu", fill=(170, 170, 185), font=FS)
        frames.append(np.asarray(im))
    mp4 = out / "bind.mp4"
    h_, w_ = frames[0].shape[:2]
    ff = shutil.which("ffmpeg") or "ffmpeg"
    p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w_}x{h_}",
                          "-r", "20", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(mp4)],
                         stdin=subprocess.PIPE)
    for fr in frames:
        p.stdin.write(np.ascontiguousarray(fr[: h_ // 2 * 2, : w_ // 2 * 2]).tobytes())
    p.stdin.close(); assert p.wait() == 0
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(mp4), "-vf",
                    "fps=8,scale=820:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=none",
                    str(out / "bind.gif")], check=True)
    Image.fromarray(frames[-1]).save(out / "bind-final.png")
    print("ok", len(frames), "frames")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]), a[1], *(float(a[2]),) if len(a) > 2 else ())
