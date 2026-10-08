#!/usr/bin/env bash
# Rebuild every Lane 9 figure from committed data. Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
(cd research/figures && "../../$PY" -m figlib.style --write-json)
"$PY" research/figures/A-survival-boundary/make_figure.py
# Figure C reads merged PR data at pinned merge commits on main (git show; no checkout).
"$PY" research/figures/C-phenotypes-one-rule/make_figure.py
# Figure D reads unmerged PRs #27, #30 and #29 at pinned commits; fetch them if missing.
for c in e1f8760c5055f671dc07ef9a4f9ff782da6bdfa6 c063d7377dffed70fafe460c3a10fec4205e0169 8c3c082c16181a942ec12b1d555c74d4b32beded; do
  git cat-file -e "$c" 2>/dev/null || git fetch -q origin claude/night0-field-tmbx06 claude/night0-hostile-review-o3avnq claude/night0-replication-13cz1b
done
"$PY" research/figures/D-pair-and-circler/make_figure.py
