#!/usr/bin/env bash
# Rebuild every Lane 9 figure from committed data. Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
(cd research/figures && "../../$PY" -m figlib.style --write-json)
"$PY" research/figures/A-survival-boundary/make_figure.py
# Figure C reads merged PR data at pinned merge commits on main (git show; no checkout).
"$PY" research/figures/C-phenotypes-one-rule/make_figure.py
# Figure D reads unmerged PRs #27 and #30 at pinned commits; fetch them if missing.
for c in 3ccb8045d83427510671c5e283f933f3513c10e7 9fc48b423b7cef51033dbb0855e212790cc018f2; do
  git cat-file -e "$c" 2>/dev/null || git fetch -q origin claude/night0-field-tmbx06 claude/night0-hostile-review-o3avnq
done
"$PY" research/figures/D-pair-and-circler/make_figure.py
