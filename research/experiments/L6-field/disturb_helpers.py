"""Lane 4 L4-001 disturbances (I001-I004), re-implemented from
claude/night0-disturbance-np4adr @ 7bd1a42 src/alm/disturb.py so Lane 6 does not
depend on an unmerged branch. Same definitions; R is passed explicitly."""
import numpy as np

from field import wrap


def offsets(shape, cx, cy):
    ny, nx = shape
    dx = wrap(np.arange(nx)[None, :] - cx, nx) * np.ones((ny, 1))
    dy = wrap(np.arange(ny)[:, None] - cy, ny) * np.ones((1, nx))
    return dx, dy


def disturb(kind, A, s, c, h, R=13):
    cx, cy = c
    hx, hy = h
    if kind == "I001":
        return (1 - s) * A
    if kind == "I002":
        dx, dy = offsets(A.shape, cx, cy)
        out = A.copy()
        out[dx**2 + dy**2 < (s * R) ** 2] = 0.0
        return out
    if kind == "I003":
        dx, dy = offsets(A.shape, cx + R * hx, cy + R * hy)
        w = 0.25 * R
        return np.clip(A + s * np.exp(-(dx**2 + dy**2) / (2 * w**2)), 0, 1)
    if kind == "I004":
        dx, dy = offsets(A.shape, cx, cy)
        lat = (dx * -hy + dy * hx).ravel()
        flat = A.ravel()
        order = np.argsort(-lat, kind="stable")
        k = min(int(np.searchsorted(np.cumsum(flat[order]), s * flat.sum() * (1 - 1e-12))), flat.size - 1)
        out = A.copy()
        out[(lat >= lat[order[k]]).reshape(A.shape)] = 0.0
        return out
    raise ValueError(kind)


def i004(A, s, c, h, R=13):
    return disturb("I004", A, s, c, h, R)
