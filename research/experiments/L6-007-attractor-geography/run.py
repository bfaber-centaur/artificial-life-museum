"""L6-007 runner (protocol.md in this directory; fixed before any run).

    python research/experiments/L6-007-attractor-geography/run.py noise --variant primary|R26|T40
    python research/experiments/L6-007-attractor-geography/run.py paths
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "L6-field"))
from field import Batch, summarize  # noqa: E402
from tables import phenotype  # noqa: E402

from alm import specimens  # noqa: E402

VARIANTS = {  # name: (R, T, sigma, N, horizon_tu, checkpoints_tu)
    "primary": (13, 10, 0.020, 128, 2000, (250, 500, 1000, 2000)),
    "R26": (26, 10, 0.0205, 256, 1000, (250, 500, 1000)),
    "T40": (13, 40, 0.019, 128, 1000, (250, 500, 1000)),
}
MU = 0.155
SEEDS = {"orbium": "S001", "circler": "S102", "ring": "S103"}
EPS = (0.01, 0.03, 0.1, 0.3)
REPS = 6


def cells(name, R):
    p = specimens.load(SEEDS[name]).cells / 255.0
    if R != 13:
        p = np.clip(ndimage.zoom(p, R / 13, order=1), 0, 1)
    return p


def place(p, N):
    A = np.zeros((N, N))
    h, w = p.shape
    A[(N - h) // 2 : (N - h) // 2 + h, (N - w) // 2 : (N - w) // 2 + w] = p
    return A


def classify(d):
    return d["fate"].upper() if d["fate"] != "localized" else phenotype({k: str(v) for k, v in d.items()})


def run_batch(starts, R, T, sigma, horizon, checkpoints, chunk=40):
    """Returns per-world lists of (class at each checkpoint), final summary, final state."""
    steps = int(round(horizon * T))
    win = int(round(100 * T))
    out = []
    for k in range(0, len(starts), chunk):
        S = np.array(starts[k : k + chunk])
        b = Batch(R=R, T=T, mu=[MU] * len(S), sigma=[sigma] * len(S))
        cps = [int(round(c * T)) for c in checkpoints]
        res = b.run(S, steps, snap_every=max(1, int(T * 5)), snap_from=steps - win, keep=tuple(cps))
        per = [[] for _ in range(len(S))]
        for c in cps[:-1]:
            # checkpoint windows: re-summarise the series up to c
            sub = {"mass": res["mass"][: c + 1], "pos": res["pos"][: c + 1], "snaps": [],
                   "final": res["states"][c]}
            for i, d in enumerate(summarize(sub, R, T, win)):
                per[i].append(classify(d))
        fin = summarize(res, R, T, win)
        for i, d in enumerate(fin):
            per[i].append(classify(d))
            out.append((per[i], d, res["final"][i]))
        print(f"  {k + len(S)}/{len(starts)}", flush=True)
    return out


def same_up_to_shift(A, B):
    """True if B equals A up to a periodic translation (bitwise)."""
    f = np.fft.irfft2(np.fft.rfft2(A) * np.conj(np.fft.rfft2(B)), s=A.shape)
    dy, dx = np.unravel_index(np.argmax(f), f.shape)
    return np.array_equal(np.roll(B, (dy, dx), (0, 1)), A)


def noise(variant):
    R, T, sigma, N, horizon, cps = VARIANTS[variant]
    starts, meta = [], []
    for i_s, s in enumerate(SEEDS):
        base = place(cells(s, R), N)
        support = ndimage.binary_dilation(base > 0, iterations=3 * R // 13)
        starts.append(base)
        meta.append((s, 0.0, -1))
        for i_e, e in enumerate(EPS):
            for k in range(REPS):
                xi = np.random.default_rng(1000 * i_s + 100 * i_e + k).uniform(-1, 1, base.shape)
                starts.append(np.clip(base + e * xi * support, 0, 1))
                meta.append((s, e, k))
    t0 = time.time()
    res = run_batch(starts, R, T, sigma, horizon, cps)
    ref = {m[0]: r for m, r in zip(meta, res) if m[2] == -1}
    phen = {"orbium": "GLIDER", "circler": "CIRCLER", "ring": "STATIC"}
    rows = []
    for (s, e, k), (cls, d, F) in zip(meta, res):
        rc, rd, rF = ref[s]
        if s == "ring":
            ret = cls[-1] == "STATIC" and same_up_to_shift(rF, F)
        else:
            ret = (cls[-1] == phen[s] and abs(d["mass_mean"] / rd["mass_mean"] - 1) <= 0.01
                   and abs(d["gyr"] / rd["gyr"] - 1) <= 0.01 and abs(d["path_speed"] / rd["path_speed"] - 1) <= 0.02)
        rows.append({"variant": variant, "seed": s, "eps": e, "rep": k, "R": R, "T": T, "mu": MU, "sigma": sigma,
                     **{f"class_{c}tu": x for c, x in zip(cps, cls)}, "returns": ret,
                     "mass": d["mass_mean"], "gyr": d["gyr"], "path_speed": d["path_speed"], "speed": d["speed"],
                     "ref_mass": rd["mass_mean"], "ref_gyr": rd["gyr"], "ref_path_speed": rd["path_speed"]})
    write(HERE / f"noise-{variant}.csv", rows)
    np.savez_compressed(HERE / f"finals-noise-{variant}.npz", final=np.array([r[2] for r in res], dtype=np.float32))
    print("wrote noise", variant, f"{time.time() - t0:.0f}s")


def paths():
    R, T, sigma, N, horizon, cps = VARIANTS["primary"]
    seeds = {s: place(cells(s, R), N) for s in SEEDS}
    pairs = [("orbium", "circler"), ("circler", "ring"), ("orbium", "ring")]
    lams = np.round(np.arange(0, 1.0001, 0.05), 2)
    starts, meta = [], []
    for p, q in pairs:
        for lam in lams:
            starts.append((1 - lam) * seeds[p] + lam * seeds[q])
            meta.append((f"{p}-{q}", lam))
    t0 = time.time()
    res = run_batch(starts, R, T, sigma, horizon, cps)
    rows = [{"path": pq, "lambda": lam, **{f"class_{c}tu": x for c, x in zip(cps, cls)},
             "mass": d["mass_mean"], "gyr": d["gyr"], "path_speed": d["path_speed"], "speed": d["speed"]}
            for (pq, lam), (cls, d, F) in zip(meta, res)]
    write(HERE / "paths.csv", rows)
    np.savez_compressed(HERE / "finals-paths.npz", final=np.array([r[2] for r in res], dtype=np.float32))
    print("wrote paths", f"{time.time() - t0:.0f}s")


def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["noise", "paths"])
    ap.add_argument("--variant", default="primary", choices=list(VARIANTS))
    a = ap.parse_args()
    noise(a.variant) if a.what == "noise" else paths()
