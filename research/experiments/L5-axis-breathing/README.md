# L5-axis-breathing: S001 travelling along a grid axis at R = 13 (a wobble that is numerical)

Lane 5, 2026-10-07. Follows up Lane 7 HR-006, which refuted L5-baseline's "feature means are
heading-invariant" at R = 13.

## Manifest

| Field | Value |
| --- | --- |
| Specimen | S001 Orbium O2u; catalog cells zoomed to R (bilinear) and rotated (bilinear), as in Lane 7's H001 `initial_state` |
| Rule | poly/poly, μ = 0.15, σ = 0.015, T = 10, β = [1], Euler + clip, float64, periodic |
| Simulator | Lane 2 `alm.Lenia` |
| Grid | round(128 R / 13), rounded up to even: 128 / 198 / 256 |
| Runs | (R, start rotation) ∈ {(13, 0), (13, 70), (20, 0), (20, 70), (26, 0), (26, 67)} |
| Horizon / window | 8000 steps; statistics over steps 2000–7999, sampled every step |
| Features | `alm.morphometrics.centroid`, `anisotropy`, `velocity`, `dominant_period` |
| Intervention / seed | none / none (deterministic) |
| Reproduction | `.venv/bin/python research/experiments/L5-axis-breathing/axis_breathing.py` (about 50 s on 4 cores) |
| Output | `results.csv` |

## Results (OBSERVED)

| R | start rot | heading | heading sd (per step) | speed (R/time) | anisotropy mean ± sd | anisotropy range | dominant period |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 0° | 68.20° | 1.6° | 0.4796 | 0.295 ± 0.005 | 0.286–0.307 | 8.0 steps |
| **13** | **70°** | **0.22°** | **4.2°** | **0.4751** | **0.267 ± 0.094** | **0.087–0.500** | **140 steps** |
| 20 | 0° | 67.19° | 0.8° | 0.4797 | 0.299 ± 0.003 | 0.292–0.307 | 7.1 steps |
| 20 | 70° | −5.49° | 1.2° | 0.4784 | 0.293 ± 0.012 | 0.269–0.310 | 10.9 steps |
| 26 | 0° | 67.07° | 0.5° | 0.4797 | 0.299 ± 0.001 | 0.297–0.303 | 5.7 steps |
| 26 | 67° | −2.06° | 0.7° | 0.4797 | 0.299 ± 0.010 | 0.284–0.315 | 22.3 steps |

### What this says

1. **At R = 13 the axis-travelling S001 "breathes".** Its elongation swings between 0.09 (nearly
   round) and 0.50, which is 20× the fluctuation on the 68.2° plateau. Its heading also wobbles
   more about the axis (per-step heading sd 4.2° vs 1.6° on the 68.2° plateau). The cycle is slow and irregular. The dominant anisotropy period is 140
   steps over steps 2000–7999, and 247 steps over steps 2000–5999 in a preliminary run. This
   is the behaviour behind Lane 7's lower mean anisotropy (0.265).
2. **The breathing is numerical.** At R = 26, the run that settles 2° off the axis has
   anisotropy 0.299 ± 0.010 with no slow component. Its mean matches the diagonal plateau to
   0.2%, as Lane 7 found. Mass, gyradius and speed differ little between headings at any R.
3. So a creature that visibly "wobbles" at R = 13 does so only because of how it sits on the
   lattice. This is NUMERICALLY_FRAGILE behaviour, not a new phenotype. It is a cautionary case
   for the nickname protocol: it would fail criterion 3 (survives a modest resolution change).

## Proposed claim (for the coordinator)

**S001 travelling along a grid axis at R = 13 shows a slow (≈140–250 steps), large-amplitude shape
oscillation (anisotropy 0.09–0.50, per-step heading sd 4.2°) that is absent at R = 26.** NUMERICALLY_FRAGILE.
Single stepping path (Lane 2). Lane 7's independent second-moment code (HR-006) agrees on the
mean anisotropy (0.2649 vs 0.2665 here, over different windows).

## Caveats

- The R = 20 run did not land on the axis (−5.5°). The transition between R = 13 and R = 26 is
  not resolved. A start rotation that pins R = 20 to 0° is the next run.
- The R = 26 "axis" run sits 2.06° off the axis on its own plateau, not at exactly 0°.
- The slow period depends on the window, which suggests it is quasi-periodic rather than a
  clean limit cycle. No spectral analysis beyond the dominant peak was done.
