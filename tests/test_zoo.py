"""Fast checks for the collision zoo (research/experiments/ZOO)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ZOO = Path(__file__).resolve().parents[1] / "research" / "experiments" / "ZOO"
sys.path.insert(0, str(ZOO))

from alm import specimens  # noqa: E402
import zoocore  # noqa: E402

needs_refs = pytest.mark.skipif(not specimens.ANIMALS_JSON.exists(), reason="upstream Lenia reference not checked out")


def test_components_merge_across_the_torus_edge():
    A = np.zeros((32, 32))
    A[10:14, 30:32] = 1.0
    A[10:14, 0:3] = 1.0  # same blob, wrapped
    A[20:23, 15:18] = 0.5
    cs = zoocore.components(A)
    assert len(cs) == 2
    assert cs[0]["mass"] == pytest.approx(20.0)
    assert cs[0]["c"][1] < 1.0 or cs[0]["c"][1] > 31.0  # circular mean sits on the seam


def test_place_pair_contact_geometry():
    class B:  # minimal stand-in for zoocore.Body
        def __init__(self, v):
            self.v = v
            self.patch = np.zeros((9, 9))
            self.patch[2:7, 2:7] = 1.0

    a, b = B((0.0, 5.0)), B((0.0, -5.0))  # head-on along x
    A0, info = zoocore.place_pair(a, b, b_R=1.0, R=13, N=256)
    pa, pb = np.array(info["pA"]), np.array(info["pB"])
    tc = info["tc"]
    # at contact time the two centres are b = 13 cells apart, perpendicular to the motion
    d = (pb + np.array(b.v) * tc) - (pa + np.array(a.v) * tc)
    assert abs(abs(d[0]) - 13.0) < 1e-9 and abs(d[1]) < 1e-9
    assert A0.sum() == pytest.approx(50.0)


# Replays are compared by physics, not by sha256. numpy's FFT picks its kernels by the CPU's SIMD
# level (AVX-512 vs AVX2 round differently), and the committed hashes were made on an AVX-512
# machine, so they only reproduce bit for bit there; CI runners vary. Reproduce the other path
# with NPY_DISABLE_CPU_FEATURES="AVX512_SPR AVX512_ICL X86_V4". The atlas bodies come from a
# rotate-and-resettle transient that amplifies those rounding differences to O(1) (ZOO.md,
# "Floating point"), so the atlas test replays from the committed bodies in tests/fixtures.
FIXTURE_STATES = Path(__file__).resolve().parent / "fixtures" / "zoo-states"


def test_atlas_rows_replay(monkeypatch, tmp_path):
    """Two committed atlas rows (head-on, fusion) replay to the same class and mass series."""
    import shutil

    import atlas

    for f in FIXTURE_STATES.glob("*.npz"):
        shutil.copy(f, tmp_path / f.name)
    monkeypatch.setattr(atlas, "STATES", tmp_path)
    rows = {(r["theta"], r["b_R"]): r for r in map(json.loads, (ZOO / "atlas-O.jsonl").read_text().splitlines())}
    for key in [(180, 0.0), (90, 0.0)]:
        r = atlas.job(("O", "O2u", "O2u", key[0], key[1]))
        assert sorted(p.name for p in tmp_path.iterdir()) == sorted(p.name for p in FIXTURE_STATES.glob("*.npz"))
        assert r["class"] == rows[key]["class"]
        assert r["n"] == rows[key]["n"]
        np.testing.assert_allclose(r["mass_series"], rows[key]["mass_series"], rtol=1e-4)


@needs_refs
def test_forage_row_replays():
    """A short free-foraging run (seed 2, K 8) replays its committed census and ends the same way."""
    import forage
    from alm.lenia import Lenia

    row = next(json.loads(l) for l in (ZOO / "forage-K8.jsonl").read_text().splitlines() if json.loads(l)["seed"] == 2)
    A0, *_ = forage.setup(2, 8, row["N"])
    assert float(A0.sum()) == pytest.approx(row["series"][0][4], rel=0.02)  # before any step vs t 5
    L = Lenia(forage.RULE, A0)
    for t, m_arc, n_rings, n, M in row["series"]:
        for _ in range(5 * forage.RULE.T):
            L.step()
        got = forage.census(L.A)
        assert got[1] == n_rings and got[2] == n, t
        assert got[0] == pytest.approx(m_arc, rel=1e-4, abs=0.2), t
        assert float(L.A.sum()) == pytest.approx(M, rel=1e-4), t


def test_ledger_numbers_match_logs():
    """The C082 masses quoted in the ledger are the feeding log's."""
    log = json.loads((ZOO / "feed-altfilm.json").read_text())["log"]
    meals = [e["mass"] for e in log if "meal" in e and "mass" in e][:4]
    assert [round(m, 1) for m in meals] == [894.1, 1030.5, 1165.5, 1299.1]
    match = json.loads((ZOO / "ladder_match.json").read_text())
    for k, row in enumerate(match, start=1):
        best = max(("P6al", "P7al", "P8al", "P9al", "P10al"), key=lambda c: row[c])
        assert best == f"P{6 + k}al" and row[best] > 0.99
