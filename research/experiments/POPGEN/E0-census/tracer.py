"""POPGEN E0, EXPLORATORY (not pre-registered): a tracker-free check of turnover.

usage: tracer.py N G_R SEED [TU]
Start from the run's uint8 snapshot at t 5000 (a full world). With a constant rule, g is only a
tracer, so set g = 1 on the left half of the world and 0 on the right. If the world is frozen,
the tracer stays in its half (apart from a few px of blur at the two seams). If cells divide, die
and move, tracer matter spreads into the other half. Records, every 10 tu, the share of tracer
mass (A*g) lying in the right half and the share of all mass that is mixed (0.1 < g < 0.9).
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "REPLICATORS"))
from genome import GenomeLenia  # noqa: E402

OUT = Path(os.environ.get("POPGEN_OUT", "/tmp/claude-0/-home-user/1e73a8fc-c1a3-55c2-9798-cc47a6a901a7/scratchpad/popgen"))
N, g_r, seed = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
TU = float(sys.argv[4]) if len(sys.argv) > 4 else 1000.0
z = np.load(OUT / f"e0_N{N}_g{g_r}_s{seed}_tu5000.npz")
A = z["snaps"][-1] / 255.0
g = np.zeros((N, N)); g[:, : N // 2] = 1.0
w = GenomeLenia(A, g, rule_g=g_r)
every = int(round(10 / w.dt)); steps = int(round(TU / w.dt))
tr = []
for s in range(steps + 1):
    if s % every == 0:
        tm = w.A * w.g
        tr.append(dict(t=round(s * w.dt), right_share=round(float(tm[:, N // 2:].sum() / tm.sum()), 4),
                       mixed=round(float(w.A[(w.g > 0.1) & (w.g < 0.9)].sum() / w.A.sum()), 4),
                       tracer_frac=round(float(tm.sum() / w.A.sum()), 4)))
    if s < steps:
        w.step()
rec = dict(N=N, g_r=g_r, seed=seed, tu=TU, trace=tr)
with open(HERE / "tracer.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(N, g_r, [(r["t"], r["right_share"], r["mixed"], r["tracer_frac"]) for r in tr[::10]])
