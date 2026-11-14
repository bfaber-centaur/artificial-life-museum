"""Fast checks for the WINGS simulators (research/experiments/WINGS)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

WINGS = Path(__file__).resolve().parents[1] / "research" / "experiments" / "WINGS"
sys.path.insert(0, str(WINGS))

from alm import rle, specimens  # noqa: E402
from alm.lenia import Lenia, Rule  # noqa: E402

import flow_lenia  # noqa: E402
import nd_lenia  # noqa: E402
import other_worlds  # noqa: E402

needs_refs = pytest.mark.skipif(not specimens.ANIMALS_JSON.exists(), reason="upstream Lenia reference not checked out")


def test_nd_lenia_one_channel_matches_alm():
    A0 = specimens.load("S001").place(128)
    rule = Rule(R=13, T=10, mu=0.15, sigma=0.015)
    a = Lenia(rule, A0)
    b = nd_lenia.NDLenia([{"R": 13, "T": 10, "b": "1", "m": 0.15, "s": 0.015, "kn": 1, "gn": 1}], A0[None])
    for _ in range(50):
        a.step()
        b.step()
    assert np.abs(a.A - b.A[0]).max() < 1e-12


@needs_refs
def test_nd_rle_decode_matches_alm_2d():
    e = json.loads(specimens.ANIMALS_JSON.read_text(encoding="utf-8"))
    e = [x for x in e if isinstance(x, dict) and "cells" in x][3]
    np.testing.assert_allclose(nd_lenia.rle_decode(e["cells"], 2), rle.decode(e["cells"]) / 255.0)


@needs_refs
def test_nd_rle_decode_3d_shape():
    e = nd_lenia.load_catalog("animals3D.json")[2]  # 4Gu3l
    A = nd_lenia.rle_decode(e["cells"], 3)
    assert A.ndim == 3 and A.max() <= 1 and A.sum() > 100


def test_flow_lenia_conserves_mass():
    rng = np.random.default_rng([7, 43])
    rule = flow_lenia.FlowRule.random(rng)
    A = np.zeros((64, 64))
    A[22:42, 22:42] = np.random.default_rng(0).uniform(0, 1, (20, 20))
    L = flow_lenia.FlowLenia(rule, A)
    m0 = L.A.sum()
    for _ in range(40):
        L.step()
    assert abs(L.A.sum() / m0 - 1) < 1e-12
    assert L.A.min() >= 0


def test_flow_lenia_reintegration_moves_mass_without_loss():
    rule = flow_lenia.FlowRule.random(np.random.default_rng(1))
    L = flow_lenia.FlowLenia(rule, np.zeros((32, 32)))
    A = np.zeros((32, 32))
    A[10, 10] = 1.0
    L.A = A
    L.step()
    assert abs(L.A.sum() - 1) < 1e-14


def test_gray_scott_trivial_state_is_fixed():
    G = other_worlds.GrayScott(0.0367, 0.0649, np.ones((16, 16)), np.zeros((16, 16)))
    for _ in range(10):
        G.step()
    assert np.all(G.u == 1) and np.all(G.v == 0)


def test_particle_lenia_gradient_matches_finite_difference():
    P = np.random.default_rng(3).uniform(-4, 4, (12, 2))
    L = other_worlds.ParticleLenia(P)
    E, _, g = L.fields()
    h = 1e-6
    for i in (0, 5):
        for d in (0, 1):
            Pp = P.copy(); Pp[i, d] += h
            Pm = P.copy(); Pm[i, d] -= h
            # E_i as a function of particle i's own position (fields from the others held fixed)
            Ep = L.fields(Pp)[0][i]
            Em = L.fields(Pm)[0][i]
            assert abs((Ep - Em) / (2 * h) - g[i, d]) < 1e-5


def test_smoothlife_kernels_normalised_and_bounded():
    A = np.random.default_rng(0).uniform(0, 1, (64, 64))
    S = other_worlds.SmoothLife(A, ra=8)
    m = np.fft.irfft2(np.fft.rfft2(np.ones((64, 64))) * S._kh[0], s=(64, 64))
    assert np.allclose(m, 1)
    S.step()
    assert 0 <= S.A.min() and S.A.max() <= 1
