"""How fast one cell fills the world, along the rule line 'division well' (lam 0) -> 'division uncontrolled' (lam 1).

Seed: 213/84's cells in every arm (+ uniform jitter of +-1e-3 on occupied cells when seed > 0).
Metric: occupancy = fraction of the torus where the field blurred with a Gaussian (sigma 4 px) exceeds 0.05;
t50 = first time occupancy >= 0.5. Recorded every 5 time units up to TU.
usage: growth.py N TU DTFAC SEED LAM [LAM ...]     (DTFAC 2 = half the catalogue timestep)
"""
import json
import sys
import time

import numpy as np
from scipy import ndimage

from common import found_entry, nd, state_hash
from interp import mix

N, TU, dtfac, seed = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])


def occupancy(S):
    return float((ndimage.gaussian_filter(S, 4.0, mode="wrap") > 0.05).mean())


for lam in map(float, sys.argv[5:]):
    t0 = time.time()
    params = mix(lam)
    for p in params:
        p["T"] = p.get("T", 10) * dtfac
    _, A = nd.entry_state(found_entry("213", 84), 2, N)
    if seed:
        A = np.clip(A + (A > 0) * np.random.default_rng(seed).uniform(-1e-3, 1e-3, A.shape), 0, 1)
    w = nd.NDLenia(params, A)
    every = int(round(5 / w.dt)); steps = int(round(TU / w.dt))
    tr, t50 = [], None
    for s in range(steps + 1):
        if s % every == 0:
            S = w.A.sum(0); oc = occupancy(S)
            tr.append((round(s * w.dt, 2), round(oc, 4), round(float(S.sum()), 1)))
            if t50 is None and oc >= 0.5:
                t50 = round(s * w.dt, 2)
            if oc == 0 or (t50 is not None and s * w.dt >= t50 + 200):
                break
        w.step()
    rec = dict(lam=lam, N=N, tu=TU, dtfac=dtfac, seed=seed, t50=t50, final_occ=tr[-1][1], trace=tr, hash=state_hash(w.A))
    with open("growth.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(lam, seed, dtfac, "t50", t50, "occ", tr[-1][1], f"{time.time() - t0:.0f}s", flush=True)
