"""Pilot job list P1-P6 in protocol schedule order, and a two-process launcher.

  python research/experiments/REEF-field/jobs.py plan                 # writes jobs-pilots.json
  python research/experiments/REEF-field/jobs.py run --protocol-addendum SHA [--procs 2]

Each job is one lockstep runner call (E + G-alone + S-alone). Control mapping (D-004): the
G-alone of every offset of a snapshot is the shared control REEF-CTRL-<snap>; each lockstep G must
reproduce its final sha256 bitwise (checked in `run`). The S-alone is per realised ring position
(REEF-P<k>-S, the lockstep S). Order: random.Random(20261020).shuffle of [P1..P6] (§5).
"""
import argparse
import json
import random
import subprocess
import sys

from reefcore import HERE

SEED = 20261020


def plan():
    c = json.loads((HERE / "controls.json").read_text())
    jobs = []
    for p in c["geometry"]["pilots"]:
        k = p["pilot"]
        geom = {kk: p[kk] for kk in ("b_R_requested", "b_R_realized", "d_R_requested", "d_R_realized", "heading_deg")}
        geom["gap_R_realized"] = p["gap_R_realized"]
        jobs.append({"pilot": k, "run_id": f"REEF-{k}-E", "snapshot": p["snapshot"],
                     "ring_shift": p["ring_shift_cells_yx"], "geometry": geom,
                     "controls": {"G": f"REEF-CTRL-{p['snapshot']}", "G_final_sha256": c[p["snapshot"]]["final_state_sha256"],
                                  "S": f"REEF-{k}-S (lockstep in REEF-{k}-E)"}})
    order = list(range(len(jobs)))
    random.Random(SEED).shuffle(order)
    sched = [dict(jobs[i], schedule={"seed": SEED, "position": pos}) for pos, i in enumerate(order)]
    out = {"schedule_seed": SEED, "shuffle": "random.Random(20261020).shuffle(list(range(6))) over [P1..P6]",
           "order": [j["pilot"] for j in sched], "N": 256, "H_tu": 50, "jobs": sched}
    (HERE / "jobs-pilots.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["order"])


def run(addendum, procs):
    plan_ = json.loads((HERE / "jobs-pilots.json").read_text())
    queue = list(plan_["jobs"])
    running = []
    while queue or running:
        while queue and len(running) < procs:
            j = queue.pop(0)
            cmd = [sys.executable, str(HERE / "runner.py"), "--run-id", j["run_id"], "--kind", "encounter",
                   "--snapshot", j["snapshot"], "--ring-shift", *map(str, j["ring_shift"]),
                   "--geometry", json.dumps(j["geometry"]), "--schedule-position", str(j["schedule"]["position"]),
                   "--protocol-addendum", addendum, "--notes", f"controls: G={j['controls']['G']} (shared), S={j['controls']['S']}"]
            running.append((j, subprocess.Popen(cmd, cwd=HERE)))
        j, p = running.pop(0)
        rc = p.wait()
        m = json.loads((HERE / "runs" / j["run_id"] / "manifest.json").read_text()) if rc == 0 else None
        ok = m is not None and m["lockstep_final_state_sha256"]["G"] == j["controls"]["G_final_sha256"]
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
