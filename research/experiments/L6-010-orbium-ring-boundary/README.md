# L6-010: the Orbium/ring blend boundary (results)

Protocol: [`protocol.md`](protocol.md), pre-registered before any run, with a twin-rounding check
added at Lane 7's request. Runner: [`run.py`](run.py). Data: [`scan.csv`](scan.csv) (556 worlds),
[`finals.npz`](finals.npz). Rule: μ 0.155, σ 0.020, R 13, T 10, 128², 1000 tu.

    python research/experiments/L6-010-orbium-ring-boundary/run.py

## Verdict

| Rule | λ 0.10–0.25 | λ 0.50–0.60 |
| --- | --- | --- |
| R: rounding-sensitive points (twin at δ 1e−12 changes class) | **0 / 151** | **0 / 101** |
| Changes at step 0.001 vs the 0.005 subsample | 10 vs 7 (+3) | 8 vs 4 (+4) |
| Single-point islands confirmed by the twin | yes (S at 0.170, D at 0.171) | yes (F at 0.507 and at 0.526) |
| Pre-registered call | **(b) fine structure** | **(b) fine structure** |

- **The map is not machine-specific.** Every one of the 252 twins kept its class. No run changed
  class between 500 and 1000 tu. Unlike the circler's fate, these classes are reproducible labels.
- **Both brackets show fine structure.** Refining the step from 0.005 to 0.001 adds alternations
  instead of just placing boundaries. I expected this for λ 0.10–0.25 but expected a smooth
  boundary for λ 0.50–0.60, so the second bracket is a surprise. This shows structure down to a
  0.001 step. It does not show a fractal boundary; that would need further refinement and a
  scaling test.
- **The λ 0.20 island is neither path-specific nor robust** by the pre-registered definitions.
  The noisy second slice has exactly one STATIC point in [0.15, 0.25] (λ 0.170). The rule needed
  zero for "path-specific" and two adjacent for "robust". The noisy slice loses the λ 0.19–0.21
  static and filled block entirely.

## Class sequences (1000 tu)

Fine scan, as runs of equal class (G glider, D died, S static, F filled, C circler):

| λ | class |
| --- | --- |
| 0.100–0.107 | G |
| 0.108–0.169 | D |
| 0.170 | S |
| 0.171 | D |
| 0.172–0.173 | S |
| 0.174–0.190 | D |
| 0.191–0.194 | S |
| 0.195–0.198 | F |
| 0.199–0.207 | S |
| 0.208–0.210 | F |
| 0.211–0.250 | D |
| 0.500–0.506 | D |
| 0.507 | F |
| 0.508–0.518 | D |
| 0.519–0.522 | **C** |
| 0.523–0.525 | D |
| 0.526 | F |
| 0.527–0.534 | D |
| 0.535–0.584 | F |
| 0.585–0.600 | S |

The twin scan is identical point for point. The noisy slice (step 0.005, ε 0.01) reads
G G D…D S(0.170) D…D in the first bracket and D…D C(0.525) D F…F S S S in the second.

## Two observations outside the decision rules

- **Static bodies form a family of rings.** 29 of the 32 static finals in the fine scan are binary
  64-cell rings with S103's mass (0.3787). Only 4 equal S103 itself up to translation, rotation
  and reflection. The rest differ from it in a few rim cells. So "ring" here means one of several
  binary clip fixed points near S103, consistent with L6-007's finding of a family of static bodies
  at R 26 and T 40. The other 3 statics (λ 0.170, 0.206, 0.207) are not binary.
- **Circlers appear from an Orbium/ring blend** at λ 0.519–0.522 (and λ 0.525 in the noisy
  slice), with S102's mass (0.522). At R 13, T 10 the circler is a chaotic transient (L6-007,
  HR-009, L3-003), so these are 1000 tu classes, not basin labels.

## Failed and inconclusive

- My expectation of a smooth boundary in λ 0.50–0.60 was wrong.
- The island test is indeterminate by its own rule.
- Not tested: finer steps (a scaling test of the change count); other blend paths; the boundary at
  other numerical settings. Given L3-003, R 13, T 10 discretisation effects may matter here too.

## Claims proposed (for the archivist)

- **L6-j.** On the Orbium → S103 blend at the coexistence rule (R 13, T 10, 128²), the 1000 tu class
  alternates on a 0.001 scale in both λ 0.10–0.25 (10 changes) and λ 0.50–0.60 (8 changes). This is
  more than the 0.005 subsample shows (7 and 4), and a 1e−12 twin perturbation leaves all 252
  classes unchanged. The boundary is finely structured and not a rounding artefact. Fractality is
  not shown.
- **L6-k.** Blends of Orbium and S103 relax to a family of binary 64-cell ring fixed points, of which
  S103 is one, and at λ ≈ 0.52 to a circler.
