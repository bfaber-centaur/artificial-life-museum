"""Flow-Lenia scout: random 10-kernel rules (FlowRule.random, rng [7, seed]) from a 40x40 uniform
noise patch on a 128^2 torus. 3000 steps (600 time units at dt 0.2). Records per seed: mass drift,
components above 0.05 at the end, bounding size of the largest, and centroid travel of the
largest component over the last 500 steps. Writes flow_scan.jsonl and states/flow_<seed>.npy.

  python flow_scan.py <start> <stop>
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from scipy import ndimage  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from flow_lenia import FlowLenia, FlowRule  # noqa: E402

HERE = Path(__file__).parent
N, STEPS, TAIL = 128, 3000, 500


def seed_state(rng, n=N, patch=40):
    A = np.zeros((n, n))
    o = (n - patch) // 2
    A[o:o + patch, o:o + patch] = rng.uniform(0, 1, (patch, patch))
    return A


def pcentroid(A):
    n = A.shape[0]
    th = 2 * np.pi * np.arange(n) / n
    my = A.sum(1); mx = A.sum(0)
    cy = (np.angle((my * np.exp(1j * th)).sum()) % (2 * np.pi)) * n / (2 * np.pi)
    cx = (np.angle((mx * np.exp(1j * th)).sum()) % (2 * np.pi)) * n / (2 * np.pi)
    return np.array([cy, cx])


def comps(A, thr=0.05):
    # periodic labelling: label a 3x3 tiling and keep labels touching the centre tile
    lab, k = ndimage.label(A > thr)
    # merge across torus edges
    if k:
        par = list(range(k + 1))
        def f(i):
            while par[i] != i:
                par[i] = par[par[i]]; i = par[i]
            return i
        for a, b in list(zip(lab[0], lab[-1])) + list(zip(lab[:, 0], lab[:, -1])):
            if a and b:
                par[f(a)] = f(b)
        lab = np.vectorize(f)(lab) * (lab > 0)
        ids = [i for i in np.unique(lab) if i]
        return lab, ids
    return lab, []


def main(a, b):
    out = HERE / "flow_scan.jsonl"
    (HERE / "states").mkdir(exist_ok=True)
    for seed in range(a, b):
        rng = np.random.default_rng([7, seed])
        ru = FlowRule.random(rng)
        L = FlowLenia(ru, seed_state(rng))
        m0 = L.A.sum()
        traj = []
        for t in range(STEPS):
            L.step()
            if t >= STEPS - TAIL and t % 50 == 0:
                traj.append(pcentroid(L.A))
        lab, ids = comps(L.A)
        sizes = sorted(((lab == i).sum() for i in ids), reverse=True)
        d = np.diff(np.array(traj), axis=0)
        d = (d + N / 2) % N - N / 2
        travel = float(np.abs(d.sum(0)).max()) if len(d) else 0.0
        rec = {"seed": seed, "mass0": m0, "mass_drift": float(L.A.sum() - m0), "max": float(L.A.max()),
               "ncomp": len(ids), "sizes": [int(x) for x in sizes[:6]], "cover": float((L.A > 0.05).mean()),
               "travel_tail": travel, "rule": ru.to_dict()}
        np.save(HERE / "states" / f"flow_{seed}.npy", L.A.astype(np.float32))
        with out.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(seed, rec["ncomp"], rec["sizes"][:3], "cover %.2f travel %.1f drift %.1e" % (rec["cover"], travel, rec["mass_drift"]), flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
