"""Lane 7 hostile-review tests for S001 (H001): the mass wobble is a lattice artifact.

These encode the H001 findings as executable checks, using shortened runs of the
preregistered protocol (research/experiments/H001-lattice-wobble/PREREGISTRATION.md).
They need the pinned upstream catalog under .refs/Lenia (./scripts/bootstrap.sh).
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "research", "experiments", "H001-lattice-wobble"))
import h001  # noqa: E402

STEPS, START = 1600, 600


@pytest.fixture(scope="module")
def runs():
    out = {}
    for R in (13, 26):
        ms, cs, N = h001.run(R, 0, steps=STEPS, start=START)
        out[R] = (ms, h001.velocity(cs, N))
    return out


@pytest.mark.parametrize("R", [13, 26])
def test_wobble_frequency_sits_on_a_lattice_line(runs, R):
    # Poisson summation: a translating profile sampled on a unit grid can only change
    # its total mass at frequencies m*vx + n*vy (folded). The dominant peak must sit there.
    ms, (vx, vy) = runs[R]
    f = h001.dominant_freq(ms)
    _, _, err = h001.nearest_line(f, vx, vy)
    assert err <= h001.TOL


def test_wobble_shrinks_when_resolution_doubles(runs):
    # A real internal oscillation would keep its relative amplitude when the same
    # creature is resolved by twice as many cells; a lattice artifact must shrink.
    rel = {R: ms.std() / ms.mean() for R, (ms, _) in runs.items()}
    assert rel[26] < rel[13] / 2


def test_mean_mass_is_resolution_independent(runs):
    # The wobble is a sampling effect on top of a resolution-stable mean.
    m13 = runs[13][0].mean() / 13 ** 2
    m26 = runs[26][0].mean() / 26 ** 2
    assert abs(m13 - m26) / m13 < 1e-3


def _heading(R, rot, steps=2500, start=1500):
    _, cs, N = h001.run(R, rot, steps=steps, start=start)
    vx, vy = h001.velocity(cs, N)
    return h001.np.degrees(h001.np.arctan2(vy, vx))


def test_heading_is_pinned_by_the_lattice_at_R13():
    # Characterization test (H001 exploratory finding, x1_R13.csv). Starting S001 rotated
    # by 6 deg and by 9 deg should, in an isotropic continuum, give headings 3 deg apart.
    # On the R=13 lattice both snap to the same heading (60.82 deg). If this test starts
    # failing, the simulator's lattice behaviour changed and H001 must be re-run.
    h6, h9 = _heading(13, 6), _heading(13, 9)
    assert abs(h6 - 60.82) < 0.1
    assert abs(h9 - 60.82) < 0.1


def test_axis_heading_distorts_shape_at_R13():
    # HR-006: Lane 5's "feature means are heading-invariant" fails at R = 13. S001 locked to
    # the lattice axis (start rotation 70 deg) is ~10% less elongated than on the 5:2 plateau.
    import heading_means

    on_plateau = heading_means.measure((13, 0))
    on_axis = heading_means.measure((13, 70))
    assert abs(on_axis[2]) < 3  # really travelling along the axis
    assert on_axis[6] < 0.9 * on_plateau[6]
