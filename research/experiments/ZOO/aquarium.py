"""ZOO aquarium: collisions and crowds in Chan's three-channel world (found/233.json 0-11).

All twelve aquarium creatures share ONE rule (code 5N7KKM: 3 channels, 15 kernels, R 24,
dt 1 as upstream executes it), so any of them can meet any other without changing physics.

    bombard  lithos at the centre of a 256^2 torus, k gyrans placed on a ring around it
             (radius d, random phases and orientations); run and count what is bound to the
             rock over time.
    soup     a 512^2 torus seeded with a random mix of free creatures (lithos, gyrans, limus,
             tardus, egg); census every 25 tu.

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/aquarium.py bombard SEED K [TU]
    ... aquarium.py soup SEED [TU]

Writes aq-<mode>.jsonl (one row per run, census series included) and keeps final states in
states/ (gitignored).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "WINGS"))
from nd_lenia import NDLenia, entry_state, load_found  # noqa: E402
from zoocore import components, crop, stamp, torus_delta  # noqa: E402

NAMES = {0: "limus", 1: "gyrans", 3: "lithos", 4: "tardus", 11: "egg"}
STATES = HERE / "states"
SETTLE = 50
UNIT = 1450.0  # rough mass of one free creature (cells, all channels)


def settled_patch(i, half=40):
    """Creature i settled SETTLE tu alone on 256^2, cropped to (3, 2h+1, 2h+1). Cached."""
    STATES.mkdir(exist_ok=True)
    f = STATES / f"aq-{i}-patch.npy"
    if f.exists():
        return np.load(f)
    es = load_found("233")
    p, A = entry_state(es[i], 2, 256)
    L = NDLenia(p, A)
    for _ in range(SETTLE):
        L.step()
    S = L.A.sum(0)
    c = components(S, floor=100)[0]["c"]
    P = np.stack([crop(L.A[k], c, half) for k in range(3)])
    np.save(f, P)
    return P


def rule():
    return load_found("233")[0]["params"]


def rotate(P, deg):
    if deg == 0:
        return P
    return np.clip(np.stack([ndimage.rotate(P[k], deg, reshape=False, order=1) for k in range(3)]), 0, 1)


def place(A, P, c):
    for k in range(3):
        stamp(A[k], P[k], c)


def census(A, floor=0.25 * UNIT):
    S = A.sum(0)
    cs = components(S, theta=0.1, floor=floor)
    return [{"mass": round(c["mass"], 1), "units": int(round(c["mass"] / UNIT)),
             "c": [round(x, 1) for x in c["c"]],
             "ch": [round(float(A[k][c["mask"]].sum()), 1) for k in range(3)]} for c in cs]


def sha(A):
    return hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()


def bombard(seed, k, tu=1500, d=70, every=25, keep=None):
    N = 256
    rng = np.random.default_rng([7, seed, k])
    A = np.zeros((3, N, N))
    place(A, settled_patch(3), (N / 2, N / 2))
    g = settled_patch(1)
    phases = np.sort(rng.uniform(0, 360, k))
    # keep the gyrans apart: jitter equal spacing
    phases = (np.arange(k) * 360 / k + rng.uniform(0, 360 / k * 0.5, k) + rng.uniform(0, 360)) % 360
    for ph in phases:
        r = d + rng.uniform(-8, 8)
        y = N / 2 - r * np.sin(np.radians(ph))
        x = N / 2 + r * np.cos(np.radians(ph))
        place(A, rotate(g, float(rng.uniform(0, 360))), (y, x))
    A = np.clip(A, 0, 1)
    return run(A, tu, every, {"mode": "bombard", "seed": seed, "k": k, "d": d}, keep)


def soup(seed, tu=3000, every=25, mix=None, N=512, keep=None):
    rng = np.random.default_rng([11, seed])
    mix = mix or {3: 4, 1: 8, 0: 4, 4: 3, 11: 3}
    A = np.zeros((3, N, N))
    pts = []
    for i, n in mix.items():
        P = settled_patch(i)
        for _ in range(n):
            for _try in range(1000):
                c = rng.uniform(0, N, 2)
                if all(np.hypot(*torus_delta(c, q, (N, N))) > 90 for q in pts):
                    break
            pts.append(c)
            place(A, rotate(P, float(rng.uniform(0, 360))), c)
    A = np.clip(A, 0, 1)
    return run(A, tu, every, {"mode": "soup", "seed": seed, "mix": {NAMES[i]: n for i, n in mix.items()}, "N": N}, keep)


def run(A, tu, every, meta, keep=None):
    L = NDLenia(rule(), A)
    t0 = time.time()
    rows = [{"t": 0, "mass": round(float(L.A.sum()), 1), "census": census(L.A)}]
    frames = [L.A.astype(np.float32)] if keep else None
    init = sha(L.A)
    for s in range(1, tu + 1):
        L.step()
        if keep and s % keep == 0:
            frames.append(L.A.astype(np.float32))
        if s % every == 0:
            rows.append({"t": s, "mass": round(float(L.A.sum()), 1), "census": census(L.A)})
    out = dict(meta, tu=tu, every=every, init_sha256=init, final_sha256=sha(L.A),
               secs=round(time.time() - t0, 1), series=rows)
    return out, frames, L.A


def summary(r):
    last = r["series"][-1]["census"]
    units = sorted([c["units"] for c in last], reverse=True)
    return f"{r['mode']} seed {r['seed']} k {r.get('k')}: mass {r['series'][0]['mass']:.0f}->{r['series'][-1]['mass']:.0f} bodies(units) {units} {r['secs']}s"


def main():
    mode = sys.argv[1]
    if mode == "bombard":
        seed, k = int(sys.argv[2]), int(sys.argv[3])
        tu = int(sys.argv[4]) if len(sys.argv) > 4 else 1500
        r, _, A = bombard(seed, k, tu)
    elif mode == "soup":
        seed = int(sys.argv[2])
        tu = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
        r, _, A = soup(seed, tu)
    np.save(STATES / f"aq-{mode}-{seed}-{r.get('k', 0)}-final.npy", A.astype(np.float32))
    with (HERE / f"aq-{mode}.jsonl").open("a") as fh:
        fh.write(json.dumps(r) + "\n")
    print(summary(r), flush=True)


if __name__ == "__main__":
    main()
