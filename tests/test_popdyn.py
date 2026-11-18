"""Population-dynamics round: neutral-marker plan (SOUP/neutral.py) and the therapy toy (REPLICATORS/therapy.py)."""
import sys
from pathlib import Path

import numpy as np
import pytest

from alm import specimens

ROOT = Path(__file__).resolve().parents[1] / "research" / "experiments"
sys.path.insert(0, str(ROOT / "SOUP"))
sys.path.insert(0, str(ROOT / "REPLICATORS"))

import neutral  # noqa: E402
import therapy  # noqa: E402


def test_neutral_plan_covers_the_72_replay_places_without_touching_discs():
    A0 = np.random.default_rng(0).uniform(0, 1, (neutral.N, neutral.N))
    groups = neutral.plan(A0, K=10)
    flat = [p[:2] for g in groups for p in g]
    assert sorted(flat) == [(k, j) for k in range(12) for j in range(6)]
    for g in groups:
        assert len(g) <= 10
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                assert neutral.tdist(g[i], g[j]) > 21


needs_refs = pytest.mark.skipif(not specimens.ANIMALS_JSON.exists(), reason="upstream Lenia reference not checked out")


@needs_refs
def test_drug_hits_fast_genomes_and_adaptive_switches_off():
    rng = np.random.default_rng(1)
    A = rng.uniform(0, 0.5, (32, 32))
    B0 = float(A.sum())
    fast = therapy.treat(A, np.ones_like(A), "constant", 0, B0, 2.0, kappa=0.5, every=1.0)
    slow = therapy.treat(A, np.zeros_like(A), "constant", 0, B0, 2.0, kappa=0.5, every=1.0)
    none = therapy.treat(A, np.ones_like(A), "none", 0, B0, 2.0, kappa=0.5, every=1.0)
    assert fast["trace"][-1][1] < none["trace"][-1][1]
    assert abs(slow["drug_time"] - 2.0) < 1e-9 and abs(none["drug_time"]) < 1e-12
    # adaptive starts with the drug on and stops once the burden is at or below half of B0
    ad = therapy.treat(A, np.ones_like(A), "adaptive", 0, 2.5 * B0, 1.0, kappa=0.5)
    assert ad["drug_time"] == 0.0


class _W:
    def __init__(self, A, g):
        self.A, self.g, self.dt = A.copy(), g.copy(), 0.1


def test_crowding_cost_hits_slow_matter_in_crowds_and_is_off_by_default():
    A = np.full((32, 32), therapy.CARRY)
    g = np.zeros_like(A); g[:, 16:] = 1.0
    w = _W(A, g)
    therapy.crowding_cost(w, 0.0)
    assert np.array_equal(w.A, A)  # cost 0: untouched, so C119-C121 runs are unchanged
    therapy.crowding_cost(w, 0.3)
    assert w.A[:, 2:14].mean() < A[:, 2:14].mean()  # slow half, full crowd: decays
    assert np.allclose(w.A[:, 18:30], A[:, 18:30])  # fast (g = 1) half: no cost
    sparse = _W(np.full((32, 32), 0.1 * therapy.CARRY), np.zeros((32, 32)))
    therapy.crowding_cost(sparse, 0.3)
    loss_sparse = 1 - sparse.A.mean() / (0.1 * therapy.CARRY)
    assert 0 < loss_sparse < 1 - w.A[:, 2:14].mean() / therapy.CARRY  # less crowded, smaller cost


import therapy2  # noqa: E402


def test_therapy2_policies():
    st = {}
    assert therapy2.holiday(1999.9, 1.0, 0.0, st) == (True, False)
    assert therapy2.holiday(2000.0, 1.0, 0.0, st) == (False, False)
    p, st = therapy2.adaptive(0.5), {}
    assert p(0, 1.0, 0, st) == (True, False)
    assert p(1, 0.5, 0, st) == (False, False)   # paused at LOW
    assert p(2, 0.9, 0, st) == (False, False)   # stays off until back at 1.0
    assert p(3, 1.0, 0, st) == (True, False)
    assert therapy2.alternate(50, 1, 0, {}) == (True, False) and therapy2.alternate(150, 1, 0, {}) == (False, True)
    st = {}
    assert therapy2.steer(0, 1, 0.4, st) == (True, False)
    assert therapy2.steer(1, 1, 0.6, st) == (False, True)    # mostly resistant: drug B
    assert therapy2.steer(2, 1, 0.3, st) == (False, True)    # hysteresis
    assert therapy2.steer(3, 1, 0.1, st) == (True, False)


@needs_refs
def test_drug_b_hits_slow_genomes_and_matches_treat_for_drug_a():
    rng = np.random.default_rng(2)
    A = rng.uniform(0, 0.5, (32, 32))
    B0 = float(A.sum())
    def loss(g):  # burden lost to drug B relative to the same world with no drug
        off = therapy2.run(A, g, 0, B0, 2.0, lambda *a: (False, False), 0.0, every=1.0)
        on = therapy2.run(A, g, 0, B0, 2.0, therapy2.only_b, 0.0, every=1.0)
        return off["trace"][-1][1] - on["trace"][-1][1]
    assert loss(np.zeros_like(A)) > 0.03 and abs(loss(np.ones_like(A))) < 1e-9
    # drug A alone under therapy2.run reproduces therapy.treat (constant arm) exactly
    g = rng.uniform(0, 1, A.shape)
    a = therapy2.run(A, g, 0, B0, 2.0, therapy2.constant, 0.1, kA=0.5, every=1.0)
    b = therapy.treat(A, g, "constant", 0, B0, 2.0, kappa=0.5, every=1.0, cost=0.1)
    assert a["final_sha"] == b["final_sha"]
