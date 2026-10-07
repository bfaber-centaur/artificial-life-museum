import numpy as np
import pytest

from alm import disturb


def blob(n=64, cx=20.3, cy=40.7, r=5.0):
    dx, dy = disturb.offsets((n, n), cx, cy)
    return np.clip(1 - (dx ** 2 + dy ** 2) / r ** 2, 0, None)


def test_periodic_centroid_across_seam():
    A = blob(cx=0.0, cy=63.0)
    cx, cy = disturb.periodic_centroid(A)
    assert disturb.wrap(cx - 0.0, 64) == pytest.approx(0, abs=1e-6)
    assert disturb.wrap(cy - 63.0, 64) == pytest.approx(0, abs=1e-6)


def test_frame_heading_wraps():
    A = blob(cx=1.0, cy=30.0)
    f = disturb.frame_from(A, (63.0, 30.0))  # moved +2 in x across the seam
    assert (f.hx, f.hy) == pytest.approx((1.0, 0.0), abs=1e-6)
    assert f.port == pytest.approx((0.0, 1.0), abs=1e-6)


def test_attenuation_scales_mass_and_does_not_mutate():
    A = blob()
    f = disturb.Frame(20.3, 40.7, 1.0, 0.0)
    B = disturb.i001_attenuate(A, f, 0.25, 13)
    assert B.sum() == pytest.approx(0.75 * A.sum())
    assert np.array_equal(A, blob())


def test_central_deletion_radius_zero_is_identity():
    A = blob()
    f = disturb.Frame(20.3, 40.7, 1.0, 0.0)
    assert np.array_equal(disturb.i002_central_deletion(A, f, 0.0, 13), A)
    B = disturb.i002_central_deletion(A, f, 0.2, 13)  # radius 2.6 cells
    dx, dy = disturb.offsets(A.shape, 20.3, 40.7)
    assert np.all(B[dx ** 2 + dy ** 2 < 2.6 ** 2] == 0)
    assert np.array_equal(B[dx ** 2 + dy ** 2 >= 2.6 ** 2], A[dx ** 2 + dy ** 2 >= 2.6 ** 2])


def test_frontal_addition_is_ahead_and_clipped():
    A = np.zeros((64, 64))
    f = disturb.Frame(10.0, 10.0, 0.0, 1.0)  # heading +y
    B = disturb.i003_frontal_addition(A, f, 1.0, 13)
    y, x = np.unravel_index(np.argmax(B), B.shape)
    assert (x, y) == (10, 23)
    assert B.max() <= 1.0
    C = disturb.i003_frontal_addition(np.ones((64, 64)), f, 0.5, 13)
    assert C.max() == 1.0


def test_port_injury_removes_port_side_and_reaches_fraction():
    A = blob(cx=32.0, cy=32.0)
    f = disturb.Frame(32.0, 32.0, 1.0, 0.0)  # port normal = +y
    for s in (0.1, 0.3, 0.5, 0.9):
        B = disturb.i004_port_injury(A, f, s, 13)
        removed = 1 - B.sum() / A.sum()
        assert removed >= s - 1e-9
        assert removed < s + 0.15
        # every removed cell lies at y >= every surviving nonzero cell's y
        gone = (A > 0) & (B == 0)
        kept = B > 0
        ys = np.arange(64)[:, None] * np.ones((1, 64))
        assert ys[gone].min() >= ys[kept].max() - 0  # straight cut parallel to heading
    assert np.array_equal(disturb.i004_port_injury(A, f, 0.0, 13), A)


def test_classify_bands():
    b = disturb.BASELINE
    ok = dict(window_mass=[b["mass"]] * 50, window_gyr=[b["gyradius"]] * 50,
              window_speed=b["speed"], final_mass=b["mass"])
    assert disturb.classify(**ok) == "RECOVERED"
    assert disturb.classify(**{**ok, "final_mass": 0.0}) == "DIED"
    assert disturb.classify(**{**ok, "final_mass": 1.0}) == "EXPLODED"
    assert disturb.classify(**{**ok, "window_speed": 0.0}) == "TRANSFORMED"
    assert disturb.classify(**{**ok, "window_speed": 0.9 * b["speed"]}, band=0.05) == "TRANSFORMED"


def test_local_centroid_is_translation_exact_across_sizes():
    a = blob(n=64, cx=20.3, cy=40.7, r=9.0)
    b = blob(n=96, cx=52.3, cy=12.7, r=9.0)
    ca, cb = disturb.local_centroid(a), disturb.local_centroid(b)
    assert cb[0] - ca[0] == pytest.approx(32.0, abs=1e-9)
    assert (cb[1] - ca[1]) % 96 == pytest.approx(68.0, abs=1e-9)
