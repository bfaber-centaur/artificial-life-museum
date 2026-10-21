"""Replay a saved REEF state on three engine routes and measure their divergence.

    python research/experiments/REEF-numerics/replay.py \
        --manifest M.json --state A0.npy --tu 20 --out OUT_DIR [--run-id ID] [--engines alm,check_fft,check_direct]

Inputs are a float64 N x N state (.npy, or .npz with --key) and a REEF run
manifest (``research/experiments/REEF/manifest.schema.json``): ``rule`` and
``world`` are read from it, and the state's sha256 must equal
``inputs.initial_state_sha256`` when the manifest gives one (``--start-sha``
overrides this for a window that starts later than t = 0).

Each engine runs in its own fresh Python process (``_worker`` mode), so the
``alm`` route doubles as the clean-process exact-input replay. Routes:

- ``alm``           alm.lenia.Lenia (primary engine)
- ``check_fft``     alm_check.lenia.World(path="fft"): a separate implementation,
                    but the same NumPy rfft2/irfft2 arithmetic; bitwise equality
                    with alm is expected and is NOT independent arithmetic
- ``check_direct``  alm_check.lenia.World(path="direct"): real-space wrap
                    correlation (scipy.ndimage), no FFT; the only different
                    arithmetic route

Writes OUT_DIR/<engine>.npz (float64 state every tu, per-step mass),
OUT_DIR/divergence.csv (per tu, each route against alm) and
OUT_DIR/replay.json (one manifest per route, in the REEF schema shape).
Large arrays stay out of git; commit replay.json and divergence.csv.
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
REPO = HERE.parents[2]
ENGINES = ("alm", "check_fft", "check_direct")
ENGINE_NAMES = {"alm": "alm", "check_fft": "alm_check.fft", "check_direct": "alm_check.direct"}
SUFFIX = {"alm": "replay", "check_fft": "chkfft", "check_direct": "direct"}
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
SUPPORT = 0.01  # protocol §6 proposal for theta_s; only used for the support-difference column


def sha256(A: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()


def file_sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_state(path: Path, key: str | None = None) -> np.ndarray:
    path = Path(path)
    if path.suffix == ".npz":
        with np.load(path) as z:
            A = z[key] if key else z[z.files[0]]
    else:
        A = np.load(path)
    if A.dtype != np.float64:
        raise ValueError(f"{path}: replay inputs must be float64, got {A.dtype}")
    return np.ascontiguousarray(A)


def check_rule(m: dict) -> dict:
    r = m["rule"]
    if (r["kernel"], r["growth"], r.get("update", "euler+clip"), r.get("dtype", "float64")) != (
        "poly", "poly", "euler+clip", "float64"):
        raise ValueError(f"replay supports poly/poly euler+clip float64 only, got {r}")
    if m["world"].get("boundary", "periodic") != "periodic":
        raise ValueError("replay supports periodic worlds only")
    if float(r["T"]) != int(r["T"]):
        raise ValueError("T must be an integer number of steps per tu")
    return r


def git_state() -> dict:
    def g(*a):
        return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = [ln[3:] for ln in g("status", "--porcelain", "--untracked-files=no").splitlines()]
    return {"commit": g("rev-parse", "HEAD"), "dirty": bool(dirty), "dirty_paths": dirty}


def env() -> dict:
    import scipy
    return {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
            **{k: os.environ.get(k) for k in THREAD_VARS}}


# ---------------------------------------------------------------- worker (one engine, fresh process)


def make_world(engine: str, r: dict, A: np.ndarray):
    if engine == "alm":
        from alm.lenia import Lenia, Rule
        rule = Rule(R=int(r["R"]), T=int(r["T"]), mu=r["mu"], sigma=r["sigma"], beta=tuple(r["beta"]),
                    kernel=r["kernel"], growth=r["growth"])
        return Lenia(rule, A)
    import alm_check.lenia as ck
    rule = ck.Rule(R=int(r["R"]), T=int(r["T"]), mu=r["mu"], sigma=r["sigma"], b=tuple(r["beta"]),
                   core=r["kernel"], growth=r["growth"])
    return ck.World(A.copy(), rule, path=engine.split("_")[1], boundary="wrap")


def worker(a) -> None:
    m = json.loads(Path(a.manifest).read_text())
    r = check_rule(m)
    A0 = load_state(a.state, a.key)
    T = int(r["T"])
    w = make_world(a.engine, r, A0)
    states, masses = [A0.copy()], [float(A0.sum())]
    t0 = time.perf_counter()
    for _ in range(a.tu):
        for _ in range(T):
            w.step()
            masses.append(float(w.A.sum()))
        states.append(w.A.copy())
    wall = time.perf_counter() - t0
    np.savez_compressed(a.out, states=np.stack(states), mass=np.array(masses), wall_s=wall)


# ---------------------------------------------------------------- driver


def divergence(ref: np.ndarray, other: np.ndarray, R: int) -> list[dict]:
    rows = []
    for k, (x, y) in enumerate(zip(ref, other)):
        d = np.abs(x - y)
        rows.append({"tu": k, "bitwise_equal": bool(np.array_equal(x, y)), "max_abs": float(d.max()),
                     "mean_abs": float(d.mean()), "mass_diff_R2": float((y.sum() - x.sum()) / R**2),
                     "support_xor_cells": int(((x > SUPPORT) ^ (y > SUPPORT)).sum())})
    return rows


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "_worker"))
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--key", default=None, help="array name inside an .npz state")
    ap.add_argument("--tu", type=int, default=20, help="time units to replay (T steps each)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--engines", default=",".join(ENGINES))
    ap.add_argument("--engine", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--run-id", default=None, help="base run id; route suffixes are appended")
    ap.add_argument("--start-sha", default=None, help="expected sha256 of the state (overrides the manifest)")
    ap.add_argument("--allow-dirty", action="store_true", help="debug only; dirty runs are flagged")
    a = ap.parse_args(argv)
    if a.mode == "_worker":
        return worker(a)

    for k in THREAD_VARS:
        os.environ[k] = "1"
    m = json.loads(Path(a.manifest).read_text())
    r = check_rule(m)
    A0 = load_state(a.state, a.key)
    N = int(m["world"]["N"])
    if A0.shape != (N, N):
        raise ValueError(f"state shape {A0.shape} != manifest world N={N}")
    want = a.start_sha or m.get("inputs", {}).get("initial_state_sha256")
    got = sha256(A0)
    if want and want != got:
        raise ValueError(f"state sha256 {got} != expected {want}")
    gs = git_state()
    if gs["dirty"] and not a.allow_dirty:
        raise SystemExit(f"refusing to run on a dirty tree: {gs['dirty_paths']}")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    engines = [e for e in a.engines.split(",") if e]
    base = a.run_id or m.get("run_id", "REEF-NUM")
    res = {}
    for e in engines:  # sequential: at most one simulation process from this tool at a time
        cmd = [sys.executable, str(Path(__file__).resolve()), "_worker", "--engine", e, "--manifest",
               str(a.manifest), "--state", str(a.state), "--tu", str(a.tu), "--out", str(out / f"{e}.npz")]
        if a.key:
            cmd += ["--key", a.key]
        subprocess.run(cmd, check=True, env=os.environ.copy())
        with np.load(out / f"{e}.npz") as z:
            res[e] = {"states": z["states"], "mass": z["mass"], "wall_s": float(z["wall_s"])}

    R = int(r["R"])
    command = " ".join(["python", "research/experiments/REEF-numerics/replay.py", "--manifest", str(a.manifest),
                        "--state", str(a.state), *(["--key", a.key] if a.key else []), "--tu", str(a.tu),
                        "--out", str(a.out), "--engines", ",".join(engines), "--run-id", base])
    div_rows, manifests = [], []
    ref = res.get("alm")
    for e in engines:
        S = res[e]["states"]
        row = {
            "run_id": f"{base}-{SUFFIX[e]}", "kind": "check", "lane": "numerics", "commit": gs["commit"],
            "commit_dirty": gs["dirty"], "engine": ENGINE_NAMES[e], "rule": m["rule"], "world": m["world"],
            "inputs": {**m.get("inputs", {}), "initial_state_sha256": got, "state_path": str(a.state),
                       "state_file_sha256": file_sha256(Path(a.state)), "source_manifest": str(a.manifest),
                       "source_manifest_sha256": file_sha256(Path(a.manifest)), "source_run_id": m.get("run_id")},
            "horizon_tu": a.tu, "command": command, "env": env(),
            "outputs": {"states_npz": str(out / f"{e}.npz"), "states_npz_sha256": file_sha256(out / f"{e}.npz"),
                        "sha256_per_tu": [sha256(x) for x in S]},
            "final_state_sha256": sha256(S[-1]), "wall_s": res[e]["wall_s"], "status": "ok",
            "result": {"final_mass_R2": float(S[-1].sum() / R**2)},
            "notes": {"alm": "fresh-process alm replay (reproducibility)",
                      "check_fft": "independent implementation, SAME NumPy FFT arithmetic as alm: not independent arithmetic",
                      "check_direct": "real-space wrap correlation, no FFT: the only different arithmetic route"}[e],
        }
        if ref is not None and e != "alm":
            rows = divergence(ref["states"], S, R)
            for x in rows:
                div_rows.append({"route": e, **x})
            row["result"].update({"vs_alm_bitwise_final": rows[-1]["bitwise_equal"],
                                  "vs_alm_max_abs_final": rows[-1]["max_abs"],
                                  "vs_alm_max_abs_any_tu": max(x["max_abs"] for x in rows),
                                  "vs_alm_first_nonbitwise_tu": next((x["tu"] for x in rows if not x["bitwise_equal"]), None)})
        expected = m.get("final_state_sha256")
        if e == "alm" and expected and float(m.get("horizon_tu", -1)) == a.tu:
            row["result"]["matches_source_final_sha256"] = row["final_state_sha256"] == expected
        manifests.append(row)
    if div_rows:
        with open(out / "divergence.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(div_rows[0]))
            w.writeheader()
            w.writerows(div_rows)
    (out / "replay.json").write_text(json.dumps(manifests, indent=1) + "\n")
    for x in manifests:
        print(x["run_id"], x["final_state_sha256"][:16], json.dumps(x["result"]))


if __name__ == "__main__":
    main()
