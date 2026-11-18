# POPGEN T1: therapy with truly resistant cells (pre-registered protocol)

Follow-up to the therapy toy (`REPLICATORS/therapy.py`, C119–C124). Bobby said on 2026-11-17 to
"give the therapy room some leash". **Written and committed before any T1 run.**

## Why

In C119–C124 the drug removes matter at rate κ·g, so even "resistant" slow matter (g < 0.4)
still dies, just more slowly. The resistant remnant left by constant dosing never regrew (C124),
so there was no relapse to delay, and adaptive therapy could not show its benefit. Adaptive
therapy theory (Gatenby et al. 2009; Zhang et al. 2017, from memory) needs two things:
**resistant cells that the drug cannot kill**, and **competition** in which sensitive cells hold
resistant ones back. T1 adds the first and switches the second (the C122 crowding cost) on and
off in a 2 × 2 design.

## Change (the only one)

The drug removes matter only where the genome is above the resistance threshold:

    A ← A (1 − dt κ g · [g ≥ 0.4])

Matter with g < 0.4 (the "resistant" type in C119–C124) is **immune**. Everything else is
`therapy.py` unchanged: one 213 #84 cell at g 0.7 with mutation 0.03, grown on a 128² torus to
B0 = 40% of carrying mass. The arms are none, constant, and adaptive (off at B0/2, on at B0), and
progression is the first time burden exceeds 1.25 B0. The optional crowding cost of resistance
is `therapy.crowding_cost`.

| Factor | Levels |
| --- | --- |
| Cost of resistance c | 0, 0.3 |
| Dose κ | 0.3, 0.4 (A1; was 0.4, 0.6) |
| Seed | 1, 2, 3, 4 |
| Arm | none (once per seed and c), constant, adaptive |

Each run lasts 6000 tu, giving 40 runs.

## Predictions

A "pair" is one (seed, κ) at one c, so there are 8 pairs per c. "Adaptive better" means it
progresses later than constant, or does not progress while constant does. "Worse" is the
reverse. Two runs that both never progress are a tie, unless one arm eradicates the tumour and
the other does not. In that case the eradicating arm is better.

| ID | Prediction |
| --- | --- |
| PT1 | **Relapse appears.** With c = 0, constant dosing ends in progression in at least 6 of 8 pairs within 6000 tu, and the matter at progression is mostly resistant (resistant share > 0.5). |
| PT2 | **With competition, adaptive delays relapse.** With c = 0.3, adaptive beats constant in at least 5 of 8 pairs. |
| PT3 | **Without competition, it doesn't.** With c = 0, adaptive beats constant in at most 4 of 8 pairs. |

PT2 and PT3 together are the theory's central claim: the benefit of adaptive therapy comes from
competition. If PT2 fails, the toy does not reproduce the effect even under the conditions
designed for it, and we say so.

## Files

`run_t1.py SEED C [N] [TU]` runs all arms and both doses for one (seed, c) and appends to
`t1.jsonl`. `analyse_t1.py` scores PT1–PT3 and writes `t1_results.json`.

## Amendments

- **A1 (2026-11-17, before the main runs).** A 10 tu smoke test (seed 1, c 0.3) showed that
  constant dosing at κ 0.6 wipes out the tumour within 10 tu, before any resistant matter can
  arise. No resistant matter exists at the start of treatment (resistant share 0.0), so κ 0.6
  cannot test relapse. This matches C119, where κ 0.6 eradicated 4 of 4. **The doses are changed
  to κ 0.3 and 0.4** (C119: 0 and 1 of 4 eradicated; survivors at κ 0.3 were 64–100% resistant).
  Nothing else changes. The smoke-test rows were deleted and are not part of the results.
