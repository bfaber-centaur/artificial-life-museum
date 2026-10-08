#!/usr/bin/env bash
# Rebuild every Lane 9 figure from committed data. Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
(cd research/figures && "../../$PY" -m figlib.style --write-json)
"$PY" research/figures/A-survival-boundary/make_figure.py
# Figure C reads merged PR data at pinned merge commits on main (git show; no checkout).
git cat-file -e 5363da22c0230bea8257589d5903e3a4f9ea8275 2>/dev/null || git fetch -q origin claude/night1-claims-c047-w1iy56  # PR #25 ledger
"$PY" research/figures/C-phenotypes-one-rule/make_figure.py
