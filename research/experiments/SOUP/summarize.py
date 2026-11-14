"""Print every number SOUP.md and claims C076–C078 and C099–C101 quote.

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


def replay_tab():
    """C099-C101: each C078 genome replayed at 6 new spots (replay.py), dominant, 500 tu."""
    first = {r["mutant"]: r for r in map(json.loads, open(HERE / "mutant.jsonl")) if r["mode"] == "dominant"}
    rep = [json.loads(l) for l in open(HERE / "replay.jsonl")]
    ks = sorted(first)
    R = np.array([[r["mutant_mass"][-1] / r["mutant_mass"][0] for r in sorted((r for r in rep if r["mutant"] == k), key=lambda r: r["placement"])] for k in ks])
    T = rep[0]["every"] * (len(rep[0]["mutant_mass"]) - 1)
    o = np.array([first[k]["mutant_mass"][T // first[k]["every"]] / first[k]["mutant_mass"][0] for k in ks])
    print(f"mutant mass ratio at {T * 0.2:.0f} tu: first trial (C078) | six replays | median, grew")
    for i, k in enumerate(ks):
        print(f"  mutant {k:2d}: {o[i]:5.2f} | " + " ".join("%5.2f" % v for v in R[i]) + f" | {np.median(R[i]):5.2f}, {(R[i] > 1).sum()}/6")
    rank = lambda v: np.argsort(np.argsort(v))
    med = np.median(R, 1)
    rho = np.corrcoef(rank(o), rank(med))[0, 1]
    print(f"  Spearman(first trial, replay median) = {rho:.2f}")
    top = np.argsort(-o)[:4]
    print("  top-4 first-trial growers", [ks[i] for i in top], "grew in", int((R[top] > 1).sum()), "of", R[top].size, "replays;",
          "others", int((np.delete(R, top, 0) > 1).sum()), "of", np.delete(R, top, 0).size)
    L = np.log(np.maximum(R, 1e-3))
    stat = lambda X: X.mean(1).var()
    b, w = stat(L), L.var(1).mean()
    rng = np.random.default_rng(0); flat = L.ravel()
    null = [stat(rng.permutation(flat).reshape(L.shape)) for _ in range(10000)]
    p = (1 + sum(x >= b for x in null)) / 10001
    print(f"  log ratio (floored at 1e-3): between-genome var {b:.2f}, within-genome var {w:.2f};"
          f" permutation p = {p:.4f} (10 000 shuffles of genome labels, rng 0)")
    print(f"  replays grown: {(R > 1).sum()}/{R.size}; below 1 % of start: {(R < 0.01).sum()}")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("diversity", diversity_tab), ("bodies", bodies_tab), ("species", species_tab), ("mutant", mutant_tab), ("replay", replay_tab)):
        if what in (name, "all"):
            f()
