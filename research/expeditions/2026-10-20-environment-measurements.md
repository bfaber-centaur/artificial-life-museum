# ALM coordinator prompt: environment and runtime measurements

Prepared 2026-10-20 (America/Los_Angeles). This is a measurement mandate, not the full Coexistence-Reef launch packet. It authorizes work only when Bobby gives it to the Claude coordinator.

## Mission and authority

You coordinate Artificial-Life Museum in `bfaber-centaur/artificial-life-museum`. Establish what the actual Claude project-thread environments can do, and return a measured execution plan for the Coexistence-Reef Safari.

You may start at most two substantive measurement threads, install the repository's existing dependencies, add small calibration scripts, run bounded benchmarks and existing relevant tests, and commit results on dedicated branches. Do not start encounters, parameter searches, new biological experiments, museum work, claim promotions, paid compute, or merges. Bobby merges. Do not treat the merged safari directive as permission to launch science.

Read README.md, research/charter.md, research/roadmap.md, research/reports/synthesis-2026-10-08.md, the integration notes in L6-009 and L6-010, and research/expeditions/2026-10-20-coexistence-reef.md. Pin and report the current origin/main SHA; all measurement threads must use the same base. Preserve prior results.

No fixed cross-project inference allocation. The previous 15% allocation is superseded. Aim to finish calibration in 20 minutes of elapsed execution, with a 30-minute stop-and-report limit after starting the first measurement thread. This is a calibration cap, not the full expedition deadline.

## Ownership and handoffs

1. Runtime lead, branch `reef/measure-runtime`: environment inventory, benchmark harness, reference timing matrix and raw results. Own `research/experiments/REEF-M0-runtime/`.
2. Independent auditor, branch `reef/measure-audit`: independently inspect its own session's resource limits and engine provenance; review the lead's harness, then rerun two representative cases from the lead's exact committed harness SHA. Own `research/experiments/REEF-M0-audit/`. Fetch the lead's branch without overwriting either lane's output.

The coordinator owns the synthesis on `reef/measure-summary`, imports only reviewed commits, records exact dependencies and opens a reviewable PR. Routine choices, one documented retry, shortening a slow sample, or stopping a broken case need no escalation. Escalate resource/access blockers and scientific ambiguities. Once done, stop; do not expand the organization.

Threads are separate cloud sessions; any subprocesses or subagents inside one thread must be budgeted against that thread's effective resources. Do not assume aggregate throughput scales linearly with thread count.

## Measure the environment

Record UTC timestamp, safe session identifier if available, repository and harness SHAs, OS, architecture, Python, NumPy and SciPy versions, FFT/BLAS backend and thread configuration.

Inspect CPU affinity, visible processors, effective cgroup CPU quota/cpuset, memory limit/current use, disk capacity/free space, and available throttling counters. Resolve the process's actual cgroup path; support v1/v2 or record unavailable. Host-visible cores and memory are not necessarily the container allowance. Use a small allowlist of runtime settings; never dump environment variables, credentials or tokens.

Record observed command/background timeout settings where accessible. Do not test the timeout by running a long job. Use bounded foreground invocations and checkpoint results after each case. No keep-alive loops or attempts to evade platform limits.

Anthropic documents approximate hosted-session ceilings of 4 vCPUs, 16 GB RAM and 30 GB disk. Treat these as expectations to check, not observed resources:
- https://code.claude.com/docs/en/cloud-environments
- https://code.claude.com/docs/en/claude-projects

## Measure ALM, with existing engines

Use existing `alm`, `L6-field/field.py` and `alm_check` APIs. Do not rewrite the simulator or silently change precision. Use float64, poly/poly, Euler plus clip, periodic boundaries, mu=.155 and sigma=.020, and separately placed S001-derived and S103 seeds. These are timing inputs, not an encounter.

Commit a small benchmark specification and harness before collecting timing results. Save exact input construction, float64 state hashes, commands and output hashes. Distinguish cold setup time, engine-only stepping, and stepping with the measurements/state output the expedition will need.

Suggested compact matrix:
- N=256, R=13, T=10: singleton, then batches of 2 and 4.
- N=512, R=13, T=10: world-size cost.
- N=512, R=26, T=10: spatial-refinement cost; explicit block resizing, same physical world extent as N256/R13.
- N=256, R=13, T=20: timestep cost per simulated time unit.
- `alm_check` FFT and direct convolution on the same N256/R13 input: short samples only for the direct path.

Use short warm-up and adaptive timed step counts targeting roughly 2–10 seconds per sample, three samples when affordable, and a 30-second per-case ceiling. Record any truncation. Avoid timing setup or imports as steady-state stepping. Benchmark throughput of up to two concurrent processes inside one thread only if it resolves whether batching or multiprocessing is better; stay within measured CPU and memory limits and avoid nested BLAS oversubscription.

Record wall time, CPU time, process-tree peak memory where measurable, steps, worlds, world-steps/second, simulated tu/second/world, output bytes, and instrumentation overhead. Report sample range as well as median. Report memory measurement limitations rather than presenting parent RSS as the entire job.

Use only a small existing correctness smoke check (for example the S103 fixed point and short-step engine agreement). Short survival is not evidence of an attractor. At T40 the existing coexistence-rule Orbium baseline becomes static; do not retune sigma or reinterpret a timing run as a biological control. Distinguish `field.py`'s shared `alm` implementation, independently implemented `alm_check`, and the genuinely different direct-convolution arithmetic.

## Deliver and stop

Keep raw inventory JSON, timing CSV, logs, minimal scripts, a benchmark specification, input hashes and exact reproduction commands in the lane directories. Do not commit huge transient arrays or overwrite historical experiments.

Produce `research/reports/reef-environment-measurements-2026-10-20.md` with:
- measured per-thread limits and variability;
- table of actual timings and explicitly labelled extrapolations;
- recommended batch size, process count, instrumentation cadence and checkpoint interval;
- estimated elapsed costs for six pilot encounters plus matched isolated controls, two independently checked contrasts, larger-world and R/T checks, and the direct-convolution contact window;
- formulas and assumed horizons for every estimate; exclude any implication that all cases scale linearly;
- bottlenecks, missing information, and a feasible minimum versus an optional extension;
- 15–20% of proposed expedition effort reserved for checking, reconciliation, an earned exhibit and reproducible handoff.

The auditor must check at least one fast FFT case and the direct-path timing on its own session, verify the reported resource interpretation, and state whether differences are expected performance variation or unresolved correctness issues.

Return a concise coordinator summary with the pinned baseline, branch/PR links, measured capacity, recommended next workload and any question Bobby must answer. If setup or a benchmark fails, preserve the failure and report the smaller verified envelope. Do not start the scientific expedition.
