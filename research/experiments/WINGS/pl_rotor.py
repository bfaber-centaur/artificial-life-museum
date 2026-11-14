"""WINGS-PL: Particle Lenia (Mordvintsev, Niklasson & Randazzo 2022) at the paper's default
parameters (mu_k 4, sigma_k 1, w_k 0.022, mu_g 0.6, sigma_g 0.15, c_rep 1, dt 0.1).

200 particles uniform in [-6, 6]^2 from default_rng([19, k]). 20000 steps (2000 time units).
Arms:
  control  : untouched
  mirror   : at step 10000 replace x by -x (a mirror image of the same body)
  cull     : at step 10000 delete 50 particles chosen by default_rng([23, k])
  dt05     : dt 0.05, 40000 steps (numerical check)
Spin = mean over particles of the change in polar angle about the particle centroid, per 100 time
units, measured in windows of 100 time units. Also: radius of gyration and mean energy.
Writes pl_rotor.jsonl and states/pl_<arm>_<k>.npy (final positions).

  python pl_rotor.py [k ...]
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from other_worlds import ParticleLenia

HERE = Path(__file__).parent
TU_END, TU_EVENT, WIN = 2000, 1000, 100


def start(k):
    return np.random.default_rng([19, k]).uniform(-6, 6, (200, 2))


def angles(P):
    c = P.mean(0)
    return np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0])


def run(arm, k, keep_every=None):
    dt = 0.05 if arm == "dt05" else 0.1
    per = int(round(1 / dt))
    L = ParticleLenia(start(k), dt=dt)
    spins, rg, energy, frames = [], [], [], []
    prev = angles(L.P)
    for s in range(1, TU_END * per + 1):
        L.step()
        if s == TU_EVENT * per:
            if arm == "mirror":
                L.P[:, 0] *= -1
            elif arm == "cull":
                keep = np.sort(np.random.default_rng([23, k]).choice(len(L.P), len(L.P) - 50, replace=False))
                L.P = L.P[keep]
            prev = angles(L.P)
            continue
        if keep_every and s % keep_every == 0:
            frames.append(L.P.copy())
        if s % (WIN * per) == 0:
            a = angles(L.P)
            spins.append(float(np.angle(np.exp(1j * (a - prev))).mean()))
            prev = a
            c = L.P.mean(0)
            rg.append(float(np.sqrt(((L.P - c) ** 2).sum(1).mean())))
            energy.append(float(L.fields()[0].mean()))
    return L, spins, rg, energy, frames


def main(ks):
    for k in ks:
        for arm in ("control", "mirror", "cull", "dt05"):
            L, spins, rg, energy, _ = run(arm, k)
            rec = {"arm": arm, "k": k, "n_final": len(L.P), "dt": L.dt, "tu_end": TU_END, "tu_event": TU_EVENT,
                   "window_tu": WIN, "spin_rad_per_window": [round(x, 5) for x in spins],
                   "radius_gyration": [round(x, 4) for x in rg], "mean_energy": [round(x, 5) for x in energy],
                   "final_sha256": hashlib.sha256(np.ascontiguousarray(L.P).tobytes()).hexdigest()}
            np.save(HERE / "states" / f"pl_{arm}_{k}.npy", L.P)
            with (HERE / "pl_rotor.jsonl").open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(arm, k, [round(x, 3) for x in spins[::2]], flush=True)


if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]] or [0, 1, 2, 3, 4])
