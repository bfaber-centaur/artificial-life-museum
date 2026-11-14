"""GEOM-S: Orbium on a sphere (icosahedral geodesic grid, area-weighted kernel).

Subcommands
  meet       two S001 Orbia launched side by side and *parallel* (same heading, perpendicular
             offset `sep` R) on spheres of radius rho; on a flat world they never meet. Sweep
             rho x sep, record when they touch and what is left at the end. -> meet.jsonl
  flat       the same pairs on the flat square torus (alm.lenia.Lenia, FFT) as control -> flat.jsonl
  curvature  one Orbium on spheres of shrinking radius: when does curvature kill it? -> curvature.jsonl

Usage:  python sphere.py meet|flat|curvature
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomlenia as g  # noqa: E402
from alm import specimens  # noqa: E402
from alm.lenia import Lenia  # noqa: E402
from alm.provenance import state_sha256  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = 68.198
R = 13
S101_MASS = 0.8737  # S101 dossier: Synorbium ignis under the S001 rule, mass / R^2


def pair_seed(w, f, sep_R):
    """Two Orbia on the great circle x-z, both heading +y (parallel at launch), offset
    sep_R * R apart along the meridian. Returns A and the two start points."""
    rho = w.params["rho"]
    phi = sep_R * R / 2 / rho
    A = np.zeros(w.n)
    ps = []
    for sg in (1, -1):
        p = np.array([np.cos(phi), 0.0, sg * np.sin(phi)])
        A = np.maximum(A, g.seed_sphere(w, f, p, np.array([0, 1.0, 0]), HOME))
        ps.append(p)
    return A, ps


def describe(w, A):
    comps = g.components(w, A)
    out = []
    for m in comps:
        a = w.area[m]
        mm = float((A[m] * a).sum())
        if mm < 1:
            continue
        c = (A[m, None] * a[:, None] * w.xy[m]).sum(0)
        c /= np.linalg.norm(c)
        rho = w.params["rho"]
        d = rho * np.arccos(np.clip(w.xy[m] @ c / rho, -1, 1))
        gyr = float(np.sqrt((A[m] * a * d**2).sum() / mm))
        out.append({"mass_R2": mm / R**2, "gyradius_R": gyr / R, "centre": c.tolist()})
    return out


def meet(args):
    rho, sep_R, steps = args
    s = specimens.load("S001")
    f = g.patch_sampler(s.cells / 255.0)
    w = g.icosphere(rho)
    A, _ = pair_seed(w, f, sep_R)
    G = g.GraphLenia(w, s.rule, A)
    first_touch = None
    cent = []
    for t in range(1, steps + 1):
        G.step()
        if t % 10 == 0:
            n = len([c for c in describe(w, G.A)])
            if first_touch is None and n <= 1:
                first_touch = t
        if t > steps - 500 and t % 10 == 0:
            cent.append(g.sphere_centroid(w, G.A))
    cent = np.array(cent)
    ang = np.arccos(np.clip((cent[1:] * cent[:-1]).sum(1), -1, 1))
    speed = float(ang.mean() * rho / 10 * s.rule.T / R)  # R per tu, of the overall centroid
    bodies = describe(w, G.A)
    return {"rho": rho, "sep_R": sep_R, "steps": steps, "n_cells": w.n, "nu": w.params["nu"],
            "first_touch_step": first_touch,
            "geodesic_meet_step_estimate": None,
            "final_mass_R2": g.mass(w, G.A) / R**2, "bodies": bodies,
            "centroid_speed_R_per_tu_last500": speed,
            "final_sha256": state_sha256(G.A)}


def n_blobs(A, thr=0.1, link=2.5):
    """Blob count on the square torus with the same rule as geomlenia.components: cells above
    thr are linked when closer than `link` cells (periodic)."""
    w = g.square_torus(A.shape[0])
    return len(g.components(w, A.ravel(), thr, link))


def flat(args):
    sep_R, steps = args
    s = specimens.load("S001")
    N = 256
    A = np.zeros((N, N))
    h, wd = s.cells.shape
    # S001 heading 68.2 deg in (col, row); offset perpendicular to it
    th = np.radians(HOME)
    perp = np.array([-np.sin(th), np.cos(th)])  # (dx, dy) in (col, row)
    for sg in (0.5, -0.5):
        dx, dy = sg * sep_R * R * perp
        x0 = int(round(N / 2 + dx - wd / 2))
        y0 = int(round(N / 2 + dy - h / 2))
        A[y0:y0 + h, x0:x0 + wd] = np.maximum(A[y0:y0 + h, x0:x0 + wd], s.cells / 255.0)
    L = Lenia(s.rule, A)
    first_touch = None
    for t in range(1, steps + 1):
        L.step()
        if t % 10 == 0 and first_touch is None:
            if n_blobs(L.A) <= 1:
                first_touch = t
    n = n_blobs(L.A)
    return {"sep_R": sep_R, "N": N, "steps": steps, "first_touch_step": first_touch,
            "n_bodies_final": int(n), "final_mass_R2": float(L.A.sum() / R**2),
            "final_sha256": state_sha256(L.A)}


def curvature(args):
    rho, steps = args
    s = specimens.load("S001")
    f = g.patch_sampler(s.cells / 255.0)
    w = g.icosphere(rho)
    G = g.GraphLenia(w, s.rule, g.seed_sphere(w, f, np.array([1.0, 0, 0]), np.array([0, 1.0, 0]),
                                              HOME))
    ms, cent = [], []
    for t in range(1, steps + 1):
        G.step()
        if t % 10 == 0:
            ms.append(g.mass(w, G.A) / R**2)
            if ms[-1] > 0:
                cent.append(g.sphere_centroid(w, G.A))
    ms = np.array(ms)
    alive = bool(ms[-1] > 0.1)
    speed = None
    if alive and len(cent) > 50:
        c = np.array(cent[-50:])
        ang = np.arccos(np.clip((c[1:] * c[:-1]).sum(1), -1, 1))
        speed = float(ang.mean() * rho / 10 * s.rule.T / R)
    death = None if alive else int(10 * (np.argmax(ms < 0.01) + 1))
    return {"rho": rho, "rho_over_R": rho / R, "n_cells": w.n, "steps": steps, "alive": alive,
            "death_step": death, "mass_R2_last": float(ms[-1]),
            "mass_R2_mean_last1000": float(ms[-100:].mean()),
            "mass_R2_max": float(ms.max()), "speed_R_per_tu_last500": speed,
            "bodies": describe(w, G.A) if alive else [], "final_sha256": state_sha256(G.A)}


if __name__ == "__main__":
    what = sys.argv[1]
    procs = int(os.environ.get("GEOM_PROCS", 4))
    if what == "meet":
        jobs = [(rho, sep, 2000) for rho in (30, 40, 60, 80) for sep in (2, 3, 4, 6)]
        fn, out = meet, "meet.jsonl"
    elif what == "flat":
        jobs = [(sep, 2000) for sep in (2, 3, 4, 6)]
        fn, out = flat, "flat.jsonl"
    elif what == "curvature":
        jobs = [(rho, 3000) for rho in (5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 25)]
        fn, out = curvature, "curvature.jsonl"
    else:
        raise SystemExit(__doc__)
    jobs.sort(key=lambda j: -j[0])  # big ones first
    with Pool(procs) as p, open(os.path.join(HERE, out), "w") as fh:
        for r in p.imap_unordered(fn, jobs):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            print(json.dumps(r)[:300], flush=True)
