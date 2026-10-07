"""Tests for research/figures/figlib (Lane 9 plotting helpers)."""
import json
import math
import pathlib
import sys

FIGS = pathlib.Path(__file__).resolve().parents[1] / "research" / "figures"
sys.path.insert(0, str(FIGS))

from figlib import edges as E  # noqa: E402
from figlib import style  # noqa: E402


def run(phase, dm, outcome, rid=""):
    return E.Run("L", "c", "I001", phase, abs(dm), dm, outcome, "f", rid)


def test_edge_brackets_closest_runs():
    rs = [run(0, -0.05, "RECOVERED"), run(0, -0.10, "RECOVERED", "s"), run(0, -0.103, "DIED", "d"),
          run(0, -0.15, "DIED")]
    (e,) = E.edges(rs)
    assert (e.survive_abs, e.die_abs, e.survive_run, e.die_run) == (0.10, 0.103, "s", "d")
    assert e.monotone and e.n_runs == 4


def test_non_monotone_is_flagged_not_hidden():
    rs = [run(0, -0.10, "RECOVERED", "a"), run(0, -0.09, "DIED", "island"), run(0, -0.12, "RECOVERED", "late")]
    (e,) = E.edges(rs)
    assert not e.monotone
    assert set(e.violations) == {"a", "island", "late"}


def test_one_sided_group_gives_nan():
    (e,) = E.edges([run(0, -0.2, "DIED")])
    assert math.isnan(e.survive_abs) and e.die_abs == 0.2


def test_conventions_json_matches_style():
    assert json.loads((FIGS / "conventions.json").read_text()) == json.loads(json.dumps(style.as_json()))
