"""Shared helpers for the REEF field lane: the fixed rule, seeds, a tracked run loop, hashes.

Physics is ``alm.lenia.Lenia`` unchanged. Tracking here is whole-world only (mass, one unwrapped
periodic centroid, component count); two-body attribution is the Behavior lane's tracker.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

from alm import specimens
from alm.lenia import Lenia, Rule
from alm.morphometrics import centroid, min_image
from alm.provenance import code_version, environment, state_sha256

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "L6-field"))
from field import components  # noqa: E402  (torus-aware 8-connected count, threshold 0.1)

RULE = Rule(R=13, T=10, mu=0.155, sigma=0.020, beta=(1.0,), kernel="poly", growth="poly")
N = 256


def sha_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance() -> dict:
    return {"code": code_version(), "env": environment(), "rule": RULE.to_dict(), "N": N}


def track(A0, steps, rule=RULE, comp_every=10, keep=(), on_step=None):
    """Run ``steps`` Euler steps from ``A0``; returns per-step series and kept states.

    ``pos`` is the unwrapped periodic centroid (cy, cx) in cells, accumulated from minimum-image
    increments (valid while the body moves < N/2 per step). ``keep`` holds step indices whose
    exact float64 states are returned.
    """
    sim = Lenia(rule, A0)
    ny, nx = sim.A.shape
    mass = np.empty(steps + 1)
    pos = np.full((steps + 1, 2), np.nan)
    ncomp = {}
    states = {}

    def observe(t, last):
        A = sim.A
        m = A.sum()
        mass[t] = m / rule.R**2
        if m > 0:
            c = np.array(centroid(A))
            if last is None:
                pos[t] = c
            else:
                prev_wrapped = np.array([last[0] % ny, last[1] % nx])
                d = np.array([min_image(c[0] - prev_wrapped[0], ny), min_image(c[1] - prev_wrapped[1], nx)])
                pos[t] = last + d
        if t % comp_every == 0:
            ncomp[t] = components(A)
        if t in keep:
            states[t] = A.copy()
        if on_step is not None:
            on_step(t, A)
        return pos[t] if m > 0 else last

    last = observe(0, None)
    for t in range(1, steps + 1):
        sim.step()
        last = observe(t, last)
    return dict(mass=mass, pos=pos, ncomp=ncomp, states=states, final=sim.A.copy())


def fit_motion(pos, t0, t1, rule=RULE):
    """Least-squares velocity over steps [t0, t1]: speed (R/tu), heading (deg, +x toward +y,
    image y-down) and straightness (net / summed per-tu path length)."""
    t = np.arange(t0, t1 + 1)
    p = pos[t0 : t1 + 1]
    vy = np.polyfit(t, p[:, 0], 1)[0]
    vx = np.polyfit(t, p[:, 1], 1)[0]
    per_tu = p[:: int(rule.T)]
    path = np.hypot(*np.diff(per_tu, axis=0).T).sum()
    net = np.hypot(*(per_tu[-1] - per_tu[0]))
    return {
        "speed_R_per_tu": float(np.hypot(vy, vx) * rule.T / rule.R),
        "speed_cells_per_step": float(np.hypot(vy, vx)),
        "heading_deg": float(np.degrees(np.arctan2(vy, vx))),
        "vy_cells_per_step": float(vy),
        "vx_cells_per_step": float(vx),
        "straightness": float(net / path) if path > 0 else float("nan"),
    }


def recentre(A):
    """Integer roll putting the periodic centroid within half a cell of (N/2, N/2)."""
    cy, cx = centroid(A)
    ny, nx = A.shape
    sy, sx = int(round(ny / 2 - cy)), int(round(nx / 2 - cx))
    B = np.roll(A, (sy, sx), axis=(0, 1))
    return B, (sy, sx)


def save_state(path, A, meta: dict):
    path = Path(path)
    np.save(path, np.ascontiguousarray(A, dtype="<f8"))
    meta = dict(meta, state_sha256=state_sha256(A), file=path.name, file_sha256=sha_file(path))
    Path(str(path) + ".json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    return meta


def load_state(path):
    A = np.load(path)
    meta = json.loads(Path(str(path) + ".json").read_text())
    if state_sha256(A) != meta["state_sha256"]:
        raise ValueError(f"{path}: state hash mismatch")
    return A, meta


def s103_state(n=N):
    return specimens.load("S103").place(n)
