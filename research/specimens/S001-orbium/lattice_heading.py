#!/usr/bin/env python3
"""Lane 1 side observation: does Orbium's mass 'oscillation' track its heading relative to the grid?

Run from repo root: python research/specimens/S001-orbium/lattice_heading.py
Rotates the O2u catalog state (bilinear, clipped), runs 3000 steps at the catalog
rule (poly/poly, R=13, T=10, m=0.15, s=0.015, 128x128 torus) and compares the
dominant period of total mass over steps 1000..2999 with the predicted
column/row crossing periods 1/|vx|, 1/|vy| (cells/step).
"""
import os
import sys

import numpy as np
import scipy.ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reconstruct as rc  # noqa: E402

N = 128
e = rc.load_catalog_entry("O2u")
c = rc.rle2int(e["cells"]) / 255
k, _ = rc.make_kernel_fft(N, 13, [1.0], "poly")
ang = 2 * np.pi * np.arange(N) / N


def centroid(A):
    return [(np.angle((A.sum(ax) * np.exp(1j * ang)).sum()) % (2 * np.pi)) * N / (2 * np.pi) for ax in (0, 1)]


for rot in (0, 23, 45):
    z = np.clip(scipy.ndimage.rotate(c, rot, order=1, reshape=True), 0, 1)
    A = np.zeros((N, N))
    h, w = z.shape
    A[(N - h) // 2:(N - h) // 2 + h, (N - w) // 2:(N - w) // 2 + w] = z
    ms, cs = [], []
    for t in range(3000):
        A, _ = rc.step(A, k, 0.15, 0.015, 10, "poly")
        if t >= 1000:
            ms.append(A.sum())
            cs.append(centroid(A))
    cs = np.array(cs)
    d = np.diff(np.unwrap(cs * 2 * np.pi / N, axis=0), axis=0) * N / (2 * np.pi)
    vx, vy = d.mean(0)
    m = np.array(ms) - np.mean(ms)
    P = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m))
    i = np.argmax(P[1:]) + 1
    print(f"rot {rot:3d}: alive={A.sum() > 1} heading {np.degrees(np.arctan2(vy, vx)):6.1f} deg, "
          f"speed {np.hypot(vx, vy):.4f} cells/step, mass sd/mean {np.std(ms) / np.mean(ms):.2e}, "
          f"dominant mass period {1 / f[i]:.2f} steps; crossing periods 1/|vx|={1 / abs(vx):.2f}, 1/|vy|={1 / abs(vy):.2f}")
