"""Parameter walks from living bodies (SPECIES-scout, phase 2).

A walk starts from a live body under a rule, then moves (mu, sigma) a small step along a fixed
direction in log space. After each step it lets the body settle for STAGE_TU, classifies it with
scout.classify, and records a snapshot. It stops when the body dies, fills the world, or stays
CHAOS for two stages in a row, or after MAX_STAGES. A change of BODY subclass, component count, or
more than 25 % in mass is flagged as a transition: a candidate new form.

Usage: python walk.py run   -> walks.jsonl + walks/<start>-<dir>.npz
Starts are defined in STARTS. Everything is deterministic (no random numbers after the seed).
"""

from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from alm.lenia import Lenia, Rule
from alm.specimens import load
from scout import HERE, N, classify, sample_rule, seeds

STAGE_TU = 60
LAG_TU = 20
STEP = 0.02  # relative step in mu and/or sigma per stage
MAX_STAGES = 40
DIRS = [(math.cos(a), math.sin(a)) for a in np.arange(8) * math.pi / 4]  # (dlog mu, dlog sigma)


def crescent_state() -> np.ndarray:
    rng = np.random.default_rng([1, 56])
    rule = sample_rule("R4", rng)
    A = seeds("R4", rule, rng)[2]
    L = Lenia(rule, A)
    for _ in range(2000):
        L.step()
    return L.A


def orbium_state() -> np.ndarray:
    return load("S001").place(N)


def start(name: str) -> tuple[Rule, np.ndarray]:
    fam, src = name.split(":")
    k, g = {"pe": ("poly", "exp"), "ep": ("exp", "poly")}[fam]
    if src == "crescent":
        A, mu, sigma = crescent_state(), 0.2817, (0.0406 if fam == "pe" else 0.0395)
    elif src == "orbium":
        A, mu, sigma = orbium_state(), 0.15, 0.016
    else:
        raise ValueError(name)
    return Rule(R=13, T=10, mu=mu, sigma=sigma, kernel=k, growth=g), A


STARTS = ["pe:crescent", "ep:crescent", "pe:orbium", "ep:orbium"]


def settle(rule: Rule, A: np.ndarray) -> tuple[np.ndarray, dict]:
    L = Lenia(rule, A)
    n, lag = int(STAGE_TU * rule.T), int(LAG_TU * rule.T)
    for t in range(n):
        L.step()
        if t == n - lag - 1:
            A_lag = L.A.copy()
    return L.A, classify(A_lag, L.A, rule.R)


def walk(args) -> dict:
    sname, d = args
    rule0, A = start(sname)
    A, c0 = settle(rule0, A)
    stages = [{"i": 0, "mu": rule0.mu, "sigma": rule0.sigma, **c0}]
    snaps = [A.astype(np.float32)]
    chaos = 0
    for i in range(1, MAX_STAGES + 1):
        mu = rule0.mu * math.exp(STEP * i * DIRS[d][0])
        sigma = rule0.sigma * math.exp(STEP * i * DIRS[d][1])
        rule = Rule(R=rule0.R, T=rule0.T, mu=round(mu, 5), sigma=round(sigma, 5),
                    kernel=rule0.kernel, growth=rule0.growth)
        A, c = settle(rule, A)
        prev = stages[-1]
        trans = c["cls"] == "BODY" and prev["cls"] == "BODY" and (
            c["sub"] != prev["sub"] or c["ncomp"] != prev["ncomp"] or abs(c["mass"] / prev["mass"] - 1) > 0.25)
        stages.append({"i": i, "mu": rule.mu, "sigma": rule.sigma, "transition": bool(trans), **c})
        snaps.append(A.astype(np.float32))
        chaos = chaos + 1 if c["cls"] == "CHAOS" else 0
        if c["cls"] in ("DIED", "FILLED") or chaos >= 2:
            break
    (HERE / "walks").mkdir(exist_ok=True)
    np.savez_compressed(HERE / "walks" / f"{sname.replace(':', '-')}-{d}.npz", A=np.stack(snaps))
    return {"start": sname, "dir": d, "kernel": rule0.kernel, "growth": rule0.growth, "stages": stages}


def main(argv):
    if argv and argv[0] == "run":
        starts = argv[1].split(",") if len(argv) > 1 else STARTS
        with open(HERE / "walks.jsonl", "a") as f, ProcessPoolExecutor(4) as ex:
            for r in ex.map(walk, [(s, d) for s in starts for d in range(8)]):
                f.write(json.dumps(r) + "\n")
                f.flush()
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
