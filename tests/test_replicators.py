"""Fast checks for the REPLICATORS helpers (research/experiments/REPLICATORS)."""
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1] / "research" / "experiments" / "REPLICATORS"
sys.path.insert(0, str(HERE))

from alm import specimens  # noqa: E402

import common  # noqa: E402
import tree  # noqa: E402

needs_refs = pytest.mark.skipif(not specimens.ANIMALS_JSON.exists(), reason="upstream Lenia reference not checked out")


def blob(N, y, x, r=6.0):
    yy, xx = np.mgrid[:N, :N]
    dy = np.minimum(np.abs(yy - y), N - np.abs(yy - y))
    dx = np.minimum(np.abs(xx - x), N - np.abs(xx - x))
    return np.exp(-(dy ** 2 + dx ** 2) / (2 * r ** 2))


def test_torus_label_joins_across_the_seam():
    m = np.zeros((32, 32), bool)
    m[10:14, 0:3] = True
    m[10:14, 29:32] = True
    _, n = common.torus_label(m)
    assert n == 1
    m3 = np.zeros((16, 16, 16), bool)
    m3[0, 5, 5] = m3[15, 5, 5] = True
    assert common.torus_label(m3)[1] == 1


def test_tracker_sees_one_division_and_ignores_a_flicker():
    N = 96
    frames = []
    for f in range(60):
        S = blob(N, 48, 48) if f < 20 else blob(N, 48, 48 - (f - 19)) + blob(N, 48, 48 + (f - 19))
        if f == 40:  # one-frame flicker: a faint extra peak near the daughters
            S = S + 0.3 * blob(N, 28, 48, 3)
        frames.append(tree.peaks(S))
    tracks = tree.link(frames, N)
    segs, keep = tree.build_tree(tracks, len(frames))
    assert sum(s["end_kind"] == "division" for s in segs) == 1
    assert len(tree.segments_at(segs, tracks, 59)) == 2
    assert not all(keep)  # the flicker was dropped


def test_tracker_splices_a_jumping_peak():
    N = 96
    frames = []
    for f in range(40):
        x = 30 if f < 20 else 52  # same single body, its peak jumps 22 px (within BIRTH, beyond LINK)
        frames.append(tree.peaks(blob(N, 48, x)))
    tracks = tree.link(frames, N)
    segs, _ = tree.build_tree(tracks, len(frames))
    assert not any(s["end_kind"] == "division" for s in segs)
    assert len(tree.segments_at(segs, tracks, 39)) == 1


@needs_refs
def test_interp_endpoints_are_the_catalogue_rules():
    from interp import mix, well, wild
    for lam, ref in ((0.0, well), (1.0, wild)):
        for p, q in zip(mix(lam), ref["params"]):
            assert p["m"] == pytest.approx(q["m"]) and p["s"] == pytest.approx(q["s"])
            assert [float(x) for x in p["b"].split(",")] == pytest.approx([float(Fraction(x)) for x in q["b"].split(",")])


@needs_refs
def test_genome_lenia_reduces_to_the_catalogue_rules():
    from common import found_entry, nd
    from genome import GenomeLenia
    _, A = nd.entry_state(found_entry("213", 84), 2, 96)
    for g, idx in ((0.0, 84), (1.0, 83)):
        a = GenomeLenia(A[0], np.full((96, 96), g))
        b = nd.NDLenia(found_entry("213", idx)["params"], A)
        for _ in range(20):
            a.step()
            b.step()
        assert np.abs(a.A - b.A[0]).max() < 1e-12
        assert np.abs(a.g - g).max() < 1e-12  # a uniform genome stays uniform
    # neutral mode: the rule ignores a non-uniform genome
    gmix = np.random.default_rng(0).uniform(0, 1, (96, 96))
    a = GenomeLenia(A[0], gmix, rule_g=0.0)
    b = nd.NDLenia(found_entry("213", 84)["params"], A)
    for _ in range(20):
        a.step()
        b.step()
    assert np.abs(a.A - b.A[0]).max() < 1e-12
    assert a.g.min() >= 0 and a.g.max() <= 1
