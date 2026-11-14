"""GEOM-K (round 2): Orbium passing a cone point, a "lens" made of pure geometry.

A cone is flat everywhere except its apex. Cutting a 60-degree wedge out of a hex lattice and
gluing the edges (5 sectors) concentrates positive curvature at the apex, like one vertex of the
icosphere; inserting an extra wedge (7 sectors) concentrates negative curvature. Two straight
lines passing on either side of the apex are bent toward each other by the deficit (they cross at
distance 2 b from the apex for a 60-degree deficit, b = half the gap) or away from each other by
the excess. This is the geometry of a cosmic string, a gravitational lens without mass.

Runs: two S001 Orbia start 6 R before the apex at chart heights +-b, heading straight past it
(sectors 5, 6, 7 x b = 1.5, 2, 3 R), plus one Orbium aimed straight at the apex (b = 0). The
separation d between the two mass centres (cone geodesic distance) is compared with the
separation of the two unfolded straight lines at the same path length s (s = s0 + path, as
pair.py). Stops at contact, or when a body nears the world's edge.

Usage:  python cone.py run   -> cone.jsonl   (python cone.py apex: re-run the single-Orbium shots at b = 0, 0.25, 0.5, 1 R)
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
R, D, RMAX, SETTLE = 13, 6 * 13, 150, 20


def setup(sectors, b_R, apex=False):
    s = specimens.load("S001")
    f = g.patch_sampler(s.cells / 255.0)
    w = g.cone(sectors, RMAX)
    tm = w.params["Theta"] / 2
    if apex:
        A = g.seed_cone(w, f, tm, (-D, 0.0), 0.0)
    else:
        b = b_R * R
        A = np.maximum(g.seed_cone(w, f, tm, (-D, b), 0.0), g.seed_cone(w, f, tm, (-D, -b), 0.0))
    return s, w, tm, A


def to_cone(w, tm, X, Y):
    """Chart point (X, Y) of an unfolded straight line -> cone polar (r, theta)."""
    r = np.hypot(X, Y)
    phi = np.arctan2(-Y, -X)
    return r, (tm + phi) % w.params["Theta"]


def run(job):
    sectors, b_R = job
    s, w, tm, A = setup(sectors, b_R)
    Th = w.params["Theta"]
    G = g.GraphLenia(w, s.rule, A)
    phi = (w.theta - tm + Th / 2) % Th - Th / 2
    masks = (phi < 0, phi >= 0)  # chart Y > 0 (upper) is phi < 0
    seeds = [to_cone(w, tm, -D, +b_R * R), to_cone(w, tm, -D, -b_R * R)]
    rows, prev, path, end = [], None, np.zeros(2), "steps"
    for t in range(0, 801):
        if t % 10 == 0 and t >= SETTLE:
            cs = [g.cone_centroid(w, G.A, m.astype(float)) for m in masks]
            if any(c is None for c in cs):
                end = "lost"
                break
            ref = seeds if prev is None else prev
            path += [float(g.cone_dist(cs[k][0], cs[k][1], ref[k][0], ref[k][1], Th)) for k in range(2)]
            prev = cs
            d = float(g.cone_dist(cs[0][0], cs[0][1], cs[1][0], cs[1][1], Th))
            sbar = float(path.mean())
            p = [to_cone(w, tm, -D + sbar, sg * b_R * R) for sg in (1, -1)]
            pred = float(g.cone_dist(p[0][0], p[0][1], p[1][0], p[1][1], Th))
            nb = len([m for m in g.components(w, G.A) if (G.A[m] * w.area[m]).sum() > 0.2 * R**2])
            rows.append({"t": t, "d": d, "pred": pred, "s": sbar, "n_bodies": nb,
                         "r": [cs[0][0], cs[1][0]], "theta_deg": [np.degrees(cs[0][1]), np.degrees(cs[1][1])],
                         "mass_R2": g.mass(w, G.A) / R**2})
            if nb < 2 or d < 1.6 * R:
                end = "contact"
                break
            if max(cs[0][0], cs[1][0]) > RMAX - 2.5 * R:
                end = "edge"
                break
        G.step()
    d = np.array([x["d"] for x in rows])
    p = np.array([x["pred"] for x in rows])
    far = d > 2.5 * R
    return {"sectors": sectors, "Theta_deg": sectors * 60, "b_R": b_R, "n_cells": w.n,
            "world_sha256": w.sha256(), "end": end, "steps": rows[-1]["t"], "rows": rows,
            "max_abs_err_R": float(np.abs(d - p)[far].max() / R) if far.any() else None,
            "final_d_R": float(d[-1] / R), "final_pred_R": float(p[-1] / R),
            "final_sha256": state_sha256(G.A)}


def apex(sectors, b_R=0.0):
    """One Orbium aimed past the apex at chart height b_R (0 = straight at it); stops when it
    nears the world's edge (or 400 steps)."""
    s, w, tm, A = setup(sectors, 0, apex=True)
    if b_R:
        f = g.patch_sampler(s.cells / 255.0)
        A = g.seed_cone(w, f, tm, (-D, b_R * R), 0.0)
    G = g.GraphLenia(w, s.rule, A)
    ms, rs, end = [], [], "steps"
    for t in range(1, 401):
        G.step()
        if t % 10 == 0:
            m = g.mass(w, G.A) / R**2
            ms.append(round(m, 4))
            if m < 0.01:
                end = "died"
                break
            c = g.cone_centroid(w, G.A, np.ones(w.n))
            rs.append(round(c[0] / R, 3))
            if c[0] > RMAX - 2.5 * R:
                end = "edge"
                break
    bodies = []
    for m in g.components(w, G.A):
        mm = float((G.A[m] * w.area[m]).sum()) / R**2
        if mm > 0.05:
            mk = np.zeros(w.n)
            mk[m] = 1
            c = g.cone_centroid(w, G.A, mk)
            bodies.append({"mass_R2": mm, "r_R": c[0] / R, "theta_deg": float(np.degrees(c[1]))})
    return {"sectors": sectors, "Theta_deg": sectors * 60, "b_R": b_R, "apex_shot": True,
            "end": end, "steps": t, "mass_R2_every_10": ms, "centre_r_R_every_10": rs,
            "min_r_R": min(rs) if rs else None, "bodies": bodies, "final_sha256": state_sha256(G.A)}


if __name__ == "__main__":
    if sys.argv[1] == "apex":  # re-run only the three apex shots, replacing their rows
        keep = [json.loads(x) for x in open(os.path.join(HERE, "cone.jsonl")) if not json.loads(x).get("apex_shot")]
        with Pool(3) as p:
            new = p.starmap(apex, [(sec, b) for sec in (5, 6, 7) for b in (0.0, 0.25, 0.5, 1.0)])
        with open(os.path.join(HERE, "cone.jsonl"), "w") as fh:
            for r in keep + new:
                fh.write(json.dumps(r) + "\n")
        for r in new:
            print("apex", r["sectors"], r["b_R"], r["end"], r["steps"], "min r", r["min_r_R"],
                  [round(b["mass_R2"], 3) for b in r["bodies"]], r["mass_R2_every_10"][-3:])
        sys.exit()
    jobs = [(sec, b) for sec in (5, 6, 7) for b in (1.5, 2, 3)]  # then: cone.py apex
    with Pool(int(os.environ.get("GEOM_PROCS", 2))) as p, \
            open(os.path.join(HERE, "cone.jsonl"), "w") as fh:
        for r in p.imap_unordered(run, jobs, chunksize=1):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            if r.get("apex_shot"):
                print("apex", r["sectors"], [round(b["mass_R2"], 3) for b in r["bodies"]], flush=True)
            else:
                print(r["sectors"], r["b_R"], r["end"], r["steps"], "d", round(r["final_d_R"], 2),
                      "pred", round(r["final_pred_R"], 2), "maxerr", r["max_abs_err_R"], flush=True)
