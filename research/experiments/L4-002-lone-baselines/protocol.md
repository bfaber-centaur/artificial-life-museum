# L4-002: lone-Orbium baselines for the S101 pair-coupling test (pre-registered protocol)

Lane 4 (Disturbance Laboratory), Night 1, 2026-10-07. **Written and committed before any L4-002
run.** Later changes go under "Amendments".

## Purpose

Lane 6's L6-008 (`research/experiments/L6-008-pair-coupling/protocol.md`, branch
`claude/night0-field-tmbx06` @ `08f6ee5`) asks whether the bound pair S101 is coupled or is two
Orbia side by side. Its in-house baseline splits each edited pair into halves and runs each half
alone. L4-002 adds the second, external baseline: **the same edits applied to a lone S001
Orbium** at the same settings. It answers "what does this disturbance do to one Orbium on its own?"
without any splitting. It makes no coupling verdict; that belongs to L6-008.

## Fixed inputs (matched to L6-008)

| Item | Value |
| --- | --- |
| Specimen | S001, catalog cells centred (as in L4-001) |
| Rule | R 13, T 10, μ 0.15, σ 0.015, β [1], poly/poly, Euler + hard clip, float64 |
| World | 128² torus |
| Warm-up | 300 tu (3000 steps) |
| Phase replicates | edit after step t0 = 3000, 3001, 3002, 3003, 3004 |
| Horizon | 300 tu (3000 steps) after the edit; outcome from the last 100 tu (1000 steps) |
| Engine | `ref` (Lane 1 stepper) via `research/experiments/L4-001-disturbance-battery/run.py` |
| Disturbances | `src/alm/disturb.py` as merged in PR #5 (the L4-001 definitions; frame from the circular-mean centroid, heading from the 10-step displacement), measured on the lone Orbium |

| ID | Strengths s (same grids as L6-008) |
| --- | --- |
| none | 0 (control) |
| I001 uniform attenuation | 0.02, 0.04, …, 0.20 (10) |
| I004 port injury | 0.05, 0.10, …, 0.60 (12) |
| I003 frontal addition, 1 R ahead, width 0.25 R | 0.1, 0.2, …, 1.0 (10) |

That makes 33 conditions × 5 phases = 165 runs.

## Outcomes

Each run gets both labels:

1. **L6-008 units, n ∈ {0, 1, other}**, using L6-008's definitions so the numbers drop into its
   independence table. n = 0 if mass < 0.01 at the end. n = 1 if it is a GLIDER (net centroid
   speed over the last 100 tu > 0.2 R/tu) and its mean mass over the last 100 tu is within 5 % of
   0.4358. Anything else is "other".
2. **L4-001 class** (RECOVERED / DIED / EXPLODED / TRANSFORMED), with L4-001's ±20 % bands, applied
   to the last 100 tu instead of L4-001's last 50 tu.

## Mass-unit caveat (stated now)

On the pair, I001 removes the fraction s from both partners, so it maps one to one onto a lone
Orbium at the same s. I004's s is a fraction of the *pair's* mass taken from the port side. That
equals about 2s of the port partner's own mass while 2s ≤ 1. So a pair edited at I004 s
corresponds to a lone Orbium at roughly 2s, and the grid covers that for pair s ≤ 0.30. The
report gives both the same-s and the 2s comparisons. I003 is placed relative to the pair's
centroid, which is not where either partner's front is, so lone I003 is only a reference for "a
blob of this size hitting one Orbium head-on", not a matched control.

## Expectations (stated now)

From L4-001 (t0 = 1000, 2000-step horizon): lone I001 survives at s ≤ 0.10 and dies at s ≥ 0.105.
Lone I004 survives at s ≤ 0.08 and dies at s ≥ 0.09. Lone I003 survives at peak ≤ 0.30 and dies at
≥ 0.32. I expect the same edges at t0 = 3000, within one 0.02 / 0.05 / 0.1 grid step. A change
would mean the edge depends on how long the creature has been running, which is itself worth
reporting.

## Outputs

`run_baselines.py` writes `lone-baselines.csv` (one row per run, with run ID, achieved ΔM/M₀,
final mass, last-100-tu mass mean, net speed, n, and L4-001 class). `README.md` reports the
per-strength table and the edges. The PR stays unmerged for review.

## Amendments

_None._
