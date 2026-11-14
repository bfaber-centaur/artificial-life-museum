"""GEOM thread: point-cloud ("graph") Lenia must agree with alm.lenia on the square torus, and
the curved worlds must have the right size."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "experiments" / "GEOM"))

import geomlenia as g  # noqa: E402
from alm import specimens  # noqa: E402
from alm.lenia import Lenia  # noqa: E402


def test_graph_lenia_equals_alm_on_square_torus():
    s = specimens.load("S001")
    N = 48
    A0 = s.place(N)
    L = Lenia(s.rule, A0)
    G = g.GraphLenia(g.square_torus(N), s.rule, A0.ravel())
    for _ in range(60):
        L.step()
        G.step()
    assert np.abs(L.A.ravel() - G.A).max() < 1e-11


def test_patch_sampler_reproduces_cells_on_the_square_lattice():
    s = specimens.load("S001")
    w = g.square_torus(64)
    f = g.patch_sampler(s.cells / 255.0)
    h, wd = s.cells.shape
    centre = (32 + (wd - 1) / 2 - wd // 2, 32 + (h - 1) / 2 - h // 2)
    A = g.seed_torus(w, f, centre).reshape(64, 64)
    y0, x0 = 32 - h // 2, 32 - wd // 2
    assert np.abs(A[y0:y0 + h, x0:x0 + wd] - s.cells / 255.0).max() < 1e-9


def test_icosphere_area_and_kernel_rows():
    w = g.icosphere(12)
    assert abs(w.area.sum() - 4 * np.pi * 144) < 1e-6 * 4 * np.pi * 144
    W = g.kernel_matrix(w, specimens.load("S001").rule)
    assert np.allclose(np.asarray(W.sum(1)).ravel(), 1.0)


def test_hyperbolic_grid_area_matches_disk_area():
    kap, rmax = 13.0, 26.0
    w = g.hyper_grid(kap, rmax)
    area = 2 * np.pi * kap**2 * (np.cosh(rmax / kap) - 1)
    # truncation at rmax cuts boundary cells, so allow a boundary-strip error
    assert abs(w.area.sum() - area) / area < 0.08
    d = g.hyp_dist(w.xy, np.zeros_like(w.xy), kap)
    assert d.max() <= rmax + 1e-9


def test_hyperbolic_distance_is_an_isometry_invariant():
    rng = np.random.default_rng(0)
    z = (rng.random((50, 2)) - 0.5) * 1.2
    zc = z[:, 0] + 1j * z[:, 1]
    p = 0.3 - 0.2j
    m = (zc - p) / (1 - np.conj(p) * zc)
    zm = np.stack([m.real, m.imag], 1)
    assert np.allclose(g.hyp_dist(z[:-1], z[1:], 7.0), g.hyp_dist(zm[:-1], zm[1:], 7.0))
