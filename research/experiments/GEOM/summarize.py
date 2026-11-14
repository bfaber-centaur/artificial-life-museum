"""Print every number the GEOM claims (C084–C087), gallery captions and room 79 quote.

Usage:  python summarize.py
"""
import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = 13
H001 = os.path.join(HERE, "..", "H001-lattice-wobble", "x1_R13.csv")


def jl(name):
    p = os.path.join(HERE, name)
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def outcome(r):
    b = [x for x in r["bodies"] if x["mass_R2"] > 0.2]
    if not b:
        return "none"
    if len(b) == 1:
        return "fused" if b[0]["mass_R2"] > 0.7 else "one"
    return f"{len(b)} bodies"


def meet():
    rows = jl("meet.jsonl")
    if not rows:
        return
    print("== C084 meet: parallel pairs on spheres (icosphere, 2000 steps = 200 tu)")
    seps = sorted({r["sep_R"] for r in rows})
    print("rho  " + "  ".join(f"sep {s}R".ljust(22) for s in seps))
    for rho in sorted({r["rho"] for r in rows}):
        cells = []
        for s in seps:
            r = next(x for x in rows if x["rho"] == rho and x["sep_R"] == s)
            t = r["first_touch_step"]
            cells.append(f"{'touch ' + str(t / 10) + 'tu' if t else 'no touch'}: {outcome(r)}".ljust(22))
        print(f"{rho:<4} " + "  ".join(cells))
    touched = [r for r in rows if r["first_touch_step"]]
    print(f"touched {len(touched)}/{len(rows)}; of those with sep >= 3R: "
          f"{sum(1 for r in touched if r['sep_R'] >= 3)}/{sum(1 for r in rows if r['sep_R'] >= 3)}")
    from collections import Counter
    print("outcomes (all):", dict(Counter(outcome(r) for r in rows)))
    fused = [b for r in rows if outcome(r) == "fused" for b in r["bodies"] if b["mass_R2"] > 0.7]
    print("fused bodies: mass/R2 %.3f-%.3f, gyradius/R %.3f-%.3f (S101 flat: 0.8737, 0.8154)" % (
        min(b["mass_R2"] for b in fused), max(b["mass_R2"] for b in fused),
        min(b["gyradius_R"] for b in fused), max(b["gyradius_R"] for b in fused)))
    singles = [b["mass_R2"] for r in rows for b in r["bodies"] if 0.2 < b["mass_R2"] < 0.7]
    print("single Orbium on the sphere: mass/R2 %.3f-%.3f" % (min(singles), max(singles)))
    for r in jl("flat.jsonl"):
        print(f"flat control sep {r['sep_R']}R: first touch {r['first_touch_step']}, "
              f"blobs at end {r['n_bodies_final']}, mass/R2 {r['final_mass_R2']:.4f}")


def pair():
    rows = jl("pair.jsonl")
    if not rows:
        return
    print("\n== C085 pair separation vs geodesic law (a = seeded separation, s = s0 + path)")
    for r in sorted(rows, key=lambda r: (r["world"], r["L"], r["sep_R"])):
        d = np.array([x["d"] for x in r["rows"]])
        p = np.array([x["pred"] for x in r["rows"]])
        s = np.array([x["s"] for x in r["rows"]])
        n = len(d)
        if r["world"] == "sphere":  # compare only until the first closest approach
            inc = np.flatnonzero(np.diff(d) > 0)
            n = inc[0] + 1 if len(inc) else len(d)
        far = np.zeros(len(d), bool)
        far[:n] = d[:n] > 2.5 * R
        err = np.abs(d - p)[far].max() / R if far.any() else float("nan")
        print(f"{r['world']:<10} L={r['L']:<3} ({r['L'] / R:.1f} R) sep {r['sep_R']}R: "
              f"travel {s[-1] / R:5.2f} R, d {d[0] / R:.2f} -> {d[-1] / R:5.2f} R "
              f"(law {p[-1] / R:5.2f}); max |d - law| while d > 2.5 R: {err:.3f} R; "
              f"min d {d.min() / R:.2f} R; first approach to {d[n - 1] / R:.2f} R (law {p[n - 1] / R:.2f})")
    hy = [r for r in rows if r["world"] == "hyperbolic"]
    if hy:
        e = max(np.abs(np.array([x["d"] for x in r["rows"]]) - np.array([x["pred"] for x in r["rows"]])).max() / R
                for r in hy)
        g = [r["final_d_R"] / r["sep_R"] for r in hy]
        print(f"hyperbolic: worst |d - law| {e:.3f} R over all samples; separation grew x{min(g):.1f}-x{max(g):.1f}")


def curvature():
    rows = jl("curvature.jsonl")
    if not rows:
        return
    print("\n== C086 one Orbium on spheres of shrinking radius (3000 steps = 300 tu)")
    for r in sorted(rows, key=lambda r: r["rho"]):
        b = r["bodies"]
        print(f"rho {r['rho']:>3} ({r['rho_over_R']:.2f} R, {r['n_cells']} cells): "
              f"{'alive' if r['alive'] else 'dead at step ' + str(r['death_step'])}; "
              f"mass/R2 last {r['mass_R2_last']:.3f} max {r['mass_R2_max']:.3f}; "
              f"speed {r['speed_R_per_tu_last500']}; bodies {len(b)}"
              + (f" gyr {b[0]['gyradius_R']:.3f}" if b else ""))


def heading():
    print("\n== C087 heading lock: square (H001-X1) vs hex vs glass, R 13, 8000 steps")

    def load(p, lattice=None):
        if not os.path.exists(p):
            return []
        out = []
        for row in csv.DictReader(open(p)):
            rot = float(row["rot"])
            out.append((rot, int(row["alive"]), float(row["heading_w7"]), float(row["heading_w6"])))
        return sorted(out)

    for name, p in (("square", H001), ("hex", os.path.join(HERE, "heading_hex.csv")),
                    ("glass", os.path.join(HERE, "heading_glass.csv"))):
        rows = load(p)
        if not rows:
            continue
        alive = [r for r in rows if r[1]]
        hs = np.array([r[2] for r in alive])
        settled = np.abs(np.array([r[2] - r[3] for r in alive])) < 0.05
        # plateaus: settled headings within 0.15 deg of each other
        hset = np.sort(hs[settled])
        plateaus = []
        for h in hset:
            if plateaus and h - plateaus[-1][-1] < 0.15:
                plateaus[-1].append(h)
            else:
                plateaus.append([h])
        # H001 rotates the start clockwise in (col, row) (heading 68.2 - rot); GEOM rotates it
        # counter-clockwise (heading 68.2 + rot)
        sign = -1 if name == "square" else 1
        expected = np.array([(68.198 + sign * r[0]) for r in alive])
        dev = (hs - expected + 180) % 360 - 180
        print(f"{name}: {len(rows)} starts, {len(alive)} alive, {settled.sum()} settled "
              f"(|w7 - w6| < 0.05 deg) on {len(plateaus)} headings: "
              + ", ".join(f"{np.mean(q):.2f} (x{len(q)})" for q in plateaus))
        print(f"   |heading - (68.2 + rotation)|: median {np.median(np.abs(dev)):.2f} deg, "
              f"max {np.abs(dev).max():.2f} deg")
        if len(alive) < len(rows):
            # a dead world has zero velocity, so its window heading prints as exactly 0.000
            dw = []
            for row in csv.DictReader(open(p)):
                if int(row["alive"]):
                    continue
                ws = [float(row[f"heading_w{k}"]) for k in range(8)]
                dw.append(next(k for k in range(8) if ws[k] == 0.0 and all(x == 0.0 for x in ws[k:])))
            print(f"   deaths: {len(dw)}; last window with motion (1000 steps each): "
                  f"{sorted(dw)} -> died within the first 100 tu: {sum(1 for k in dw if k <= 1)}")
            for row in csv.DictReader(open(p)):
                if int(row["alive"]):
                    ws = [round(float(row[f"heading_w{k}"]), 1) for k in range(8)]
                    print(f"   survivor rot {row['rot']}: window headings {ws}")


if __name__ == "__main__":
    meet()
    pair()
    curvature()
    heading()
