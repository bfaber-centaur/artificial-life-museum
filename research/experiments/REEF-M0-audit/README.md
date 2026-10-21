# REEF-M0 audit: independent environment and runtime check

Auditor lane of `research/expeditions/2026-10-20-environment-measurements.md`. Calibration only:
no encounters, parameter searches, claim changes or merges. All inputs are timing inputs.

- Baseline: `origin/main` = `7ccf7f9b9fe8950eae134af0d38187a04741dd07` (contains the required commit; it is the tip).
- Auditor harness committed before results: `46561aa` (`audit_bench.py`).
- Lead harness rerun from its exact committed SHA: `reef/measure-runtime` @ `418ac5ded3ad0d0230ec90d1df82a6c70a91b295`,
  checked out in a detached worktree so neither lane's output was overwritten.
- Session: separate cloud container from the lead (`session_01DFiPip…`). Measured 2026-10-21 04:55–05:01 UTC.

## Files

| file | what |
|---|---|
| `inventory.json` / `inventory.py` | allowlisted resource inventory (no env dump) |
| `audit_bench.py`, `raw/timings.jsonl`, `raw-bench.log` | independent timing matrix (own harness, own input construction) |
| `lead-harness-418ac5d-rerun.jsonl` | lead harness rerun on this session: `n256-w1-engine`, `check-direct`, `n256-w4-instr`, 2-process `concurrent` |
| `lead-harness-418ac5d-smoke.json` | lead harness `smoke` on this session |
| `smoke.py`, `smoke.json` | auditor's own correctness smoke (separately placed S001 / S103 worlds) |
| `pytest.log` | `tests/test_lane6_specimens.py tests/test_lenia.py`: 15 passed, 2 skipped |

Reproduce (repo root, after `pip install -e '.[dev]'`):

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python research/experiments/REEF-M0-audit/audit_bench.py research/experiments/REEF-M0-audit/raw
python research/experiments/REEF-M0-audit/smoke.py
python research/experiments/REEF-M0-audit/inventory.py
# lead harness, from a worktree at 418ac5d, PYTHONPATH=<worktree>/src:
python bench.py case n256-w1-engine audit-rerun; python bench.py case check-direct audit-rerun
python bench.py case n256-w4-instr audit-rerun; python bench.py concurrent; python bench.py smoke
```

## Resources (this session)

| quantity | measured | interpretation |
|---|---|---|
| CPU | 4 visible, affinity 4, cpuset `0-3`, CFS quota `-1`, `nr_throttled 0` | 4 vCPU, no quota throttling observed. Matches the documented ~4 vCPU. Intel Xeon @ 2.80 GHz, 1 thread/core |
| memory | `/proc/meminfo` 16.5 GB, no swap; root cgroup unlimited; **the process's own memory cgroup** (`/process_api/<id>/claude-code-bash`, cgroup v1) limit **14,343,688,192 B = 13.36 GiB**; failcnt 0 | the effective limit is ~13.4 GiB, not the 16 GB host figure. Exceeding it OOM-kills with no swap |
| disk | device reports 252 G, but free = **31.3 GB** writable allowance | ~30 GB per-session allowance; matches docs. `df` "Size" is misleading |
| cgroup | v1 hybrid; `0::/` unified hierarchy is empty; pids cgroup has no `pids.max` | v2 paths are unavailable here |
| timeouts | Bash tool: foreground default 120 s, max 600 s; background default 30 min, max 2 h | from tool documentation; not tested by running long jobs |
| stack | Python 3.13.16, NumPy 2.5.3 (scipy-openblas 0.3.34), SciPy 1.18.1; numpy.fft = pocketfft, single-threaded | BLAS is not on the stepping path |

## Timings (this session, float64 poly/poly, mu .155, sigma .020, Euler+clip, periodic)

3 samples of ~2.3–3.4 s each, no truncation. "ws/s" = world-steps per second, median (min–max).

| case | auditor harness | lead harness @418ac5d rerun here |
|---|---|---|
| N256 R13 T10, `alm.lenia.Lenia`, 1 world, engine only | 336.5 (wall 2.60–2.68 s) | 342.2 (314.0–347.3) |
| N256, `field.Batch` W1, per-step mass+centroid, morph every 100 steps | 316.1 | — |
| N256, same update arithmetic, no measurements, W1 | 354.3 | — |
| N256, `field.Batch` W2 | 286.4 | — |
| N256, `field.Batch` W4 (auditor: morph/100; lead: morph every T steps) | 311.0 | 297.9 (279.1–341.7) |
| N256, no measurements, W4 | 306.6 | — |
| N512 R13 T10, `field.Batch` W1 | 74.0 | — |
| N512 R26 T10, `field.Batch` W1 (block-resized seed) | 73.7 | — |
| N256 R13 **T20**, `field.Batch` W1 | 334.1 ws/s = **16.7 tu/s** (vs 31.6 tu/s at T10) | — |
| `alm_check` FFT, N256 | 373.8 | — |
| `alm_check` **direct**, N256 (wrap) | **20.98** (61 steps/sample) | **21.02** (21.0–21.1) |
| 2 concurrent processes, N256 engine, each | — | 332.1 and 331.6 (aggregate ~664) |

Peak RSS per case process: 38–85 MB. Lead `n256-w4-instr` output (compressed npz of series + final): 144,793 B per 223-step sample.

## Correctness smoke

- `alm.lenia` vs `field.Batch`: bitwise equal after 200 steps (both harnesses, both seeds).
- `alm_check` FFT vs `alm.lenia`: max |diff| = 0.0 after 200 steps. Note: although `alm_check` was written
  independently, its FFT path reduces to the same numpy rfft arithmetic, so this agreement is an
  implementation check, not an arithmetic one. Only the direct path is different arithmetic.
- Direct vs FFT: 1.68e-14 after 20 steps (lead input), 5.2e-13 after 200 steps (S001 alone), 0.0 for S103.
- S103 under the coexistence rule: exact fixed point (max |dA| = 0 at step 501, identical to step 0). Existing test also passes.

## Audit findings

**Agreements (expected performance variation).** The two harnesses agree on this session to within 2% for the
engine FFT case (336.5 vs 342.2) and 0.2% for the direct path (20.98 vs 21.02), despite different input layouts
(auditor: one seed per world, centred; lead: both seeds in one world). Sample spread within one case is up to
~±10% (e.g. 279–342 ws/s at W4), so differences below ~10% between sessions should be read as noise.
The resource interpretation in the lead's inventory code (resolve the process's v1 memory cgroup and read its
limit rather than the root's) is correct for this container type; on this session it yields 13.36 GiB.

**Things the synthesis should carry.**
1. Batching does not help. W2 and W4 are no faster per world-step than W1 (286–311 vs 316–354 ws/s) in either harness.
   Use batching only for bookkeeping convenience; get parallelism from processes.
2. Two processes scale almost linearly (2 × ~332 ws/s on 4 vCPU). More than two concurrent processes was not tested,
   as the mandate allows; 4 should not be assumed linear.
3. Per-step centroid/mass instrumentation costs ~11% at W1 (316 vs 354). At W4 it was within noise (311 vs 307).
   Treat ~10% as the overhead estimate, with an unresolved W-dependence.
4. N512 costs 4.3–4.8× N256 per world-step. R does not change FFT cost (R26 = R13 at N512).
   T20 costs the same per step, so half the simulated time per second.
5. Direct convolution is **~16–18× slower** than FFT at N256/R13 (21 vs 336–374 ws/s), i.e. ~2.1 tu/s per process.
   The cost scales with (2R+1)², so at R26 expect ~4× worse again (extrapolation, not measured).

**Unresolved differences.** None in correctness. Lead's own timing results were not yet on
`reef/measure-runtime` when this audit was written (branch held only the harness commit `418ac5d`), so the
cross-session comparison is harness-vs-harness on the auditor's session only. Whoever writes the synthesis
should compare the lead's numbers to the table above and treat >10% gaps as session variation unless the
final-state hashes for an identical step count disagree.

**Review notes on the lead harness (418ac5d).** No defects found that would change results. Minor:
(a) `batch` mode still records per-step mass+centroid, so "engine vs batch" measures instrumentation and the
`field.Batch` code path together; (b) `output_bytes` covers only the last sample's series, so scale it by
steps; (c) final-state hashes depend on the adaptive step count, so they are not comparable across sessions;
use the 200-step smoke hash for that; on this session it is `59714babf013cdc5…` (compare with the lead's `smoke.json`).

## Extrapolations (labelled; formulas only, not measured)

Per process, N256/R13/T10 with instrumentation: ~300 ws/s ≈ 30 tu/s. Elapsed for a horizon H tu per world:
`t ≈ H × T / (ws/s)`, divided by up to 2 for two processes. Example: 1000 tu at T10 ≈ 33 s/world;
12 worlds (six pilots + six matched controls) ≈ 6.7 min on one process, ~3.4 min on two.
At N512 multiply by ~4.5, at T20 by 2, and for the direct contact window use ~21 ws/s (≈ 16× slower):
a 100-tu direct window at N256/R13/T10 ≈ 48 s. These assume steady state and no I/O beyond the measured npz size.
