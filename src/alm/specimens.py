"""Specimen registry: stable IDs mapped to an exact initial state and rule.

A specimen's cells are integer levels 0..255 (cell value = level / 255), so the
initial state is exact and hashable. ``place`` centres the patch on an empty
torus with offset ((N - h) // 2, (N - w) // 2), as upstream ``Board.add`` does
with ``is_centered=True``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

import numpy as np

from . import rle
from .lenia import Rule

REPO_ROOT = Path(__file__).resolve().parents[2]
SPECIMEN_DIR = REPO_ROOT / "research" / "specimens"
ANIMALS_JSON = REPO_ROOT / ".refs" / "Lenia" / "Python" / "animals.json"
ANIMALS_SHA256 = "09cf0a831c1ef8a73ebfaa9126257fbe076108362b706a98d88650ca9848d206"

# Catalog family numbers as upstream LeniaND.py *executes* them (not as its UI labels them).
_CATALOG_KERNEL = {1: "poly", 2: "exp"}
_CATALOG_GROWTH = {1: "poly", 2: "exp"}


@dataclass(frozen=True)
class Specimen:
    id: str
    name: str
    rule: Rule
    cells: np.ndarray = field(repr=False)  # int levels 0..255
    source: str = ""

    @property
    def cells_sha256(self) -> str:
        return hashlib.sha256(np.ascontiguousarray(self.cells, dtype="<i2").tobytes()).hexdigest()

    def place(self, size: int | tuple[int, int] = 128) -> np.ndarray:
        ny, nx = (size, size) if isinstance(size, int) else size
        h, w = self.cells.shape
        if h > ny or w > nx:
            raise ValueError(f"{self.id} ({h}x{w}) does not fit a {ny}x{nx} grid")
        A = np.zeros((ny, nx), dtype=np.float64)
        y0, x0 = (ny - h) // 2, (nx - w) // 2
        A[y0 : y0 + h, x0 : x0 + w] = self.cells / 255.0
        return A

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "cells_shape": list(self.cells.shape),
            "cells_level_sum": int(self.cells.sum()),
            "cells_sha256_int16le": self.cells_sha256,
            "rule": self.rule.to_dict(),
        }


def _s001() -> Specimen:
    path = SPECIMEN_DIR / "S001-orbium" / "initial-cells-u8.csv"
    cells = np.loadtxt(path, delimiter=",", dtype=np.int64)
    return Specimen(
        id="S001",
        name="Orbium unicaudatus (O2u)",
        rule=Rule(R=13, T=10, mu=0.15, sigma=0.015, beta=(1.0,), kernel="poly", growth="poly"),
        cells=cells,
        source="research/specimens/S001-orbium.md; Chakazul/Lenia@adfc542 Python/animals.json code O2u",
    )


_REGISTRY = {"S001": _s001}


def register(specimen_id: str, loader) -> None:
    """Add a specimen loader (a zero-argument callable returning a Specimen)."""
    if specimen_id in _REGISTRY:
        raise ValueError(f"specimen {specimen_id} already registered")
    _REGISTRY[specimen_id] = loader


def ids() -> list[str]:
    return sorted(_REGISTRY)


def load(specimen_id: str) -> Specimen:
    try:
        return _REGISTRY[specimen_id]()
    except KeyError:
        raise KeyError(f"unknown specimen {specimen_id!r}; known: {ids()}") from None


def from_catalog(code: str, specimen_id: str | None = None, path: Path = ANIMALS_JSON) -> Specimen:
    """Build a specimen from the pinned upstream catalog (needs .refs/Lenia)."""
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != ANIMALS_SHA256:
        raise ValueError(f"animals.json sha256 {digest} != pinned {ANIMALS_SHA256}")
    entries = [e for e in json.loads(raw) if e.get("code") == code]
    if len(entries) != 1:
        raise KeyError(f"expected one catalog entry with code {code!r}, found {len(entries)}")
    e = entries[0]
    p = e["params"]
    rule = Rule(
        R=int(p["R"]),
        T=p["T"],
        mu=p["m"],
        sigma=p["s"],
        beta=tuple(float(Fraction(x)) for x in str(p["b"]).split(",")),
        kernel=_CATALOG_KERNEL[p.get("kn", 1)],
        growth=_CATALOG_GROWTH[p.get("gn", 1)],
    )
    return Specimen(
        id=specimen_id or f"catalog:{code}",
        name=e.get("name", code),
        rule=rule,
        cells=rle.decode(e["cells"]),
        source=f"Chakazul/Lenia@adfc542 Python/animals.json code {code}",
    )
