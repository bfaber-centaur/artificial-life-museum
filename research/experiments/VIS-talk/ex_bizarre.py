"""Round two, 'bizarre': G014 kaleidoscope, G015 map of worlds, G016 live mutation, G017 rush hour,
G018 the invisible wall.

G015, G016 and G018 change the rule in space or time, which ``alm.lenia.Lenia`` cannot do.
``FieldLenia`` below repeats its step exactly (same ``alm.lenia.kernel`` and ``alm.lenia.growth``,
Euler + clip, float64) but takes mu and sigma as arrays or as functions of the step.
``equivalence_check`` shows that with uniform parameters it is bitwise equal to ``Lenia``; each
of those exhibits records the result in its provenance.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from film import (BG, DIM, EXHIBITS, INK, S001_RULE, Run, bar, colorize, crop, exhibit, paste, roll_to_centre,
                  save_provenance, text, write_media)
from alm.lenia import Lenia, Rule, growth, kernel

import ex_orbium as eo

R, T = S001_RULE.R, S001_RULE.T


class FieldLenia:
    """Lenia step with mu, sigma given as scalars, arrays (same shape as A) or callables t -> (mu, sigma)."""

    def __init__(self, rule: Rule, A: np.ndarray, mu, sigma=None):
        self.rule = rule
        self.A = np.array(A, dtype=np.float64, copy=True)
        self.t = 0
        self._khat = np.fft.rfft2(kernel(self.A.shape, rule))
        self.mu, self.sigma = mu, sigma

    def params(self):
        if callable(self.mu):
            return self.mu(self.t)
        return self.mu, self.sigma

    def potential(self):
        return np.fft.irfft2(np.fft.rfft2(self.A) * self._khat, s=self.A.shape)

    def step(self):
        mu, sigma = self.params()
        G = growth(self.rule.growth, self.potential(), mu, sigma)
        self.A = np.clip(self.A + G * self.rule.dt, 0.0, 1.0)
        self.t += 1
        return G


def equivalence_check(steps: int = 200) -> bool:
    A = np.zeros((128, 128))
    paste(A, eo.orbium_patch(), 64, 64)
    a, b = Lenia(S001_RULE, A), FieldLenia(S001_RULE, A, np.full(A.shape, S001_RULE.mu), np.full(A.shape, S001_RULE.sigma))
    c = FieldLenia(S001_RULE, A, lambda t: (S001_RULE.mu, S001_RULE.sigma))
    for _ in range(steps):
        a.step(), b.step(), c.step()
    return bool(np.array_equal(a.A, b.A) and np.array_equal(a.A, c.A))


EQUIV_NOTE = ("FieldLenia (ex_bizarre.py) repeats alm.lenia.Lenia's step with mu, sigma as arrays or functions of "
              "the step; with uniform S001 parameters it equals Lenia bitwise over 200 steps (checked at render: {})")


def u8(sim, s):
    return np.rint(sim.A * 255).astype(np.uint8)


# --- G014 kaleidoscope ---------------------------------------------------------------------------

def d4_soup(seed: int = 4, s: int = 40, amp: float = 0.3, N: int = 256) -> np.ndarray:
    """An 80x80 patch of uniform [0, amp) noise made exactly symmetric under the 8 symmetries of the square."""
    rng = np.random.default_rng(seed)
    q = rng.random((s, s)) * amp
    q = np.triu(q) + np.triu(q, 1).T
    P = np.zeros((2 * s, 2 * s))
    P[s:, s:], P[s:, :s], P[:s, s:], P[:s, :s] = q, q[:, ::-1], q[::-1], q[::-1, ::-1]
    A = np.zeros((N, N))
    o = N // 2 - s
    A[o:o + 2 * s, o:o + 2 * s] = P
    return A


def asym(A):
    return np.maximum(np.abs(A - np.rot90(A)), np.abs(A - A.T))


@exhibit("G014")
def g014(render: bool = True):
    A0 = d4_soup()
    assert np.array_equal(A0, np.rot90(A0)) and np.array_equal(A0, A0.T)
    series = []

    def grab(sim, s):
        d = asym(sim.A)
        series.append((s / T, float(d.max()), float(sim.A.sum()) / R**2))
        return (np.rint(sim.A * 255).astype(np.uint8), np.log10(np.maximum(d, 1e-17)).astype(np.float32))

    run = Run("G014:d4-soup-seed4", S001_RULE, A0, 80 * T,
              built="d4_soup(seed=4): 40x40 uniform [0, 0.3) block (numpy default_rng(4)), symmetrised across the "
                    "diagonal and mirrored into an 80x80 patch with all 8 square symmetries, centred on zero 256^2",
              keep_every=2)
    run.go(record=render, on_step=grab)
    if not render:
        return [run]
    folder = EXHIBITS / "G014-kaleidoscope"
    sc, pad = 2, 16
    tile = 256 * sc
    frames = []
    for s in sorted(run.frames):
        A, L = run.frames[s]
        img = Image.new("RGB", (2 * tile + 3 * pad, tile + 130), BG)
        text(img, (pad, 12), "A perfectly symmetric world, broken by rounding error", 22, bold=True)
        text(img, (2 * tile + 2 * pad, 16), f"t = {s / T:5.1f}", 20, anchor="ra")
        img.paste(Image.fromarray(colorize(A / 255.0, sc)), (pad, 56))
        img.paste(Image.fromarray(colorize(L, sc, "viridis", -16, 0)), (2 * pad + tile, 56))
        text(img, (pad, 56 + tile + 10), "the world", 15, fill=DIM)
        m = float(10 ** L.max())
        text(img, (2 * pad + tile, 56 + tile + 10),
             f"how far it is from its own mirror image, log scale 1e-16 (dark) to 1 (yellow); max {m:.0e}", 15,
             fill=DIM)
        frames.append(img)
    media = write_media(frames, folder, "kaleidoscope", fps=20, gif_width=640, gif_every=3, gif_colors=96)
    for t_still in (10, 30, 50):
        k = min(run.frames, key=lambda s: abs(s - t_still * T))
        frames[sorted(run.frames).index(k)].save(folder / f"kaleidoscope-t{t_still}.png", optimize=True)
    np.savetxt(folder / "asymmetry.csv", np.array(series), delimiter=",", header="t_tu,max_asymmetry,mass_R2",
               comments="", fmt="%.6g")
    save_provenance(folder, {
        "exhibit": "G014", "title": "A perfectly symmetric world, broken by rounding error",
        "media": media + ["kaleidoscope-t10.png", "kaleidoscope-t30.png", "kaleidoscope-t50.png", "asymmetry.csv"],
        "frames": {"keep_every_steps": 2, "mp4_fps": 20, "time_compression": "4 tu per second"},
        "view": "whole 256^2 world, 2 px per cell; right panel max(|A - rot90 A|, |A - A^T|) per cell, log10, "
                "viridis from -16 to 0 (values below 1e-16, including exact zeros, shown as -16)",
        "measured": "max asymmetry 0 at t = 0, about 2e-13 at 5 tu, 3e-10 at 15 tu, 2e-5 at 25 tu, 1 by 40 tu "
                    "(asymmetry.csv; growth roughly 30x per 5 tu while the colony grows)",
        "caveats": [
            "The rule and the initial state are exactly symmetric, so in exact arithmetic the world stays symmetric. "
            "The symmetry is broken by floating-point rounding in the FFT convolution (float64, numpy pocketfft) and "
            "then amplified. Another FFT library or summation order would break it differently.",
            "One seed; in a 24-run pilot of D4 soups (seeds 0-11 at amplitudes 0.3 and 0.35), 8 filled the world and "
            "16 died out, and every survivor was fully asymmetric (max difference 1) by 100 tu.",
            "The world-filling lattice is the same kind of state as G010's filled soups (C056).",
        ],
    }, [run])
    return [run]


# --- G015 map of worlds -----------------------------------------------------------------------------

N15, H15 = 1024, 200
MU15, K15 = (0.10, 0.40), (0.08, 0.22)  # mu along x, sigma/mu along y, over the displayed quadrant


def map_fields(N=N15):
    w = (1 - np.cos(2 * np.pi * np.arange(N) / N)) / 2  # 0 at the edge, 1 at the middle: periodic, no seam
    mu = MU15[0] + (MU15[1] - MU15[0]) * w[None, :] * np.ones((N, 1))
    k = K15[0] + (K15[1] - K15[0]) * w[:, None] * np.ones((1, N))
    return mu, mu * k


@exhibit("G015")
def g015(render: bool = True):
    mu, sig = map_fields()
    A0 = np.random.default_rng(0).random((N15, N15)) * 0.5
    h = N15 // 2
    run = Run("G015:map-of-worlds", S001_RULE, A0, H15 * T,
              built="uniform [0, 0.5) noise over the whole 1024^2 world, numpy default_rng(0)",
              keep_every=10, make_sim=lambda A: FieldLenia(S001_RULE, A, mu, sig),
              rule_note="S001 kernel (R 13, poly, beta [1]) and poly growth, but mu and sigma vary in space: "
                        "mu = 0.10 + 0.30 w(x), sigma = mu (0.08 + 0.14 w(y)), w(z) = (1 - cos(2 pi z / 1024)) / 2")
    run.go(record=render, on_step=lambda sim, s: np.rint(sim.A[:h, :h] * 255).astype(np.uint8))
    if not render:
        return [run]
    eq = equivalence_check()
    folder = EXHIBITS / "G015-map-of-worlds"
    left, top, bottom = 70, 56, 64
    frames = []
    for s in sorted(run.frames):
        img = Image.new("RGB", (left + h + 16, top + h + bottom), BG)
        img.paste(Image.fromarray(colorize(run.frames[s] / 255.0)), (left, top))
        text(img, (16, 12), "One world, a different rule at every point", 22, bold=True)
        text(img, (left + h, 16), f"t = {s / T:5.1f}", 18, anchor="ra")
        # tick labels at the true mu of those columns (cosine spacing)
        for col in (0, h // 4, h // 2, 3 * h // 4, h - 1):
            m = float(mu[0, col])
            text(img, (left + col, top + h + 6), f"{m:.2f}", 12, fill=DIM, anchor="ma")
        text(img, (left + h // 2, top + h + 28), "growth centre mu  (left to right)", 14, anchor="ma")
        for row in (0, h // 4, h // 2, 3 * h // 4, h - 1):
            k = float(sig[row, 0] / mu[row, 0])
            text(img, (left - 6, top + row - 6), f"{k:.2f}", 12, fill=DIM, anchor="ra")
        text(img, (6, top + h + 28), "sigma/mu", 12, fill=DIM)
        frames.append(img)
    media = write_media(frames, folder, "map-of-worlds", fps=20, gif_width=480, gif_every=2, gif_colors=64, crf=24)
    frames[-1].save(folder / "map-of-worlds-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G015", "title": "One world, a different rule at every point",
        "media": media + ["map-of-worlds-final.png"],
        "frames": {"keep_every_steps": 10, "mp4_fps": 20, "time_compression": "20 tu per second"},
        "view": "top-left 512^2 quadrant of the 1024^2 world (rows and columns 0-511), where mu and sigma/mu both "
                "rise monotonically; 1 px per cell. The other three quadrants mirror the parameter ramp.",
        "equivalence": EQUIV_NOTE.format(eq),
        "caveats": [
            "Not classic Lenia: the rule changes from cell to cell. Patterns near one point feel parameters up to "
            "R = 13 cells away, so a region is not an isolated world with that point's rule; boundaries between "
            "regimes are shaped by the gradient itself.",
            "Tick labels give the exact mu and sigma/mu of the labelled column and row; spacing is cosine, not linear.",
            "Chan 2019 maps where Orbium survives in (mu, sigma); this picture is a different thing (what random noise "
            "turns into), from one seed and one horizon (200 tu). We did not search the literature for spatially "
            "varying Lenia parameters beyond the project's reference list.",
        ],
    }, [run])
    return [run]


# --- G016 live mutation ------------------------------------------------------------------------------

H16 = 150
RAMPS = {"mu": (0.15, 0.11), "sigma": (0.015, 0.035)}


def ramp(kind):
    a, b = RAMPS[kind]
    n = H16 * T

    def f(t):
        x = a + (b - a) * min(t, n) / n
        return (x, S001_RULE.sigma) if kind == "mu" else (S001_RULE.mu, x)
    return f


@exhibit("G016")
def g016(render: bool = True):
    P = eo.orbium_patch()
    runs = []
    for kind in ("mu", "sigma"):
        A0 = np.zeros((256, 256))
        paste(A0, P, 128, 128)
        f = ramp(kind)
        a, b = RAMPS[kind]
        run = Run(f"G016:{kind}-ramp", S001_RULE, A0, H16 * T,
                  built="settled S001 Orbium (48^2 crop) pasted centred on zero 256^2", keep_every=3,
                  make_sim=lambda A, f=f: FieldLenia(S001_RULE, A, f),
                  rule_note=f"S001 rule with {kind} ramped linearly from {a} at step 0 to {b} at step {H16 * T}; "
                            f"the step uses the value at its own step index")
        run.go(record=render, on_step=u8)
        runs.append(run)
    if not render:
        return runs
    eq = equivalence_check()
    folder = EXHIBITS / "G016-live-mutation"
    sc, pad = 2, 16
    tile = 256 * sc
    frames = []
    for s in sorted(runs[0].frames):
        img = Image.new("RGB", (2 * tile + 3 * pad, tile + 110), BG)
        text(img, (pad, 12), "Changing the laws of physics under a living creature", 22, bold=True)
        text(img, (2 * tile + 2 * pad, 16), f"t = {s / T:5.1f}", 20, anchor="ra")
        for i, (run, kind) in enumerate(zip(runs, ("mu", "sigma"))):
            x = pad + i * (tile + pad)
            img.paste(Image.fromarray(colorize(run.frames[s] / 255.0, sc)), (x, 56))
            m, sg = ramp(kind)(s)
            lab = f"growth centre mu = {m:.4f} (falling)" if kind == "mu" else f"growth width sigma = {sg:.4f} (rising)"
            text(img, (x, 56 + tile + 10), lab, 16)
        frames.append(img)
    media = write_media(frames, folder, "live-mutation", fps=25, gif_width=720, gif_every=3, gif_colors=96)
    frames[-1].save(folder / "live-mutation-final.png", optimize=True)
    for run, kind in zip(runs, ("mu", "sigma")):
        np.savetxt(folder / f"mass-{kind}.csv", np.c_[np.arange(len(run.mass)) / T, run.mass], delimiter=",",
                   header="t_tu,mass_R2", comments="", fmt="%.6g")
    save_provenance(folder, {
        "exhibit": "G016", "title": "Changing the laws of physics under a living creature",
        "media": media + ["live-mutation-final.png", "mass-mu.csv", "mass-sigma.csv"],
        "frames": {"keep_every_steps": 3, "mp4_fps": 25, "time_compression": "7.5 tu per second"},
        "view": "whole 256^2 worlds, 2 px per cell",
        "equivalence": EQUIV_NOTE.format(eq),
        "caveats": [
            "The rule changes during the run; the creature is never at equilibrium with it, so its shape at a given "
            "mu or sigma is not the shape a creature would settle to at that fixed rule.",
            "One ramp rate each. In a prototype, the mu ramp kept a single Orbium until mu ~ 0.114, then gave a "
            "two-lobed body and a world-filling lattice; the sigma ramp kept it until sigma ~ 0.022, then filled.",
            "Gradual parameter change as a way to morph Lenia creatures is Chan's own method (2019 sec. 2.3.2).",
        ],
    }, runs)
    return runs


# --- G017 rush hour ------------------------------------------------------------------------------------

N17, H17, COUNT17 = 512, 120, 30


def rush_state(seed=0):
    P = eo.orbium_patch()
    rng = np.random.default_rng(seed)
    A = np.zeros((N17, N17))
    placed = []
    while len(placed) < COUNT17:
        r, tr = int(rng.integers(4)), bool(rng.random() < 0.5)
        Q = np.rot90(P, r)
        Q = Q.T if tr else Q
        y, x = int(rng.integers(N17)), int(rng.integers(N17))
        try:
            paste(A, Q, y, x)
        except ValueError:
            continue
        placed.append((y, x, r, tr))
    return A, placed


@exhibit("G017")
def g017(render: bool = True):
    A0, placed = rush_state()
    run = Run("G017:rush-hour", S001_RULE, A0, H17 * T,
              built=f"{COUNT17} copies of the settled S001 Orbium (48^2 crop), each rotated by a multiple of 90 deg and "
                    f"optionally transposed, at random positions (numpy default_rng(0); overlapping supports "
                    f"rejected and redrawn) on zero {N17}^2",
              keep_every=2)
    run.go(record=render, on_step=u8)
    if not render:
        return [run]
    folder = EXHIBITS / "G017-rush-hour"
    sc = 1.5
    w = int(N17 * sc)
    frames = []
    for s in sorted(run.frames):
        img = Image.new("RGB", (w, w + 56), BG)
        img.paste(Image.fromarray(colorize(run.frames[s] / 255.0, 3)).resize((w, w), Image.Resampling.NEAREST), (0, 56))
        text(img, (14, 12), f"Rush hour: {COUNT17} Orbia, one rule, no traffic lights", 22, bold=True)
        text(img, (w - 14, 16), f"t = {s / T:5.1f}", 20, anchor="ra")
        frames.append(img)
    media = write_media(frames, folder, "rush-hour", fps=25, gif_width=480, gif_every=3, gif_colors=64, crf=24)
    k = min(run.frames, key=lambda s: abs(s - 30 * T))
    frames[sorted(run.frames).index(k)].save(folder / "rush-hour-t30.png", optimize=True)
    np.savetxt(folder / "mass.csv", np.c_[np.arange(len(run.mass)) / T, run.mass], delimiter=",",
               header="t_tu,mass_R2", comments="", fmt="%.6g")
    save_provenance(folder, {
        "exhibit": "G017", "title": "Rush hour",
        "media": media + ["rush-hour-t30.png", "mass.csv"],
        "frames": {"keep_every_steps": 2, "mp4_fps": 25, "time_compression": "5 tu per second"},
        "view": f"whole {N17}^2 world, 1.5 px per cell (nearest neighbour)",
        "placements_y_x_rot_transpose": placed,
        "caveats": [
            "One random arrangement. Which collision detonates first, and when, depends on it.",
            "Transposing the Orbium mirrors it; mirror images are exact symmetries of the square-grid kernel.",
            "Detonation is one of Chan's collision outcomes (2019 sec. 3.5.5); the colony is the same kind of frozen "
            "lattice as G010's filled soups.",
        ],
    }, [run])
    return [run]


# --- G018 the invisible wall -----------------------------------------------------------------------------

WALL_MU = (0.12, 0.13, 0.14, 0.16, 0.17, 0.18)
H18 = 120


@exhibit("G018")
def g018(render: bool = True):
    P = eo.orbium_patch()
    N = 256
    runs = []
    for X in WALL_MU:
        mu = np.full((N, N), S001_RULE.mu)
        mu[N // 2:, :] = X
        sig = np.full((N, N), S001_RULE.sigma)
        A0 = np.zeros((N, N))
        paste(A0, P, 40, 128)
        run = Run(f"G018:mu{X}", S001_RULE, A0, H18 * T,
                  built="settled S001 Orbium (48^2 crop) pasted at row 40, column 128 of zero 256^2, heading mostly down",
                  keep_every=3, make_sim=lambda A, mu=mu, sig=sig: FieldLenia(S001_RULE, A, mu, sig),
                  rule_note=f"S001 rule in rows 0-127; mu = {X} (sigma unchanged) in rows 128-255. The torus wraps, "
                            f"so there are two walls, at rows 128 and 0")
        run.go(record=render, on_step=u8)
        runs.append(run)
    if not render:
        return runs
    eq = equivalence_check()
    folder = EXHIBITS / "G018-invisible-wall"
    m1 = P.sum() / R**2
    fates = ["crosses and keeps going" if r.final.sum() / R**2 > 0.5 * m1 else "dies at the wall" for r in runs]
    cols, pad, head = 3, 12, 28
    tile = 256 * 1
    sc = 1.4
    tl = int(tile * sc)
    Wd = cols * tl + (cols + 1) * pad
    Hd = 52 + 2 * (tl + head + pad) + 30
    frames = []
    for s in sorted(runs[0].frames):
        img = Image.new("RGB", (Wd, Hd), BG)
        text(img, (pad, 12), "An invisible wall: the lower half has a slightly different rule", 20, bold=True)
        text(img, (Wd - pad, 16), f"t = {s / T:5.1f}", 18, anchor="ra")
        for i, (run, X) in enumerate(zip(runs, WALL_MU)):
            r, c = divmod(i, cols)
            x = pad + c * (tl + pad)
            y = 52 + r * (tl + head + pad)
            im = Image.fromarray(colorize(run.frames[s] / 255.0, 2)).resize((tl, tl), Image.Resampling.NEAREST)
            # tint the lower half very slightly so the wall is visible
            arr = np.array(im).astype(np.int16)
            arr[tl // 2:] = np.clip(arr[tl // 2:] + np.array([0, 10, 22]), 0, 255)
            img.paste(Image.fromarray(arr.astype(np.uint8)), (x, y + head))
            text(img, (x, y + 6), f"upper mu 0.15, lower mu {X}", 14)
        text(img, (pad, Hd - 24), "Blue-tinted half: the other rule. Final fates: " +
             ", ".join(f"{X}: {'crosses' if 'crosses' in f else 'dies'}" for X, f in zip(WALL_MU, fates)), 13, fill=DIM)
        frames.append(img)
    media = write_media(frames, folder, "invisible-wall", fps=25, gif_width=640, gif_every=3, gif_colors=64)
    frames[-1].save(folder / "invisible-wall-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G018", "title": "The invisible wall",
        "media": media + ["invisible-wall-final.png"],
        "frames": {"keep_every_steps": 3, "mp4_fps": 25, "time_compression": "7.5 tu per second"},
        "view": "six whole 256^2 worlds, 2.8 px per cell; the lower half is tinted blue (overlay only)",
        "equivalence": EQUIV_NOTE.format(eq),
        "fates_at_120_tu": dict(zip([str(x) for x in WALL_MU], fates)),
        "fate_rule": "final mass > 0.5 x one Orbium's mass -> 'crosses and keeps going', else 'dies at the wall'",
        "caveats": [
            "A sharp step in mu between neighbouring cells; the Orbium feels the other rule up to R = 13 cells "
            "before reaching the wall. One phase, one approach angle per lane.",
            "A survivor only shows that a body with Orbium's mass persisted; it may have changed shape in the other half.",
        ],
    }, runs)
    return runs
