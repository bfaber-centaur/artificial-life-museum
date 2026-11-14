"""Fast checks for the SOUP engine (research/experiments/SOUP/soup.py)."""
import sys
from pathlib import Path

import numpy as np

SOUP = Path(__file__).resolve().parents[1] / "research" / "experiments" / "SOUP"
sys.path.insert(0, str(SOUP))

import soup  # noqa: E402


def world(n=64, seed=0):
    kern = soup.Kernels(np.random.default_rng([7, 16]), R=6.0)
    rng = np.random.default_rng(seed)
    A = rng.uniform(0, 0.4, (n, n))
    G = np.where(np.arange(n)[None, None, :] < n // 2, 0.2, 0.8) * np.ones((kern.K, n, n))
    return kern, A, G


def test_mass_and_genome_mass_conserved_under_blending():
    kern, A, G = world()
    S = soup.Soup(kern, A, G, mut_every=0, inherit="blend")
    m0, q0 = S.A.sum(), (S.A[None] * S.G).sum((1, 2))
    for _ in range(30):
        S.step()
    assert abs(S.A.sum() / m0 - 1) < 1e-10
    assert np.allclose((S.A[None] * S.G).sum((1, 2)), q0, rtol=1e-9)  # averaging conserves "genome mass"


def test_dominant_never_invents_new_genomes():
    kern, A, G = world()
    S = soup.Soup(kern, A, G, mut_every=0, inherit="dominant")
    for _ in range(30):
        S.step()
    assert abs(S.A.sum() / A.sum() - 1) < 1e-10
    vals = np.unique(np.round(S.G[0][S.A > 1e-6], 6))
    # every cell still holds one of the two founder genomes (up to parcels split within one offset)
    near = np.minimum(np.abs(vals - 0.2), np.abs(vals - 0.8))
    assert (near < 1e-6).mean() > 0.95


def test_mutation_is_logged_and_deterministic():
    kern, A, G = world()
    runs = []
    for _ in range(2):
        S = soup.Soup(kern, A, G, mut_every=5, seed=3)
        for _ in range(20):
            S.step()
        runs.append((S.A.copy(), S.G.copy(), list(S.log)))
    assert len(runs[0][2]) == 4
    assert np.array_equal(runs[0][0], runs[1][0]) and np.array_equal(runs[0][1], runs[1][1])
