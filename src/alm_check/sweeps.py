"""Lane 3 numerical red-team sweeps on S001 Orbium.

Usage (repo root, after ./scripts/bootstrap.sh):
    .venv/bin/python -m alm_check.sweeps {xcheck,timestep,resolution,boundary,precision,all}

Each experiment writes a summary CSV to research/traces/lane3/. Every run is
deterministic (no RNG). Statistics use the window t >= T0 time units.
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

from .lenia import REPO, Rule, World, load_orbium, place, recentre, run

OUT = REPO / "research" / "traces" / "lane3"
HORIZON = 400.0  # time units (4000 steps at T = 10, the S001 baseline run)
T0 = 100.0  # stats window start, time units
R0 = 13


def scaled_orbium(R: float, order: int = 0) -> np.ndarray:
    """Catalog cells resampled from R0 to R (order 0 = upstream nearest zoom)."""
    cells = load_orbium()
    if R == R0:
        return cells
    return np.clip(ndimage.zoom(cells, R / R0, order=order), 0, 1)


def dominant_period(x: np.ndarray, min_period: float = 2.0) -> tuple[float, float]:
    """(period in samples, peak power fraction) of a detrended series."""
    x = np.asarray(x, float)
    if len(x) < 16 or not np.isfinite(x).all():
        return float("nan"), float("nan")
    t = np.arange(len(x))
    x = x - np.polyval(np.polyfit(t, x, 1), t)
    p = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x))
    ok = (f > 0) & (f <= 1 / min_period)
    ok &= f >= 4 / len(x)  # ignore drift
    if not ok.any() or p[ok].sum() == 0:
        return float("nan"), float("nan")
    i = np.argmax(np.where(ok, p, 0))
    return 1 / f[i], p[i] / p[ok].sum()


def summarise(tr: dict, rule: Rule, n: int, start_mass: float) -> dict:
    steps, T, R = tr["step"], rule.T, rule.R
    tu = steps / T
    alive_end = bool(tr["alive"][-1]) and tu[-1] >= HORIZON - 1e-9
    w = (tu >= T0) & np.isfinite(tr["vx"])
    out = dict(final_t=float(tu[-1]), alive=int(alive_end))
    if w.sum() < 10:
        out["fate"] = "dies" if not tr["alive"][-1] else "short"
        return out
    mass, gyr = tr["mass"][w], tr["gyradius"][w]
    vx, vy = tr["vx"][w].mean(), tr["vy"][w].mean()  # cells per step, every = 1
    per, frac = dominant_period(mass, min_period=2.0)
    big = gyr.max() * R > n / 4 or mass.max() > 4 * start_mass
    out.update(
        fate="dies" if not alive_end else ("explodes" if big else "persists"),
        mass=mass.mean(), mass_rel_sd=mass.std() / mass.mean(),
        mass_min=mass.min(), mass_max=mass.max(),
        gyradius=gyr.mean(),
        speed=np.hypot(vx, vy) * T / R, speed_cells_per_step=np.hypot(vx, vy),
        heading_deg=np.degrees(np.arctan2(vy, vx)),
        mass_period_steps=per, mass_period_tu=per / T, mass_period_power=frac,
    )
    return out


def one_run(job: dict) -> dict:
    rule = Rule(**job.get("rule", {}))
    n = job["n"]
    dtype = np.float32 if job.get("dtype") == "float32" else np.float64
    cells = scaled_orbium(rule.R, job.get("zoom_order", 0))
    A = place(cells, n, dtype)
    w = World(A, rule, path=job.get("path", "fft"), boundary=job.get("boundary", "wrap"))
    t = time.time()
    steps = int(round(HORIZON * rule.T))
    tr = run(w, steps, every=1, keep_states=tuple(job.get("keep", ())))
    row = dict(job_id=job["id"], n=n, R=rule.R, T=rule.T, mu=rule.mu, sigma=rule.sigma,
               core=rule.core, growth=rule.growth, path=w.path, boundary=w.boundary,
               dtype=np.dtype(dtype).name, zoom_order=job.get("zoom_order", 0), steps=steps)
    row.update(summarise(tr, rule, n, cells.sum() / rule.R**2))
    row["wall_s"] = round(time.time() - t, 1)
    if job.get("return_trace"):
        row["_trace"] = tr
    return row


def _pool_map(jobs):
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    with Pool(min(len(jobs), os.cpu_count() or 1)) as p:
        return p.map(one_run, jobs, chunksize=1)


def _write(name: str, rows: list[dict]):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    keys = list(dict.fromkeys(k for r in rows for k in r))
    path = OUT / f"{name}.csv"
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, keys)
        wr.writeheader()
        for r in rows:
            wr.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    print(f"wrote {path.relative_to(REPO)}")
    for r in rows:
        print({k: r.get(k) for k in ("job_id", "fate", "mass", "mass_rel_sd", "gyradius",
                                       "speed", "heading_deg", "mass_period_tu")})


# ------------------------------------------------------------ experiments


def exp_timestep():
    Ts = [1, 2, 3, 4, 5, 7, 10, 15, 20, 40, 80, 160, 320]
    return [dict(id=f"T{T}", n=128, rule=dict(T=T)) for T in Ts]


def exp_resolution():
    jobs = []
    for R in [5, 6, 7, 8, 9, 10, 11, 13, 16, 20, 26, 39, 52]:
        n = 2 * int(round(64 * R / R0))
        for order in (0, 1):
            if R == R0 and order == 1:
                continue
            jobs.append(dict(id=f"R{R}-z{order}", n=n, rule=dict(R=R), zoom_order=order))
    return jobs


def exp_boundary():
    jobs = [dict(id=f"N{n}", n=n) for n in (32, 40, 44, 48, 52, 56, 64, 96, 128, 256)]
    jobs.append(dict(id="N128-dead-edge", n=128, path="direct", boundary="constant"))
    jobs.append(dict(id="N128-direct-wrap", n=128, path="direct", boundary="wrap"))
    return jobs


def exp_precision():
    return [dict(id=f"{d}", n=128, dtype=d) for d in ("float64", "float32")]


EXPERIMENTS = dict(timestep=exp_timestep, resolution=exp_resolution,
                   boundary=exp_boundary, precision=exp_precision)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("experiment", choices=[*EXPERIMENTS, "all"])
    a = ap.parse_args(argv)
    names = list(EXPERIMENTS) if a.experiment == "all" else [a.experiment]
    for name in names:
        _write(name, _pool_map(EXPERIMENTS[name]()))


if __name__ == "__main__":
    main()
