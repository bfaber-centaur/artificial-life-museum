# L5-baseline: S001 morphometric baseline and heading dependence

Lane 5 (Morphometrics / Behaviour), 2026-10-07.

## Manifest

| Field | Value |
| --- | --- |
| Specimen | S001 Orbium O2u, cells from `research/specimens/S001-orbium/initial-cells-u8.csv` |
| Rule | poly/poly, R = 13, T = 10, μ = 0.15, σ = 0.015, β = [1], Euler + clip, float64 |
| Grid | 128 × 128 periodic torus, start patch centred as in the dossier |
| Stepping path | **interim**: Lane 1's `reconstruct.py` (`make_kernel_fft`, `step`). To be re-run on Lane 2's `src/alm` runner. |
| Features | `alm.morphometrics.snapshot(A, R=13)` every step (area threshold 0.1) |
| Intervention | none; the start state is rotated 0°, 23°, 45° (bilinear, clipped, as in Lane 1's `lattice_heading.py`) to change heading relative to the grid |
| Horizon / window | 4000 steps; statistics over steps 1000–4000 (3001 samples, every step) |
| Seed | none (deterministic) |
| Reproduction | `.venv/bin/python research/experiments/L5-baseline/measure_s001.py` (about 90 s) |
| Outputs | `trace-rot00.csv`, `trace-rot23.csv`, `trace-rot45.csv` (per step), `summary.csv` |

Two clean-process runs produced byte-identical traces.

## Results (OBSERVED)

| Feature (steps 1000–4000) | rot 0° (heading 68.2°) | rot 23° (heading 40.4°) | rot 45° (heading 21.8°) |
| --- | --- | --- | --- |
| speed, R per time unit | 0.4796 | 0.4790 | 0.4796 |
| mass ΣA/R², mean ± sd | 0.43580 ± 0.00111 | 0.43592 ± 0.00289 | 0.43581 ± 0.00111 |
| gyradius (R), mean ± sd | 0.4376 ± 0.0012 | 0.4382 ± 0.0045 | 0.4376 ± 0.0012 |
| anisotropy 1 − λmin/λmax | 0.295 ± 0.005 | 0.292 ± 0.014 | 0.295 ± 0.005 |
| occupied area A > 0.1 (R²) | 1.005 ± 0.015 | 1.003 ± 0.024 | 1.005 ± 0.015 |
| harmonic a₂ (bilateral elongation) | 0.216 ± 0.008 | 0.213 ± 0.013 | 0.216 ± 0.008 |
| major axis − heading | −0.05° | +0.27° | +0.05° |
| max wrap extent | 0.18 | 0.20 | 0.18 |
| dominant period: mass | 4.32 | 14.24 | 4.32 |
| dominant period: gyradius | 8.64 | 14.24 | 8.64 |
| dominant period: area | 2.37 | 14.24 | 2.37 |

### What this says

1. **Feature means are heading-invariant; feature fluctuations are not.** Means agree across
   headings to 0.3% (mass), 0.15% (gyradius) and 1.2% (anisotropy). The standard deviations are
   1.6–3.9× larger at heading 40.4° than at 68.2°/21.8°.
2. **Every dominant period is a grid-crossing frequency.** At heading 68.2°, 1/|vx| = 4.32 steps,
   8.64 is its first subharmonic, and 2.37 steps is the row-crossing frequency 1/1.73 = 0.578
   cycles/step aliased below Nyquist (1 − 0.578 = 0.422 → 2.37 steps). At 40.4° everything locks
   to the 14.2-step beat Lane 1 reported. No feature showed a period that is not explained by
   the lattice. This extends Lane 1's mass-period observation to gyradius, anisotropy, area and the
   rotational harmonics.
3. **Orbium is elongated along its direction of travel**, to within 0.3°. So the
   second-moment major axis gives the heading (up to sign) from a single snapshot, without
   tracking. The dominant rotational harmonic is k = 2 (a₂ ≈ 0.216), which is this elongation.
   Orbium has no rotational symmetry beyond that.
4. The 0° and 45° runs are mirror images (heading 68.2° vs 21.8° = 90° − 68.2°) and give identical
   statistics to 4–5 digits. This is a free sanity check on the feature code.

### Implications for Lane 4 (recovery definitions)

- Use **feature means over a window of at least ~15 steps** (longer than the slowest lattice beat
  seen, 14.2 steps) rather than instantaneous values when comparing pre/post states.
- Do **not** set recovery tolerances from the baseline sd of one heading. The sd changes up to 4× with
  heading, so a "3 sd" band fit at 68.2° would call a healthy organism at 40.4° unrecovered.
  A heading-independent band is, for example, ±1% of the windowed mean mass.
- An injury that rotates the organism changes its heading, so fluctuation-based metrics can
  change after a perturbation for purely lattice reasons.

## Proposed claims (for the coordinator)

1. **S001 baseline morphometrics are heading-invariant in mean** (mass 0.4358, gyradius 0.438 R,
   anisotropy 0.29, area 1.00 R², speed 0.479 R/time) across headings 21.8°, 40.4°, 68.2°.
   OBSERVED; single stepping path (Lane 1 reference transcription).
2. **All S001 baseline feature oscillations are lattice artifacts**: their dominant periods equal
   grid-crossing periods (or their alias/beat) at every tested heading. OBSERVED. This extends Lane 1's
   claim 3 and is a target for Lane 3/7, for example by varying R and checking that the periods scale.

## Caveats

- One grid size (128), one R (13), one T (10). Resolution/timestep dependence is Lane 3's.
- Rotated starts are bilinear-interpolated, so they are not exactly the catalog organism. They
  relax to the same means within the 1000-step burn-in.
- The area threshold (0.1) is a fixed convention and was not tuned.
