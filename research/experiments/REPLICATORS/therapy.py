"""A toy of adaptive therapy in GenomeLenia (our modified rule; see genome.py).

A "tumour" grows from one 213 #84 cell at genome 0.7 with mutation on (amp 0.03 every 10 tu),
the level where selection in GenomeLenia levels off (C111). When it reaches B0 = 40% of the
world's carrying mass we start a "drug" that removes matter in proportion to its genome, the way
chemotherapy hits fast-dividing cells hardest:   A <- A (1 - dt * KAPPA * g)   while the drug is on.
Low-genome matter divides slowly but barely feels the drug: it is the "resistant" type, and its
resistance has a cost (slower growth, and it loses ground to fast genomes where they meet, C092).

Three arms from the identical pre-treatment state and identical mutation noise:
  none       no drug;
  constant   drug always on (the "maximum tolerated dose");
  adaptive   drug on until the burden falls to B0/2, then off until it is back at B0
             (the rule of the Zhang et al. 2017 pilot trial, PSA replaced by total mass).
"Progression" = the first time the burden exceeds 1.25 B0 after treatment starts.

  python therapy.py SEED KAPPA[,KAPPA...] [N] [TU]   append one record per arm and dose to
                                                    therapy.jsonl (the untreated arm once per seed)
"""
import json
import sys
import time

import numpy as np

from common import found_entry, nd, state_hash
from genome import GenomeLenia

KAPPA, G0, MUT, CAP_FRAC, LOW, HIGH, PROG = 0.3, 0.7, 0.03, 0.4, 0.5, 1.0, 1.25
RESIST = 0.4   # "resistant" = matter with genome below this
CARRY = 0.196  # carrying mass per pixel of a saturated g~0.7 tissue (12,600 / 256², C110 world)


def grow(seed, N):
    _, A = nd.entry_state(found_entry("213", 84), 2, N)
    w = GenomeLenia(A[0], np.full((N, N), G0), mut_amp=MUT, seed=seed)
    B0 = CAP_FRAC * CARRY * N * N
    while w.A.sum() < B0:
        w.step()
        if w.n * w.dt > 3000:
            raise RuntimeError("tumour never reached B0")
    return w.A.copy(), w.g.copy(), round(w.n * w.dt, 1), float(w.A.sum())


def treat(A, g, arm, seed, B0, TU, kappa=KAPPA, every=5.0):
    w = GenomeLenia(A, g, mut_amp=MUT, seed=10_000 + seed)
    on = arm in ("constant", "adaptive")
    tr, prog, drug_time = [], None, 0.0
    k = int(round(every / w.dt))
    for s in range(int(round(TU / w.dt)) + 1):
        m = float(w.A.sum())
        if arm == "adaptive":
            if on and m <= LOW * B0:
                on = False
            elif not on and m >= HIGH * B0:
                on = True
        if prog is None and m > PROG * B0:
            prog = round(s * w.dt, 1)
        if s % k == 0:
            a = w.A
            tr.append([round(s * w.dt, 1), round(m / B0, 4),
                       round(float((a * w.g).sum() / max(m, 1e-9)), 4),
                       round(float(a[w.g < RESIST].sum() / max(m, 1e-9)), 4), int(on)])
        if s * w.dt >= TU:
            break
        w.step()
        if on:
            w.A *= 1 - w.dt * kappa * w.g
            drug_time += w.dt
    return dict(trace=tr, progression=prog, drug_time=round(drug_time, 1),
                final_sha=state_hash(np.stack([w.A, w.g])))


def main(seed, kappas=(KAPPA,), N=128, TU=2000.0, out="therapy.jsonl"):
    t0 = time.time()
    A, g, t_grow, B0 = grow(seed, N)
    r = treat(A, g, "none", seed, B0, TU)
    runs = [("none", None, r)] + [(arm, k, None) for k in kappas for arm in ("constant", "adaptive")]
    for arm, kappa, r in runs:
        if r is None:
            r = treat(A, g, arm, seed, B0, TU, kappa)
        rec = dict(seed=seed, N=N, tu=TU, arm=arm, kappa=kappa, g0=G0, mut=MUT, B0=round(B0, 1),
                   t_start=t_grow, columns=["t", "burden/B0", "mean_g", "resistant_share", "drug_on"], **r)
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        last = r["trace"][-1]
        print(seed, arm, kappa, "prog", r["progression"], "drug", r["drug_time"], "end", last,
              f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    ks = tuple(float(x) for x in a[1].split(","))
    main(int(a[0]), ks, *(int(a[2]),) if len(a) > 2 else (), *(float(a[3]),) if len(a) > 3 else ())
