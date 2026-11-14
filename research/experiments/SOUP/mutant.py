"""Jenkin's test: does one mutation survive blending?

A one-species world (every cell has the founder genome h = the kernel set's own weights) of
kernel set 16 settles for `settle` steps from uniform(0, 0.3) noise, with no mutation. Then one
mutant disc (radius 10, centred on the matter-weighted random cell, delta ~ N(0, 0.15) per weight,
clipped to [0, 1]) is written and the world runs `steps` more steps with no further mutation,
under inherit = blend and inherit = dominant from the same mutated state.

Metric every 50 steps: "mutant mass" = matter (A > 0.05) whose genome is still more than halfway
from h to h + delta along delta's direction, i.e. (g - h).u > |delta_eff| / 2, where delta_eff is
the clipped change actually written. Writes mutant.jsonl.

  python mutant.py <k0> <k1>      (mutant ids; each id fixes the mutation's rng)
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from soup import Kernels, Soup

HERE = Path(__file__).parent
RULE, N, SETTLE, STEPS, EVERY = 16, 256, 2000, 5000, 50
STATE = Path(os.environ.get("SOUP_OUT", HERE / "states")) / "mutant_settled.npz"


def settled(kern):
    if STATE.exists():
        d = np.load(STATE)
        return d["A"], d["G"]
    A = np.random.default_rng([99, 1000]).uniform(0, 0.3, (N, N))
    G = np.broadcast_to(kern.h[:, None, None], (kern.K, N, N)).copy()
    S = Soup(kern, A, G, mut_every=0)
    for _ in range(SETTLE):
        S.step()
    STATE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(STATE, A=S.A, G=S.G)
    return S.A, S.G


def main(k0, k1):
    kern = Kernels(np.random.default_rng([7, RULE]))
    A0, G0 = settled(kern)
    h = kern.h
    for k in range(k0, k1):
        rng = np.random.default_rng([555, k])
        c = rng.choice(N * N, p=(A0 / A0.sum()).ravel()); y, x = divmod(int(c), N)
        delta = rng.normal(0, 0.15, kern.K)
        G1 = G0.copy()
        yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
        dy = np.minimum(np.abs(yy - y), N - np.abs(yy - y)); dx = np.minimum(np.abs(xx - x), N - np.abs(xx - x))
        disc = dy ** 2 + dx ** 2 <= 100
        G1[:, disc] = np.clip(G1[:, disc] + delta[:, None], 0, 1)
        deff = np.clip(h + delta, 0, 1) - h
        u = deff / np.linalg.norm(deff); half = np.linalg.norm(deff) / 2
        for mode in ("blend", "dominant"):
            S = Soup(kern, A0, G1, mut_every=0, inherit=mode)
            series = []
            for t in range(STEPS + 1):
                if t % EVERY == 0:
                    proj = np.tensordot(u, S.G - h[:, None, None], 1)
                    live = S.A > 0.05
                    series.append(round(float(S.A[live & (proj > half)].sum()), 3))
                if t < STEPS:
                    S.step()
            rec = dict(mutant=k, mode=mode, y=y, x=x, delta=delta.round(4).tolist(), dnorm=float(np.linalg.norm(deff)),
                       every=EVERY, mutant_mass=series,
                       final_sha256=hashlib.sha256(S.A.tobytes() + S.G.tobytes()).hexdigest())
            with open(HERE / "mutant.jsonl", "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(k, mode, series[0], series[len(series) // 2], series[-1], flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
