# H001 preregistration: is S001's mass wobble a lattice artifact?

Lane 7 (Hostile Reviewer), written 2026-10-07 **before** any H001 run. Committed alone so the
git history shows the predictions and thresholds predate the data.

## The claim under attack

S001 dossier, proposed claim 3: "S001's mass oscillation period is set by grid-crossing at its
heading (4.32 steps at 68.2°, 14.3 steps at 40.4°)".

## Problems with the existing evidence

1. **Only one independent heading was tested.** The 0° and 45° rows give headings 68.2° and 21.8°,
   which are mirror images across the lattice diagonal (90° − 68.2° = 21.8°, and vx and vy swap
   exactly). The square lattice is symmetric under that reflection, so the 45° row restates the 0°
   row. The claim rests on two headings, not three.
2. **The 23° explanation was found after seeing the number.** The 14.29-step period was explained
   as a beat 1/(1/2.11 − 1/2.48). With enough combinations of two crossing frequencies and
   aliasing, almost any period can be "explained". The prediction set must be fixed in advance and
   compared to a chance baseline.
3. **No resolution test.** The decisive way to separate a lattice artifact from a real internal
   oscillation is to change R, which the dossier itself names as the obvious next test.

## Competing hypotheses

- **H_L (lattice aliasing).** A smoothly translating profile sampled on a unit lattice has total
  mass Σ_n f(n − x(t)) = Σ_k F̂(k) e^{2πik·x(t)} (Poisson summation). With x(t) = v t, mass varies
  only at the lattice frequencies f_mn = m·vx + n·vy cycles/step (integer m, n, not both 0), folded
  into [0, 0.5] by per-step sampling. Its amplitude is set by the profile's spectrum at one cycle per
  cell, which should shrink as the creature is resolved by more cells.
- **H_I (intrinsic oscillation).** S001 has a real internal breathing mode with a fixed period in
  time units. With T fixed, its period in steps is R-independent and its amplitude does not vanish
  as R grows.

## Protocol (fixed)

Rule: S001 baseline (poly/poly, μ = 0.15, σ = 0.015, β = [1], T = 10, Euler, clip, float64,
periodic) using the semantics of `research/specimens/S001-orbium/reconstruct.py`.

- Initial state: catalog cells /255, zoomed by R/13 with bilinear interpolation (order 1), clipped
  to [0, 1], optionally rotated (bilinear, `reshape=True`), centred in an N × N torus with
  N = round(128·R/13) rounded up to an even number.
- Run 3000 steps. Analyse steps 1000–2999 (2000 samples, one per step).
- Velocity (vx, vy) in cells/step = mean per-step displacement of the periodic (circular-mean)
  centroid over the analysis window.
- Mass spectrum: total mass minus its mean, Hann window, `rfft`. The dominant peak is the largest
  bin above frequency 0 (excluding bin 0), refined by parabolic interpolation.
- Lattice lines: all f_mn with |m|, |n| ≤ 2, not both zero, folded into [0, 0.5].
- **Match tolerance: 0.002 cycles/step** (4 bins at this resolution).

## Experiments and predictions

**E1, resolution sweep.** Rotation 0, R ∈ {13, 20, 26, 39}.
- P1 (H_L): at every R, the dominant peak lies within tolerance of a lattice line.
- P2 (H_L): the dominant period in steps changes with R by more than 10% between R = 13 and
  R = 39. H_I predicts it stays within 10%.
- P3 (H_L): relative mass amplitude sd/mean decreases monotonically in R and falls by at least a
  factor of 2 from R = 13 to R = 39. H_I predicts roughly constant amplitude.

**E2, heading sweep.** R = 13, N = 128, initial rotation 0°, 3°, …, 45° (16 runs).
- P4 (H_L): in at least 14 of the 16 runs the dominant peak lies within tolerance of a lattice line.
- Chance baseline, computed per run: the fraction of [0, 0.5] covered by the tolerance windows
  around that run's lattice lines. The expected number of chance matches is the sum of those
  fractions; the result is reported next to it.

**Verdict rule.** H_L survives if P1, P2, P3 and P4 all hold. H_I survives if P2 and P3 both fail.
Any other pattern is reported as MIXED, with the failing predictions named. No threshold above may
be changed after running; any later analysis is labelled exploratory.

## Exploratory (no prediction)

E2 also records the final heading versus initial rotation. If the creature merely rotates, heading
should equal 68.2° − rotation (up to the sign convention). Any systematic deviation (for example
headings attracted to low-order rational slopes) would itself be a lattice effect and becomes a new
claim for review.
