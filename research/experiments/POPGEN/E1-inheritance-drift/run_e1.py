"""POPGEN E1 runner (protocol.md).

usage: run_e1.py ARM WORLD_SEED RNG_SEED [TU]
ARM: blend+ | part+ | part0 (E1a, one mutant cell) | drift0.5 | drift0.1 (E1b, cells labelled with p0)
Starts from the E0 snapshot e0_N256_g0.5_s{WORLD_SEED}_tu5000.npz (t 5000) in $POPGEN_OUT.
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
G0 = 0.5
ARMS = {"blend+": ("blend", 0.2, None), "part+": ("part", 0.2, None), "part0": ("part", 0.0, None),
        "drift0.5": ("part", 0.0, 0.5), "drift0.1": ("part", 0.0, 0.1),
        # E1c (protocol_e1c.md): unbiased stochastic particulate inheritance
        "s+": ("stoch", 0.2, None), "s0": ("stoch", 0.0, None), "sdrift0.5": ("stoch", 0.0, 0.5), "sdrift0.1": ("stoch", 0.0, 0.1)}
mode, delta, p0 = ARMS[arm]
TU = float(sys.argv[4]) if len(sys.argv) > 4 else (3000.0 if p0 is None else 2000.0)
z = np.load(OUT / f"e0_N256_g0.5_s{ws}_tu5000.npz")
A = z["snaps"][-1] / 255.0
rng = np.random.default_rng(rs)
if p0 is None:
    n = len(label_cells(A, 0.0, rng)[1])
    L, P, chosen = label_cells(A, 0.0, rng, which=[int(np.random.default_rng(rs).integers(n))])
else:
    L, P, chosen = label_cells(A, p0, rng)
w = TwoType(A, L, G0, delta, mode, seed=1000 * ws + rs)
h0 = state_hash(np.stack([w.A, w.L]))
every = int(round(10 / w.dt)); steps = int(round(TU / w.dt))
tr = []; t0 = time.time()
for s in range(steps + 1):
    if s % every == 0:
        maj = float(w.A[w.L > 0.5].sum() / w.A.sum())
        tr.append([round(s * w.dt), round(w.share(), 5), round(maj, 5), round(w.mixed(), 4), round(float(w.A.sum()), 1)])
    if s < steps:
        w.step()
rec = dict(arm=arm, mode=mode, delta=delta, p0=p0, g0=G0, world_seed=ws, rng_seed=rs, tu=TU, n_cells=len(P),
           chosen=[int(c) for c in chosen], initial_sha=h0, final_sha=state_hash(np.stack([w.A, w.L])),
           columns=["t", "share", "majority_share", "mixed", "mass"], trace=tr, secs=round(time.time() - t0))
with open(HERE / "e1.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(arm, ws, rs, "share", tr[0][1], "->", tr[-1][1], "maj", tr[-1][2], f"{time.time() - t0:.0f}s", flush=True)
