"""Print every number quoted in REPLICATORS.md and claims C072-C075 from the committed records."""
import json
import statistics
from collections import defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
EX = H.parents[1] / "gallery" / "exhibits"

print("== scout (scout_N256.jsonl): catalogue entries named as dividers, 600 tu, 256^2")
for l in open(H / "scout_N256.jsonl"):
    r = json.loads(l)
    print(f"  {r['stem']}#{r['idx']:<3} {r['name']!r:45} pieces(thr .1) start {r['trace'][0][1]} end {r['trace'][-1][1]}  mass end {r['trace'][-1][2]}")

print("== C072 family tree (G029 tree.json)")
t = json.loads((EX / "G029-family-tree" / "tree.json").read_text())
print(f"  {t['divisions']} divisions, {t['vanished']} disappearances, {t['max_gen']} generations, {t['alive_end']} cells at the end "
      f"({t['frames'] - 1} tu, N {t['N']}); flicker births dropped {t['flicker_births_dropped']}")
print("  cells every 50 tu:", t["alive_every_50"])

print("== C073 growth (growth.jsonl): t50 by lam, seeds 0-2 at dt 0.1; dt 0.05 seed 0")
g = defaultdict(dict)
for l in open(H / "growth.jsonl"):
    r = json.loads(l)
    g[r["lam"]][(r["seed"], r["dtfac"])] = (r["t50"], r["final_occ"])
for lam in sorted(g):
    base = [g[lam][(s, 1)] for s in (0, 1, 2)]
    t50s = [b[0] for b in base]
    half = g[lam].get((0, 2))
    print(f"  lam {lam:.1f}: t50 {t50s} median {statistics.median(t50s):.0f}; plateau occupancy "
          f"{min(b[1] for b in base):.2f}-{max(b[1] for b in base):.2f}" + (f"; dt/2: t50 {half[0]}" if half else ""))

print("== C074 3-D (replicate3d.jsonl)")
for l in open(H / "replicate3d.jsonl"):
    r = json.loads(l)
    tr = r["trace"]
    print(f"  {r['stem']}#{r['idx']} {r['name']!r} N {r['N']} dt/{r['dtfac']}: bodies max {max(x[1] for x in tr)} end {tr[-1][1]}; "
          f"mass {tr[0][2]} -> {tr[-1][2]} (x{tr[-1][2] / tr[0][2]:.0f}); first >1 body at t {next((x[0] for x in tr if x[1] > 1), None)}")
f3 = json.loads((EX / "G031-replicating-in-3d" / "replicator3d.json").read_text())
tr = f3["trace"]
print(f"  film N {f3['N']}: bodies max {max(x[1] for x in tr)}, mass {tr[0][2]} -> {tr[-1][2]}")

print("== C090/C091 evolution (evolve.jsonl): mass-weighted mean genome averaged over t >= 1800, paired by seed")
ev = defaultdict(dict)
for l in open(H / "evolve.jsonl"):
    r = json.loads(l)
    end = [x["gmean"] for x in r["trace"] if x["t"] >= 1800 and "gmean" in x]
    if r["N"] != 256:
        print(f"  long run N {r['N']} g0 {r['g0']} seed {r['seed']} {'neutral' if r['neutral'] else 'selected'}: "
              + ", ".join(f"t{int(x['t'])} {x['gmean']}" for x in r["trace"] if x["t"] % 500 == 0 and "gmean" in x))
        continue
    ev[(r["g0"], r["seed"])]["neutral" if r["neutral"] else "selected"] = sum(end) / len(end)
for g0 in sorted({k[0] for k in ev}):
    rows = [(s, ev[(g0, s)]) for (g, s) in sorted(ev) if g == g0 and len(ev[(g, s)]) == 2]
    sel = [v["selected"] for _, v in rows]; neu = [v["neutral"] for _, v in rows]
    print(f"  g0 {g0}: selected {min(sel):.3f}-{max(sel):.3f}, neutral {min(neu):.3f}-{max(neu):.3f}; "
          f"paired differences {[round(v['selected'] - v['neutral'], 3) for _, v in rows]} (seeds {[s for s, _ in rows]})")

print("== C092 invasion (invasion.jsonl): mass-weighted mean genome, start -> t 1000")
for l in open(H / "invasion.jsonl"):
    r = json.loads(l)
    tr = r["trace"]
    print(f"  seed {r['seed']}: {tr[0]['gmean']} -> {tr[-1]['gmean']}; well-half columns (0-31) mean genome at t 1000 "
          f"{sum(tr[-1]['cols'][:32]) / 32:.3f}, uncontrolled half {sum(tr[-1]['cols'][32:]) / 32:.3f}")

print("== C119-C121 therapy toy (therapy.jsonl): 128², 2000 tu after treatment starts, B0 = 40% of carrying mass")
TH = [json.loads(l) for l in open(H / "therapy.jsonl")]


def outcome(r):
    end = r["trace"][-1]
    if end[1] == 0:
        return "cured"
    return f"progressed t{r['progression']:.0f}" if r["progression"] is not None else f"held ({end[1]:.2f} B0)"


for r in sorted((r for r in TH if r["arm"] == "none"), key=lambda r: r["seed"]):
    end = r["trace"][-1]
    print(f"  untreated seed {r['seed']}: starts at t {r['t_start']}, burden at 2000 tu {end[1]:.2f} B0, "
          f"mean genome {end[2]:.2f}, resistant (g < 0.4) share {end[3]:.2f}")
for k in sorted({r["kappa"] for r in TH if r["kappa"] is not None}):
    print(f"  dose kappa {k}:")
    for s in sorted({r["seed"] for r in TH}):
        c = next(r for r in TH if r["seed"] == s and r["kappa"] == k and r["arm"] == "constant")
        a = next(r for r in TH if r["seed"] == s and r["kappa"] == k and r["arm"] == "adaptive")
        print(f"    seed {s}: constant {outcome(c)} (resistant share {c['trace'][-1][3]:.2f}) | adaptive {outcome(a)}"
              f" (resistant share {a['trace'][-1][3]:.2f}, drug on {a['drug_time'] / 20:.0f}% of the time,"
              f" lowest burden {min(x[1] for x in a['trace'][1:]):.2f} B0)")
