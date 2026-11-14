"""WINGS: N-dimensional, multi-channel, multi-kernel Lenia (Chan 2020 "expanded universe").

Independent numpy re-implementation of what upstream ``LeniaNDKC.py`` (pinned adfc542) executes
on its CPU path, read from ``Automaton.calc_kernel`` / ``Automaton.calc_once``:

  for each kernel k with source channel c0 and target channel c1:
      U_k = K_k * A[c0]              K_k = shell(|x|/R / r_k, b_k) normalised to sum 1
      D[c1] += h_k * G(U_k; m_k, s_k)
  A[c] <- clip(A[c] + dt * D[c] / sum_k(h_k for kernels into c), 0, 1),   dt = 1 / params[0].T

Only params[0] sets R, T and the kernel / growth families for every kernel (upstream reads
``R`` and ``gn`` from params[0]; ``kn`` is read per kernel). With one channel, one kernel and
D = 2 this is classic Lenia and equals ``alm.lenia.Lenia`` (tests/test_wings.py).

Catalog loaders: ``animals3D.json`` / ``animals4D.json`` (one channel, one kernel, D = 3 / 4) and
``found/<D><C><K>.json`` (multi-channel / multi-kernel creatures Chan found; C channels, K kernels
per channel pair as in the file name).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
UPSTREAM = REPO / ".refs" / "Lenia" / "Python"

DIM_DELIM = {0: "", 1: "$", 2: "%", 3: "#", 4: "@A", 5: "@B"}


def kernel_core(kn: int, r):
    r = np.asarray(r, dtype=np.float64)
    if kn == 1:
        return (4 * r * (1 - r)) ** 4
    if kn == 2:
        with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
            out = np.exp(4 - 1 / (r * (1 - r)))
        return np.where((r > 0) & (r < 1), out, 0.0)
    if kn == 3:
        return ((r >= 0.25) & (r <= 0.75)).astype(np.float64)
    raise ValueError(kn)


def growth(gn: int, u, m, s):
    if gn == 1:
        return np.maximum(0, 1 - (u - m) ** 2 / (9 * s ** 2)) ** 4 * 2 - 1
    if gn == 2:
        return np.exp(-((u - m) ** 2) / (2 * s ** 2)) * 2 - 1
    if gn == 3:
        return (np.abs(u - m) <= s) * 2.0 - 1
    raise ValueError(gn)


def shell(D: np.ndarray, p: dict) -> np.ndarray:
    """Upstream ``kernel_shell``: D is distance / R."""
    r = p.get("r", 1)
    bs = np.asarray([float(Fraction(x)) for x in str(p["b"]).split(",")])
    B = len(bs)
    Br = B * D / r
    b = bs[np.minimum(np.floor(Br).astype(int), B - 1)]
    return (D < r) * kernel_core(p.get("kn", 1), np.minimum(Br % 1, 1)) * b


def signed_grid(shape):
    return np.meshgrid(*[np.fft.fftfreq(n, 1.0 / n) for n in shape], indexing="ij")


@dataclass
class NDLenia:
    """State A has shape (C, *world). ``params`` is upstream's list of kernel dicts."""

    params: list
    A: np.ndarray
    R: float | None = None  # overrides params[0]["R"] (upstream: world R, used when rescaling)
    _khat: list = field(default_factory=list, repr=False)

    def __post_init__(self):
        self.A = np.asarray(self.A, dtype=np.float64).copy()
        self.C = self.A.shape[0]
        shape = self.A.shape[1:]
        R = self.R if self.R is not None else self.params[0]["R"]
        D = np.sqrt(sum(x ** 2 for x in signed_grid(shape))) / R
        self.dt = 1.0 / self.params[0]["T"]
        self.gn = self.params[0].get("gn", 1)
        self.src, self.dst, self.h, self.m, self.s = [], [], [], [], []
        for p in self.params:
            K = shell(D, p)
            self._khat.append(np.fft.rfftn(K / K.sum()))
            c0, c1 = p.get("c", [0, 0])
            self.src.append(c0)
            self.dst.append(c1)
            self.h.append(p.get("h", 1))
            self.m.append(p["m"])
            self.s.append(p["s"])
        self.hsum = np.zeros(self.C)
        for c1, h in zip(self.dst, self.h):
            self.hsum[c1] += h

    def growth_fields(self, A=None):
        A = self.A if A is None else A
        shape = A.shape[1:]
        F = [np.fft.rfftn(A[c]) for c in range(self.C)]
        D = np.zeros_like(A)
        for k, kh in enumerate(self._khat):
            U = np.fft.irfftn(F[self.src[k]] * kh, s=shape, axes=tuple(range(len(shape))))
            D[self.dst[k]] += self.h[k] * growth(self.gn, U, self.m[k], self.s[k])
        for c in range(self.C):
            D[c] = D[c] / self.hsum[c] if self.hsum[c] > 0 else 0.0
        return D

    def step(self):
        self.A = np.clip(self.A + self.dt * self.growth_fields(), 0.0, 1.0)
        return self.A


# --- upstream RLE (N-D) -------------------------------------------------------------------------

def _ch2val(c: str) -> int:
    if c in ".b":
        return 0
    if c == "o":
        return 255
    if len(c) == 1:
        return ord(c) - ord("A") + 1
    return (ord(c[0]) - ord("p")) * 24 + (ord(c[1]) - ord("A") + 25)


def rle_decode(st: str, dim: int) -> np.ndarray:
    """N-D port of upstream ``Board.rle2cells`` (values / 255); ragged axes zero-padded."""
    stacks = [[] for _ in range(dim)]
    last, count = "", ""
    delims = [DIM_DELIM[d] for d in range(dim)]
    st = st.rstrip("!") + DIM_DELIM[dim - 1]

    def append(stack, item, cnt, repeat):
        n = int(cnt) if cnt else 1
        if repeat:
            stack.extend([item] * n)
        else:
            stack.append(item)
            for _ in range(n - 1):
                stack.append([])

    for ch in st:
        if ch.isdigit():
            count += ch
        elif ch in "pqrstuvwxy@":
            last = ch
        else:
            tok = last + ch
            if tok not in delims:
                append(stacks[0], _ch2val(tok) / 255, count, True)
            else:
                d = delims.index(tok)
                for e in range(d):
                    append(stacks[e + 1], stacks[e], count, False)
                    stacks[e] = []
            last, count = "", ""
    nested = stacks[dim - 1]

    def depth_lens(a, lvl, lens):
        if lvl < dim - 1 or isinstance(a, list):
            lens[lvl] = max(lens[lvl], len(a))
            if lvl < dim - 1:
                for x in a:
                    depth_lens(x, lvl + 1, lens)

    lens = [0] * dim
    depth_lens(nested, 0, lens)
    out = np.zeros(lens)

    def fill(a, idx):
        if len(idx) == dim - 1:
            out[tuple(idx)][: len(a)] = a
        else:
            for i, x in enumerate(a):
                fill(x, idx + [i])

    fill(nested, [])
    return out


def load_catalog(name: str):
    """animals3D.json / animals4D.json: entries with params."""
    data = json.loads((UPSTREAM / name).read_text(encoding="utf-8"))
    return [e for e in data if isinstance(e, dict) and "params" in e]


def load_found(stem: str):
    """found/<stem>.json (upstream reads it as '[' + text + ']')."""
    st = (UPSTREAM / "found" / f"{stem}.json").read_text(encoding="utf-8")
    data = json.loads("[" + st.rstrip(", \n\r\t") + "]")
    return [e for e in data if isinstance(e, dict) and "params" in e]


def entry_state(e: dict, dim: int, size: int, C: int | None = None) -> tuple[list, np.ndarray]:
    """(params list, A of shape (C, size^dim)) with the creature's cells centred."""
    params = e["params"] if isinstance(e["params"], list) else [e["params"]]
    params = [dict(p) for p in params]
    cells = e["cells"] if isinstance(e["cells"], list) else [e["cells"]]
    if C is None:
        C = len(cells)
    parts = [rle_decode(c, dim) for c in cells]
    A = np.zeros((C,) + (size,) * dim)
    for c, part in enumerate(parts):
        # upstream rle axis order is (.., z, y, x) reversed relative to string nesting; we keep
        # the nesting order (outermost delimiter = axis 0), which is a fixed relabelling of axes
        sl = tuple(slice((size - n) // 2, (size - n) // 2 + n) for n in part.shape)
        A[(c,) + sl] = part
    return params, A
