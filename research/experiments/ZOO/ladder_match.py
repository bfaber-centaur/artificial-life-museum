"""Shape match between the fed arc after k meals and the catalogue Pteryx with the same segment count.

For k = 1..4 (P7al..P10al) and, as a control, the neighbouring rungs: rotate the fed arc's
141x141 window in 0.5 deg steps (scipy.ndimage.rotate, order 1), align centroids by FFT
cross-correlation, and report the best normalised correlation sum(a*b)/sqrt(sum a^2 sum b^2).
Writes ladder_match.json.

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/ladder_match.py
"""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
from atlas import base_body
from zoocore import components

HERE = Path(__file__).resolve().parent
codes = ["P6al", "P7al", "P8al", "P9al", "P10al"]
cat = {c: base_body("P", c)[0] for c in codes}


def ncc_best(a, b):
    best = 0.0
    fb = np.fft.rfft2(b)
    nb = np.sqrt((b ** 2).sum())
    for ang in np.arange(0, 360, 0.5):
        r = np.clip(ndimage.rotate(a, ang, reshape=False, order=1), 0, None)
        cc = np.fft.irfft2(np.fft.rfft2(r).conj() * fb, s=b.shape)  # all cyclic shifts
        v = cc.max() / (np.sqrt((r ** 2).sum()) * nb)
        if v > best:
            best, arg = v, ang
    return float(best), float(arg)


out = []
for k in range(1, 5):
    F = np.load(HERE / "states" / f"feed-altfilm-meal{k:02d}.npy")
    c = components(F, floor=30)[0]["c"]
    cy, cx = int(round(c[0])), int(round(c[1]))
    F = F[cy - 70:cy + 71, cx - 70:cx + 71]
    row = {"meals": k, "mass": round(float(F.sum()), 1)}
    for code in codes:
        row[code] = round(ncc_best(F, cat[code])[0], 4)
    out.append(row)
    print(row, flush=True)
(HERE / "ladder_match.json").write_text(json.dumps(out, indent=1) + "\n")
