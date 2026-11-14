"""Bodies, species and phylogeny for a SOUP run.

Bodies: connected components of A > 0.05 on the torus (8-connected, wrap-merged); each body's
genome is its mass-weighted mean genome. Species: bodies are scanned snapshot by snapshot and
joined to the nearest species seen in the previous `memory` snapshots whose centroid is within
`thr` (L2 over the K weights, weights in [0, 1]); the centroid follows its members (mass-weighted
mean of the current snapshot). A body with no species within `thr` founds a new species whose
parent is the nearest living species. This is a bookkeeping convention for drawing a tree, not
a biological species concept.

  python species.py <npz> <out.json> [thr]
"""
import json, sys
import numpy as np
from scipy import ndimage

THR, MEMORY, MIN_MASS = 0.25, 5, 5.0


def bodies(A, G, thr=0.05):
    lab, k = ndimage.label(A > thr, structure=np.ones((3, 3)))
    if k == 0:
        return []
    par = np.arange(k + 1)
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    for a, b in list(zip(lab[0], lab[-1])) + list(zip(lab[:, 0], lab[:, -1])):
        if a and b:
            ra, rb = f(a), f(b)
            if ra != rb:
                par[ra] = rb
    root = np.array([f(i) for i in range(k + 1)])
    lab = root[lab]
    idx = lab.ravel()
    m = np.bincount(idx, weights=A.ravel().astype(np.float64), minlength=k + 1)
    g = np.stack([np.bincount(idx, weights=(A * Gk).ravel().astype(np.float64), minlength=k + 1) for Gk in G])
    out = []
    for i in np.unique(idx):
        if i and m[i] >= MIN_MASS:
            out.append((float(m[i]), g[:, i] / m[i]))
    return out


def track(path, thr=THR):
    d = np.load(path)
    A, G, T = d["A"], d["G"], d["t"]
    species = []  # dict(id, parent, born, centroid, mass{snap: m})
    for s in range(len(T)):
        a = A[s].astype(np.float32); g = G[s].astype(np.float32) / 255.0
        bs = bodies(a, g)
        alive = [sp for sp in species if s - sp["last"] <= MEMORY]
        acc = {}
        new = []
        for m, gen in bs:
            best, bd = None, 1e9
            for sp in alive:
                dd = float(np.linalg.norm(sp["c"] - gen))
                if dd < bd:
                    best, bd = sp, dd
            if best is not None and bd < thr:
                acc.setdefault(best["id"], []).append((m, gen))
            else:
                # join a species founded earlier in this same snapshot if close
                for sp in new:
                    if np.linalg.norm(sp["c"] - gen) < thr:
                        acc.setdefault(sp["id"], []).append((m, gen)); break
                else:
                    sp = dict(id=len(species), parent=(best["id"] if best is not None else None), born=s, last=s,
                              c=gen.copy(), mass={}, dist=(bd if best is not None else None))
                    species.append(sp); new.append(sp)
                    acc.setdefault(sp["id"], []).append((m, gen))
        for sid, mem in acc.items():
            sp = species[sid]
            ms = np.array([x[0] for x in mem]); gs = np.array([x[1] for x in mem])
            sp["c"] = (ms[:, None] * gs).sum(0) / ms.sum()
            sp["mass"][s] = float(ms.sum()); sp["n"] = sp.get("n", {}); sp["n"][s] = len(mem)
            sp["last"] = s
    return T, species


def main():
    path, out = sys.argv[1], sys.argv[2]
    thr = float(sys.argv[3]) if len(sys.argv) > 3 else THR
    T, species = track(path, thr)
    rec = dict(t=T.tolist(), thr=thr, species=[dict(id=sp["id"], parent=sp["parent"], born=sp["born"],
               last=sp["last"], centroid=sp["c"].round(4).tolist(),
               mass={str(k): round(v, 2) for k, v in sp["mass"].items()},
               n={str(k): v for k, v in sp.get("n", {}).items()}) for sp in species])
    json.dump(rec, open(out, "w"))
    tot = len(species); big = [sp for sp in species if max(sp["mass"].values(), default=0) > 100]
    print(f"{tot} species, {len(big)} ever >100 mass; alive at end:",
          sum(1 for sp in species if sp["last"] == len(T) - 1))


if __name__ == "__main__":
    main()
