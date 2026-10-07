"""Tests for alm.morphometrics on synthetic shapes with known answers, plus the S001 start state."""

import math
from pathlib import Path

import numpy as np
import pytest

from alm import morphometrics as f

ROOT = Path(__file__).resolve().parents[1]
S001_CELLS = ROOT / "research" / "specimens" / "S001-orbium" / "initial-cells-u8.csv"


def gaussian(shape, center, sy, sx=None, angle_deg=0.0):
    """Periodic anisotropic Gaussian blob; major axis sx along angle_deg from +x toward +y."""
    sx = sy if sx is None else sx
    dy, dx = f.offsets(shape, center)
    a = math.radians(angle_deg)
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    return np.exp(-0.5 * ((u / sx) ** 2 + (v / sy) ** 2))


def s001_state(n=128):
    cells = np.loadtxt(S001_CELLS, delimiter=",")
    A = np.zeros((n, n))
    o = (n - 20) // 2
    A[o:o + 20, o:o + 20] = cells / 255.0
    return A


# --- mass and area ----------------------------------------------------------


def test_mass_and_area_units():
    A = np.zeros((32, 32))
    A[:4, :5] = 0.5
    A[10, 10] = 0.05
    assert f.mass(A) == pytest.approx(10.05)
    assert f.mass(A, R=2) == pytest.approx(10.05 / 4)
    assert f.occupied_area(A) == 20
    assert f.occupied_area(A, threshold=0.01, R=2) == pytest.approx(21 / 4)


# --- centroid ---------------------------------------------------------------


@pytest.mark.parametrize("center", [(20.3, 40.7), (0.4, 63.6), (63.9, 0.2)])
def test_centroid_of_symmetric_blob_including_across_the_seam(center):
    A = gaussian((64, 64), center, 4.0)
    cy, cx = f.centroid(A)
    assert f.displacement(center, (cy, cx), A.shape) == pytest.approx((0, 0), abs=1e-9)


def test_centroid_of_asymmetric_body_matches_linear_centroid_and_is_roll_covariant():
    A = np.zeros((96, 96))
    A[40:50, 30:36] = 1.0
    A[44:46, 36:52] = 0.3   # a tail makes the body asymmetric
    y, x = np.indices(A.shape)
    linear = ((A * y).sum() / A.sum(), (A * x).sum() / A.sum())
    assert f.centroid(A) == pytest.approx(linear, abs=1e-9)
    shift = (60, 70)   # pushes the body across both seams
    B = np.roll(A, shift, axis=(0, 1))
    expected = ((linear[0] + shift[0]) % 96, (linear[1] + shift[1]) % 96)
    assert f.displacement(expected, f.centroid(B), B.shape) == pytest.approx((0, 0), abs=1e-9)


def test_centroid_rejects_empty_state():
    with pytest.raises(ValueError):
        f.centroid(np.zeros((8, 8)))


# --- velocity ---------------------------------------------------------------


def test_velocity_unwraps_seam_and_converts_units():
    shape = (64, 64)
    # 1.5 cells/step in x, -0.5 in y, sampled every 2 steps, crossing both seams.
    cs = [((5 - 1.0 * i) % 64, (60 + 3.0 * i) % 64) for i in range(10)]
    v = f.velocity(cs, shape, every=2)
    assert v == pytest.approx(np.tile([-0.5, 1.5], (9, 1)))
    # R=13, T=10: (cells/step) * T / R
    vr = f.velocity(cs, shape, every=2, T=10, R=13)
    assert vr[0] == pytest.approx([-0.5 * 10 / 13, 1.5 * 10 / 13])


# --- second moment, gyradius, anisotropy -----------------------------------


def test_second_moment_of_axis_aligned_gaussian():
    A = gaussian((128, 128), (64, 64), sy=3.0, sx=6.0)
    M = f.second_moment(A)
    assert M[1, 1] == pytest.approx(36.0, rel=1e-6)   # Ixx
    assert M[0, 0] == pytest.approx(9.0, rel=1e-6)    # Iyy
    assert M[0, 1] == pytest.approx(0.0, abs=1e-9)
    assert f.gyradius(A, R=2.0) == pytest.approx(math.sqrt(45.0) / 2, rel=1e-6)
    e, ang = f.anisotropy(A)
    assert e == pytest.approx(0.75, rel=1e-6)
    assert min(ang, 180 - ang) == pytest.approx(0.0, abs=1e-6)


@pytest.mark.parametrize("angle", [30.0, 90.0, 135.0])
def test_anisotropy_axis_follows_rotation(angle):
    A = gaussian((128, 128), (64.2, 63.7), sy=3.0, sx=7.0, angle_deg=angle)
    e, ang = f.anisotropy(A)
    assert e == pytest.approx(1 - 9 / 49, rel=1e-3)
    diff = (ang - angle) % 180
    assert min(diff, 180 - diff) == pytest.approx(0.0, abs=0.1)


def test_isotropic_blob_has_no_anisotropy():
    e, _ = f.anisotropy(gaussian((64, 64), (31.5, 31.5), 5.0))
    assert e == pytest.approx(0.0, abs=1e-6)


# --- rotational harmonics ---------------------------------------------------


def test_rotational_harmonics_detect_k_fold_symmetry():
    shape, c = (128, 128), (64.0, 64.0)
    dy, dx = f.offsets(shape, c)
    r, th = np.hypot(dx, dy), np.arctan2(dy, dx)
    ring = np.exp(-0.5 * ((r - 15) / 3) ** 2)
    disk_h = f.rotational_harmonics(ring, c, kmax=6)
    assert np.all(disk_h[1:] < 1e-2)

    tri = ring * (1 + 0.8 * np.cos(3 * th))
    h = f.rotational_harmonics(tri, c, kmax=6)
    assert f.symmetry_order(h) == 3
    assert h[3] > 0.3
    assert max(h[1], h[2], h[4], h[5]) < 2e-2


def test_features_are_translation_invariant_on_s001():
    A = s001_state()
    B = np.roll(A, (70, -50), axis=(0, 1))
    sa, sb = f.snapshot(A, R=13), f.snapshot(B, R=13)
    for k in sa:
        if k in ("cy", "cx"):
            continue
        assert sb[k] == pytest.approx(sa[k], abs=1e-9), k


# --- S001 start state agrees with the Lane 1 reference trace ----------------


def test_s001_start_state_matches_reference_trace_row0():
    snap = f.snapshot(s001_state(), R=13)
    # reference-trace.csv step 0: mass 0.454809, gyradius 0.455188 (R units)
    assert snap["mass"] == pytest.approx(19600 / 255 / 169, rel=1e-12)
    assert snap["mass"] == pytest.approx(0.454809, abs=1e-6)
    assert snap["gyradius"] == pytest.approx(0.455188, abs=2e-6)
    # Lane 1's circular-mean centroid (64.599, 64.516) is biased by ~0.01 cell;
    # ours must be within a few hundredths of a cell of it.
    assert snap["cy"] == pytest.approx(64.599, abs=0.03)
    assert snap["cx"] == pytest.approx(64.516, abs=0.03)
    assert snap["wrap_extent"] < 0.5


def test_snapshot_of_empty_state():
    s = f.snapshot(np.zeros((16, 16)))
    assert s["mass"] == 0 and s["area"] == 0
    assert math.isnan(s["gyradius"]) and math.isnan(s["cx"])


def test_wrap_extent_flags_debris_on_far_side():
    A = gaussian((64, 64), (32, 32), 3.0)
    assert f.wrap_extent(A) < 0.6
    A[0, 0] = 0.5
    assert f.wrap_extent(A) > 0.95


# --- dominant period --------------------------------------------------------


@pytest.mark.parametrize("period", [4.32, 14.29, 37.0])
def test_dominant_period_is_sub_bin_accurate(period):
    t = np.arange(3000)
    x = 0.436 + 1e-3 * np.sin(2 * np.pi * t / period + 0.3)
    assert f.dominant_period(x) == pytest.approx(period, rel=5e-3)
    if period > 4 * 2:   # sampled every 2 steps (well above Nyquist) the answer is still in steps
        assert f.dominant_period(x[::2], every=2) == pytest.approx(period, rel=5e-3)


def test_dominant_period_of_constant_series_is_nan():
    assert math.isnan(f.dominant_period(np.ones(100)))
    assert math.isnan(f.dominant_period([1.0, 2.0]))


# --- recovery time ----------------------------------------------------------


def test_recovery_time_cases():
    base = [1.0] * 5
    dip = base + [0.5, 0.7, 0.9, 0.98, 1.01, 0.99, 1.0, 1.0]
    # intervention at index 5; within 0.05 from index 8 onward -> 3 samples later
    assert f.recovery_time(dip, 1.0, 0.05, start=5) == 3
    assert f.recovery_time(dip, 1.0, 0.05, start=5, every=10) == 30
    # never left the band
    assert f.recovery_time(base, 1.0, 0.05) == 0
    # re-leaves the band at the end: not recovered
    assert f.recovery_time(dip + [0.5], 1.0, 0.05, start=5) == math.inf
    # recovered, but not long enough to satisfy hold
    assert f.recovery_time(dip, 1.0, 0.05, start=5, hold=6) == math.inf
    assert f.recovery_time(dip, 1.0, 0.05, start=5, hold=5) == 3


# --- runner integration -----------------------------------------------------


def test_morpho_feature_set_in_runner_trace():
    from alm import run

    res = run.run(run.RunConfig(steps=20, every=10, features=("basic", "morpho")), out_root=None)
    row = res.rows[0]
    assert row["morpho_gyradius"] == pytest.approx(0.455188, abs=2e-6)
    assert row["morpho_symmetry_order"] == 2
    assert "mass" in row and "morpho_mass" not in row
    assert f.displacement((row["cy_cells"], row["cx_cells"]),
                          (row["morpho_cy"], row["morpho_cx"]), (128, 128)) == pytest.approx((0, 0), abs=0.03)
