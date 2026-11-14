"""Bubble-chamber sheets: replay atlas collisions and draw each as a time-exposure.

Each tile is the maximum of A over the whole run (sampled every 0.5 tu), cropped around the
contact point, so incoming and outgoing tracks show as trails, like a bubble-chamber photo.
The tile border is the outcome class from atlas-<world>.jsonl; replay is checked against the
row's final_sha256 (the frame classified, at the row's ``tu``).

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/chamber.py O O2u O2u out.png
"""

from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib

from alm.lenia import Lenia
from atlas import WORLDS, body
from zoocore import place_pair, sha

HERE = Path(__file__).resolve().parent
FONT_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
LUT = (matplotlib.colormaps["inferno"](np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)
BG = (12, 10, 18)
INK = (236, 230, 220)
DIM = (150, 144, 140)
COLORS = {  # outcome class -> border colour
    "MISS": (90, 90, 100),
    "SCATTER": (90, 170, 255),
    "SURVIVOR": (250, 200, 60),
    "FUSE": (80, 220, 140),
    "ANNIHILATE": (200, 60, 200),
    "MULTIPLY": (255, 255, 255),
    "EXPLODE": (255, 70, 50),
}
LABEL = {
    "MISS": "miss / deflect",
    "SCATTER": "touch and part",
    "SURVIVOR": "one dies",
    "FUSE": "fuse",
    "ANNIHILATE": "both die",
    "MULTIPLY": "fission",
    "EXPLODE": "detonate",
}


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


def exposure(args):
    world, a, b, theta, b_R, tu, crop_half, want_sha = args
    W = WORLDS[world]
    A = body(world, a, 0.0)
    hA = A.heading if A.heading is not None else 0.0
    B = body(world, b, hA + theta)
    A0, info = place_pair(A, B, b_R, W["rule"].R, W["N"])
    L = Lenia(W["rule"], A0)
    E = L.A.copy()
    k = max(1, int(round(0.5 * W["rule"].T)))
    for s in range(1, int(round(tu * W["rule"].T)) + 1):
        L.step()
        if s % k == 0:
            np.maximum(E, L.A, out=E)
    ok = (sha(L.A) == want_sha) if want_sha else None
    N = W["N"]
    c = N // 2
    tile = E[c - crop_half:c + crop_half, c - crop_half:c + crop_half]
    return (theta, b_R), tile.astype(np.float32), ok


def sheet(world, a, b, out, crop_half=None, tile_px=96, title=None, sub=None):
    rows = [json.loads(l) for l in (HERE / f"atlas-{world}.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["a"] == a and r["b"] == b]
    thetas = sorted({r["theta"] for r in rows}, reverse=True)
    bs = sorted({r["b_R"] for r in rows})
    crop_half = crop_half or WORLDS[world]["N"] // 2
    jobs = [(world, a, b, r["theta"], r["b_R"], r["tu"], crop_half, r["final_sha256"]) for r in rows]
    with Pool(4) as pool:
        res = pool.map(exposure, jobs)
    tiles = {k: (t, ok) for k, t, ok in res}
    bad = [k for k, (_, ok) in tiles.items() if ok is False]
    cls = {(r["theta"], r["b_R"]): r["class"] for r in rows}
    pad, lm, tm, gap = 6, 70, 112, 4
    W_ = lm + len(bs) * (tile_px + gap) + 20
    H_ = tm + len(thetas) * (tile_px + gap) + 70
    img = Image.new("RGB", (W_, H_), BG)
    d = ImageDraw.Draw(img)
    d.text((14, 12), title or f"Collision atlas: {a} × {b}", fill=INK, font=font(24, True))
    d.text((14, 44), sub or "", fill=DIM, font=font(14))
    d.text((lm, tm - 40), "impact parameter b / R  →", fill=DIM, font=font(13))
    for j, bR in enumerate(bs):
        d.text((lm + j * (tile_px + gap) + tile_px // 2, tm - 4), f"{bR:g}", fill=DIM, font=font(12), anchor="ms")
    for i, th in enumerate(thetas):
        y = tm + i * (tile_px + gap)
        d.text((lm - 8, y + tile_px // 2), f"{th:g}°", fill=DIM, font=font(13), anchor="rm")
        for j, bR in enumerate(bs):
            x = lm + j * (tile_px + gap)
            if (th, bR) not in tiles:
                continue
            t, _ = tiles[(th, bR)]
            idx = np.rint(np.clip(t, 0, 1) ** 0.7 * 255).astype(np.uint8)
            im = Image.fromarray(LUT[idx]).resize((tile_px - 2 * 3, tile_px - 2 * 3), Image.Resampling.LANCZOS)
            d.rectangle([x, y, x + tile_px - 1, y + tile_px - 1], fill=COLORS[cls[(th, bR)]])
            img.paste(im, (x + 3, y + 3))
    d.text((14, tm - 40), "angle", fill=DIM, font=font(13))
    # legend
    present = [c for c in COLORS if c in set(cls.values())]
    x = lm
    y = H_ - 40
    for c in present:
        d.rectangle([x, y, x + 14, y + 14], fill=COLORS[c])
        d.text((x + 20, y + 7), LABEL[c], fill=INK, font=font(13), anchor="lm")
        x += 40 + int(d.textlength(LABEL[c], font=font(13)))
    img.save(out)
    print(f"{out}: {len(tiles)} tiles, replay hash mismatches: {len(bad)} {bad[:5]}")
    return bad


if __name__ == "__main__":
    world, a, b, out = sys.argv[1:5]
    ch = int(sys.argv[5]) if len(sys.argv) > 5 else None
    sheet(world, a, b, out, crop_half=ch)
