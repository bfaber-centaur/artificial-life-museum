"""KLEIN: Lenia on a Klein bottle via its glide-symmetric double cover (C102-C104)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "experiments" / "KLEIN"))

import klein as K  # noqa: E402
import kview as kv  # noqa: E402
from alm import specimens  # noqa: E402
from alm.lenia import Lenia  # noqa: E402


def test_cover_stays_glide_symmetric():
    """The re-imposed symmetry only removes round-off: one plain step of the double cover keeps
    A[y + Ny, x] = A[y, -x] to 1e-12, so the Klein bottle is the torus dynamics restricted."""
    s = specimens.load("S001")
    w = K.Klein(s.rule, K.place(s.cells, (40, 64), (35, 10), k=0))  # straddles the twisted seam
    for _ in range(30):
        w.step()
    L = Lenia(s.rule, w.full.copy())
    L.step()
    ny = w.ny
    assert np.abs(L.A[ny:] - K.mirror_x(L.A[:ny])).max() < 1e-12
    w.step()
    assert np.abs(w.full - L.A).max() < 1e-12


def test_mirror_and_bodies():
    A = np.zeros((6, 8))
    A[2, 1] = 1
    assert K.mirror_x(A)[2, 7] == 1
    B = np.zeros((10, 10))
    B[0, 3] = B[9, 3] = B[4, 0] = B[4, 9] = 2.0  # two bodies, each split by a periodic edge
    assert sorted(m for _, m in K.bodies(B)) == [4.0, 4.0]


def test_bottle_gluing_matches_klein():
    """Immersion: (u = pi, v) is the point (u = 0, pi - v), i.e. chart x -> -x across the seam."""
    v = np.linspace(0, 2 * np.pi, 13)
    assert np.allclose(kv.bottle(np.pi, v), kv.bottle(0.0, np.pi - v))
    f = np.linspace(0, 1, 50)
    u = kv.arc_u(f)
    assert abs(u[0]) < 1e-12 and abs(u[-1] - np.pi) < 1e-12 and np.all(np.diff(u) > 0)
