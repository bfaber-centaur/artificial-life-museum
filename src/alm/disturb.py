"""Lane 4 disturbance battery: instantaneous edits of a Lenia state array.

Every function takes a 2-D float array A (rows = y, columns = x, periodic
torus), the creature frame measured on that state, and a strength, and
returns a new array; the input is never modified. Definitions follow
research/experiments/L4-001-disturbance-battery/protocol.md.

These functions know nothing about how the world is stepped, so they work
with any engine (Lane 1's reference stepper or the src/alm simulator).
"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Frame:
    """Creature frame at the intervention step, in array coordinates."""

    cx: float  # periodic centroid, column (x)
    cy: float  # periodic centroid, row (y)
    hx: float  # unit heading, x component
    hy: float  # unit heading, y component

    @property
    def port(self):
        """Port normal n = (-h_y, h_x)."""
        return -self.hy, self.hx


def periodic_centroid(A):
    """Circular-mean centroid (cx, cy) of a periodic array, in cells."""
    ny, nx = A.shape
    ax = 2 * np.pi * np.arange(nx) / nx
    ay = 2 * np.pi * np.arange(ny) / ny
    cx = (np.angle((A.sum(0) * np.exp(1j * ax)).sum()) % (2 * np.pi)) * nx / (2 * np.pi)
    cy = (np.angle((A.sum(1) * np.exp(1j * ay)).sum()) % (2 * np.pi)) * ny / (2 * np.pi)
    return cx, cy


def wrap(d, n):
    """Wrap a coordinate difference into [-n/2, n/2)."""
    return (d + n / 2) % n - n / 2


def offsets(shape, cx, cy):
    """Periodic offsets (dx, dy) of every cell from the point (cx, cy)."""
    ny, nx = shape
    dx = wrap(np.arange(nx)[None, :] - cx, nx) * np.ones((ny, 1))
    dy = wrap(np.arange(ny)[:, None] - cy, ny) * np.ones((1, nx))
    return dx, dy


def gyradius(A, cx, cy):
    """RMS distance of mass from (cx, cy), in cells."""
    m = A.sum()
    if m <= 0:
        return 0.0
    dx, dy = offsets(A.shape, cx, cy)
    return float(np.sqrt(((dx ** 2 + dy ** 2) * A).sum() / m))


def frame_from(A, prev_centroid):
    """Frame of state A, heading from prev_centroid (cx, cy) to A's centroid."""
    ny, nx = A.shape
    cx, cy = periodic_centroid(A)
    vx = wrap(cx - prev_centroid[0], nx)
    vy = wrap(cy - prev_centroid[1], ny)
    n = np.hypot(vx, vy)
    if n == 0:
        raise ValueError("creature did not move; heading undefined")
    return Frame(cx, cy, vx / n, vy / n)


# --- interventions -------------------------------------------------------

def i001_attenuate(A, frame, s, R):
    """I001 mass attenuation: A <- (1 - s) A."""
    return (1.0 - s) * A


def i002_central_deletion(A, frame, s, R):
    """I002: zero cells whose periodic distance to the centroid is < s R."""
    dx, dy = offsets(A.shape, frame.cx, frame.cy)
    out = A.copy()
    out[dx ** 2 + dy ** 2 < (s * R) ** 2] = 0.0
    return out


def i003_frontal_addition(A, frame, s, R, ahead=1.0, width=0.25):
    """I003: add a Gaussian of peak s, width `width` R, centred `ahead` R in front."""
    px = frame.cx + ahead * R * frame.hx
    py = frame.cy + ahead * R * frame.hy
    dx, dy = offsets(A.shape, px, py)
    w = width * R
    return np.clip(A + s * np.exp(-(dx ** 2 + dy ** 2) / (2 * w ** 2)), 0.0, 1.0)


def i004_port_injury(A, frame, s, R):
    """I004: zero the most-port cells until removed mass first reaches s * M0.

    All cells with lateral coordinate >= the threshold are removed (ties
    included), so the achieved fraction can slightly exceed s."""
    if s <= 0:
        return A.copy()
    dx, dy = offsets(A.shape, frame.cx, frame.cy)
    nx_, ny_ = frame.port
    lat = (dx * nx_ + dy * ny_).ravel()
    flat = A.ravel()
    order = np.argsort(-lat, kind="stable")
    cum = np.cumsum(flat[order])
    k = int(np.searchsorted(cum, s * flat.sum() * (1 - 1e-12)))
    k = min(k, flat.size - 1)
    thresh = lat[order[k]]
    out = A.copy()
    out[(lat >= thresh).reshape(A.shape)] = 0.0
    return out


INTERVENTIONS = {
    "I001": i001_attenuate,
    "I002": i002_central_deletion,
    "I003": i003_frontal_addition,
    "I004": i004_port_injury,
}


# --- outcome classification (protocol "Outcome definition") ----------------

# Lane 1 S001 dossier baseline, 128^2, steps 1000-4000; fixed before L4-001.
BASELINE = {"mass": 0.4358, "gyradius": 0.4376, "speed": 0.4796}


def classify(window_mass, window_gyr, window_speed, final_mass, band=0.2,
             baseline=BASELINE):
    """Protocol class for one run.

    window_mass, window_gyr: 10-step samples over the evaluation window
    (mass as sum(A)/R^2, gyradius in R units); window_speed in R per time
    unit; final_mass at the end of the horizon."""
    m, g, v = baseline["mass"], baseline["gyradius"], baseline["speed"]
    if final_mass < 0.01:
        return "DIED"
    if final_mass > 2 * m:
        return "EXPLODED"
    wm = np.asarray(window_mass)
    wg = np.asarray(window_gyr)
    lo, hi = 1 - band, 1 + band
    if (np.all((wm >= lo * m) & (wm <= hi * m))
            and np.all((wg >= lo * g) & (wg <= hi * g))
            and lo * v <= window_speed <= hi * v):
        return "RECOVERED"
    return "TRANSFORMED"
