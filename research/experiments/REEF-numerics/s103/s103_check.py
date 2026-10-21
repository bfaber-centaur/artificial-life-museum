"""S103 fixed-point check on both arithmetic routes, with growth margins.

A deterministic map with A1 == A0 bitwise is fixed for every later step on that
route, so one exact step plus the margins below is the whole argument; the long
alm.run traces in traces/ repeat the original 10k/20k-step evidence.

    python research/experiments/REEF-numerics/s103/s103_check.py > s103_check.json
"""
import hashlib, json
import numpy as np
from alm.lenia import Lenia, Rule
from alm.specimens import load
import alm_check.lenia as ck

sha = lambda A: hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()
rule = Rule(R=13, T=10, mu=.155, sigma=.020)
cr = ck.Rule(R=13, T=10, mu=.155, sigma=.020)
assert load("S103").rule == rule
out = {}
for n in (128, 256):
    A0 = load("S103").place(n)
    full, empty = A0 == 1.0, A0 == 0.0
    assert (full | empty).all()
    row = {"initial_sha256": sha(A0)}
    for route in ("alm_fft", "check_fft", "check_direct"):
        if route == "alm_fft":
            w = Lenia(rule, A0); G = w.growth_field()
        else:
            w = ck.World(A0.copy(), cr, path=route.split("_")[1]); G = w.field()
        for k in range(20):
            w.step()
        row[route] = dict(min_G_full=float(G[full].min()), max_G_empty=float(G[empty].max()),
                          steps=20, final_sha256=sha(w.A), bitwise_fixed=bool(np.array_equal(w.A, A0)))
    out[f"N{n}"] = row
print(json.dumps(out, indent=1))
