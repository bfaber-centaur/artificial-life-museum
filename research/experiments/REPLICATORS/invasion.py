"""Tissue against tissue: a world whose left half is grown 'division well' tissue (g 0) and whose right
half is grown 'division uncontrolled' tissue (g 1), under GenomeLenia (genome.py). Which invades which?

usage: invasion.py SEED TU [MUT_AMP]
Tissues: one 213 #84 cell grown on 256^2 for 2000 tu (well) and 400 tu (wild) under the catalogue rules
(seed > 0 jitters the founder by +-1e-3); the two 256^2 tissues are placed side by side on a 256 x 512 torus.
Records every 10 tu: mass-weighted mean genome per column (64 bins), total mean genome, mass.
"""
import json
import sys
import time

import numpy as np

from common import found_entry, nd, state_hash
from genome import GenomeLenia



def tissue(stem_idx, tu, seed=0):
    _, A = nd.entry_state(found_entry("213", 84), 2, 256)
    if seed:
        A = np.clip(A + (A > 0) * np.random.default_rng(seed).uniform(-1e-3, 1e-3, A.shape), 0, 1)
    w = nd.NDLenia(found_entry(*stem_idx)["params"], A)
    for _ in range(int(round(tu / w.dt))):
        w.step()
    return w.A[0]


if __name__ == "__main__":
    seed, TU = int(sys.argv[1]), float(sys.argv[2])
    mut = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    t0 = time.time()
    L, Rt = tissue(("213", 84), 2000, seed), tissue(("213", 83), 400, seed)
    A = np.concatenate([L, Rt], 1)
    g = np.concatenate([np.zeros_like(L), np.ones_like(Rt)], 1)
    w = GenomeLenia(A, g, mut_amp=mut, seed=seed)
    h0 = state_hash(np.stack([A, g]))
    every = int(round(10 / w.dt)); steps = int(round(TU / w.dt))
    tr = []
    for s in range(steps + 1):
        if s % every == 0:
            col = (w.A * w.g).sum(0) / np.maximum(w.A.sum(0), 1e-9)
            bins = col.reshape(64, -1).mean(1)
            tr.append(dict(t=round(s * w.dt, 1), mass=round(float(w.A.sum()), 1),
                           gmean=round(float((w.A * w.g).sum() / w.A.sum()), 4), cols=[round(float(x), 3) for x in bins]))
        if s < steps:
            w.step()
    np.save(f"states/invasion_s{seed}_m{mut}.npy", np.stack([w.A, w.g]))
    rec = dict(seed=seed, tu=TU, mut=mut, initial_sha=h0, final_sha=state_hash(np.stack([w.A, w.g])), trace=tr)
    with open("invasion.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(seed, mut, "gmean", [x["gmean"] for x in tr[:: max(1, len(tr) // 12)]], f"{time.time() - t0:.0f}s")
