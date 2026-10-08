"""Lane 7 HR-009 E2, as corrected by Lane 6's L6-009: the gap pulse unbinds S101; it does not kill it.

At I003 s = 0.2 (phase t0 = 3000) the bound pair is dead at 300 tu on the 128² torus, while each
partner alone survives even the *full* pulse (HR-009 E2, which first read this as coupling). L6-009
showed why: the pulse splits the pair into two intact Orbia that later collide on the small torus.
The same edited state, zero-padded to 256², ends as two Orbia (L6-009 bigworld.csv; HR-009c).
"""
import numpy as np

from alm import specimens
from alm.disturb import offsets, periodic_centroid, wrap
from alm.lenia import Lenia

M1 = 0.4358  # single-Orbium mass, sum(A)/R^2


def _run(rule, A, steps, check=()):
    w = Lenia(rule, A)
    seen = {}
    for t in range(1, steps + 1):
        w.step()
        if t in check:
            seen[t] = w.A.sum() / rule.R**2
    return w.A.sum() / rule.R**2, seen


def test_gap_pulse_unbinds_the_pair_and_deaths_need_the_small_torus():
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
    E = np.clip(A + G, 0, 1)

    # each partner alone survives the full pulse
    assert abs(_run(rule, np.clip(np.where(port, A, 0) + G, 0, 1), 3000)[0] / M1 - 1) < 0.05
    assert abs(_run(rule, np.clip(np.where(port, 0, A) + G, 0, 1), 3000)[0] / M1 - 1) < 0.05
    # on 128² the pair carries two Orbia's mass at 40 tu, yet is dead by 300 tu (a later collision)
    final, seen = _run(rule, E, 3000, check=(400,))
    assert abs(seen[400] / (2 * M1) - 1) < 0.01
    assert final < 0.01
    # the same edited state on a 256² torus ends as two Orbia
    big = np.zeros((256, 256))
    big[64:192, 64:192] = np.roll(E, (64 - int(round(c[1])), 64 - int(round(c[0]))), (0, 1))
    assert abs(_run(rule, big, 3000)[0] / (2 * M1) - 1) < 0.05
