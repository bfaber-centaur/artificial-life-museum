"""Print every number quoted in ZOO.md, the claims C080-C083 and room 78.

    .venv/bin/python research/experiments/ZOO/summarize.py
"""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(w):
    return [json.loads(l) for l in (HERE / f"atlas-{w}.jsonl").read_text().splitlines()]


print("== C080 Orbium x Orbium (atlas-O, T10) and the dt/2 check (atlas-O20)")
O, O20 = rows("O"), rows("O20")
for name, R in (("T10", O), ("T20", O20)):
    c = collections.Counter(r["class"] for r in R)
    print(name, len(R), dict(c))
    ex = sorted((r["theta"], r["b_R"]) for r in R if r["class"] == "EXPLODE")
    print("  detonations (theta, b):", ex)
    fu = [r for r in R if r["class"] == "FUSE"]
    print("  fused product mass / one Orbium:", sorted({round(r["products"][0]["mass"] / r["mA"], 2) for r in fu}))
    sv = [r for r in R if r["class"] == "SURVIVOR"]
    print("  survivor mass / one Orbium: min %.2f max %.2f" % (min(r["products"][0]["mass"] / r["mA"] for r in sv),
                                                              max(r["products"][0]["mass"] / r["mA"] for r in sv)))
    print("  max mass ratio at tc+25 among detonations: %.1f" % max(r["mass_ratio"] for r in R if r["class"] == "EXPLODE"))
a = {(r["theta"], r["b_R"]): r["class"] for r in O}
b = {(r["theta"], r["b_R"]): r["class"] for r in O20}
same = sum(a[k] == b[k] for k in b)
print(f"cells agreeing T10 vs T20: {same}/{len(b)} = {same / len(b):.0%}")
contact = [k for k in a if a[k] != "MISS"]
print("contact cells T10:", len(contact), " of which agree:", sum(a[k] == b[k] for k in contact))

print("\n== C081 Pteryx world (atlas-P, atlas-P6-dense, atlas-PC)")
P = rows("P")
pp = [r for r in P if r["b"] != "C0v"]
print("Pteryx-Pteryx rows:", len(pp), dict(collections.Counter(r["class"] for r in pp)))
d = rows("P6-dense")
print("P6al dense rows:", len(d), dict(collections.Counter(r["class"] for r in d)))
pc = [r for r in P if r["b"] == "C0v"]
print("Pteryx-C0v rows (coarse):", len(pc), dict(collections.Counter(r["class"] for r in pc)))
PC = rows("PC")
for code in ["P6al", "P7al", "P8al", "P9al", "P10al"]:
    rs = sorted([r for r in PC if r["a"] == code], key=lambda r: r["b_R"])
    sw = [r["b_R"] for r in rs if r["class"] == "SURVIVOR"]
    ex = [r["b_R"] for r in rs if r["class"] == "EXPLODE"]
    gain = [round(r["products"][0]["mass"] - r["mA"]) for r in rs if r["class"] == "SURVIVOR"]
    print(f"  {code}: swallow b {sw}; detonate b {min(ex)}..{max(ex)}; mass gained {gain}; classes {dict(collections.Counter(r['class'] for r in rs))}")
print("  C0v mass:", round(PC[0]["mB"], 1))

print("\n== C082 / C083 feeding (feed-*.json, ladder_match.json)")
for tag in ("-altfilm", "-alt", "-run1", "-T20"):
    f = HERE / f"feed{tag}.json"
    if not f.exists():
        continue
    L = json.loads(f.read_text())
    meals = [e for e in L["log"] if "meal" in e and "mass" in e]
    stop = [e for e in L["log"] if e.get("event") == "no offset grew"]
    gains = [round(meals[i]["mass"] - (meals[i - 1]["mass"] if i else L["ladder"]["P6al"]), 1) for i in range(len(meals))]
    retries = sum(len(m["tries"]) - 1 for m in meals)
    print(f"{tag}: T{L['args'].get('T', 10)} alternate={L['args']['alternate']} meals grown {len(meals)}, "
          f"segments {meals[-1]['segments_est']}, final mass {meals[-1]['mass']}, retries {retries}, "
          f"gain per meal min {min(gains)} max {max(gains)}; stop: {[t['outcome'] for t in stop[0]['tries']] if stop else None}")
    if tag == "-altfilm":
        print("   per-segment mass from ladder P6-P10:", round(L["per_segment"], 1), " ring mass:", round(L["ring_mass"], 1))
        fc = [e for e in L["log"] if e.get("event") == "final cruise"]
        print("   final cruise:", fc)
alt = json.loads((HERE / "feed-alt.json").read_text())["log"]
film = json.loads((HERE / "feed-altfilm.json").read_text())["log"]
print("alt and altfilm logs bitwise equal (sha per meal):", [x.get("sha256") for x in alt] == [x.get("sha256") for x in film])
for r in json.loads((HERE / "ladder_match.json").read_text()):
    print("ladder match", r)

print("\n== aquarium bombardment (aq-bombard.jsonl), notes only")
aq = [json.loads(l) for l in (HERE / "aq-bombard.jsonl").read_text().splitlines()]
for k in (1, 2, 3, 4):
    rs = [r for r in aq if r["k"] == k]
    left = [len(r["series"][-1]["census"]) - 1 for r in rs]
    multi = [max(c["units"] for c in r["series"][-1]["census"]) for r in rs]
    print(f"k={k}: runs {len(rs)}, free bodies left besides the rock {left}, largest body (units) {multi}")
