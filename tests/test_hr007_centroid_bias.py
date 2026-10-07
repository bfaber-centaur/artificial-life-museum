"""Lane 7 HR-007: the circular-mean centroid has a torus-size-dependent bias.

Lane 4 places I002-I004 edits at the circular-mean centroid. That estimator's bias falls as
1/N^2, so the same creature gets its edit placed ~0.007 cells differently on a 128 and a 192
torus. Near a survive/die edge that is enough to flip the outcome (3 of 40 L4-001 bracket runs,
research/experiments/HR007-c023-world-size/). A bias-corrected centroid is N-independent.
"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "research", "experiments", "H001-lattice-wobble"))
import h001  # noqa: E402


def refined(A, N, iterations=3):
    c = h001.centroid(A, N)
    m, i = A.sum(), np.arange(N)
    for _ in range(iterations):
        c = np.array([(c[0] + (A.sum(0) * ((i - c[0] + N / 2) % N - N / 2)).sum() / m) % N,
                      (c[1] + (A.sum(1) * ((i - c[1] + N / 2) % N - N / 2)).sum() / m) % N])
    return c


@pytest.fixture(scope="module")
def centroids():
    out = {}
    for N in (128, 192):
        A = h001.initial_state(13, 0, N)
        kfft, _ = h001.rc.make_kernel_fft(N, 13, [1.0], "poly")
        for _ in range(1000):
            A, _ = h001.rc.step(A, kfft, h001.MU, h001.SIGMA, h001.T, "poly")
        out[N] = (h001.centroid(A, N), refined(A, N))
    return out


def test_circular_mean_centroid_depends_on_torus_size(centroids):
    # Same creature, same sub-pixel position: the fractional circular-mean centroid moves.
    shift = np.abs(centroids[128][0] % 1 - centroids[192][0] % 1)
    assert shift.max() > 0.005


def test_bias_falls_as_inverse_square_of_torus_size(centroids):
    b128 = np.abs(centroids[128][0] - centroids[128][1]).max()
    b192 = np.abs(centroids[192][0] - centroids[192][1]).max()
    assert b192 / b128 == pytest.approx((128 / 192) ** 2, rel=0.1)


def test_refined_centroid_is_torus_size_independent(centroids):
    assert np.abs(centroids[128][1] % 1 - centroids[192][1] % 1).max() < 1e-4
