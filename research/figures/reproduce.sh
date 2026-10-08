#!/usr/bin/env bash
# Rebuild every Lane 9 figure from committed data. Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
(cd research/figures && "../../$PY" -m figlib.style --write-json)
"$PY" research/figures/A-survival-boundary/make_figure.py
# Figure C reads merged PR data at pinned merge commits on main (git show; no checkout).
"$PY" research/figures/C-phenotypes-one-rule/make_figure.py
# Figure D reads unmerged PR #27 and merged #29 and #30 at pinned commits; fetch them if missing.
for c in 968d330235e234fae4c6818a07c2b9eeee265113 0b9b47f8d7c48847219441cd15152792adbd45de 20bdff9f3827290cff6646fae6bc8f283e5aa373; do
  git cat-file -e "$c" 2>/dev/null || git fetch -q origin claude/night0-field-tmbx06 claude/night0-hostile-review-o3avnq claude/night0-replication-13cz1b
done
"$PY" research/figures/D-pair-and-circler/make_figure.py
