"""GEOM films: Orbium on a sphere and on the hyperbolic plane (gallery G038, G039) and the
lattice compass roses (G040).

Every run is deterministic (fixed worlds, fixed seeds, float64, single-threaded BLAS). Each
exhibit writes media and provenance.json into research/gallery/exhibits/G0xx-*/, with the
final-state sha256 of every run; ``verify`` replays without rendering and compares the hashes.

Usage:
  python film.py G038 [G039 G040]
  python film.py verify [G038 ...]
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
import geomlenia as g  # noqa: E402
import geomrender as rd  # noqa: E402
from alm import specimens  # noqa: E402
from alm.lenia import Lenia  # noqa: E402
from alm.provenance import code_version, state_sha256  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = specimens.REPO_ROOT
GAL = REPO / "research" / "gallery" / "exhibits"
SHARE = Path("/mnt/project-files/strange-geometries")
HOME, R = 68.198, 13
CMD = "PYTHONPATH=src .venv/bin/python research/experiments/GEOM/film.py"


def s001():
    s = specimens.load("S001")
    return s, g.patch_sampler(s.cells / 255.0)


def gif(frames, path, every=2, scale=0.6, fps=15):
    from PIL import Image

    ims = []
    for f in frames[::every]:
        im = Image.fromarray(f)
        im = im.resize((int(im.width * scale) // 2 * 2, int(im.height * scale) // 2 * 2),
                       Image.NEAREST)
        ims.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0,
                optimize=True)


def flat_pair(sep_R, N=256):
    """Two S001 Orbia on the flat square torus, side by side, same heading (alm.lenia)."""
    s, _ = s001()
    A = np.zeros((N, N))
    h, wd = s.cells.shape
    th = np.radians(HOME)
    perp = np.array([-np.sin(th), np.cos(th)])
    for sg in (0.5, -0.5):
        dx, dy = sg * sep_R * R * perp
        x0, y0 = int(round(N / 2 + dx - wd / 2)), int(round(N / 2 + dy - h / 2))
        A[y0:y0 + h, x0:x0 + wd] = np.maximum(A[y0:y0 + h, x0:x0 + wd], s.cells / 255.0)
    return Lenia(s.rule, A)


def flat_view(A, centre, half=70, scale=2, rot_deg=0.0):
    """Window of the torus around centre (x, y), rotated so S001's heading points up."""
    N = A.shape[0]
    n = 2 * half * scale
    yy, xx = np.mgrid[0:n, 0:n]
    u = (xx + 0.5) / scale - half
    v = half - (yy + 0.5) / scale
    t = np.radians(rot_deg)
    x = centre[0] + u * np.cos(t) - v * np.sin(t)
    y = centre[1] + u * np.sin(t) + v * np.cos(t)
    ix = np.floor(x).astype(int) % N
    iy = np.floor(y).astype(int) % N
    return rd.colour(A[iy, ix]).astype(np.uint8)


def side_by_side(*imgs, gap=12):
    h = max(i.shape[0] for i in imgs)
    out = []
    for k, im in enumerate(imgs):
        pad = np.empty((h, im.shape[1], 3), np.uint8)
        pad[:] = rd.BG
        y0 = (h - im.shape[0]) // 2
        pad[y0:y0 + im.shape[0]] = im
        out.append(pad)
        if k < len(imgs) - 1:
            sp = np.empty((h, gap, 3), np.uint8)
            sp[:] = rd.BG
            out.append(sp)
    return np.concatenate(out, 1)


def caption_bar(img, lines, h=46):
    bar = np.empty((h, img.shape[1], 3), np.uint8)
    bar[:] = rd.BG
    out = np.concatenate([bar, img], 0)
    for k, (x, text) in enumerate(lines):
        out = rd.label(out, text, (x, 6), size=17)
    return out


# ------------------------------------------------------------------------------------------ G038


def g038(render=True):
    """Parallel lines meet: a pair 3 R apart, flat torus vs a sphere of radius 40 cells; and a
    'planet' of eight Orbia on a sphere of radius 60."""
    s, f = s001()
    steps, every = 900, 3
    # flat control
    L = flat_pair(3)
    # sphere
    rho = 40
    w = g.icosphere(rho)
    phi = 3 * R / 2 / rho
    A = np.zeros(w.n)
    for sg in (1, -1):
        A = np.maximum(A, g.seed_sphere(w, f, np.array([np.cos(phi), 0, sg * np.sin(phi)]),
                                        np.array([0, 1.0, 0]), HOME))
    G = g.GraphLenia(w, s.rule, A)
    a0 = (L.A.copy(), G.A.copy())
    globe = rd.Globe(w, 420) if render else None
    frames, eye = [], None
    from alm.measure import periodic_centroid
    for t in range(steps + 1):
        if render and t % every == 0:
            c = np.array(periodic_centroid(L.A))
            left = flat_view(L.A, c, half=70, scale=3, rot_deg=HOME - 90)
            cg = g.sphere_centroid(w, G.A)
            eye = cg if eye is None else eye * 0.85 + cg * 0.15
            # look from slightly behind and above the travel direction
            right = globe.frame(G.A, eye)
            fr = side_by_side(left, right)
            fr = caption_bar(fr, [(10, f"flat world  ·  t = {t / 10:5.1f}"),
                                  (left.shape[1] + 22, "sphere, radius 3.1 R")])
            frames.append(fr)
        if t < steps:
            L.step()
            G.step()
    runs = [{"key": "G038:flat-pair-3R", "world": "square torus 256^2 (alm.lenia)",
             "rule": s.rule.to_dict(), "steps": steps,
             "initial_sha256": state_sha256(a0[0]), "final_sha256": state_sha256(L.A)},
            {"key": "G038:sphere-pair-rho40-3R", "world": "icosphere rho 40",
             "world_sha256": w.sha256(), "n_cells": w.n, "rule": s.rule.to_dict(),
             "steps": steps, "initial_sha256": state_sha256(a0[1]),
             "final_sha256": state_sha256(G.A)}]
    # planet: eight Orbia, random positions and headings, rho 60
    rho2, steps2, every2 = 60, 1500, 3
    w2 = g.icosphere(rho2)
    rng = np.random.default_rng(38)
    A2 = np.zeros(w2.n)
    placed = []
    while len(placed) < 8:
        p = rng.normal(size=3)
        p /= np.linalg.norm(p)
        if any(rho2 * np.arccos(np.clip(p @ q, -1, 1)) < 4 * R for q in placed):
            continue
        hv = np.cross(p, rng.normal(size=3))
        A2 = np.maximum(A2, g.seed_sphere(w2, f, p, hv, HOME))
        placed.append(p)
    G2 = g.GraphLenia(w2, s.rule, A2)
    a20 = G2.A.copy()
    globe2 = rd.Globe(w2, 560) if render else None
    frames2, masses, stills = [], [], []
    for t in range(steps2 + 1):
        if t % 50 == 0:
            masses.append(g.mass(w2, G2.A) / R**2)
        if render and t in (0, 100, 250, 1500):
            comps = g.components(w2, G2.A)
            big = max(comps, key=lambda m: (G2.A[m] * w2.area[m]).sum())
            ce = (G2.A[big, None] * w2.xy[big]).sum(0)
            st = globe2.frame(G2.A, ce)
            stills.append(rd.label(st, f"t = {t / 10:g}", (12, 10), size=18))
        if render and t % every2 == 0:
            ang = 2 * np.pi * t / steps2 * 1.25
            eye = np.array([np.cos(ang), np.sin(ang), 0.8 * np.sin(2 * ang)])
            fr = globe2.frame(G2.A, eye)
            fr = rd.label(fr, f"eight Orbia on a sphere of radius 4.6 R  ·  t = {t / 10:5.1f}",
                          (10, 8), size=16)
            frames2.append(fr)
        if t < steps2:
            G2.step()
    bodies = len(g.components(w2, G2.A))
    runs.append({"key": "G038:planet-rho60-8", "world": "icosphere rho 60",
                 "world_sha256": w2.sha256(), "n_cells": w2.n, "rule": s.rule.to_dict(),
                 "steps": steps2, "seed": "numpy default_rng(38): 8 points >= 4 R apart, random "
                 "tangent headings", "initial_sha256": state_sha256(a20),
                 "final_sha256": state_sha256(G2.A),
                 "mass_R2_every_50_steps": [round(m, 4) for m in masses],
                 "bodies_final": bodies})
    # tiny planets: one Orbium on spheres of shrinking radius (same runs as sphere.py curvature)
    tiles = []
    for rho3 in (25, 14, 9, 7, 6, 5):
        w3 = g.icosphere(rho3)
        G3 = g.GraphLenia(w3, s.rule, g.seed_sphere(w3, f, np.array([1.0, 0, 0]),
                                                    np.array([0, 1.0, 0]), HOME))
        for _ in range(3000):
            G3.step()
        runs.append({"key": f"G038:tiny-planet-rho{rho3}", "world": f"icosphere rho {rho3}",
                     "world_sha256": w3.sha256(), "n_cells": w3.n, "rule": s.rule.to_dict(),
                     "steps": 3000, "final_sha256": state_sha256(G3.A),
                     "mass_R2_final": g.mass(w3, G3.A) / R**2})
        if render:
            gl3 = rd.Globe(w3, int(16 * rho3) + 20)  # same pixels per cell on every planet
            im = gl3.frame(G3.A, g.sphere_centroid(w3, G3.A))
            tw = max(im.shape[1] + 24, 190)
            tile = np.empty((440, tw, 3), np.uint8)
            tile[:] = rd.BG
            y0 = (420 - im.shape[0]) // 2 + 20
            x0 = (tw - im.shape[1]) // 2
            tile[y0:y0 + im.shape[0], x0:x0 + im.shape[1]] = im
            tile = rd.label(tile, f"radius {rho3} = {rho3 / R:.2f} R", (12, 412), size=14)
            tiles.append(tile)
    if not render:
        return runs
    out = GAL / "G038-parallel-lines-meet"
    out.mkdir(parents=True, exist_ok=True)
    rd.write_mp4(frames, out / "meet.mp4", fps=30)
    gif(frames, out / "meet.gif", every=3, scale=0.75, fps=12)
    key = [0, 25, 40, 60, 120, 300]
    rd.save_png(np.concatenate([frames[k][46:, -420:] for k in key], 1), out / "meet-strip.png")
    rd.save_png(np.concatenate(tiles, 1), out / "tiny-planets.png")
    rd.write_mp4(frames2, out / "planet.mp4", fps=30)
    gif(frames2, out / "planet.gif", every=4, scale=0.8, fps=12)
    rd.save_png(np.concatenate([np.concatenate(stills[:2], 1), np.concatenate(stills[2:], 1)], 0),
                out / "planet-still.png")
    prov = {
        "exhibit": "G038", "title": "Parallel lines meet",
        "media": ["meet.mp4", "meet.gif", "meet-strip.png", "planet.mp4", "planet.gif",
                  "planet-still.png", "tiny-planets.png"],
        "frames": {"meet": "every 3 steps (0.3 tu), 30 fps = 9 tu per second",
                   "planet": "every 3 steps, 30 fps = 9 tu per second; camera circles 1.25 times while bobbing in latitude; still: four moments, each globe turned to the largest body"},
        "view": "flat panel: window 140 x 140 cells following the pair, rotated so travel is up, "
                "nearest cell. Globes: orthographic, nearest cell per pixel, Lambert shading "
                "0.5 + 0.5 cos and a faint blue lift on empty cells so the ball is visible. "
                "The meet globe follows the pair's centroid (smoothed).",
        "claim": "C084 (pairs, planet), C086 (tiny planets)",
        "caveats": [
            "tiny-planets.png: each planet after 300 tu, drawn at the same 16 pixels per cell, "
            "turned to face the animal; the same six runs are in sphere.py curvature "
            "(curvature.jsonl, matching final hashes).",
            "The sphere is an icosahedral geodesic grid with 12 five-fold defects; kernel weights "
            "use each cell's spherical-Voronoi area. Same R, T, mu, sigma as S001.",
            "One pair, one sphere radius in the film; the sweep over 4 radii x 4 separations is "
            "research/experiments/GEOM/meet.jsonl.",
        ],
        "runs": runs, "code_version": code_version(), "command": f"{CMD} G038",
    }
    (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    return runs


# ------------------------------------------------------------------------------------------ G039


def g039(render=True):
    """Parallel lines part: the same pair on the hyperbolic plane (kappa 26 cells = 2 R)."""
    s, f = s001()
    kap = 26
    w = g.hyper_grid(kap, 4.0 * kap)
    c = -0.55  # Mobius translation along x: start the pair left of centre
    yy = np.tanh(3 * R / 2 / kap / 2)
    A = np.zeros(w.n)
    for sg in (1, -1):
        z0 = sg * 1j * yy
        p = (z0 + c) / (1 + c * z0)
        head = np.degrees(-2 * np.angle(1 + c * z0))
        A = np.maximum(A, g.seed_disk(w, f, p, head))
    G = g.GraphLenia(w, s.rule, A)
    L = flat_pair(3)
    a0 = (L.A.copy(), G.A.copy())
    disk = rd.Disk(w, 620) if render else None
    from alm.measure import periodic_centroid
    frames, trail, t = [], [], 0
    steps = 420
    for t in range(steps + 1):
        if t % 2 == 0:
            m_up = w.xy[:, 1] > 0
            for m in (m_up, ~m_up):
                if (G.A * m).sum() > 1:
                    trail.append(g.disk_centroid(w, G.A, m))
            if render:
                img = disk.frame(G.A)
                if t == 110:
                    still_disk = img.copy()
                for z in trail[:-2]:
                    px = int(310 + z.real * 302)
                    py = int(310 - z.imag * 302)
                    img[py - 1:py + 1, px - 1:px + 1] = (200, 200, 210)
                cc = np.array(periodic_centroid(L.A))
                left = flat_view(L.A, cc, half=70, scale=3, rot_deg=HOME)
                fr = side_by_side(left, img)
                fr = caption_bar(fr, [(10, f"flat world  ·  t = {t / 10:5.1f}"),
                                      (left.shape[1] + 22, "hyperbolic plane, curvature radius 2 R")])
                frames.append(fr)
                if t == 110:
                    still_left = left
        if t < steps:
            G.step()
            L.step()
    runs = [{"key": "G039:flat-pair-3R", "world": "square torus 256^2 (alm.lenia)",
             "rule": s.rule.to_dict(), "steps": steps, "initial_sha256": state_sha256(a0[0]),
             "final_sha256": state_sha256(L.A)},
            {"key": "G039:hyperbolic-pair-k26-3R", "world": "{3,7} geodesic grid, kappa 26, "
             "radius 104 cells, Poincare disk", "world_sha256": w.sha256(), "n_cells": w.n,
             "rule": s.rule.to_dict(), "steps": steps, "mobius_shift": c,
             "initial_sha256": state_sha256(a0[1]), "final_sha256": state_sha256(G.A)}]
    if not render:
        return runs
    out = GAL / "G039-parallel-lines-part"
    out.mkdir(parents=True, exist_ok=True)
    rd.write_mp4(frames, out / "part.mp4", fps=24)
    gif(frames, out / "part.gif", every=2, scale=0.7, fps=12)
    for z in trail:  # still: the pair at t = 11 with both complete paths
        px, py = int(310 + z.real * 302), int(310 - z.imag * 302)
        still_disk[py - 1:py + 1, px - 1:px + 1] = (200, 200, 210)
    st = side_by_side(still_left, still_disk)
    st = caption_bar(st, [(10, "flat world  ·  t = 11"),
                          (still_left.shape[1] + 22, "hyperbolic plane  ·  t = 11, with the full paths")])
    rd.save_png(st, out / "part-still.png")
    prov = {
        "exhibit": "G039", "title": "Parallel lines part",
        "media": ["part.mp4", "part.gif", "part-still.png"],
        "frames": {"every_steps": 2, "mp4_fps": 24, "time_compression": "4.8 tu per second"},
        "view": "left: flat torus window following the pair, rotated so travel is to the right. "
                "Right: Poincare disk (the whole hyperbolic world, radius 4 kappa = 104 cells), "
                "nearest cell per pixel; the disk picture shrinks distances toward the rim, so "
                "both animals look smaller as they move out though they keep their size. Grey "
                "dots: each half's mass centre every 0.2 tu. The ring is the world's edge "
                "(absorbing: empty beyond).",
        "claim": "C085",
        "caveats": [
            "The hyperbolic world is the {3,7} triangle tiling subdivided 25 times per edge "
            "(locally a hex lattice with seven-fold defects), kernel weights use exact cell "
            "areas, and kernel rows near the rim keep the interior normalisation (vacuum "
            "beyond, not renormalised).",
            "The animals leave the world after about 30 tu; the separation law is measured "
            "until then (research/experiments/GEOM/pair.jsonl).",
        ],
        "runs": runs, "code_version": code_version(), "command": f"{CMD} G039",
    }
    (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    return runs


EXHIBITS = {"G038": g038, "G039": g039}
DIRS = {"G038": "G038-parallel-lines-meet", "G039": "G039-parallel-lines-part"}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "verify":
        ok = True
        for ex in args[1:] or list(EXHIBITS):
            prov = json.loads((GAL / DIRS[ex] / "provenance.json").read_text())
            runs = EXHIBITS[ex](render=False)
            for a, b in zip(prov["runs"], runs):
                good = a["final_sha256"] == b["final_sha256"]
                ok &= good
                print(ex, a["key"], "OK" if good else "MISMATCH", flush=True)
        sys.exit(0 if ok else 1)
    for ex in args:
        EXHIBITS[ex]()
        print("rendered", ex, flush=True)
