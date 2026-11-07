"""G007 (a bestiary of catalogued species) and G012 (catalogued growers), filmed from the pinned catalog."""

from __future__ import annotations

import json

import numpy as np
from PIL import Image

from film import (BG, DIM, EXHIBITS, HERE, INK, Run, bar, catalog_entry, colorize, exhibit, save_provenance,
                  text, write_media)
from alm.measure import periodic_centroid

import survey  # world_size / place: the same placement as the VIS-S1 survey


def world(index: int):
    e, rule, cells = catalog_entry(index)
    n = survey.world_size(rule.R, np.rint(cells * 255))
    return e, rule, survey.place(np.rint(cells * 255), n)


def follow(A: np.ndarray, win: int) -> np.ndarray:
    n = A.shape[0]
    cx, cy = periodic_centroid(A)
    B = np.roll(A, (int(round(n / 2 - cy)), int(round(n / 2 - cx))), axis=(0, 1))
    o = (n - win) // 2
    return B[o:o + win, o:o + win]


def survey_row(index: int) -> dict:
    for line in (HERE / "survey.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["index"] == index:
            return r
    return {}


# Picked by eye from the VIS-S1 contact sheets for variety of form (all PERSISTED in the survey).
BESTIARY = [4, 19, 35, 72, 86, 172, 207, 222, 242, 259, 277, 322, 375, 395, 417, 568]
WIN_R = {259: 9, 277: 10, 19: 7}  # window in R for the long ones (default 6 R)
FILM_TU = (60, 90)  # film this window, after 60 tu of settling from the catalog seed
TILE = 240


@exhibit("G007")
def g007(render: bool = True):
    runs, info = [], []
    for idx in BESTIARY:
        e, rule, A0 = world(idx)
        t0, t1 = (int(round(x * rule.T)) for x in FILM_TU)
        every = int(round(rule.T / 5))  # 5 frames per tu (all picks have T = 10)
        assert every * 5 == rule.T
        win = min(A0.shape[0], int(WIN_R.get(idx, 6) * rule.R))
        run = Run(f"G007:{idx}:{e.get('code')}", rule, A0, t1,
                  built=f"catalog entry #{idx} ({e.get('code')} {e.get('name')}) cells placed centred on zero "
                        f"{A0.shape[0]}^2 (VIS-talk survey.place)",
                  keep_every=every, keep_from=t0)
        run.go(record=render, on_step=lambda sim, s, w=win: follow(sim.A, w).astype(np.float32))
        runs.append(run)
        info.append({"index": idx, "code": e.get("code"), "name": e.get("name"), "R": rule.R, "T": rule.T,
                     "window_cells": win, "survey_class": survey_row(idx).get("class")})
        print("G007", idx, e.get("code"), flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G007-bestiary"
    cols, pad, head = 4, 10, 26
    Wd = cols * TILE + (cols + 1) * pad
    rows = (len(runs) + cols - 1) // cols
    Hd = 54 + rows * (TILE + head + pad) + pad
    nfr = min(len(r.frames) for r in runs)
    frames = []
    for k in range(nfr):
        img = Image.new("RGB", (Wd, Hd), BG)
        text(img, (pad, 14), "Sixteen species from the Lenia catalogue, alive in our simulator", 22, bold=True)
        for i, (run, m) in enumerate(zip(runs, info)):
            r, c = divmod(i, cols)
            x = pad + c * (TILE + pad)
            y = 54 + r * (TILE + head + pad)
            A = run.frames[sorted(run.frames)[k]]
            im = Image.fromarray(colorize(A)).resize((TILE, TILE), Image.Resampling.NEAREST)
            img.paste(im, (x, y + head))
            text(img, (x, y + 4), m["name"], 14)
            bar(img, m["R"], TILE / m["window_cells"], (x + 8, y + head + TILE - 26), "R", 11)
        frames.append(img)
    media = write_media(frames, folder, "bestiary", fps=20, gif_width=640, gif_every=2, gif_colors=96)
    frames[0].save(folder / "bestiary-still.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G007", "title": "Sixteen catalogued species, alive in our simulator",
        "media": media + ["bestiary-still.png"],
        "frames": {"window_tu": list(FILM_TU), "frames_per_tu": 5, "mp4_fps": 20,
                   "time_compression": "4 tu per second"},
        "view": "each tile follows its creature's periodic centroid (integer shift), window 6 R (7-10 R for the three long species, see WIN_R; or the whole world "
                "if smaller), nearest-neighbour; tiles have different cell scales, so each carries its own R bar",
        "species": info,
        "caveats": [
            "Every species, name and seed is Bert Chan's, from the pinned upstream catalog (Chakazul/Lenia@adfc542 "
            "Python/animals.json). Nothing here is a new species; the exhibit shows that ALM's own simulator runs them.",
            "Picked by eye for variety from the VIS-S1 survey (survey.py, SURVEY.md); 'persisted for 100 tu in our "
            "world' is all the survey checks, not that the shape is the catalogued one.",
            "Each species runs under its own catalogued rule (R, T, mu, sigma, kernel shells b) - sixteen different rules.",
        ],
    }, runs)
    return runs


GROWERS = [197, 157, 198, 12, 62, 262]
GROW_TU = 100


@exhibit("G012")
def g012(render: bool = True):
    runs, info = [], []
    for idx in GROWERS:
        e, rule, A0 = world(idx)
        steps = int(round(GROW_TU * rule.T))
        every = int(round(rule.T * 0.4))  # one frame per 0.4 tu, so panels with T 5 and T 10 stay in step
        assert abs(every - rule.T * 0.4) < 1e-9
        run = Run(f"G012:{idx}:{e.get('code')}", rule, A0, steps,
                  built=f"catalog entry #{idx} ({e.get('code')} {e.get('name')}) cells placed centred on zero "
                        f"{A0.shape[0]}^2 (VIS-talk survey.place)",
                  keep_every=every)
        run.go(record=render, on_step=lambda sim, s: np.rint(sim.A * 255).astype(np.uint8))
        runs.append(run)
        info.append({"index": idx, "code": e.get("code"), "name": e.get("name"), "R": rule.R, "N": A0.shape[0],
                     "survey_class": survey_row(idx).get("class")})
        print("G012", idx, e.get("code"), flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G012-growers"
    cols, tile, pad, head = 3, 320, 12, 26
    Wd = cols * tile + (cols + 1) * pad
    Hd = 54 + 2 * (tile + head + pad) + pad
    nfr = min(len(r.frames) for r in runs)
    frames = []
    for k in range(nfr):
        img = Image.new("RGB", (Wd, Hd), BG)
        text(img, (pad, 14), "Catalogued growers: one seed, a whole world of pattern", 22, bold=True)
        tt = None
        for i, (run, m) in enumerate(zip(runs, info)):
            r, c = divmod(i, cols)
            x = pad + c * (tile + pad)
            y = 54 + r * (tile + head + pad)
            s = sorted(run.frames)[k]
            tt = s / run.rule.T
            im = Image.fromarray(colorize(run.frames[s] / 255.0)).resize((tile, tile), Image.Resampling.LANCZOS)
            img.paste(im, (x, y + head))
            text(img, (x, y + 4), f"{m['name']}", 14)
        text(img, (Wd - pad, 18), f"t = {tt:5.1f}", 18, anchor="ra")
        frames.append(img)
    media = write_media(frames, folder, "growers", fps=25, gif_width=540, gif_every=3, gif_colors=64, crf=24)
    frames[-1].save(folder / "growers-final.png", optimize=True)
    for run, m in zip(runs, info):
        last = run.frames[max(run.frames)] / 255.0
        Image.fromarray(colorize(last)).save(folder / f"{m['code'].replace('+', 'plus').replace('?', '')}-final.png",
                                             optimize=True)
    save_provenance(folder, {
        "exhibit": "G012", "title": "Catalogued growers",
        "media": media + ["growers-final.png"],
        "frames": {"frames_per_tu": 2.5, "mp4_fps": 25, "time_compression": "10 tu per second"},
        "view": "whole periodic worlds (256^2 or 512^2, see runs), downsampled to 320 px with Lanczos filtering "
                "(this exhibit is NOT one pixel per cell)",
        "species": info,
        "caveats": [
            "These are the catalogue's own 'Cateno-' (chain-forming) and related growing species: growth is their "
            "catalogued behaviour, not our discovery. Gyrorbium revolvens (OG2r) is included because it filled its "
            "world in our survey.",
            "Whether a grower fills the world depends on world size and time; these are single runs to 100 tu.",
            "The labyrinths resemble reaction-diffusion (Turing) patterns; that is a resemblance, not a tested mechanism.",
        ],
    }, runs)
    return runs


SPIRAL = 197  # Catenohelicium monospirae (HN+m)
N13, H13 = 1024, 150


@exhibit("G013")
def g013(render: bool = True):
    e, rule, cells = catalog_entry(SPIRAL)
    A0 = survey.place(np.rint(cells * 255), N13)
    steps = int(round(H13 * rule.T))
    run = Run(f"G013:{SPIRAL}:{e.get('code')}", rule, A0, steps,
              built=f"catalog entry #{SPIRAL} ({e.get('code')} {e.get('name')}) cells placed centred on zero "
                    f"{N13}^2 (VIS-talk survey.place)",
              keep_every=5)
    run.go(record=render, on_step=lambda sim, s: np.rint(sim.A * 255).astype(np.uint8))
    if not render:
        return [run]
    folder = EXHIBITS / "G013-spiral"
    frames = []
    # Fixed camera on the central 768^2 cells, shown at 1 px per cell, so nothing is resampled.
    o, w = (N13 - 768) // 2, 768
    for s in sorted(run.frames):
        A = run.frames[s][o:o + w, o:o + w] / 255.0
        img = Image.new("RGB", (w, w + 56), BG)
        img.paste(Image.fromarray(colorize(A)), (0, 56))
        text(img, (14, 12), "A spiral that draws itself", 24, bold=True)
        text(img, (w - 14, 16), f"t = {s / rule.T:5.1f}", 20, anchor="ra")
        bar(img, 10 * rule.R, 1, (w - 14 - 10 * rule.R, 40), "10 R", 11)
        frames.append(img)
    media = write_media(frames, folder, "spiral", fps=30, gif_width=480, gif_every=3, gif_colors=64, crf=24)
    frames[-1].save(folder / "spiral-final.png", optimize=True)
    last = run.frames[max(run.frames)] / 255.0
    fill = float((last > 0.1).mean())
    np.savetxt(folder / "mass.csv", np.c_[np.arange(steps + 1) / rule.T, run.mass], delimiter=",",
               header="t_tu,mass_sumA_over_R2", comments="", fmt="%.6g")
    save_provenance(folder, {
        "exhibit": "G013", "title": "A spiral that draws itself",
        "media": media + ["spiral-final.png", "mass.csv"],
        "frames": {"keep_every_steps": 5, "mp4_fps": 30, "time_compression": "15 tu per second"},
        "view": f"central 768^2 cells of a {N13}^2 periodic world, 1 px per cell, fixed camera",
        "species": {"index": SPIRAL, "code": e.get("code"), "name": e.get("name"), "R": rule.R, "T": rule.T,
                    "mu": rule.mu, "sigma": rule.sigma, "beta": list(rule.beta)},
        "final_fill_fraction_A_gt_0.1": fill,
        "caveats": [
            "Catalogued species and catalogued behaviour: Chan 2019 sec. 3.5.4 (pdf p. 28) describes 'spiral "
            "elongation (in Helicidae)' with quadratic mass growth. Nothing here is new; the exhibit shows ALM "
            "reproducing it at a large world size.",
            "Single run, alm only. In a 512^2 world (G012) the arm meets its own periodic image by about 70 tu and a "
            "labyrinth texture takes over where it collides; check the film's last frames for the same here.",
        ],
    }, [run])
    return [run]
