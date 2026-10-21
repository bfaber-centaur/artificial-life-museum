"""Write runs.jsonl manifests for the settle and isolated-control runs (settle.json, controls.json)."""
import json

from reefcore import HERE, RULE

rule = {"kernel": "poly", "growth": "poly", "beta": [1.0], "mu": RULE.mu, "sigma": RULE.sigma, "R": RULE.R,
        "T": int(RULE.T), "update": "euler+clip", "dtype": "float64"}
s = json.loads((HERE / "settle.json").read_text())
c = json.loads((HERE / "controls.json").read_text())
seeds = {k: json.loads((HERE / "seeds" / f"{k}.npy.json").read_text()) for k in ("GA", "GB", "S103")}
rows = [{
    "run_id": "REEF-SETTLE-G", "kind": "settle", "lane": "field", "commit": "586b134e9a88e1efa189016a4e06a61537bd91d0", "engine": "alm",
    "rule": rule, "world": {"N": 256, "boundary": "periodic"},
    "inputs": {"glider": None, "ring": None, "initial_state_sha256": s["seed"]["placed_sha256"],
               "seed": "S001 cells, Specimen.place(256), offset (118,118)"},
    "horizon_tu": 501.0, "command": "python research/experiments/REEF-field/settle.py",
    "env": s["provenance"]["env"],
    "outputs": {"settle.json": "research/experiments/REEF-field/settle.json",
                "GA": seeds["GA"]["state_sha256"], "GB": seeds["GB"]["state_sha256"], "S103": seeds["S103"]["state_sha256"]},
    "final_state_sha256": seeds["GA"]["source_state_sha256"], "wall_s": s["wall_s"], "status": "ok",
    "result": {"extension": s["extension"], "assessment_400_500tu": {k: s["assessment"][-1][k] for k in ("motion", "mass_mean", "mass_rsd", "drift", "accepted", "acceptance")}},
    "notes": "README F-001/F-004, R-001. "
             "Preregistered one-component criterion failed from single-cell specks; see R-001.",
}]
for key, rid, snap in (("GA", "REEF-CTRL-GA", "GA"), ("GB", "REEF-CTRL-GB", "GB"), ("GA_100tu", "REEF-CTRL-GA-100tu", "GA"), ("S103", "REEF-CTRL-S103", None)):
    o = c[key]
    rows.append({
        "run_id": rid, "kind": "control_S" if snap is None else "control_G", "lane": "field", "commit": "87d90e1826785d3091db18fcee5d7d191a0d7a17",
        "engine": "alm", "rule": rule, "world": {"N": 256, "boundary": "periodic"},
        "inputs": {"glider": None if snap is None else {"snapshot": snap, "state_sha256": seeds[snap]["state_sha256"],
                   "path": f"research/experiments/REEF-field/seeds/{snap}.npy", "shift_cells": [0, 0]},
                   "ring": None if snap else {"state_sha256": seeds["S103"]["state_sha256"],
                   "path": "research/experiments/REEF-field/seeds/S103.npy", "shift_cells": [0, 0]},
                   "initial_state_sha256": o["initial_state_sha256"]},
        "horizon_tu": o["steps"] / 10, "command": "python research/experiments/REEF-field/controls.py",
        "env": c["provenance"]["env"], "outputs": {"controls.json": "research/experiments/REEF-field/controls.json",
                                                    "controls-series.npz": "research/experiments/REEF-field/controls-series.npz"},
        "final_state_sha256": o["final_state_sha256"], "wall_s": o["wall_s"], "status": "ok",
        "result": {k: o[k] for k in ("motion_fit", "noise_1tu", "support_radius_R_max", "ncomp_fraction", "displacement_R")},
        "notes": "Shared G-alone control for every offset of this snapshot (D-004) when the encounter's glider input and N match."
                 if snap and key != "GA_100tu" else "",
    })
with open(HERE / "runs.jsonl") as f:
    old = f.read()
with open(HERE / "runs.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r, default=float, separators=(",", ":")) + "\n")
    f.write(old)
