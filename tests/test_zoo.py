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


@needs_refs
def test_atlas_rows_replay():
    """Two committed atlas rows replay bit for bit (one head-on, one fusion)."""
    from atlas import job

    rows = {(r["theta"], r["b_R"]): r for r in map(json.loads, (ZOO / "atlas-O.jsonl").read_text().splitlines())}
    for key in [(180, 0.0), (90, 0.0)]:
        r = job(("O", "O2u", "O2u", key[0], key[1]))
        assert r["final_sha256"] == rows[key]["final_sha256"]
        assert r["class"] == rows[key]["class"]


def test_ledger_numbers_match_logs():
    """The C082 masses quoted in the ledger are the feeding log's."""
    log = json.loads((ZOO / "feed-altfilm.json").read_text())["log"]
    meals = [e["mass"] for e in log if "meal" in e and "mass" in e][:4]
    assert [round(m, 1) for m in meals] == [894.1, 1030.5, 1165.5, 1299.1]
    match = json.loads((ZOO / "ladder_match.json").read_text())
    for k, row in enumerate(match, start=1):
        best = max(("P6al", "P7al", "P8al", "P9al", "P10al"), key=lambda c: row[c])
        assert best == f"P{6 + k}al" and row[best] > 0.99


@needs_refs
def test_forage_row_replays():
    """A short free-foraging run (seed 2, K 8) replays to its committed final hash."""
    import forage
    from alm.lenia import Lenia

    row = next(json.loads(l) for l in (ZOO / "forage-K8.jsonl").read_text().splitlines() if json.loads(l)["seed"] == 2)
    A0, *_ = forage.setup(2, 8, row["N"])
    assert zoocore.sha(A0) == row["init_sha256"]
    L = Lenia(forage.RULE, A0)
    for _ in range(row["t_end"] * forage.RULE.T):
        L.step()
    assert zoocore.sha(L.A) == row["final_sha256"]
