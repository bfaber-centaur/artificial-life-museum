#!/usr/bin/env python3
"""HR-008: are the I001 and I003 lingering (edge) states the same state, and are they Orbium?

Best match over translations (FFT cross-correlation on the torus) and rotations (all angles in 2-deg
steps) of the saved aligned states, plus the unperturbed S001 control aligned the same way.
Reports the best normalized correlation and the residual relative L2 at that alignment, and the
mass / gyradius of each state.
Usage: PYTHONPATH=$L4/src python compare_states.py $L4
"""
import os
import sys

import numpy as np
from scipy import ndimage

L4 = sys.argv[1]
sys.path.insert(0, os.path.join(L4, "research", "experiments", "L4-001-disturbance-battery"))
import run as L4run  # noqa: E402
from alm import disturb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
step = L4run.engine("ref", 128, 13, 10)
A, prev = L4run.warm("ref", 128, 1000)
for _ in range(100):
    A = step(A)
B = step(A)
ctrl = L4run.aligned(B, disturb.frame_from(B, disturb.periodic_centroid(A)))  # heading from 1 step
S = {"I001": np.load(os.path.join(HERE, "edge-I001.npy")),
     "I003": np.load(os.path.join(HERE, "edge-I003.npy")), "control": ctrl}


def best(a, b):
    out = (-1, None, None)
    fa = np.fft.fft2(a - a.mean())
    for ang in range(-180, 180, 2):
        bb = ndimage.rotate(b, ang, reshape=False, order=1, mode="grid-wrap")
        cc = np.real(np.fft.ifft2(fa * np.conj(np.fft.fft2(bb - bb.mean()))))
        i = np.unravel_index(np.argmax(cc), cc.shape)
        c = cc[i] / (np.linalg.norm(a - a.mean()) * np.linalg.norm(bb - bb.mean()))
        if c > out[0]:
            sh = np.roll(bb, i, axis=(0, 1))
            out = (c, ang, np.linalg.norm(a - sh) / np.linalg.norm(a))
    return out


for k, X in S.items():
    c = disturb.periodic_centroid(X)
    print(f"{k}: mass {X.sum() / 169:.4f}, gyradius {disturb.gyradius(X, *c) / 13:.4f}")
ks = list(S)
for i in range(3):
    for j in range(i + 1, 3):
        c, ang, rl2 = best(S[ks[i]], S[ks[j]])
        print(f"{ks[i]} vs {ks[j]}: best corr {c:.4f} at rotation {ang} deg, rel L2 {rl2:.3f}")
