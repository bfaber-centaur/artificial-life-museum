"""VIS-talk round three: Wolfram's Rule 90 (the Sierpinski triangle) inside Lenia, and its 2-D square.

G019  Rule 90 inside Lenia: a one-row Lenia world (poly kernel R = 2, exp growth mu 0.5, sigma 0.1,
      T = 1) grown from one cell is Rule 90 to within 1e-5; then the same seed while the rule is
      made continuous (wider sigma, smaller dt) -- the triangle survives dt = 1/2 and 1/4 and
      dissolves as sigma widens.
G020  Rule 90 squared: a 2-D Lenia world (poly kernel R = 2, poly growth centred on the weight of
      ONE diagonal neighbour, T = 1) grown from one cell. Every frame equals the outer product of
      two Rule 90 rows, exactly.

Both exhibits use ``alm.lenia.Lenia`` unchanged. The 1-D runs are 1 x N worlds: the kernel on a
one-row torus only sees offsets along the row. ECA reference rows are computed independently with
integer XOR and compared.

Usage: python film.py G019 G020   |   python film.py verify G019 G020
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from film import BG, DIM, EXHIBITS, Run, colorize, exhibit, save_provenance, text, write_media
from alm.lenia import Rule, kernel

# --- shared helpers ---------------------------------------------------------------------------


def rule90_rows(n: int, steps: int) -> np.ndarray:
    """Elementary CA Rule 90 from one centred cell on a ring of n cells, by integer XOR."""
    r = np.zeros((steps + 1, n), dtype=np.uint8)
    r[0, n // 2] = 1
    for t in range(steps):
        r[t + 1] = np.roll(r[t], 1) ^ np.roll(r[t], -1)
    return r


def one_cell(shape) -> np.ndarray:
    A = np.zeros(shape)
    A[shape[0] // 2, shape[1] // 2] = 1.0
    return A


def keep_row(sim, s):
    return sim.A[0].astype(np.float32).copy()


def spacetime(run: Run) -> np.ndarray:
    return np.stack([run.frames[s] for s in sorted(run.frames)])


# --- G019 -------------------------------------------------------------------------------------

N19 = 1024
STEPS19 = 511
R90_RULE = Rule(R=2, T=1, mu=0.5, sigma=0.1, kernel="poly", growth="exp")
MELT_T = (1, 2, 4)
MELT_SIGMA = (0.10, 0.17, 0.20, 0.30)
MELT_N, MELT_STEPS = 512, 255
SWEEP_SIGMA = tuple(round(0.10 + 0.0025 * i, 4) for i in range(81))  # 0.10 .. 0.30


def melt_run(T, sigma, steps=MELT_STEPS, n=MELT_N, tag="melt"):
    rule = Rule(R=2, T=T, mu=0.5, sigma=sigma, kernel="poly", growth="exp")
    return Run(f"G019:{tag}:T{T}:s{sigma}", rule, one_cell((1, n)), steps,
               built=f"one cell set to 1 at the centre of a zero 1 x {n} ring",
               rule_note="one-row world: the 2-D kernel on a 1 x N torus reduces to a 1-D kernel "
                         "(R = 2 poly core: weight 1/2 at offsets +-1, 0 elsewhere, including the cell itself)")


@exhibit("G019")
def g019(render: bool = True):
    main = Run("G019:rule90", R90_RULE, one_cell((1, N19)), STEPS19,
               built=f"one cell set to 1 at the centre of a zero 1 x {N19} ring",
               rule_note="one-row world: R = 2 poly kernel = weight 1/2 at offsets +-1, 0 at the cell itself")
    main.go(record=True, on_step=keep_row)
    runs = [main]
    melt = [melt_run(T, s) for T in MELT_T for s in MELT_SIGMA]
    for r in melt:
        r.go(record=True, on_step=keep_row)
    runs += melt
    sweep = [melt_run(1, s, tag="sweep") for s in SWEEP_SIGMA]
    for r in sweep:
        r.go(record=True, on_step=keep_row)
    runs += sweep
    if not render:
        return runs

    folder = EXHIBITS / "G019-rule-90-inside-lenia"
    ST = spacetime(main).astype(np.float64)
    ref = rule90_rows(N19, STEPS19).astype(np.float64)
    dev = float(np.abs(ST - ref).max())
    same_binarised = bool(((ST > 0.5) == (ref > 0.5)).all())

    # 1. the triangle, drawn top to bottom (rows = time)
    pad, head, foot = 16, 54, 34
    W = N19 + 2 * pad
    H = head + (STEPS19 + 1) + foot
    still = Image.new("RGB", (W, H), BG)
    text(still, (pad, 12), "Rule 90 inside Lenia: one cell, 511 steps", 20, bold=True)
    text(still, (pad, 36), "Each row is the whole 1-D world at one step; time runs downward. "
         "Lenia rule: R 2, T 1, mu 0.5, sigma 0.1 (exp growth).", 13, fill=DIM)
    still.paste(Image.fromarray(colorize(ST)), (pad, head))
    text(still, (pad, H - 26), f"Largest difference from Wolfram's Rule 90 over all {STEPS19 + 1} rows: "
         f"{dev:.1e} (cell values run 0 to 1).", 13, fill=DIM)
    folder.mkdir(parents=True, exist_ok=True)
    still.save(folder / "rule90-lenia.png", optimize=True)

    grow = []
    for s in range(0, STEPS19 + 1, 4):
        img = still.copy()
        arr = np.array(img)
        arr[head + s + 1: head + STEPS19 + 1, pad:pad + N19] = BG
        grow.append(Image.fromarray(arr))
    grow += [still] * 30

    # 2. melt grid: rows T, columns sigma
    cw = MELT_N // 2  # crop the central half of the ring: the light cone never leaves it
    gpad, ghead, lab = 12, 58, 22
    Wg = len(MELT_SIGMA) * cw + (len(MELT_SIGMA) + 1) * gpad + 70
    Hg = ghead + len(MELT_T) * (MELT_STEPS + 1 + lab + gpad) + 30
    grid = Image.new("RGB", (Wg, Hg), BG)
    text(grid, (gpad, 12), "Melting the triangle: same seed, rule made more continuous", 20, bold=True)
    text(grid, (gpad, 38), "Across: wider growth bump (sigma). Down: smaller time step (dt = 1/T). "
         "Top-left is Rule 90.", 13, fill=DIM)
    for i, T in enumerate(MELT_T):
        for j, sg in enumerate(MELT_SIGMA):
            r = melt[i * len(MELT_SIGMA) + j]
            st = spacetime(r)[:, MELT_N // 2 - cw // 2: MELT_N // 2 + cw // 2]
            x = 70 + gpad + j * (cw + gpad)
            y = ghead + i * (MELT_STEPS + 1 + lab + gpad)
            text(grid, (x, y + 2), f"sigma {sg}", 13)
            grid.paste(Image.fromarray(colorize(st)), (x, y + lab))
        text(grid, (gpad, ghead + i * (MELT_STEPS + 1 + lab + gpad) + lab + MELT_STEPS // 2),
             f"dt 1/{T}", 14, bold=True)
    text(grid, (gpad, Hg - 24), "Each panel: 256 steps from one cell, central 256 cells of a 512-cell ring.",
         13, fill=DIM)
    grid.save(folder / "melt-grid.png", optimize=True)

    # 3. the sweep film: sigma 0.10 -> 0.30 at dt = 1, one full space-time diagram per frame
    sw = []
    for sg, r in zip(SWEEP_SIGMA, sweep):
        st = spacetime(r)
        img = Image.new("RGB", (MELT_N + 2 * pad, MELT_STEPS + 1 + 90), BG)
        text(img, (pad, 12), "Widening the growth bump, dt = 1", 18, bold=True)
        text(img, (img.width - pad, 14), f"sigma = {sg:.4f}", 16, anchor="ra")
        img.paste(Image.fromarray(colorize(st)), (pad, 44))
        text(img, (pad, img.height - 34), "sigma <= 0.15: exactly Rule 90.  Wider: more cells grow, "
             "values stop being 0 or 1, the fractal dissolves.", 12, fill=DIM)
        sw.append(img)
    sw = [sw[0]] * 12 + sw + [sw[-1]] * 12 + sw[::-1]

    media = write_media(grow, folder, "rule90-grows", fps=25, gif_width=640, gif_every=2, gif_colors=32)
    media += write_media(sw, folder, "melt-sweep", fps=12, gif_width=540, gif_colors=64)
    save_provenance(folder, {
        "exhibit": "G019", "title": "Rule 90 inside Lenia",
        "media": media + ["rule90-lenia.png", "melt-grid.png"],
        "rule90_check": {"reference": "integer XOR of left and right neighbours on the same ring",
                         "max_abs_difference": dev, "identical_after_threshold_0.5": same_binarised,
                         "steps": STEPS19},
        "why_it_works": "R = 2 poly kernel core is zero at r = 0 and r = 1, so on a 1-D ring it puts weight "
                        "1/2 on each nearest neighbour and none on the cell. U is 0, 1/2 or 1. With T = 1, "
                        "A <- clip(A + G(U)) gives 1 when G(U) ~ +1 (U = 1/2, one neighbour on) and 0 when "
                        "G(U) ~ -1 -- exactly Rule 90. exp growth leaves residues of order 2e^(-12.5) ~ 7e-6.",
                        "view": "space-time diagrams: x = cell, y = step (downward); inferno, nearest-neighbour",
        "caveats": [
            "Classic Lenia's radially symmetric kernel cannot express left-right asymmetric rules such as "
            "Rule 30 or Rule 110 exactly; see claim C061 for the set that the discrete limit reaches.",
            "T = 1 (dt = 1) is far outside the usual Lenia regime (T = 10 for Orbium); this is the discrete limit "
            "Chan 2019 sec. 2.1.6 uses to embed Game of Life.",
        ],
    }, runs)
    return runs


# --- G020 -------------------------------------------------------------------------------------

N20 = 512
STEPS20 = 255


def diag_rule() -> Rule:
    k = kernel((N20, N20), Rule(R=2))
    return Rule(R=2, T=1, mu=float(k[1, 1]), sigma=0.004, kernel="poly", growth="poly")


def u8_full(sim, s):
    return sim.A.astype(np.float32).copy()


@exhibit("G020")
def g020(render: bool = True):
    rule = diag_rule()
    run = Run("G020:diag", rule, one_cell((N20, N20)), STEPS20,
              built=f"one cell set to 1 at the centre of a zero {N20}^2 torus",
              rule_note="mu is set to the normalised kernel weight of ONE diagonal neighbour (k[1,1]); "
                        "sigma 0.004 poly growth makes G = -1 exactly for every other neighbour sum")
    run.go(record=render, on_step=u8_full)
    if not render:
        return [run]
    folder = EXHIBITS / "G020-rule-90-squared"
    folder.mkdir(parents=True, exist_ok=True)

    r90 = rule90_rows(N20, STEPS20).astype(np.float64)
    worst, binary = 0.0, True
    for s in sorted(run.frames):
        F = run.frames[s].astype(np.float64)
        worst = max(worst, float(np.abs(F - np.outer(r90[s], r90[s])).max()))
        binary &= bool(np.all((F == 0) | (F == 1)))

    def pool(F):  # 2 x 2 blocks -> one pixel (max); live cells sit on a checkerboard, so this hides it
        return F.reshape(N20 // 2, 2, N20 // 2, 2).max(axis=(1, 3))

    view = N20 // 2
    pad, head = 16, 70
    sc = 3
    frames = []
    for s in sorted(run.frames):
        img = Image.new("RGB", (view * sc + 2 * pad, head + view * sc + 40), BG)
        text(img, (pad, 12), "Rule 90 squared: one cell, one rule, in 2-D Lenia", 20, bold=True)
        text(img, (pad, 40), "A cell is full next step only if exactly one of its four diagonal neighbours "
             "is full now.", 13, fill=DIM)
        text(img, (img.width - pad, 16), f"step {s:3d}", 18, anchor="ra")
        img.paste(Image.fromarray(colorize(pool(run.frames[s]), sc)), (pad, head))
        text(img, (pad, img.height - 30), "Every frame equals (Rule 90 row) x (Rule 90 row), exactly. "
             "At steps 2^k it collapses to four cells.", 13, fill=DIM)
        frames.append(img)
    hold = [frames[-1]] * 25
    media = write_media(frames + hold, folder, "rule90-squared", fps=10, gif_width=560, gif_colors=16)
    for s in (63, 64, 100, 191, 255):
        frames[s].save(folder / f"rule90-squared-step{s}.png", optimize=True)

    # time exposure: how many of the 256 frames each 2 x 2 block was full in (log scale)
    count = sum(run.frames[s].astype(np.float64) for s in sorted(run.frames))
    count = count.reshape(N20 // 2, 2, N20 // 2, 2).sum(axis=(1, 3))
    expo = np.log1p(count) / np.log1p(count).max()
    img = Image.new("RGB", (view * sc + 2 * pad, head + view * sc + 40), BG)
    text(img, (pad, 12), "Rule 90 squared, time exposure (steps 0-255)", 20, bold=True)
    text(img, (pad, 40), "Brightness = how many steps each 2 x 2 block held a full cell (log scale).",
         13, fill=DIM)
    img.paste(Image.fromarray(colorize(expo, sc)), (pad, head))
    img.save(folder / "rule90-squared-exposure.png", optimize=True)

    save_provenance(folder, {
        "exhibit": "G020", "title": "Rule 90 squared",
        "media": media + [f"rule90-squared-step{s}.png" for s in (63, 64, 100, 191, 255)]
                 + ["rule90-squared-exposure.png"],
        "outer_product_check": {"claim": "A_t(y, x) == r_t(y) * r_t(x), r_t = Rule 90 row from one cell",
                                "max_abs_difference_all_steps": worst, "all_frames_exactly_0_or_1": binary},
        "why_it_works": "With A_t = a(y) a(x), the diagonal-neighbour sum factorises as "
                        "(a(y-1) + a(y+1)) (a(x-1) + a(x+1)); it equals exactly 1 iff both factors equal 1, "
                        "i.e. iff Rule 90 turns on both coordinates.",
        "view": f"whole {N20}^2 torus; each pixel block is a 2 x 2 block of cells (max for frames, sum for the "
                "exposure), {sc} px per block; inferno",
        "caveats": ["T = 1 discrete limit, as in G019; not a regime where Lenia's gliders live."],
    }, [run])
    return [run]
