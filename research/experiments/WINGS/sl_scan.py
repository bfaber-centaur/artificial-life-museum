"""SmoothLife glider scout (Rafler 2011 transition, other_worlds.SmoothLife, smooth time step).

Rule per index i: default_rng([13, i]) draws ra in [8, 16], b1 in [0.20, 0.32],
b2 = b1 + [0.03, 0.15], d1 in [0.20, 0.40], d2 = d1 + [0.05, 0.25]; alpha_n 0.028,
alpha_m 0.147, dt 0.1. World 192^2 with 12 random filled squares. 1500 steps.
Moving bodies: components (v > 0.5) smaller than 6 ra^2 whose nearest component 100 steps
earlier is more than 3 cells away. Writes sl_scan.jsonl and states/sl_<i>.npy.

  python sl_scan.py <start> <stop>
"""
import json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).parent))
from other_worlds import SmoothLife

HERE = Path(__file__).parent
N, STEPS = 192, 1500


def draw(i):
    rng = np.random.default_rng([13, i])
    ra = float(rng.uniform(8, 16)); b1 = float(rng.uniform(0.2, 0.32)); b2 = b1 + float(rng.uniform(0.03, 0.15))
    d1 = float(rng.uniform(0.2, 0.4)); d2 = d1 + float(rng.uniform(0.05, 0.25))
    A = np.zeros((N, N))
    for _ in range(12):
        y, x = rng.integers(0, N, 2); r = int(rng.integers(int(ra * 0.6), int(ra * 1.4)))
        A[np.ix_(np.arange(y - r, y + r) % N, np.arange(x - r, x + r) % N)] = 1.0
    return dict(ra=ra, b1=b1, b2=b2, d1=d1, d2=d2), A


def bodies(A, ra):
    lab, k = ndimage.label(A > 0.5)
    if not k:
        return []
    sz = ndimage.sum(np.ones_like(A), lab, range(1, k + 1))
    com = ndimage.center_of_mass(A, lab, range(1, k + 1))
    return [(np.array(c), s) for c, s in zip(com, sz) if s < 6 * ra * ra]


def main(a, b):
    for i in range(a, b):
        prm, A = draw(i)
        S = SmoothLife(A, **prm)
        for t in range(STEPS - 100):
            S.step()
        before = bodies(S.A, prm["ra"])
        for t in range(100):
            S.step()
        after = bodies(S.A, prm["ra"])
        moving = 0
        for c, s in after:
            if before:
                d = min(np.abs(((c - c0) + N / 2) % N - N / 2).max() for c0, _ in before)
                moving += d > 3 and d < 40
        rec = {"i": i, **prm, "cover": float((S.A > 0.5).mean()), "nbodies": len(after), "moving": int(moving),
               "ncomp": int(ndimage.label(S.A > 0.5)[1])}
        np.save(HERE / "states" / f"sl_{i}.npy", S.A.astype(np.float32))
        with (HERE / "sl_scan.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(i, rec["cover"].__round__(3), rec["nbodies"], rec["moving"], flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
