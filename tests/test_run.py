"""Runner, provenance and hook checks, plus S001 agreement with Lane 1's reference trace."""

import csv
import json
from dataclasses import dataclass
from typing import ClassVar

import numpy as np
import pytest

from alm import interventions, measure, run, specimens

REF_TRACE = specimens.SPECIMEN_DIR / "S001-orbium" / "reference-trace.csv"


def test_s001_matches_lane1_reference_trace():
    """Lane 1's numpy transcription (a different code path) printed a 4000-step trace."""
    res = run.run(run.RunConfig(steps=4000, every=10), out_root=None)
    ref = list(csv.DictReader(open(REF_TRACE)))
    assert [int(r["step"]) for r in ref] == [r["step"] for r in res.rows]
    for r, o in zip(ref, res.rows):
        assert o["mass"] == pytest.approx(float(r["mass"]), abs=1e-6)
        assert o["gyradius"] == pytest.approx(float(r["gyradius"]), abs=1e-6)
        if r["growth"] != "nan":
            assert o["growth"] == pytest.approx(float(r["growth"]), abs=1e-6)
        assert measure.wrap(o["cx_cells"] - float(r["cx"]), 128) == pytest.approx(0, abs=1e-3)
        assert measure.wrap(o["cy_cells"] - float(r["cy"]), 128) == pytest.approx(0, abs=1e-3)
    s = res.summary
    assert s["alive_final"]
    assert s["mass_mean"] == pytest.approx(0.4358, abs=2e-4)
    assert s["speed_R_per_time"] == pytest.approx(0.4796, abs=2e-3)
    assert s["heading_deg_image"] == pytest.approx(68.2, abs=0.5)


def test_run_writes_provenance(tmp_path):
    cfg = run.RunConfig(steps=60, every=20, size=64, interventions=[interventions.parse("30:mass_scale:factor=0.5")])
    res = run.run(cfg, out_root=tmp_path)
    d = res.run_dir
    for f in ("manifest.json", "trace.csv", "summary.json", "series.npz", "states.npz", "final.png"):
        assert (d / f).exists(), f
    man = json.loads((d / "manifest.json").read_text())
    for key in ("simulator", "specimen", "rule", "seed", "grid", "timestep", "interventions_applied",
                "measurements", "final_state_sha256", "reproduction"):
        assert key in man, key
    assert man["simulator"]["git_commit"] is None or len(man["simulator"]["git_commit"]) == 40
    assert man["specimen"]["id"] == "S001"
    assert "--intervene 30:mass_scale:factor=0.5" in man["reproduction"]["command"]
    states = np.load(d / "states.npz")
    assert {"initial", "final", "iv0_pre", "iv0_post"} <= set(states.files)
    from alm.provenance import state_sha256

    assert state_sha256(states["final"]) == man["final_state_sha256"]
    rows = list(csv.DictReader(open(d / "trace.csv")))
    assert [int(r["step"]) for r in rows] == [0, 20, 40, 60]


def test_reproduction_command_roundtrips(tmp_path):
    cfg = run.RunConfig(steps=40, every=10, size=64, T=20, sigma=0.016, kernel="exp",
                        interventions=[interventions.parse("10:mass_scale:factor=0.9")])
    a = run.run(cfg, out_root=None)
    import shlex

    argv = shlex.split(a.manifest["reproduction"]["command"])[3:]
    cfg2, _ = run.parse_args(argv)
    b = run.run(cfg2, out_root=None)
    assert a.run_id == b.run_id
    assert a.manifest["final_state_sha256"] == b.manifest["final_state_sha256"]
    assert a.manifest["rule"]["T"] == 20 and a.manifest["rule"]["kernel"] == "exp"


def test_deterministic_and_config_sensitive_ids():
    a = run.run(run.RunConfig(steps=30, size=64), out_root=None)
    b = run.run(run.RunConfig(steps=30, size=64), out_root=None)
    c = run.run(run.RunConfig(steps=30, size=64, sigma=0.016), out_root=None)
    assert a.run_id == b.run_id != c.run_id
    assert np.array_equal(a.final, b.final)


def test_intervention_hook_logs_mass_change():
    res = run.run(run.RunConfig(steps=20, every=10, size=64,
                                interventions=[interventions.parse("10:mass_scale:factor=0.5")]), out_root=None)
    (ev,) = res.manifest["interventions_applied"]
    assert ev["step"] == 10 and ev["params"] == {"factor": 0.5}
    assert ev["mass_after"] == pytest.approx(ev["mass_before"] / 2)
    assert res.rows[1]["mass"] == pytest.approx(ev["mass_after"])


def test_custom_intervention_and_feature_registration():
    @interventions.register
    @dataclass(frozen=True)
    class _Saturate(interventions.Intervention):
        name: ClassVar[str] = "_test_saturate"
        amount: float = 2.0

        def apply(self, A, sim, rng):
            return A + self.amount + rng.random(A.shape)  # runner must re-clip

    @measure.register("_test_max")
    def _mx(A, sim):
        return {"maxval": float(A.max())}

    try:
        cfg = run.RunConfig(steps=10, every=5, size=64, features=("basic", "_test_max"),
                            interventions=[(5, interventions.make("_test_saturate", amount="0.5"))])
        res = run.run(cfg, out_root=None)
        assert res.rows[1]["maxval"] == 1.0  # clipped
        assert "maxval" in res.manifest["measurements"]["columns"]
    finally:
        interventions.REGISTRY.pop("_test_saturate")
        measure.REGISTRY.pop("_test_max")


def test_bad_intervention_step_rejected():
    with pytest.raises(ValueError):
        run.run(run.RunConfig(steps=10, interventions=[interventions.parse("11:mass_scale:factor=1")]), out_root=None)


def test_dominant_period():
    t = np.arange(2000)
    assert run.dominant_period(np.sin(2 * np.pi * t / 4.32)) == pytest.approx(4.32, rel=1e-3)
