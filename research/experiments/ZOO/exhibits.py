"""Gallery exhibits G035-G037 for the collision zoo.

    PYTHONPATH=src:research/experiments/ZOO:research/experiments/VIS-talk \
        .venv/bin/python research/experiments/ZOO/exhibits.py G035 G036 G037

G035  Collision atlas of two Orbia (bubble-chamber sheet from atlas-O.jsonl) + detonation film.
G036  A Hexapteryx fed Circium rings one at a time (film from feed.py --alternate) + ladder still.
G037  Tip or belly: where a ring meets a Pteryx decides swallow or detonation (atlas-PC.jsonl).

Colour rule as the gallery: A in [0, 1] linear onto inferno (chamber tiles use A^0.7 and are
time exposures: max over the run, disclosed in the caption). Every simulated run records its
initial and final state sha256; replays are checked against the atlas rows / feed logs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from alm.lenia import Lenia
from atlas import WORLDS, base_body, body
from chamber import COLORS, LABEL, exposure, font, sheet
from film import colorize, text, write_media, BG, INK, DIM, ACCENT  # VIS-talk helpers
from zoocore import components, place_pair, sha

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXHIBITS = REPO / "research" / "gallery" / "exhibits"
CMD = "PYTHONPATH=src:research/experiments/ZOO:research/experiments/VIS-talk .venv/bin/python research/experiments/ZOO/exhibits.py"


def provenance(folder, d):
    (folder / "provenance.json").write_text(json.dumps(d, indent=2) + "\n")


def row(world, a, b, theta, bR):
    for l in (HERE / f"atlas-{world}.jsonl").read_text().splitlines():
        r = json.loads(l)
        if (r["a"], r["b"], r["theta"], r["b_R"]) == (a, b, theta, bR):
            return r
    raise KeyError((world, a, b, theta, bR))


def g035():
    folder = EXHIBITS / "G035-orbium-collision-atlas"
    folder.mkdir(parents=True, exist_ok=True)
    bad = sheet("O", "O2u", "O2u", str(folder / "atlas.png"), crop_half=110, tile_px=96,
                title="Two Orbia, 204 collisions",
                sub="Each tile is a time exposure (max of A over the run). Rows: angle between headings "
                    "(180° = head-on). Columns: sideways offset b in kernel radii. S001 rule, 384² torus.")
    assert not bad, bad
    # the detonation film
    W = WORLDS["O"]
    theta, bR, tu = 75, 0.75, 130
    r = row("O", "O2u", "O2u", theta, bR)
    A = body("O", "O2u", 0.0)
    B = body("O", "O2u", A.heading + theta)
    A0, info = place_pair(A, B, bR, W["rule"].R, W["N"])
    L = Lenia(W["rule"], A0)
    init = sha(L.A)
    frames = []
    masses = []
    for s in range(0, int(tu * W["rule"].T) + 1):
        if s:
            L.step()
        if s == int(round(r["tu"] * W["rule"].T)):
            assert sha(L.A) == r["final_sha256"], "replay differs from atlas row"
        if s % 10 == 0:
            t = s / W["rule"].T
            im = Image.new("RGB", (W["N"] * 2, W["N"] * 2 + 64), BG)
            im.paste(Image.fromarray(colorize(L.A, 2)), (0, 64))
            text(im, (14, 10), "Two Orbia meet at 75°", 22, bold=True)
            text(im, (14, 38), f"t = {t:5.1f}   mass = {L.A.sum() / (A.mass + B.mass):6.1f} × the two gliders", 15, fill=DIM)
            frames.append(im)
            masses.append(round(float(L.A.sum()), 2))
    media = write_media(frames, folder, "detonation", fps=15, gif_width=320, gif_every=2, gif_colors=96)
    frames[-1].save(folder / "detonation-final.png")
    provenance(folder, {
        "exhibit": "G035", "title": "Two Orbia, 204 collisions",
        "media": ["atlas.png", *media, "detonation-final.png"],
        "claim": "C080",
        "view": "atlas.png: each tile is max over time of A (sampled every 0.5 tu), 220x220 window "
                "around the contact point, A^0.7 onto inferno; border colour = outcome class. "
                "detonation: whole 384^2 torus, A linear onto inferno, every 1 tu (gif: every 2 tu, 320 px).",
        "atlas": {"rows": "research/experiments/ZOO/atlas-O.jsonl", "replayed": 204,
                  "hash_mismatches": 0},
        "runs": [{"key": "G035:detonation", "rule": W["rule"].to_dict(), "grid": [W["N"], W["N"]],
                  "boundary": "periodic", "time_units": tu, "theta_deg": theta, "b_R": bR,
                  "initial_state": "two settled S001-rule Orbia (atlas.body), placed by zoocore.place_pair",
                  "initial_state_sha256": init, "final_state_sha256": sha(L.A),
                  "atlas_row_final_sha256_checked_at_tu": r["tu"], "mass_every_5tu": masses[::5]}],
        "command": f"{CMD} G035",
    })


def ladder_still(folder, feed_log, states_tag):
    """Catalogue P6al..P10al next to the fed arc after 1..4 meals (same segment count)."""
    tiles = []
    for k, code in enumerate(["P6al", "P7al", "P8al", "P9al", "P10al"]):
        p, v, m = base_body("P", code)
        cat = colorize(p, 2)
        if k == 0:
            fed = cat
            fm = m
        else:
            F = np.load(HERE / "states" / f"feed{states_tag}-meal{k:02d}.npy")
            c = components(F, floor=30)[0]["c"]
            cy, cx = int(round(c[0])), int(round(c[1]))
            F = F[cy - 70:cy + 71, cx - 70:cx + 71]
            fed = colorize(F, 2)
            fm = float(F.sum())
        tiles.append((code, m, cat, fed, fm))
    tw = 282
    im = Image.new("RGB", (14 + 5 * (tw + 10), 110 + 2 * (tw + 40)), BG)
    text(im, (14, 10), "Is the fed arc the catalogued animal?", 22, bold=True)
    text(im, (14, 40), "Top: catalogue Pteryx species, settled. Bottom: a Hexapteryx after 0-4 Circium meals. "
                       "Same rule, same scale.", 14, fill=DIM)
    for i, (code, m, cat, fed, fm) in enumerate(tiles):
        x = 14 + i * (tw + 10)
        im.paste(Image.fromarray(cat), (x, 100))
        text(im, (x, 100 + tw + 6), f"{code}  mass {m:.0f}", 14)
        im.paste(Image.fromarray(fed), (x, 100 + tw + 40))
        text(im, (x, 100 + 2 * tw + 46), f"{i} meal{'s' if i != 1 else ''}  mass {fm:.0f}", 14,
             fill=ACCENT if i else INK)
    im.save(folder / "ladder.png")


def g036():
    folder = EXHIBITS / "G036-the-arc-that-eats-rings"
    folder.mkdir(parents=True, exist_ok=True)
    log = json.loads((HERE / "feed-altfilm.json").read_text())
    z = np.load(HERE / "states" / "feed-alt-film.npz")["frames"]
    meals = [e for e in log["log"] if "meal" in e and "mass" in e]
    per, m6 = log["per_segment"], log["ladder"]["P6al"]
    frames = []
    # time of each frame: the film keeps 1 frame per tu of accepted history after the first 10 tu
    # (the first 10 tu are recorded too); meal k is accepted at meals[k]["t"]
    for i in range(0, len(z), 2):
        A = z[i].astype(np.float32) / 255
        im = Image.new("RGB", (512, 512 + 64), BG)
        im.paste(Image.fromarray(colorize(A, 2)), (0, 64))
        done = [m for m in meals if m["t"] - 5 <= i + 1]
        n = len(done)
        seg = 6 + (float(A.sum()) * 4 - m6) / per if False else (done[-1]["segments_est"] if done else 6.0)
        text(im, (14, 10), "A Hexapteryx fed Circium rings", 22, bold=True)
        text(im, (14, 38), f"meals {n:2d}   segments ≈ {round(seg):2d}   (512² torus shown at half resolution)", 15, fill=DIM)
        frames.append(im)
    media = write_media(frames, folder, "feeding", fps=24, gif_width=384, gif_every=3)
    frames[-1].save(folder / "feeding-final.png")
    ladder_still(folder, log, "-altfilm")
    final = [e for e in log["log"] if e.get("event") == "final cruise"]
    stop = [e for e in log["log"] if e.get("event") == "no offset grew"]
    provenance(folder, {
        "exhibit": "G036", "title": "The arc that eats rings",
        "media": [*media, "feeding-final.png", "ladder.png"],
        "claims": ["C082", "C083"],
        "view": "feeding: whole 512^2 torus downsampled 2x (every other cell), every 2 tu, A linear onto "
                "inferno (frames stored as uint8). ladder.png: settled catalogue bodies (top) and fed arc "
                "after k meals (bottom), 141x141 windows, 2x nearest-neighbour.",
        "run": {"rule": WORLDS["P"]["rule"].to_dict(), "grid": [512, 512], "boundary": "periodic",
                "start": "settled catalogue P6al (Hexapteryx arcus labens), alone",
                "food": "settled catalogue C0v (Circium ventilans), stamped ahead of the arc, alternating sides",
                "feed_log": "research/experiments/ZOO/feed-altfilm.json",
                "meals_accepted": len(meals), "stopped": stop[0] if stop else None,
                "final_state_sha256": meals[-1]["sha256"]},
        "caveats": ["The feeding is an intervention by a keeper: each ring is placed by hand, and a meal that "
                    "did not grow the arc is rewound and retried at another offset (every try is logged).",
                    "Segment counts are estimated from mass with the catalogue ladder P6al-P10al and checked "
                    "by eye in ladder.png for 0-4 meals only."],
        "command": f"{CMD} G036",
    })


def g037():
    folder = EXHIBITS / "G037-tip-or-belly"
    folder.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in (HERE / "atlas-PC.jsonl").read_text().splitlines()]
    codes = ["P6al", "P7al", "P8al", "P9al", "P10al"]
    bs = sorted({r["b_R"] for r in rows})
    # three exposures for P8al: swallow, detonate, miss
    picks = [("swallow", 4.5), ("detonate", 0.0), ("miss", 6.0)]
    exps = []
    for name, bR in picks:
        r = row("PC", "P8al", "C0v", 180, bR)
        k, t, ok = exposure(("PC", "P8al", "C0v", 180, bR, r["tu"], 150, r["final_sha256"]))
        assert ok, (name, bR)
        exps.append((name, bR, t, r["class"]))
    cell = 9
    lm = 90
    Wd = lm + len(bs) * cell + 30
    im = Image.new("RGB", (max(Wd, 3 * 310 + 30), 126 + len(codes) * 26 + 60 + 330), BG)
    d = ImageDraw.Draw(im)
    text(im, (14, 10), "Tip or belly", 22, bold=True)
    text(im, (14, 40), "A Pteryx arc meets a still Circium ring head-on, offset sideways by b.", 14, fill=DIM)
    text(im, (14, 60), "Grey: miss. Red: detonation. Yellow: the ring is swallowed and the arc grows a segment.", 14, fill=DIM)
    y0 = 96
    for i, code in enumerate(codes):
        y = y0 + i * 26
        text(im, (14, y + 2), code, 14)
        g = {r["b_R"]: r["class"] for r in rows if r["a"] == code}
        for j, bR in enumerate(bs):
            c = {"MISS": COLORS["MISS"], "EXPLODE": COLORS["EXPLODE"], "SURVIVOR": COLORS["SURVIVOR"]}.get(g.get(bR), (40, 40, 40))
            d.rectangle([lm + j * cell, y, lm + j * cell + cell - 2, y + 20], fill=c)
    ya = y0 + len(codes) * 26 + 4
    for bR in range(-9, 10, 3):
        j = bs.index(float(bR))
        text(im, (lm + j * cell + cell // 2, ya), f"{bR}", 12, fill=DIM, anchor="ma")
    text(im, (lm, ya + 18), "b / R (kernel radii)", 12, fill=DIM)
    yb = ya + 50
    for i, (name, bR, t, cls) in enumerate(exps):
        x = 14 + i * 310
        tile = Image.fromarray(colorize(np.clip(t, 0, 1) ** 0.7, 1)).resize((300, 300), Image.Resampling.LANCZOS)
        im.paste(tile, (x, yb))
        text(im, (x, yb + 304), f"P8al, b = {bR:g} R: {name}", 14)
    im.save(folder / "tip-or-belly.png")
    provenance(folder, {
        "exhibit": "G037", "title": "Tip or belly",
        "media": ["tip-or-belly.png"], "claim": "C081",
        "view": "Strip: outcome class of each atlas-PC row (Pteryx vs C0v, head-on, b step 0.25 R). "
                "Bottom: time exposures (max over the run of A, A^0.7 onto inferno), 300x300 window around "
                "the contact point, replayed and hash-checked against atlas-PC rows.",
        "atlas": "research/experiments/ZOO/atlas-PC.jsonl",
        "runs": [{"key": f"G037:P8al-b{bR:g}", "final_state_sha256": row("PC", "P8al", "C0v", 180, bR)["final_sha256"]}
                 for _, bR in picks],
        "command": f"{CMD} G037",
    })


if __name__ == "__main__":
    for g in sys.argv[1:]:
        {"G035": g035, "G036": g036, "G037": g037}[g]()
        print(g, "done", flush=True)
