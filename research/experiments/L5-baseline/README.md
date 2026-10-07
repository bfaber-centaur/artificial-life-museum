# L5-baseline: S001 morphometric baseline and heading dependence

Lane 5 (Morphometrics / Behaviour), 2026-10-07.

## Manifest

| Field | Value |
| --- | --- |
| Specimen | S001 Orbium O2u, cells from `research/specimens/S001-orbium/initial-cells-u8.csv` |
| Rule | poly/poly, R = 13, T = 10, μ = 0.15, σ = 0.015, β = [1], Euler + clip, float64 |
| Grid | 128 × 128 periodic torus, start patch centred as in the dossier |
| Stepping path | Lane 2's simulator, `alm.Lenia` with `alm.specimens.load("S001").rule` (first version stepped Lane 1's `reconstruct.py`; see *Cross-check* below) |
| Features | `alm.morphometrics.snapshot(A, R=13)` every step (area threshold 0.1) |
| Intervention | none; the start state is rotated 0°, 23°, 45° (bilinear, clipped, as in Lane 1's `lattice_heading.py`) to change heading relative to the grid |
| Horizon / window | 4000 steps; statistics over steps 1000–4000 (3001 samples, every step) |
| Seed | none (deterministic) |
| Reproduction | `.venv/bin/python research/experiments/L5-baseline/measure_s001.py` (about 90 s) |
| Outputs | `trace-rot00.csv`, `trace-rot23.csv`, `trace-rot45.csv` (per step), `summary.csv` |

Two clean-process runs produced byte-identical traces.

### Cross-check: Lane 1 stepper vs Lane 2 simulator

The first version of this experiment stepped Lane 1's reference transcription. Re-running the
same script on Lane 2's `alm.Lenia` (an independent `rfft2` implementation) changes per-step
features by at most 1.9e−7 (mass), 1.9e−7 (gyradius) and 1.1e−6 (anisotropy) over 4000 steps at
heading 68.2°. Every summary statistic in the table below agrees to a relative 7.6e−5 or better;
the largest difference is the sd of thresholded area, which is sensitive to single cells crossing
0.1. These are float-rounding-level differences, the same scale Lane 1 saw against upstream.

> **Correction (2026-10-07, after Lane 7 HR-003/HR-006).** The original version of this page
> claimed that S001 feature means are heading-invariant, and that every dominant period is a
> grid-crossing period. The three headings tested here (68.2°, 40.4°, 21.8°) are all diagonal
> lattice plateaus, and 0°/45° are mirror images. Lane 7 showed that S001 travelling along a grid
> axis at R = 13 is 10% less elongated. [`../L5-axis-breathing/`](../L5-axis-breathing/) shows
> why: at R = 13 the axis-travelling organism's shape swings by a factor of six on a slow,
> irregular cycle, and the effect is gone at R = 26. The claims below are restated accordingly.
> `rotational_harmonics` is now radius-weighted, and `symmetry_order` has a noise floor
> (HR-003 #1). The a₂ row and the traces were regenerated with the new definition.

## Results (OBSERVED, diagonal plateaus only)

| Feature (steps 1000–4000) | rot 0° (heading 68.2°) | rot 23° (heading 40.4°) | rot 45° (heading 21.8°) |
| --- | --- | --- | --- |
| speed, R per time unit | 0.4796 | 0.4790 | 0.4796 |
| mass ΣA/R², mean ± sd | 0.43580 ± 0.00111 | 0.43592 ± 0.00289 | 0.43581 ± 0.00111 |
| gyradius (R), mean ± sd | 0.4376 ± 0.0012 | 0.4382 ± 0.0045 | 0.4376 ± 0.0012 |
| anisotropy 1 − λmin/λmax | 0.295 ± 0.005 | 0.292 ± 0.014 | 0.295 ± 0.005 |
| occupied area A > 0.1 (R²) | 1.005 ± 0.015 | 1.003 ± 0.024 | 1.005 ± 0.015 |
| harmonic a₂ (r-weighted elongation) | 0.216 ± 0.002 | 0.214 ± 0.012 | 0.216 ± 0.002 |
| major axis − heading | −0.05° | +0.27° | +0.05° |
| max wrap extent | 0.18 | 0.20 | 0.18 |
| dominant period: mass | 4.32 | 14.24 | 4.32 |
| dominant period: gyradius | 8.64 | 14.24 | 8.64 |
| dominant period: anisotropy | 8.01 | 14.24 | 8.02 |
| dominant period: area | 2.37 | 14.24 | 2.37 |

### What this says

1. **On the diagonal plateaus, feature means agree across headings, but fluctuations do not.**
   Means agree to 0.3% (mass), 0.15% (gyradius) and 1.2% (anisotropy). The standard deviations
   are 1.6–3.9× larger at heading 40.4° than at 68.2°/21.8°. **This does not extend to a heading
   along a grid axis.** At R = 13 that heading gives anisotropy 0.265 ± 0.094 (Lane 7 HR-006,
   reproduced in `L5-axis-breathing`). Mass and gyradius means stay within 0.2% there.
2. **Most dominant periods are grid-crossing periods.** At heading 68.2°, 1/|vx| = 4.32 steps and
   8.64 is its subharmonic. 2.37 steps is the row-crossing frequency 1/1.73 = 0.578 cycles/step,
   aliased below Nyquist (1 − 0.578 = 0.422 → 2.37 steps). At 40.4° everything locks to the
   14.2-step beat. **The anisotropy period at 68.2° (8.01 steps) does not sit on a low-order
   lattice line** (Lane 7 HR-003 #2). It is still a lattice effect: it vanishes at R = 20 and 26,
   and anisotropy sd falls with R. Period matching alone is therefore weak evidence. The
   evidence that a fluctuation is an artifact is a resolution test.
3. **Orbium is elongated along its direction of travel**, to within 0.3°. The second-moment
   major axis therefore gives the heading (up to sign) from a single snapshot. The dominant
   rotational harmonic is k = 2, which is this elongation. Orbium has no higher rotational
   symmetry.
4. The 0° and 45° runs are mirror images (heading 68.2° vs 21.8° = 90° − 68.2°) and give
   identical statistics to 4–5 digits. This only checks the feature code. It is not a second
   heading.

### Implications for Lane 4 (recovery definitions)

- Use **feature means over a window** rather than instantaneous values when comparing pre/post
  states. At least ~15 steps covers the diagonal-plateau beats. At R = 13, an organism that
  ends up travelling along an axis needs a window of several hundred steps (see
  `L5-axis-breathing`).
- Do **not** set recovery tolerances from the baseline sd of one heading. The sd changes up to
  4× between diagonal plateaus and about 20× on the axis plateau at R = 13. Mass and gyradius
  bands are the safe choice, because their means hold across all headings tested.
  **Anisotropy is not a heading-free recovery metric at R = 13.**
- An injury that rotates the organism can move it onto a different lattice plateau. Its shape
  statistics can then change for purely numerical reasons.

## Proposed claims (for the coordinator)

1. **S001 mass and gyradius means are heading-invariant to 0.2%** at R = 13 (mass 0.4358,
   gyradius 0.438 R) across the diagonal plateaus 21.8°, 40.4°, 68.2° and the axis plateau
   (Lane 7 HR-006). Speed is invariant to 1%. OBSERVED. The diagonal plateaus were checked
   on two stepping paths.
2. ~~All S001 baseline feature oscillations are lattice artifacts, shown by period matching.~~
   Restated as follows. **S001's short-period feature fluctuations on the diagonal plateaus
   (2–15 steps) shrink with resolution** (anisotropy sd 4.8e−3 → 3.1e−3 → 1.4e−3 at
   R = 13/20/26), so they are numerical. Period matching alone did not establish this.
   OBSERVED. Lane 7 checked it independently.

## Caveats

- One grid size per R (128 at R = 13), one T (10).
- Rotated starts are bilinear-interpolated, so they are not exactly the catalog organism. They
  relax to the same means within the 1000-step burn-in.
- The area threshold (0.1) is a fixed convention and was not tuned.
