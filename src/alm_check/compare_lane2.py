"""Black-box comparison of a Lane 2 (``alm.run``) trace directory with alm_check.

Reads only the trace files Lane 2 publishes (trace.csv, states.npz), reruns the
same S001 baseline with alm_check, and prints the largest disagreement per
column plus the final-state difference.

    .venv/bin/python -m alm_check.compare_lane2 research/traces/S001-<run-id>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from .lenia import Rule, World, load_orbium, place, run


def compare(trace_dir: Path) -> dict:
    L = np.genfromtxt(trace_dir / "trace.csv", delimiter=",", names=True)
    steps = L["step"].astype(int)
    every = int(steps[1] - steps[0])
    n_steps = int(steps[-1])
    n = 128
    states = np.load(trace_dir / "states.npz") if (trace_dir / "states.npz").exists() else None
    if states is not None:
        n = states["initial"].shape[0]
    tr = run(World(place(load_orbium(), n), Rule()), n_steps, every=every, keep_states=(n_steps,))
    out = {}
    for ours, theirs in [("mass", "mass"), ("growth", "growth"), ("gyradius", "gyradius"), ("speed", "speed")]:
        a, b = tr[ours], L[theirs]
        m = np.isfinite(a) & np.isfinite(b)
        out[ours] = float(np.abs(a[m] - b[m]).max())
    for ours, theirs in [("cx", "cx_cells"), ("cy", "cy_cells")]:
        out[ours] = float(np.abs((tr[ours] - L[theirs] + n / 2) % n - n / 2).max())
    if states is not None:
        out["initial_equal"] = bool(np.array_equal(place(load_orbium(), n), states["initial"]))
        out["final_max_abs_diff"] = float(np.abs(tr["states"][n_steps] - states["final"]).max())
    out["steps"] = n_steps
    return out


if __name__ == "__main__":
    print(json.dumps(compare(Path(sys.argv[1])), indent=2))
