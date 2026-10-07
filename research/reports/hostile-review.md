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

- **R = 13, 46 start rotations (0°–45° by 1°)** (`x1_R13.csv`): all runs converge to one of **11
  headings**: 68.20, 62.14, 60.82, 51.58, 49.57, ≈45 (wanders ±1.3° with no lock), 40.42, 38.43,
  29.18, 27.85, 21.80°. These form mirror pairs about 45°. No run ends between 51.6° and 60.8°,
  or between 29.2° and 38.4°. Some runs take thousands of steps to snap (rotation 8°: 59.1° →
  60.82° by step 7000; rotation 31°: still drifting at step 8000).
- **R = 26, 16 start rotations (0°–45° by 3°)** (`x1_R26.csv`): **16 distinct headings**
  (67.1, 63.4, 59.35, 58.7, 53.28, 49.33, 47.91, 43.46, 42.09, 40.67, 36.72, 31.4, 30.64, 25.9,
  22.93, 20.7°), roughly following 67° − rotation, with a few still drifting slowly. Pinning is
  much weaker at the finer resolution. The 1°-step R = 26 sweep (`x2_R26_fine.csv`) is below.
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
- **S001 heading pinning at R = 13**: OBSERVED (exploratory). 46 start rotations → 11 headings at
  R = 13; 16 start rotations → 16 headings at R = 26. Run IDs: H001-X1-R13-rot{0..45},
  H001-X1-R26-rot{0..45 by 3}. Caveat: 8000-step horizon; some runs still drifting.

### Reproduction

```bash
./scripts/bootstrap.sh
D=research/experiments/H001-lattice-wobble
.venv/bin/python $D/h001.py e1 > $D/e1.csv             # ~45 s
.venv/bin/python $D/h001.py e2 > $D/e2.csv             # ~45 s
.venv/bin/python $D/h001_explore.py 13 1 > $D/x1_R13.csv   # ~5 min on 4 cores
.venv/bin/python $D/h001_explore.py 26 3 > $D/x1_R26.csv   # ~8 min on 4 cores
.venv/bin/pytest -q tests/test_h001_lattice_wobble.py
```

---

## HR-002: Lane 4 protocol L4-001 (branch `claude/night0-disturbance-np4adr`, no PR yet)

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

## HR-003: Lane 5 `alm.features` (branch `claude/night0-morphometrics-1103d7`, no PR yet)

1. **`symmetry_order` reports lattice symmetry for an isotropic body.** A sampled isotropic
   Gaussian (σ = 6 cells, 128²) gets `symmetry_order` 8, 4 or 6 depending only on its sub-pixel
   centre ((64, 64), (64.5, 64.5), (64.3, 64.7)), with `rotational_harmonics` up to 0.033. Those
   harmonics are the lattice's own, not the body's. Suggested fix: document a noise floor measured
   from isotropic controls at the organism's size, and return "none" (0) when no harmonic exceeds
   it. Suggested test: an isotropic Gaussian must not report a symmetry order.
2. **`dominant_period` on mass will return the lattice line.** The docstring already warns. Since
   HR-001 gives an explicit formula, a helper that lists the lattice lines m·vx + n·vy for a given
   velocity would let callers flag a period as artifact automatically.
