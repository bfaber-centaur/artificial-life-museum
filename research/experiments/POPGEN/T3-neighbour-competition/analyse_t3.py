"""POPGEN T3 analysis (protocol.md): PT2-1..PT2-4 -> t3_results.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
recs = [json.loads(l) for l in open(HERE / "t3.jsonl")]
R = {(r["seed"], r["cost"], r["arm"], r["kappa"]): r for r in recs}
INF = float("inf")


def outcome(r):
    return INF if r["progression"] is None else r["progression"]


def compare(c, a):
    """+1 adaptive better, -1 worse, 0 tie."""
    pa, pc = outcome(a), outcome(c)
    if pa != pc:
        return 1 if pa > pc else -1
    if pa == INF and a["eradicated"] != c["eradicated"]:
        return 1 if a["eradicated"] else -1
    return 0


res = {"pairs": []}
for cost in (0.3,):
    better = worse = tie = 0; const_prog = const_prog_res = 0
    for seed in (1, 2, 3, 4):
        for k in (0.3, 0.4):
            c, a = R.get((seed, cost, "constant", k)), R.get((seed, cost, "adaptive", k))
            if not (c and a):
                continue
            v = compare(c, a)
            better += v == 1; worse += v == -1; tie += v == 0
            if c["progression"] is not None:
                const_prog += 1
                const_prog_res += (c["resistant_at_progression"] or 0) > 0.5
            n = R.get((seed, cost, "none", None))
            res["pairs"].append(dict(seed=seed, cost=cost, kappa=k, verdict=v,
                                     constant=dict(prog=c["progression"], res=c["resistant_at_progression"], erad=c["eradicated"], end=c["trace"][-1]),
                                     adaptive=dict(prog=a["progression"], res=a["resistant_at_progression"], erad=a["eradicated"], drug=a["drug_time"], end=a["trace"][-1]),
                                     none_end=n["trace"][-1] if n else None))
    res[f"c{cost}"] = dict(adaptive_better=better, worse=worse, tie=tie, constant_progressed=const_prog, constant_progressed_mostly_resistant=const_prog_res)
res["PT1"] = dict(pass_=res["c0.3"]["constant_progressed_mostly_resistant"] >= 4, **res["c0.3"])
res["PT2"] = dict(pass_=res["c0.3"]["adaptive_better"] >= 5, **res["c0.3"])
for p in res["pairs"]:
    print(p["cost"], p["seed"], p["kappa"], p["verdict"], "C", p["constant"]["prog"], p["constant"]["res"], p["constant"]["erad"], p["constant"]["end"][1:4],
          "| A", p["adaptive"]["prog"], p["adaptive"]["res"], p["adaptive"]["erad"], p["adaptive"]["drug"], p["adaptive"]["end"][1:4])
for k in ("PT1", "PT2"):
    print(k, res[k])
json.dump(res, open(HERE / "t3_results.json", "w"), indent=1)
rows = [r for r in recs if r["arm"] == "none"]
res["PT3-3"] = dict(seeds=[(r["seed"], r["clone_share"], r["trace"][-1][3]) for r in rows],
                    pass_=sum(r["trace"][-1][3] < r["clone_share"] for r in rows) >= 3)
res["PT3-1"], res["PT3-2"] = res.pop("PT1"), res.pop("PT2")
print("PT3-3", res["PT3-3"])
json.dump(res, open(HERE / "t3_results.json", "w"), indent=1)
