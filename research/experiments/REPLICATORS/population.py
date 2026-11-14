"""Long population runs of catalogue dividers: body count and mass every 10 tu.

usage: population.py STEM IDX N TU SEED_JITTER  (jitter 0 = exact catalogue cells; >0 = tiny noise, seed)
"""
import json
import sys
import time

import numpy as np

from common import count_bodies, found_entry, nd, state_hash

stem, idx, N, TU, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
e = found_entry(stem, idx)
params, A = nd.entry_state(e, 2, N)
if seed:
    A = np.clip(A + (A > 0) * np.random.default_rng(seed).uniform(-1e-3, 1e-3, A.shape), 0, 1)
w = nd.NDLenia(params, A)
steps = int(round(TU / w.dt)); every = int(round(10 / w.dt))
trace = []; t0 = time.time()
for s in range(steps + 1):
    if s % every == 0:
        n, ms = count_bodies(w.A, thr=0.2)
        trace.append((round(s * w.dt, 2), n, round(float(w.A.sum()), 2)))
        if n == 0:
            break
    if s < steps:
        w.step()
rec = dict(stem=stem, idx=idx, name=e.get("name"), N=N, tu=TU, seed=seed, trace=trace, hash=state_hash(w.A))
with open("population.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(stem, idx, N, seed, "n:", [t[1] for t in trace[:: max(1, len(trace) // 20)]], f"{time.time() - t0:.0f}s")
