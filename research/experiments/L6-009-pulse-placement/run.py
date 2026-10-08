"""L6-009 runner (protocol.md in this directory; fixed before any run).

    python research/experiments/L6-009-pulse-placement/run.py
"""
import csv
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "L6-field"))
sys.path.insert(0, str(HERE.parent / "L6-008-pair-coupling"))
from disturb_helpers import offsets  # noqa: E402
from field import Batch, centroids, components, summarize  # noqa: E402
from run import HORIZON, MU, N, PHASES, R, SIGMA, T, WARM, WIN, units  # noqa: E402  (L6-008)

from alm import specimens  # noqa: E402

STRENGTHS = (0.2, 0.3)
FRACS = (0.0, 0.25, 0.5, 0.75, 1.0)
TRACK = 1000  # steps tracked in pair worlds (100 tu)
EVERY = 10


def pulse(shape, centre, s):
    dx, dy = offsets(shape, *centre)
    w = 0.25 * R
    return s * np.exp(-(dx**2 + dy**2) / (2 * w**2))


def frame(warm, ph):
    t = WARM + ph
    A = warm["states"][t][0]
    cx, cy = centroids(A[None])
    c = np.array([cx[0], cy[0]])
    v = warm["pos"][t, 0] - warm["pos"][t - 10, 0]
    h = v / np.hypot(*v)
    n = np.array([-h[1], h[0]])  # port normal, as in L6-008 (lat = dx * -hy + dy * hx)
    dx, dy = offsets(A.shape, *c)
    lat = dx * n[0] + dy * n[1]
    port = lat > 0
    lp = float((A * lat)[port].sum() / A[port].sum())
    return A, c, h, n, port, lp


def track(starts, heads):
    """Step pair worlds TRACK steps; every EVERY steps record mass, components and lateral spread.
    Same update as field.Batch (FFT convolution, poly growth, Euler + clip)."""
    from alm.lenia import Rule, growth, kernel
    B = np.array(starts, dtype=np.float64)
    W, ny, nx = B.shape
    khat = np.fft.rfft2(kernel((ny, nx), Rule(R=R, T=T, mu=MU, sigma=SIGMA, kernel="poly", growth="poly")))
    rows = []
    for t in range(TRACK + 1):
        if t:
            U = np.fft.irfft2(np.fft.rfft2(B) * khat, s=(ny, nx))
            B = np.clip(B + growth("poly", U, MU, SIGMA) * (1.0 / T), 0.0, 1.0)
        if t % EVERY:
            continue
        cx, cy = centroids(B)
        for i in range(W):
            A = B[i]
            m = A.sum() / R**2
            if m <= 0 or np.isnan(cx[i]):
                rows.append((i, t, m, 0, float("nan")))
                continue
            dx, dy = offsets(A.shape, cx[i], cy[i])
            lat = dx * heads[i][0] + dy * heads[i][1]
            rows.append((i, t, m, components(A), float(np.sqrt((A * lat**2).sum() / A.sum()))))
    return rows


def main():
    S = specimens.load("S101")
    warm = Batch(R, T, [MU], [SIGMA]).run(S.place(N)[None], WARM + max(PHASES), snap_every=10**9,
                                         keep=tuple(WARM + p for p in PHASES))
    jobs, starts = [], []
    tstarts, theads, tmeta = [], [], []
    for ph in PHASES:
        A, c, h, n, port, lp = frame(warm, ph)
        tstarts.append(A)
        theads.append(n)
        tmeta.append(("none", 0.0, 0.0, ph))
        for s in STRENGTHS:
            for f in FRACS:
                G = pulse(A.shape, c + R * h + f * lp * n, s)
                E = np.clip(A + G, 0, 1)
                starts += [E, np.clip(np.where(port, A, 0.0) + G, 0, 1), np.clip(np.where(port, 0.0, A) + G, 0, 1)]
                jobs.append((s, f, ph, lp))
                tstarts.append(E)
                theads.append(n)
                tmeta.append(("pulse", s, f, ph))
    t0 = time.time()
    outs = []
    for k in range(0, len(starts), 50):
        B = np.array(starts[k : k + 50])
        res = Batch(R, T, [MU] * len(B), [SIGMA] * len(B)).run(B, HORIZON, snap_every=50, snap_from=HORIZON - WIN)
        outs += [(d, res["final"][i]) for i, d in enumerate(summarize(res, R, T, WIN))]
        print(f"{k + len(B)}/{len(starts)} {time.time() - t0:.0f}s", flush=True)
    rows = []
    for j, (s, f, ph, lp) in enumerate(jobs):
        (dp, Fp), (da, Fa), (db, Fb) = outs[3 * j : 3 * j + 3]
        n_pair, n_port, n_stb = units(dp, Fp), units(da, Fa), units(db, Fb)
        both = isinstance(n_port, int) and isinstance(n_stb, int)
        drag = both and ((isinstance(n_pair, int) and n_pair < n_port + n_stb) or
                         (n_pair == "other" and n_port + n_stb == 2))
        rows.append({"s": s, "f": f, "phase": ph, "t0": WARM + ph, "l_port": round(lp, 3),
                     "n_pair": n_pair, "n_port_full": n_port, "n_starboard_full": n_stb, "drag_down": drag,
                     "pair_mass": round(dp["mass_mean"], 5), "pair_fate": dp["fate"]})
    with open(HERE / "placement.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    trows = track(tstarts, theads)
    with open(HERE / "tracks.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["kind", "s", "f", "phase", "step", "mass", "components", "sigma_lat"])
        for i, t, m, nc, sl in trows:
            w.writerow([*tmeta[i], t, f"{m:.5g}", nc, f"{sl:.4g}"])
    print("wrote placement.csv and tracks.csv", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
