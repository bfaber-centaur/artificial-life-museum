"""Print every number quoted in C102-C104, room 79's Klein-bottle section and G053-G054."""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    return [json.loads(x) for x in open(os.path.join(HERE, name))]


print("== C102 twist (Klein 128 x 128 vs torus 128 x 256, 10 000 steps)")
for r in sorted(load("twist.jsonl"), key=lambda r: r["k"]):
    heads = sorted({round(x["chart_heading_deg"] % 90, 1) for x in r["rows"]})
    print(f"  k={r['k']}: crossings {r['crossings']}, travelled {r['distance_travelled_R']:.1f} R, "
          f"max path diff {r['max_path_diff_cells']:.3f} cells, max mass diff {r['max_window_mass_diff']:.2e}, "
          f"chart headings mod 90 {heads}, cover headings {sorted({round(x['cover_heading_deg'], 1) for x in r['rows']})}, "
          f"torus headings {sorted({round(x['torus_heading_deg'], 1) for x in r['rows']})}")

print("== C103 narrow (S001, 128 wide, 400 tu; k = quarter turns of the seed, 4 x positions)")
rs = load("narrow.jsonl")
for ks, lab in (((0, 2), "across the short way (k 0, 2)"), ((1, 3), "along the long way (k 1, 3)")):
    for kind in ("klein", "torus"):
        for lo, hi in ((18, 21), (22, 22), (23, 26), (27, 27), (28, 40)):
            c = collections.Counter(r["outcome"] for r in rs if r["kind"] == kind and r["k"] in ks and lo <= r["ny"] <= hi)
            print(f"  {lab:32s} {kind:5s} heights {lo}-{hi}: {dict(c)}")
for ny in range(18, 41):
    row = []
    for kind in ("klein", "torus"):
        n = sum(r["outcome"] == "glider" for r in rs if r["kind"] == kind and r["ny"] == ny)
        row.append(f"{kind} {n}/16")
    print(f"  height {ny}: gliders {', '.join(row)}")

print("== C104 spin (catalogue spinners, 400 tu)")
for code in ("PG1a", "OG2g"):
    for kind in ("klein", "torus"):
        sub = [r for r in load("spin.jsonl") if r["code"] == code and r["kind"] == kind]
        ok = [r for r in sub if r["end"] == "steps"]
        bad = sorted((r["ny_R"], r["end"]) for r in sub if r["end"] != "steps")
        print(f"  {code} {kind}: heights {sorted(r['ny_R'] for r in ok)} R: drift "
              f"{min(r['net_drift_R_per_tu'] for r in ok):.4f}-{max(r['net_drift_R_per_tu'] for r in ok):.4f} R/tu, "
              f"path speed {min(r['path_speed_R_per_tu'] for r in ok):.3f}-{max(r['path_speed_R_per_tu'] for r in ok):.3f} R/tu, "
              f"turn {min(r['turn_deg_per_tu'] for r in ok):.1f} to {max(r['turn_deg_per_tu'] for r in ok):.1f} deg/tu; "
              f"failed {bad}")
