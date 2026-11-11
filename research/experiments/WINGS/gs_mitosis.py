"""WINGS-GS: dividing spots in Gray-Scott reaction-diffusion (Pearson 1993), with an intervention.

Specimen GS-1: one spot at F 0.0367, k 0.0649 (Pearson's dividing-spot regime), Du 0.2, Dv 0.1,
grown from a 10x10 seed (u 0.5, v 0.25 + uniform(0, 0.01) noise from default_rng([11, seed]))
in the centre of a 256^2 torus of u 1, v 0.

Arms (all 40000 steps at dt 1, i.e. 40000 time units; dt 0.5 arm runs 80000 half-steps):
  control      : untouched
  wipe         : at t = 20000 reset the left half (x < 128) to u 1, v 0
  control-dt05 : control with dt 0.5 (numerical check)
Spots = 8-connected components of v > 0.2, counted every 500 time units.
Writes gs_mitosis.jsonl (one row per arm and seed) and states/gs_<arm>_<seed>.npy (final v).

  python gs_mitosis.py [seeds...]
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
from other_worlds import GrayScott  # noqa: E402

HERE = Path(__file__).parent
N, F, K = 256, 0.0367, 0.0649
T_END, T_WIPE, EVERY = 40000, 20000, 500


def seed_state(seed, n=N):
    rng = np.random.default_rng([11, seed])
    u = np.ones((n, n)); v = np.zeros((n, n))
    c = n // 2
    u[c - 5:c + 5, c - 5:c + 5] = 0.5
    v[c - 5:c + 5, c - 5:c + 5] = 0.25 + rng.uniform(0, 0.01, (10, 10))
    return u, v


def spots(v):
    return int(ndimage.label(v > 0.2, structure=np.ones((3, 3)))[1])


def run(arm, seed, frames=None, frame_every=None):
    u, v = seed_state(seed)
    dt = 0.5 if arm.endswith("dt05") else 1.0
    G = GrayScott(F, K, u, v, dt=dt)
    per = int(round(1 / dt))
    counts, left = [], []
    for s in range(int(T_END * per) + 1):
        t = s / per
        if arm == "wipe" and s == T_WIPE * per:
            G.u[:, : N // 2] = 1.0
            G.v[:, : N // 2] = 0.0
        if s % (EVERY * per) == 0:
            counts.append(spots(G.v))
            left.append(spots(G.v[:, : N // 2 - 8]))
        if frames is not None and s % (frame_every * per) == 0:
            frames.append(G.v.astype(np.float32).copy())
        if s < T_END * per:
            G.step()
    return G, counts, left


def main(seeds):
    out = HERE / "gs_mitosis.jsonl"
    (HERE / "states").mkdir(exist_ok=True)
    for seed in seeds:
        for arm in ("control", "wipe", "control-dt05"):
            G, counts, left = run(arm, seed)
            rec = {"arm": arm, "seed": seed, "F": F, "k": K, "Du": G.Du, "Dv": G.Dv, "dt": G.dt, "N": N,
                   "t_end": T_END, "t_wipe": T_WIPE if arm == "wipe" else None, "every": EVERY,
                   "spots": counts, "spots_left_half": left,
                   "final_v_sha256": hashlib.sha256(np.ascontiguousarray(G.v).tobytes()).hexdigest()}
            np.save(HERE / "states" / f"gs_{arm}_{seed}.npy", G.v.astype(np.float32))
            with out.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(arm, seed, counts[::8], flush=True)


if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]] or [0, 1])
