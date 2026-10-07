# S102: Gyrorbium-like circler under the coexistence rule

Stable ID **S102**. Nickname: none. It is the catalogued Gyrorbium gyrans (`OG2g`) carried to a
nearby rule, and it fails the resolution check at its own rule. Dossier owner: Lane 6,
2026-10-07. Experiments: [`../experiments/L6-field/`](../experiments/L6-field/README.md).

## Provenance

In L6-001 (μ × σ sweep seeded with S001's cells), Orbium at μ 0.155, σ 0.022 turned into a
circler within 100 tu. The seed is that state after 20 000 steps (T 10, R 13, 128²). It is
registered under the **coexistence rule** μ 0.155, σ 0.020, where Orbium gliders (and S103)
also persist (L6-004).

**Reference check:** catalog `OG2g` Gyrorbium gyrans (μ 0.156, σ 0.0224) cells under the
coexistence rule converge to the same body: mass 0.5228 vs 0.5223, gyradius 0.5155 vs 0.5158,
path speed 0.498 vs 0.497 R/tu.

## Rule

R 13, T 10, **μ 0.155, σ 0.020**, β [1], poly kernel core, poly growth, Euler + hard clip,
float64, periodic torus. Registered in `alm.specimens` as `S102`.

## Exact initial state

[`S102-circler/initial-cells-u8.csv`](S102-circler/initial-cells-u8.csv): 21 × 24 levels, sum
24 129, rebuilt bit-for-bit by `make_seeds.py`. Placed centred.

## Preview

![S102](S102-circler/preview.png)

## Baseline behaviour

It moves about as fast as Orbium but in a tight circle, so it goes nowhere.

| Metric | T 10, R 13 | T 40, R 13 | T 10, R 26 |
| --- | --- | --- | --- |
| mass | 0.522 (sd 0.010, 1.9%) | 0.497 | **died** |
| gyradius (R) | 0.516 | 0.499 | — |
| net speed (R/tu) | 0.0008 | 0.0004 | — |
| path speed, 1-tu velocity (R/tu) | 0.44–0.50 | 0.48–0.57 | — |
| turning rate | 95°/tu (one lap per ~3.8 tu) | 109–113°/tu | — |
| circle radius | ~0.27 R | ~0.25 R | — |

Runs: `S102-5bfac8f95f` (T 10; second process identical, final sha256 `10d65755…`) and
`S102-7b439113e1` (T 40). The mass oscillates (dominant period 8.9 steps at T 10, 30.5 steps at
T 40).

## Tested perturbations (L6-005, coexistence rule, 2 phases)

It is the most fragile of the three phenotypes under this rule. Survival is phase-dependent
already at the smallest strengths: I001 0.05, I002 0.05–0.10, I004 0.05–0.10. I003 is survived
to 0.10. In one phase, **I004 port injury at 0.15 and 0.25 turned it into the S103 static
ring** (2 of 38 I004 runs). It never turned into a glider.

## Claims

- Proposed L6-a (coexistence with Orbium and S103 under one rule): the circler is one of the
  three phenotypes.
- Proposed L6-b: no circler → glider switch under I001–I004.
- Novelty: REFUTED (catalogued `OG2g` branch).

## Numerical-stability notes

**NUMERICALLY_FRAGILE at its registered rule:** at R 26 the resized seed dies at μ 0.155,
σ 0.020, though it lives from σ 0.0205 up. At T 40 it persists, turning ~15% faster. The
coexistence band with Orbium exists at all three settings but sits at different σ
(L6-004 table).
