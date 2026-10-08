#!/usr/bin/env bash
# Rebuild every Lane 9 figure from committed data. Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
(cd research/figures && "../../$PY" -m figlib.style --write-json)
"$PY" research/figures/A-survival-boundary/make_figure.py
# Figure C reads Lane 6's data at the PR #11 merge commit on main (git show; no checkout).
# It also reads pinned commits from Lane 6's D2 rerun and the PR #22 ledger (Lane 3's data is on main).
for c in 413003da752922e61be8a220abff8d86600e6aee \
         a9ff91867b4dd6cad080fe7ae3f0cc4a6ef9f006; do
  git cat-file -e "$c" 2>/dev/null || git fetch -q origin \
    claude/night0-field-tmbx06 claude/night1-claims-l3002-w1iy56
done
"$PY" research/figures/C-phenotypes-one-rule/make_figure.py
