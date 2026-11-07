"""Tests for the REEF-behavior tracker: translation, wrap, merge, split, plus bookkeeping.

    PYTHONPATH=src python -m pytest -q research/experiments/REEF-behavior/test_track.py
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from track import ImageGuard, Tracker, TrackerConfig, components, label_torus, superposition_defect, support_gap  # noqa: E402

N = 64


def disc(n, cy, cx, r, amp=1.0):
    """A smooth disc (Gaussian-edged) centred at (cy, cx) on an n x n torus."""
    y = np.arange(n)[:, None]
    x = np.arange(n)[None, :]
    dy = (y - cy + n / 2) % n - n / 2
    dx = (x - cx + n / 2) % n - n / 2
    d = np.hypot(dy, dx)
    return amp * np.clip(1.2 - d / r, 0, 1) ** 2


def bfs_labels(mask):
    ny, nx = mask.shape
    lab = -np.ones(mask.shape, int)
    n = 0
    for y in range(ny):
        for x in range(nx):
            if mask[y, x] and lab[y, x] < 0:
                st = [(y, x)]
                lab[y, x] = n
                while st:
                    a, b = st.pop()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            c, d = (a + dy) % ny, (b + dx) % nx
                            if mask[c, d] and lab[c, d] < 0:
                                lab[c, d] = n
                                st.append((c, d))
                n += 1
    return lab, n


@pytest.mark.parametrize("p", [0.15, 0.35, 0.55])
def test_labels_match_bruteforce_torus_bfs(p):
    rng = np.random.default_rng(int(p * 100))
    for _ in range(4):
        m = rng.random((19, 27)) < p
        a, na = label_torus(m)
        b, nb = bfs_labels(m)
        assert na == nb
        assert len(set(zip(a[m], b[m]))) == na  # same partition


def test_component_across_both_edges_is_one():
    A = disc(N, 0, 0, 4)  # centred on the corner: four quadrants on the array
    comps = components(A, 0.1)
    assert len(comps) == 1
    cy, cx = comps[0].centroid
    assert min(cy, N - cy) < 1e-9 and min(cx, N - cx) < 1e-9


def test_translation_known_shift():
    A0 = disc(N, 20, 20, 4)
    tr = Tracker(A0, {"G": A0 > 0.1})
    for k in range(1, 31):
        tr.update(np.roll(A0, (0, k), (0, 1)), k)
    r = tr.records[-1]["labels"]["G"]
    assert r["status"] == "single"
    assert np.allclose(np.subtract(r["unwrapped"], tr.records[0]["labels"]["G"]["unwrapped"]), (0, 30), atol=1e-9)
    assert tr.events == []


def test_wrap_across_both_edges_many_times():
    A0 = disc(N, 50, 55, 4)
    tr = Tracker(A0, {"G": A0 > 0.1})
    steps = 2 * N + 7  # crosses each edge twice and then some
    for k in range(1, steps + 1):
        tr.update(np.roll(A0, (k, 2 * k), (0, 1)), k)
        assert tr.records[-1]["n_bodies"] == 1
    r = tr.records[-1]["labels"]["G"]
    d = np.subtract(r["unwrapped"], tr.records[0]["labels"]["G"]["unwrapped"])
    assert np.allclose(d, (steps, 2 * steps), atol=1e-9)
    assert tr.events == []


def test_merge_reports_topology_not_two_centroids():
    G0 = disc(N, 32, 10, 4)
    S = disc(N, 32, 40, 4)
    tr = Tracker(G0 + S, {"G": G0 > 0.1, "S": S > 0.1})
    t_merge = None
    for k in range(1, 25):  # stop before the discs superpose (real bodies cannot; see README)
        A = np.roll(G0, (0, k), (0, 1)) + S
        rec = tr.update(A, k)
        if t_merge is None and rec["topology"] == "GS":
            t_merge = k
            assert rec["labels"]["G"]["status"] == rec["labels"]["S"]["status"] == "merged"
            assert "centroid" not in rec["labels"]["G"] and "centroid" not in rec["labels"]["S"]
            assert rec["support_gap"] <= np.sqrt(2)
            prev = tr.records[-2]
            assert prev["topology"] == "G|S" and prev["support_gap"] > np.sqrt(2)
    assert t_merge is not None
    assert [e["kind"] for e in tr.events] == ["merge"]
    # bookkeeping: total = support + halo, and nothing orphaned
    rec = tr.records[-1]
    assert abs(rec["total_mass"] - rec["support_mass"] - rec["halo_mass"]) < 1e-9
    assert rec["orphan_mass"] == 0.0


def test_split_is_fragmented_not_forced_single():
    a = disc(N, 32, 26, 4)
    b = disc(N, 32, 38, 4)
    bridge = np.zeros((N, N))
    bridge[31:34, 26:39] = 0.6
    A0 = np.maximum(a + b, bridge)
    tr = Tracker(A0, {"G": A0 > 0.1})
    assert tr.records[0]["n_bodies"] == 1
    for k in range(1, 8):  # bridge gone, halves drift apart
        A = np.roll(a, (0, -k), (0, 1)) + np.roll(b, (0, k), (0, 1))
        rec = tr.update(A, k)
    assert rec["labels"]["G"]["status"] == "fragmented"
    assert rec["labels"]["G"]["n_carriers"] == 2
    assert "centroid" not in rec["labels"]["G"]
    assert rec["topology"] == "G|G"
    assert tr.events[0]["kind"] == "split"


def test_merge_then_split_reacquires_labels_by_cell_overlap():
    G0 = disc(N, 32, 14, 4)
    S0 = disc(N, 32, 40, 4)
    tr = Tracker(G0 + S0, {"G": G0 > 0.1, "S": S0 > 0.1})
    for k in range(1, 21):  # approach and fuse
        tr.update(np.roll(G0, (0, k), (0, 1)) + S0, k)
    assert tr.records[-1]["topology"] == "GS"
    for j in range(1, 16):  # G leaves again
        rec = tr.update(np.roll(G0, (0, 20 - j), (0, 1)) + S0, 20 + j)
    assert rec["topology"] == "G|S"
    assert rec["labels"]["G"]["status"] == rec["labels"]["S"]["status"] == "single"
    assert all(b["contact_lineage"] == "GS" for b in rec["bodies"])
    assert [e["kind"] for e in tr.events] == ["merge", "split"]
    # the reacquired glider's track is continuous: it ends where the roll put it
    uw = np.subtract(rec["labels"]["G"]["unwrapped"], tr.records[0]["labels"]["G"]["unwrapped"])
    assert np.allclose(uw, (0, 5), atol=0.05)
    assert abs(rec["labels"]["S"]["unwrapped"][1] - 40) < 0.05


def test_debris_and_orphans_are_bookkept():
    G0 = disc(N, 20, 20, 4)
    tr = Tracker(G0, {"G": G0 > 0.1}, TrackerConfig(theta=0.1, debris_mass=0.5, R=1))
    # a far new blob with no parent (orphan) and a tiny shed fragment next to G (debris, child of G)
    orphan = disc(N, 50, 50, 3)
    A = G0 + orphan
    A[20, 27] = 0.4  # touches G's support -> part of G, not debris
    rec = tr.update(A, 1)
    assert rec["orphan_mass"] > 0 and rec["labels"]["G"]["status"] == "single"
    assert rec["topology"] == "-|G"
    assert abs(rec["unassigned_mass"] - rec["halo_mass"] - rec["orphan_mass"] - rec["debris_mass"]) < 1e-12


def test_support_gap_minimum_image():
    a = np.array([[0, 0]])
    b = np.array([[0, N - 1]])
    assert support_gap(a, b, (N, N)) == 1.0


def test_image_guard_ignores_edge_crossing_but_flags_other_image():
    g = ImageGuard((100, 100), target=(50.0, 50.0), guard=20.0)
    primary = g.primary((50.0, 20.0))
    assert primary == (0, 0)
    assert g.check((50.0, 110.0), primary)[0] is False  # crossed the edge, still nearest primary
    censor, d = g.check((50.0, 135.0), primary)  # approaching the (0, +1) image at x = 150
    assert censor and abs(d - 15.0) < 1e-9


def test_superposition_defect_zero_when_far_apart_real_dynamics():
    """S001 cells and S103 under the coexistence rule, far apart: encounter == sum of controls."""
    pytest.importorskip("alm")
    from alm.lenia import Lenia, Rule
    from alm.specimens import load

    rule = Rule(R=13, T=10, mu=0.155, sigma=0.020, beta=(1.0,), kernel="poly", growth="poly")
    n = 128
    g = np.roll(load("S001").place(n), (-32, -32), (0, 1))
    s = np.roll(load("S103").place(n), (32, 32), (0, 1))
    E, G, S = Lenia(rule, g + s), Lenia(rule, g), Lenia(rule, s)
    worst = 0.0
    for _ in range(50):
        for sim in (E, G, S):
            sim.step()
        worst = max(worst, superposition_defect(E.A, G.A, S.A)["defect_max"])
    assert worst < 1e-12
    assert np.array_equal(S.A, s)  # S103 is an exact fixed point


def test_real_glider_translation_matches_reference_centroid():
    """S001 under its native rule: tracker unwrapped centroid == alm.morphometrics centroid path."""
    pytest.importorskip("alm")
    from alm.lenia import Lenia
    from alm.morphometrics import centroid, min_image
    from alm.specimens import load

    sp = load("S001")
    n = 64  # small world so the glider crosses an edge within the test
    sim = Lenia(sp.rule, np.roll(sp.place(n), (0, 24), (0, 1)))
    tr = Tracker(sim.A, {"G": sim.A > 0.01}, TrackerConfig(theta=0.01))  # satellites (< 0.01 R^2) are debris
    ref = np.array(centroid(sim.A))
    ref_uw = ref.copy()
    for k in range(1, 401):
        sim.step()
        rec = tr.update(sim.A, k)
        c = np.array(centroid(sim.A))
        ref_uw = ref_uw + min_image(c - ref, n)
        ref = c
        assert rec["labels"]["G"]["status"] == "single"
    uw = np.array(tr.records[-1]["labels"]["G"]["unwrapped"])
    # theta-support centroid differs from the all-mass centroid only by halo weighting
    assert np.hypot(*(uw - ref_uw)) < 0.5
    disp = uw - np.array(tr.records[0]["labels"]["G"]["unwrapped"])
    assert np.hypot(*disp) > n / 2  # it really travelled a long way (wrapping)
