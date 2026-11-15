"""G067: the therapy toy (therapy.py) filmed: no drug, constant drug, adaptive drug, side by side.

Colour = genome on coolwarm (blue 0 'well', slow and drug-tolerant; red 1 'uncontrolled', fast
and drug-sensitive), brightness = field value, as in G045. Below: tumour burden / B0 for each arm,
with the adaptive arm's drug-on periods shaded. Re-runs therapy.treat for each arm and checks
that the final state hash matches therapy.jsonl.

  python film_therapy.py SEED KAPPA OUT_DIR [TU]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import therapy as th
from common import state_hash
from genome import GenomeLenia

cmap = matplotlib.colormaps["coolwarm"]
try:
    FT, FS = ImageFont.truetype("DejaVuSans.ttf", 16), ImageFont.truetype("DejaVuSans.ttf", 13)
except OSError:
    FT = FS = ImageFont.load_default()
BG = (11, 11, 15)
LINE = {"none": (200, 200, 210), "constant": (230, 159, 0), "adaptive": (86, 180, 233)}
TITLE = {"none": "no drug", "constant": "constant drug", "adaptive": "adaptive: on/off"}


def paint(A, g, scale):
    v = np.clip(A, 0, 1)[..., None]
    rgb = cmap(g)[..., :3] * (0.1 + 0.9 * v) * (v > 0.01)
    return np.kron((np.clip(rgb, 0, 1) * 255).astype(np.uint8), np.ones((scale, scale, 1), np.uint8))


def main(seed, kappa, out, TU=2000.0, scale=3, every=10.0):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in open(Path(__file__).with_name("therapy.jsonl"))]
    A0, g0, t_grow, B0 = th.grow(seed, 128)
    N = A0.shape[0]
    worlds, on = {}, {}
    for arm in ("none", "constant", "adaptive"):
        worlds[arm] = GenomeLenia(A0, g0, mut_amp=th.MUT, seed=10_000 + seed)
        on[arm] = arm != "none"
    hist = {a: [] for a in worlds}
    onhist = []
    side, pad, top, ch = N * scale, 14, 36, 150
    W, H = 3 * side + 4 * pad, top + side + 26 + ch + 30
    dt = worlds["none"].dt
    nsteps = int(round(TU / dt)); k = int(round(every / dt))
    frames = []
    for s in range(nsteps + 1):
        # identical bookkeeping to therapy.treat
        for arm, w in worlds.items():
            m = float(w.A.sum())
            if arm == "adaptive":
                if on[arm] and m <= th.LOW * B0:
                    on[arm] = False
                elif not on[arm] and m >= th.HIGH * B0:
                    on[arm] = True
        if s % k == 0:
            for arm, w in worlds.items():
                hist[arm].append(float(w.A.sum()) / B0)
            onhist.append(on["adaptive"])
            im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
            for j, (arm, w) in enumerate(worlds.items()):
                x0 = pad + j * (side + pad)
                im.paste(Image.fromarray(paint(w.A, w.g, scale)), (x0, top))
                gm = float((w.A * w.g).sum() / max(w.A.sum(), 1e-9))
                tag = "  (drug on)" if on[arm] and arm == "adaptive" else ""
                d.text((x0, 10), TITLE[arm] + tag, fill=LINE[arm], font=FT)
                d.text((x0, top + side + 4), f"burden {hist[arm][-1]:4.2f} × start   mean genome {gm:.2f}",
                       fill=(200, 200, 210), font=FS)
            cy0, cy1 = top + side + 30, top + side + 26 + ch
            cx0, cx1 = pad + 40, W - pad
            ymax = 2.6
            for i, o in enumerate(onhist):
                if o:
                    x = cx0 + (cx1 - cx0) * i * every / TU
                    d.line([(x, cy0), (x, cy1)], fill=(24, 44, 60), width=max(1, int((cx1 - cx0) * every / TU) + 1))
            for yv in (0.5, 1.0, 1.25, 2.0):
                yy = cy1 - (cy1 - cy0) * yv / ymax
                d.line([(cx0, yy), (cx1, yy)], fill=(70, 70, 85) if yv == 1.25 else (38, 38, 50))
                d.text((pad - 4, yy - 7), f"{yv:g}×", fill=(150, 150, 165), font=FS)
            for arm in worlds:
                h = np.array(hist[arm])
                xs = cx0 + (cx1 - cx0) * np.arange(h.size) * every / TU
                ys = cy1 - (cy1 - cy0) * np.minimum(h, ymax) / ymax
                if h.size > 1:
                    d.line(list(zip(xs.tolist(), ys.tolist())), fill=LINE[arm], width=2)
            d.text((cx0 + 6, cy0 - 2), "tumour burden (× burden when treatment starts); 1.25× = progression;"
                   " shading: adaptive drug on", fill=(160, 160, 175), font=FS)
            d.text((cx1 - 120, cy1 + 6), f"t = {s * dt:5.0f} tu", fill=(170, 170, 185), font=FS)
            frames.append(np.asarray(im))
        if s == nsteps:
            break
        for arm, w in worlds.items():
            w.step()
            if on[arm]:
                w.A *= 1 - w.dt * kappa * w.g
    for arm, w in worlds.items():
        ref = next(r for r in rows if r["seed"] == seed and r["arm"] == arm and r["tu"] == TU
                   and (arm == "none" or r["kappa"] == kappa))
        assert ref["final_sha"] == state_hash(np.stack([w.A, w.g])), f"{arm}: replay differs from therapy.jsonl"
    mp4 = out / "therapy.mp4"
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
                    str(out / "therapy.gif")], check=True)
    Image.fromarray(frames[-1]).save(out / "therapy-final.png")
    print("ok", len(frames), "frames")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]), float(a[1]), a[2], *(float(a[3]),) if len(a) > 3 else ())
