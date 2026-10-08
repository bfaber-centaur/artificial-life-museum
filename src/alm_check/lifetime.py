"""L3-003 runner: lifetime of the S102 circler (replication of Lane 6, PR #27).

Protocol: research/experiments/L3-003-circler-lifetime/PREREGISTRATION.md
(fixed before this code was run). Writes research/traces/lane3/L3-003/.

    .venv/bin/python -m alm_check.lifetime        # Q1-Q5
    .venv/bin/python -m alm_check.lifetime --q6   # Q6 (amendment 1): lifetime distribution
"""

from __future__ import annotations

import csv
import sys
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

from .lenia import REPO, Rule, World, periodic_centroid, place

OUT = REPO / "research" / "traces" / "lane3" / "L3-003"
SEED = REPO / "research" / "specimens" / "S102-circler" / "initial-cells-u8.csv"
MU, SIGMA, DEATH = 0.155, 0.020, 0.01
EPS, REPS = (0.01, 0.03), 6

# id: (R, T, resize, noisy, horizon tu)
CONDITIONS = {
    "A0": (13, 10, "native", False, 5000),
    "A1": (13, 10, "native", True, 5000),
    "B26-block": (26, 10, "block", False, 8000),
    "B26-nearest": (26, 10, "nearest", False, 8000),
    "B26-cubic": (26, 10, "cubic", False, 8000),
    "B39-block": (39, 10, "block", False, 8000),
    "B39-nearest": (39, 10, "nearest", False, 8000),
    "B39-cubic": (39, 10, "cubic", False, 8000),
    "B26-bilinear": (26, 10, "bilinear", False, 100),
    "B39-bilinear": (39, 10, "bilinear", False, 100),
    "D20": (13, 20, "native", False, 8000),
    "D40": (13, 40, "native", False, 8000),
    "E26": (26, 10, "block", True, 5000),
    # amendment 1: delta = 1e-12 copies, rng 7000 + 100 i_R + k
    "Q6-13": (13, 10, "native", True, 5000),
    "Q6-26": (26, 10, "block", True, 8000),
}
Q6 = {"Q6-13": (0, 24), "Q6-26": (1, 12)}  # cond: (i_R, replicates)
DELTA = 1e-12


def seed(R: int, resize: str) -> np.ndarray:
    c = np.loadtxt(SEED, delimiter=",") / 255.0
    k = R // 13
    if resize in ("native", "block"):
        return np.kron(c, np.ones((k, k)))
    order = {"nearest": 0, "bilinear": 1, "cubic": 3}[resize]
    return np.clip(ndimage.zoom(c, k, order=order), 0, 1)


def starts(cond: str) -> list[tuple[float, int, np.ndarray]]:
    R, T, resize, noisy, _ = CONDITIONS[cond]
    base = place(seed(R, resize), 128 * R // 13)
    if not noisy:
        return [(0.0, -1, base)]
    support = ndimage.binary_dilation(base > 0, iterations=3 * R // 13)
    if cond in Q6:
        i_r, reps = Q6[cond]
        return [(DELTA, k, np.clip(base + DELTA * np.random.default_rng(7000 + 100 * i_r + k)
                                   .uniform(-1, 1, base.shape) * support, 0, 1))
                for k in range(reps)]
    out = []
    for i_e, e in enumerate(EPS):
        for k in range(REPS):
            xi = np.random.default_rng(1000 * 1 + 100 * i_e + k).uniform(-1, 1, base.shape)
            out.append((e, k, np.clip(base + e * xi * support, 0, 1)))
    return out


def run_one(job) -> dict:
    cond, e, k, A0 = job
    R, T, _, _, horizon = CONDITIONS[cond]
    w = World(A0.copy(), Rule(R=R, T=T, mu=MU, sigma=SIGMA))
    steps = int(horizon * T)
    mass_tu, cen_tu = [], []
    death = None
    for s in range(1, steps + 1):
        w.step()
        m = w.A.sum() / R**2
        if death is None and m < DEATH:
            death = s
        if s % T == 0:
            mass_tu.append(m)
            cen_tu.append(periodic_centroid(w.A) if m > 0 else (np.nan, np.nan))
        if death is not None and s >= death + 10 * T:  # 10 tu past death is enough
            break
    rid = f"{cond}" + ("" if e == 0 else f"-e{e}-r{k}")
    np.savez_compressed(OUT / f"{rid}.npz", mass=np.array(mass_tu), centroid=np.array(cen_tu))
    row = dict(run_id=f"L3-003-{rid}", condition=cond, R=R, T=T, eps=e, rep=k,
               death_step="" if death is None else death,
               death_tu="" if death is None else death / T,
               mass_last_100tu=float(np.mean(mass_tu[-100:])), steps_run=s)
    print(row, flush=True)
    return row


def run_all(jobs) -> list[dict]:
    with Pool(4) as pool:
        rows = pool.map(run_one, jobs, chunksize=1)
    order = list(CONDITIONS)
    rows.sort(key=lambda r: (order.index(r["condition"]), r["eps"], r["rep"]))
    return rows


def write(rows: list[dict], name: str) -> None:
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if "--q6" in sys.argv:
        jobs = [(c, e, k, A) for c in Q6 for e, k, A in starts(c)]
        jobs.sort(key=lambda j: -CONDITIONS[j[0]][0])
        write(run_all(jobs), "q6.csv")
        return
    same = np.array_equal(seed(26, "nearest"), seed(26, "block")), \
        np.array_equal(seed(39, "nearest"), seed(39, "block"))
    print("nearest == block bitwise at R26, R39:", same, flush=True)
    skip = {c for c, s in zip(("B26-nearest", "B39-nearest"), same) if s}
    jobs = [(c, e, k, A) for c in CONDITIONS if c not in skip | set(Q6) for e, k, A in starts(c)]
    jobs.sort(key=lambda j: -CONDITIONS[j[0]][0] ** 2 * CONDITIONS[j[0]][1] * CONDITIONS[j[0]][4])
    write(run_all(jobs), "lifetimes.csv")
    with open(OUT / "nearest-equals-block.txt", "w") as f:
        f.write(f"R26 {same[0]}\nR39 {same[1]}\n")


if __name__ == "__main__":
    main()
