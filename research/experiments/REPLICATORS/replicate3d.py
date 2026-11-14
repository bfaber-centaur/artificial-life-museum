"""3-D catalogue dividers: bodies (26-connected, field blurred 1.5 voxels > 0.08, torus) and mass every 10 tu.

usage: replicate3d.py STEM IDX N TU DTFAC
"""
import json
import sys
import time

from scipy import ndimage

from common import found_entry, nd, state_hash, torus_label

stem, idx, N, TU, dtfac = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
e = found_entry(stem, idx)
params, A = nd.entry_state(e, 3, N)
for p in params:
    p["T"] = p.get("T", 10) * dtfac
w = nd.NDLenia(params, A)
h0 = state_hash(w.A)
every = int(round(10 / w.dt)); steps = int(round(TU / w.dt))
tr = []; t0 = time.time()
for s in range(steps + 1):
    if s % every == 0:
        n = torus_label(ndimage.gaussian_filter(w.A[0], 1.5, mode="wrap") > 0.08)[1]
        tr.append((round(s * w.dt, 1), n, round(float(w.A.sum()), 1), round(float((w.A[0] > 0.25).mean()), 4)))
    if s < steps:
        w.step()
rec = dict(stem=stem, idx=idx, name=e.get("name"), N=N, tu=TU, dtfac=dtfac, initial_sha=h0, final_sha=state_hash(w.A), trace=tr)
with open("replicate3d.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(stem, idx, N, dtfac, [(t[0], t[1], t[2]) for t in tr[::5]], f"{time.time() - t0:.0f}s", flush=True)
