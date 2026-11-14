"""WINGS-SL: a SmoothLife glider (rule SL-32 from sl_scan.py: default_rng([13, 32])).

Specimen: the 40x40 window centred on cell (116, 167) of the sl_scan rule-32 world at step 1500
(states/sl_32.npy; rebuilt from scratch by `glider_patch()`), pasted into a zero 192^2 torus.
Arms (1000 time units each):
  dt10   : dt 0.1 (the scout's step)
  dt05   : dt 0.05
  dt025  : dt 0.025
  res2   : radii doubled (ra 2x), patch upsampled 2x (scipy.ndimage.zoom, order 1), 384^2, dt 0.1
  ring   : dt 0.1, plus the still ring from the same scout world (window centred on (38, 52))
           placed 60 cells ahead of the glider on its path
Track: components of A > 0.5; glider centroid every 10 time units; mass.
Writes sl_glider.jsonl.

  python sl_glider.py [arm ...]
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).parent))
from other_worlds import SmoothLife
import sl_scan

HERE = Path(__file__).parent
TU = 1000


def rule():
    prm, _ = sl_scan.draw(32)
    return prm


def scout_world():
    prm, A = sl_scan.draw(32)
    S = SmoothLife(A, **prm)
    for _ in range(sl_scan.STEPS):
        S.step()
    return S.A


def window(A, cy, cx, w=20):
    n = A.shape[0]
    return np.roll(A, (n // 2 - cy, n // 2 - cx), (0, 1))[n // 2 - w:n // 2 + w, n // 2 - w:n // 2 + w].copy()


def build(arm):
    W = scout_world()
    g = window(W, 116, 167)
    prm = rule()
    n, dt = 192, 0.1
    if arm == "dt05":
        dt = 0.05
    if arm == "dt025":
        dt = 0.025
    if arm == "res2":
        g = np.clip(ndimage.zoom(g, 2, order=1), 0, 1)
        n = 384
        prm = {**prm, "ra": prm["ra"] * 2}
    A = np.zeros((n, n))
    h = g.shape[0] // 2
    c = n // 2
    A[c - h:c + h, c - h:c + h] = g
    if arm == "ring":
        r = window(W, 38, 52)
        A[c - 20:c + 20, c + 60 - 20:c + 60 + 20] = np.maximum(A[c - 20:c + 20, c + 40:c + 80], r)
    return SmoothLife(A, dt=dt, **prm)


def run(arm, frames=None, frame_every_tu=None):
    S = build(arm)
    per = int(round(1 / S.dt))
    A0 = S.A.copy()
    track = []
    for s in range(TU * per + 1):
        if s % (10 * per) == 0:
            lab, k = ndimage.label(S.A > 0.5)
            cs = [tuple(round(float(v), 2) for v in x) for x in ndimage.center_of_mass(S.A, lab, range(1, k + 1))] if k else []
            track.append({"t": s // per, "ncomp": int(k), "centroids": cs, "mass": round(float(S.A.sum()), 3)})
        if frames is not None and s % (frame_every_tu * per) == 0:
            frames.append(S.A.astype(np.float32).copy())
        if s < TU * per:
            S.step()
    return S, A0, track


def main(arms):
    for arm in arms:
        S, A0, track = run(arm)
        rec = {"arm": arm, "rule": {k: getattr(S, k) for k in ("ra", "ri", "b1", "b2", "d1", "d2", "alpha_n", "alpha_m", "dt", "mode")},
               "N": S.A.shape[0], "tu": TU, "track": track,
               "initial_sha256": hashlib.sha256(np.ascontiguousarray(A0).tobytes()).hexdigest(),
               "final_sha256": hashlib.sha256(np.ascontiguousarray(S.A).tobytes()).hexdigest()}
        with (HERE / "sl_glider.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(arm, [(x["t"], x["ncomp"]) for x in track[::10]], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or ["dt10", "dt05", "dt025", "res2", "ring"])
