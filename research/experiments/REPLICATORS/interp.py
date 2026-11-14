"""Interpolate the rule from 'division well' (213/84, lam 0) to 'division uncontrolled' (213/83, lam 1).

Same seed creature (84's cells) in every arm; body count and mass at 600 tu on 256².
usage: interp.py LAM [LAM ...]
"""
import json
import sys
from fractions import Fraction

import numpy as np

from common import count_bodies, found_entry, nd, state_hash

well, wild = found_entry("213", 84), found_entry("213", 83)


def mix(lam):
    out = []
    for p, q in zip(well["params"], wild["params"]):
        r = dict(p)
        bp = [float(Fraction(x)) for x in p["b"].split(",")]
        bq = [float(Fraction(x)) for x in q["b"].split(",")]
        r["b"] = ",".join(repr((1 - lam) * a + lam * b) for a, b in zip(bp, bq))
        r["m"] = (1 - lam) * p["m"] + lam * q["m"]
        r["s"] = (1 - lam) * p["s"] + lam * q["s"]
        out.append(r)
    return out


if __name__ == "__main__":
    N, TU = 256, 600
    for lam in map(float, sys.argv[1:]):
        _, A = nd.entry_state(well, 2, N)
        w = nd.NDLenia(mix(lam), A)
        tr = []
        for s in range(int(TU / w.dt) + 1):
            if s % 100 == 0:
                n, _ = count_bodies(w.A, thr=0.2)
                tr.append((round(s * w.dt), n, round(float(w.A.sum()), 1)))
            w.step()
        rec = dict(lam=lam, N=N, tu=TU, trace=tr, hash=state_hash(w.A))
        with open("interp.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(lam, [t[1] for t in tr[::6]], "mass", tr[-1][2], flush=True)
