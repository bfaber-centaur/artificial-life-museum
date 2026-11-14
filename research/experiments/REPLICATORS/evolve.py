"""Evolution on the well -> uncontrolled line: one 213 #84 cell with genome G0 everywhere, mutation on.

usage: evolve.py SEED N TU G0 MUT_AMP [neutral]   (neutral: rule fixed at G0, genome only a tracer)
Records every 10 tu: mass, mass-weighted mean genome, its 10/50/90 % quantiles (mass-weighted).
"""
import json
import sys
import time

import numpy as np

from common import found_entry, nd, state_hash
from genome import GenomeLenia

seed, N, TU, g0, mut = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
neutral = len(sys.argv) > 6 and sys.argv[6] == "neutral"
_, A = nd.entry_state(found_entry("213", 84), 2, N)
w = GenomeLenia(A[0], np.full((N, N), g0), mut_amp=mut, seed=seed, rule_g=g0 if neutral else None)
h0 = state_hash(np.stack([w.A, w.g]))
every = int(round(10 / w.dt)); steps = int(round(TU / w.dt))
tr = []; t0 = time.time()


def wq(x, wt, q):
    o = np.argsort(x); c = np.cumsum(wt[o]); c /= c[-1]
    return float(x[o][np.searchsorted(c, q)])


for s in range(steps + 1):
    if s % every == 0:
        a, g = w.A.ravel(), w.g.ravel(); m = a > 0.05
        row = dict(t=round(s * w.dt, 1), mass=round(float(a.sum()), 1))
        if m.sum() > 10:
            row.update(gmean=round(float((a * g).sum() / a.sum()), 4), q=[round(wq(g[m], a[m], q), 3) for q in (0.1, 0.5, 0.9)])
        tr.append(row)
        if a.sum() == 0:
            break
    if s < steps:
        w.step()
np.save(f"states/evolve_s{seed}_g{g0}_m{mut}_N{N}{'_neutral' if neutral else ''}.npy", np.stack([w.A, w.g]))
rec = dict(neutral=neutral, seed=seed, N=N, tu=TU, g0=g0, mut=mut, initial_sha=h0, final_sha=state_hash(np.stack([w.A, w.g])), trace=tr)
with open("evolve.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(seed, g0, mut, "neutral" if neutral else "selected", [(r["t"], r.get("gmean")) for r in tr[:: max(1, len(tr) // 12)]], f"{time.time() - t0:.0f}s")
