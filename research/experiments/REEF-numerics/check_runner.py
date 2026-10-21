"""§9 check runner: an encounter E and its matched controls G-alone, S-alone, stepped in lockstep
on one engine route, scored live with the behavior lane's recorder (reef/behavior score.py).

    python research/experiments/REEF-numerics/check_runner.py --run-id REEF-P2-E-direct \
        --states CKPT.npz --keys E_00030 G_00030 S_00030 --t0 3 --tu-end 25 \
        --engine check_direct --R 13 --T 10 --behavior-dir PATH/REEF-behavior --out OUT

Inputs are three float64 states (from an .npz with --keys, or three .npy files with --npy) and
the rule (poly/poly, mu .155, sigma .020, beta [1], Euler + clip, float64, periodic). All three
worlds use the same engine: ``alm`` (alm.lenia), ``check_fft`` (alm_check FFT: separate code,
same NumPy FFT arithmetic as alm) or ``check_direct`` (alm_check real-space wrap correlation:
the only different arithmetic route).

Per step it records masses, the superposition residual max|E - (G + S)|, E body count from the
recorder, and r95: the 95th-percentile minimum-image distance (in R) of E support cells
(A > 0.01) from the S-alone control's centroid. Ignition (lead, D-017) = first step with
E mass >= 2 x (G mass + S mass) and >= 5 E bodies. Front speed = least-squares slope of r95 over
a declared window (see ``front``).

Writes OUT/summary.json (score, ignition, fronts, hashes), OUT/series.csv (per step) and
OUT/checkpoints.npz (float64 E/G/S every tu; not committed).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay import file_sha256, git_state, make_world, sha256  # noqa: E402

THETA_S = 0.01


def periodic_centroid(A):
    out = []
    for ax in (0, 1):
        n = A.shape[ax]
        w = A.sum(axis=1 - ax)
        th = 2 * np.pi * np.arange(n) / n
        out.append((np.arctan2((w * np.sin(th)).sum(), (w * np.cos(th)).sum()) % (2 * np.pi)) * n / (2 * np.pi))
    return np.array(out)


def r95(A, c, R):
    idx = np.argwhere(A > THETA_S)
    if len(idx) == 0:
        return 0.0
    N = np.array(A.shape)
    d = (idx - c + N / 2) % N - N / 2
    return float(np.percentile(np.hypot(d[:, 0], d[:, 1]), 95) / R)


def front(t, r, t_from, r_max):
    """Slope of r95 (R/tu) from t_from until r95 first reaches r_max (before the colony nears its own images)."""
    t, r = np.asarray(t), np.asarray(r)
    stop = np.argmax(r >= r_max) if (r >= r_max).any() else len(r)
    m = (t >= t_from) & (np.arange(len(t)) < stop)
    if m.sum() < 10:
        return {"speed_R_per_tu": None, "fit_tu": None}
    p = np.polyfit(t[m], r[m], 1)
    return {"speed_R_per_tu": float(p[0]), "fit_tu": [float(t[m][0]), float(t[m][-1])],
            "rms_resid_R": float(np.sqrt(np.mean((np.polyval(p, t[m]) - r[m]) ** 2)))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--states", help=".npz holding the three states")
    ap.add_argument("--keys", nargs=3, metavar=("E", "G", "S"))
    ap.add_argument("--npy", nargs=3, metavar=("E", "G", "S"))
    ap.add_argument("--expect-sha", nargs=3, metavar=("E", "G", "S"), default=None)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--tu-end", type=float, required=True)
    ap.add_argument("--engine", choices=("alm", "check_fft", "check_direct"), default="alm")
    ap.add_argument("--R", type=int, default=13)
    ap.add_argument("--T", type=int, default=10)
    ap.add_argument("--horizon", type=float, default=50.0, help="scorer horizon in tu (absolute time)")
    ap.add_argument("--behavior-dir", required=True)
    ap.add_argument("--source", default="", help="free text: where the inputs came from")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    sys.path.insert(0, a.behavior_dir)
    from score import EncounterRecorder, ScoreParams, score_trace  # noqa: E402

    if a.npy:
        A0 = [np.load(p) for p in a.npy]
        src_files = {k: {"path": p, "sha256": file_sha256(Path(p))} for k, p in zip("EGS", a.npy)}
    else:
        z = np.load(a.states)
        A0 = [z[k] for k in a.keys]
        src_files = {"npz": {"path": a.states, "sha256": file_sha256(Path(a.states)), "keys": a.keys}}
    A0 = [np.ascontiguousarray(x, dtype=np.float64) for x in A0]
    shas = [sha256(x) for x in A0]
    if a.expect_sha and list(a.expect_sha) != shas:
        raise SystemExit(f"input sha mismatch: {shas}")
    gs = git_state()
    if gs["dirty"]:
        raise SystemExit(f"refusing to run on a dirty tree: {gs['dirty_paths']}")
    N, R, T = A0[0].shape[0], a.R, a.T
    rule = {"kernel": "poly", "growth": "poly", "beta": [1.0], "mu": 0.155, "sigma": 0.020, "R": R, "T": T,
            "update": "euler+clip", "dtype": "float64"}
    worlds = [make_world(a.engine, rule, x) for x in A0]
    p = ScoreParams(N=N, R=float(R), T=float(T), horizon=a.horizon)
    t0_wall = time.time()
    rec = EncounterRecorder(*A0, p, a.t0, float(np.abs(A0[0] - (A0[1] + A0[2])).max()))
    cS = periodic_centroid(A0[2])
    k0, k1 = round(a.t0 * T), round(a.tu_end * T)
    series, ckpt = [], {}

    def observe(k, row):
        E, G, S = (w.A for w in worlds)
        mE, mG, mS = (x.sum() / R**2 for x in (E, G, S))
        series.append({"step": k, "t": k / T, "mass_E": mE, "mass_G": mG, "mass_S": mS,
                       "residual_max": float(np.abs(E - (G + S)).max()), "n_bodies_E": row["E"]["n_bodies"],
                       "n_components_E": row["E"]["n_components"], "fill": row["fill"], "r95_R": r95(E, cS, R),
                       "S_bitwise_initial": bool(np.array_equal(S, A0[2]))})
        if k % T == 0 or k == k1:
            for n_, x in zip("EGS", (E, G, S)):
                ckpt[f"{n_}_{k:05d}"] = x.copy()

    observe(k0, rec.rows[-1])
    for k in range(k0 + 1, k1 + 1):
        for w in worlds:
            w.step()
        E, G, S = (w.A for w in worlds)
        row = rec.update(E, G, S, k / T, float(np.abs(E - (G + S)).max()))
        observe(k, row)
    wall = time.time() - t0_wall

    res = score_trace(rec.rows, p)
    ign = next((s for s in series if s["mass_E"] >= 2 * (s["mass_G"] + s["mass_S"]) and s["n_bodies_E"] >= 5), None)
    t = [s["t"] for s in series]
    rr = [s["r95_R"] for s in series]
    half = N / 2 / R

    def at(tt):
        s = next((s for s in series if abs(s["t"] - tt) < 1e-9), None)
        return None if s is None else {"mass_E": s["mass_E"], "n_bodies_E": s["n_bodies_E"], "r95_R": s["r95_R"]}

    fronts = {}
    if ign:
        fronts["from_ignition_to_r95_0.7_half"] = front(t, rr, ign["t"], 0.7 * half)
        for w0 in np.arange(np.ceil(ign["t"]), t[-1] - 4.99, 5.0):  # sliding 5-tu slopes, for the constancy question
            m = (np.array(t) >= w0) & (np.array(t) <= w0 + 5)
            fronts.setdefault("sliding_5tu", []).append(
                {"tu": [float(w0), float(w0 + 5)], "speed_R_per_tu": float(np.polyfit(np.array(t)[m], np.array(rr)[m], 1)[0]),
                 "r95_end_R": float(np.array(rr)[m][-1])})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "checkpoints.npz", **ckpt)
    with open(out / "series.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(series[0]))
        wr.writeheader()
        wr.writerows(series)
    score = {k: res.get(k) for k in ("class", "partial_class", "flags", "t_int", "t_kr", "t_c", "t_cen")}
    score["observables"] = {k: v for k, v in res.get("observables", {}).items() if not isinstance(v, (list, dict))}
    summary = {
        "run_id": a.run_id, "kind": "check", "lane": "numerics", "commit": gs["commit"],
        "engine": {"alm": "alm", "check_fft": "alm_check.fft", "check_direct": "alm_check.direct"}[a.engine],
        "arithmetic_note": "check_direct is the only different arithmetic route; alm_check FFT shares NumPy FFT arithmetic with alm",
        "rule": rule, "world": {"N": N, "boundary": "periodic"}, "t0_tu": a.t0, "t_end_tu": a.tu_end,
        "inputs": {"source": a.source, "files": src_files, "initial_state_sha256": dict(zip("EGS", shas))},
        "behavior_scorer": {"dir": a.behavior_dir, "params": vars(p) if hasattr(p, "__dict__") else str(p)},
        "command": "python research/experiments/REEF-numerics/check_runner.py " + " ".join(sys.argv[1:]),
        "env": {"python": sys.version.split()[0], "numpy": np.__version__,
                **{v: os.environ.get(v) for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}},
        "final_state_sha256": {n_: sha256(w.A) for n_, w in zip("EGS", worlds)},
        "S_bitwise_constant": all(s["S_bitwise_initial"] for s in series),
        "score": score,
        "ignition": None if ign is None else {"t": ign["t"], "mass_E": ign["mass_E"], "n_bodies_E": ign["n_bodies_E"]},
        "front": fronts, "at_t20": at(20.0), "at_t25": at(25.0), "at_t50": at(50.0), "at_end": at(series[-1]["t"]),
        "outputs": {"series.csv": file_sha256(out / "series.csv"), "checkpoints.npz": file_sha256(out / "checkpoints.npz")},
        "wall_s": wall, "status": "ok",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=float) + "\n")
    print(json.dumps({k: summary[k] for k in ("run_id", "final_state_sha256", "ignition", "at_t20", "at_t25")}, default=float))
    print(json.dumps(score, default=float)[:600])
    print(json.dumps(fronts, default=float)[:800])


if __name__ == "__main__":
    main()
