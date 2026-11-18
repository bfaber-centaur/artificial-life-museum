"""POPGEN E0: grow GenomeLenia (constant rule g_r, no mutation) from one cell and census it.

usage: run.py N G_R SEED [TU]     (see protocol.md)
Every 1 tu: peaks of tree.peaks on the field. Every 100 tu: uint8 snapshot of the field.
Big data go to $POPGEN_OUT (default: scratchpad); one summary row is appended to e0.jsonl.
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "REPLICATORS"))
from common import found_entry, nd, state_hash  # noqa: E402
from genome import GenomeLenia  # noqa: E402
import tree  # noqa: E402

N, g_r, seed = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
TU = float(sys.argv[4]) if len(sys.argv) > 4 else 5000.0
OUT = Path(os.environ.get("POPGEN_OUT", "/tmp/claude-0/-home-user/1e73a8fc-c1a3-55c2-9798-cc47a6a901a7/scratchpad/popgen"))
OUT.mkdir(parents=True, exist_ok=True)
tag = f"e0_N{N}_g{g_r}_s{seed}_tu{int(TU)}"

_, A = nd.entry_state(found_entry("213", 84), 2, N)
A = A[0]
if seed:
    A = np.clip(A + (A > 0) * np.random.default_rng(seed).uniform(-1e-3, 1e-3, A.shape), 0, 1)
w = GenomeLenia(A, np.full((N, N), g_r), rule_g=g_r)
h0 = state_hash(w.A)
per_tu = int(round(1 / w.dt)); steps = int(round(TU / w.dt))
peaks, counts, mass, snaps, snap_t = [], [], [], [], []
t0 = time.time()
for s in range(steps + 1):
    if s % per_tu == 0:
        P = tree.peaks(w.A)
        peaks.append(P.astype(np.float32)); counts.append(len(P)); mass.append(float(w.A.sum()))
        if (s // per_tu) % 100 == 0:
            snaps.append(np.clip(np.rint(w.A * 255), 0, 255).astype(np.uint8)); snap_t.append(s * w.dt)
    if s < steps:
        w.step()
off = np.cumsum([0] + [len(p) for p in peaks])
np.savez_compressed(OUT / f"{tag}.npz", peaks=np.concatenate(peaks) if off[-1] else np.zeros((0, 2), np.float32),
                    offsets=off, counts=np.array(counts), mass=np.array(mass), snaps=np.array(snaps), snap_t=np.array(snap_t))
rec = dict(tag=tag, N=N, g_r=g_r, seed=seed, tu=TU, initial_sha=h0, final_sha=state_hash(w.A),
           counts_every_100=counts[::100], mass_every_100=[round(m, 1) for m in mass[::100]], secs=round(time.time() - t0))
with open(HERE / "e0.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(tag, "n:", counts[::500], f"{time.time() - t0:.0f}s")
