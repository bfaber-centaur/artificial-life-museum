# Reef environment and runtime measurements (REEF-M0), integrated

**Status:** calibration report, not scientific evidence. No encounters, parameter searches, claim changes or merges.
Mandate: `research/expeditions/2026-10-20-environment-measurements.md`.

This integrated version replaces the runtime-lane draft of this file (PR #38 @ `d8a495b`). Corrections to that draft
are listed in §8. Raw measurements in both lane directories are unchanged.

## 1. Provenance

| item | value |
|---|---|
| pinned base | origin/main `7ccf7f9b9fe8950eae134af0d38187a04741dd07` (both lanes) |
| runtime lane | `reef/measure-runtime`. Harness `418ac5d`, committed before timing. Results `d8a495b` (PR #38). Session `cse_01Ud…` |
| audit lane | `reef/measure-audit`. Own harness `46561aa`, committed before results. Results `782cb30` (PR #37). Session `session_01DFiPip…` |
| integration | `reef/measure-summary`: two `--no-ff` merges of the reviewed lane heads above, then this report |
| measured | 2026-10-21, 04:55–05:02 UTC on both sessions |
| raw data | `research/experiments/REEF-M0-runtime/` (results.jsonl, timings.csv, inventory.json, smoke.json, logs, SHA256SUMS) and `research/experiments/REEF-M0-audit/` (raw/timings.jsonl, lead-harness-418ac5d-rerun.jsonl and -smoke.json, inventory.json, smoke.json, pytest.log) |
| software (both sessions) | Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1. numpy.fft is pocketfft and single-threaded. BLAS is scipy-openblas 0.3.34 and is not on the stepping path. OMP/OPENBLAS/MKL threads = 1 |

## 2. Per-thread limits (measured)

| resource | runtime session | audit session | planning value |
|---|---|---|---|
| CPU | 4 visible, affinity {0–3}, Xeon @ 2.80 GHz, CFS quota −1, `nr_throttled` 0 | the same | **4 vCPU, shared with the agent's own work** |
| memory | the process memory cgroup (v1, `/process_api/<id>/claude-code-bash`) has `limit_in_bytes` **14,343,688,192 B = 13.36 GiB**; parent and root are unlimited; host MemTotal 15.7 GiB; no swap; failcnt 0 | the same 13.36 GiB process limit | **13.36 GiB per thread**; going over it is an OOM kill |
| disk | 31.3 GB free (the per-session allowance; `df` Size is misleading) | 31.3 GB free | ~30 GB |
| pids | no `pids.max` file | the same | unknown |
| timeouts | Bash foreground 120 s default / 600 s max; background up to 2 h (tool documentation, **not tested**) | the same | keep any single foreground invocation well under 600 s |

Peak RSS per benchmark process was 38–85 MB on both sessions. That figure covers a single process; no case spawned children.

## 3. What was timed, and what was not

**Timed:**
- engine stepping (`alm.lenia.Lenia.step`, `alm_check.lenia.World`);
- `field.Batch.run` with its built-in per-step whole-world mass and periodic centroid;
- a morphology snapshot (`field.morph`) every 1 tu ("instr") on the runtime lane, and every 100 steps on the audit lane.

**Not timed. None of this is in any estimate below:**
- **Compression and output.** The runtime lane's `output_bytes` came from an npz written after the timer stopped, and it covers only the last sample's series. It measures size, not cost.
- **Checkpoint I/O.** No state checkpoints were written during timing.
- **Two-body tracking (not implemented).** `field.py` tracks one whole-world centroid. With S001 and S103 in the same world, that centroid is a joint centroid, so it gives neither separation, contact time nor per-body speed. Scoring first contact needs a per-component tracker, and that tracker's cost is unknown.

## 4. Measured timings

All runs use float64, poly/poly, Euler+clip, a periodic torus, mu = 0.155 and sigma = 0.020. Each case has 3 samples of about 2–3.4 s, with no truncation. ws/s means world-steps per second; values are medians with [min–max] where recorded.

| case | runtime session, lead harness | audit session, lead harness @418ac5d | audit session, audit harness |
|---|---|---|---|
| N256 R13 T10, engine, 1 world | 223.2 [214.3–240.2] | 342.2 [314.0–347.3] | 336.5 |
| N256, no measurements, W1 | — | — | 354.3 |
| N256, Batch W1 (mass+centroid each step) | 233.4 [209.4–242.9] | — | 316.1 (morph every 100 steps) |
| N256, Batch W1 + morph every 1 tu | 221.5 [219.3–241.2] | — | — |
| N256, Batch W2 | 232.6 (no morph) / 207.3 (morph) | — | 286.4 |
| N256, Batch W4 + morph every 1 tu | 213.6 [205.6–216.8] | 297.9 [279.1–341.7] | 311.0 (morph every 100 steps) |
| N256, 4 sequential engines | 254.0 [252.0–262.5] | — | 306.6 (no measurements) |
| N512 R13 T10 | engine 52.2 [51.4–53.5] (retry 52.2); instr 54.8 | — | 74.0 |
| N512 R26 T10 (2×2 block-resized) | engine 42.3 [42.2–42.3], **retry 49.8**; instr 49.9 | — | 73.7 |
| N256 R13 **T20** | engine 239.2, instr 227.5 (≈ 11.4 tu/s) | — | 334.1 (16.7 tu/s) |
| `alm_check` FFT, N256 | 279.2 [261.6–311.1] | — | 373.8 |
| `alm_check` **direct**, N256 (wrap) | **19.1** [19.0–19.4] | **21.0** [21.0–21.1] | **20.98** |
| 2 concurrent N256 engine processes, each | 231.0, 224.1 | 332.1, 331.6 | — |
| 4 concurrent N256 engine processes, each | 236–258 (aggregate ≈ 980) — *scope deviation, see §8* | not run | not run |

What the measurements show:
- **Batching gives no speedup.** Both sessions and both harnesses agree.
- **Two processes scale close to linearly** on both sessions.
- **Instrumentation overhead is about 0–11%.** On the runtime session, engine vs instr at W1 was −1%. On the audit session, the measured overhead was −11% at W1 and within noise at W4. The dependence on W is unresolved.
- **World size.** N512 costs 4.3–4.8× N256 per step.
- **R changes almost nothing.** At N512, R26 runs about as fast as R13, but the first R26 engine run was 18% slower than its retry (unresolved, §7).
- **Timestep.** T20 costs the same per step as T10, so it costs twice as much per tu.
- **Direct convolution.** It is 11.7× slower than the primary engine on the runtime session and 16–18× slower on the audit session. In absolute terms it runs at 19–21 ws/s.

## 5. Correctness smoke, and what each kind of agreement means

- **Same implementation, different code path.** `alm.lenia` and `field.Batch` are bitwise equal after 200 steps. `field.py` reuses `alm`'s kernel and growth, so this is not an independent check.
- **Independent implementation, same arithmetic.** The `alm_check` FFT path gives max |diff| 0.0 after 200 steps. `alm_check` was written independently, but its FFT path reduces to the same NumPy rfft arithmetic. The agreement checks the implementation, not the numerical route.
- **Different arithmetic.** The `alm_check` direct path (real-space `ndimage.correlate`) differs from FFT by 1.68e-14 after 20 steps on the shared input, and by 5.2e-13 after 200 steps for S001 alone (audit). It is identical for S103. Only this path is a genuinely different numerical route.
- **Cross-session.** The 200-step smoke state hash `59714babf013cdc5…` is identical on both sessions.
- **Existing tests.** The S103 exact fixed point passes on both sessions; the audit session also found the S103 fixed point exact at step 501. The runtime session ran `tests/test_lenia.py` plus the fixed-point test: 9 passed, 2 skipped. The audit session ran `tests/test_lane6_specimens.py` and `tests/test_lenia.py`: 15 passed, 2 skipped. The skipped tests are the same 2 on both sessions; they need `.refs/Lenia`, which was not cloned in either session. **The upstream-comparison tests were therefore not exercised.**

**The benchmark inputs are not isolated encounter controls.** The runtime-lane input puts raw S001 and S103 seed cells into one world at fixed positions. The S001 cells are seeds from the native rule, not settled at the coexistence rule. Nothing measured the S001 heading, nothing aimed the seeds at each other, and nothing censors interactions across the torus. The audit lane placed each seed alone in its own world, but only to time the engine. No run here tests whether either specimen survives alone at mu = 0.155, sigma = 0.020. Survival over a few hundred steps is not attractor evidence, and none of these states should be reused as control or encounter starting states.

## 6. Cross-session reconciliation

The audit left its cross-session comparison open because the runtime results were not pushed yet. Comparing the same lead harness on the two sessions:

| case | runtime | audit | audit / runtime |
|---|---|---|---|
| n256-w1-engine | 223.2 | 342.2 | 1.53 |
| n256-w4-instr | 213.6 | 297.9 | 1.39 |
| 2-process concurrent, each | 224–231 | 332 | 1.46 |
| check-direct | 19.1 | 21.0 | 1.10 |

The gaps exceed the audit's 10% noise threshold. The audit's rule is to treat such gaps as session variation unless hashes for an identical step count disagree. The 200-step smoke hashes are identical. No benchmark case ran the same adaptive step count on both sessions, so the per-case final hashes cannot be compared (as the audit noted).

**Conclusion:** this is host performance variation, not a correctness difference. The variation is not uniform. FFT cases ran about 1.4–1.5× faster on the audit host, while the direct path ran only 1.1× faster. The cause, perhaps cache, memory bandwidth or CPU features behind the same model string, is **unexplained**. Plan with the slower session's rates.

## 7. Cost estimates

Every number below is an extrapolation. It is not measured.

**Formula.** One run costs `t_run = H · T / r` seconds. Serial cost is the sum over runs. With P processes, wall time is roughly serial / P, rounded up to whole runs per process.

**Rates.** These are the slowest sample on the runtime session, instrumented where it was measured:
- N256/T10: r = 205
- T20: r = 206, with twice the steps
- N512/R13: r = 51
- N512/R26: r = 42
- `alm_check` FFT: r = 262
- direct N256/R13: r = 19.0

**What a case means.** One case is 1 encounter plus 2 matched isolated controls (S001 alone and S103 alone, with matched seeds, transforms and horizon).

**Horizons used for costing only.** The estimates use H = 200 tu per run and Hd = 20 tu per direct window. These are **costing examples only**. First-contact, follow-up and direct-check horizons are scientific design decisions that this calibration does not make. Costs scale linearly in H per run.

**Excluded.** Setup takes under 0.35 s per run and is ignored. Untimed compression, checkpoint I/O and two-body tracking (§3) are excluded. Treat every figure as a lower bound until those are measured.

| workload | runs | steps/run | serial (s) | **P = 2 (conservative)** | P = 4 (conditional) |
|---|---|---|---|---|---|
| 6 pilot encounters + matched isolated controls | 18 | 2000 | 176 | 88 s | 49 s |
| contrast check, `alm_check` FFT, 2 contrasts | 6 | 2000 | 46 | 23 s | 15 s |
| contrast check, T20, 2 contrasts | 6 | 4000 | 117 | 58 s | 39 s |
| contrast check, R26 at N512, 2 contrasts | 6 | 2000 | 284 | 142 s | 95 s |
| larger world, N512/R13, 2 contrasts | 6 | 2000 | 235 | 118 s | 78 s |
| direct-convolution contact window, N256/R13, 2 contrasts | 6 | 200 | 63 | 32 s | 21 s |
| **feasible minimum** | 48 | | **≈ 920 s** | **≈ 8 min** | ≈ 4–5 min |
| optional: 7 offsets × 4 phases + 8 shared controls | 36 | 2000 | 351 | 176 s | 88 s |
| optional: direct path at N512/R26, 2 contrasts | 6 | 200 | ~1000 | ~8 min | ~4–6 min |

The optional direct case at N512/R26 is unmeasured. Its estimate assumes cost ∝ N²(2R+1)², which gives about 16× the N256/R13 cost, or about 1.2 ws/s.

**Formula for any horizon,** feasible minimum, serial: about 4.3 s per tu of H, plus 3.2 s per tu of Hd. Halve that for P = 2.

**P = 2 is conservative.** Near-linear two-process scaling was measured on both sessions. The mandate allowed up to two concurrent processes.

**P = 4 is conditional.** It rests on one 12 s, engine-only, N256 test on one session (§8). It holds only if all of the following are true:
- four-way scaling also holds for instrumented runs and for N512 jobs, where memory bandwidth is untested;
- the agent's own work does not compete for the 4 vCPU;
- the tracker and I/O, once added, do not change the balance.

Do not assume that more threads, or more project threads, add throughput linearly.

**Reserve.** Reserve **15–20%** of expedition effort for checking, reconciliation, one earned exhibit and a reproducible handoff. Compute for the feasible minimum takes minutes. The binding costs are agent analysis time, review, and building the missing tooling. This calibration measures none of them.

**Recommendations:**
- Run one world per process, with P = 2 by default. Use P = 4 only after a short instrumented four-process check at the real workload.
- Pin thread variables to 1.
- Record per-step mass and centroid, plus a snapshot every 1 tu.
- Checkpoint the full float64 state every 10 tu (512 KiB at N256, 2 MiB at N512), with a sha256 for each checkpoint. Commit hashes and selected compressed states only.
- Memory (≤ 85 MB per process against 13.36 GiB) and disk (~31 GB) are not binding.

## 8. Failures, deviations and open items carried forward

1. **Memory correction.** The PR #38 draft said this session had no cgroup memory limit. That was wrong: it read the parent cgroup. The lane's own `inventory.json` records the process cgroup limit as 14,343,688,192 B = **13.36 GiB**, the same as the audit session. The draft's "cgroup peak 0.93 GB" was also read from the parent cgroup.
2. **Scope deviation.** The mandate allowed up to two concurrent processes. The runtime lane also ran one four-process test (12 s, about 150 MB in total). Its result is kept in `results.jsonl`, tagged `concurrent4-*`. It is the only support for P = 4, and that is why P = 4 is conditional.
3. **Host variation.** The audit host ran 1.4–1.5× faster on FFT cases and 1.1× faster on the direct path, with identical smoke hashes. The cause is unexplained (§6).
4. **Unresolved variance.** The first n512-r26-engine run gave 42.3 ws/s and its one documented retry gave 49.8, an 18% swing. The audit measured R26 equal to R13 (73.7 vs 74.0).
5. **Skipped tests.** Two upstream-comparison tests in `tests/test_lenia.py` were skipped on both sessions because `.refs/Lenia` was absent.
6. **Instrumentation overhead depends on W.** The overhead measured at W1 vs W4 differs, and the cause is unresolved.
7. **Unmeasured.**
   - The cost of compression, checkpoint I/O and two-body tracking.
   - The direct path at R26/N512.
   - More than 2 concurrent processes for instrumented runs or at N512.
   - Tool-timeout behaviour.

## 9. Readiness assessment and remaining scientific decisions

**Ready:**
- The environment is characterised: 4 vCPU, 13.36 GiB, ~30 GB.
- Engine throughput is known to within about 1.5× across hosts.
- The engines agree bitwise. The direct-arithmetic check agrees to about 1e-14 over 20 steps.
- The compute for the feasible minimum is small, about 8 min at P = 2 under the example horizons.

**Not ready. These must be fixed before encounters can be scored:**
- A two-body or per-component tracker giving separation, contact time and per-body speed and heading. It does not exist yet.
- Settled, hashed starting states for S001 and S103 at the coexistence rule.
- Validated isolated controls for both specimens in the chosen world.
- A cost check of checkpoint and compression, which can be short.
- Cloning `.refs/Lenia` so the two skipped upstream tests run.

**Scientific decisions for Bobby (not made here):**
1. The first-contact horizon and the post-contact follow-up horizon. The 200 tu here is a costing example only.
2. The direct-check contact window. The 20 tu here is a costing example only.
3. The world size, and how runs are censored for re-encounters across the torus.
4. The settling procedure and acceptance test for the isolated controls.
5. The contact definition and the fixed moving/static classification rules.
6. Preregistration of the offset × phase grid before broad runs.
7. Which 2–4 contrasts get independent checks, and whether R26/N512 direct-path checking is needed.
