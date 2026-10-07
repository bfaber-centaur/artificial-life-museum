# Vendored from unmerged PR #11 (Lane 6, field exploration)

This folder is the gallery's only dependency on PR #11 (branch `claude/night0-field-tmbx06`),
which was **not merged** when the gallery was built. The files are byte-for-byte copies at PR #11
head `f40f303e7a9a71be7cb1ff8038372540f358d53d`; the seed CSVs are identical at `83c8bff`, the
commit the claims ledger cites.

| Specimen | File here | Copied from (PR #11) | sha256 |
| --- | --- | --- | --- |
| S101 | `S101-orbium-pair-initial-cells-u8.csv` | `research/specimens/S101-orbium-pair/initial-cells-u8.csv` | `a42c1f9d…698b` |
| S102 | `S102-circler-initial-cells-u8.csv` | `research/specimens/S102-circler/initial-cells-u8.csv` | `a087169c…6547` |
| S103 | `S103-static-ring-initial-cells-u8.csv` | `research/specimens/S103-static-ring/initial-cells-u8.csv` | `aadf75ce…830b` |

Rules, copied from PR #11's `src/alm/specimens.py`: S101 uses the S001 rule (R 13, T 10, μ 0.15,
σ 0.015, β [1], poly/poly); S102 and S103 use the coexistence rule (same, but μ 0.155, σ 0.020).

[`../../galspec.py`](../../galspec.py) checks the hashes, registers these IDs in `alm.specimens`
only if main does not already have them, and refuses to run if main's copy differs. When PR #11
merges, delete this folder and the `PR11` table; the gallery's run IDs and pictures stay valid
as long as the check passes.

The specimens' scientific status is whatever `research/claims.md` says (C038–C045: Lane 6's own
evidence, not yet reproduced by a second lane).
