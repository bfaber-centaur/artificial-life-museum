"""Run upstream LeniaND.py's own ``Automaton`` headless (third execution path).

The class source is lifted from the pinned checkout with ``ast`` and executed
with the module globals it needs for a 2-D world. Reikna/GPU is stubbed out, so
upstream takes its numpy float64 CPU path. Nothing in .refs/ is modified.
"""

from __future__ import annotations

import ast
import types

import numpy as np

from .lenia import REPO, Rule

SRC = REPO / ".refs" / "Lenia" / "Python" / "LeniaND.py"


def _automaton_class(n: int):
    tree = ast.parse(SRC.read_text())
    node = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "Automaton")
    mod = ast.Module(body=[node], type_ignores=[])
    size = [n, n]
    mid = [n // 2, n // 2]
    g = dict(
        np=np, DIM=2, SIZE=size, MID=mid, MIDX=mid[0], MIDY=mid[1],
        SIZER=min(mid), SIZETH=size[0], ROUND=10,
        reikna=types.SimpleNamespace(cluda=types.SimpleNamespace(any_api=_no_gpu)),
    )
    exec(compile(mod, str(SRC), "exec"), g)
    return g["Automaton"]


def _no_gpu():
    raise RuntimeError("no GPU in headless check")


class _Board:
    def __init__(self, A, rule: Rule):
        self.cells = A
        self.params = {"R": rule.R, "T": rule.T, "m": rule.mu, "s": rule.sigma,
                       "b": list(rule.b), "kn": {"poly": 1, "exp": 2}[rule.core],
                       "gn": {"poly": 1, "exp": 2}[rule.growth]}
        self.param_P = 0


def upstream_automaton(A: np.ndarray, rule: Rule):
    """Return an upstream Automaton wrapping a copy of ``A``; call ``.calc_once()`` to step."""
    import contextlib
    import io

    cls = _automaton_class(A.shape[0])
    with contextlib.redirect_stdout(io.StringIO()):  # upstream prints the GPU error
        return cls(_Board(A.copy(), rule))
