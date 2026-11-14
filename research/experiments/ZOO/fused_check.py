"""Are the fused two-lobed gliders of the Orbium atlas (C080 FUSE) the S101 bound pair?

For every FUSE row of atlas-O.jsonl: replay the collision (checking the row's hash at its
classification time), continue to contact + 300 tu, then measure over the last 50 tu the mass
(sum A / R^2), gyradius (R) and speed (R / tu), and the best normalised correlation of the
body against settled S101 over rotations (1 deg) and all shifts. S101 is settled 500 tu alone on
the same 384^2 torus. Writes fused_check.json.

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/fused_check.py
"""

from __future__ import annotations

import json
import math
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy import ndimage

from alm.lenia import Lenia
from alm.specimens import load
from atlas import WORLDS, body
from zoocore import centroid, components, crop, place_pair, sha, torus_delta

HERE = Path(__file__).resolve().parent
W = WORLDS["O"]
RULE, N, R = W["rule"], W["N"], W["rule"].R


def stats(L, tu=50):
    ms, gs, cs = [], [], []
    for s in range(tu * RULE.T):
        L.step()
        if s % RULE.T == 0:
            A = L.A
            c = centroid(A)
            cs.append(c)
            ms.append(A.sum() / R**2)
            yy, xx = np.indices(A.shape)
            dy = (yy - c[0] + N / 2) % N - N / 2
            dx = (xx - c[1] + N / 2) % N - N / 2
            gs.append(math.sqrt((A * (dy**2 + dx**2)).sum() / A.sum()) / R)
    d = sum(np.hypot(*torus_delta(cs[i], cs[i + 1], (N, N))) for i in range(len(cs) - 1))
    return float(np.mean(ms)), float(np.mean(gs)), float(d / (len(cs) - 1) / R)


def ncc_best(a, b):
    fb = np.fft.rfft2(b)
    nb = np.sqrt((b**2).sum())
    best = 0.0
    for ang in np.arange(0, 360, 1.0):
        r = np.clip(ndimage.rotate(a, ang, reshape=False, order=1), 0, None)
        cc = np.fft.irfft2(np.fft.rfft2(r).conj() * fb, s=b.shape)
        best = max(best, float(cc.max() / (np.sqrt((r**2).sum()) * nb)))
    return best


def s101_ref():
    L = Lenia(RULE, load("S101").place(N))
    for _ in range(500 * RULE.T):
        L.step()
    patch = crop(L.A, components(L.A, floor=20)[0]["c"], 30)
    m, g, v = stats(L)
    return patch, m, g, v


def one(r):
    A = body("O", "O2u", 0.0)
    B = body("O", "O2u", A.heading + r["theta"])
    A0, info = place_pair(A, B, r["b_R"], R, N)
    L = Lenia(RULE, A0)
    k_check = int(round(r["tu"] * RULE.T))
    total = int(round((info["tc"] + 300) * RULE.T))
    ok = None
    for s in range(1, total + 1):
        L.step()
        if s == k_check:
            ok = sha(L.A) == r["final_sha256"]
    cs = components(L.A, floor=20)
    patch = crop(L.A, cs[0]["c"], 30) if cs else None
    m, g, v = stats(L)
    return {"theta": r["theta"], "b_R": r["b_R"], "replay_ok": ok, "n_bodies": len(cs),
            "mass_R2": round(m, 4), "gyradius_R": round(g, 4), "speed_R_tu": round(v, 4), "patch": patch}


if __name__ == "__main__":
    rows = [json.loads(l) for l in (HERE / "atlas-O.jsonl").read_text().splitlines()]
    fused = [r for r in rows if r["class"] == "FUSE"]
    with Pool(4) as pool:
        ref = pool.apply_async(s101_ref)
        res = pool.map(one, fused)
        rp, rm, rg, rv = ref.get()
    out = {"S101": {"mass_R2": round(rm, 4), "gyradius_R": round(rg, 4), "speed_R_tu": round(rv, 4)}, "fused": []}
    for x in res:
        p = x.pop("patch")
        x["ncc_vs_S101"] = round(ncc_best(p, rp), 4) if p is not None else None
        out["fused"].append(x)
        print(x, flush=True)
    print("S101", out["S101"])
    (HERE / "fused_check.json").write_text(json.dumps(out, indent=1) + "\n")
