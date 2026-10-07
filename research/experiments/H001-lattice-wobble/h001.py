#!/usr/bin/env python3
"""H001: is S001's mass wobble a lattice artifact? (Lane 7, hostile review)

Protocol: see PREREGISTRATION.md in this directory (committed before any run).
Semantics come from research/specimens/S001-orbium/reconstruct.py (Lane 1 reference).

Usage (repo root):
    .venv/bin/python research/experiments/H001-lattice-wobble/h001.py e1 > research/experiments/H001-lattice-wobble/e1.csv
    .venv/bin/python research/experiments/H001-lattice-wobble/h001.py e2 > research/experiments/H001-lattice-wobble/e2.csv
"""
import os
import sys

import numpy as np
import scipy.ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "specimens", "S001-orbium"))
import reconstruct as rc  # noqa: E402

MU, SIGMA, T = 0.15, 0.015, 10
TOL = 0.002  # cycles/step, preregistered


def grid_size(R):
    N = int(round(128 * R / 13))
    return N + (N % 2)


def initial_state(R, rot, N):
    c = rc.rle2int(rc.load_catalog_entry("O2u")["cells"]) / 255.0
    if R != 13:
        c = np.clip(scipy.ndimage.zoom(c, R / 13, order=1), 0, 1)
    if rot:
        c = np.clip(scipy.ndimage.rotate(c, rot, order=1, reshape=True), 0, 1)
    A = np.zeros((N, N))
    h, w = c.shape
    A[(N - h) // 2:(N - h) // 2 + h, (N - w) // 2:(N - w) // 2 + w] = c
    return A


def centroid(A, N):
    ang = 2 * np.pi * np.arange(N) / N
    return np.array([(np.angle((A.sum(ax) * np.exp(1j * ang)).sum()) % (2 * np.pi)) * N / (2 * np.pi)
                     for ax in (0, 1)])  # (cx, cy)


def run(R, rot=0.0, steps=3000, start=1000, N=None):
    """Return (mass series, centroid series) over steps start..steps-1, plus final alive flag."""
    N = N or grid_size(R)
    A = initial_state(R, rot, N)
    kfft, _ = rc.make_kernel_fft(N, R, [1.0], "poly")
    ms, cs = [], []
    for t in range(steps):
        A, _ = rc.step(A, kfft, MU, SIGMA, T, "poly")
        if t >= start:
            ms.append(A.sum())
            cs.append(centroid(A, N))
    return np.array(ms), np.array(cs), N


def velocity(cs, N):
    d = np.diff(np.unwrap(cs * 2 * np.pi / N, axis=0), axis=0) * N / (2 * np.pi)
    return d.mean(0)  # (vx, vy) cells/step


def dominant_freq(m):
    x = (m - m.mean()) * np.hanning(len(m))
    P = np.abs(np.fft.rfft(x)) ** 2
    i = int(np.argmax(P[1:])) + 1
    if 1 <= i < len(P) - 1:  # parabolic refinement on log power
        a, b, c = np.log(P[i - 1:i + 2] + 1e-300)
        i = i + 0.5 * (a - c) / (a - 2 * b + c)
    return i / len(m)


def fold(f):
    f = np.abs(f) % 1.0
    return np.minimum(f, 1.0 - f)


def lattice_lines(vx, vy, kmax=2):
    out = []
    for m in range(-kmax, kmax + 1):
        for n in range(-kmax, kmax + 1):
            if (m, n) != (0, 0):
                out.append(((m, n), fold(m * vx + n * vy)))
    return out


def nearest_line(f, vx, vy):
    lines = lattice_lines(vx, vy)
    (mn, fl) = min(lines, key=lambda x: abs(x[1] - f))
    return mn, fl, abs(fl - f)


def chance_coverage(vx, vy, tol=TOL):
    """Fraction of [0, 0.5] within tol of some lattice line (exact interval union)."""
    iv = sorted((max(0, fl - tol), min(0.5, fl + tol)) for _, fl in lattice_lines(vx, vy))
    tot, cur_a, cur_b = 0.0, None, None
    for a, b in iv:
        if cur_b is None or a > cur_b:
            if cur_b is not None:
                tot += cur_b - cur_a
            cur_a, cur_b = a, b
        else:
            cur_b = max(cur_b, b)
    tot += cur_b - cur_a
    return tot / 0.5


def analyse(R, rot):
    ms, cs, N = run(R, rot)
    vx, vy = velocity(cs, N)
    f = dominant_freq(ms)
    mn, fl, err = nearest_line(f, vx, vy)
    return dict(R=R, rot=rot, N=N, alive=int(ms[-1] > 1),
                mass_norm=ms.mean() / R ** 2, rel_sd=ms.std() / ms.mean(),
                vx=vx, vy=vy, speed=np.hypot(vx, vy), heading=np.degrees(np.arctan2(vy, vx)),
                f_peak=f, period=1 / f, line_m=mn[0], line_n=mn[1], f_line=fl, err=err,
                match=int(err <= TOL), chance=chance_coverage(vx, vy))


COLS = ["R", "rot", "N", "alive", "mass_norm", "rel_sd", "vx", "vy", "speed", "heading",
        "f_peak", "period", "line_m", "line_n", "f_line", "err", "match", "chance"]


def emit(rows):
    print(",".join(COLS))
    for r in rows:
        print(",".join(f"{r[c]:.6g}" if isinstance(r[c], float) else str(r[c]) for c in COLS), flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "e1"
    if which == "e1":
        emit(analyse(R, 0) for R in (13, 20, 26, 39))
    elif which == "e2":
        emit(analyse(13, rot) for rot in range(0, 46, 3))
    else:
        sys.exit("usage: h001.py e1|e2")
