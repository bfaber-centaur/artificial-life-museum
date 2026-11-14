"""ZOO collision atlas: run every (pair, relative angle, impact parameter) in a world.

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/atlas.py run O
    ... atlas.py run P          # Pteryx world (mu 0.38, sigma 0.07)
    ... atlas.py run C          # coexistence world (mu 0.155, sigma 0.020)

Bodies are cached in research/experiments/ZOO/states/ (gitignored); results are appended
to atlas-<world>.jsonl, one row per collision, keyed by (a, b, theta, b_R).
"""

from __future__ import annotations

import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from alm.lenia import Rule
from alm.specimens import from_catalog, load
from zoocore import (Body, classify, crop, heading_deg, make_body, place_pair, run_collision,
                     settle, sha, components)

HERE = Path(__file__).resolve().parent
STATES = HERE / "states"

WORLDS = {
    # name: rule, world size, settle tu, crop half-size, species codes
    "O": dict(rule=Rule(R=13, T=10, mu=0.15, sigma=0.015), N=384, half=20,
              species=["O2u"], settle_tu=100),
    # numerical check of the O map: same rule at half the timestep
    "O20": dict(rule=Rule(R=13, T=20, mu=0.15, sigma=0.015), N=384, half=20,
                species=["O2u"], settle_tu=100),
    "P": dict(rule=Rule(R=13, T=10, mu=0.38, sigma=0.07), N=512, half=70,
              species=["P6al", "P7al", "P8al", "P10al", "C0v"], settle_tu=100,
              thetas=[60, 120, 180], bs=[-8, -6, -4, -2, 0, 2, 4, 6, 8]),
    # feeding scan: each Pteryx against a static Circium, fine impact parameter, head-on only
    "PC": dict(rule=Rule(R=13, T=10, mu=0.38, sigma=0.07), N=512, half=70,
               species=["P6al", "P7al", "P8al", "P9al", "P10al", "C0v"], settle_tu=100,
               thetas=[180], bs=[x / 4 for x in range(-36, 37)], only_vs="C0v"),
    # numerical check of PC at half the timestep
    "PC20": dict(rule=Rule(R=13, T=20, mu=0.38, sigma=0.07), N=512, half=70,
                 species=["P6al", "P7al", "P8al", "P9al", "P10al", "C0v"], settle_tu=100,
                 thetas=[180], bs=[x / 4 for x in range(-36, 37)], only_vs="C0v"),
    "C": dict(rule=Rule(R=13, T=10, mu=0.155, sigma=0.020), N=384, half=30,
              species=["glider", "S102", "S103"], settle_tu=200),
}

THETAS = list(range(15, 181, 15))  # angle between the two headings (deg); 180 = head-on
BS = [x / 4 for x in range(-8, 9)]  # impact parameter in R


def seed(world, code):
    W = WORLDS[world]
    N = W["N"]
    if code == "glider":  # Orbium seed settled under the coexistence rule (as the reef did)
        A = load("S001").place(N)
    elif code.startswith("S1"):
        A = load(code).place(N)
    else:
        A = from_catalog(code).place(N)
    return A


def base_body(world, code):
    """Settled, unrotated body (cached)."""
    STATES.mkdir(exist_ok=True)
    f = STATES / f"{world}-{code}-base.npz"
    W = WORLDS[world]
    if f.exists():
        z = np.load(f)
        return z["patch"], tuple(z["v"]), float(z["mass"])
    A, m, v, alive, comps = settle(W["rule"], seed(world, code), W["settle_tu"])
    if not alive:
        raise RuntimeError(f"{code} died while settling in world {world}")
    patch = crop(A, comps[0]["c"], W["half"])
    np.savez(f, patch=patch, v=np.array(v), mass=float(patch.sum()))
    return patch, v, float(patch.sum())


def body(world, code, heading):
    """Body of species ``code`` re-settled facing ``heading`` (deg) (cached)."""
    W = WORLDS[world]
    patch0, v0, m0 = base_body(world, code)
    moving = math.hypot(*v0) > 0.05
    rot = ((heading - heading_deg(v0)) % 360) if moving else 0.0
    rot = round(rot, 3)
    f = STATES / f"{world}-{code}-rot{rot:07.3f}.npz"
    if f.exists():
        z = np.load(f, allow_pickle=False)
        return Body(world, code, code, rot, z["patch"], float(z["mass"]), tuple(z["v"]), True)
    b = make_body(world, W["rule"], code, patch0, rot, W["N"] if W["N"] <= 256 else 256,
                  30, W["half"])
    np.savez(f, patch=b.patch, mass=b.mass, v=np.array(b.v))
    return b


def job(args):
    world, a, b, theta, b_R = args
    W = WORLDS[world]
    rule, N = W["rule"], W["N"]
    A = body(world, a, 0.0)
    hA = A.heading if A.heading is not None else 0.0
    B = body(world, b, hA + theta)  # theta = angle between headings: 180 head-on, 90 T-bone
    A0, info = place_pair(A, B, b_R, rule.R, N)
    tc = info["tc"] if info["tc"] is not None else 0.0
    if info["tc"] is None and A.speed < 0.05 and B.speed < 0.05:
        return None
    t_after = 25.0 if world != "C" else 60.0
    tu = math.ceil((tc + t_after) / 5) * 5
    t0 = time.time()
    frames, times, _ = run_collision(rule, A0, tu, every_tu=5.0)
    out = classify(frames, times, A.mass, B.mass, rule.R, tc)
    real_theta = None
    if A.heading is not None and B.heading is not None:
        real_theta = round((B.heading - A.heading) % 360, 2)
    out.update(world=world, a=a, b=b, theta=theta, b_R=b_R, tc=tc, tu=tu,
               headA=A.heading, headB=B.heading, real_theta=real_theta,
               vA=A.v, vB=B.v, mA=A.mass, mB=B.mass, final_sha256=sha(frames[-1]),
               mass_series=[float(F.sum()) for F in frames], secs=round(time.time() - t0, 1))
    return out


def pairs(world):
    sp = WORLDS[world]["species"]
    if WORLDS[world].get("only_vs"):
        t = WORLDS[world]["only_vs"]
        return [(a, t) for a in sp if a != t]
    return [(sp[i], sp[j]) for i in range(len(sp)) for j in range(i, len(sp))]


def jobs(world):
    thetas = WORLDS[world].get("thetas", THETAS)
    bs = WORLDS[world].get("bs", BS)
    out = []
    for a, b in pairs(world):
        for th in thetas:
            for bR in bs:
                out.append((world, a, b, th, bR))
    return out


def main():
    cmd, world = sys.argv[1], sys.argv[2]
    path = HERE / f"atlas-{world}.jsonl"
    if cmd == "run":
        # build bodies serially first so workers only read the cache
        W = WORLDS[world]
        for code in W["species"]:
            base_body(world, code)
        js = jobs(world)
        done = set()
        if path.exists():
            for line in path.read_text().splitlines():
                r = json.loads(line)
                done.add((r["a"], r["b"], r["theta"], r["b_R"]))
        js = [j for j in js if (j[1], j[2], j[3], j[4]) not in done]
        # pre-build every rotated body serially
        for (_, a, b, th, bR) in js:
            A = body(world, a, 0.0)
            hA = A.heading if A.heading is not None else 0.0
            body(world, b, hA + th)
        print(f"{len(js)} jobs", flush=True)
        with Pool(4) as pool, path.open("a") as fh:
            for r in pool.imap_unordered(job, js):
                if r is None:
                    continue
                r.pop("products_masks", None)
                fh.write(json.dumps(r) + "\n")
                fh.flush()
                print(r["a"], r["b"], r["theta"], r["b_R"], r["class"],
                      f"M={r['mass_ratio']:.2f} n={r['n']} {r['secs']}s", flush=True)


if __name__ == "__main__":
    main()
