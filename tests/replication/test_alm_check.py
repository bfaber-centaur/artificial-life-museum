"""Lane 3: the independent implementation agrees with every other path we have."""

import numpy as np
import pytest

import alm_check as c
from alm_check.lenia import ORBIUM_RLE, REPO

S001 = REPO / "research" / "specimens" / "S001-orbium"


def test_rle_decoder_matches_lane1_cells():
    ours = c.decode_rle(ORBIUM_RLE)
    lane1 = np.loadtxt(S001 / "initial-cells-u8.csv", delimiter=",", dtype=int)
    assert ours.shape == (20, 20)
    assert (ours == lane1).all()
    assert ours.sum() == 19600


def test_fft_and_direct_paths_agree():
    A = c.place(c.load_orbium(), 64)
    worlds = [c.World(A.copy(), c.Rule(), path=p) for p in ("fft", "direct")]
    for _ in range(50):
        for w in worlds:
            w.step()
    assert np.abs(worlds[0].A - worlds[1].A).max() < 1e-12


def test_dead_edge_equals_torus_before_contact():
    A = c.place(c.load_orbium(), 128)
    torus = c.World(A.copy(), c.Rule(), path="direct", boundary="wrap")
    dead = c.World(A.copy(), c.Rule(), path="direct", boundary="constant")
    for _ in range(20):
        torus.step()
        dead.step()
    assert np.array_equal(torus.A, dead.A)


def test_matches_lane1_reference_trace():
    ref = np.genfromtxt(S001 / "reference-trace.csv", delimiter=",", names=True)
    tr = c.run(c.World(c.place(c.load_orbium(), 128), c.Rule()), 300, every=10)
    for k in ("mass", "growth", "gyradius", "cx", "cy", "speed"):
        a, b = tr[k], ref[k][: len(tr[k])]
        m = np.isfinite(a) & np.isfinite(b)
        assert np.allclose(a[m], b[m], atol=1e-3 if k in ("cx", "cy") else 2e-6), k


@pytest.mark.skipif(not (REPO / ".refs/Lenia/Python/LeniaND.py").exists(), reason="no upstream checkout")
def test_matches_upstream_automaton():
    from alm_check.upstream import upstream_automaton

    A = c.place(c.load_orbium(), 128)
    up = upstream_automaton(A, c.Rule())
    ours = c.World(A.copy(), c.Rule())
    for _ in range(100):
        up.calc_once()
        ours.step()
    assert np.abs(up.world.cells - ours.A).max() < 1e-12


LANE2_TRACES = sorted((REPO / "research" / "traces").glob("S001-*/trace.csv"))


@pytest.mark.skipif(not LANE2_TRACES, reason="no Lane 2 S001 trace on this branch yet")
def test_lane2_baseline_trace_agrees(tmp_path):
    """Black-box: Lane 2's published S001 trace, first 2000 steps, vs alm_check."""

    from alm_check.compare_lane2 import compare

    src = LANE2_TRACES[0].parent
    lines = (src / "trace.csv").read_text().splitlines()
    every = int(lines[2].split(",")[0]) - int(lines[1].split(",")[0])
    (tmp_path / "trace.csv").write_text("\n".join(lines[: 2 + 2000 // every]) + "\n")
    res = compare(tmp_path)
    for k in ("mass", "growth", "gyradius", "speed"):
        assert res[k] < 1e-6, (k, res[k])
    assert res["cx"] < 1e-4 and res["cy"] < 1e-4
