"""Free-world foraging: one Hexapteryx loose among scattered Circium rings, no keeper.

World: the Pteryx rule (C081), N^2 torus. One settled P6al, rotated to a random heading and
re-settled (atlas.body), at a random place; K settled C0v rings at random places, at least
``gap`` R apart from each other and from the arc's start. Then nothing is touched.

Every 5 tu the census labels components (A >= 0.1, torus): the arc is the heaviest component
heavier than 400 cells; rings are components of 80-250 cells. A run ends at ``tu`` or when the
world detonates (total mass > 4x start or support > 20 % of the world) or the arc is gone.
Meals are counted from the log: each time the arc's mass steps up by 60-250 cells within 20 tu
while the ring count drops by one.

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/forage.py SEED [K] [TU] [N]

Appends one row per run to forage-K<K>.jsonl.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from alm.lenia import Lenia
from atlas import WORLDS, base_body, body
from zoocore import components, sha, stamp, torus_delta

HERE = Path(__file__).resolve().parent
RULE = WORLDS["P"]["rule"]
R = RULE.R


def setup(seed, K, N, gap=4.0):
    rng = np.random.default_rng([23, seed, K, N])
    heading = float(rng.uniform(0, 360))
    arc = body("P", "P6al", heading)
    ring, _, m_ring = base_body("P", "C0v")
    A = np.zeros((N, N))
    p0 = rng.uniform(0, N, 2)
    stamp(A, arc.patch, p0)
    pts = []
    tries = 0
    while len(pts) < K and tries < 100000:
        tries += 1
        c = rng.uniform(0, N, 2)
        if np.hypot(*torus_delta(c, p0, (N, N))) < 6 * R:
            continue
        if any(np.hypot(*torus_delta(c, q, (N, N))) < gap * R for q in pts):
            continue
        pts.append(c)
        stamp(A, ring, c)
    return np.clip(A, 0, 1), arc, m_ring, heading, len(pts)


def census(A):
    cs = components(A, floor=40)
    arc = [c for c in cs if c["mass"] > 400]
    rings = [c for c in cs if 80 <= c["mass"] <= 250]
    return (arc[0]["mass"] if arc else 0.0), len(rings), len(cs)


def main():
    seed = int(sys.argv[1])
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    tu = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    N = int(sys.argv[4]) if len(sys.argv) > 4 else 512
    A0, arc, m_ring, heading, K_placed = setup(seed, K, N)
    L = Lenia(RULE, A0)
    M0 = float(L.A.sum())
    init = sha(L.A)
    series = []
    end = "time"
    t0 = time.time()
    for s in range(1, tu * RULE.T + 1):
        L.step()
        if s % (5 * RULE.T) == 0:
            m_arc, n_rings, n = census(L.A)
            M = float(L.A.sum())
            series.append([s // RULE.T, round(m_arc, 1), n_rings, n, round(M, 1)])
            if M > 4 * M0 or (L.A >= 0.1).mean() > 0.2:
                end = "detonated"
                break
            if m_arc == 0.0:
                end = "arc lost"
                break
    # meals: arc mass steps of one ring with a ring disappearing
    meals = []
    for i in range(4, len(series)):
        t, m, nr = series[i][0], series[i][1], series[i][2]
        tp, mp, nrp = series[i - 4][0], series[i - 4][1], series[i - 4][2]
        if 60 < m - mp < 250 and nr == nrp - 1 and mp > 0 and (not meals or t - meals[-1]["t"] > 20):
            meals.append({"t": t, "mass_before": mp, "mass_after": m})
    m6 = base_body("P", "P6al")[2]
    per = (base_body("P", "P10al")[2] - m6) / 4
    last_arc = max((r[1] for r in series[-3:]), default=0.0)
    row = {"seed": seed, "K": K_placed, "N": N, "tu_max": tu, "heading0": round(heading, 2),
           "end": end, "t_end": series[-1][0] if series else 0, "meals": meals,
           "n_meals": len(meals), "rings_left": series[-1][2] if series else K_placed,
           "arc_mass_final": last_arc, "segments_final": round(6 + (last_arc - m6) / per, 2) if last_arc else None,
           "init_sha256": init, "final_sha256": sha(L.A), "secs": round(time.time() - t0, 1),
           "series": series}
    with (HERE / f"forage-K{K}.jsonl").open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(f"seed {seed}: {end} at t {row['t_end']}, meals {len(meals)}, segments {row['segments_final']}, "
          f"rings left {row['rings_left']}/{K_placed}, {row['secs']}s", flush=True)


if __name__ == "__main__":
    main()
