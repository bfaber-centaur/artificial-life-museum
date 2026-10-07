#!/usr/bin/env python3
"""Reference reconstruction of specimen S001 (Orbium unicaudatus, code O2u).

Lane 1 (Reference Naturalist) artifact. This is a deliberately small, numpy-only
transcription of upstream Chakazul/Lenia `Python/LeniaND.py` 2-D semantics at
commit adfc542939266de7f4bb7ebb552e8499701ee107. It exists to pin down the
exact initial state and to show the catalog entry behaves as documented. It is
NOT the ALM simulator (that is Lane 2's `src/alm`), and should not be imported
by it: independent agreement is the evidence we want.

Usage (from repo root, after ./scripts/bootstrap.sh or an equivalent venv):

    python research/specimens/S001-orbium/reconstruct.py \
        --steps 2000 --size 128 --kernel poly --growth poly --sigma 0.015

Upstream line references are to .refs/Lenia/Python/LeniaND.py.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys

import numpy as np

LENIA_SHA = "adfc542939266de7f4bb7ebb552e8499701ee107"
ANIMALS_SHA256 = "09cf0a831c1ef8a73ebfaa9126257fbe076108362b706a98d88650ca9848d206"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ANIMALS = os.path.join(ROOT, ".refs", "Lenia", "Python", "animals.json")


# --- RLE decoding: Board.ch2val / Board.rle2arr (LeniaND.py:107-192), DIM=2 ---
def ch2val(c):
    if c in ".b":
        return 0
    if c == "o":
        return 255
    if len(c) == 1:
        return ord(c) - ord("A") + 1
    return (ord(c[0]) - ord("p")) * 24 + (ord(c[1]) - ord("A") + 25)


def rle2int(st):
    """Decode a 2-D Lenia RLE string to an integer array of levels 0..255.

    Upstream divides by 255 to get cell values; we keep integers so the state
    is exact. Rows are axis 0 (y), columns axis 1 (x). Short rows are
    right-padded with zeros (Board._recur_cubify)."""
    rows, row = [], []
    last, count = "", ""
    for ch in st.rstrip("!") + "$":
        if ch.isdigit():
            count += ch
        elif ch in "pqrstuvwxy@":
            last = ch
        else:
            tok = last + ch
            n = int(count) if count else 1
            if tok == "$":
                rows.append(row)
                rows.extend([[] for _ in range(n - 1)])
                row = []
            else:
                row.extend([ch2val(tok)] * n)
            last, count = "", ""
    width = max(len(r) for r in rows)
    return np.array([r + [0] * (width - len(r)) for r in rows], dtype=np.int64)


def load_catalog_entry(code):
    with open(ANIMALS, "rb") as f:
        raw = f.read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != ANIMALS_SHA256:
        sys.exit(f"animals.json sha256 {digest} != pinned {ANIMALS_SHA256}")
    entries = [e for e in json.loads(raw) if e.get("code") == code]
    if len(entries) != 1:
        sys.exit(f"expected exactly one entry with code {code}, found {len(entries)}")
    return entries[0]


# --- Kernel and growth: Automaton.kernel_core / growth_func / kernel_shell (LeniaND.py:271-319) ---
KERNEL_CORE = {
    "poly": lambda r: (4 * r * (1 - r)) ** 4,               # upstream index 0 == kn=1
    "exp": lambda r: np.exp(4 - 1 / (r * (1 - r))),          # upstream index 1 == kn=2
}
GROWTH = {
    "poly": lambda n, m, s: np.maximum(0, 1 - (n - m) ** 2 / (9 * s ** 2)) ** 4 * 2 - 1,  # gn=1
    "exp": lambda n, m, s: np.exp(-((n - m) ** 2) / (2 * s ** 2)) * 2 - 1,                # gn=2
}


def make_kernel_fft(size, R, b, core):
    mid = size // 2
    i = np.arange(size)
    X = (i[None, :] - mid) / R
    Y = (i[:, None] - mid) / R
    D = np.sqrt(X ** 2 + Y ** 2)
    B = len(b)
    Br = B * D
    bs = np.asarray(b, dtype=float)[np.minimum(np.floor(Br).astype(int), B - 1)]
    with np.errstate(divide="ignore", invalid="ignore"):
        k = (D < 1) * np.nan_to_num(KERNEL_CORE[core](np.minimum(Br % 1, 1))) * bs
    return np.fft.fft2(k / k.sum()), (X, Y)


def step(A, kfft, m, s, T, growth):
    # Automaton.calc_once (LeniaND.py:364-406), default flags: Euler, hard clip, no P quantization
    U = np.fft.fftshift(np.real(np.fft.ifft2(kfft * np.fft.fft2(A))))
    G = GROWTH[growth](U, m, s)
    return np.clip(A + G / T, 0, 1), G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", default="O2u")
    ap.add_argument("--size", type=int, default=128)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--kernel", choices=KERNEL_CORE, default="poly")
    ap.add_argument("--growth", choices=GROWTH, default="poly")
    ap.add_argument("--sigma", type=float, default=None, help="override catalog s")
    ap.add_argument("--mu", type=float, default=None, help="override catalog m")
    ap.add_argument("--every", type=int, default=10,
                    help="sampling interval; keep displacement per sample < size/2 or speed aliases")
    ap.add_argument("--out", default=None, help="directory for initial/final .npy and trace .csv")
    a = ap.parse_args()

    e = load_catalog_entry(a.code)
    p = e["params"]
    R, T = p["R"], p["T"]
    m = a.mu if a.mu is not None else p["m"]
    s = a.sigma if a.sigma is not None else p["s"]
    b = [float(Fraction(x)) for x in str(p["b"]).split(",")]  # Board.st2fracs
    cells = rle2int(e["cells"])

    A = np.zeros((a.size, a.size))
    h, w = cells.shape
    y0, x0 = (a.size - h) // 2, (a.size - w) // 2   # Board._recur_add, is_centered=True
    A[y0:y0 + h, x0:x0 + w] = cells / 255.0
    kfft, (X, Y) = make_kernel_fft(a.size, R, b, a.kernel)

    print(f"# {e['code']} {e['name']} R={R} T={T} m={m} s={s} b={b} kernel={a.kernel} growth={a.growth}")
    print(f"# cells {cells.shape} int-sum={int(cells.sum())} sha256(int16)={hashlib.sha256(cells.astype('<i2').tobytes()).hexdigest()[:16]}")
    print("step,mass,growth,gyradius,cx_wrapped,cy_wrapped,speed_since_last,alive")
    rows = []
    prev = None
    A0 = A.copy()
    for t in range(a.steps + 1):
        if t > 0:
            A, G = step(A, kfft, m, s, T, a.growth)
        if t % a.every == 0:
            mass = A.sum()
            alive = mass > 1e-10
            # Periodic centroid via circular mean (upstream uses a non-periodic
            # centroid plus auto-centering; this is a convenience, not a port).
            ang = 2 * np.pi * np.arange(a.size) / a.size
            cx = (np.angle((A.sum(0) * np.exp(1j * ang)).sum()) % (2 * np.pi)) * a.size / (2 * np.pi)
            cy = (np.angle((A.sum(1) * np.exp(1j * ang)).sum()) % (2 * np.pi)) * a.size / (2 * np.pi)
            # gyradius in R units about the periodic centroid
            dx = (np.arange(a.size)[None, :] - cx + a.size / 2) % a.size - a.size / 2
            dy = (np.arange(a.size)[:, None] - cy + a.size / 2) % a.size - a.size / 2
            gyr = np.sqrt(((dx ** 2 + dy ** 2) * A).sum() / mass) / R if alive else 0.0
            g = np.maximum(G, 0).sum() / R ** 2 if t > 0 else float("nan")
            if prev is not None:
                ddx = (cx - prev[0] + a.size / 2) % a.size - a.size / 2
                ddy = (cy - prev[1] + a.size / 2) % a.size - a.size / 2
                spd = np.hypot(ddx, ddy) / R / (a.every / T)   # kernel radii per unit time
            else:
                spd = float("nan")
            prev = (cx, cy)
            row = (t, mass / R ** 2, g, gyr, cx, cy, spd, int(alive))
            rows.append(row)
            print("%d,%.6f,%.6f,%.6f,%.3f,%.3f,%.6f,%d" % row)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        np.save(os.path.join(a.out, "initial.npy"), A0)
        np.save(os.path.join(a.out, "final.npy"), A)
        with open(os.path.join(a.out, "trace.csv"), "w") as f:
            f.write("step,mass,growth,gyradius,cx,cy,speed,alive\n")
            for r in rows:
                f.write("%d,%.6f,%.6f,%.6f,%.3f,%.3f,%.6f,%d\n" % r)


if __name__ == "__main__":
    main()
