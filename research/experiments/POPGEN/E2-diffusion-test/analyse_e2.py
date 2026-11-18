"""POPGEN E2 analysis (protocol.md) -> e2_results.json."""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import binom, spearmanr

HERE = Path(__file__).resolve().parent
E1 = [json.loads(l) for l in open(HERE.parent / "E1-inheritance-drift" / "e1.jsonl")]
E2 = [json.loads(l) for l in open(HERE / "e2.jsonl")]
T_END, THR = 3000.0, 0.05
rng = np.random.default_rng(0)


def fitD(rs):
    T = np.array([x[0] for x in rs[0]["trace"]], float)
    P = np.array([[x[1] for x in r["trace"]] for r in rs]); p0 = P[:, :1]
    F = ((P - p0) ** 2 / (p0 * (1 - p0))).mean(0)
    (D,), _ = curve_fit(lambda t, D: 1 - np.exp(-t / D), T[1:], F[1:], p0=[5e4], bounds=(1, 1e9))
    return float(D)


sd = [r for r in E1 if r["arm"].startswith("sdrift")]
D = fitD(sd)
Db = [fitD([sd[i] for i in rng.integers(len(sd), size=len(sd))]) for _ in range(2000)]
res = dict(D=round(D, 1), D_CI95=[round(float(np.percentile(Db, q)), 1) for q in (2.5, 97.5)])

# Phase A
s_t = {}
for d in (0.02, 0.05, 0.1, 0.2):
    sl = []
    for r in E2:
        if r["kind"] == "h" and r["delta"] == d:
            t = np.array([x[0] for x in r["trace"]], float); p = np.clip([x[1] for x in r["trace"]], 1e-4, 1 - 1e-4)
            m = t >= 100
            sl.append(np.polyfit(t[m], np.log(p[m] / (1 - p[m])), 1)[0])
    if sl:
        s_t[d] = dict(n=len(sl), mean=float(np.mean(sl)), sd=float(np.std(sl, ddof=1)) if len(sl) > 1 else None, each=[float(x) for x in sl])
s_t[0.0] = dict(n=0, mean=0.0)
res["s_t"] = {str(k): v for k, v in s_t.items()}
vals = [s_t[d]["mean"] for d in (0.02, 0.05, 0.1, 0.2) if d in s_t]
res["P2a"] = dict(pass_=len(vals) == 4 and all(a < b for a, b in zip(vals, vals[1:])))


def simulate(p0, s, D, n=20000, T=T_END, dt=1.0, seed=1):
    g = np.random.default_rng(seed)
    p = np.full(n, p0)
    for _ in range(int(T / dt)):
        a = (p > 0) & (p < 1)
        pa = p[a]
        p[a] = pa + s * pa * (1 - pa) * dt + np.sqrt(np.maximum(pa * (1 - pa), 0) / D * dt) * g.standard_normal(pa.size)
        p = np.clip(p, 0, 1)
    return float((p >= THR).mean())


# Phase B (+ E1c s+ as delta 0.2, s0 as delta 0)
cond = {}
for d in (0.0, 0.02, 0.05, 0.1, 0.2):
    if d in (0.0, 0.2):
        rows = [r for r in E1 if r["arm"] == ("s0" if d == 0 else "s+")]
    else:
        rows = [r for r in E2 if r["kind"] == "m" and r["delta"] == d]
    if not rows or d not in s_t:
        continue
    p0 = float(np.mean([r["trace"][0][1] for r in rows]))
    obs = sum(r["trace"][-1][1] >= THR for r in rows)
    n = len(rows)
    pi = simulate(p0, s_t[d]["mean"], D)
    pi_lo, pi_hi = simulate(p0, s_t[d]["mean"], res["D_CI95"][0]), simulate(p0, s_t[d]["mean"], res["D_CI95"][1])
    lo, hi = binom.ppf(0.025, n, pi), binom.ppf(0.975, n, pi)
    cond[str(d)] = dict(n=n, p0=round(p0, 4), s_t=s_t[d]["mean"], observed=int(obs), predicted_pi=round(pi, 3),
                        pi_range_over_D_CI=[round(pi_lo, 3), round(pi_hi, 3)], interval95=[int(lo), int(hi)], inside=bool(lo <= obs <= hi))
res["conditions"] = cond
k = sum(c["inside"] for c in cond.values())
res["P2b"] = dict(inside=k, of=len(cond), verdict="pass" if k == 5 else ("partial" if k == 4 else "fail"))
ds = sorted(cond, key=float)
rho = spearmanr([float(d) for d in ds], [cond[d]["observed"] / cond[d]["n"] for d in ds]).correlation if len(ds) > 2 else None
res["P2c"] = dict(rho=rho, pass_=bool(rho is not None and rho > 0))
print(json.dumps(res, indent=1))
json.dump(res, open(HERE / "e2_results.json", "w"), indent=1)
