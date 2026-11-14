"""Track each aquarium creature alone for 300 tu: is its path straight, curved or still?"""
import sys, time, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "WINGS"))
from nd_lenia import NDLenia, entry_state, load_found
from zoocore import centroid, torus_delta
N = 256
es = load_found("233")[:12]
for i in [int(x) for x in sys.argv[1:]]:
    e = es[i]
    p, A = entry_state(e, 2, N)
    L = NDLenia(p, A)
    t = time.time()
    track = []
    for s in range(300):
        L.step()
        if s % 5 == 4:
            track.append(centroid(L.A.sum(0)))
    d = np.array([torus_delta(track[k], track[k + 1], (N, N)) for k in range(len(track) - 1)])
    path = np.cumsum(d, 0)
    sp = np.hypot(*d.T) / 5
    head = np.degrees(np.arctan2(-d[:, 0], d[:, 1]))
    print(i, e["name"], f"{time.time()-t:.0f}s mass {L.A.sum():.0f} speed mean {sp[10:].mean():.3f} c/tu",
          "net disp", np.round(path[-1], 1), "heading every 50tu", np.round(head[9::10]).tolist(), flush=True)
