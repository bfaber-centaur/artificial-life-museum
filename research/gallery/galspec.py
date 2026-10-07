"""Gallery specimen registration, with the one isolated dependency on unmerged PR #11.

S001 is registered in ``alm.specimens`` on main. S101-S103 are Lane 6 specimens proposed in
PR #11 (branch ``claude/night0-field-tmbx06``), which is not merged. Their exact seed cells
and rules are vendored here, under ``vendor/pr11/``, and nowhere else in the gallery:

- if ``alm.specimens`` already knows an ID (PR #11 merged), the official registration is used
  and its cells and rule must equal the vendored copy, or ``ensure_registered`` raises;
- otherwise the vendored copy is registered under the same ID.

Delete ``vendor/pr11/`` and the ``PR11`` table once PR #11 lands and nothing else changes.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from alm import specimens
from alm.lenia import Rule

VENDOR = Path(__file__).resolve().parent / "vendor" / "pr11"
PR11_COMMIT = "f40f303e7a9a71be7cb1ff8038372540f358d53d"

_S001_RULE = Rule(R=13, T=10, mu=0.15, sigma=0.015, beta=(1.0,), kernel="poly", growth="poly")
_COEX_RULE = Rule(R=13, T=10, mu=0.155, sigma=0.020, beta=(1.0,), kernel="poly", growth="poly")

# ID -> (slug, registered name, rule, sha256 of the vendored CSV), copied from PR #11's
# src/alm/specimens.py and research/specimens/<ID>-<slug>/initial-cells-u8.csv at PR11_COMMIT.
PR11 = {
    "S101": ("orbium-pair", "bound Orbium pair (Synorbium-like) under the S001 rule", _S001_RULE,
             "a42c1f9d7cf50f9cd5abe1ad7845e99d1198b2f50a9032f12ec40325b69e698b"),
    "S102": ("circler", "Gyrorbium-like circler under the coexistence rule", _COEX_RULE,
             "a087169c504626baac319a72aa2d9be517a439a415556de300880d92ae2c6547"),
    "S103": ("static-ring", "Circium-like static ring under the coexistence rule", _COEX_RULE,
             "aadf75cec9a60d559dea7a93572fd7d0170a2671f2d4e55f96a296c7ecc0830b"),
}


def _vendored(specimen_id: str) -> specimens.Specimen:
    slug, name, rule, sha = PR11[specimen_id]
    path = VENDOR / f"{specimen_id}-{slug}-initial-cells-u8.csv"
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != sha:
        raise ValueError(f"{path} sha256 {got} != pinned {sha}")
    return specimens.Specimen(
        id=specimen_id,
        name=name,
        rule=rule,
        cells=np.loadtxt(path, delimiter=",", dtype=np.int64),
        source=(f"research/gallery/vendor/pr11/{path.name} (vendored from unmerged PR #11 "
                f"@ {PR11_COMMIT[:7]}, research/specimens/{specimen_id}-{slug}/initial-cells-u8.csv)"),
    )


def ensure_registered() -> None:
    for sid in PR11:
        vend = _vendored(sid)
        if sid in specimens.ids():
            official = specimens.load(sid)
            if official.rule != vend.rule or not np.array_equal(official.cells, vend.cells):
                raise ValueError(f"{sid} in alm.specimens differs from the vendored PR #11 copy")
        else:
            specimens.register(sid, lambda sid=sid: _vendored(sid))
