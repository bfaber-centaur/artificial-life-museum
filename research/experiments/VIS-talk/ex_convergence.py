"""G021 "Same body plan, different physics": three bodies found by SPECIES-scout under kernel/growth
families the catalogue barely uses, each filmed above its nearest catalogued cousin.

Top row (ours, built from seeds by research/experiments/SPECIES-scout/convergence.py):
  Orbium moved into the exp/exp family (Chan's paper rule, sigma 0.016)
  the crescent glider, poly kernel + exp growth
  star A, exp/exp three-shell kernel
Bottom row (catalogue, pinned animals.json, under its own poly/poly rule):
  #4 O2u Orbium unicaudatus, #96 P4cf Paraptera cavus furiosus, #407 3R5m Asterium metamorpha
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image

from film import BG, DIM, EXHIBITS, INK, REPO, Run, bar, colorize, exhibit, save_provenance, text, write_media
from ex_catalog import follow, world

sys.path.insert(0, str(REPO / "research" / "experiments" / "SPECIES-scout"))
import convergence  # noqa: E402

from alm.lenia import Lenia, Rule  # noqa: E402

FILM_TU = 30
FPS_TU = 5
TILE = 300
SETTLE_TU = 200  # ours: same settle as convergence.py
CAT_SETTLE_TU = 60  # catalogue: same window start as G007

OURS = [
    ("orbium-ee", "Orbium, exp kernel + exp growth", "orbium", Rule(R=13, T=10, mu=0.15, sigma=0.016, kernel="exp", growth="exp")),
    ("crescent", "Crescent, poly kernel + exp growth", "crescent", None),
    ("starA", "Star, exp/exp three-shell kernel", "starA", None),
]
COUSINS = [(4, "Orbium unicaudatus (O2u)"), (96, "Paraptera cavus furiosus (P4cf)"), (407, "Asterium metamorpha (3R5m)")]


def our_run(key, body, rule_override):
    rule, A0, built = convergence.home(body)
    settle = SETTLE_TU
    if rule_override is not None:  # Orbium: settle under the home rule first, then switch family
        L = Lenia(rule, A0)
        for _ in range(int(SETTLE_TU * rule.T)):
            L.step()
        A0, rule, settle = L.A, rule_override, 0
        built += f"; settled {SETTLE_TU} tu under the S001 rule, then moved unchanged into the rule below"
    t0 = int(settle * rule.T)
    return Run(f"G021:{key}", rule, A0, t0 + int(FILM_TU * rule.T), built=built,
               keep_every=int(rule.T // FPS_TU), keep_from=t0)


def cousin_run(idx):
    e, rule, A0 = world(idx)
    t0 = int(CAT_SETTLE_TU * rule.T)
    return e, Run(f"G021:cat{idx}:{e.get('code')}", rule, A0, t0 + int(FILM_TU * rule.T),
                  built=f"catalog entry #{idx} ({e.get('code')} {e.get('name')}) cells centred on zero "
                        f"{A0.shape[0]}^2 (VIS-talk survey.place)",
                  keep_every=int(rule.T // FPS_TU), keep_from=t0)


@exhibit("G021")
def g021(render: bool = True):
    runs, labels = [], []
    for key, label, body, override in OURS:
        r = our_run(key, body, override)
        r.go(record=render, on_step=lambda sim, s, w=6 * r.rule.R: follow(sim.A, w).astype(np.float32))
        runs.append(r)
        labels.append(label)
        print("G021", key, flush=True)
    for idx, label in COUSINS:
        e, r = cousin_run(idx)
        r.go(record=render, on_step=lambda sim, s, w=6 * r.rule.R: follow(sim.A, w).astype(np.float32))
        runs.append(r)
        labels.append(label)
        print("G021", idx, flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G021-convergence"
    pad, head, top, mid = 14, 40, 70, 36
    Wd = 3 * TILE + 4 * pad
    Hd = top + 2 * (TILE + head) + mid + pad
    nfr = min(len(r.frames) for r in runs)
    frames = []
    for k in range(nfr):
        img = Image.new("RGB", (Wd, Hd), BG)
        text(img, (pad, 14), "Same body plan, different physics", 24, bold=True)
        text(img, (pad, 44), f"found by our scout (top) and in Chan's catalogue (bottom)   t = +{k / FPS_TU:4.1f} tu", 14, fill=DIM)
        for i, (run, lab) in enumerate(zip(runs, labels)):
            row, col = divmod(i, 3)
            x = pad + col * (TILE + pad)
            y = top + row * (TILE + head + mid)
            if row == 1 and col == 0:
                text(img, (pad, y - 26), "catalogue cousins, polynomial kernel + polynomial growth", 14, fill=DIM)
            A = run.frames[sorted(run.frames)[k]]
            im = Image.fromarray(colorize(A)).resize((TILE, TILE), Image.Resampling.NEAREST)
            img.paste(im, (x, y + head))
            text(img, (x, y + 4), lab, 14)
            ru = run.rule
            text(img, (x, y + 22), f"R {ru.R}  mu {ru.mu:g}  sigma {ru.sigma:g}  shells {len(ru.beta)}", 11, fill=DIM)
            bar(img, ru.R, TILE / (6 * ru.R), (x + 8, y + head + TILE - 26), "R", 11)
        frames.append(img)
    media = write_media(frames, folder, "convergence", fps=20, gif_width=600, gif_every=2, gif_colors=96)
    frames[0].save(folder / "convergence-still.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G021", "title": "Same body plan, different physics",
        "media": media + ["convergence-still.png"],
        "frames": {"window_tu": FILM_TU, "frames_per_tu": FPS_TU, "mp4_fps": 20, "time_compression": "4 tu per second"},
        "view": "each tile follows its body's periodic centroid (integer shift), window 6 R, nearest-neighbour",
        "claim": "C063",
        "caveats": [
            "Nothing here is claimed as a new species. Each top-row body has a catalogued cousin with the same body plan "
            "(bottom row); the point is that the plan recurs when the kernel and growth curves change.",
            "Top-row bodies come from one seeded soup (or S001) each, at one sigma; their survival windows across families "
            "are in research/experiments/SPECIES-scout/convergence.jsonl (C063).",
            "The star runs at R 18 and its cousin at R 27: different resolutions, so fine texture differs.",
        ],
    }, runs)
    return runs
