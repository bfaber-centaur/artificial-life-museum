"""POPGEN T4 runner (protocol.md): sensitive-triggered adaptive dosing in the T3 world.

usage: run_t4.py SEED [N] [TU]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "T1-relapse"))
sys.path.insert(0, str(HERE.parent))
from run_t1 import KAPPAS, th  # noqa: E402
from genome import GenomeLenia  # noqa: E402
from common import state_hash  # noqa: E402
from popgen import label_cells  # noqa: E402

th.CROWD_SIGMA = 30.0
COST, G_CLONE = 0.3, 0.3


def treat_sensitive(A, g, seed, B0, TU, kappa, cost, every=5.0):
    w = GenomeLenia(A, g, mut_amp=th.MUT, seed=10_000 + seed)
    S0 = float(w.A[w.g >= th.RESIST].sum())
    on, tr, prog, prog_res, drug_time = True, [], None, None, 0.0
    k = int(round(every / w.dt))
    for s in range(int(round(TU / w.dt)) + 1):
        m = float(w.A.sum()); S = float(w.A[w.g >= th.RESIST].sum())
        if on and S <= 0.5 * S0:
            on = False
        elif not on and m >= th.HIGH * B0:
            on = True
        res = 1 - S / max(m, 1e-9)
        if prog is None and m > th.PROG * B0:
            prog, prog_res = round(s * w.dt, 1), round(res, 4)
        if s % k == 0:
            tr.append([round(s * w.dt, 1), round(m / B0, 4), round(float((w.A * w.g).sum() / max(m, 1e-9)), 4), round(res, 4), int(on)])
        if s * w.dt >= TU:
            break
        w.step()
        th.crowding_cost(w, cost)
        if on:
            w.A *= 1 - w.dt * kappa * w.g * (w.g >= th.RESIST)
            drug_time += w.dt
    return dict(trace=tr, progression=prog, resistant_at_progression=prog_res, drug_time=round(drug_time, 1),
                eradicated=bool(m < 1.0), S0=round(S0, 1), final_sha=state_hash(np.stack([w.A, w.g])))


if __name__ == "__main__":
    seed = int(sys.argv[1])
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 128
    TU = float(sys.argv[3]) if len(sys.argv) > 3 else 6000.0
    t0 = time.time()
    A, g, t_grow, B0 = th.grow(seed, N, COST)
    t3 = [json.loads(l) for l in open(HERE.parent / "T3-neighbour-competition" / "t3.jsonl")]
    ref = next(r for r in t3 if r["seed"] == seed and r["arm"] == "none")
    assert abs(ref["B0"] - round(B0, 1)) < 1e-6 and ref["t_start"] == t_grow, "pre-treatment state differs from T3"
    n = len(label_cells(A, 0.0, np.random.default_rng(seed))[1])
    L, P, chosen = label_cells(A, 0.0, np.random.default_rng(seed), which=[int(np.random.default_rng(seed).integers(n))])
    clone = (L > 0.5) & (A > 0)
    g = np.where(clone, G_CLONE, g)
    assert abs(float(A[clone].sum() / A.sum()) - ref["clone_share"]) < 1e-4
    for kappa in KAPPAS:
        r = treat_sensitive(A, g, seed, B0, TU, kappa, COST)
        rec = dict(seed=seed, cost=COST, crowd_sigma=th.CROWD_SIGMA, N=N, tu=TU, arm="adaptive_sensitive", kappa=kappa,
                   B0=round(B0, 1), t_start=t_grow, clone_share=ref["clone_share"],
                   columns=["t", "burden/B0", "mean_g", "resistant_share", "drug_on"], **r)
        with open(HERE / "t4.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(seed, kappa, "prog", r["progression"], "res", r["resistant_at_progression"], "drug", r["drug_time"],
              "erad", r["eradicated"], "end", r["trace"][-1], f"{time.time() - t0:.0f}s", flush=True)
