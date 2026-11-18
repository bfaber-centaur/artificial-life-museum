"""POPGEN E2 runner (protocol.md).

usage: run_e2.py ARM WORLD_SEED RNG_SEED
ARM: h<delta> (head-to-head, half the cells mutant, 1500 tu) | m<delta> (one mutant cell, 3000 tu).
Stochastic particulate inheritance ("stoch"), residents g0 0.5. Starts from the E0 256² g_r 0.5 snapshots.
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from popgen import TwoType, label_cells, state_hash  # noqa: E402

OUT = Path(os.environ.get("POPGEN_OUT", "/tmp/claude-0/-home-user/1e73a8fc-c1a3-55c2-9798-cc47a6a901a7/scratchpad/popgen"))
arm, ws, rs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
kind, delta = arm[0], float(arm[1:])
assert kind in "hm"
G0, TU = 0.5, (1500.0 if kind == "h" else 3000.0)
z = np.load(OUT / f"e0_N256_g0.5_s{ws}_tu5000.npz")
A = z["snaps"][-1] / 255.0
rng = np.random.default_rng(rs)
if kind == "m":  # same cell choice rule as run_e1.py
    n = len(label_cells(A, 0.0, rng)[1])
    L, P, chosen = label_cells(A, 0.0, rng, which=[int(np.random.default_rng(rs).integers(n))])
else:
    L, P, chosen = label_cells(A, 0.5, rng)
w = TwoType(A, L, G0, delta, "stoch", seed=1000 * ws + rs)
h0 = state_hash(np.stack([w.A, w.L]))
every = int(round(10 / w.dt)); steps = int(round(TU / w.dt))
tr = []; t0 = time.time()
for s in range(steps + 1):
    if s % every == 0:
        tr.append([round(s * w.dt), round(w.share(), 5), round(float(w.A.sum()), 1)])
    if s < steps:
        w.step()
rec = dict(arm=arm, kind=kind, delta=delta, g0=G0, world_seed=ws, rng_seed=rs, tu=TU, n_cells=len(P),
           chosen=[int(c) for c in chosen], initial_sha=h0, final_sha=state_hash(np.stack([w.A, w.L])),
           columns=["t", "share", "mass"], trace=tr, secs=round(time.time() - t0))
with open(HERE / "e2.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(arm, ws, rs, "share", tr[0][1], "->", tr[-1][1], f"{time.time() - t0:.0f}s", flush=True)
