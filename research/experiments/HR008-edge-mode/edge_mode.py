#!/usr/bin/env python3
"""HR-008: is "a small unstable mode" (L5-002 claim 2) supported, or narrative?

A single unstable edge state predicts two things that can be measured independently:
  (a) the collapse time diverges as  t_death ~ -(1/lambda) ln(s - s*),
  (b) two runs straddling s* separate as  |A_die - A_surv| ~ exp(lambda t)  in the lingering phase,
with the SAME lambda. And if every disturbance funnels into the SAME edge state, lambda and the
lingering state itself are the same for I001, I003 and I004.

For each intervention at t0 = 1000 (N = 128, ref engine, Lane 4's frame and edits) this script
bisects s* to ~1e-12 (died = mass < 0.01 by step 1000 after the edit), runs s* + 10^-k for
k = 3..11 to get (a), steps the final straddling pair to get (b), and saves the aligned
lingering state. Exploratory; nothing here was preregistered.

Usage (repo root; L4 = a checkout of claude/night0-morphometrics-1103d7 or later, which
carries Lane 4's run.py and alm.disturb):
    PYTHONPATH=$L4/src .venv/bin/python research/experiments/HR008-edge-mode/edge_mode.py $L4
    then analyze_edge.py > edge_mode.txt and compare_states.py $L4 > compare_states.txt
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

L4 = sys.argv[1]
sys.path.insert(0, os.path.join(L4, "research", "experiments", "L4-001-disturbance-battery"))
import run as L4run  # noqa: E402
from alm import disturb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
N, T0, H = 128, 1000, 1000
BRACKETS = {"I001": (0.1, 0.103125), "I003": (0.30625, 0.309375), "I004": (0.08125, 0.084375)}


def start(iv, s):
    A, prev = L4run.warm("ref", N, T0)
    frame = L4run.get_frame(A, prev)
    return disturb.INTERVENTIONS[iv](A, frame, s, 13)


def trajectory(iv, s, steps=H, keep=False):
    step = L4run.engine("ref", N, 13, 10)
    A = start(iv, s)
    masses, states = [], []
    for k in range(1, steps + 1):
        A = step(A)
        masses.append(A.sum() / 169)
        if keep:
            states.append(A)
    m = np.array(masses)
    death = int(np.argmax(m < 0.01)) + 1 if (m < 0.01).any() else None
    return death, m, states


def bisect(iv):
    lo, hi = BRACKETS[iv]
    assert trajectory(iv, lo)[0] is None and trajectory(iv, hi)[0] is not None
    while hi - lo > 2e-12:
        mid = 0.5 * (lo + hi)
        if trajectory(iv, mid)[0] is None:
            lo = mid
        else:
            hi = mid
    return lo, hi


def aligned_state(A, prev_c):
    f = disturb.frame_from(A, prev_c)
    return L4run.aligned(A, f)


def study(iv):
    lo, hi = bisect(iv)
    sstar = 0.5 * (lo + hi)
    scaling = []
    for k in range(3, 12):
        d, _, _ = trajectory(iv, sstar + 10.0 ** -k)
        scaling.append((10.0 ** -k, d))
    _, m_lo, S_lo = trajectory(iv, lo, steps=400, keep=True)
    d_hi, m_hi, S_hi = trajectory(iv, hi, steps=400, keep=True)
    diff = [float(np.linalg.norm(a - b)) for a, b in zip(S_lo, S_hi)]
    # lingering state: the dying run at the step where the pair difference first reaches 1e-3
    k = next(i for i, d in enumerate(diff) if d > 1e-3)
    edge = aligned_state(S_hi[k], disturb.periodic_centroid(S_hi[k - 10]))
    np.save(os.path.join(HERE, f"edge-{iv}.npy"), edge)
    return dict(iv=iv, s_lo=lo, s_hi=hi, s_star=sstar, scaling=scaling, death_hi=d_hi,
                diff=diff, mass_lo=m_lo.tolist(), mass_hi=m_hi.tolist(), linger_step=k + 1)


if __name__ == "__main__":
    with Pool(3) as p:
        res = p.map(study, list(BRACKETS))
    with open(os.path.join(HERE, "edge_mode.json"), "w") as f:
        json.dump(res, f)
    print("done")
