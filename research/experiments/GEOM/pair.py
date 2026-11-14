"""GEOM-P: do Orbia travel along geodesics? Track two parallel Orbia on curved worlds and compare
their separation with the geodesic prediction.

Two S001 Orbia start a = sep R apart, both heading perpendicular to the geodesic joining them
("parallel"). For two geodesics that leave a common perpendicular at distance a, after each has
travelled arc length s:

    flat:        d = a
    sphere:      sin(d / 2 rho)    = sin(a / 2 rho)    cos(s / rho)      (they meet at s = pi rho / 2)
    hyperbolic:  sinh(d / 2 kappa) = sinh(a / 2 kappa) cosh(s / kappa)

The run measures d (geodesic distance between the two halves' mass centres; the halves are
z > 0 / z < 0 on the sphere and y > 0 / y < 0 on the disk, which the pair never crosses before
contact) and s, every 10 steps, and evaluates the prediction with a = the seeded separation
(the two seed points lie on a common perpendicular, so the pair starts exactly parallel) and
s = s0 + accumulated geodesic path of each centre after SETTLE steps, where s0 is the distance
from each seed point to its centre at SETTLE (the animals have already moved about 1 R by then).

Usage:  python pair.py run                      -> pair.jsonl (all 15 runs)
        python pair.py one hyperbolic 26 3      -> appends one run to pair.jsonl
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomlenia as g  # noqa: E402
from alm import specimens  # noqa: E402
from alm.provenance import state_sha256  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HOME, R = 68.198, 13
SETTLE = 20  # steps; a and s are measured from here


def predict(kind, a, s, L):
    if kind == "sphere":
        return 2 * L * np.arcsin(np.clip(np.sin(a / 2 / L) * np.cos(s / L), -1, 1))
    return 2 * L * np.arcsinh(np.sinh(a / 2 / L) * np.cosh(s / L))


def sphere_pts(w, A, mask):
    a = A * w.area * mask
    c = (a[:, None] * w.xy).sum(0)
    n = np.linalg.norm(c)
    return c / n if n > 0 else None


def run(job):
    kind, L, sep, steps = job
    s = specimens.load("S001")
    f = g.patch_sampler(s.cells / 255.0)
    if kind == "sphere":
        w = g.icosphere(L)
        phi = sep * R / 2 / L
        A = np.zeros(w.n)
        for sg in (1, -1):
            A = np.maximum(A, g.seed_sphere(w, f, np.array([np.cos(phi), 0, sg * np.sin(phi)]),
                                            np.array([0, 1.0, 0]), HOME))
        masks = (w.xy[:, 2] > 0, w.xy[:, 2] < 0)
        seeds = [np.array([np.cos(phi), 0, sg * np.sin(phi)]) for sg in (1, -1)]

        def centres(A):
            return [sphere_pts(w, A, m) for m in masks]

        def dist(p, q):
            return L * np.arccos(np.clip(p @ q, -1, 1))
    else:
        rmax = {26: 4.0, 39: 3.0}[L] * L
        w = g.hyper_grid(L, rmax)
        yy = np.tanh(sep * R / 2 / L / 2)
        A = np.maximum(g.seed_disk(w, f, 1j * yy, 0.0), g.seed_disk(w, f, -1j * yy, 0.0))
        masks = (w.xy[:, 1] > 0, w.xy[:, 1] < 0)
        seeds = [np.array([0.0, yy]), np.array([0.0, -yy])]

        def centres(A):
            out = []
            for m in masks:
                if (A * m).sum() < 1:
                    out.append(None)
                    continue
                c = g.disk_centroid(w, A, m)
                out.append(np.array([c.real, c.imag]))
            return out

        def dist(p, q):
            return float(g.hyp_dist(p, q, L))
    G = g.GraphLenia(w, s.rule, A)
    rows, prev, path = [], None, np.zeros(2)
    a = None
    for t in range(0, steps + 1):
        if t % 10 == 0 and t >= SETTLE:
            cs = centres(G.A)
            if any(c is None for c in cs):
                break
            if prev is None:
                path += [dist(cs[k], seeds[k]) for k in range(2)]  # s0
            else:
                path += [dist(cs[k], prev[k]) for k in range(2)]
            prev = cs
            d = dist(cs[0], cs[1])
            if a is None:
                a = sep * R
            sbar = float(path.mean())
            ml = g.mass(w, G.A)
            rows.append({"t": t, "d": d, "s": sbar, "pred": float(predict(kind, a, sbar, L)),
                         "mass_R2": ml / R**2})
            if kind == "sphere" and d < 1.6 * R:  # bodies touch: stop comparing
                break
            if kind == "hyperbolic":
                r0 = [float(g.hyp_dist(c, np.zeros(2), L)) for c in cs]
                if max(r0) > rmax - 1.5 * R:  # near the absorbing rim
                    break
        G.step()
    d = np.array([r["d"] for r in rows])
    p = np.array([r["pred"] for r in rows])
    rel = np.abs(d - p) / p
    return {"world": kind, "L": L, "sep_R": sep, "n_cells": w.n, "a_cells": a,
            "s0_R": rows[0]["s"] / R, "max_abs_err_R": float(np.abs(d - p).max() / R),
            "rows": rows, "max_rel_err": float(rel.max()), "final_d_R": float(d[-1] / R),
            "final_pred_R": float(p[-1] / R), "final_s_R": rows[-1]["s"] / R,
            "final_sha256": state_sha256(G.A)}


if __name__ == "__main__":
    if sys.argv[1] == "one":
        r = run((sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), 600))
        with open(os.path.join(HERE, "pair.jsonl"), "a") as fh:
            fh.write(json.dumps(r) + "\n")
        print(r["world"], r["L"], r["sep_R"], "maxabs", round(r["max_abs_err_R"], 3))
        sys.exit()
    jobs = ([("hyperbolic", k, sep, 600) for k in (26, 39) for sep in (2, 3, 4)]
            + [("sphere", rho, sep, 600) for rho in (40, 60, 80) for sep in (3, 4, 6)])
    with Pool(int(os.environ.get("GEOM_PROCS", 2))) as p, \
            open(os.path.join(HERE, "pair.jsonl"), "w") as fh:
        for r in p.imap_unordered(run, jobs, chunksize=1):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            print(r["world"], r["L"], r["sep_R"], "a", round(r["a_cells"] / R, 3), "s",
                  round(r["final_s_R"], 2), "d", round(r["final_d_R"], 2), "pred",
                  round(r["final_pred_R"], 2), "maxrel", round(r["max_rel_err"], 4), "s0", round(r["s0_R"], 2),
                  "maxabs", round(r["max_abs_err_R"], 3), flush=True)
