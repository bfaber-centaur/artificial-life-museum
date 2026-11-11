"""WINGS-3D intervention: flatten each 3-D catalogue species (animals3D.json) to 2-D.

For each entry: centre its cells on a 64^3 torus, run 20 time units in 3-D (nd_lenia.NDLenia),
then cut the 2-D plane through the mass centroid normal to each axis (3 slices), paste it in the
centre of a 128^2 torus and run 100 time units of 2-D Lenia with the *same* rule (same R, T, mu,
sigma, kernel shells; the kernel is now a disk instead of a ball). The 3-D control continues
100 time units in 3-D. Outcome as nd_survey: DIED (< 1 % of start mass), FILLED (cover > 0.5),
else PERSISTED. Writes flatten.jsonl.

  python flatten.py [start stop]
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).parent))
from nd_lenia import NDLenia, entry_state, load_catalog
from nd_survey import centroid

HERE = Path(__file__).parent
SETTLE, TU = 20, 100


def outcome(m0, m1, cover):
    return "DIED" if m1 < 0.01 * m0 else ("FILLED" if cover > 0.5 else "PERSISTED")


def main(a, b):
    cat = load_catalog("animals3D.json")
    for i in range(a, min(b, len(cat))):
        e = cat[i]
        p, A = entry_state(e, 3, 64)
        T = p[0]["T"]
        L = NDLenia(p, A)
        for _ in range(int(SETTLE * T)):
            L.step()
        A3 = L.A[0].copy()
        c = np.rint(centroid(A3)).astype(int) % 64
        rec = {"index": i, "code": e.get("code"), "name": e.get("name"), "R": p[0]["R"], "T": T,
               "settle_tu": SETTLE, "tu": TU, "slices": []}
        L3 = NDLenia(p, A3[None])
        for _ in range(int(TU * T)):
            L3.step()
        rec["control_3d"] = outcome(A3.sum(), L3.A.sum(), float((L3.A[0] > 0.1).mean()))
        for ax in range(3):
            sl = np.take(A3, c[ax], axis=ax)
            W = np.zeros((128, 128)); W[32:96, 32:96] = sl
            L2 = NDLenia(p, W[None])
            m0 = float(W.sum())
            for _ in range(int(TU * T)):
                L2.step()
            m1 = float(L2.A.sum()); cover = float((L2.A[0] > 0.1).mean())
            rec["slices"].append({"axis": ax, "plane": int(c[ax]), "mass0": round(m0, 3), "mass1": round(m1, 3),
                                  "cover": round(cover, 4), "ncomp": int(ndimage.label(L2.A[0] > 0.1, structure=np.ones((3, 3)))[1]),
                                  "outcome": outcome(m0, m1, cover) if m0 > 0 else "EMPTY",
                                  "final_sha256": hashlib.sha256(np.ascontiguousarray(L2.A).tobytes()).hexdigest()})
        with (HERE / "flatten.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(i, rec["code"], rec["control_3d"], [s["outcome"] for s in rec["slices"]], flush=True)


if __name__ == "__main__":
    args = [int(x) for x in sys.argv[1:]] or [0, 999]
    main(*args)
