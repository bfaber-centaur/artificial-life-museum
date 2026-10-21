# L6-010: is the Orbium/ring basin boundary smooth or finely structured? (pre-registered protocol)

Lane 6, Night 1, 2026-10-08. **Written and committed before any L6-010 run.** Later changes go
under "Amendments". This is Q3 of `/mnt/project-files/lane6/next-questions.md`, with a
twin-perturbation check added at Lane 7's request (raised via the coordinator), so that the
boundary map is not specific to one machine's rounding.

## Background

In L6-007 Part B (step 0.05, 2000 tu), the Orbium → ring blend at the coexistence rule reads
G G G D **S** D D D D D D F S S S S S S S S S. That includes an isolated static point at λ 0.20
between dead zones. On this path every run kept its class from 250 to 2000 tu. No circler is
involved, Orbium and S103 are attractors (L6-007 Part A), and death is final. So unlike the
circler end, a class here could be a real basin label. HR-009 showed that the circler is chaotic,
but nobody has checked whether the transients on *this* path are rounding-sensitive.

## Competing explanations

- **(a) Smooth.** Each boundary between classes is a single crossing, and refining λ only places
  it more precisely.
- **(b) Fine structure.** The classes keep alternating as λ is refined, as near a fractal basin
  boundary, and the λ 0.20 island is one visible piece of that.

## Fixed inputs

Rule μ 0.155, σ 0.020, R 13, T 10, β [1], poly/poly, Euler + clip, float64, 128² torus. Engine
`L6-field/field.py` through L6-007's `run_batch` and classifier (the same code path as Part B).
Blend A₀(λ) = (1 − λ)·S001 + λ·S103, both centred, built exactly as in L6-007's `paths()`.
Horizon **1000 tu**, with classes at 250, 500 and 1000 tu. The horizon is halved from Part B
because no run on this path changed class after 250 tu. Any class change found between 500 and
1000 tu here is reported as a horizon warning.

Runs:

1. **Fine scan.** λ = 0.100, 0.101, …, 0.250 (151 points) and λ = 0.500, 0.501, …, 0.600
   (101 points).
2. **Twins.** The same 252 starts plus δ·ξ, with δ = 1e−12 and ξ uniform in [−1, 1] on the blend's
   support (A₀ > 0 dilated by 3 cells), using rng `default_rng(10000 + i)` for point i. 252 runs.
3. **Second slice.** The blend plus 1% noise (ε = 0.01, same support, rng `default_rng(20000 + i)`)
   at λ step 0.005 over the same two brackets (31 + 21 = 52 runs). This checks that the island is
   not an artefact of one straight-line path.

In total 556 worlds. For every STATIC final, record whether it equals the S103 state bitwise up to
a periodic shift.

## Definitions

- A point is **rounding-sensitive** if its twin's 1000 tu class differs from its own.
- **Changes** in a bracket: the number of adjacent λ pairs whose 1000 tu classes differ.

## Predictions and decision rules

- **R (rounding).** I expect rounding-sensitive points to be ≤ 5% of each bracket, and only within
  0.002 of a class change. If a bracket has > 5% rounding-sensitive points, its boundary map is
  declared **machine-specific**. Its change counts are then reported twice, over all points and over
  rounding-robust points only (where the original and its twin agree), and (a)/(b) is judged on the
  robust points only.
- **(a) supported** in a bracket if, at step 0.001, the classes change at most 2 more times than
  they do in the 0.005 subsample of the same bracket (refinement adds no new alternations beyond
  placing each boundary).
- **(b) supported** in a bracket if the 0.001 scan has at least 3 more changes than its 0.005
  subsample, or contains a class run of length 1 (a single-point island) that its twin confirms.
- **Island.** The λ 0.20 static island is **path-specific** if no second-slice point in
  [0.15, 0.25] is STATIC, and **robust** if at least 2 adjacent second-slice points there are
  STATIC.

Deterministic runs, so no p-values. The thresholds above are the decision rules.

## Expected (stated now)

I expect (b) in the [0.10, 0.25] bracket, given the island, and (a) in [0.50, 0.60]. I also expect
rounding sensitivity to be rare, because the attractors on this path are not chaotic.

## Outputs

`scan.csv` (one row per world: slice, λ, classes, mass, whether it is S103 up to shift),
`finals.npz`, written by `run.py`. `README.md` reports the verdicts.

## Amendments

_None._
