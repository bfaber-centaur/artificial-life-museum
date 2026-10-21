"""D-018 discovery grid X1-X8: geometry, blob stand-ins and the scheduled job list.

  python research/experiments/REEF-field/discovery.py plan     # seeds/BLOB-X7/X8.npy + jobs-discovery.json
  python research/experiments/REEF-field/discovery.py run --protocol-addendum SHA [--procs 2]

X1-X6: same placement as the pilots (controls.json geometry: heading from each snapshot's
whole-H G-alone fit, glider front / ring back extents along it, requested gap 4 R), at new b.
X7/X8: the glider is replaced by a static isotropic Gaussian blob
    A(r) = a exp(-r^2 / (2 s^2)) for r <= 4 s, else 0 (float64, clip-safe: a < 1),
centred at the GA-alone control's (wrapped) centroid at step 55 (t = 5.5 tu), with a and s solved
on the grid so that mass = 0.4873 ΣA/R^2 and gyradius = 0.477 R exactly (to 1e-12), and the
P2 / P3 ring rolls.
"""
import argparse
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from reefcore import HERE, N, RULE, save_state
from alm.morphometrics import centroid, gyradius, min_image

SEED = 20261020
SHARED = Path("/mnt/project-files/reef-field/runs")
R = RULE.R
GAP = 4.0
BLOB_MASS, BLOB_GYR, BLOB_CUT, BLOB_STEP = 0.4873, 0.477, 4.0, 55


def ring_geometry(c, snap, b):
    p0 = next(p for p in c["geometry"]["pilots"] if p["snapshot"] == snap)
    hd = np.radians(p0["heading_deg"])
    h = np.array([np.sin(hd), np.cos(hd)])
    nrm = np.array([h[1], -h[0]])
    cG = np.array(p0["glider_centroid_yx"])
    cS0 = np.array(p0["ring_centroid_yx"]) - np.array(p0["ring_shift_cells_yx"])
    d_req = GAP * R + (p0["glider_front_R"] - p0["ring_back_R"]) * R
    shift = np.rint(cG + d_req * h + b * R * nrm - cS0).astype(int)
    rel = cS0 + shift - cG
    return shift, {"b_R_requested": b, "b_R_realized": float(rel @ nrm / R), "d_R_requested": d_req / R,
                   "d_R_realized": float(rel @ h / R),
                   "gap_R_realized": float(rel @ h / R - p0["glider_front_R"] + p0["ring_back_R"]),
                   "heading_deg": p0["heading_deg"]}


def blob(center):
    yy, xx = np.mgrid[0:N, 0:N]
    r2 = min_image(yy - center[0], N) ** 2 + min_image(xx - center[1], N) ** 2

    def shape(s):
        return np.where(r2 <= (BLOB_CUT * s) ** 2, np.exp(-r2 / (2 * s * s)), 0.0)

    s = brentq(lambda s: gyradius(shape(s), center, R) - BLOB_GYR, 1.0, 20.0, xtol=1e-14)
    B = shape(s)
    a = BLOB_MASS * R**2 / B.sum()
    A = a * B
    assert A.max() < 1
    return A, {"form": "a*exp(-r^2/(2 s^2)) for r <= 4 s (minimum-image r from centre), else 0",
               "a": a, "s_cells": s, "cut_cells": BLOB_CUT * s, "centre_yx": list(map(float, center)),
               "target_mass_R2": BLOB_MASS, "target_gyradius_R": BLOB_GYR,
               "mass_R2": float(A.sum() / R**2), "gyradius_R": gyradius(A, center, R),
               "centroid_yx": list(centroid(A)), "support_cells_gt_0.01": int((A > 0.01).sum()),
               "centre_source": f"REEF-CTRL-GA pos at step {BLOB_STEP} (controls-series.npz GA_pos, wrapped)"}


def plan():
    c = json.loads((HERE / "controls.json").read_text())
    pos = np.load(HERE / "controls-series.npz")["GA_pos"]
    centre = np.mod(pos[BLOB_STEP], N)
    jobs = []
    for x, snap, b in (("X1", "GA", -1.5), ("X2", "GA", -1.25), ("X3", "GA", 1.25), ("X4", "GA", 1.5),
                       ("X5", "GB", -1.5), ("X6", "GB", 1.5)):
        shift, geom = ring_geometry(c, snap, b)
        jobs.append({"id": x, "run_id": f"REEF-{x}-E", "snapshot": snap, "ring_shift": shift.tolist(), "geometry": geom,
                     "controls": {"G": f"REEF-CTRL-{snap}", "G_final_sha256": c[snap]["final_state_sha256"],
                                  "S": f"REEF-{x}-S (lockstep)"}})
    A, info = blob(centre)
    for x, pilot in (("X7", "P2"), ("X8", "P3")):
        p = next(q for q in c["geometry"]["pilots"] if q["pilot"] == pilot)
        name = f"BLOB-{x}"
        meta = save_state(HERE / "seeds" / f"{name}.npy", A, {"name": name, "construction": dict(info, geometry_of=pilot),
                                                               "rule": RULE.to_dict(), "N": N})
        rel = np.array(p["ring_centroid_yx"]) - centre
        hd = np.radians(p["heading_deg"])
        h = np.array([np.sin(hd), np.cos(hd)])
        geom = {"stand_in": "static Gaussian blob", "geometry_of": pilot, "b_R_requested": p["b_R_requested"],
                "ring_shift_from": pilot, "blob_to_ring_along_heading_R": float(rel @ h / R),
                "blob_to_ring_lateral_R": float(rel @ np.array([h[1], -h[0]]) / R), "heading_deg": p["heading_deg"]}
        jobs.append({"id": x, "run_id": f"REEF-{x}-E", "snapshot": name, "ring_shift": p["ring_shift_cells_yx"],
                     "geometry": geom, "blob_state_sha256": meta["state_sha256"],
                     "controls": {"G": f"REEF-{x}-G (lockstep blob-alone)", "S": f"REEF-{x}-S (lockstep)"}})
    order = list(range(len(jobs)))
    random.Random(SEED).shuffle(order)
    sched = [dict(jobs[i], schedule={"seed": SEED, "position": k}) for k, i in enumerate(order)]
    out = {"decision": "D-018 (reef/coordinator a0698db)", "schedule_seed": SEED,
           "shuffle": "random.Random(20261020).shuffle(list(range(8))) over [X1..X8]",
           "order": [j["id"] for j in sched], "N": N, "H_tu": 50, "blob": info, "jobs": sched}
    (HERE / "jobs-discovery.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["order"])
    for j in sched:
        print(j["id"], j["snapshot"], j["ring_shift"], json.dumps(j["geometry"]))
    print(json.dumps(info))


def run(addendum, procs):
    plan_ = json.loads((HERE / "jobs-discovery.json").read_text())
    queue, running = list(plan_["jobs"]), []
    while queue or running:
        while queue and len(running) < procs:
            j = queue.pop(0)
            cmd = [sys.executable, str(HERE / "runner.py"), "--run-id", j["run_id"], "--kind", "encounter",
                   "--snapshot", j["snapshot"], "--ring-shift", *map(str, j["ring_shift"]),
                   "--geometry", json.dumps(j["geometry"]), "--schedule-position", str(j["schedule"]["position"]),
                   "--protocol-addendum", addendum, "--notes", f"D-018 {j['id']}; controls: G={j['controls']['G']}, S={j['controls']['S']}"]
            running.append((j, subprocess.Popen(cmd, cwd=HERE)))
        j, p = running.pop(0)
        rc = p.wait()
        ok = None
        if rc == 0:
            m = json.loads((HERE / "runs" / j["run_id"] / "manifest.json").read_text())
            if "G_final_sha256" in j["controls"]:
                ok = m["lockstep_final_state_sha256"]["G"] == j["controls"]["G_final_sha256"]
            dst = SHARED / j["run_id"]
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HERE / "runs" / j["run_id"] / "frames.npz", dst / "frames.npz")
        print(j["run_id"], "rc", rc, "lockstep G == shared control:", ok, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run"])
    ap.add_argument("--protocol-addendum", default="")
    ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "plan":
        plan()
    else:
        if not a.protocol_addendum:
            ap.error("--protocol-addendum required")
        run(a.protocol_addendum, min(a.procs, 2))
