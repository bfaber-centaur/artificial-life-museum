"""Does the field lane's settled glider GA stay GLIDER under the §9 refinement settings?

    git show 5f21378:research/experiments/REEF-field/seeds/GA.npy > GA.npy
    python research/experiments/REEF-numerics/glider/glider_variants.py GA.npy [--tu 100]

Settings: base (T10, N256), T20 (N256), N512 (T10, same R, centred embed) and R26 (2x2 kron,
N512). Per tu: mass (sum/R^2), unwrapped centroid (min-image increments per step), component
count at A > 0.1. Classes reuse protocol §7 / L6-field: GLIDER net speed > 0.2 R/tu, STATIC path
speed < 0.02 R/tu, CIRCLER net < 0.1 and path > 0.2, judged per 10-tu window. GA is a T10/R13
settled state, so every refined setting starts with a transient; the series shows it.
"""
import argparse, csv, hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy import ndimage
from alm.lenia import Lenia, Rule

HERE = Path(__file__).resolve().parent
GA_SHA = "982b793956a8336d96969d1cd5ed71e83604e78c1aa360819c334eaa098c25f1"
sha = lambda A: hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()


def centroid(A):
    out = []
    for ax in (0, 1):
        n = A.shape[ax]; w = A.sum(axis=1 - ax); th = 2 * np.pi * np.arange(n) / n
        out.append((np.arctan2((w * np.sin(th)).sum(), (w * np.cos(th)).sum()) % (2 * np.pi)) * n / (2 * np.pi))
    return np.array(out)


def ncomp(A):
    lab, n = ndimage.label(A > 0.1, structure=np.ones((3, 3)))
    # merge labels touching across the torus seam
    parent = list(range(n + 1))
    def f(x):
        while parent[x] != x: x = parent[x]
        return x
    for a, b in list(zip(lab[0], lab[-1])) + list(zip(lab[:, 0], lab[:, -1])):
        if a and b: parent[f(a)] = f(b)
    return len({f(i) for i in range(1, n + 1)})


def run(name, A, R, T, tu):
    w = Lenia(Rule(R=R, T=T, mu=.155, sigma=.020), A)
    N = A.shape[0]; pos = np.zeros(2); c = centroid(w.A); rows = []
    for k in range(1, tu + 1):
        for _ in range(T):
            w.step(); c2 = centroid(w.A); d = (c2 - c + N / 2) % N - N / 2; pos += d; c = c2
        rows.append({"setting": name, "tu": k, "mass_R2": w.A.sum() / R**2, "y_R": pos[0] / R, "x_R": pos[1] / R,
                     "components": ncomp(w.A)})
    P = np.array([[0, 0]] + [[r["y_R"], r["x_R"]] for r in rows])
    wins = []
    for s in range(0, tu, 10):
        seg = P[s:s + 11]; net = np.hypot(*(seg[-1] - seg[0])) / 10
        path = np.hypot(*np.diff(seg, axis=0).T).sum() / 10
        cls = "GLIDER" if net > 0.2 else "STATIC" if path < 0.02 else "CIRCLER" if (net < 0.1 and path > 0.2) else "OTHER"
        d = seg[-1] - seg[0]
        wins.append({"tu": [s, s + 10], "net_R_per_tu": net, "path_R_per_tu": path, "class": cls,
                     "heading_deg": float(np.degrees(np.arctan2(d[0], d[1]))),
                     "mass_R2_end": rows[s + 9]["mass_R2"], "components_max": max(r["components"] for r in rows[s:s + 10])})
    return rows, {"setting": name, "R": R, "T": T, "N": N, "initial_sha256": sha(A), "final_sha256": sha(w.A), "windows": wins}


ap = argparse.ArgumentParser(); ap.add_argument("ga"); ap.add_argument("--tu", type=int, default=100)
ap.add_argument("--only", default="base,T20,N512,R26"); a = ap.parse_args()
GA = np.load(a.ga)
assert sha(GA) == GA_SHA, sha(GA)
big = np.zeros((512, 512)); big[128:384, 128:384] = GA  # GA is centred; its support is far from the seam
assert GA[:20].sum() == GA[-20:].sum() == GA[:, :20].sum() == GA[:, -20:].sum() == 0
S = {"base": (GA, 13, 10), "T20": (GA, 13, 20), "N512": (big, 13, 10), "R26": (np.kron(GA, np.ones((2, 2))), 26, 10)}
allrows, summ = [], {"GA_sha256": GA_SHA, "GA_source": "reef/field 5f21378 research/experiments/REEF-field/seeds/GA.npy"}
for name in a.only.split(","):
    rows, s = run(name, *S[name], a.tu); allrows += rows; summ[name] = s
    print(name, [(w["tu"][0], w["class"], round(w["net_R_per_tu"], 3), round(w["heading_deg"], 1), round(w["mass_R2_end"], 4)) for w in s["windows"]], flush=True)
tag = "-".join(a.only.split(","))
with open(HERE / f"glider_variants_{tag}.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(allrows[0])); wr.writeheader(); wr.writerows(allrows)
(HERE / f"glider_variants_{tag}.json").write_text(json.dumps(summ, indent=1) + "\n")
