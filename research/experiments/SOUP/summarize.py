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


def neutral_tab():
    """C116-C118: neutral markers at the same 72 places as the replays (neutral.py)."""
    rep = {(r["mutant"], r["placement"]): r for r in map(json.loads, open(HERE / "replay.jsonl"))}
    neu = {(r["place_of_mutant"], r["placement"]): r for r in map(json.loads, open(HERE / "neutral.jsonl"))}
    keys = sorted(rep)
    assert sorted(neu) == keys, "neutral.jsonl must cover all 72 replay places"
    rm = np.array([rep[k]["mutant_mass"][-1] / rep[k]["mutant_mass"][0] for k in keys])
    rn = np.array([neu[k]["marker_mass"][-1] / neu[k]["marker_mass"][0] for k in keys])
    Lm, Ln = np.log(np.maximum(rm, 1e-3)), np.log(np.maximum(rn, 1e-3))
    print("neutral markers at the 72 replay places, 500 tu (ratio end / start)")
    print(f"  neutral: grew {(rn > 1).sum()}/72, below 1 % of start {(rn < 0.01).sum()}, "
          f"median {np.median(rn):.2f}, var of log ratio {Ln.var():.2f}")
    print(f"  mutants: grew {(rm > 1).sum()}/72, below 1 % of start {(rm < 0.01).sum()}, "
          f"median {np.median(rm):.2f}, var of log ratio {Lm.var():.2f}")
    rank = lambda v: np.argsort(np.argsort(v))
    rho = np.corrcoef(rank(Lm), rank(Ln))[0, 1]
    rng = np.random.default_rng(1)
    null = [np.corrcoef(rank(Lm), rank(rng.permutation(Ln)))[0, 1] for _ in range(10000)]
    p = (1 + sum(abs(x) >= abs(rho) for x in null)) / 10001
    print(f"  same place, mutant vs neutral: Spearman {rho:.2f} (two-sided permutation p = {p:.4f})")
    both_grew = int(((rm > 1) & (rn > 1)).sum()); both_shrank = int(((rm <= 1) & (rn <= 1)).sum())
    print(f"  agree on direction at {both_grew + both_shrank}/72 places ({both_grew} both grew, {both_shrank} both shrank)")
    D = (Lm - Ln).reshape(12, 6)
    print("  per genome: median log(mutant/neutral) over its 6 places, and places where mutant beat neutral")
    for k in range(12):
        print(f"    mutant {k:2d}: {np.median(D[k]):+.2f}  beat neutral {int((D[k] > 0).sum())}/6")
    beat = int((D > 0).sum())
    print(f"  mutants beat the neutral marker at {beat}/72 places")
    # sign test per genome: how many genomes beat neutral at >= 5 of 6 places, or lose at >= 5 of 6
    stat = lambda X: X.mean(1).var()
    b = stat(D)
    rng = np.random.default_rng(2)
    nullD = [stat(rng.permutation(D.ravel()).reshape(D.shape)) for _ in range(10000)]
    pD = (1 + sum(x >= b for x in nullD)) / 10001
    from math import comb
    p45 = sum(comb(72, i) for i in range(beat, 73)) / 2 ** 72 * 2
    print(f"  log(mutant/neutral): between-genome var {b:.2f}, within {D.var(1).mean():.2f}; "
          f"permutation p = {pD:.4f} (10 000 shuffles, rng 2); sign test {beat}/72 two-sided p = {p45:.3f}")
    print(f"  genomes beating neutral at >=5/6 places: {[k for k in range(12) if (D[k] > 0).sum() >= 5]}; "
          f"losing at >=5/6: {[k for k in range(12) if (D[k] < 0).sum() >= 5]}")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("diversity", diversity_tab), ("bodies", bodies_tab), ("species", species_tab), ("mutant", mutant_tab), ("replay", replay_tab), ("neutral", neutral_tab)):
        if what in (name, "all"):
            f()
