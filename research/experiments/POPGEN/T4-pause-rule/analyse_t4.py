"""POPGEN T4 analysis (protocol.md) -> t4_results.json; constant arms from T3."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
t3 = {(r["seed"], r["kappa"]): r for r in map(json.loads, open(HERE.parent / "T3-neighbour-competition" / "t3.jsonl")) if r["arm"] == "constant"}
t4 = {(r["seed"], r["kappa"]): r for r in map(json.loads, open(HERE / "t4.jsonl"))}
INF = float("inf")
rows, better, paused, lower_res = [], 0, 0, 0
for key, a in sorted(t4.items()):
    c = t3[key]
    pa = INF if a["progression"] is None else a["progression"]; pc = INF if c["progression"] is None else c["progression"]
    v = 1 if pa > pc else (-1 if pa < pc else (0 if a["eradicated"] == c["eradicated"] else (1 if a["eradicated"] else -1)))
    ra = a["resistant_at_progression"] if a["progression"] is not None else a["trace"][-1][3]
    rc = c["resistant_at_progression"] if c["progression"] is not None else c["trace"][-1][3]
    better += v == 1; paused += a["drug_time"] < 0.8 * a["tu"]; lower_res += ra < rc
    rows.append(dict(seed=key[0], kappa=key[1], verdict=v, adaptive_prog=a["progression"], constant_prog=c["progression"],
                     adaptive_drug=a["drug_time"], res_adaptive=ra, res_constant=rc))
    print(rows[-1])
res = dict(rows=rows, PT4_1=dict(paused=paused, pass_=paused >= 6), PT4_2=dict(better=better, n=len(rows), pass_=better >= 5),
           PT4_3=dict(lower_res=lower_res, pass_=lower_res >= 5))
print({k: v for k, v in res.items() if k != "rows"})
json.dump(res, open(HERE / "t4_results.json", "w"), indent=1)
