"""Gallery interventions: Lane 4's disturbances wrapped for ``alm.run``'s intervention hook.

The disturbance itself is Lane 4's pure function (``alm.disturb``, protocol L4-001); only the
frame is built here. The runner hands an intervention the current state but not the previous one,
so the heading is a forward difference: the centroid shift over one probe step of a copy of the
world (the world itself is not advanced). Lane 4 measures the heading backward, from the previous
step's centroid; at Orbium's speed (0.62 cells/step) the two differ by a fraction of a degree.
This difference is disclosed wherever a gallery exhibit uses these interventions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from alm import disturb
from alm.interventions import Intervention, register
from alm.lenia import Lenia


def forward_frame(A: np.ndarray, sim) -> disturb.Frame:
    probe = Lenia(sim.rule, A)
    probe.step()
    ny, nx = A.shape
    cx, cy = disturb.periodic_centroid(A)
    px, py = disturb.periodic_centroid(probe.A)
    vx, vy = disturb.wrap(px - cx, nx), disturb.wrap(py - cy, ny)
    n = float(np.hypot(vx, vy))
    if n == 0:
        raise ValueError("creature did not move; heading undefined")
    return disturb.Frame(cx, cy, vx / n, vy / n)


if "gallery_port_injury" not in __import__("alm.interventions", fromlist=["REGISTRY"]).REGISTRY:

    @register
    @dataclass(frozen=True)
    class GalleryPortInjury(Intervention):
        """L4-001 I004 port injury of strength s (fraction of mass removed from the port side)."""

        name: ClassVar[str] = "gallery_port_injury"
        s: float = 0.1

        def apply(self, A, sim, rng):
            return disturb.i004_port_injury(A, forward_frame(A, sim), self.s, sim.rule.R)


def chord_heading(specimen_id: str, t0: int, chord: int = 10, size: int = 128) -> tuple[float, float]:
    """Unit heading of the uninterrupted specimen run at step t0, from its unwrapped centroid
    ``chord`` steps earlier: Lane 6's L6-005 recipe (``disturb_switch.py``: pos[t] - pos[t - 10])."""
    from alm import measure, specimens

    spec = specimens.load(specimen_id)
    sim = Lenia(spec.rule, spec.place(size))
    ny, nx = sim.A.shape
    last = measure.periodic_centroid(sim.A)
    pos = np.zeros((t0 + 1, 2))
    p = np.array(last, dtype=float)
    for t in range(1, t0 + 1):
        sim.step()
        c = measure.periodic_centroid(sim.A)
        p += (measure.wrap(c[0] - last[0], nx), measure.wrap(c[1] - last[1], ny))
        last = c
        pos[t] = p
    v = pos[t0] - pos[t0 - chord]
    n = float(np.hypot(*v))
    if n == 0:
        raise ValueError("creature did not move over the chord; heading undefined")
    return float(v[0] / n), float(v[1] / n)


if "gallery_port_injury_h" not in __import__("alm.interventions", fromlist=["REGISTRY"]).REGISTRY:

    @register
    @dataclass(frozen=True)
    class GalleryPortInjuryH(Intervention):
        """L4-001 I004 port injury with the heading given as (hx, hy), centred on the current
        periodic centroid. Use ``chord_heading`` to reproduce Lane 6's L6-005 cuts."""

        name: ClassVar[str] = "gallery_port_injury_h"
        s: float = 0.1
        hx: float = 1.0
        hy: float = 0.0

        def apply(self, A, sim, rng):
            cx, cy = disturb.periodic_centroid(A)
            return disturb.i004_port_injury(A, disturb.Frame(cx, cy, self.hx, self.hy), self.s, sim.rule.R)
