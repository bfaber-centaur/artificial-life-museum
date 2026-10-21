"""Scorer tests on synthetic encounters (kinematic discs, no Lenia), plus a real far-apart sham.

    PYTHONPATH=src python -m pytest -q research/experiments/REEF-behavior/test_score.py
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import EncounterRecorder, ScoreParams, score_trace  # noqa: E402
from test_track import disc  # noqa: E402

N = 64
P = ScoreParams(R=4, T=10, N=N, theta_int=1e-9, approach_timeout=3, post_contact=2, horizon=5,
                fit_window=0.5, bind_min=1.0, capture_last=1.0, censor_margin=0.5)
RING = (39, 30)


def run(path_E, path_G=None, ring_E=lambda t: disc(N, *RING, 3), steps=50):
    """path_*(t) -> glider centre (y, x) or None (gone). Controls: straight glider, fixed ring."""
    path_G = path_G or (lambda t: (32, 5 + 10 * t))
    S = disc(N, *RING, 3)

    def g(pos):
        return np.zeros((N, N)) if pos is None else disc(N, pos[0], pos[1], 3)

    rec = EncounterRecorder(g(path_E(0)) + ring_E(0), g(path_G(0)), S, P)
    for k in range(1, steps + 1):
        t = k / P.T
        rec.update(np.minimum(g(path_E(t)) + ring_E(t), 1), g(path_G(t)), S, t)
    return rec


def test_pass_with_brief_contact():
    rec = run(lambda t: (32, 5 + 10 * t))
    res = score_trace(rec.rows, P)
    assert res["class"] == "PASS"
    assert "BRIEF_CONTACT" in res["flags"] and "RING_EXACT" in res["flags"]
    assert res["t_c"] is not None and res["t_int"] is None  # superposition is exact here
    assert abs(res["observables"]["heading_change_deg"]) < 1e-6


def test_deflect_signed():
    def path(t):  # after passing the ring the glider turns toward -y (negative heading change)
        return (32, 5 + 10 * t) if t <= 3.2 else (32 - 4 * (t - 3.2), 37 + 10 * (t - 3.2))

    res = score_trace(run(path).rows, P)
    assert res["class"] == "DEFLECT"
    assert res["observables"]["heading_change_deg"] < -5 and res["observables"]["lateral_R"] < 0


def test_capture_static_merged_body():
    res = score_trace(run(lambda t: (32, 5 + 10 * min(t, 2.6))).rows, P)
    assert res["class"] == "CAPTURE"


def test_glider_death_after_contact():
    res = score_trace(run(lambda t: (32, 5 + 10 * t) if t < 2.8 else None).rows, P)
    assert res["class"] == "G_DEATH"


def test_no_contact_far_flank():
    res = score_trace(run(lambda t: (20, 5 + 10 * t), path_G=lambda t: (20, 5 + 10 * t)).rows, P)
    assert res["class"] == "NO_CONTACT" and res["t_c"] is None


def test_censor_on_other_ring_image():
    p = ScoreParams(**{**P.__dict__, "horizon": 9, "post_contact": 7})
    rec = run(lambda t: (32, 5 + 10 * t), steps=90)
    res = score_trace(rec.rows, p)
    assert res["class"] == "CENSORED" and res["partial_class"] == "PASS"
    assert "ring image (0, 1)" in res["censor_reason"]
    assert res["t_cen"] < res["t_c"] + 7


def test_control_failure_when_ring_control_changes():
    rec = run(lambda t: (32, 5 + 10 * t))
    rec.rows[20]["Sc"]["mass"] += 1e-6
    assert score_trace(rec.rows, P)["class"] == "CONTROL_FAILURE"


def test_real_sham_far_apart_is_no_contact():
    """Real S001 cells + S103 under the coexistence rule, ring far off the glider's path."""
    pytest.importorskip("alm")
    from alm.lenia import Lenia, Rule
    from alm.specimens import load

    rule = Rule(R=13, T=10, mu=0.155, sigma=0.020, beta=(1.0,), kernel="poly", growth="poly")
    n = 128
    g = load("S001").place(n)
    s = np.roll(load("S103").place(n), (0, 64), (0, 1))
    E, G, S = Lenia(rule, g + s), Lenia(rule, g), Lenia(rule, s)
    p = ScoreParams(N=n, horizon=3, approach_timeout=3, fit_window=1.0, censor_margin=0.0)
    rec = EncounterRecorder(E.A, G.A, S.A, p)
    for k in range(1, 31):
        for sim in (E, G, S):
            sim.step()
        rec.update(E.A, G.A, S.A, k / 10)
    res = score_trace(rec.rows, p)
    assert res["t_int"] is None and res["t_c"] is None
    assert max(r["defect_max"] for r in rec.rows) < 1e-12
    assert all(r["ring_box_equal"] for r in rec.rows)
