"""Gallery specimen shim: vendored PR #11 seeds load, match their pins, and run."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "gallery"))

import galspec  # noqa: E402
from alm import provenance, specimens  # noqa: E402
from alm.lenia import Lenia  # noqa: E402


def test_vendored_specimens_register_and_match_pins():
    galspec.ensure_registered()
    galspec.ensure_registered()  # idempotent: second call checks instead of re-registering
    for sid in galspec.PR11:
        spec = specimens.load(sid)
        assert spec.cells.dtype.kind == "i" and spec.cells.max() <= 255


def test_s103_is_a_fixed_point_for_a_few_steps():
    galspec.ensure_registered()
    spec = specimens.load("S103")
    A0 = spec.place(128)
    sim = Lenia(spec.rule, A0)
    for _ in range(20):
        sim.step()
    assert provenance.state_sha256(sim.A) == provenance.state_sha256(A0)
    assert np.isclose(A0.sum() / spec.rule.R**2, 0.3787, atol=1e-4)
