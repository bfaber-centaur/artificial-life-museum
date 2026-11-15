"""Drift vs selection: how often does one new mutant take over?

Two textbook population-genetics models, written from their definitions:

* Moran process (Moran 1958): N individuals; each event one individual is chosen to reproduce
  with probability proportional to fitness (mutant r = 1 + s, resident 1) and its copy replaces
  one individual chosen uniformly. Only events that change the mutant count matter for fixation,
  so we simulate the embedded jump chain: from i mutants (0 < i < N) the count goes up with
  probability r / (1 + r), down otherwise. Exact fixation probability from one mutant:
      rho = (1 - 1/r) / (1 - 1/r**N),  rho = 1/N when r = 1.
* Wright-Fisher (Fisher 1930, Wright 1931): N haploids; each generation the next N are drawn
  binomially with mutant probability p r / (p r + 1 - p). Kimura's (1962) diffusion
  approximation for one starting mutant: u = (1 - exp(-2 s)) / (1 - exp(-2 N s)).

  python drift.py moran OUT.jsonl     fixation probability for N in {20, 200} over a range of s
  python drift.py fates OUT.jsonl      500 Wright-Fisher frequency paths, N 1000, s 0.02
"""
import json
import sys

import numpy as np


def moran_exact(N, s):
    r = 1.0 + s
    if abs(s) < 1e-15:
        return 1.0 / N
    return (1 - 1 / r) / (1 - r ** (-N))


def moran_fixations(N, s, reps, rng):
    """Number of replicate runs (each starting from one mutant) in which the mutant fixes."""
    up = (1 + s) / (2 + s)
    i = np.ones(reps, dtype=np.int64)
    alive = np.ones(reps, dtype=bool)
    while alive.any():
        idx = np.flatnonzero(alive)
        i[idx] += np.where(rng.random(idx.size) < up, 1, -1)
        alive[idx] = (i[idx] > 0) & (i[idx] < N)
    return int((i == N).sum())


def kimura(N, s):
    if abs(s) < 1e-15:
        return 1.0 / N
    return (1 - np.exp(-2 * s)) / (1 - np.exp(-2 * N * s))


def wright_fisher_paths(N, s, reps, gens, rng):
    """Mutant frequency per generation, shape (gens + 1, reps); every run starts from one copy."""
    k = np.ones(reps, dtype=np.int64)
    out = np.empty((gens + 1, reps), dtype=np.float32)
    out[0] = k / N
    r = 1.0 + s
    for g in range(1, gens + 1):
        p = k / N
        q = np.clip(p * r / (p * r + 1 - p), 0.0, 1.0)
        k = rng.binomial(N, q)
        out[g] = k / N
    return out


S_GRID = [-0.05, -0.02, -0.01, -0.005, 0.0, 0.005, 0.01, 0.02, 0.05, 0.1]
N_GRID = [20, 200]
REPS = 40000


def run_moran(path):
    rows = []
    for N in N_GRID:
        for j, s in enumerate(S_GRID):
            rng = np.random.default_rng([2026, 11, 15, N, j])
            fixed = moran_fixations(N, s, REPS, rng)
            rho = moran_exact(N, s)
            se = np.sqrt(rho * (1 - rho) / REPS)
            rows.append(dict(model="moran", N=N, s=s, reps=REPS, fixed=fixed, sim=fixed / REPS,
                             exact=rho, se_exact=se, z=(fixed / REPS - rho) / se,
                             seed=[2026, 11, 15, N, j]))
            print(json.dumps(rows[-1]))
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


FATES = dict(N=1000, s=0.02, reps=500, gens=1500, seed=[2026, 11, 15, 1])


def fates_paths():
    f = FATES
    return wright_fisher_paths(f["N"], f["s"], f["reps"], f["gens"], np.random.default_rng(f["seed"]))


def run_fates(path):
    N, s, reps, gens = FATES["N"], FATES["s"], FATES["reps"], FATES["gens"]
    P = fates_paths()
    final = P[-1]
    row = (dict(model="wright-fisher", N=N, s=s, reps=reps, gens=gens,
                          fixed=int((final == 1).sum()), lost=int((final == 0).sum()),
                          unresolved=int(((final > 0) & (final < 1)).sum()),
                          kimura=kimura(N, s),
                          lost_by_gen20=int((P[20] == 0).sum()), seed=FATES["seed"]))
    print(json.dumps(row))
    with open(path, "w") as f:
        f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "moran":
        run_moran(sys.argv[2])
    elif cmd == "fates":
        run_fates(sys.argv[2])
