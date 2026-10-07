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
only if main does not already have them, and refuses to run if main's copy differs. PR #12 does
not depend on PR #11 merging; it works the same whether or not #11 lands.

## Cleanup after PR #11 merges

Do this as its own small PR, after #11 is on main:

1. On updated main, run `.venv/bin/python -m pytest -q tests/test_gallery.py`. If it passes,
   main's S101–S103 have exactly the vendored cells and rules (`galspec.ensure_registered`
   compares them), and the steps below change nothing that any picture depends on. If it fails
   because main's cells or rules differ, stop. Keep this folder and report the difference to
   the coordinator: the gallery's runs were made from the vendored seeds and stay reproducible
   from them.
2. Delete `research/gallery/vendor/pr11/` (this folder) and `research/gallery/galspec.py`. In
   `research/gallery/run_specimen.py`, remove the `galspec` import and call (it still registers
   the gallery's interventions, so keep the file).
3. In `research/gallery/render.py`, remove `import galspec`, both `galspec.ensure_registered()`
   calls, and the `galspec.PR11 or` part of the condition in `_run_command` (keep the
   `gallery_ivs` part).
4. In `tests/test_gallery.py`, delete `test_vendored_specimens_register_and_match_pins`, the
   `galspec` import and the `ensure_registered()` calls. Keep
   the S103 fixed-point test and the render-pipeline tests as they are.
5. In `research/gallery/README.md`, point the "Seed cells from" column at
   `research/specimens/S10x-*/`. Then delete the "Unmerged dependency" paragraph and the
   S101–S103 note on the `run_specimen.py` line under "Reproduce", and add a cycle-log line.
6. Run `render.py render` and check that `git status` shows no changed media. Do not re-run
   `collect`: the existing traces keep their run IDs and hashes, and their manifests still name
   the vendored source, which is the historical record of how they were made.

The specimens' scientific status is whatever `research/claims.md` says (C038–C045: Lane 6's own
evidence, not yet reproduced by a second lane).
