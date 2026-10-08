"""L6-008 runner (protocol.md in this directory; fixed before any run).

    python research/experiments/L6-008-pair-coupling/run.py
"""
import csv
import pickle
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "L6-field"))
from disturb_helpers import disturb, offsets  # noqa: E402
from field import Batch, centroids, components, summarize  # noqa: E402

from alm import specimens  # noqa: E402

R, T, MU, SIGMA, N = 13, 10, 0.15, 0.015, 128
WARM = 3000
PHASES = (0, 1, 2, 3, 4)
HORIZON = 3000  # 300 tu
WIN = 1000  # last 100 tu
GRIDS = {
    "none": [0.0],
    "I001": [round(0.02 * i, 2) for i in range(1, 11)],
    "I004": [round(0.05 * i, 2) for i in range(1, 13)],
    "I003": [round(0.1 * i, 1) for i in range(1, 11)],
}
M1, M2, M2SEP = 0.4358, 0.8736, 0.8716


def units(d, F):
    """Orbium units in a world: 0, 1, 2 or 'other' (protocol 'Outcome per world')."""
    if d["fate"] == "died":
        return 0
    if d["fate"] != "localized":
        return "other"
    m = d["mass_mean"]
    if d["speed"] > 0.2 and abs(m / M1 - 1) <= 0.05:
        return 1
    if d["speed"] > 0.2 and abs(m / M2 - 1) <= 0.05:
        return 2
    if abs(m / M2SEP - 1) <= 0.05 and components(F) >= 2:
        return 2
    return "other"


def recovery_time(mass, t_edit_rel=0):
    """First time (tu) after the edit when the 10-step windowed mass stays within 2% of M1 for 10 tu."""
    w = np.convolve(mass, np.ones(10) / 10, mode="valid")
    ok = np.abs(w / M1 - 1) <= 0.02
    need = int(10 * T)
    run = 0
    for i, o in enumerate(ok):
        run = run + 1 if o else 0
        if run >= need:
            return (i - need + 1) / T
    return float("nan")


def main():
    S = specimens.load("S101")
    warm = Batch(R, T, [MU], [SIGMA]).run(S.place(N)[None], WARM + max(PHASES), snap_every=10**9,
                                         keep=tuple(WARM + p for p in PHASES))
    # frames and validity checks on the undisturbed pair
    pair_states, halves, checks = [], [], []
    jobs = []
    for ph in PHASES:
        t = WARM + ph
        A = warm["states"][t][0]
        cx, cy = centroids(A[None])
        c = (cx[0], cy[0])
        v = warm["pos"][t, 0] - warm["pos"][t - 10, 0]
        h = v / np.hypot(*v)
        dx, dy = offsets(A.shape, *c)
        lat = dx * -h[1] + dy * h[0]
        port = lat > 0
        checks.append({"phase": ph, "port_mass": float(A[port].sum()) / R**2,
                       "starboard_mass": float(A[~port].sum()) / R**2,
                       "seam_frac": float(A[np.abs(lat) < 1].sum() / A.sum())})
        for kind, grid in GRIDS.items():
            for s in grid:
                E = A.copy() if kind == "none" else disturb(kind, A, s, c, h, R)
                jobs.append((kind, s, ph, E, port, E.sum() / A.sum() - 1))
    starts, idx = [], []
    for j, (kind, s, ph, E, port, dm) in enumerate(jobs):
        starts += [E, np.where(port, E, 0.0), np.where(port, 0.0, E)]
        idx.append(j)
    t0 = time.time()
    outs = []
    cache = Path("/tmp/claude-0/l6-cache")  # per-chunk results, so a restarted container resumes
    cache.mkdir(parents=True, exist_ok=True)
    for k in range(0, len(starts), 48):
        cf = cache / f"l6008-{k}.pkl"
        if cf.exists():
            outs += pickle.loads(cf.read_bytes())
            print(f"{k}: cached", flush=True)
            continue
        n0 = len(outs)
        B = np.array(starts[k : k + 48])
        res = Batch(R, T, [MU] * len(B), [SIGMA] * len(B)).run(B, HORIZON, snap_every=50, snap_from=HORIZON - WIN)
        for i, d in enumerate(summarize(res, R, T, WIN)):
            outs.append((d, res["final"][i], res["mass"][:, i]))
        cf.write_bytes(pickle.dumps(outs[n0:]))
        print(f"{k + len(B)}/{len(starts)} {time.time() - t0:.0f}s", flush=True)
    rows = []
    for j, (kind, s, ph, E, port, dm) in enumerate(jobs):
        (dp, Fp, mp), (da, Fa, ma), (db, Fb, mb) = outs[3 * j : 3 * j + 3]
        n_pair, n_port, n_stb = units(dp, Fp), units(da, Fa), units(db, Fb)
        valid = all(isinstance(n, int) for n in (n_port, n_stb))
        mismatch = (valid and isinstance(n_pair, int) and n_pair != n_port + n_stb) or (valid and n_pair == "other")
        rows.append({"disturbance": kind, "s": s, "phase": ph, "t0": WARM + ph, "dmass_frac": dm,
                     "n_pair": n_pair, "n_port": n_port, "n_starboard": n_stb, "baseline_valid": valid,
                     "mismatch": mismatch,
                     "direction": ("" if not mismatch or not isinstance(n_pair, int) else
                                   "rescue" if n_pair > n_port + n_stb else "drag-down"),
                     "pair_mass": dp["mass_mean"], "pair_speed": dp["speed"], "port_mass": da["mass_mean"],
                     "starboard_mass": db["mass_mean"],
                     "rec_pair_tu": recovery_time(mp) if n_pair == 1 else float("nan"),
                     "rec_starboard_alone_tu": recovery_time(mb) if n_stb == 1 else float("nan")})
    with open(HERE / "pair-coupling.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    with open(HERE / "validity.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(checks[0]))
        w.writeheader()
        w.writerows(checks)
    print("wrote pair-coupling.csv", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
