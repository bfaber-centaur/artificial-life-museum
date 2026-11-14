"""Is a grower fitter, or just lucky? Replay each C078 mutant genome at new places.

Same settled one-species world as mutant.py (kernel set 16, 256²). For mutant k (its delta read
from mutant.jsonl) and placement j = 0..P-1, the disc (radius 10) is centred on a mass-weighted
random cell from default_rng([777, k, j]) and set to clip(h + delta). The world then runs
`steps` steps with no background mutation under inherit = dominant. Metric as mutant.py:
mutant mass every 50 steps. Writes replay.jsonl.

  python replay.py <k0> <k1> [P] [steps]
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from soup import Kernels, Soup
from mutant import RULE, N, settled

HERE = Path(__file__).parent


def main(k0, k1, P=6, steps=2500, every=50):
    kern = Kernels(np.random.default_rng([7, RULE]))
    A0, G0 = settled(kern)
    h = kern.h
    deltas = {}
    for l in open(HERE / "mutant.jsonl"):
        r = json.loads(l)
        deltas[r["mutant"]] = np.array(r["delta"])
    yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    for k in range(k0, k1):
        mut = np.clip(h + deltas[k], 0, 1); deff = mut - h
        u = deff / np.linalg.norm(deff); half = np.linalg.norm(deff) / 2
        for j in range(P):
            rng = np.random.default_rng([777, k, j])
            c = rng.choice(N * N, p=(A0 / A0.sum()).ravel()); y, x = divmod(int(c), N)
            dy = np.minimum(np.abs(yy - y), N - np.abs(yy - y)); dx = np.minimum(np.abs(xx - x), N - np.abs(xx - x))
            G1 = G0.copy(); disc = dy ** 2 + dx ** 2 <= 100
            G1[:, disc] = mut[:, None]
            S = Soup(kern, A0, G1, mut_every=0, inherit="dominant")
            series = []
            for t in range(steps + 1):
                if t % every == 0:
                    proj = np.tensordot(u, S.G - h[:, None, None], 1)
                    series.append(round(float(S.A[(S.A > 0.05) & (proj > half)].sum()), 3))
                if t < steps:
                    S.step()
            rec = dict(mutant=k, placement=j, y=y, x=x, every=every, mutant_mass=series,
                       final_sha256=hashlib.sha256(S.A.tobytes() + S.G.tobytes()).hexdigest())
            with open(HERE / "replay.jsonl", "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(k, j, series[0], series[-1], flush=True)


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:]]
    main(*a)
