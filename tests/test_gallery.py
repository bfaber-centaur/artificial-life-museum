"""Gallery: committed runs match the registry, S103 is a fixed point, the render pipeline works."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "gallery"))

from alm import provenance, specimens  # noqa: E402
from alm.lenia import Lenia  # noqa: E402


def test_committed_gallery_runs_match_the_specimen_registry():
    """Every run the gallery shows was made from the cells now registered under its specimen ID."""
    import json

    root = Path(__file__).resolve().parents[1]
    runs = json.loads((root / "research" / "gallery" / "runs.json").read_text())
    for run_id in runs.values():
        man = json.loads((root / "research" / "traces" / run_id / "manifest.json").read_text())
        spec = specimens.load(man["specimen"]["id"])
        assert spec.cells_sha256 == man["specimen"]["cells_sha256_int16le"], run_id


def test_s103_is_a_fixed_point_for_a_few_steps():
    spec = specimens.load("S103")
    A0 = spec.place(128)
    sim = Lenia(spec.rule, A0)
    for _ in range(20):
        sim.step()
    assert provenance.state_sha256(sim.A) == provenance.state_sha256(A0)
    assert np.isclose(A0.sum() / spec.rule.R**2, 0.3787, atol=1e-4)


def _short_pipeline(tmp_path, monkeypatch):
    """Point render.py at a scratch tree and shrink the runs to 60 steps."""
    import render

    monkeypatch.setattr(render, "TRACES", tmp_path / "traces")
    monkeypatch.setattr(render, "EXHIBITS", tmp_path / "exhibits")
    monkeypatch.setattr(render, "RUNS_JSON", tmp_path / "runs.json")
    monkeypatch.setattr(render, "STEPS", 60)
    monkeypatch.setattr(render, "WINDOW", (20, 60))
    monkeypatch.setattr(render, "G4_STEPS", 60)
    monkeypatch.setattr(render, "G4_T0", 30)
    render.collect()
    return render


def test_render_pipeline_end_to_end(tmp_path, monkeypatch):
    """Real short runs -> verified replay -> every exhibit's media and provenance."""
    import json

    render = _short_pipeline(tmp_path, monkeypatch)
    runs = json.loads((tmp_path / "runs.json").read_text())
    assert sorted(runs) == sorted(render.run_configs())
    render.render()

    folders = sorted((tmp_path / "exhibits").iterdir())
    assert [f.name[:4] for f in folders] == ["G001", "G002", "G003", "G004"]
    for folder in folders:
        prov = json.loads((folder / "provenance.json").read_text())
        assert prov["media"]
        for name in prov["media"]:
            assert (folder / name).stat().st_size > 0, f"{folder.name}/{name} missing"
        assert {src["run_id"] for src in prov["sources"]} <= set(runs.values())
        for src in prov["sources"]:
            man = json.loads((tmp_path / "traces" / src["run_id"] / "manifest.json").read_text())
            assert src["final_state_sha256"] == man["final_state_sha256"]
            assert src["replay_verified"] is True


def test_render_refuses_a_run_whose_hash_does_not_match(tmp_path, monkeypatch):
    import json

    import pytest

    render = _short_pipeline(tmp_path, monkeypatch)
    run_id = json.loads((tmp_path / "runs.json").read_text())["S001"]
    path = tmp_path / "traces" / run_id / "manifest.json"
    man = json.loads(path.read_text())
    man["final_state_sha256"] = "0" * 64
    path.write_text(json.dumps(man))
    with pytest.raises(ValueError, match="replay final sha256"):
        render.render()
    assert not (tmp_path / "exhibits").exists()
