"""Tests for the Lane 10 museum build (museum/build.py)."""
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "museum"))

import build as M  # noqa: E402

SITE = REPO / "museum" / "site"


def test_build_succeeds_and_cites_only_existing_sources(tmp_path):
    snap = M.build(tmp_path)
    assert {"index.html", "claims.html", "museum.css"} <= {p.name for p in tmp_path.iterdir()}
    assert snap["claims"], "the museum should cite at least one claim"
    for room, sources in snap["sources"].items():
        assert sources, f"{room} cites no sources"
        for s in sources:
            assert (REPO / s).exists(), s


def test_committed_site_matches_current_ledger():
    """Every claim on display must still have the status the committed pages show; else rebuild."""
    current = M.ledger.parse(M.LEDGER)
    snap = json.loads((SITE / "ledger-snapshot.json").read_text())
    for cid, c in snap["claims"].items():
        assert current[cid]["status"] == c["status"], (
            f"{cid} is {current[cid]['status']} in claims.md but the museum shows {c['status']}; "
            f"run .venv/bin/python museum/build.py")


def _room(tmp_path, body, expect):
    rooms = tmp_path / "rooms"
    rooms.mkdir(parents=True)
    head = json.dumps({"slug": "index", "order": 0, "title": "t", "expect": expect})
    (rooms / "00-index.html").write_text(f"<!--meta {head} -->\n{body}")
    return rooms


def test_status_drift_stops_the_build(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOMS", _room(tmp_path, "{{claim:C001}} {{src:research/claims.md}}",
                                          {"C001": "REFUTED"}))
    with pytest.raises(M.MuseumBuildError, match="C001"):
        M.build(tmp_path / "out")


def test_undeclared_claim_and_missing_file_are_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOMS", _room(tmp_path, "{{claim:C001}} {{src:research/claims.md}}", {}))
    with pytest.raises(M.MuseumBuildError, match="without declaring"):
        M.build(tmp_path / "out")
    monkeypatch.setattr(M, "ROOMS", _room(tmp_path / "b", "{{src:research/no-such-file.md}}", {}))
    with pytest.raises(M.MuseumBuildError, match="no such file"):
        M.build(tmp_path / "out")


def test_pr_links_need_a_provisional_room(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOMS", _room(tmp_path, "{{pr:27}} {{src:research/claims.md}}", {}))
    with pytest.raises(M.MuseumBuildError, match="under_review"):
        M.build(tmp_path / "out")
