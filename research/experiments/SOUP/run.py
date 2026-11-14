"""Run one SOUP world and save snapshots.

  python run.py <name> --rule 9 --seed 0 --n 256 --steps 6000 --every 50 [--founders 16 --density 0.3
                 --mut-every 20 --mut-sd 0.15 --start voronoi|patches]

Writes <out>/<name>.npz: A (snap, n, n) float16, G (snap, K, n, n) uint8 (genome x 255), t, and
the mutation log; prints mass and final-state sha256.
"""
import argparse, hashlib, json, os, sys, time
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from soup import Kernels, Soup

OUT = Path(os.environ.get("SOUP_OUT", Path(__file__).parent / "states"))


def initial(kern, rng, n, founders, density, start, founder_sd):
    K = kern.K
    genomes = np.clip(kern.h[None] + rng.normal(0, founder_sd, (founders, K)), 0, 1)
    if start == "voronoi":
        cy, cx = rng.uniform(0, n, (2, founders))
        y, x = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
        dy = np.abs(y[None] - cy[:, None, None]); dy = np.minimum(dy, n - dy)
        dx = np.abs(x[None] - cx[:, None, None]); dx = np.minimum(dx, n - dx)
        owner = np.argmin(dy ** 2 + dx ** 2, axis=0)
        A = rng.uniform(0, density, (n, n))
    else:  # patches of noise
        A = np.zeros((n, n)); owner = np.zeros((n, n), int)
        p = 40
        for f in range(founders):
            y, x = rng.integers(0, n, 2)
            gy = (np.arange(p) + y) % n; gx = (np.arange(p) + x) % n
            A[np.ix_(gy, gx)] = rng.uniform(0, 1, (p, p)); owner[np.ix_(gy, gx)] = f
    G = np.moveaxis(genomes[owner], -1, 0)
    return A, G, owner, genomes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("--rule", type=int, default=9); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n", type=int, default=256); ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--every", type=int, default=50); ap.add_argument("--founders", type=int, default=16)
    ap.add_argument("--density", type=float, default=0.3); ap.add_argument("--start", default="voronoi")
    ap.add_argument("--founder-sd", type=float, default=0.25)
    ap.add_argument("--mut-every", type=int, default=20); ap.add_argument("--mut-sd", type=float, default=0.15)
    ap.add_argument("--mut-r", type=int, default=10); ap.add_argument("--halo", type=float, default=4.0)
    ap.add_argument("--inherit", default="blend")
    a = ap.parse_args()
    kern = Kernels(np.random.default_rng([7, a.rule]))
    rng = np.random.default_rng([99, a.seed])
    A, G, owner, genomes = initial(kern, rng, a.n, a.founders, a.density, a.start, a.founder_sd)
    S = Soup(kern, A, G, seed=a.seed, mut_every=a.mut_every, mut_sd=a.mut_sd, mut_r=a.mut_r, halo=a.halo, inherit=a.inherit)
    m0 = S.A.sum()
    As, Gs, ts = [], [], []
    def snap():
        As.append(S.A.astype(np.float16)); Gs.append(np.round(S.G * 255).astype(np.uint8)); ts.append(S.t)
    snap(); t0 = time.time()
    for _ in range(a.steps):
        S.step()
        if S.t % a.every == 0:
            snap()
    sha = hashlib.sha256(np.ascontiguousarray(S.A).tobytes() + np.ascontiguousarray(S.G).tobytes()).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / f"{a.name}.npz", A=np.array(As), G=np.array(Gs), t=np.array(ts), owner=owner,
                        founders=genomes, args=json.dumps(vars(a)), mutlog=json.dumps(S.log))
    rec = dict(name=a.name, args=vars(a), mass0=float(m0), mass1=float(S.A.sum()),
               rel_drift=float(S.A.sum() / m0 - 1), final_sha256=sha, sec=round(time.time() - t0))
    with open(Path(__file__).parent / "runs.jsonl", "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
