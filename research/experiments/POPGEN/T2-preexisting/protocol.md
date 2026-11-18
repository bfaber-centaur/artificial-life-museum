# POPGEN T2: adaptive therapy with a pre-existing resistant clone (pre-registered protocol)

Follow-up to T1 ([`../T1-relapse/`](../T1-relapse/)). **Written after T1's results and before any T2 run.**

## Why

T1 scored as follows:

- PT1 failed: 4 of 8 constant runs relapsed with mostly resistant matter, all of them at κ 0.4. At κ 0.3 the drug was too weak to control even sensitive matter.
- PT2 failed: with the cost of resistance, constant dosing eradicated **8 of 8** tumours, and adaptive dosing never did better.
- PT3 passed.

The reason is the starting state. A T1 tumour has **no resistant matter when treatment starts**
(resistant share 0.000). With the cost of resistance switched on, almost none arises before the
drug clears the tumour. Adaptive therapy is designed for the opposite case: an incurable tumour
that already carries a resistant clone (Gatenby et al. 2009, from memory). T2 adds that clone
and changes nothing else.

## Change from T1 (the only one)

At the moment treatment starts (burden B0), one cell of the tumour becomes resistant. This is
the Voronoi region of one `tree.peaks` peak, chosen with rng seed = run seed, and its genome is
set to **g 0.3**. That makes it immune to the drug (threshold 0.4) and slow. Mutation (0.03 per
10 tu) continues as before. Its realised mass share is recorded. The none, constant and adaptive
arms all start from **the same** edited state.

The grid is as in T1 after amendment A1: c ∈ {0, 0.3}, κ ∈ {0.3, 0.4}, seeds 1–4, 128², 6000 tu,
giving 40 runs.

## Predictions

Pairs and the scoring of "adaptive better" are as in T1.

| ID | Prediction |
| --- | --- |
| PT2-1 | **Constant dosing relapses from the clone.** With c = 0, constant dosing progresses with mostly resistant matter (share > 0.5 at progression) in at least 6 of 8 pairs. |
| PT2-2 | **With competition, adaptive delays relapse.** With c = 0.3, adaptive beats constant in at least 5 of 8 pairs. |
| PT2-3 | **Without competition, it doesn't.** With c = 0, adaptive beats constant in at most 4 of 8 pairs. |
| PT2-4 | **The untreated tumour keeps the clone small when there is competition.** With c = 0.3, the untreated arm's resistant share at 6000 tu is below its starting share in at least 3 of 4 seeds. With c = 0 it is not. |

## Files

`run_t2.py SEED C` appends to `t2.jsonl`. `analyse_t2.py` writes `t2_results.json`. Both reuse
T1's `treat`.

## Amendments

- **A1 (2026-11-18, before the main runs; design unchanged).** Two smoke tests (seed 1, 5 tu at
  c 0.3 and 100 tu at c 0) were run and their rows deleted. They showed that **without the drug
  the clone dissolves within about 80 tu, even at c 0** (resistant share 0.15 → 0.0002), because
  GenomeLenia's inheritance blends the clone's genome into its neighbours' (E0, E1a). Under the
  drug, the resistant share grows instead. So PT2-4's "c 0: not smaller" half is expected to
  fail, for a reason unrelated to competition: blending removes the clone faster than any cost
  could. The design and predictions are left as registered. A particulate-inheritance version
  of T2 is the natural next step.
