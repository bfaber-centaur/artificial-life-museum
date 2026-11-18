"""POPGEN T2 runner (protocol.md): T1 plus one resistant cell (g 0.3) at the start of treatment.

usage: run_t2.py SEED C [N] [TU]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "T1-relapse"))
sys.path.insert(0, str(HERE.parent))
from run_t1 import KAPPAS, th, treat  # noqa: E402
from popgen import label_cells  # noqa: E402

G_CLONE = 0.3

if __name__ == "__main__":
    seed, cost = int(sys.argv[1]), float(sys.argv[2])
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    TU = float(sys.argv[4]) if len(sys.argv) > 4 else 6000.0
    t0 = time.time()
    A, g, t_grow, B0 = th.grow(seed, N, cost)
    rng = np.random.default_rng(seed)
    n = len(label_cells(A, 0.0, rng)[1])
    L, P, chosen = label_cells(A, 0.0, rng, which=[int(np.random.default_rng(seed).integers(n))])
    clone = (L > 0.5) & (A > 0)
    g = np.where(clone, G_CLONE, g)
    clone_share = float(A[clone].sum() / A.sum())
    for arm, kappa in [("none", 0.0)] + [(a, k) for k in KAPPAS for a in ("constant", "adaptive")]:
        r = treat(A, g, arm, seed, B0, TU, kappa, cost)
        rec = dict(seed=seed, cost=cost, N=N, tu=TU, arm=arm, kappa=kappa or None, B0=round(B0, 1), t_start=t_grow,
                   n_cells=n, clone_share=round(clone_share, 4), g_clone=G_CLONE,
                   columns=["t", "burden/B0", "mean_g", "resistant_share", "drug_on"], **r)
        with open(HERE / "t2.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(seed, cost, arm, kappa, "clone", round(clone_share, 3), "prog", r["progression"], "res",
              r["resistant_at_progression"], "erad", r["eradicated"], "end", r["trace"][-1], f"{time.time() - t0:.0f}s", flush=True)
