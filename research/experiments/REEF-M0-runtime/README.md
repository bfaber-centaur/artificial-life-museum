# REEF-M0-runtime: environment and runtime calibration (runtime lead)

Calibration only. Base: origin/main 7ccf7f9b9fe8950eae134af0d38187a04741dd07. Harness committed at
418ac5ded3ad0d0230ec90d1df82a6c70a91b295 before any timing (SPEC.md, bench.py).

Files: SPEC.md (benchmark spec), bench.py (harness), summarize.py, inventory.json (environment),
smoke.json + pytest.log (correctness smoke), results.jsonl (raw, one record per case run), timings.csv
(one row per sample), summary-table.md, run-all.log / run-extra.log (stdout), SHA256SUMS.

Reproduce (from repo root, after `pip install -e '.[dev]'`):

    cd research/experiments/REEF-M0-runtime
    python bench.py inventory && python bench.py smoke
    rm -f results.jsonl && python bench.py all
    python bench.py concurrent
    python bench.py case n512-r26-engine retry-1; python bench.py case n512-r13-engine retry-1
    python -c "import subprocess,sys;ps=[subprocess.Popen([sys.executable,'bench.py','case','n256-w1-engine',f'concurrent4-{i}']) for i in range(4)];[p.wait() for p in ps]"
    python summarize.py
    (cd ../../.. && OMP_NUM_THREADS=1 python -m pytest -q tests/test_lane6_specimens.py::test_s103_is_an_exact_fixed_point tests/test_lenia.py)

Input SHA-256 (float64 C-order): N256 6a4a13b0…bffee, N512/R13 28b6ee59…daad74, N512/R26 (kron 2x2 of N256) 6afa618e…daad74 — full hashes in results.jsonl.
