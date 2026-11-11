"""WINGS-MC: knock out one chemical channel of Chan's three-channel "aquarium" creatures.

Creatures: found/233.json entries 0-11 (code 5N7KKM; 3 channels, 15 kernels, R 24). Upstream
executes them with dt = 1 / params[0].T = 1 (params[0] has T 1; the other kernels' T is unused).
Each creature is centred on a zero 256^2 torus and settled 20 time units under its rule. Then:
  control  : continue 200 time units
  ko<c>    : set channel c (0, 1, 2) to zero, continue 200 time units
  T10      : same rule with dt 0.1 (params[0].T = 10) from the catalogued cells, 220 time units
Outcome per arm: DIED (total mass < 1 % of mass at the knockout), FILLED (cover > 0.5), else
PERSISTED; plus per-channel mass at the end, components and centroid travel over the last 50 tu.
Writes mc_knockout.jsonl.

  python mc_knockout.py [first last]
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).parent))
from nd_lenia import NDLenia, entry_state, load_found
from nd_survey import centroid

HERE = Path(__file__).parent
N, SETTLE, TU, TAIL = 256, 20, 200, 50


def outcome(m0, A):
    cover = float((A.sum(0) > 0.1).mean())
    return ("DIED" if A.sum() < 0.01 * m0 else ("FILLED" if cover > 0.5 else "PERSISTED")), cover


def settled(i, T=None):
    e = load_found("233")[i]
    p, A = entry_state(e, 2, N)
    if T is not None:
        p = [dict(q) for q in p]
        p[0]["T"] = T
    L = NDLenia(p, A)
    for _ in range(int(SETTLE * p[0]["T"])):
        L.step()
    return e, p, L


def go(L, steps, T):
    cs = []
    for s in range(1, steps + 1):
        L.step()
        if s > steps - TAIL * T and s % int(T) == 0:
            cs.append(centroid(L.A.sum(0)))
    d = np.diff(np.array(cs), axis=0)
    d = (d + N / 2) % N - N / 2
    return float(np.sqrt((d.sum(0) ** 2).sum())) if len(d) else 0.0


def main(a, b):
    for i in range(a, b):
        for arm in ("control", "ko0", "ko1", "ko2", "T10"):
            T = 10 if arm == "T10" else None
            e, p, L = settled(i, T)
            if arm.startswith("ko"):
                L.A[int(arm[2])] = 0.0
            m0 = float(L.A.sum())
            Tn = p[0]["T"]
            travel = go(L, int(TU * Tn), Tn)
            out, cover = outcome(m0, L.A)
            rec = {"index": i, "code": e["code"], "name": e["name"], "arm": arm, "dt": 1 / Tn, "settle_tu": SETTLE, "tu": TU,
                   "mass_at_event": round(m0, 3), "mass_end": [round(float(x), 3) for x in L.A.sum(axis=(1, 2))],
                   "ncomp": int(ndimage.label(L.A.sum(0) > 0.1, structure=np.ones((3, 3)))[1]), "cover": round(cover, 4),
                   "travel_last50tu": round(travel, 2), "outcome": out,
                   "final_sha256": hashlib.sha256(np.ascontiguousarray(L.A).tobytes()).hexdigest()}
            with (HERE / "mc_knockout.jsonl").open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(i, e["name"], arm, out, rec["mass_end"], flush=True)


if __name__ == "__main__":
    args = [int(x) for x in sys.argv[1:]] or [0, 12]
    main(*args)
