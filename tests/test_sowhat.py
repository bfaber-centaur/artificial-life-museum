"""Fast checks for the "So what?" wing demos (research/experiments/SOWHAT/)."""
import sys
from pathlib import Path

import numpy as np

SOWHAT = Path(__file__).resolve().parents[1] / "research" / "experiments" / "SOWHAT"
sys.path.insert(0, str(SOWHAT))

import drift  # noqa: E402
import epidemic as ep  # noqa: E402
import turing  # noqa: E402


def test_moran_formula_limits():
    assert drift.moran_exact(50, 0.0) == 1 / 50
    assert abs(drift.moran_exact(50, 1e-9) - 1 / 50) < 1e-6      # continuous through neutral
    assert drift.moran_exact(50, 0.1) > 1 / 50 > drift.moran_exact(50, -0.1)
    assert abs(drift.moran_exact(10_000, 0.1) - (1 - 1 / 1.1)) < 1e-12  # large N: 1 - 1/r


def test_moran_simulation_matches_formula():
    rng = np.random.default_rng(0)
    reps, N, s = 20000, 10, 0.1
    rho = drift.moran_exact(N, s)
    sim = drift.moran_fixations(N, s, reps, rng) / reps
    assert abs(sim - rho) < 4 * np.sqrt(rho * (1 - rho) / reps)


def test_wright_fisher_paths_absorb():
    P = drift.wright_fisher_paths(100, 0.05, 200, 3000, np.random.default_rng(1))
    assert P.shape == (3001, 200)
    assert np.all((P[-1] == 0) | (P[-1] == 1))
    assert np.all(P[0] == 0.01)


def test_gray_scott_batch_matches_single_world_reference():
    sys.path.insert(0, str(SOWHAT.parent / "WINGS"))
    from other_worlds import GrayScott
    u0, v0 = turing.initial(32, np.random.default_rng(3), squares=2, half=4)
    F, k = np.array([0.03, 0.05]), np.array([0.06, 0.062])
    _, v = turing.run(F, k, u0, v0, 200, 100)
    for i in range(2):
        g = GrayScott(F=F[i], k=k[i], u=u0, v=v0)
        for _ in range(200):
            g.step()
        assert np.allclose(v[i], g.v, atol=1e-12)


def test_epidemic_counts_and_recovery_only():
    E = ep.Epidemic(40, "lattice", seed=0)
    assert np.isclose(E.counts().sum(), 1) and E.counts()[1] == 9 / 1600
    prev_r = 0
    for _ in range(50):
        E.step()
        c = E.counts()
        assert c[2] >= prev_r            # nobody leaves R
        prev_r = c[2]


def test_lattice_infection_is_local():
    E = ep.Epidemic(40, "lattice", beta=1.0, gamma=0.0, seed=0)
    E.step()
    infected = np.argwhere(E.x == ep.I)
    # a 3x3 block grows to a 5x5 diamond-ish plus-shape: nothing beyond distance 1 of the block
    assert infected.min() >= 18 and infected.max() <= 22
    assert (E.x == ep.I).sum() == 9 + 12


def test_shortcuts_with_p_zero_equals_lattice():
    # with beta 1 and gamma 0 nothing is random, so p = 0 shortcuts must equal the lattice
    a = ep.Epidemic(30, "lattice", beta=1.0, gamma=0.0, seed=5)
    b = ep.Epidemic(30, "shortcuts", beta=1.0, gamma=0.0, p=0.0, seed=5)
    for _ in range(5):
        a.step()
        b.step()
    assert np.array_equal(a.x, b.x)
