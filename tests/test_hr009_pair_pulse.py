"""Lane 7 HR-009 E2 check: S101's frontal-addition drag-down is not just the pulse being split.

L6-008 gives each partner alone only its own half of the I003 pulse. Here each partner alone gets
the *whole* pulse and still survives as an Orbium at s = 0.2 (phase t0 = 3000), while the bound
pair dies (research/experiments/HR009-l6-review/e2.csv; L6-008 pair-coupling.csv).
"""
import numpy as np

from alm import specimens
from alm.disturb import offsets, periodic_centroid, wrap
from alm.lenia import Lenia

M1 = 0.4358  # single-Orbium mass, sum(A)/R^2


def _run(rule, A, steps):
    w = Lenia(rule, A)
    for _ in range(steps):
        w.step()
    return w.A.sum() / rule.R**2


def test_full_pulse_halves_survive_where_the_pair_dies():
    S = specimens.load("S101")
    rule = specimens.load("S001").rule  # L6-008 runs S101 under the S001 rule
    w = Lenia(rule, S.place(128))
    for _ in range(2990):
        w.step()
    c0 = periodic_centroid(w.A)
    for _ in range(10):
        w.step()
    A = w.A.copy()
    c = periodic_centroid(A)
    v = np.array([wrap(c[0] - c0[0], 128), wrap(c[1] - c0[1], 128)])
    hx, hy = v / np.hypot(*v)
    dx, dy = offsets(A.shape, *c)
    port = (dx * -hy + dy * hx) > 0
    R = rule.R
    gx, gy = offsets(A.shape, c[0] + R * hx, c[1] + R * hy)
    G = 0.2 * np.exp(-(gx**2 + gy**2) / (2 * (0.25 * R) ** 2))

    pair = _run(rule, np.clip(A + G, 0, 1), 3000)
    port_alone = _run(rule, np.clip(np.where(port, A, 0) + G, 0, 1), 3000)
    stb_alone = _run(rule, np.clip(np.where(port, 0, A) + G, 0, 1), 3000)
    assert pair < 0.01
    assert abs(port_alone / M1 - 1) < 0.05
    assert abs(stb_alone / M1 - 1) < 0.05
