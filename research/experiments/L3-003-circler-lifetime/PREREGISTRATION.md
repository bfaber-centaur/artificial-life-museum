# L3-003: Is the S102 circler a long transient? Independent replication (pre-registration)

Lane 3 (Numerical Red Team), Night 1, replication of Lane 6's L6-007 follow-up (PR #27).
Written and committed **before any run of this experiment**. The commit that adds this file is
the pre-registration timestamp. Later changes go under "Amendments" with a reason; the original
text is not edited.

## What is being replicated

Lane 6 (PR #27, `research/experiments/L6-007-attractor-geography/`, `followup_circler.py`,
`circler-lifetimes.csv`) reports, at the registered coexistence rule (μ 0.155, σ 0.020, R 13,
T 10, N 128, poly/poly, Euler + clip, torus):

- L6-a: the unperturbed S102 seed is a circler for a long time and then dies at **3979.9 tu**
  (step 39799), the same step in two engines.
- L6-b: with their seeded noise recipe, 2 of 6 ε = 0.01 starts die (933.7 and 977.6 tu) and
  2 of 6 ε = 0.03 starts die (1291.0 and 988.8 tu) within 5000 tu; the other 8 are alive at
  5000 tu with mass ≈ 0.522.
- Lane 6 used bilinear seed resizing for R ≠ 13. L3-002 (C047) showed bilinear resizing kills
  S102 at R 26 and 39 within 10 tu, while block, nearest and cubic seeds survive 1000 tu. So no
  lifetime at R 26 has been measured from a seed that survives the resize.

## Questions

- **Q1** Does `alm_check` reproduce L6-a: the unperturbed death step at R 13, T 10?
- **Q2** Does `alm_check` reproduce L6-b: the fate and death time of each of the 12 noisy starts?
- **Q3** Is the finite lifetime a property of the refined system? Lifetime at R 26 and R 39 from
  block, nearest and cubic seeds (no bilinear; bilinear is run only as a known-death control).
- **Q4** Does the R 13 lifetime depend on the timestep? T 20 and T 40.
- **Q5** At R 26, do the same noise amplitudes kill some starts (L6-b at refined resolution)?

This test does not search rules, change μ or σ, or study other specimens.

## Fixed inputs

| Item | Value |
| --- | --- |
| Engine | `alm_check` (Lane 3 independent stepper), FFT path, float64, periodic torus |
| Rule | μ 0.155, σ 0.020, β [1], poly core, poly growth, Euler + hard clip [0, 1] |
| Seed | `research/specimens/S102-circler/initial-cells-u8.csv`, level/255, centred placement |
| World | N = 128·(R/13) (same size in R units as Lane 6) |
| Mass | ΣA / R² after each step |
| Death | first step s ≥ 1 with mass < 0.01; death time = s / T (Lane 6's definition) |

Seed resizing for R = 13k: **block** = `np.kron(cells, ones((k, k)))`; **nearest**, **bilinear**,
**cubic** = `clip(scipy.ndimage.zoom(cells, k, order=0 / 1 / 3), 0, 1)` (as in L3-002's
`s102_resize_check.py`). If the nearest seed is bitwise equal to the block seed it is reported as
identical and not run twice.

Noise (Lane 6's recipe, copied from `followup_circler.py` / `run.py`): base = placed seed;
support = `ndimage.binary_dilation(base > 0, iterations=3·R//13)`; for amplitude index i_e
(ε 0.01 → 0, ε 0.03 → 1) and replicate k = 0..5,
ξ = `np.random.default_rng(1000·1 + 100·i_e + k).uniform(-1, 1, base.shape)`, start =
`clip(base + ε·ξ·support, 0, 1)`. At R 26 the same formula is used on the 256 × 256 block-seeded
world (the draws are therefore not the same numbers as at R 13; only the recipe is the same).

## Conditions (fixed now)

| ID | R | T | Seed | Starts | Horizon (tu) | Question |
| --- | --- | --- | --- | --- | --- | --- |
| A0 | 13 | 10 | native | unperturbed | 5000 | Q1 |
| A1 | 13 | 10 | native | 12 noisy (ε 0.01, 0.03 × 6) | 5000 | Q2 |
| B26-block, B26-nearest, B26-cubic | 26 | 10 | resized | unperturbed | 8000 | Q3 |
| B39-block, B39-nearest, B39-cubic | 39 | 10 | resized | unperturbed | 8000 | Q3 |
| B26-bilinear, B39-bilinear | 26, 39 | 10 | bilinear | unperturbed | 100 | control (expected death < 10 tu) |
| D20, D40 | 13 | 20, 40 | native | unperturbed | 8000 | Q4 |
| E26 | 26 | 10 | block | 12 noisy | 5000 | Q5 |

8000 tu is twice the reported R 13 lifetime. No run is extended beyond its horizon in this
experiment; any longer run is a separate, labelled follow-up.

## Pass / label rules (fixed now)

- **Q1** REPLICATED-EXACT if the A0 death step equals 39799; REPLICATED if it is within ±10 steps
  (1 tu); otherwise NOT REPLICATED (death step reported).
- **Q2** per start: fate (dead / alive at 5000 tu) must match Lane 6's CSV, and a death time must be
  within ±1 tu. Q2 is REPLICATED if 12/12 match, PARTIAL if the fates match but some death times do
  not, otherwise NOT REPLICATED (with the count). Alive starts are compared on mean mass over the
  last 100 tu (Lane 6: `mass_last_100tu`), reported, not scored.
- **Q3** each seed is labelled DIES at t or ALIVE at 8000 tu. Interpretation, fixed now:
  - all six non-bilinear refined runs die → "finite lifetime persists under refinement"; the
    lifetimes are reported per R and the R 13 value is labelled resolution-dependent if any differs
    from 3979.9 tu by more than 10%.
  - all six alive at 8000 tu → "the R 13 lifetime is a finite-resolution feature" (the refined
    circler outlives the R 13 one by at least 2×; this does **not** show it is an attractor).
  - anything else → reported per seed as MIXED, no summary label.
- **Q4** D20 and D40 labelled DIES at t or ALIVE at 8000 tu. If both die, the Richardson estimate
  2·t(T40) − t(T20) is reported as indicative only (lifetime need not be smooth in Δt).
- **Q5** count of the 12 E26 starts dead by 5000 tu, with death times. Compared descriptively with
  A1; no pass criterion (different noise draws).

## Expected outcomes (written down so they can be wrong)

- Q1: exact match (Night 0 showed `alm_check` and Lane 2's engine agree bitwise over 20k steps for
  S001, and Lane 6 reports two engines agreeing).
- Q2: 12/12, possibly with small death-time differences if the engines differ in FFT summation
  order and the transient amplifies them.
- Q3: no prediction. A long transient caused by slow drift on the R 13 lattice would predict a
  different lifetime (or survival) at R 26/39.
- Q4: no prediction.
- Q5: some deaths, by analogy with A1.

## Outputs

- `research/traces/lane3/L3-003/lifetimes.csv`: one row per run (condition, ε, rep, death step,
  death tu, mass over the last 100 tu, steps run).
- `research/traces/lane3/L3-003/<condition>.npz`: per-tu mass and centroid series.
- `research/experiments/L3-003-circler-lifetime/README.md`: the answers to Q1–Q5 and a figure.
- Proposed claims for the coordinator and archivist; nothing is written to `research/claims.md`
  by this lane.

## Run IDs and reproduction

Run ID `L3-003-<condition>[-e<ε>-r<k>]`. The runner `src/alm_check/lifetime.py` is added in a
later commit, before any run. Command: `.venv/bin/python -m alm_check.lifetime`.

## Amendments

### Amendment 1 (2026-10-08, written while the main runs were in progress, before any result was read)

Reason: Lane 7's HR-009 (PR #30) shows the circler is chaotic at R 13: copies differing by 1e-14 to
1e-10 on the support die anywhere from 292 tu to more than 5000 tu. A single death step is then a
property of one floating-point trajectory, not of the rule. The coordinator asked that this
replication target the lifetime distribution, i.e. the transient-not-attractor conclusion.

Changes (additions only; Q1 to Q5 and their rules stand and are still reported):

- Q1 and Q2 are reinterpreted. A match shows that `alm_check` performs the same arithmetic as Lane
  6's engine; a mismatch is **not** evidence against Lane 6's conclusion. Neither outcome bears on
  whether the circler is an attractor.
- Q3 to Q5 single runs are read as one draw each from a lifetime distribution, not as "the" lifetime
  at that setting. The Q3 "differs by more than 10%" rule is dropped as uninformative.
- **Q6 (new, primary for the conclusion).** Lifetime distribution under δ = 1e-12 perturbations:
  start = clip(base + δ·ξ·support, 0, 1), ξ = `np.random.default_rng(7000 + 100·i_R + k)`
  `.uniform(-1, 1, base.shape)`, support as above (dilation 3·R//13). Independent seeds from
  Lane 6 (1000+) and Lane 7 (9000+).
  - Q6-13: R 13, T 10, native seed, k = 0..23 (i_R = 0), horizon 5000 tu.
  - Q6-26: R 26, T 10, block seed, k = 0..11 (i_R = 1), horizon 8000 tu.
  - Reported: number dead by the horizon, sorted death times, median (if more than half die).
  - Label for each R: **TRANSIENT** if at least one copy dies within the horizon (an attractor
    basin containing the seed would not lose copies to 1e-12 noise); **NO DEATH OBSERVED** if all
    copies are alive at the horizon (this does not show an attractor).
  - Q6-13 is compared with Lane 7's E1 δ = 1e-12 row (5 of 8 dead by 5000 tu, 292–3556 tu)
    descriptively (counts and ranges), no test.
- Q6 runs are written to the same `lifetimes.csv` schema in `research/traces/lane3/L3-003/q6.csv`,
  by `.venv/bin/python -m alm_check.lifetime --q6`, added to the runner before Q6 is run.
