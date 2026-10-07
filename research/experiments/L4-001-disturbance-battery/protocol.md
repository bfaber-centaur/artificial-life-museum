# L4-001: S001 disturbance battery (pre-registered protocol)

Lane 4 (Disturbance Laboratory), Night 0. Written and committed **before any perturbation run was
executed**. The git commit that adds this file is the pre-registration timestamp. Later changes to
definitions below are appended under "Amendments" with a reason and never rewrite the original
text, so any threshold change made after seeing results stays visible.

## Question

For specimen S001 (Orbium, LeniaND rule), at what strength does each of four standardized
disturbances stop being survivable, and is that transition sharp (phase-independent) or smeared
by the creature's internal/lattice phase?

## Fixed inputs

| Item | Value |
| --- | --- |
| Specimen | S001 Orbium `O2u`, cells from `research/specimens/S001-orbium/initial-cells-u8.csv`, centred placement |
| Rule | R = 13, T = 10, μ = 0.15, σ = 0.015, β = [1], polynomial core and polynomial growth, Euler + clip [0, 1], float64 |
| World | N × N periodic torus, N = 128 (primary) |
| Randomness | none; every run is deterministic, so there is no seed |
| Warm-up | the unperturbed creature is stepped from the catalog state to the intervention step t0 |
| Intervention steps t0 | 1000, 1001, 1002, 1003, 1004 (five **phase replicates** spanning one 4.32-step lattice wobble period) |
| Horizon | H = 2000 steps (200 time units) after the intervention |
| Sampling | every step for the centroid; every 10 steps for the recorded trace |

The intervention is applied to the state *after* step t0 and before step t0 + 1, as an
instantaneous edit of the array. Nothing else about the rule changes.

### Engines (execution paths)

- `ref`: Lane 1's reference stepper `research/specimens/S001-orbium/reconstruct.py` (`make_kernel_fft`,
  `step`), already cross-checked against upstream `Automaton` to max|ΔA| ≈ 1e−6 at 1000 steps.
  The coarse sweep and bisection run on this engine because it exists now.
- `alm`: Lane 2's simulator in `src/alm`, once merged. The bracketing strengths of every transition
  are re-run on it. A transition is only proposed as "reproduced in two execution paths" if both
  engines give the same classification at both bracket ends.

## Creature frame at t0

Measured on the pre-intervention state at t0:

- **centroid c**: periodic (circular-mean) centroid, as in `reconstruct.py`.
- **heading ĥ**: unit vector of the wrapped centroid displacement from t0 − 10 to t0.
- **port normal n̂** = (−ĥ_y, ĥ_x) in array (x = column, y = row, y downward) coordinates.

All geometric interventions are placed in this frame, so they hit the same body part regardless of
where on the torus the creature is.

## Intervention battery

Each intervention has one strength parameter s. Every run also logs the *achieved* mass change
ΔM/M₀ (M₀ = mass just before the edit), so strength can be compared across interventions in mass
units and so "did the intervention remove more mass than intended?" is answerable for every run.

| ID | Name | Edit (applied to array A) | Strength s | Coarse grid |
| --- | --- | --- | --- | --- |
| I001 | Mass attenuation | A ← (1 − s)·A | fraction of mass removed | 0.00, 0.05, …, 0.95 (20) |
| I002 | Central deletion | A ← 0 on cells with periodic distance to c < s·R | disc radius in units of R | 0.00, 0.05, …, 1.00 (21) |
| I003 | Frontal addition | A ← clip(A + s·exp(−d²/(2w²)), 0, 1), d = periodic distance to c + 1.0·R·ĥ, w = 0.25 R | peak amplitude | 0.00, 0.05, …, 1.00 (21) |
| I004 | Port-side injury | zero the cells with the largest lateral coordinate (x − c)·n̂ until the removed mass first reaches s·M₀ | fraction of mass removed from the port side | 0.00, 0.05, …, 0.95 (20) |

Notes fixed in advance:

- I002 and I004 act on whole cells, so their achieved strength is quantized. I002 is bisected on
  the radius and the result is reported both as radius and as removed mass fraction; a transition
  that falls between two pixel shells is reported as such, not interpolated.
- I004's cut is a straight line parallel to ĥ (all cells with lateral coordinate ≥ ℓ* are zeroed,
  with ℓ* the largest threshold that reaches s·M₀). Ties at ℓ* are all removed.
- s = 0 is included in every grid as the unperturbed control, and must classify as RECOVERED. If it
  does not, the classification is wrong and the sweep stops.

## Outcome definition (primary)

Reference values are Lane 1's S001 dossier baseline (128², steps 1000–4000), fixed before this
experiment: mass m̄ = 0.4358 (ΣA/R²), gyradius ḡ = 0.4376 R, speed v̄ = 0.4796 R per time unit.

Measured over the **evaluation window**: the last 500 steps of the horizon, (t0 + 1500, t0 + 2000].

- **mass(t)** = ΣA/R².
- **gyradius(t)** = RMS distance of mass from the periodic centroid, in units of R.
- **window speed** = mean over the five consecutive 100-step blocks of the window of |net wrapped
  centroid displacement over the block| / 10 time units, in R per time unit. (Per-step wrapped
  displacements are summed, so the step-1 centroid sampling never aliases.)

Classes, checked in this order:

1. **DIED**: mass < 0.01 at the end of the horizon.
2. **EXPLODED**: mass > 2·m̄ = 0.8716 at the end of the horizon.
3. **RECOVERED**: at every 10-step sample of the window, 0.8·m̄ ≤ mass ≤ 1.2·m̄ and
   0.8·ḡ ≤ gyradius ≤ 1.2·ḡ, **and** 0.8·v̄ ≤ window speed ≤ 1.2·v̄.
   (Bounded mass, one compact localized body, resumed gliding at the baseline speed.)
4. **TRANSFORMED**: anything else (alive and bounded but not baseline-like: a stationary blob, a
   slower/faster glider, two bodies, an oscillating mess). The metrics are recorded so these can be
   inspected and, if repeatable, handed to Lane 6.

**Survival** for the headline transition means RECOVERED. DIED/EXPLODED/TRANSFORMED are all
non-recovery and are reported separately.

### Secondary measures (recorded, not used for the primary class)

- **recovery time**: first step after t0 from which mass and gyradius stay inside their ±20 % bands
  through the end of the horizon (10-step samples), in time units.
- **template correlation**: Pearson correlation between the final state and the unperturbed control
  run's state at the same step, each recentred on its centroid and rotated so its heading is +x
  (bilinear). Reported to address "is recovery merely a new blob?".
- **band sensitivity**: the class each run would get with ±10 % and ±30 % bands instead of ±20 %.
  The headline transition is reported for all three, so the conclusion's dependence on the chosen
  threshold is visible.
- **delayed outcome**: the two runs bracketing each transition (phase t0 = 1000) are extended to
  5000 post-intervention steps, and any class change after step 2000 is reported.

## Procedure

1. **Control**: s = 0 for every intervention and phase. Must be RECOVERED (sanity gate).
2. **Coarse sweep**: every grid strength × 5 phase replicates on `ref`, N = 128. One CSV row per run.
3. **Transition location**: for each intervention and phase replicate, let s_fail be the smallest
   coarse strength that is not RECOVERED and s_ok the coarse strength just below it. If no coarse
   strength fails, the intervention has no transition in range and that is the result.
4. **Refinement**: bisect each (intervention, phase) bracket [s_ok, s_fail] to a width of 1/256
   (I002 bisects radius in R units; stop early if the disc's pixel set no longer changes).
   The transition estimate s*_p is the bracket midpoint.
5. **Non-monotonicity**: any coarse strength above s_fail that is RECOVERED is listed explicitly.
   It is not discarded, and it makes the transition "non-monotone" in the report.
6. **Sharpness verdict (fixed now)**: a transition is called **sharp** if all five phase replicates'
   s*_p lie within one coarse step (0.05) of each other and the coarse sweep is monotone; otherwise
   **phase-smeared** or **non-monotone**.
7. **Robustness re-runs** at the bracket ends (phase t0 = 1000 at least):
   - second execution path (`alm` engine) when available;
   - world size N = 192 (same R, same creature: tests that the result is not tied to the torus size).
8. **States saved**: for each intervention, the runs at the coarse strengths on either side of the
   transition (phase t0 = 1000) save `before` (t0, pre-edit), `during` (t0, post-edit) and `after`
   (t0 + H) states as compressed `.npz`, plus a 10-step trace CSV.

## Run IDs and reproduction

Run ID format: `L4-001-<intervention>-s<strength, 4 decimals>-t<t0>-N<size>-<engine>`, e.g.
`L4-001-I002-s0.4000-t1002-N128-ref`. Run IDs are deterministic, so the ID alone reproduces the run.

The runner script and exact commands are added in later commits next to this file; this protocol
commit deliberately contains no code and no results.

## Amendments

### A1 (2026-10-07, after the N = 128 coarse sweep and bisection, before any T/R run)

**Added check, nothing in the original definitions changes.** Lane 3 (PR #8) reports that S001's
speed depends on T (0.479 R/time at T = 10, about 0.572 as dt → 0) and that at R = 13 the heading
snaps to grid directions. A transition that is a discretisation artifact would move under a modest
change of either. So the full battery (all four interventions, the same coarse grids, then
bisection) is re-run at phase t0 = 100 time units under two extra discretisations:

- **T20**: R = 13, T = 20 (dt halved).
- **R26**: R = 26, T = 10, the catalog cells zoomed 2× nearest-neighbour (as upstream's GUI zoom
  does), world N = 256 so the creature has the same size relative to the torus.

Everything is kept in time units and R units: t0 = 100 time units, horizon 200, evaluation window
the last 50, speed blocks of 10 time units, geometry in R. Because the baseline itself changes with
T and R, the ±20 % bands for these two conditions are centred on that condition's own s = 0 control
(means over its window) instead of Lane 1's T = 10, R = 13 numbers. No pass/fail threshold is set
for the shift of s*: the result is reported as the measured s* per intervention under each
discretisation next to the T10/R13 value, and a shift larger than the T10/R13 phase spread is
called discretisation-sensitive.
