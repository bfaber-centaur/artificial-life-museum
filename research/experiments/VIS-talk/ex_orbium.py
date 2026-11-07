"""G009 (Orbium collisions), G010 (a soup scan) and G011 (anatomy of one step), all at the S001 rule."""

from __future__ import annotations

import json

import numpy as np
from PIL import Image

from film import (BG, DIM, EXHIBITS, HERE, INK, S001_RULE, Run, bar, colorize, crop, exhibit, paste,
                  save_provenance, settled_orbium, text, write_media)
from alm.lenia import growth
from alm.measure import periodic_centroid

R = S001_RULE.R
T = S001_RULE.T


def orbium_patch(size: int = 48):
    """Settled S001 Orbium, cropped to size x size around its centroid; checks nothing is cut off."""
    A = settled_orbium()
    P = crop(A, size)
    lost = A.sum() - P.sum()
    if lost > 1e-9:
        raise ValueError(f"crop loses mass {lost}")
    return P


def heading(P: np.ndarray, steps: int = 200) -> np.ndarray:
    """Unit (dy, dx) heading of the patch, measured by running it alone on 128^2 (not filmed)."""
    from alm.lenia import Lenia

    W = np.zeros((128, 128))
    paste(W, P, 64, 64)
    sim = Lenia(S001_RULE, W)
    prev = np.array(periodic_centroid(sim.A))
    total = np.zeros(2)
    for _ in range(steps):  # unwrap every step: the Orbium moves ~0.6 cells per step
        sim.step()
        c = np.array(periodic_centroid(sim.A))
        total += (c - prev + 64) % 128 - 64
        prev = c
    v = np.array([total[1], total[0]])
    return v / np.hypot(*v)


def components(A, thr=0.1):
    import sys

    sys.path.insert(0, str(HERE.parent / "L6-field"))
    from field import components as comp

    return comp(A, thr)


# --- G009 ---------------------------------------------------------------------------------------

N9 = 256
H9 = 120  # tu
COLLISIONS = [  # (label, kind, transverse offset b in R, delay of B in tu)
    ("head-on, b = 0", "head", 0.0, 0),
    ("head-on, b = 0.25 R", "head", 0.25, 0),
    ("head-on, b = 0.5 R", "head", 0.5, 0),
    ("head-on, b = 0.75 R", "head", 0.75, 0),
    ("head-on, b = 1 R", "head", 1.0, 0),
    ("right angle, b = 0", "perp", 0.0, 0),
    ("right angle, b = 0.5 R", "perp", 0.5, 0),
    ("right angle, b = 1 R", "perp", 1.0, 0),
    ("right angle, b = -0.5 R", "perp", -0.5, 0),
]
GAP_R = 5.0  # each body starts this many R from the meeting point


def collision_state(P, h, kind, b):
    """Exact two-body state: B is P rotated by 180 deg (head-on) or 90 deg (right angle).

    Rotations by multiples of 90 deg are exact symmetries of the square-grid kernel, so B is
    exactly an Orbium heading along -h (head-on) or along h rotated by 90 deg."""
    W = np.zeros((N9, N9))
    c = np.array([N9 / 2, N9 / 2])
    perp = np.array([-h[1], h[0]])
    if kind == "head":
        Q = np.rot90(P, 2)
        hb = -h
        pa = c - GAP_R * R * h + 0.5 * b * R * perp
        pb = c - GAP_R * R * hb - 0.5 * b * R * perp
    else:
        # np.rot90 (counter-clockwise) maps a (dy, dx) vector to (-dx, dy)
        Q = np.rot90(P, 1)
        hb = perp
        pa = c - GAP_R * R * h
        pb = c - GAP_R * R * hb + b * R * h  # B crosses A's line b R beyond the centre
    paste(W, P, int(round(pa[0])), int(round(pa[1])))
    paste(W, Q, int(round(pb[0])), int(round(pb[1])))
    return W, hb, pa, pb


def classify(A, m0_single):
    """Outcome label from the final state: survivors by mass, binding by connectivity at A > 0.01."""
    m = A.sum() / R**2
    fill = (A > 0.1).mean()
    if fill > 0.25 or m > 6 * m0_single:
        return "detonation (fills the world)"
    k = int(round(m / m0_single))
    if k == 0:
        return "both die"
    if k == 1:
        return "one dies, one survives"
    if k == 2 and components(A, 0.01) == 1:
        return "fused into one bound pair"
    if k == 2:
        return "both survive, scattered"
    return f"{m / m0_single:.2f}x Orbium mass"


@exhibit("G009")
def g009(render: bool = True):
    P = orbium_patch()
    h = heading(P)
    m1 = P.sum() / R**2
    runs, meta = [], []
    for label, kind, b, _ in COLLISIONS:
        W, hb, pa, pb = collision_state(P, h, kind, b)
        run = Run(f"G009:{label}", S001_RULE, W, H9 * T,
                  built=f"two copies of the settled S001 Orbium (S001 on 128^2 after 1000 steps, 48^2 crop), "
                        f"A at {pa.round(1).tolist()} heading {h.round(3).tolist()}, B = np.rot90(A, "
                        f"{2 if kind == 'head' else 1}) at {pb.round(1).tolist()}, on a zero {N9}^2 world",
                  keep_every=4)
        run.go(record=render, on_step=lambda sim, s: np.rint(sim.A * 255).astype(np.uint8))
        runs.append(run)
        meta.append({"label": label, "kind": kind, "b_R": b, "outcome": classify(run.final, m1) if render else None})
    if not render:
        return runs
    folder = EXHIBITS / "G009-orbium-collisions"
    cols, scale, pad, head = 3, 1.5, 12, 34
    tile = int(N9 * scale)
    Wd = cols * tile + (cols + 1) * pad
    Hd = 3 * (tile + head) + 4 * pad + 50
    frames = []
    keys = sorted(runs[0].frames)
    for s in keys:
        img = Image.new("RGB", (Wd, Hd), BG)
        text(img, (pad, 12), "Two Orbia, nine ways to meet", 24, bold=True)
        text(img, (Wd - pad, 16), f"t = {s / T:5.1f}", 20, anchor="ra")
        for i, (run, m) in enumerate(zip(runs, meta)):
            r, c = divmod(i, cols)
            x = pad + c * (tile + pad)
            y = 50 + pad + r * (tile + head + pad)
            A = run.frames[s] / 255.0
            im = Image.fromarray(colorize(A, 3)).resize((tile, tile), Image.Resampling.NEAREST)
            img.paste(im, (x, y + head))
            text(img, (x, y + 8), m["label"], 16)
        frames.append(img)
    media = write_media(frames, folder, "collisions", fps=25, gif_width=720, gif_every=2, gif_colors=96)
    frames[-1].save(folder / "collisions-final.png", optimize=True)
    # outcome sheet: final frames with measured outcome labels
    sheet = frames[-1].copy()
    for i, m in enumerate(meta):
        r, c = divmod(i, cols)
        x = pad + c * (tile + pad)
        y = 50 + pad + r * (tile + head + pad)
        text(sheet, (x + 6, y + head + tile - 22), m["outcome"], 13, fill=(120, 220, 255))
    sheet.save(folder / "collisions-outcomes.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G009", "title": "Two Orbia, nine ways to meet",
        "media": media + ["collisions-final.png", "collisions-outcomes.png"],
        "frames": {"keep_every_steps": 4, "mp4_fps": 25, "time_compression": "10 tu per second"},
        "view": f"nine whole {N9}^2 periodic worlds, fixed camera",
        "orbium_heading_dy_dx": h.tolist(), "single_orbium_mass_R2": m1,
        "outcomes_at_t_120": meta,
        "outcome_rule": "at t = 120 tu: k = round(mass / one Orbium's mass); k 0 'both die', 1 'one dies', 2 and "
                        "one connected component of A > 0.01 on the torus 'fused into one bound pair', 2 otherwise "
                        "'both survive, scattered'; 'detonation' if fill (A > 0.1) > 0.25 or mass > 6 x",
        "caveats": [
            "One phase of the Orbium and one starting gap (5 R) per geometry; outcomes of Lenia collisions depend on "
            "phase and exact offset, so each panel is one sample, not the outcome for that angle.",
            "Single runs, alm only, R13 T10, 256^2 torus: after a collision, debris can wrap around and meet again.",
            "Not novel: Chan 2019 sec. 3.5.5 catalogues Orbium collision outcomes (merging, bouncing, death, "
            "detonation). This is our simulator reproducing that kind of zoo.",
        ],
    }, runs)
    (folder / "outcomes.json").write_text(json.dumps(meta, indent=2) + "\n")
    return runs


# --- G011 ---------------------------------------------------------------------------------------

@exhibit("G011")
def g011(render: bool = True):
    """Anatomy of a step: the state A, the neighbourhood sum U = K * A, and the growth G(U)."""
    P = orbium_patch()
    W = np.zeros((128, 128))
    paste(W, P, 64, 64)
    keep = {}

    def grab(sim, s):
        U = sim.potential()
        return (sim.A.copy(), U, growth("poly", U, S001_RULE.mu, S001_RULE.sigma))

    run = Run("G011:S001-anatomy", S001_RULE, W, 40 * T,
              built="settled S001 Orbium (S001 on 128^2 after 1000 steps, 48^2 crop) pasted centred on a zero 128^2 world",
              keep_every=1)
    run.go(record=render, on_step=grab)
    if not render:
        return [run]
    folder = EXHIBITS / "G011-anatomy-of-a-step"
    from alm.lenia import kernel

    K = np.fft.fftshift(kernel((128, 128), S001_RULE))
    win, sc = 64, 6
    tile = win * sc
    pad = 20
    Wd = 3 * tile + 4 * pad
    Hd = tile + 150
    frames = []
    for s in sorted(run.frames):
        A, U, G = run.frames[s]
        cx, cy = periodic_centroid(A)
        sy, sx = int(round(64 - cy)), int(round(64 - cx))
        def c(X):
            return crop(np.roll(X, (sy, sx), axis=(0, 1)), win)
        img = Image.new("RGB", (Wd, Hd), BG)
        panels = [(colorize(c(A), sc), "A: the creature", "cell values 0 to 1"),
                  (colorize(c(U), sc, "viridis", 0, 0.3), "U = K * A: what each cell senses", "weighted ring sum, 0 to 0.3"),
                  (colorize(c(G), sc, "RdBu_r", -1, 1), "G(U): grow (red) or shrink (blue)", "next A = clip(A + G/10)")]
        for i, (rgb, title, sub) in enumerate(panels):
            x = pad + i * (tile + pad)
            img.paste(Image.fromarray(rgb), (x, 60))
            text(img, (x, 18), title, 18, bold=True)
            text(img, (x, 60 + tile + 10), sub, 14, fill=DIM)
        bar(img, R, sc, (pad, 60 + tile + 40), "R = 13 cells (kernel radius)", 13)
        text(img, (Wd - pad, 60 + tile + 40), f"t = {s / T:5.1f}", 16, anchor="ra")
        frames.append(img)
    media = write_media(frames, folder, "anatomy", fps=20, gif_width=800, gif_every=3, gif_colors=96)
    frames[0].save(folder / "anatomy-still.png", optimize=True)
    kimg = Image.fromarray(colorize(crop(K, 32) / K.max(), 10, "viridis"))
    kimg.save(folder / "kernel.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G011", "title": "Anatomy of one step",
        "media": media + ["anatomy-still.png", "kernel.png"],
        "frames": {"keep_every_steps": 1, "mp4_fps": 20, "time_compression": "2 tu per second"},
        "view": "64x64-cell window, integer-shifted to follow the centroid, 6 px per cell",
        "colormaps": {"A": "inferno 0..1", "U": "viridis 0..0.3",
                      "G": "RdBu_r -1..1", "kernel.png": "viridis, K / max K, 32x32 cells"},
        "caveats": ["U is clipped to 0..0.3 for display only; G is computed from the unclipped U.",
                    "Teaching exhibit, no claim. Rule = S001 (C001 family)."],
    }, [run])
    return [run]


# --- G010 ---------------------------------------------------------------------------------------

N10 = 256
SIDE10, AMP10 = 80, 0.3
SEEDS10 = range(40)
H10 = 100  # tu


def soup(seed: int) -> np.ndarray:
    """An 80x80 square of i.i.d. uniform [0, 0.3) values (numpy default_rng(seed)), centred on zero 256^2."""
    rng = np.random.default_rng(seed)
    A = np.zeros((N10, N10))
    o = (N10 - SIDE10) // 2
    A[o:o + SIDE10, o:o + SIDE10] = rng.random((SIDE10, SIDE10)) * AMP10
    return A


def soup_class(A, m1):
    m = A.sum() / R**2
    fill = (A > 0.1).mean()
    if m < 0.05 * m1:
        return "died"
    if fill > 0.15:
        return "filled"
    return f"{int(round(m / m1))} orbium-mass"


@exhibit("G010")
def g010(render: bool = True):
    import json as _json

    m1 = orbium_patch().sum() / R**2
    folder = EXHIBITS / "G010-soup"
    scan_path = folder / "soup-scan.json"
    if render or not scan_path.exists():
        table = []
        for seed in SEEDS10:
            run = Run(f"G010:scan:{seed}", S001_RULE, soup(seed), H10 * T, built=f"soup(seed={seed})")
            run.go(record=False)
            table.append({"seed": seed, "class": soup_class(run.final, m1), "mass_R2": run.final.sum() / R**2,
                          "final_state_sha256": run.final_sha})
            print("soup", seed, table[-1]["class"], flush=True)
        folder.mkdir(parents=True, exist_ok=True)
        scan_path.write_text(_json.dumps({"side": SIDE10, "amp": AMP10, "N": N10, "horizon_tu": H10,
                                          "orbium_mass_R2": m1, "rows": table}, indent=1) + "\n")
    table = _json.loads(scan_path.read_text())["rows"]
    pick = []
    for want in ("died", "orbium", "filled"):
        for r in table:
            if want in r["class"]:
                pick.append(r["seed"])
                break
    runs = []
    for seed in pick:
        run = Run(f"G010:seed{seed}", S001_RULE, soup(seed), H10 * T,
                  built=f"80x80 square of uniform [0, 0.3) noise, numpy default_rng({seed}).random, centred on zero 256^2",
                  keep_every=2)
        run.go(record=render, on_step=lambda sim, s: np.rint(sim.A * 255).astype(np.uint8))
        runs.append(run)
    if not render:
        return runs
    from collections import Counter

    counts = Counter("orbium" if "orbium" in r["class"] else r["class"] for r in table)
    names = {"died": "fades away", "orbium": "an Orbium-like glider is born", "filled": "takes over the world"}
    labels = []
    for seed in pick:
        cl = next(r["class"] for r in table if r["seed"] == seed)
        key = "orbium" if "orbium" in cl else cl
        labels.append(f"seed {seed}: {names[key]}")
    sc, pad, head = 2, 14, 32
    tile = N10 * sc
    Wd = 3 * tile + 4 * pad
    Hd = tile + head + 100
    frames = []
    for s in sorted(runs[0].frames):
        img = Image.new("RGB", (Wd, Hd), BG)
        text(img, (pad, 12), "Same recipe, three fates: random noise under the Orbium rule", 22, bold=True)
        text(img, (Wd - pad, 16), f"t = {s / T:5.1f}", 20, anchor="ra")
        for i, (run, lab) in enumerate(zip(runs, labels)):
            x = pad + i * (tile + pad)
            img.paste(Image.fromarray(colorize(run.frames[s] / 255.0, sc)), (x, 50 + head))
            text(img, (x, 56), lab, 17)
        text(img, (pad, 50 + head + tile + 14),
             f"Of {len(table)} noise seeds: {counts.get('died', 0)} fade away, {counts.get('orbium', 0)} leave "
             f"Orbium-sized survivors, {counts.get('filled', 0)} take over the world (t = {H10}).", 16, fill=DIM)
        frames.append(img)
    media = write_media(frames, folder, "soup", fps=25, gif_width=720, gif_every=3, gif_colors=64, crf=23)
    frames[-1].save(folder / "soup-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G010", "title": "Same recipe, three fates",
        "media": media + ["soup-final.png", "soup-scan.json"],
        "frames": {"keep_every_steps": 2, "mp4_fps": 25, "time_compression": "5 tu per second"},
        "view": f"three whole {N10}^2 periodic worlds, 2 px per cell",
        "scan": {"seeds": f"0..{len(table) - 1}", "counts": dict(counts),
                 "classes": "died: mass < 0.05 x one Orbium; filled: fill (A > 0.1) > 0.15; otherwise "
                            "'k orbium-mass' with k = round(mass / one Orbium's mass) (a mass count, not an identification)"},
        "picked": "the first seed of each class in seed order (not the prettiest)",
        "caveats": [
            "One noise recipe (80x80, uniform [0, 0.3)), one rule (S001), one world size; the counts are for this "
            "recipe only. Most other amplitudes we tried in a 6-seed pilot died out entirely.",
            "'Orbium-sized survivor' is a mass count; the film shows what it is for the picked seed only.",
            "The world-filling outcome resembles the reef lattice (G008) but happens here under the S001 rule, "
            "not the coexistence rule; we have not compared the two lattices.",
            "Random initial states as a way to find Lenia creatures are standard practice (Chan 2019); not novel.",
        ],
    }, runs)
    return runs
