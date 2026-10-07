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
