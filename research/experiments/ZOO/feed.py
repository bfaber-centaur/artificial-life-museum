"""Feed a Pteryx arc one Circium ring at a time and watch it climb the Pteryx ladder.

World: mu 0.38, sigma 0.07, R 13, T 10, poly/poly, 512^2 torus (the catalogue rule of
P6al ... P24al and C0v). The arc starts as the settled catalogue Hexapteryx (P6al). Each
feeding drops a settled C0v (Circium ventilans) ``ahead`` R beyond the arc's leading edge along its
current heading, offset sideways by the arc's lateral half-width plus ``b`` R: the PC scan
(atlas-PC.jsonl) found clean swallows only when the ring meets a wing tip, at half-width
+0.7 ... +1.2 R for P6al and P7al; a hit on the body of the arc detonates. The keeper then waits until the
world holds one body again plus ``digest`` tu, measures it and feeds again. A feeding that
leaves two bodies after ``wait`` tu is a miss and is retried once with the next b in the list.

The segment count of the product is estimated from its mass with the catalogue ladder
(P6al ... P10al settled masses: about 135 cells per segment) and checked by eye on the stills.

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/feed.py run --b 4 --meals 20
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from alm.lenia import Lenia
from atlas import WORLDS, base_body
from zoocore import _radius, centroid, components, crop, sha, stamp, torus_delta

HERE = Path(__file__).resolve().parent
RULE = WORLDS["P"]["rule"]
R = RULE.R
N = 512
LADDER = {}  # code -> settled mass (filled in main)


def heading_and_speed(L, tu=5):
    c0 = centroid(L.A)
    for _ in range(int(tu * RULE.T)):
        L.step()
    d = torus_delta(c0, centroid(L.A), L.A.shape)
    v = d / tu
    return v, float(np.hypot(*v))


def segments(mass, m6, per):
    return 6 + (mass - m6) / per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--b", type=float, nargs="+", default=[0.95, 0.8, 1.1, 0.7, 1.25, 0.6, 1.4],
                    help="ring offset beyond the arc's lateral half-width, in R (retries use the next)")
    ap.add_argument("--alternate", action="store_true", help="alternate the side fed")
    ap.add_argument("--ahead", type=float, default=3.0)
    ap.add_argument("--meals", type=int, default=20)
    ap.add_argument("--digest", type=float, default=40)
    ap.add_argument("--wait", type=float, default=60)
    ap.add_argument("--start", default="P6al")
    ap.add_argument("--film", default=None, help="npz path for frames every 1 tu (float16, downsampled 2x)")
    ap.add_argument("--tag", default="")
    ap.add_argument("--T", type=int, default=10, help="steps per tu (numerical check: 20)")
    a = ap.parse_args()
    global RULE
    if a.T != RULE.T:
        from dataclasses import replace
        RULE = replace(RULE, T=a.T)

    for code in ("P6al", "P7al", "P8al", "P9al", "P10al"):
        LADDER[code] = base_body("P", code)[2]
    m6 = LADDER["P6al"]
    per = (LADDER["P10al"] - LADDER["P6al"]) / 4
    ring, _, m_ring = base_body("P", "C0v")

    patch, v0, m0 = base_body("P", a.start)
    A = np.zeros((N, N))
    stamp(A, patch, (N / 2, N / 2))
    L = Lenia(RULE, A)
    log = []
    film = []  # accepted frames only (uint8, 2x downsampled, every 1 tu)
    t = 0.0

    def advance(L, tu, frames):
        for s in range(int(round(tu * RULE.T))):
            L.step()
            if a.film and (s + 1) % RULE.T == 0:
                frames.append(np.rint(L.A[::2, ::2] * 255).astype(np.uint8))

    advance(L, 10, film)
    t += 10
    meal = 0
    while meal < a.meals:
        cs = components(L.A, floor=30)
        if len(cs) != 1:
            log.append({"t": t, "event": f"{len(cs)} bodies before feeding"})
            break
        # heading from a 5 tu probe on a copy (the probe is not part of the history)
        probe = Lenia(RULE, L.A)
        c0 = centroid(probe.A)
        for _ in range(5 * RULE.T):
            probe.step()
        v = torus_delta(c0, centroid(probe.A), L.A.shape) / 5
        sp = float(np.hypot(*v))
        if sp < 0.5:
            log.append({"t": t, "event": "stopped"})
            break
        u = v / sp
        nrm = np.array([u[1], -u[0]])
        body_c = np.array(cs[0]["c"])
        P = crop(L.A, body_c, 150)
        ys, xs = np.nonzero(P >= 0.1)
        w = P[ys, xs]
        cy, cx = (ys * w).sum() / w.sum(), (xs * w).sum() / w.sum()
        half_w = float(np.max(np.abs((ys - cy) * nrm[0] + (xs - cx) * nrm[1]))) / R
        lead = float(np.max((ys - cy) * u[0] + (xs - cx) * u[1]))
        body_c = body_c + np.array([cy - 150, cx - 150])
        side = 1 if (not a.alternate or meal % 2 == 0) else -1
        m_prev = float(L.A.sum())
        accepted = None
        tries = []
        for off in a.b:
            b = side * (half_w + off)
            T_ = Lenia(RULE, L.A)
            stamp(T_.A, ring, body_c + u * (lead + a.ahead * R) + nrm * b * R)
            np.clip(T_.A, 0, 1, out=T_.A)
            frames = []
            waited, one = 0.0, False
            while waited < a.wait:
                advance(T_, 5, frames)
                waited += 5
                if len(components(T_.A, floor=30)) == 1:
                    one = True
                    break
            advance(T_, a.digest, frames)
            cs2 = components(T_.A, floor=30)
            M = float(T_.A.sum())
            grew = len(cs2) == 1 and 0.5 * m_ring < M - m_prev < 1.5 * m_ring
            outcome = ("grew" if grew else "exploded" if M > 3 * m_prev else
                       "missed" if not one else "ate, no growth" if len(cs2) == 1 else "split")
            tries.append({"off": off, "b": round(b, 3), "outcome": outcome, "mass": round(M, 1)})
            if grew:
                accepted = (T_, frames, waited + a.digest, b, M)
                break
        if accepted is None:
            log.append({"t": t, "meal": meal + 1, "event": "no offset grew", "tries": tries})
            print(log[-1], flush=True)
            break
        L, frames, dt_, b, M = accepted
        film.extend(frames)
        t += dt_
        meal += 1
        rec = {"t": round(t, 1), "meal": meal, "b": round(b, 3), "half_width_R": round(half_w, 3),
               "mass": round(M, 1), "segments_est": round(segments(M, m6, per), 2),
               "cells": int((L.A >= 0.1).sum()), "tries": tries, "sha256": sha(L.A)}
        log.append(rec)
        print({k: rec[k] for k in ("t", "meal", "b", "mass", "segments_est")}, [x["outcome"] for x in tries], flush=True)
        np.save(HERE / "states" / f"feed{a.tag}-meal{meal:02d}.npy",
                crop(L.A, components(L.A, floor=30)[0]["c"], 160).astype(np.float32))
    # let the final arc cruise and measure it
    if len(components(L.A, floor=30)) == 1:
        c0 = centroid(L.A)
        advance(L, 20, film)
        v = torus_delta(c0, centroid(L.A), L.A.shape) / 20
        log.append({"t": t + 20, "event": "final cruise", "mass": round(float(L.A.sum()), 1),
                    "speed": round(float(np.hypot(*v)), 3), "sha256": sha(L.A)})
    out = HERE / f"feed{a.tag}.json"
    out.write_text(json.dumps({"args": vars(a), "ladder": LADDER, "ring_mass": m_ring, "per_segment": per,
                               "log": log}, indent=1))
    if a.film:
        np.savez_compressed(a.film, frames=np.array(film))
    print("wrote", out)


if __name__ == "__main__":
    main()
