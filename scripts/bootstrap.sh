#!/usr/bin/env bash
# Recreate the ALM working environment from a fresh clone.
# Idempotent: safe to re-run. Usage: ./scripts/bootstrap.sh
set -euxo pipefail

cd "$(dirname "$0")/.."

LENIA_URL=https://github.com/Chakazul/Lenia.git
LENIA_SHA=adfc542939266de7f4bb7ebb552e8499701ee107

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip wheel
# Dependencies come from pyproject.toml, not upstream Python/requirements.txt.
python -m pip install -e '.[dev]'

mkdir -p .refs
if [ ! -d .refs/Lenia/.git ]; then
  git clone "$LENIA_URL" .refs/Lenia
fi
if ! git -C .refs/Lenia cat-file -e "$LENIA_SHA^{commit}" 2>/dev/null; then
  git -C .refs/Lenia fetch origin "$LENIA_SHA"
fi
git -C .refs/Lenia checkout --detach "$LENIA_SHA"

mkdir -p \
  research/specimens \
  research/experiments \
  research/traces \
  research/reports

python - <<'PY'
import numpy, scipy, PIL, matplotlib, imageio, alm
print("ALM environment ready")
print("numpy:", numpy.__version__)
print("scipy:", scipy.__version__)
print("alm:", alm.__version__)
PY

actual_sha=$(git -C .refs/Lenia rev-parse HEAD)
echo "Lenia reference: $actual_sha"
test "$actual_sha" = "$LENIA_SHA"
