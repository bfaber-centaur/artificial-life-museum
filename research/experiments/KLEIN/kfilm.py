"""KLEIN films (gallery G053, G054) and their verification.

Deterministic: fixed seeds, float64, single-threaded FFT. Each exhibit writes media and
provenance.json into research/gallery/exhibits/G05x-*/ with the final-state sha256 of every run;
``verify`` replays the runs without rendering and compares the hashes.

Usage:
  python kfilm.py G053 [G054]
  python kfilm.py verify [G053 ...]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import klein as K  # noqa: E402
import kview as kv  # noqa: E402
from alm import specimens  # noqa: E402
from alm.provenance import code_version, state_sha256  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = specimens.REPO_ROOT
GAL = REPO / "research" / "gallery" / "exhibits"
SHARE = Path("/mnt/project-files/strange-geometries")
CMD = "PYTHONPATH=src .venv/bin/python research/experiments/KLEIN/kfilm.py"
DIRS = {"G053": "G053-through-the-looking-glass", "G054": "G054-the-mirror-next-door"}


def gif(frames, path, every=2, scale=0.6, fps=15):
    from PIL import Image

    ims = []
    for f in frames[::every]:
        im = Image.fromarray(f)
        im = im.resize((int(im.width * scale) // 2 * 2, int(im.height * scale) // 2 * 2), Image.LANCZOS)
        ims.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0, optimize=True)


def pad_to(img, h):
    out = np.empty((h, img.shape[1], 3), np.uint8)
    out[:] = kv.BG
    o = (h - img.shape[0]) // 2
    out[o:o + img.shape[0]] = img
    return out


def side_by_side(*imgs, gap=10):
    h = max(i.shape[0] for i in imgs)
    parts = []
    for k, i in enumerate(imgs):
        if k:
            g = np.empty((h, gap, 3), np.uint8)
            g[:] = kv.BG
            parts.append(g)
        parts.append(pad_to(i, h))
    return np.hstack(parts)


def caption(img, lines, h=44):
    bar = np.empty((h, img.shape[1], 3), np.uint8)
    bar[:] = kv.BG
    for k, t in enumerate(lines):
        bar = kv.label(bar, t, (12, 4 + 19 * k), size=14, fill=(200, 200, 205) if k else (240, 240, 240))
    return np.vstack([img, bar])


def write(out, frames, stem, every=2, scale=0.6, fps=24):
    out.mkdir(parents=True, exist_ok=True)
    kv.write_mp4(frames, out / f"{stem}.mp4", fps=fps)
    gif(frames, out / f"{stem}.gif", every=every, scale=scale, fps=12)


# ------------------------------------------------------------------ G053
G053_N, G053_STEPS = 96, 600


def g053(render=True):
    """One Orbium (S001, as registered: k = 0) on a 96 x 96 Klein bottle for 60 tu."""
    s = specimens.load("S001")
    n = G053_N
    w = K.Klein(s.rule, K.place(s.cells, (n, n), (70, 30), k=0))
    chart = kv.Chart(n, n, scale=4, pad=26)
    bot = kv.Bottle(n, n, size=470)
    shape = np.array([2 * n, n])
    frames, trail, crossings = [], [], 0
    p = K.centroid(w.full[:n])
    half = 0
    for t in range(0, G053_STEPS + 1):
        if t:
            w.step()
        if t % 2:
            continue
        cs = [K.centroid(w.full, m) for m, mm in K.bodies(w.full) if mm > 30]
        if cs:
            c = min(cs, key=lambda c: np.hypot(*K.wrap(c - p, shape)))
            h = int(c[0] // n)
            if h != half:
                crossings += 1
                half = h
            p = c
            yx = (c[0] % n, c[1] if h == 0 else (-c[1]) % n)  # chart position
            trail.append(yx)
        if not render:
            continue
        left = chart.frame(w.A)
        from PIL import Image, ImageDraw
        im = Image.fromarray(left)
        d = ImageDraw.Draw(im)
        for (y, x) in trail[:-1:3]:
            d.ellipse([26 + 4 * x - 1.5, 26 + 4 * y - 1.5, 26 + 4 * x + 1.5, 26 + 4 * y + 1.5], fill=(150, 150, 160))
        left = np.asarray(im)
        left = kv.label(left, "the chart", (30, 30), size=15)
        right = bot.frame(w.A, az_deg=-40 + 100 * t / G053_STEPS, el_deg=14)
        right = kv.label(right, "the same world, as a glass bottle", (10, 8), size=15)
        img = side_by_side(left, right)
        times = {0: "not yet", 1: "once", 2: "twice"}.get(crossings, f"{crossings} times")
        side = "as it did at the start" if crossings % 2 == 0 else "like its own mirror image"
        img = caption(img, [f"t = {t / 10:5.1f} tu    through the twist {times}: on the chart it now looks {side}",
                            "chart: left and right edges glued straight (blue), top and bottom glued with a flip (red)"])
        frames.append(img)
    runs = [{"key": "G053", "world": f"Klein bottle {n} x {n}", "seed": "S001 cells (k = 0) centred at (y 70, x 30)",
             "steps": G053_STEPS, "crossings": crossings, "final_sha256": state_sha256(w.A)}]
    if render:
        out = GAL / DIRS["G053"]
        write(out, frames, "looking-glass", every=2, scale=0.62)
        from PIL import Image
        Image.fromarray(frames[-1]).save(out / "looking-glass-final.png", optimize=True)
        prov = {
            "exhibit": "G053", "title": "Through the looking glass",
            "media": ["looking-glass.mp4", "looking-glass.gif", "looking-glass-final.png"],
            "frames": {"every_steps": 2, "mp4_fps": 24, "time_compression": "4.8 tu per second"},
            "view": "left: the Klein bottle's chart (fundamental domain), nearest cell per pixel, 4 px per cell; "
                    "grey dots: the animal's mass centre every 0.6 tu, drawn where the chart shows it. Right: the same "
                    "state on the standard immersed Klein bottle, nearest cell per sample, Lambert shading "
                    "0.35 + 0.65 |cos|, glass drawn transparent (four nearest layers composited). The camera turns "
                    "100 degrees during the film. The 3-D bottle distorts areas (its neck is thin) and passes through "
                    "itself; the simulated world does neither.",
            "claim": "C102",
            "caveats": ["The animal is simulated on the bottle's double cover (an ordinary 96 x 192 torus kept "
                        "glide-symmetric), with alm.lenia; nothing is simulated on the 3-D surface."],
            "runs": runs, "code_version": code_version(), "command": f"{CMD} G053",
        }
        (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    return runs


# ------------------------------------------------------------------ G054
G054_NY, G054_NX, G054_STEPS = 24, 128, 400


def tiled(A, klein, sc=4):
    """The world (middle, full brightness) with the copies above and below it that its kernel
    reaches across the glued edges (dimmed): plain copies on the torus, mirror images on the bottle."""
    nb = K.mirror_x(A) if klein else A
    img = np.vstack([kv.colour(nb) * 0.5, kv.colour(A), kv.colour(nb) * 0.5]).astype(np.uint8)
    img = np.repeat(np.repeat(img, sc, 0), sc, 1)
    h = A.shape[0] * sc
    for y in (h, 2 * h):
        img[y - 1, ::6] = (120, 120, 140)
        img[y - 1, 1::6] = (120, 120, 140)
    return img


def g054(render=True):
    """Orbium (S001, k = 0: heading mostly across the narrow direction) in a 128 x 24 world:
    torus vs Klein bottle, same seed."""
    s = specimens.load("S001")
    ny, nx = G054_NY, G054_NX
    seed = K.place(s.cells, (ny, nx), (ny // 2, 16), k=0)
    worlds = {"torus": K.Torus(s.rule, seed), "klein": K.Klein(s.rule, seed)}
    frames = []
    for t in range(0, G054_STEPS + 1):
        if t:
            for w in worlds.values():
                w.step()
        if not render or t % 2:
            continue
        panels = []
        for kind, w in worlds.items():
            img = tiled(w.A, kind == "klein")
            head = np.empty((26, img.shape[1], 3), np.uint8)
            head[:] = kv.BG
            title = ("torus: its neighbours are copies" if kind == "torus"
                     else "Klein bottle: its neighbours are mirror images")
            head = kv.label(head, title, (6, 4), size=14)
            m = float(w.A.sum()) / 73.5
            foot = np.empty((22, img.shape[1], 3), np.uint8)
            foot[:] = kv.BG
            foot = kv.label(foot, f"mass {m:4.1f} x one Orbium", (6, 2), size=13, fill=(190, 190, 195))
            panels.append(np.vstack([head, img, foot]))
        img = np.vstack([panels[0], np.full((10, panels[0].shape[1], 3), kv.BG, np.uint8), panels[1]])
        img = caption(img, [f"t = {t / 10:5.1f} tu    same Orbium, same start, 128 x 24 cells",
                            "bright: the world; dim: what lies across its top and bottom edges"])
        frames.append(img)
    runs = [{"key": f"G054-{kind}", "world": f"{kind} {nx} x {ny}", "seed": "S001 cells (k = 0) centred at (y 12, x 16)",
             "steps": G054_STEPS, "final_mass_orbia": float(w.A.sum()) / 73.5, "final_sha256": state_sha256(w.A)}
            for kind, w in worlds.items()]
    if render:
        out = GAL / DIRS["G054"]
        write(out, frames, "mirror-next-door", every=2, scale=0.75)
        from PIL import Image
        Image.fromarray(frames[len(frames) // 4]).save(out / "mirror-next-door-t10.png", optimize=True)
        prov = {
            "exhibit": "G054", "title": "The mirror next door",
            "media": ["mirror-next-door.mp4", "mirror-next-door.gif", "mirror-next-door-t10.png"],
            "frames": {"every_steps": 2, "mp4_fps": 24, "time_compression": "4.8 tu per second"},
            "view": "each panel: the 128 x 24 world (middle band, nearest cell per pixel, 4 px per cell) with the "
                    "copy of the world that lies across its top and bottom edges drawn above and below it at half "
                    "brightness: a plain copy on the torus, the left-right mirror image on the Klein bottle.",
            "claim": "C103",
            "caveats": ["One seed of the 64 in narrow.jsonl at heights 23-26 for this heading; 29 of 32 such Klein "
                        "runs fail, 0 of 32 torus runs (kb.py narrow)."],
            "runs": runs, "code_version": code_version(), "command": f"{CMD} G054",
        }
        (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    return runs


EXHIBITS = {"G053": g053, "G054": g054}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "verify":
        ok = True
        for ex in args[1:] or list(EXHIBITS):
            prov = json.loads((GAL / DIRS[ex] / "provenance.json").read_text())
            for a, b in zip(prov["runs"], EXHIBITS[ex](render=False)):
                good = a["final_sha256"] == b["final_sha256"]
                ok &= good
                print(ex, a["key"], "OK" if good else "MISMATCH", flush=True)
        sys.exit(0 if ok else 1)
    for ex in args:
        EXHIBITS[ex]()
        print("rendered", ex, flush=True)
