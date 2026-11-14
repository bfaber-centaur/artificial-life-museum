"""Survey Chan's 3-D catalogue (animals3D.json) and found multi-channel / multi-kernel creatures
(found/<D><C><K>.json, 2-D only) under nd_lenia.NDLenia, our independent implementation.

Each creature: cells centred on a zero torus (2-D: 256^2; 3-D: 64^3), run 100 time units
(100 T steps). Records total mass per channel at start/end, number of components (sum of
channels > 0.1, 8-/26-connected, not torus-merged), cover fraction and centroid travel over the
last 20 tu. Outcome: DIED (mass < 1 % of start), FILLED (cover > 0.5), else PERSISTED.

  python nd_survey.py 3d            -> nd_survey_3d.jsonl
  python nd_survey.py found <stem>  -> nd_survey_found.jsonl (appends)
"""
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from scipy import ndimage  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from nd_lenia import NDLenia, entry_state, load_catalog, load_found  # noqa: E402

HERE = Path(__file__).parent
TU, TAIL = 100, 20


def centroid(T):
    n = T.shape[0]
    out = []
    for ax in range(T.ndim):
        m = T.sum(axis=tuple(a for a in range(T.ndim) if a != ax))
        th = 2 * np.pi * np.arange(T.shape[ax]) / T.shape[ax]
        out.append((np.angle((m * np.exp(1j * th)).sum()) % (2 * np.pi)) * T.shape[ax] / (2 * np.pi))
    return np.array(out)


def run(e, dim, size):
    p, A = entry_state(e, dim, size)
    L = NDLenia(p, A)
    T = p[0]["T"]
    steps = int(round(TU * T))
    m0 = L.A.sum(axis=tuple(range(1, L.A.ndim)))
    cs = []
    for t in range(1, steps + 1):
        L.step()
        if t >= steps - TAIL * T and t % max(1, int(T)) == 0:
            cs.append(centroid(L.A.sum(0)))
    tot = L.A.sum(0)
    m1 = L.A.sum(axis=tuple(range(1, L.A.ndim)))
    st = ndimage.generate_binary_structure(dim, dim)
    ncomp = ndimage.label(tot > 0.1, structure=st)[1]
    cover = float((tot > 0.1).mean())
    d = np.diff(np.array(cs), axis=0)
    d = (d + size / 2) % size - size / 2
    travel = float(np.sqrt((d.sum(0) ** 2).sum())) if len(d) else 0.0
    outcome = "DIED" if m1.sum() < 0.01 * m0.sum() else ("FILLED" if cover > 0.5 else "PERSISTED")
    return {"code": e.get("code"), "name": e.get("name"), "cname": e.get("cname"), "R": p[0]["R"], "T": T,
            "kernels": len(p), "channels": int(A.shape[0]), "size": size, "tu": TU, "mass0": m0.round(3).tolist(),
            "mass1": m1.round(3).tolist(), "ncomp": int(ncomp), "cover": round(cover, 4),
            "travel_last20tu": round(travel, 2), "outcome": outcome,
            "final_sha256": hashlib.sha256(np.ascontiguousarray(L.A).tobytes()).hexdigest()}


def main(argv):
    if argv[0] == "3d":
        out = HERE / "nd_survey_3d.jsonl"
        for i, e in enumerate(load_catalog("animals3D.json")):
            rec = {"source": "animals3D.json", "index": i, **run(e, 3, 64)}
            with out.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(rec["index"], rec["code"], rec["outcome"], rec["ncomp"], rec["travel_last20tu"], flush=True)
    else:
        stem = argv[1]
        out = HERE / "nd_survey_found.jsonl"
        F = load_found(stem)
        limit = int(argv[2]) if len(argv) > 2 else len(F)
        for i, e in enumerate(F[:limit]):
            rec = {"source": f"found/{stem}.json", "index": i, **run(e, 2, 256)}
            with out.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(stem, i, rec["code"], rec["outcome"], rec["ncomp"], rec["travel_last20tu"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
