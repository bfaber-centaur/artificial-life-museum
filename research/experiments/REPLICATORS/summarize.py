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
