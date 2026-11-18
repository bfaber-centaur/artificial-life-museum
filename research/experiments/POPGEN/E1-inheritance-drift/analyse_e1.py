"""POPGEN E1 analysis (protocol.md): P1a-P1f -> e1_results.json."""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

HERE = Path(__file__).resolve().parent
TAU, K = 183.0, 74.0
recs = [json.loads(l) for l in open(HERE / "e1.jsonl")]
by = {}
for r in recs:
    by.setdefault(r["arm"], []).append(r)
res = {}


def fin(r, col):
    return r["trace"][-1][col]


# E1a
a = {arm: by.get(arm, []) for arm in ("blend+", "part+", "part0")}
summ = {}
for arm, rs in a.items():
    rs = sorted(rs, key=lambda r: (r["world_seed"], r["rng_seed"]))
    summ[arm] = dict(n=len(rs), start=[r["trace"][0][1] for r in rs], final_share=[fin(r, 1) for r in rs],
                     final_majority=[fin(r, 2) for r in rs],
                     grew=sum(fin(r, 1) > r["trace"][0][1] for r in rs),
                     lost=sum(fin(r, 2) == 0 for r in rs),
                     median_final=float(np.median([fin(r, 1) for r in rs])) if rs else None,
                     over_half=sum(fin(r, 2) > 0.5 for r in rs))
res["E1a"] = summ
if all(summ[k]["n"] == 12 for k in summ):
    res["P1a"] = dict(dissolved=sum(m < 0.01 for m in summ["blend+"]["final_majority"]), pass_=sum(m < 0.01 for m in summ["blend+"]["final_majority"]) >= 10)
    res["P1b"] = dict(grew_part_plus=summ["part+"]["grew"], grew_part0=summ["part0"]["grew"],
                      median_part_plus=summ["part+"]["median_final"], median_part0=summ["part0"]["median_final"],
                      pass_=summ["part+"]["grew"] > summ["part0"]["grew"] and summ["part+"]["median_final"] > summ["part0"]["median_final"])
    res["P1c"] = dict(part_plus_over_half=summ["part+"]["over_half"], blend_plus_over_half=summ["blend+"]["over_half"],
                      pass_=summ["part+"]["over_half"] >= 1 and summ["blend+"]["over_half"] == 0)


# E1b
def F_curve(rs):
    T = np.array([row[0] for row in rs[0]["trace"]], float)
    P = np.array([[row[1] for row in r["trace"]] for r in rs])
    p0 = P[:, :1]
    return T, ((P - p0) ** 2 / (p0 * (1 - p0))).mean(0), P[:, -1] - P[:, 0]


def fit_ne(T, F):
    m = T > 0
    f = lambda t, ne: 1 - np.exp(-t / (ne * TAU))
    (ne,), _ = curve_fit(f, T[m], F[m], p0=[50.0], bounds=(0.5, 1e5))
    return float(ne)


rng = np.random.default_rng(0)
for p0 in ("0.5", "0.1"):
    rs = by.get(f"drift{p0}", [])
    if len(rs) < 2:
        continue
    T, F, d = F_curve(rs)
    ne = fit_ne(T, F)
    boots = []
    for _ in range(2000):
        idx = rng.integers(len(rs), size=len(rs))
        Tb, Fb, _ = F_curve([rs[i] for i in idx])
        boots.append(fit_ne(Tb, Fb))
    se = float(d.std(ddof=1) / np.sqrt(len(d)))
    res[f"E1b_p{p0}"] = dict(n=len(rs), Ne=round(ne, 1), CI95=[round(float(np.percentile(boots, q)), 1) for q in (2.5, 97.5)],
                             mean_dp=round(float(d.mean()), 4), se_dp=round(se, 4), F_final=round(float(F[-1]), 4),
                             P1d_pass=bool(abs(d.mean()) <= 2 * se), P1e_pass=bool(0.2 * K <= ne <= 2 * K))
if "E1b_p0.5" in res and "E1b_p0.1" in res:
    a_, b_ = res["E1b_p0.5"], res["E1b_p0.1"]
    ratio = max(a_["Ne"], b_["Ne"]) / min(a_["Ne"], b_["Ne"])
    overlap = not (a_["CI95"][1] < b_["CI95"][0] or b_["CI95"][1] < a_["CI95"][0])
    res["P1f"] = dict(ratio=round(ratio, 2), CIs_overlap=overlap, verdict="pass" if ratio <= 1.5 else ("inconclusive" if overlap else "fail"))
print(json.dumps({k: v for k, v in res.items() if k != "E1a"}, indent=1))
for arm, s in res["E1a"].items():
    print(arm, {k: v for k, v in s.items() if k not in ("start", "final_share", "final_majority")})
json.dump(res, open(HERE / "e1_results.json", "w"), indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
