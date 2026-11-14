"""Scout kernel sets for a lively soup: for each rule seed (Kernels from default_rng([7, rule])),
a 128^2 Voronoi soup of 12 founder genomes, 2000 steps. Measures in the last 1000 steps:
  motion   = sum|A(t) - A(t-100)| / (2 mass), averaged over 10 windows
  turnover = mass-weighted mean |G(2000) - G(1000)| (L2 over the K weights)
  div      = mass-weighted genome spread at the end
Writes scout.jsonl.   python scout.py <start> <stop>
"""
import json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from soup import Kernels, Soup
from run import initial

for rule in range(int(sys.argv[1]), int(sys.argv[2])):
    kern = Kernels(np.random.default_rng([7, rule]))
    A, G, _, _ = initial(kern, np.random.default_rng([99, 0]), 128, 12, 0.3, "voronoi", 0.25)
    S = Soup(kern, A, G, seed=0)
    mot = []; prev = None; Gmid = None
    for t in range(1, 2001):
        S.step()
        if t == 1000:
            Gmid = S.G.copy(); Amid = S.A.copy()
        if t > 1000 and t % 100 == 0:
            if prev is not None:
                mot.append(np.abs(S.A - prev).sum() / (2 * S.A.sum()))
            prev = S.A.copy()
    w = np.minimum(S.A, Amid); w = w / w.sum()
    turn = float((np.sqrt(((S.G - Gmid) ** 2).sum(0)) * w).sum())
    wa = S.A / S.A.sum(); gm = (S.G * wa).sum((1, 2))
    div = float((np.sqrt(((S.G - gm[:, None, None]) ** 2).sum(0)) * wa).sum())
    rec = dict(rule=rule, motion=float(np.mean(mot)), turnover=turn, div=div, cover=float((S.A > 0.05).mean()),
               maxA=float(S.A.max()))
    print(json.dumps(rec), flush=True)
    with open(Path(__file__).parent / "scout.jsonl", "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    os.makedirs("/tmp/claude-0/scout", exist_ok=True)
    np.savez_compressed(f"/tmp/claude-0/scout/r{rule}.npz", A=S.A.astype(np.float16), G=np.round(S.G * 255).astype(np.uint8))
