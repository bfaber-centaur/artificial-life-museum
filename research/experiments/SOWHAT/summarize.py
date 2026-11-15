"""Print every number the "So what?" wing quotes (claims C112-C115)."""
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    return [json.loads(l) for l in (HERE / name).read_text().splitlines() if l.strip()]


def drift():
    print("C112 Moran (embedded chain), one starting mutant")
    R = rows("moran.jsonl")
    for r in R:
        print(f"  N {r['N']:3d}  s {r['s']:+.3f}  sim {r['sim']:.5f}  exact {r['exact']:.5f}  z {r['z']:+.2f}")
    print(f"  max |z| over {len(R)} conditions: {max(abs(r['z']) for r in R):.2f}")
    f = rows("fates.jsonl")[0]
    print(f"  Wright-Fisher N {f['N']} s {f['s']}: fixed {f['fixed']}/{f['reps']}, lost {f['lost']} "
          f"({f['lost_by_gen20']} by generation 20), unresolved {f['unresolved']}; Kimura {f['kimura']:.4f}")


def atlas():
    print("C113 Gray-Scott atlas")
    R = rows("atlas.jsonl")
    c = Counter(r["kind"] for r in R)
    print("  kinds:", dict(c))
    for kind in sorted(c):
        pts = [(r["F"], r["k"]) for r in R if r["kind"] == kind]
        print(f"  {kind}: F {min(p[0] for p in pts)}-{max(p[0] for p in pts)}, "
              f"k {min(p[1] for p in pts)}-{max(p[1] for p in pts)}")


def epidemic():
    print("C114 epidemic, beta 0.15, gamma 0.1, 200 x 200, 10 seeds")
    R = rows("epidemic.jsonl")
    for w in ("mixed", "lattice", "shortcuts"):
        rr = [r for r in R if r["world"] == w]
        pk = [r["peak"] for r in rr]
        tp = [r["t_peak"] for r in rr]
        fs = [r["final_size"] for r in rr]
        st = [r["steps"] for r in rr]
        print(f"  {w:9s} peak {100*min(pk):.1f}-{100*max(pk):.1f}%  at t {min(tp)}-{max(tp)}  "
              f"final {100*min(fs):.1f}-{100*max(fs):.1f}%  over by t {min(st)}-{max(st)}")
    print("C115 take-off sweep (final size per run, %)")
    T = rows("threshold.jsonl")
    d = defaultdict(list)
    for r in T:
        d[(r["world"], r["beta"])].append(100 * r["final_size"])
    for w in ("mixed", "lattice", "shortcuts"):
        line = []
        for b in sorted({r["beta"] for r in T}):
            v = d[(w, b)]
            took = sum(x > 10 for x in v)
            line.append(f"{b}:{took}/{len(v)}")
        print(f"  {w:9s} runs with >10% ever infected: " + "  ".join(line))
        smallest = min(b for b in sorted({r['beta'] for r in T}) if sum(x > 10 for x in d[(w, b)]) * 2 > len(d[(w, b)]))
        print(f"  {w:9s} smallest beta where most runs take off: {smallest}")


if __name__ == "__main__":
    drift()
    atlas()
    epidemic()
