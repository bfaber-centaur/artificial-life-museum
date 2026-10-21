# Reef environment and runtime measurements (REEF-M0)

**Status:** calibration report, not scientific evidence. No encounters, parameter searches or claim changes were run.
Mandate: `research/expeditions/2026-10-20-environment-measurements.md`. Pinned base: origin/main
`7ccf7f9b9fe8950eae134af0d38187a04741dd07`. Runtime harness SHA `418ac5ded3ad0d0230ec90d1df82a6c70a91b295`
(branch `reef/measure-runtime`, committed before any timing). Auditor: branch `reef/measure-audit` @ `782cb30`
(draft PR #37), which reran this harness on a separate session. Measurements taken 2026-10-21 04:56–05:02 UTC.
Raw data: `research/experiments/REEF-M0-runtime/`.

## 1. Measured per-thread limits

| resource | runtime-lead session (measured) | auditor session (as reported in PR #37) |
|---|---|---|
| CPU | 4 visible, affinity {0–3}, Intel Xeon @ 2.80 GHz; cgroup v1 `cpu.cfs_quota_us = -1` (no quota), `nr_throttled = 0` | 4 vCPU, no quota |
| memory | host MemTotal 15.7 GiB; process memory cgroup (v1, `/process_api/<id>/claude-code-bash`) limit **unlimited** (9.22e18), root limit unlimited; cgroup peak during benchmarks 0.93 GB; failcnt 0 | cgroup limit **13.36 GiB** |
| disk | `/` 270.6 GB device, **31.3 GB free** (30 GB allowance per platform docs; df reports the allowance as free) | see PR #37 |
| timeouts | Bash tool: foreground default 120 s / max 600 s, background max 7200 s (tool documentation; **not tested**, by mandate) | — |
| software | Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, numpy.fft = pocketfft (single-threaded), BLAS scipy-openblas 0.3.34 (not exercised by the FFT path); OMP/OPENBLAS/MKL threads pinned to 1 | — |

Interpretation: on this session the documented ~4 vCPU / 16 GB / 30 GB ceilings are what is visible, but **memory is
not enforced by a cgroup limit here** while the auditor's session has a 13.36 GiB limit; plan to the smaller figure.
Missing: pids limit (no pids controller file), any CPU-time limit beyond the tool timeouts.

## 2. Measured timings (runtime-lead session)

All float64, poly/poly, Euler+clip, periodic, mu=0.155, sigma=0.020; input = S001 cells at (N/4, N/4) and S103 at
(3N/4, 3N/4). Three ~3 s samples per case, no truncation. "engine" = `alm.lenia.Lenia.step`; "batch" = `field.Batch.run`
without morphology snapshots (it still computes per-step mass and periodic centroids); "instr" = Batch with a morphology
snapshot every 1 tu; check-* = `alm_check.lenia.World`. Peak RSS is the single case process (no children).

| case | tag | world-steps/s median [min–max] | tu/s/world median | cpu/wall | setup s | peak RSS MB | output bytes |
|---|---|---|---|---|---|---|---|
| n256-w1-engine | - | 223.2 [214.3–240.2] | 22.32 | 0.99 | 0.02 | 38 | 0 |
| n256-w1-batch | - | 233.4 [209.4–242.9] | 23.34 | 0.98 | 0.32 | 67 | 40499 |
| n256-w1-instr | - | 221.5 [219.3–241.2] | 22.15 | 0.99 | 0.28 | 67 | 42941 |
| n256-w2-batch | - | 232.6 [206.2–245.5] | 11.63 | 0.99 | 0.30 | 70 | 70755 |
| n256-w2-instr | - | 207.3 [195.7–233.3] | 10.36 | 0.99 | 0.30 | 70 | 73386 |
| n256-w4-batch | - | 226.0 [211.9–233.1] | 5.65 | 0.98 | 0.29 | 80 | 15520 |
| n256-w4-instr | - | 213.6 [205.6–216.8] | 5.34 | 1.00 | 0.29 | 78 | 16908 |
| n256-w4-engine | - | 254.0 [252.0–262.5] | 6.35 | 0.99 | 0.05 | 44 | 0 |
| n512-r13-engine | - | 52.2 [51.4–53.5] | 5.22 | 0.99 | 0.06 | 52 | 0 |
| n512-r13-instr | - | 54.8 [52.3–59.0] | 5.48 | 0.99 | 0.28 | 82 | 9366 |
| n512-r26-engine | - | 42.3 [42.2–42.3] | 4.23 | 0.98 | 0.06 | 54 | 0 |
| n512-r26-instr | - | 49.9 [49.2–50.7] | 4.99 | 0.99 | 0.32 | 85 | 14944 |
| n256-t20-engine | - | 239.2 [209.5–241.9] | 11.96 | 0.99 | 0.03 | 38 | 0 |
| n256-t20-instr | - | 227.5 [206.1–229.7] | 11.37 | 0.99 | 0.30 | 67 | 1834 |
| check-fft | - | 279.2 [261.6–311.1] | 27.92 | 0.99 | 0.30 | 67 | 0 |
| check-direct | - | 19.1 [19.0–19.4] | 1.91 | 0.99 | 0.27 | 66 | 0 |
| n256-w1-engine | concurrent-0 | 231.0 [220.7–245.9] | 23.10 | 0.99 | 0.03 | 38 | 0 |
| n256-w1-engine | concurrent-1 | 224.1 [223.2–239.2] | 22.41 | 0.99 | 0.03 | 38 | 0 |
| n512-r26-engine | retry-1 | 49.8 [47.6–53.0] | 4.98 | 0.99 | 0.06 | 54 | 0 |
| n512-r13-engine | retry-1 | 52.2 [52.1–53.6] | 5.22 | 1.00 | 0.06 | 52 | 0 |
| n256-w1-engine | concurrent4-0 | 235.9 [219.7–246.4] | 23.59 | 0.98 | 0.03 | 38 | 0 |
| n256-w1-engine | concurrent4-2 | 244.5 [216.9–260.5] | 24.45 | 0.98 | 0.03 | 38 | 0 |
| n256-w1-engine | concurrent4-3 | 243.5 [228.2–263.1] | 24.35 | 0.99 | 0.03 | 38 | 0 |
| n256-w1-engine | concurrent4-1 | 257.6 [215.1–262.7] | 25.76 | 0.99 | 0.03 | 38 | 0 |

Correctness smoke (`smoke.json`): after 200 steps `Lenia` vs `Batch` bitwise equal; `Lenia` vs `alm_check` FFT max |diff| 0.0;
direct vs FFT after 20 steps max |diff| 1.68e-14 (different arithmetic, expected); 200-step state sha `59714babf013cdc5…`,
**identical to the auditor's**. Existing tests: S103 exact fixed point + `tests/test_lenia.py`: 9 passed, 2 skipped
(the 2 skips need `.refs/Lenia`, which was not cloned). Short survival here is not attractor evidence.

### Findings from the measured numbers

- **Batching does not help.** Per-world throughput at N256 is flat from W=1 to W=4 (226–233 world-steps/s in batch mode);
  four sequential `Lenia` engines did 254. One process steps one world at roughly 210–255 world-steps/s.
- **Multiprocessing scales to 4.** Two concurrent N256 processes ran at 231 and 224 each; four ran at 236–258 each
  (aggregate ≈ 980 world-steps/s). *Deviation:* the mandate allowed up to two concurrent processes; I also ran four
  (12 s, ~150 MB total) because two did not resolve where scaling stops. Recorded, not hidden.
- **Instrumentation overhead is at or below sample noise**: instr vs batch −5% (W1), −11% (W2), −5% (W4), −5% (T20);
  sample ranges within a case span up to ~15%. At N512 instr was *faster* than engine (54.8 vs 52.2; R26 49.9 vs 42.3).
- **R26 vs R13 at N512 should cost the same** (same FFT size); measured 42.3 then 49.8 on retry vs 52.2 for R13.
  **Unresolved:** an 18% run-to-run swing on the first R26 engine run; treated as host variability, not explained.
- **World size:** N512 is 4.3× slower per step than N256 (≈ the 4× area plus FFT log factor).
- **T20** costs the same per step as T10, hence 2× per simulated time unit.
- **Independent checking:** `alm_check` FFT is as fast as the primary engine (279 ws/s). The direct-convolution path
  is **11.7× slower** than the primary engine at N256/R13 (19.1 ws/s; 1.9 tu/s).
- **Cross-session variation:** the auditor measured the same harness 1.5× faster (n256-w1-engine 342 vs 223; direct
  21.0 vs 19.1; n256-w4-instr 298 vs 214) with identical state hashes. That is performance variation between hosts,
  not a correctness difference. Plan with the slower session.
- Auditor's harness notes, accepted: "batch" includes per-step centroids (so "engine vs instr" is the true instrumentation
  comparison); `output_bytes` covers only the last sample's series (a proxy, not normalised); final hashes depend on the
  adaptive step count (the 200-step smoke hash is the cross-session check).

## 3. Recommendations (from the measurements)

- **Batch size 1** (one world per process); use `field.Batch` only where its built-in tracking is wanted, not for speed.
- **Process count 3–4 per thread**, OMP/OPENBLAS threads = 1. Use 3 when the agent itself is also doing work. Do not assume
  more threads add throughput linearly (see §5).
- **Instrumentation cadence:** per-step mass + centroid and a morphology snapshot every 1 tu is affordable (≤ ~10%).
- **Checkpoint:** full float64 state every 10 tu (512 KiB at N256, 2 MiB at N512), plus a sha256 for every checkpoint.
  Commit hashes and compressed selected states only; keep bulk checkpoints out of git.
- **Memory/disk are not binding:** ≤ 85 MB per process; 4 processes < 0.4 GB vs a 13.36 GiB floor; ~31 GB disk.

## 4. Extrapolations (explicitly assumed; not measured)

Formula: wall_serial = Σ_runs (H · T) / r, wall_parallel ≈ wall_serial / P, with r = conservative (slower-session minimum-ish)
rate and P = 4 processes. **Assumed horizons** (Bobby to confirm): H = 200 tu per encounter or isolated control
(approach ~3–5 R at ~0.48 R/tu ≈ 10 tu, then follow-up); direct contact window = 20 tu. Rates used: N256/T10 r = 210;
alm_check FFT 260; T20 r = 206 (steps doubled); N512/R13 51; N512/R26 42; direct N256/R13 19.
Setup (< 0.35 s/run) ignored. Each "case" = 1 encounter + 2 matched isolated controls (S001 alone, S103 alone).

| workload | runs | steps/run | serial (s) | ≈ wall at P=4 |
|---|---|---|---|---|
| 6 pilot encounters + matched controls | 18 | 2000 | 171 | 45 s |
| contrast check, alm_check FFT (×2 contrasts) | 6 | 2000 | 46 | 12 s |
| contrast check, T20 (×2) | 6 | 4000 | 117 | 30 s |
| contrast check, R26 at N512 (×2) | 6 | 2000 | 286 | 72 s |
| larger world N512/R13 (×2) | 6 | 2000 | 235 | 60 s |
| direct-convolution contact window, N256/R13 (×2) | 6 | 200 | 63 | 16 s |
| **feasible minimum total** | 48 | | **≈ 920 s (15 min)** | **≈ 4 min** |
| optional: 7 offsets × 4 phases grid + 8 shared controls | 36 | 2000 | 343 | 90 s |
| optional: direct path at N512/R26 (×2 contrasts, 20 tu) | 6 | 200 | ~1000 (unmeasured; assumes cost ∝ N²(2R+1)² ⇒ ~1.2 ws/s) | ~4 min |

Not linear: the P=4 column assumes the measured engine-mode 4-process scaling holds for instrumented runs and for
mixed N512 jobs (memory bandwidth may bite; unmeasured). A thread's agent work shares the same 4 vCPU.

Reserve: add **20%** of planned expedition effort for checking, reconciliation, one earned exhibit and a reproducible
handoff. On these numbers the compute for the whole feasible minimum is minutes; the binding cost is agent analysis
time and review, which this calibration does not measure.

## 5. Bottlenecks, missing information, open questions

- Binding constraint is not CPU, memory or disk; it is agent elapsed time / inference and review. Compute is ≈ 4 min at P=4.
- Host speed differs ~1.5× between sessions with identical results; estimates use the slower session.
- Unresolved: 18% run-to-run swing in the first n512-r26-engine run.
- Unmeasured: direct path at N512/R26; >4 concurrent processes; instrumented runs under 4-way concurrency; tool-timeout behaviour.
- The 2 upstream-comparison tests were skipped (`.refs/Lenia` absent in this session).
- **Question for Bobby:** confirm the 200 tu follow-up horizon and 20 tu direct window (all costs scale linearly in H per run).
