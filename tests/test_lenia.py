"""Unit checks of the Lenia kernel, growth and update semantics."""

import json

import numpy as np
import pytest

from alm import rle, specimens
from alm.lenia import Lenia, Rule, growth, kernel, kernel_core


def test_kernel_normalised_symmetric_and_compact():
    rule = Rule()
    k = kernel((128, 128), rule)
    assert k.sum() == pytest.approx(1.0, abs=1e-14)
    assert (k >= 0).all()
    # centred at (0, 0) on the torus: symmetric under reflection
    assert np.allclose(k, np.roll(k[::-1, :], 1, axis=0))
    assert np.allclose(k, k.T)
    y = np.fft.fftfreq(128, 1 / 128)
    D = np.hypot(y[:, None], y[None, :]) / rule.R
    assert (k[D >= 1] == 0).all()
    assert k[0, 0] == 0  # core vanishes at r = 0


def test_kernel_core_families():
    r = np.array([0.0, 0.25, 0.5, 1.0])
    assert np.allclose(kernel_core("poly", r), [0, 0.75**4, 1, 0])
    assert np.allclose(kernel_core("exp", r), [0, np.exp(4 - 1 / 0.1875), 1, 0])


def test_growth_families():
    mu, s = 0.15, 0.015
    assert growth("poly", np.array(mu), mu, s) == pytest.approx(1.0)
    assert growth("exp", np.array(mu), mu, s) == pytest.approx(1.0)
    # poly growth has compact support |u - mu| < 3 sigma
    assert growth("poly", np.array(mu + 3 * s), mu, s) == pytest.approx(-1.0)
    assert growth("exp", np.array(mu + 3 * s), mu, s) > -1.0


def test_multi_ring_kernel_uses_beta():
    k = kernel((64, 64), Rule(R=10, beta=(1.0, 0.5)))
    # ring 1 peak (r = 0.25 R) is twice ring 2 peak (r = 0.75 R) before normalisation
    assert k[0, 2] / k[0, 7] == pytest.approx(2.0, rel=0.25)


def test_euler_clip_step_matches_direct_convolution():
    rng = np.random.default_rng(1)
    A = rng.random((32, 32)) * (rng.random((32, 32)) < 0.3)
    rule = Rule(R=5)
    sim = Lenia(rule, A)
    k = kernel(A.shape, rule)
    # direct periodic convolution U(x) = sum_n k(n) A(x + n)  (k is symmetric)
    U = np.zeros_like(A)
    for dy, dx in zip(*np.nonzero(k)):
        U += k[dy, dx] * np.roll(A, (-dy, -dx), axis=(0, 1))
    expect = np.clip(A + growth("poly", U, rule.mu, rule.sigma) / rule.T, 0, 1)
    sim.step()
    assert np.allclose(sim.A, expect, atol=1e-13)
    assert sim.t == 1


def test_periodic_translation_equivariance():
    spec = specimens.load("S001")
    A = spec.place(64)
    a, b = Lenia(spec.rule, A), Lenia(spec.rule, np.roll(A, (30, -17), axis=(0, 1)))
    for _ in range(50):
        a.step()
        b.step()
    assert np.allclose(np.roll(a.A, (30, -17), axis=(0, 1)), b.A, atol=1e-12)


def test_s001_cells_match_dossier():
    spec = specimens.load("S001")
    assert spec.cells.shape == (20, 20)
    assert int(spec.cells.sum()) == 19600
    A = spec.place(128)
    assert A.sum() / 13**2 == pytest.approx(0.4548, abs=1e-4)
    assert A[54:74, 54:74].sum() == A.sum()


def test_rle_decoder_roundtrip_small():
    assert rle.decode("A.B$2.pA!").tolist() == [[1, 0, 2], [0, 0, 25]]
    assert rle.decode("o2$b!").tolist() == [[255], [0], [0]]


@pytest.mark.skipif(not specimens.ANIMALS_JSON.exists(), reason="needs .refs/Lenia")
def test_catalog_o2u_matches_s001():
    cat = specimens.from_catalog("O2u")
    s001 = specimens.load("S001")
    assert np.array_equal(cat.cells, s001.cells)
    assert cat.rule == s001.rule


@pytest.mark.skipif(not specimens.ANIMALS_JSON.exists(), reason="needs .refs/Lenia")
def test_rle_decodes_whole_catalog():
    entries = [e for e in json.loads(specimens.ANIMALS_JSON.read_text()) if "cells" in e]
    for e in entries:
        a = rle.decode(e["cells"])
        assert a.ndim == 2 and a.min() >= 0 and a.max() <= 255
