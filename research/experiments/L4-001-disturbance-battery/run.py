#!/usr/bin/env python3
"""L4-001 runner: S001 disturbance battery (see protocol.md next to this file).

Subcommands (run from the repo root with .venv/bin/python):

    run.py one    --iv I002 --s 0.4 --t0 1000 [--size 128] [--engine ref] [--save DIR]
    run.py sweep  [--ivs I001,I002,I003,I004] [--out results/coarse.csv]
    run.py bisect --coarse results/coarse.csv [--out results/bisect.csv]

Every run is deterministic; its run ID reproduces it.
"""
import argparse
import csv
import functools
import json
import importlib.util
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from alm import disturb  # noqa: E402

S001 = os.path.join(ROOT, "research", "specimens", "S001-orbium")
R, T, MU, SIGMA, BETA = 13, 10, 0.15, 0.015, [1.0]
PHASES = (1000, 1001, 1002, 1003, 1004)
HORIZON = 2000
WINDOW = 500
GRIDS = {
    "I001": [round(0.05 * i, 4) for i in range(20)],
    "I002": [round(0.05 * i, 4) for i in range(21)],
    "I003": [round(0.05 * i, 4) for i in range(21)],
    "I004": [round(0.05 * i, 4) for i in range(20)],
}
BISECT_WIDTH = 1 / 256

# Discretisation conditions (protocol amendment A1). "base" is the original protocol.
CONDS = {"base": (13, 10, 1), "T20": (13, 20, 1), "R26": (26, 10, 2)}
COND = "base"
ZOOM = 1
SAMPLE = 10  # steps per trace sample (= 1 time unit)
BASELINE = dict(disturb.BASELINE)
CENTROID = "circular"  # amendment A3: "local" = disturb.local_centroid for the frame


def set_cond(name, baseline=None, centroid=None):
    """Switch R, T, zoom and all step counts to condition `name` (times kept in time units)."""
    global COND, R, T, ZOOM, PHASES, HORIZON, WINDOW, SAMPLE, BASELINE, CENTROID
    COND = name
    if centroid is not None:
        CENTROID = centroid
    R, T, ZOOM = CONDS[name]
    SAMPLE = T
    if name != "base":
        PHASES = (100 * T,)
        HORIZON = 200 * T
        WINDOW = 50 * T
    if baseline is not None:
        BASELINE = dict(baseline)


def git_rev():
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "unknown"


# --- engines ----------------------------------------------------------------

def _load_ref():
    spec = importlib.util.spec_from_file_location("s001_reconstruct",
                                                  os.path.join(S001, "reconstruct.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def initial_state(size):
    cells = np.loadtxt(os.path.join(S001, "initial-cells-u8.csv"), delimiter=",", dtype=np.int64)
    cells = np.kron(cells, np.ones((ZOOM, ZOOM), dtype=np.int64))  # nearest-neighbour zoom
    A = np.zeros((size, size))
    h, w = cells.shape
    y0, x0 = (size - h) // 2, (size - w) // 2
    A[y0:y0 + h, x0:x0 + w] = cells / 255.0
    return A


@functools.lru_cache(maxsize=None)
def engine(name, size, R, T):
    """Return a step function A -> A for the S001 rule on an N x N torus."""
    if name == "ref":
        ref = _load_ref()
        kfft, _ = ref.make_kernel_fft(size, R, BETA, "poly")
        return lambda A: ref.step(A, kfft, MU, SIGMA, T, "poly")[0]
    if name == "alm":
        # Lane 2 simulator (src/alm/lenia.py, PR #6). Set ALM_SRC to a checkout's src/
        # to use it before it is merged here.
        if os.environ.get("ALM_SRC"):
            sys.path.insert(0, os.environ["ALM_SRC"])
            for m in [m for m in sys.modules if m == "alm" or m.startswith("alm.")]:
                del sys.modules[m]
        from alm.lenia import Lenia, Rule
        sim = Lenia(Rule(R=R, T=T, mu=MU, sigma=SIGMA, beta=tuple(BETA),
                         kernel="poly", growth="poly"), np.zeros((size, size)))

        def step(A):
            sim.A = A
            sim.step()
            return sim.A
        return step
    raise ValueError(name)


@functools.lru_cache(maxsize=None)
def warm(engine_name, size, t0):
    """(state at t0, centroid one time unit before t0) for the unperturbed creature."""
    step = engine(engine_name, size, R, T)
    A = initial_state(size)
    prev = None
    for t in range(1, t0 + 1):
        A = step(A)
        if t == t0 - SAMPLE:
            prev = disturb.periodic_centroid(A)
    return A, prev


def get_frame(A, prev):
    est = disturb.local_centroid if CENTROID == "local" else disturb.periodic_centroid
    return disturb.frame_from(A, prev, centroid=est)


# --- one run -------------------------------------------------------------------

def run_id(iv, s, t0, size, eng):
    tag = ("" if COND == "base" else f"-{COND}") + ("-cL" if CENTROID == "local" else "")
    return f"L4-001-{iv}-s{s:.6f}-t{t0}-N{size}-{eng}{tag}"


def aligned(A, frame):
    """Recentre A on its centroid and rotate its heading to +x (bilinear)."""
    n = A.shape[0]
    B = ndimage.shift(A, (n / 2 - frame.cy, n / 2 - frame.cx), order=1, mode="grid-wrap")
    ang = np.degrees(np.arctan2(frame.hy, frame.hx))
    return ndimage.rotate(B, ang, reshape=False, order=1, mode="grid-wrap")


def run(iv, s, t0, size=128, eng="ref", horizon=None, save=None, keep_final=False):
    horizon = HORIZON if horizon is None else horizon
    step = engine(eng, size, R, T)
    A, prev = warm(eng, size, t0)
    frame = get_frame(A, prev)
    before = A
    M0 = A.sum()
    A = disturb.INTERVENTIONS[iv](A, frame, s, R)
    during = A
    M1 = A.sum()

    n = size
    c = disturb.periodic_centroid(A)
    disp = np.zeros(2)  # cumulative wrapped centroid displacement since t0
    samples = []  # (step after t0, mass, gyradius, cum dx, cum dy)
    last10 = []
    for k in range(1, horizon + 1):
        A = step(A)
        cn = disturb.periodic_centroid(A)
        disp += (disturb.wrap(cn[0] - c[0], n), disturb.wrap(cn[1] - c[1], n))
        c = cn
        if k % SAMPLE == 0:
            m = A.sum()
            samples.append((k, m / R ** 2, disturb.gyradius(A, *c) / R, disp[0], disp[1]))
        if k == horizon - SAMPLE:
            last10 = c
    samples = np.array(samples)
    win = samples[samples[:, 0] > horizon - WINDOW]
    # five 10-time-unit blocks of net displacement inside the window
    blocks = []
    blk = 10 * T
    for b0 in range(horizon - WINDOW, horizon, blk):
        p0 = samples[samples[:, 0] == b0][0, 3:5] if b0 > 0 else np.zeros(2)
        p1 = samples[samples[:, 0] == b0 + blk][0, 3:5]
        blocks.append(np.hypot(*(p1 - p0)) / R / (blk / T))
    wspeed = float(np.mean(blocks))
    final_mass = samples[-1, 1]
    cls = {b: disturb.classify(win[:, 1], win[:, 2], wspeed, final_mass, band=b,
                               baseline=BASELINE)
           for b in (0.1, 0.2, 0.3)}

    # recovery time: first sample from which mass and gyradius stay in the +/-20% bands
    bm, bg = BASELINE["mass"], BASELINE["gyradius"]
    ok = ((samples[:, 1] >= 0.8 * bm) & (samples[:, 1] <= 1.2 * bm)
          & (samples[:, 2] >= 0.8 * bg) & (samples[:, 2] <= 1.2 * bg))
    rec_t = float("nan")
    if ok[-1]:
        bad = np.where(~ok)[0]
        first = 0 if len(bad) == 0 else bad[-1] + 1
        rec_t = samples[first, 0] / T

    row = {
        "run_id": run_id(iv, s, t0, size, eng),
        "intervention": iv, "strength": s, "t0": t0, "size": size, "engine": eng,
        "horizon": horizon, "code_rev": git_rev(),
        "mass_before": M0 / R ** 2, "mass_after_edit": M1 / R ** 2,
        "achieved_dmass_frac": (M1 - M0) / M0,
        "final_mass": final_mass,
        "win_mass_min": win[:, 1].min(), "win_mass_max": win[:, 1].max(),
        "win_gyr_min": win[:, 2].min(), "win_gyr_max": win[:, 2].max(),
        "win_mass_mean": win[:, 1].mean(), "win_gyr_mean": win[:, 2].mean(),
        "cond": COND, "R": R, "T": T,
        "win_speed": wspeed,
        "recovery_time": rec_t,
        "class": cls[0.2], "class_band10": cls[0.1], "class_band30": cls[0.3],
    }
    final_frame = None
    if final_mass >= 0.01 and len(last10):
        try:
            final_frame = disturb.frame_from(A, last10)
        except ValueError:
            final_frame = None
    if save:
        os.makedirs(save, exist_ok=True)
        np.savez_compressed(os.path.join(save, row["run_id"] + ".npz"),
                            before=before, during=during, after=A)
        with open(os.path.join(save, row["run_id"] + ".trace.csv"), "w") as f:
            f.write("step_after_t0,mass,gyradius,cum_dx,cum_dy\n")
            for r_ in samples:
                f.write("%d,%.6f,%.6f,%.3f,%.3f\n" % tuple(r_))
    if keep_final:
        return row, (aligned(A, final_frame) if final_frame else None)
    return row


FIELDS = ["run_id", "intervention", "strength", "t0", "size", "engine", "horizon", "code_rev",
          "mass_before", "mass_after_edit", "achieved_dmass_frac", "final_mass",
          "win_mass_min", "win_mass_max", "win_gyr_min", "win_gyr_max", "win_mass_mean",
          "win_gyr_mean", "win_speed", "cond", "R", "T",
          "recovery_time", "template_corr", "class", "class_band10", "class_band30"]


def write_rows(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r_ in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r_.items()})


def _job(args):
    return run(*args, keep_final=True)


def corr(a, b):
    if a is None or b is None:
        return float("nan")
    return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])


def baseline_path(out):
    return os.path.join(os.path.dirname(os.path.abspath(out)), f"baseline-{COND}.json")


def calibrate(out, size, eng):
    """Amendment A1: centre the bands on this condition's own s = 0 control."""
    r_ = run("I001", 0.0, PHASES[0], size, eng)
    b = {"mass": r_["win_mass_mean"], "gyradius": r_["win_gyr_mean"], "speed": r_["win_speed"]}
    os.makedirs(os.path.dirname(baseline_path(out)), exist_ok=True)
    with open(baseline_path(out), "w") as f:
        json.dump({"cond": COND, "R": R, "T": T, "size": size, "engine": eng,
                   "control_run": r_["run_id"], **b}, f, indent=1)
    set_cond(COND, b)


def pool(workers):
    return Pool(workers, initializer=set_cond, initargs=(COND, BASELINE, CENTROID))


def sweep(ivs, out, size, eng, workers):
    if COND != "base":
        calibrate(out, size, eng)
    jobs = [(iv, s, t0, size, eng) for iv in ivs for s in GRIDS[iv] for t0 in PHASES]
    with pool(workers) as p:
        res = p.map(_job, jobs, chunksize=1)
    controls = {(r_["intervention"], r_["t0"]): fa for r_, fa in res if r_["strength"] == 0}
    rows = []
    for r_, fa in res:
        r_["template_corr"] = corr(fa, controls.get((r_["intervention"], r_["t0"])))
        rows.append(r_)
    write_rows(out, rows)
    return rows


def _bisect_job(args):
    iv, t0, lo, hi, size, eng, ctrl = args
    rows = []
    dist = None
    if iv == "I002":
        A, prev = warm(eng, size, t0)
        f = get_frame(A, prev)
        dx, dy = disturb.offsets(A.shape, f.cx, f.cy)
        dist = np.sqrt(dx ** 2 + dy ** 2) / R
    while hi - lo > BISECT_WIDTH:
        # I002: stop once no pixel lies between the two radii (same deleted set)
        if iv == "I002" and not np.any((dist >= lo) & (dist < hi)):
            break
        mid = round((lo + hi) / 2, 6)
        r_, fa = run(iv, mid, t0, size, eng, keep_final=True)
        r_["template_corr"] = corr(fa, ctrl)
        rows.append(r_)
        if r_["class"] == "RECOVERED":
            lo = mid
        else:
            hi = mid
    return iv, t0, lo, hi, rows


def bisect(coarse, out, size, eng, workers):
    if COND != "base":
        with open(baseline_path(coarse)) as f:
            b = json.load(f)
        set_cond(COND, {k: b[k] for k in ("mass", "gyradius", "speed")})
    with open(coarse) as f:
        rows = list(csv.DictReader(f))
    jobs = []
    for iv in sorted({r_["intervention"] for r_ in rows}):
        for t0 in PHASES:
            rs = sorted((r_ for r_ in rows if r_["intervention"] == iv and int(r_["t0"]) == t0),
                        key=lambda r_: float(r_["strength"]))
            fail = [i for i, r_ in enumerate(rs) if r_["class"] != "RECOVERED"]
            if not fail or fail[0] == 0:
                continue
            i = fail[0]
            ctrl = run(iv, 0.0, t0, size, eng, keep_final=True)[1]
            jobs.append((iv, t0, float(rs[i - 1]["strength"]), float(rs[i]["strength"]),
                         size, eng, ctrl))
    with pool(workers) as p:
        res = p.map(_bisect_job, jobs, chunksize=1)
    allrows = [r_ for *_, rs in res for r_ in rs]
    write_rows(out, allrows)
    summary = os.path.splitext(out)[0] + "-brackets.csv"
    with open(summary, "w") as f:
        f.write("intervention,t0,s_ok,s_fail,s_star\n")
        for iv, t0, lo, hi, _ in res:
            f.write(f"{iv},{t0},{lo:.6f},{hi:.6f},{(lo + hi) / 2:.6f}\n")
    return res


def _check_job(args):
    iv, s, t0, size, eng, horizon = args
    return run(iv, s, t0, size, eng, horizon)


def check(brackets, out, size, eng, workers, horizon, phases):
    """Re-run both ends of every bisected bracket under another engine/size/horizon."""
    with open(brackets) as f:
        br = [b for b in csv.DictReader(f) if int(b["t0"]) in phases]
    jobs = [(b["intervention"], float(b[k]), int(b["t0"]), size, eng, horizon)
            for b in br for k in ("s_ok", "s_fail")]
    with pool(workers) as p:
        rows = p.map(_check_job, jobs, chunksize=1)
    write_rows(out, rows)
    return rows


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    one = sub.add_parser("one")
    one.add_argument("--iv", required=True, choices=disturb.INTERVENTIONS)
    one.add_argument("--s", type=float, required=True)
    one.add_argument("--t0", type=int, default=1000)
    one.add_argument("--horizon", type=int, default=None)
    one.add_argument("--save", default=None)
    for p in (one, sub.add_parser("sweep"), sub.add_parser("bisect"), sub.add_parser("check")):
        p.add_argument("--size", type=int, default=128)
        p.add_argument("--engine", default="ref", choices=["ref", "alm"])
        p.add_argument("--workers", type=int, default=os.cpu_count())
        p.add_argument("--cond", default="base", choices=CONDS)
        p.add_argument("--centroid", default="circular", choices=["circular", "local"])
    sw = sub.choices["sweep"]
    sw.add_argument("--ivs", default="I001,I002,I003,I004")
    sw.add_argument("--out", default=os.path.join(HERE, "results", "coarse.csv"))
    bi = sub.choices["bisect"]
    bi.add_argument("--coarse", default=os.path.join(HERE, "results", "coarse.csv"))
    bi.add_argument("--out", default=os.path.join(HERE, "results", "bisect.csv"))
    ck = sub.choices["check"]
    ck.add_argument("--brackets", default=os.path.join(HERE, "results", "bisect-brackets.csv"))
    ck.add_argument("--horizon", type=int, default=None)
    ck.add_argument("--phases", default=None)
    ck.add_argument("--out", required=True)
    a = ap.parse_args()
    set_cond(a.cond, centroid=a.centroid)
    if a.cmd == "one":
        r_ = run(a.iv, a.s, a.t0, a.size, a.engine, a.horizon, a.save)
        for k in FIELDS:
            if k in r_:
                print(f"{k}: {r_[k]}")
    elif a.cmd == "sweep":
        sweep(a.ivs.split(","), a.out, a.size, a.engine, a.workers)
    elif a.cmd == "check":
        check(a.brackets, a.out, a.size, a.engine, a.workers, a.horizon,
              [int(x) for x in a.phases.split(",")] if a.phases else PHASES)
    else:
        bisect(a.coarse, a.out, a.size, a.engine, a.workers)


if __name__ == "__main__":
    main()
