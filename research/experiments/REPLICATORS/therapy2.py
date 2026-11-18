"""Therapy toy, round 3: drug holidays, adaptive thresholds and a second drug (C125+).

Same tumour, drug and cost of resistance as therapy.py (grow(), crowding_cost(), B0, mutation
seed 10 000 + seed during treatment), but the schedule is a policy that reads the tumour each
step and decides which drugs are on:

  drug A (as therapy.py)   A <- A (1 - dt * kA * g)         hits fast, drug-sensitive matter
  drug B (new)             A <- A (1 - dt * kB * (1 - g))   hits slow, A-resistant matter

Experiments (one record per run in OUT, default therapy2.jsonl):
  holiday     drug A on until T_OFF, then off: does a resistant remnant regrow (relapse)?
  threshold   adaptive drug A, off at LOW * B0, on again at 1.0 B0, for several LOW
  bind        drug A only, drug B only, both together, fixed alternation, and "steering"
              (A until the tumour is mostly resistant, then B until it is mostly sensitive)

  python therapy2.py EXP SEED COST [TU] [OUT]
"""
import json
import sys
import time

import numpy as np

import therapy as T
from common import state_hash
from genome import GenomeLenia

KA = KB = 0.3
T_OFF = 2000.0
LOWS = (0.3, 0.5, 0.7, 0.9)
PERIOD = 100.0      # alternation: A for PERIOD tu, then B for PERIOD tu
STEER_HI, STEER_LO = 0.5, 0.2   # steering: switch to B above this resistant share, back to A below


def run(A, g, seed, B0, TU, policy, cost, kA=KA, kB=KB, every=5.0, on_step=None):
    w = GenomeLenia(A, g, mut_amp=T.MUT, seed=10_000 + seed)
    st = {}
    tr, prog, dose = [], None, {"A": 0.0, "B": 0.0}
    k = int(round(every / w.dt))
    for s in range(int(round(TU / w.dt)) + 1):
        t = s * w.dt
        m = float(w.A.sum())
        res = float(w.A[w.g < T.RESIST].sum() / max(m, 1e-9))
        a, b = policy(t, m / B0, res, st)
        if prog is None and m > T.PROG * B0:
            prog = round(t, 1)
        if on_step is not None:
            on_step(s, w, a, b)
        if s % k == 0:
            tr.append([round(t, 1), round(m / B0, 4), round(float((w.A * w.g).sum() / max(m, 1e-9)), 4),
                       round(res, 4), int(a), int(b)])
        if t >= TU:
            break
        w.step()
        T.crowding_cost(w, cost)
        if a:
            w.A *= 1 - w.dt * kA * w.g
            dose["A"] += w.dt
        if b:
            w.A *= 1 - w.dt * kB * (1 - w.g)
            dose["B"] += w.dt
    # relapse time, only meaningful for the holiday policy (drug stopped at T_OFF)
    regrow = next((x[0] for x in tr if x[0] > T_OFF and x[1] >= 1.0), None) if policy is holiday else None
    return dict(trace=tr, progression=prog, drug_A=round(dose["A"], 1), drug_B=round(dose["B"], 1),
                final_sha=state_hash(np.stack([w.A, w.g])), back_to_B0=regrow)


def constant(t, b, r, st):
    return True, False


def holiday(t, b, r, st):
    return t < T_OFF, False


def adaptive(low):
    def p(t, b, r, st):
        on = st.get("on", True)
        if on and b <= low:
            on = False
        elif not on and b >= 1.0:
            on = True
        st["on"] = on
        return on, False
    return p


def only_b(t, b, r, st):
    return False, True


def both(t, b, r, st):
    return True, True


def alternate(t, b, r, st):
    return int(t // PERIOD) % 2 == 0, int(t // PERIOD) % 2 == 1


def steer(t, b, r, st):
    useb = st.get("b", False)
    if not useb and r > STEER_HI:
        useb = True
    elif useb and r < STEER_LO:
        useb = False
    st["b"] = useb
    return not useb, useb


EXPS = {
    "holiday": lambda: [("holiday", holiday)],
    "threshold": lambda: [(f"adaptive{lo}", adaptive(lo)) for lo in LOWS],
    "bind": lambda: [("A", constant), ("B", only_b), ("A+B", both), ("alternate", alternate), ("steer", steer)],
}


def main(exp, seed, cost, TU, out):
    t0 = time.time()
    A, g, t_grow, B0 = T.grow(seed, 128, cost)
    for name, pol in EXPS[exp]():
        r = run(A, g, seed, B0, TU, pol, cost)
        rec = dict(exp=exp, arm=name, seed=seed, cost=cost, N=128, tu=TU, kA=KA, kB=KB, B0=round(B0, 1),
                   t_start=t_grow, columns=["t", "burden/B0", "mean_g", "resistant_share", "A_on", "B_on"], **r)
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        e = r["trace"][-1]
        print(exp, seed, cost, name, "prog", r["progression"], "A", r["drug_A"], "B", r["drug_B"],
              "back", r["back_to_B0"], "end", e[1:4], f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], int(a[1]), float(a[2]), float(a[3]) if len(a) > 3 else 4000.0,
         a[4] if len(a) > 4 else "therapy2.jsonl")
