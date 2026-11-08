"""G008: the reef, filmed at N1024 (four times the area of the expedition's largest world)."""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image

from film import (BG, COEX_RULE, DIM, EXHIBITS, INK, REPO, Run, bar, colorize, exhibit, save_provenance,
                  text, write_media)

FIELD = REPO / "research" / "experiments" / "REEF-field"
sys.path.insert(0, str(FIELD))
sys.path.insert(0, str(FIELD.parent / "L6-field"))

N = 1024
H_TU = 130
P2 = {"snapshot": "GA", "ring_shift": [64, 20]}  # jobs-pilots.json, pilot P2 (head-on, b/R 0.02)


def build() -> np.ndarray:
    from runner import build as reef_build

    G, S, _, _ = reef_build(P2["snapshot"], P2["ring_shift"], N)
    return G + S


@exhibit("G008")
def g008(render: bool = True):
    A0 = build()
    steps = H_TU * COEX_RULE.T
    run = Run("REEF-P2-N1024", COEX_RULE, A0, steps,
              built="REEF-field runner.build('GA', ring_shift=[64, 20], N=1024): pilot P2 geometry "
                    "(head-on, b/R 0.02) from jobs-pilots.json, glider snapshot GA and S103 seeds embedded "
                    "centred in a zero 1024^2 world",
              keep_every=3)
    run.go(record=render, on_step=lambda sim, s: np.rint(sim.A * 255).astype(np.uint8))
    if not render:
        return [run]
    folder = EXHIBITS / "G008-the-reef"
    R = COEX_RULE.R
    T = COEX_RULE.T
    steps_kept = sorted(run.frames)

    # (a) world film: whole 1024^2 torus, 1 px per cell, plus caption band
    frames = []
    for s in steps_kept:
        A = run.frames[s] / 255.0
        img = Image.new("RGB", (N, N + 60), BG)
        img.paste(Image.fromarray(colorize(A)), (0, 60))
        text(img, (16, 12), "One glider meets one ring", 26, bold=True)
        text(img, (N - 16, 16), f"t = {s / T:5.1f}", 22, anchor="ra")
        bar(img, 10 * R, 1, (N - 16 - 10 * R, 40), "10 R", 12)
        frames.append(img)
    media = write_media(frames, folder, "reef-world", fps=30, gif_width=400, gif_every=3, gif_colors=64, crf=26)

    # (b) first contact close-up: 200^2 crop around the meeting point, 4x, 0-24 tu
    cy, cx = N // 2 + 40, N // 2 + 16
    hw = 100
    close = []
    for s in steps_kept:
        if s > 24 * T:
            break
        A = run.frames[s][cy - hw:cy + hw, cx - hw:cx + hw] / 255.0
        img = Image.new("RGB", (800, 860), BG)
        img.paste(Image.fromarray(colorize(A, 4)), (0, 60))
        text(img, (16, 12), "First contact", 26, bold=True)
        text(img, (784, 16), f"t = {s / T:5.1f}", 22, anchor="ra")
        bar(img, R, 4, (784 - 4 * R, 40), "R", 12)
        close.append(img)
    media += write_media(close, folder, "reef-contact", fps=15, gif_width=600, gif_colors=128)

    # (c) stills: final world, and a 160^2 detail of the frozen lattice behind the front
    last = run.frames[steps_kept[-1]] / 255.0
    Image.fromarray(colorize(last)).save(folder / "reef-world-final.png", optimize=True)
    d = last[N // 2 - 80:N // 2 + 80, N // 2 - 280:N // 2 - 120]
    Image.fromarray(colorize(d, 5)).save(folder / "reef-lattice-detail.png", optimize=True)
    mid = run.frames[min(steps_kept, key=lambda s: abs(s - 60 * T))] / 255.0
    Image.fromarray(colorize(mid)).save(folder / "reef-world-t60.png", optimize=True)
    np.savetxt(folder / "mass.csv", np.c_[np.arange(steps + 1) / T, run.mass], delimiter=",",
               header="t_tu,mass_sumA_over_R2", comments="", fmt="%.6g")
    save_provenance(folder, {
        "exhibit": "G008", "title": "The reef: one glider meets one ring",
        "media": media + ["reef-world-final.png", "reef-world-t60.png", "reef-lattice-detail.png", "mass.csv"],
        "frames": {"keep_every_steps": 3, "mp4_fps": {"reef-world": 30, "reef-contact": 15},
                   "time_compression": "reef-world 9 tu per second; reef-contact 4.5 tu per second",
                   "gif": "reef-world GIF is downsized to 400 px (Lanczos), every 3rd kept frame, 64 colours; use the MP4 on a projector"},
        "view": {"reef-world": "whole 1024^2 periodic world, 1 px per cell",
                 "reef-contact": "200x200-cell window at rows 452-652, cols 428-628, 4 px per cell, 0-24 tu",
                 "reef-lattice-detail": "160x160 cells at rows 432-592, cols 232-392 at t = 130 tu, 5 px per cell"},
        "claims": ["C052", "C053", "C054", "C055"],
        "caveats": [
            "Same P2 encounter geometry as the expedition, but in a 1024^2 world that the expedition never ran. "
            "The checked result (C052) covers contact, fusion and ignition within 3-25 tu at N256/N512; "
            "everything after 25 tu here is alm-only and unchecked by a second arithmetic route.",
            "Ignition timing and colony mass are NUMERICALLY_FRAGILE in T and R (C053); the film shows R13, T10 only.",
            "Not novel as a phenomenon: Chan 2019 sec. 3.5.5 lists 'detonation' among collision outcomes.",
            "The interior lattice is frozen, not self-replicating: no division was seen (expedition report sec. 3).",
        ],
    }, [run])
    return [run]
