"""L6-009 exploratory follow-up (added after the main results were read, NOT pre-registered).

At f = 0 the pulse split the pair into two free Orbia that later collided on the 128² torus. This
reruns every s 0.2/0.3, f 0 and 0.25 pair world on a 256² torus (the same edited state, centred
and zero-padded), 300 tu, and writes bigworld.csv with L6-008's units() outcome.

    python research/experiments/L6-009-pulse-placement/followup_bigworld.py
"""
import csv
import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("l6009", HERE / "run.py")
l9 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l9)

from alm import specimens  # noqa: E402

NB = 256


def main():
    S = specimens.load("S101")
    warm = l9.Batch(l9.R, l9.T, [l9.MU], [l9.SIGMA]).run(
        S.place(l9.N)[None], l9.WARM + max(l9.PHASES), snap_every=10**9,
        keep=tuple(l9.WARM + p for p in l9.PHASES))
    starts, meta = [], []
    for ph in l9.PHASES:
        A, c, h, n, port, lp = l9.frame(warm, ph)
        for s in l9.STRENGTHS:
            for f in (0.0, 0.25):
                E = np.clip(A + l9.pulse(A.shape, c + l9.R * h + f * lp * n, s), 0, 1)
                E = np.roll(E, (l9.N // 2 - int(round(c[1])), l9.N // 2 - int(round(c[0]))), (0, 1))
                Bg = np.zeros((NB, NB))
                o = (NB - l9.N) // 2
                Bg[o:o + l9.N, o:o + l9.N] = E
                starts.append(Bg)
                meta.append((s, f, ph))
    res = l9.Batch(l9.R, l9.T, [l9.MU] * len(starts), [l9.SIGMA] * len(starts)).run(
        np.array(starts), l9.HORIZON, snap_every=50, snap_from=l9.HORIZON - l9.WIN)
    rows = []
    for (s, f, ph), d, F in zip(meta, l9.summarize(res, l9.R, l9.T, l9.WIN), res["final"]):
        rows.append({"s": s, "f": f, "phase": ph, "N": NB, "n_pair": l9.units(d, F),
                     "mass": round(float(d["mass_mean"]), 5), "fate": d["fate"]})
        print(rows[-1], flush=True)
    with open(HERE / "bigworld.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
