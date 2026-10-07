"""Lane 6 field specimens S101-S103: exact seeds load, and their defining behaviour shows quickly."""

import numpy as np
import pytest

from alm import specimens
from alm.lenia import Lenia
from alm.measure import periodic_centroid, wrap


@pytest.mark.parametrize("sid, levels, shape", [("S101", 37582, (35, 31)), ("S102", 24129, (21, 24)),
                                                ("S103", 16320, (12, 12))])
def test_seed_is_exact(sid, levels, shape):
    s = specimens.load(sid)
    assert s.cells.shape == shape
    assert int(s.cells.sum()) == levels
    assert s.cells.min() >= 0 and s.cells.max() <= 255


def test_s101_and_s102_share_rules_with_their_neighbours():
    assert specimens.load("S101").rule == specimens.load("S001").rule
    assert specimens.load("S102").rule == specimens.load("S103").rule
    r = specimens.load("S102").rule
    assert (r.mu, r.sigma, r.R, r.T) == (0.155, 0.020, 13, 10)


def test_s103_is_an_exact_fixed_point():
    """The ring is binary (levels 0/255) and the clipped Euler step leaves it unchanged."""
    s = specimens.load("S103")
    assert set(np.unique(s.cells)) == {0, 255}
    sim = Lenia(s.rule, s.place(64))
    A0 = sim.A.copy()
    for _ in range(50):
        sim.step()
    assert np.array_equal(sim.A, A0)


def _track(sid, steps, size=96):
    s = specimens.load(sid)
    sim = Lenia(s.rule, s.place(size))
    last = periodic_centroid(sim.A)
    path, net = 0.0, np.zeros(2)
    for _ in range(steps):
        sim.step()
        c = periodic_centroid(sim.A)
        d = np.array([wrap(c[0] - last[0], size), wrap(c[1] - last[1], size)])
        path += np.hypot(*d)
        net += d
        last = c
    R = s.rule.R
    return sim.A.sum() / R**2, np.hypot(*net) / R, path / R


def test_s101_glides_as_a_pair():
    mass, net, path = _track("S101", 300)
    assert mass == pytest.approx(0.8736, abs=0.01)
    assert net == pytest.approx(path, rel=0.02)  # straight line
    assert net / 30 == pytest.approx(0.4727, abs=0.01)  # R per time unit, 30 time units


def test_s102_circles_in_place():
    mass, net, path = _track("S102", 300)
    assert mass == pytest.approx(0.522, abs=0.03)
    assert path / 30 > 0.4  # moves about as fast as Orbium...
    assert net < 1.0  # ...but stays within about one kernel radius
