"""KLEIN experiments (strange geometries round 3, claims C102-C104).

  python kb.py twist    -> twist.jsonl   C102: Orbium round the twist vs the same Orbium on a torus
  python kb.py narrow   -> narrow.jsonl  C103: narrowest bottle / torus an Orbium survives in
  python kb.py spin     -> spin.jsonl    C104: a spinner next to its own mirror image

Run from this folder with PYTHONPATH=../../../src.
"""
from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import klein as K  # noqa: E402
from alm import specimens  # noqa: E402
from alm.provenance import state_sha256  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ORBIUM_MASS = 73.5  # S001 settled sum(A), cells


def heading(d):
    return float(np.degrees(np.arctan2(-d[0], d[1])) % 360)  # chart angle, y up


# ---------------------------------------------------------------- C102 twist
def twist(k):
    """Orbium (S001 rotated k quarter turns) on the 128 x 128 Klein bottle, and the same seed on the
    128 x 256 torus (the bottle's double cover with only one animal in it). The bottle animal is
    followed on the cover; its path and mass are compared with the torus animal's."""
    s = specimens.load("S001")
    nx, ny = 128, 128
    seed = K.place(s.cells, (ny, nx), (ny // 2, nx // 2), k=k)
    kb = K.Klein(s.rule, seed)
    to = K.Torus(s.rule, np.vstack([seed, np.zeros_like(seed)]))
    shape = np.array([2 * ny, nx])
    pk = pt = K.centroid(seed)
    path_k, path_t = [np.zeros(2)], [np.zeros(2)]
    rows, crossings, last_half = [], 0, 0
    max_mass_diff = 0.0
    for t in range(1, 10001):
        kb.step()
        to.step()
        if t % 10:
            continue
        cs = [K.centroid(kb.full, m) for m, mm in K.bodies(kb.full) if mm > 0.5 * ORBIUM_MASS]
        ck = min(cs, key=lambda c: np.hypot(*K.wrap(c - pk, shape)))
        ct = K.centroid(to.A)
        path_k.append(path_k[-1] + K.wrap(ck - pk, shape))
        path_t.append(path_t[-1] + K.wrap(ct - pt, shape))
        # which half of the cover the followed animal is in: odd = it has crossed the twist an odd number of times
        half = int(ck[0] // ny)
        if half != last_half:
            crossings += 1
            last_half = half
        # compare the followed animal's neighbourhood with the torus animal's (same window, aligned by centroids)
        a = np.roll(kb.full, (int(round(ny - ck[0])), int(round(nx // 2 - ck[1]))), (0, 1))[ny - 40:ny + 40, nx // 2 - 40:nx // 2 + 40]
        b = np.roll(to.A, (int(round(ny - ct[0])), int(round(nx // 2 - ct[1]))), (0, 1))[ny - 40:ny + 40, nx // 2 - 40:nx // 2 + 40]
        max_mass_diff = max(max_mass_diff, abs(float(a.sum() - b.sum())))
        d = path_k[-1] - path_k[-2]
        # the chart (fundamental domain) sees the animal mirrored after an odd number of crossings
        chart_d = d * np.array([1, -1]) if half % 2 else d
        if t % 500 == 0:
            rows.append({"t": t, "crossings": crossings, "chart_heading_deg": heading(chart_d),
                         "cover_heading_deg": heading(d), "torus_heading_deg": heading(path_t[-1] - path_t[-2]),
                         "mass": float(a.sum())})
        pk, pt = ck, ct
    path_k, path_t = np.array(path_k), np.array(path_t)
    return {"exp": "twist", "k": k, "nx": nx, "ny": ny, "steps": 10000, "crossings": crossings,
            "max_path_diff_cells": float(np.abs(path_k - path_t).max()),
            "max_window_mass_diff": max_mass_diff,
            "distance_travelled_R": float(np.hypot(*np.diff(path_k, axis=0).T).sum() / 13),
            "rows": rows, "final_sha256": state_sha256(kb.A), "torus_final_sha256": state_sha256(to.A)}


# ---------------------------------------------------------------- C103 narrow
def classify(w, m0):
    """Outcome after 400 tu. Bodies are counted on the double cover for the bottle (its chart's
    top and bottom edges are glued with a flip, so the chart cuts bodies) and halved."""
    cover = 2 if w.kind == "klein" else 1
    bs = K.bodies(w.full, min_mass=0.2 * m0)
    m = float(w.full.sum()) / cover
    if m < 1:
        return "died"
    n = len(bs) // cover
    if n >= 1 and all(abs(mm - m0) < 0.1 * m0 for _, mm in bs):
        return "glider" if n == 1 else f"{n} gliders"
    if m > 5 * m0:
        return "filled"
    return "other"


def narrow(job):
    kind, ny, k, x0 = job
    s = specimens.load("S001")
    A = K.place(s.cells, (ny, 128), (ny // 2, x0), k=k)
    w = (K.Klein if kind == "klein" else K.Torus)(s.rule, A)
    ms = []
    for t in range(1, 4001):
        w.step()
        if t % 100 == 0:
            ms.append(round(float(w.A.sum()), 2))
            if ms[-1] < 1:
                break
    return {"exp": "narrow", "kind": kind, "ny": ny, "k": k, "x0": x0, "steps": t,
            "outcome": classify(w, ORBIUM_MASS), "mass_every_100": ms, "final_sha256": state_sha256(w.A)}


# ---------------------------------------------------------------- C104 spin
SPINNERS = {"PG1a": "Gyropteron arcus", "OG2g": "Gyrorbium gyrans"}


def spin(job):
    code, kind, ny_R = job
    sp = specimens.from_catalog(code)
    R = sp.rule.R
    ny, nx = int(round(ny_R * R)), 8 * R
    A = K.place(sp.cells, (ny, nx), (ny // 2, 0))
    w = (K.Klein if kind == "klein" else K.Torus)(sp.rule, A)
    shape = np.array(w.full.shape)
    m0 = float(A.sum())
    p, path, ms, turn = K.centroid(A), [np.zeros(2)], [], []
    steps = int(round(400 * sp.rule.T))
    end = "steps"
    for t in range(1, steps + 1):
        w.step()
        if t % 10:
            continue
        m = float(w.A.sum())
        ms.append(round(m, 2))
        if m < 1:
            end = "died"
            break
        cs = [K.centroid(w.full, mk) for mk, mm in K.bodies(w.full) if mm > 0.3 * m0]
        if not cs or m > 3 * m0:
            end = "grew" if m > 3 * m0 else "split"
            break
        c = min(cs, key=lambda c: np.hypot(*K.wrap(c - p, shape)))
        path.append(path[-1] + K.wrap(c - p, shape))
        p = c
    path = np.array(path)
    dt = 10 / sp.rule.T
    res = {"exp": "spin", "code": code, "name": SPINNERS[code], "kind": kind, "ny_R": ny_R, "ny": ny, "nx": nx,
           "end": end, "t_end": t / sp.rule.T, "mass0": m0, "mass_every_10_steps": ms[::10]}
    if end == "steps":
        h = len(path) // 4  # skip the first quarter
        d = np.diff(path[h:], axis=0)
        ang = np.unwrap(np.arctan2(-d[:, 0], d[:, 1]))
        res.update({"net_drift_R_per_tu": float(np.hypot(*(path[-1] - path[h])) / R / ((len(path) - 1 - h) * dt)),
                    "path_speed_R_per_tu": float(np.hypot(*d.T).mean() / R / dt),
                    "turn_deg_per_tu": float(np.degrees(ang[-1] - ang[0]) / ((len(path) - 1 - h) * dt)),
                    "max_excursion_R": float(np.hypot(*(path[h:] - path[h:].mean(0)).T).max() / R),
                    "final_sha256": state_sha256(w.A)})
    return res


def main():
    what = sys.argv[1]
    if what == "twist":
        jobs, fn = [0, 1], twist
    elif what == "narrow":
        jobs, fn = [(kind, ny, k, x0) for ny in range(18, 41) for k in range(4) for x0 in (0, 16, 32, 48)
                    for kind in ("klein", "torus")], narrow
    elif what == "spin":
        jobs, fn = [(c, kind, r) for c in SPINNERS for r in (1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8)
                    for kind in ("klein", "torus")], spin
    with Pool(int(os.environ.get("KLEIN_PROCS", 4))) as p, open(os.path.join(HERE, f"{what}.jsonl"), "w") as fh:
        for r in p.imap_unordered(fn, jobs, chunksize=1):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            print({k: v for k, v in r.items() if k not in ("rows", "mass_every_100", "mass_every_10_steps")}, flush=True)


if __name__ == "__main__":
    main()
