"""Quick-look figure for one run directory.

    python -m alm.plot research/traces/<run_id>

writes ``overview.png`` next to the trace: mass and speed against time, the
unwrapped centroid path, and the final state.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np


def overview(run_dir: Path | str) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    run_dir = Path(run_dir)
    man = json.loads((run_dir / "manifest.json").read_text())
    rows = list(csv.DictReader(open(run_dir / "trace.csv")))
    t = np.array([float(r["time"]) for r in rows])
    speed = np.array([float(r["speed"]) for r in rows])
    series = np.load(run_dir / "series.npz")
    final = np.load(run_dir / "states.npz")["final"]
    dt = man["timestep"]["dt"]
    ts = np.arange(len(series["mass"])) * dt

    fig, ax = plt.subplots(2, 2, figsize=(10, 7))
    ax[0, 0].plot(ts, series["mass"], lw=0.6)
    ax[0, 0].set(xlabel="time", ylabel="mass  ΣA/R²", title="mass (every step)")
    ax[0, 1].plot(t, speed, lw=0.8)
    ax[0, 1].set(xlabel="time", ylabel="speed (R per unit time)", title=f"speed (every {man['measurements']['every']} steps)")
    ax[1, 0].plot(series["x_cells"], series["y_cells"], lw=0.8)
    ax[1, 0].invert_yaxis()
    ax[1, 0].set_aspect("equal")
    ax[1, 0].set(xlabel="x (cells, unwrapped)", ylabel="y (cells, down)", title="centroid path")
    ax[1, 1].imshow(final, cmap="viridis", vmin=0, vmax=1, interpolation="nearest")
    ax[1, 1].set(title=f"final state, step {man['timestep']['steps']}", xticks=[], yticks=[])
    for s in man["interventions_applied"]:
        for a in (ax[0, 0], ax[0, 1]):
            a.axvline(s["step"] * dt, color="r", lw=0.8, ls="--")
    fig.suptitle(f"{man['run_id']}  ({man['specimen']['id']}, {man['grid']['shape'][0]}², T={man['rule']['T']})")
    fig.tight_layout()
    out = run_dir / "overview.png"
    fig.savefig(out, dpi=90)
    plt.close(fig)
    return out


if __name__ == "__main__":
    for d in sys.argv[1:]:
        print(overview(d))
