#!/usr/bin/env bash
# Reproduce every L4-001 result from a fresh clone (after ./scripts/bootstrap.sh).
# Usage: research/experiments/L4-001-disturbance-battery/reproduce.sh [stage...]
# Stages: base checks a1 edge states analyze (default: all, in that order).
# The alm-engine check needs Lane 2's simulator: either merged into src/alm, or
# ALM_SRC=/path/to/checkout/src set in the environment.
set -euo pipefail
cd "$(dirname "$0")/../../.."
E=research/experiments/L4-001-disturbance-battery
PY=.venv/bin/python
stages=("$@")
[ ${#stages[@]} -eq 0 ] && stages=(base checks a1 edge states analyze)

for st in "${stages[@]}"; do
  case "$st" in
    base)
      $PY $E/run.py sweep --out $E/results/coarse.csv
      $PY $E/run.py bisect --coarse $E/results/coarse.csv --out $E/results/bisect.csv ;;
    checks)
      $PY $E/run.py check --engine alm --out $E/results/check-alm-N128.csv
      $PY $E/run.py check --size 192 --out $E/results/check-ref-N192.csv
      $PY $E/run.py check --horizon 5000 --phases 1000 --out $E/results/check-ref-N128-H5000.csv
      $PY $E/run.py bisect --size 192 --coarse $E/results/coarse.csv --out $E/results/bisect-N192.csv
      $PY $E/run.py check --centroid local --out $E/results/check-ref-N128-cL.csv
      $PY $E/run.py check --centroid local --size 192 --out $E/results/check-ref-N192-cL.csv ;;
    a1)
      $PY $E/run.py sweep --cond T20 --out $E/results/T20/coarse.csv
      $PY $E/run.py bisect --cond T20 --coarse $E/results/T20/coarse.csv --out $E/results/T20/bisect.csv
      $PY $E/run.py sweep --cond R26 --size 256 --out $E/results/R26/coarse.csv
      $PY $E/run.py bisect --cond R26 --size 256 --coarse $E/results/R26/coarse.csv --out $E/results/R26/bisect.csv ;;
    edge)
      $PY $E/explore_separatrix.py
      $PY $E/explore_separatrix.py --scan
      L4_ENGINE=alm $PY $E/explore_separatrix.py --scan
      $PY $E/plot_separatrix.py ;;
    states)
      $PY $E/save_states.py ;;
    analyze)
      $PY $E/analyze.py ;;
    *) echo "unknown stage $st" >&2; exit 2 ;;
  esac
done
