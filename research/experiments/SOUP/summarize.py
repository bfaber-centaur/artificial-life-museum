"""Print every number SOUP.md and claims C076–C078 quote.

Needs the run snapshots (SOUP_OUT, default states/): B16s0–3 (blend) and D16s0–3 (dominant), each
`run.py <name> --rule 16 --seed k --steps 12000 --every 40 [--inherit dominant]`; plus mutant.jsonl.

  python summarize.py [diversity|bodies|species|mutant|all]
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from diversity import spread
from species import bodies, track

HERE = Path(__file__).parent
OUT = Path(os.environ.get("SOUP_OUT", HERE / "states"))
PAIRS = [(f"B16s{k}", f"D16s{k}") for k in range(4)]


def load(name):
    return np.load(OUT / f"{name}.npz")


def diversity_tab():
    print("genome spread (mass-weighted RMS distance from mean genome), t = 0 / 1000 / 2400 tu")
    for b, d in PAIRS:
        row = []
        for n in (b, d):
            z = load(n); A, G, T = z["A"], z["G"], z["t"]
            i = int(np.argmin(np.abs(T * 0.2 - 1000)))
            row.append(" ".join("%.3f" % spread(A[s].astype(np.float32), G[s].astype(np.float32) / 255) for s in (0, i, -1)))
        print(f"  seed {b[-1]}:  blend {row[0]}   dominant {row[1]}")


def bodies_tab():
    print("final bodies (A > 0.05, mass >= 5): count, largest body's share of body mass, top-3 share")
    for b, d in PAIRS:
        row = []
        for n in (b, d):
            z = load(n); a = z["A"][-1].astype(np.float32); g = z["G"][-1].astype(np.float32) / 255
            m = sorted((x[0] for x in bodies(a, g)), reverse=True)
            row.append("%3d  %.2f  %.2f" % (len(m), m[0] / sum(m), sum(m[:3]) / sum(m)))
        print(f"  seed {b[-1]}:  blend {row[0]}   dominant {row[1]}")


def species_tab():
    print("species bookkeeping (thr 0.25): founded, alive at end, ever above mass 100")
    for b, d in PAIRS:
        row = []
        for n in (b, d):
            T, sp = track(OUT / f"{n}.npz")
            row.append("%4d %4d %3d" % (len(sp), sum(1 for s in sp if s["last"] == len(T) - 1),
                                        sum(1 for s in sp if max(s["mass"].values(), default=0) > 100)))
        print(f"  seed {b[-1]}:  blend {row[0]}   dominant {row[1]}")


def mutant_tab():
    rows = [json.loads(l) for l in open(HERE / "mutant.jsonl")]
    print("one mutant in a one-species world: mutant mass at t = 0 / 200 / 500 / 1000 tu")
    by = {}
    for r in rows:
        by.setdefault(r["mutant"], {})[r["mode"]] = r
    alive = {"blend": 0, "dominant": 0}
    for k in sorted(by):
        line = f"  mutant {k:2d} |delta| {by[k]['blend']['dnorm']:.2f}:"
        for mode in ("blend", "dominant"):
            s = by[k][mode]["mutant_mass"]; e = by[k][mode]["every"]
            pick = [s[int(t / 0.2 / e)] for t in (0, 200, 500, 1000)]
            line += f"  {mode} " + " ".join("%6.1f" % v for v in pick)
            alive[mode] += s[-1] > 0
        print(line)
    print(f"  mutants with mass > 0 at 1000 tu: blend {alive['blend']}/{len(by)}, dominant {alive['dominant']}/{len(by)}")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("diversity", diversity_tab), ("bodies", bodies_tab), ("species", species_tab), ("mutant", mutant_tab)):
        if what in (name, "all"):
            f()
