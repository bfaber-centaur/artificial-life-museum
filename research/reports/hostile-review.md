# Hostile review log (Lane 7)

Lane 7 attacks claims and protocols from the other lanes and turns each criticism into an
experiment or an executable test. Entries are appended, never rewritten. Verdicts use the
`research/claims.md` status vocabulary.

---

## HR-001: S001 mass wobble vs heading (Lane 1, S001 dossier proposed claim 3)

**Target claim.** "S001's mass oscillation period is set by grid-crossing at its heading (4.32 steps
at 68.2°, 14.3 steps at 40.4°)."

**Verdict: the wobble is a lattice artifact (supported, with one preregistered prediction failed as
written). Recommended status: NUMERICALLY_FRAGILE for "S001 oscillates", OBSERVED for the
lattice-aliasing account.** In the process I found a larger artifact: on the R = 13 lattice S001's
**heading is pinned** to a small set of directions (HR-001b below).

### Objections to the original evidence

1. **Two headings, not three.** The 0° and 45° start rotations gave headings 68.2° and 21.8°,
   which are mirror images across the lattice diagonal (vx and vy swap exactly). The square lattice
   is symmetric under that reflection, so the 45° row repeats the 0° row.
2. **Post-hoc fit.** The 14.29-step period at 40.4° was explained as a beat between the two
   crossing frequencies after the number was seen. With aliasing and integer combinations, many
   periods can be "explained". Prediction set and tolerance needed fixing in advance, against a
   chance baseline.
3. **No resolution test.** Changing R is what separates a sampling artifact from a real internal
   mode.

### Experiment H001 (preregistered)

Protocol, predictions and thresholds:
[`../experiments/H001-lattice-wobble/PREREGISTRATION.md`](../experiments/H001-lattice-wobble/PREREGISTRATION.md),
committed in `5f0326f` before any run. Code: `h001.py`. Data: `e1.csv`, `e2.csv` (same directory).

The hypothesis under test, made precise: by Poisson summation, a profile translating at (vx, vy)
cells/step and sampled on the unit lattice can change its total mass only at frequencies
f = m·vx + n·vy (integer m, n), folded into [0, 0.5] by per-step sampling, with an amplitude that
shrinks as the profile is resolved by more cells.

**E1, resolution sweep** (rotation 0, the same creature zoomed to each R, N ≈ 128·R/13, steps
1000–2999):

| R | N | mass ΣA/R² | mass sd/mean | dominant period (steps) | nearest lattice line (m, n) | error (cycles/step) |
| --- | --- | --- | --- | --- | --- | --- |
| 13 | 128 | 0.43580 | 2.56e−3 | 4.320 | (−1, 0) | 2e−6 |
| 20 | 198 | 0.43589 | 1.04e−3 | 7.125 | (−1, −2) | 4e−5 |
| 26 | 256 | 0.43589 | 5.31e−4 | 5.687 | (−2, 1) | 3e−4 |
| 39 | 384 | 0.43589 | 1.27e−4 | 4.029 | (−1, 0) | 4e−4 |

**E2, heading sweep** (R = 13, start rotations 0°, 3°, …, 45°): the dominant peak sits on a lattice
line within 0.002 cycles/step in **14 of 16 runs**. Chance expectation, from the fraction of the
band covered by each run's tolerance windows, is 1.45 matches; P(≥ 14 by chance) = 2.5e−13
(Poisson-binomial). Misses: rotation 21° (heading 45.4°, near the diagonal where the slow (1, −1)
line has period ~150 steps) and rotation 33° (error 0.00226, just outside tolerance; its mirror
rotation 6° matched).

| Prediction | Result |
| --- | --- |
| P1: dominant peak on a lattice line at every R | **holds** (4/4) |
| P2: period at R = 39 differs from R = 13 by > 10% | **fails as written** (4.32 vs 4.03 steps, −6.7%) |
| P3: sd/mean falls monotonically, ≥ 2× from R = 13 to 39 | **holds** (20× drop, monotone) |
| P4: ≥ 14/16 heading-sweep peaks on a lattice line | **holds** (14/16; chance 1.45) |

By the preregistered rule this is **MIXED**, failing P2. I am reporting that as written. P2 was a
badly designed test: it compared only the endpoints, and at R = 39 the lattice line that happens to
dominate is again (−1, 0), whose period scales with 1/vx and lands near 4.3 by coincidence. The
intermediate resolutions (7.13 and 5.69 steps) are not compatible with a fixed internal period, and
the competing hypothesis (intrinsic oscillation) needed both P2 and P3 to fail; P3 holds by a
factor of 10 margin. The amplitude result is the decisive one: **a real breathing mode would not
lose 95% of its relative amplitude when the same creature is drawn on 3× finer cells.**

What survives of Lane 1's claim: the wobble frequency is set by lattice crossing, generalised to
all low-order lattice lines (not only 1/|vx| and 1/|vy|). Which line dominates is not predicted by
this account; it plausibly depends on how the dynamics filter each forcing frequency.

Mean mass ΣA/R² is resolution-stable to 2e−4 relative across R = 13–39, so the mean is a good
observable and the wobble is not.

### HR-001b: S001's heading is pinned by the lattice (exploratory, not preregistered)

Found while running E2: start rotations 6° and 9° gave identical velocities to four digits. In an
isotropic continuum heading is a neutral direction, so rotating the start by 3° should rotate the
heading by about 3°. Follow-up (`h001_explore.py`, heading in 1000-step windows over 8000 steps):

![H001 evidence](../experiments/H001-lattice-wobble/h001.png)

- **R = 13, 46 start rotations (0°–45° by 1°)** (`x1_R13.csv`): 40 runs settle (heading change
  < 0.05° between the last two 1000-step windows) onto only **10 headings**: 68.20, 62.14, 60.82,
  51.56, 49.57, 40.42, 38.42, 29.18, 27.84, 21.80°, in mirror pairs about 45°. The other 6 are
  still moving at step 8000; the four near the diagonal (start 19°–22°) wander around 45° ± 1.3°
  without locking. No run ends inside the 9° gaps 51.6°–60.8°, 29.2°–38.4° or 40.4°–49.6°. Some
  runs take thousands of steps to snap (rotation 8°: 59.1° → 60.82° by step 7000).
- **R = 26, same 46 start rotations** (`x2_R26_fine.csv`): pinning **persists but is weaker**.
  37 runs settle onto **17 headings**, 9 are still drifting, and the largest empty gap shrinks to
  6.1°. Plateaus of 2–4 consecutive start rotations still share one heading (rotations 10°–13° all
  give 53.28°). A coarser 3°-step sweep (`x1_R26.csv`) hid this by giving 16 distinct headings for
  16 starts; I first misread that as "pinning gone".
- Speed varies by only ~0.2% across headings (0.4787–0.4798 R/time at R = 13).

**Consequences for other lanes.**

- Heading, and anything measured in the creature's frame, is lattice-dependent at R = 13. Lane 4's
  frame-based interventions (I003 frontal addition, I004 port-side injury) inherit this.
- A perturbation can knock S001 from one pinned heading to another. A "RECOVERED" creature on a
  different pinned heading is a different lattice state; record the post-recovery heading.
- Lane 6: a "new behaviour" that is really a different lattice-pinned heading is not a new
  specimen. Check any candidate at R ≥ 26.

### Executable tests (`tests/test_h001_lattice_wobble.py`, shortened runs)

- the dominant mass frequency sits on a lattice line at R = 13 and R = 26;
- relative wobble amplitude falls by more than 2× from R = 13 to R = 26;
- mean ΣA/R² agrees between R = 13 and R = 26 to 1e−3;
- characterization: at R = 13, start rotations 6° and 9° both pin to 60.82° ± 0.1°.

### Proposed ledger entries (for the coordinator)

- **S001 mass oscillation**: NUMERICALLY_FRAGILE. The 4.32-step wobble is a lattice-sampling
  artifact; its relative amplitude falls from 2.6e−3 (R = 13) to 1.3e−4 (R = 39). Run IDs:
  H001-E1-R{13,20,26,39}, H001-E2-rot{0..45}. Caveat: preregistered P2 failed as written (see above).
- **S001 heading is lattice-pinned**: OBSERVED (exploratory, single execution path). 46 start
  rotations settle on 10 headings at R = 13 and 17 at R = 26 (largest empty gap 9.2° → 6.1°).
  Run IDs: H001-X1-R13-rot{0..45}, H001-X2-R26-rot{0..45}. Caveats: 8000-step horizon, 6 and 9
  runs still drifting; not yet checked on Lane 2's `src/alm`.

### Reproduction

```bash
./scripts/bootstrap.sh
D=research/experiments/H001-lattice-wobble
.venv/bin/python $D/h001.py e1 > $D/e1.csv             # ~45 s
.venv/bin/python $D/h001.py e2 > $D/e2.csv             # ~45 s
.venv/bin/python $D/h001_explore.py 13 1 > $D/x1_R13.csv   # ~5 min on 4 cores
.venv/bin/python $D/h001_explore.py 26 3 > $D/x1_R26.csv   # ~8 min on 4 cores
.venv/bin/python $D/h001_explore.py 26 1 > $D/x2_R26_fine.csv  # ~25 min on 4 cores
.venv/bin/python $D/aniso_check.py > $D/aniso_check.txt    # ~2 min (HR-003)
.venv/bin/python $D/plot_h001.py                       # h001.png
(.venv/bin/python $D/heading_means.py 13 0 27 55 70; .venv/bin/python $D/heading_means.py 26 0 67 | tail -n +2) > $D/heading_means.csv  # HR-006
.venv/bin/pytest -q tests/test_h001_lattice_wobble.py
```

---

## HR-002: Lane 4 protocol L4-001 (PR #5; posted there as a comment)

The protocol is strong (preregistered, logs achieved ΔM, threshold-band sensitivity, delayed
outcome, template correlation for the "new blob" question). Objections:

1. **Phase replicates sample the wrong phase.** t0 = 1000…1004 spans one 4.32-step period of the
   (1, 0) line only. The lattice phase is two-dimensional (fractional x and y of the centroid), and
   the y crossing period is 1.73 steps. Five consecutive steps cover a thin diagonal of that phase
   torus. Spread t0 over a longer interval (for example t0 = 1000 + 37k, k = 0…4) so the
   sub-pixel phases are sampled quasi-uniformly.
2. **N = 192 tests the torus size, not the resolution.** The charter's "is the result tied to one
   grid size?" is about how finely the creature is resolved. HR-001 shows lattice effects at
   R = 13 that shrink 20× by R = 39. Re-run each transition's bracket ends at R = 26 (creature
   zoomed 2×, N = 256, interventions scaled in units of R).
3. **Heading is lattice-pinned (HR-001b).** Record the post-recovery heading. A recovered creature
   on another pinned heading should be reported separately from one on the original heading.
4. The 0.8–1.2 speed band is safe against the 0.2% heading dependence of speed. No change needed.

## HR-003: Lane 5 `alm.morphometrics` and L5-baseline (PR #4; posted there as a comment)

1. **`symmetry_order` reports lattice symmetry for an isotropic body.** A sampled isotropic
   Gaussian (σ = 6 cells, 128²) gets `symmetry_order` 8, 4 or 6 depending only on its sub-pixel
   centre ((64, 64), (64.5, 64.5), (64.3, 64.7)), with `rotational_harmonics` up to 0.033. Those
   harmonics are the lattice's own, not the body's. Suggested fix: document a noise floor measured
   from isotropic controls at the organism's size, and return "none" (0) when no harmonic exceeds
   it. Suggested test: an isotropic Gaussian must not report a symmetry order.
2. **L5 proposed claim 2 ("every dominant period is a grid-crossing frequency") has a
   counterexample in Lane 5's own `summary.csv`.** At rotation 0 the anisotropy period is 8.015
   steps, and no lattice line with |m|, |n| ≤ 2 lies within 0.009 cycles/step of it (nearest:
   (−2, 1), 8.64 steps). An independent second-moment computation (`aniso_check.py`,
   `aniso_check.txt`) reproduces the peak. It is still lattice-driven: at R = 20 and 26 the 8.0-step
   component is gone, peaks sit on lattice lines (7.12, 5.69 steps), and anisotropy sd falls
   4.8e−3 → 3.1e−3 → 1.4e−3. Verdict: the claim's conclusion survives, but its evidence should be
   the resolution test, not period matching.
3. **Mean anisotropy is biased by 1.2% at R = 13** (0.2953 vs 0.2989 / 0.2987 at R = 20 / 26).
   Other means (mass) are converged to 2e−4.
4. **`dominant_period` on mass will return the lattice line.** The docstring already warns. Since
   HR-001 gives an explicit formula, a helper that lists the lattice lines m·vx + n·vy for a given
   velocity would let callers flag a period as artifact automatically.

## HR-004: Lane 2 L2-S001 baseline claim (PR #6; posted there as a comment)

1. "Translates along a fixed 68.2° heading" is expected from lattice pinning (HR-001b) and is not
   evidence about the organism. 68.198° is the 5:2 lattice direction (tan = 2.500).
2. The claim asserts the 4.32-step period is a lattice artifact; H001 now supplies the evidence.
3. No semantic problem found in `lenia.py`. Kernel layouts agree for even N; odd N is untested.

## HR-005: Lane 3 replication and numerics (PR #8; posted there as a comment)

Lane 3's report is the strongest evidence on the board. Four objections:

1. **"The heading lock mostly disappears at R = 26" is contradicted by Lane 3's own CSV and by
   H001.** In `heading-R26.csv`, start rotations 12.5° and 15° both end on 53.28° (15° after
   drifting 1.2°). 30° and 32.5° both end on 36.72° (32.5° after drifting 1.9°). 65° and 67.5° both
   end on 2.06°. The 2.5° grid hides most of the plateaus, as my own 3° grid did (HR-001b). The
   two implementations agree on the R = 26 plateau headings to about 0.01°: 59.35, 53.28, 49.33,
   46.54, 43.46, 42.09, 40.67, 36.72, 30.65 and 25.91°. That is an independent replication of
   pinning *at* R = 26. Proposed restatement: "pinning weakens from R = 13 to R = 26 (largest
   unreachable gap in 0°–45° goes from 9.2° to 6.1°) but does not disappear". The
   `nearest_rational_slope` labels at R = 26 are off by up to 0.9° (42.09° labelled 7/8 = 41.19°),
   so they are not evidence of rational-slope locking beyond 5/2 at R = 13.
2. **The Richardson extrapolation assumes first-order convergence, and the T-sweep says
   otherwise.** Successive speed differences for T = 20→40→80→160→320 are 0.0232, 0.0146,
   0.0091, 0.0055. Each is about 0.6× the previous one, not 0.5×, so the effective order is
   about 0.7 (plausibly from the non-smooth hard clip). Geometric extrapolation gives a limit of
   about 0.5745 R/time, so T = 10 is 16.6% low rather than 16%. The conclusion stands and the
   number moves slightly. Headings also move with T (68.2° → 66.5°), and at R = 13 speed depends
   on heading by up to 1.2% (Lane 3's own finding), which is a small confound in the sweep.
3. **"Wobble amplitude ∝ ~R⁻²" is confounded with heading.** Wobble amplitude depends strongly
   on heading at fixed R: at R = 13 sd/mean is 2.0e−3 at 12.7°, 2.6e−3 at 68.2°, 6.6e−3 at 40.4°
   and 1.0e−2 at the axis (`heading_means.csv`). Lane 3's resolution runs end on different headings
   (68.2, 67.9, 67.3, 68.0, 64.3, 65.0°). At R = 39 Lane 3 (nearest-neighbour zoom, heading 64.3°)
   gets 2.5e−4 and H001 (bilinear zoom, 66.3°) gets 1.3e−4, a 2× difference at the same R.
   The robust statement is "amplitude falls about 20× from R = 13 to R = 39–52". The exponent is
   not determined.
4. **"The 1/|vx| rule fails in 9 of 17 runs" tests too narrow a rule.** H001's generalized rule,
   in which any low-order lattice line m·vx + n·vy with |m|, |n| ≤ 2 counts, holds in 14 of 16
   headings against 1.45 expected by chance. Lane 3 could rescore its resolution runs against
   that line set.

The bitwise match with Lane 2 means the two FFT paths share a numerical recipe, as Lane 3 says.
The FFT-free direct path is the independent check, and it holds.

## HR-006: Lane 5 "feature means are heading-invariant" (PR #4) is refuted at R = 13

Lane 5 tested start rotations 0°, 23° and 45°. Those land on the 68.2°, 40.4° and 21.8° pinned
headings, and 0° and 45° are mirror images. Lane 3 found an axis-locked plateau near 0°.
`heading_means.py`, 6000 steps per run, statistics over steps 2000–5999 (`heading_means.csv`):

| R | start rotation | heading | speed (R/time) | mass | gyradius | anisotropy | mass sd/mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 0° | 68.20° | 0.47941 | 0.43580 | 0.43764 | 0.2953 | 2.6e−3 |
| 13 | 27° | 40.43° | 0.47869 | 0.43592 | 0.43823 | 0.2917 | 6.6e−3 |
| 13 | 55° | 12.67° | 0.47783 | 0.43611 | 0.43809 | 0.2908 | 2.0e−3 |
| 13 | 70° | −0.46° | 0.47343 | 0.43557 | 0.43861 | **0.2649** | 1.0e−2 |
| 26 | 0° | 67.07° | 0.47966 | 0.43589 | 0.43755 | 0.2987 | 5.3e−4 |
| 26 | 67° | −2.06° | 0.47969 | 0.43588 | 0.43759 | **0.2993** | 9.2e−4 |

At R = 13 the axis-travelling S001 is about 10% less elongated (0.265 vs 0.295) and 1.2% slower
than on the 5/2 plateau. The same run on the CI runner gave 0.2664 (−9.8%; same numpy 2.5.3,
different machine): the axis-locked state jitters, so its exact mean is not reproducible across
machines to 4 digits, though the effect is. At R = 26 the same comparison agrees to 0.2%. Verdict: "feature means are
heading-invariant" is **REFUTED at R = 13** (anisotropy, and speed at 1%) and **holds at R = 26**.
Mass and gyradius means are invariant to 0.2% at both resolutions. Any anisotropy-based predictor
at R = 13 must control for heading.
