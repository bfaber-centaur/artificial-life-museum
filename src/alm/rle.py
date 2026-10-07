"""Decoder for upstream Lenia 2-D RLE cell strings (catalog ``cells`` field).

Levels: ``.``/``b`` = 0, ``A``..``X`` = 1..24, ``pA``..``yO`` = 25..255, ``o`` = 255.
Rows end with ``$`` (a count before ``$`` adds blank rows); short rows are
right-padded with zeros, and trailing blank rows are kept (as upstream). Returns integer levels; divide by 255 for cell values.
"""

from __future__ import annotations

import re

import numpy as np

_TOKEN = re.compile(r"(\d*)([p-y@]?[^\dp-y@])")


def _level(tok: str) -> int:
    if tok in (".", "b"):
        return 0
    if tok == "o":
        return 255
    if len(tok) == 1:
        return ord(tok) - ord("A") + 1
    return (ord(tok[0]) - ord("p")) * 24 + ord(tok[1]) - ord("A") + 25


def decode(rle: str) -> np.ndarray:
    body = rle.strip().rstrip("!")
    rows: list[list[int]] = [[]]
    pos = 0
    while pos < len(body):
        m = _TOKEN.match(body, pos)
        if not m:
            raise ValueError(f"bad RLE at offset {pos}: {body[pos:pos + 8]!r}")
        n = int(m.group(1)) if m.group(1) else 1
        tok = m.group(2)
        if tok == "$":
            rows.extend([] for _ in range(n))
        else:
            rows[-1].extend([_level(tok)] * n)
        pos = m.end()
    width = max(len(r) for r in rows)
    return np.array([r + [0] * (width - len(r)) for r in rows], dtype=np.int64)
