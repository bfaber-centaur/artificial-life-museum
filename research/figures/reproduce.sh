#!/usr/bin/env bash
# Rebuild every Lane 9 figure from committed data. Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
(cd research/figures && "../../$PY" -m figlib.style --write-json)
"$PY" research/figures/A-survival-boundary/make_figure.py
# Figure C reads Lane 6's PR #11 at a pinned commit; fetch it if it is missing.
git cat-file -e f40f303e7a9a71be7cb1ff8038372540f358d53d 2>/dev/null || git fetch -q origin claude/night0-field-tmbx06
"$PY" research/figures/C-phenotypes-one-rule/make_figure.py
