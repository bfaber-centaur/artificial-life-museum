"""Print the numbers quoted in WINGS.md and claims C064-C071 from the committed *.jsonl files."""
import collections, json
from pathlib import Path
import numpy as np

H = Path(__file__).parent
J = lambda f: [json.loads(l) for l in (H / f).open()]


def flow():
    R = J("flow_rings.jsonl")
    print("## Flow-Lenia FL-43 (flow_rings.jsonl)")
    by = collections.defaultdict(list)
    for r in R:
        if r["key"].startswith("size"):
            p = int(r["key"].split("-")[1]); by[p].append(r)
    allm = []
    for p in sorted(by):
        n = [r["ncomp"] for r in by[p]]; m = [r["mass0"] for r in by[p]]
        mpr = [a / b for a, b in zip(m, n)]; allm += mpr
        print(f"patch {p}: mass {np.mean(m):7.1f}  cells {n}  mass per cell {np.min(mpr):.1f}-{np.max(mpr):.1f}")
    x = np.array([r["mass0"] for v in by.values() for r in v]); y = np.array([r["ncomp"] for v in by.values() for r in v])
    k = (x * y).sum() / (x * x).sum()
    print(f"fit n = mass / {1 / k:.1f}; max |rel mass drift| {max(abs(r['rel_mass_drift']) for v in by.values() for r in v):.1e}")
    for r in R:
        if r["key"].startswith("classic"):
            print(r["key"], "mass x%.1f" % (r["mass1"] / r["mass0"]), "cover %.2f" % r["cover"], "comps", r["ncomp"])


def gs():
    print("## Gray-Scott (gs_mitosis.jsonl)")
    R = J("gs_mitosis.jsonl")
    for r in R:
        s = r["spots"]
        print(r["arm"], r["seed"], "t=0,5k,10k,20k,25k,30k,40k:", [s[i] for i in (0, 10, 20, 40, 50, 60, 80)])


def pl():
    print("## Particle Lenia (pl_rotor.jsonl): spin rad / 100 tu, mean of the last 5 windows")
    for r in J("pl_rotor.jsonl"):
        s = r["spin_rad_per_window"]
        print(r["arm"], r["k"], "before event %.3f" % np.mean(s[5:9]), "end %.3f" % np.mean(s[-5:]), "n", r["n_final"])


def sl():
    print("## SmoothLife SL-32 glider (sl_glider.jsonl)")
    for r in J("sl_glider.jsonl"):
        tr = r["track"]; N = r["N"]
        ok = all(x["ncomp"] >= 1 for x in tr)
        if r["arm"] != "ring":
            xs = [x["centroids"][0][1] for x in tr if x["ncomp"] == 1]
            ts = [x["t"] for x in tr if x["ncomp"] == 1]
            un = np.unwrap(np.array(xs) * 2 * np.pi / N) * N / (2 * np.pi)
            v = np.polyfit(ts, un, 1)[0]
            print(r["arm"], "alive all 1000 tu" if ok else "LOST", "speed %.4f cells/tu = %.5f ra/tu" % (v, v / r["rule"]["ra"]))
        else:
            print("ring: components at t=0,100,200,300,500,1000:", [tr[i]["ncomp"] for i in (0, 10, 20, 30, 50, 100)])


def nd():
    print("## 3-D survey (nd_survey_3d.jsonl)")
    R = J("nd_survey_3d.jsonl")
    print(len(R), collections.Counter(r["outcome"] for r in R), "movers (>1 cell / 20 tu):", [r["code"] for r in R if r["travel_last20tu"] > 1])
    print("## flatten (flatten.jsonl)")
    C = collections.Counter(); per = collections.Counter()
    for r in J("flatten.jsonl"):
        cs = []
        for s in r["slices"]:
            if s["mass0"] == 0:
                c = "EMPTY"
            else:
                q = s["mass1"] / s["mass0"]
                c = "DIED" if q < 0.01 else ("GREW" if q > 2 else "KEPT")
            cs.append(c)
        C.update(cs)
        per["all3 died or grew" if all(c in ("DIED", "GREW", "EMPTY") for c in cs) else "some slice kept"] += 1
    print(C, per, "3-D controls:", collections.Counter(r["control_3d"] for r in J("flatten.jsonl")))
    print("## found multi-channel survey (nd_survey_found.jsonl)")
    R = J("nd_survey_found.jsonl")
    print(len(R), collections.Counter(r["outcome"] for r in R))
    print("## knockout (mc_knockout.jsonl)")
    t = collections.defaultdict(collections.Counter)
    for r in J("mc_knockout.jsonl"):
        t[r["arm"]][r["outcome"]] += 1
    for a, c in t.items():
        print(a, dict(c))


if __name__ == "__main__":
    flow(); gs(); pl(); sl(); nd()
