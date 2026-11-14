"""Simulate a catalogue creature and store the summed field every `every_tu` time units as uint8.

usage: record.py STEM IDX N TU OUT.npz [EVERY_TU] [LAM]
LAM (optional) uses interp.mix(LAM) rules (213/84 -> 213/83) with 84's cells.
"""
import sys
import time

import numpy as np

from common import found_entry, nd, state_hash

stem, idx, N, TU, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
every_tu = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
lam = float(sys.argv[7]) if len(sys.argv) > 7 else None
e = found_entry(stem, idx)
params, A = nd.entry_state(e, 2, N)
if lam is not None:
    from interp import mix
    params = mix(lam)
w = nd.NDLenia(params, A)
h0 = state_hash(w.A)
every = int(round(every_tu / w.dt)); steps = int(round(TU / w.dt))
C = w.A.shape[0]
frames, times = [], []
t0 = time.time()
for s in range(steps + 1):
    if s % every == 0:
        frames.append(np.clip(np.rint(w.A.sum(0) / C * 255), 0, 255).astype(np.uint8)); times.append(s * w.dt)
    if s < steps:
        w.step()
np.savez_compressed(out, S=np.array(frames), t=np.array(times), C=C, stem=stem, idx=idx, N=N,
                    initial_sha=h0, final_sha=state_hash(w.A), lam=-1 if lam is None else lam)
print(out, len(frames), "frames", state_hash(w.A), f"{time.time() - t0:.0f}s")
