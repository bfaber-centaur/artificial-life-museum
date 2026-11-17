"""POPGEN T1 runner (protocol.md): therapy.py with an immune resistant type (g < 0.4 not killed).

usage: run_t1.py SEED C [N] [TU]    runs none, then constant and adaptive at kappa 0.3 and 0.4 (A1).
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "REPLICATORS"))
import therapy as th  # noqa: E402
from genome import GenomeLenia  # noqa: E402
from common import state_hash  # noqa: E402

KAPPAS = (0.3, 0.4)  # protocol amendment A1


def treat(A, g, arm, seed, B0, TU, kappa, cost, every=5.0):
    """therapy.treat with one change: the drug spares matter with g < RESIST."""
    w = GenomeLenia(A, g, mut_amp=th.MUT, seed=10_000 + seed)
    on = arm in ("constant", "adaptive")
    tr, prog, drug_time, prog_res = [], None, 0.0, None
    k = int(round(every / w.dt))
    for s in range(int(round(TU / w.dt)) + 1):
        m = float(w.A.sum())
        if arm == "adaptive":
            if on and m <= th.LOW * B0:
                on = False
            elif not on and m >= th.HIGH * B0:
                on = True
        res = float(w.A[w.g < th.RESIST].sum() / max(m, 1e-9))
        if prog is None and m > th.PROG * B0:
            prog, prog_res = round(s * w.dt, 1), round(res, 4)
        if s % k == 0:
            tr.append([round(s * w.dt, 1), round(m / B0, 4), round(float((w.A * w.g).sum() / max(m, 1e-9)), 4),
                       round(res, 4), int(on)])
        if s * w.dt >= TU:
            break
        w.step()
        th.crowding_cost(w, cost)
        if on:
            w.A *= 1 - w.dt * kappa * w.g * (w.g >= th.RESIST)
            drug_time += w.dt
    return dict(trace=tr, progression=prog, resistant_at_progression=prog_res, drug_time=round(drug_time, 1),
                eradicated=bool(m < 1.0), final_sha=state_hash(np.stack([w.A, w.g])))


seed, cost = int(sys.argv[1]), float(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 128
TU = float(sys.argv[4]) if len(sys.argv) > 4 else 6000.0
t0 = time.time()
A, g, t_grow, B0 = th.grow(seed, N, cost)
for arm, kappa in [("none", 0.0)] + [(a, k) for k in KAPPAS for a in ("constant", "adaptive")]:
    r = treat(A, g, arm, seed, B0, TU, kappa, cost)
    rec = dict(seed=seed, cost=cost, N=N, tu=TU, arm=arm, kappa=kappa or None, B0=round(B0, 1), t_start=t_grow,
               columns=["t", "burden/B0", "mean_g", "resistant_share", "drug_on"], **r)
    with open(HERE / "t1.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(seed, cost, arm, kappa, "prog", r["progression"], "res", r["resistant_at_progression"], "erad", r["eradicated"],
          "end", r["trace"][-1], f"{time.time() - t0:.0f}s", flush=True)
