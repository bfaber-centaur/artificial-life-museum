"""Run every catalogue entry whose name says it divides/replicates; record body count vs time."""
import json
import sys
import time

import numpy as np

from common import count_bodies, found_entry, nd, state_hash

TARGETS = [("212", 3), ("212", 7), ("213", 17), ("213", 82), ("213", 83), ("213", 84), ("221", 35), ("233", 11)]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 256
TU = float(sys.argv[2]) if len(sys.argv) > 2 else 600
out = open(f"scout_N{N}.jsonl", "w")
for stem, idx in TARGETS:
    e = found_entry(stem, idx)
    params, A = nd.entry_state(e, 2, N)
    w = nd.NDLenia(params, A)
    steps = int(round(TU / w.dt))
    every = max(1, int(round(10 / w.dt)))
    t0 = time.time()
    trace = []
    for s in range(steps + 1):
        if s % every == 0:
            n, ms = count_bodies(w.A)
            trace.append((round(s * w.dt, 3), n, round(float(w.A.sum()), 2)))
        if s < steps:
            w.step()
    rec = dict(stem=stem, idx=idx, name=e.get("name"), N=N, tu=TU, trace=trace, hash=state_hash(w.A))
    out.write(json.dumps(rec) + "\n"); out.flush()
    print(stem, idx, e.get("name"), "bodies:", [t[1] for t in trace[::6]], "mass end", trace[-1][2], f"{time.time()-t0:.0f}s", flush=True)
