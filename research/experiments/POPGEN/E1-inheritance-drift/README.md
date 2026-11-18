# POPGEN E1: blending vs particulate inheritance, neutral drift (results)

Protocols: [`protocol.md`](protocol.md) (E1a, E1b; committed 651c13f before any run) and
[`protocol_e1c.md`](protocol_e1c.md) (E1c; committed 4e50a1b after E1a/b and before any E1c run).
Model: [`../popgen.py`](../popgen.py). Runner `run_e1.py`, data `e1.jsonl` (108 runs, one row each),
scores `analyse_e1.py` → `e1_results.json`. All runs start from the E0 256² worlds at g_r 0.5
(*K* 75 and 73), use residents at g 0.5, τ = 183 tu per generation, and *K* = 74.

    python run_e1.py ARM WORLD_SEED RNG_SEED     # see protocol tables for the 108 (arm, world, rng) triples
    python analyse_e1.py

## Headline

**How the inheritance rule is written decides whether Lenia can do population genetics at all.**
The same mutant cell (one cell out of ~74, at g 0.7 among residents at 0.5) was run under three
rules:

| Inheritance rule | Mutant grew (of 12) | Mutant still present at 3000 tu | Final mutant share (median) | Neutral control cell present at 3000 tu |
| --- | --- | --- | --- | --- |
| **blend** (GenomeLenia as built) | 5 (as a diluted average) | **0** as a distinct type: matter with *L* > 0.5 is 0 in 12/12 | 0.015 (as a blur) | — |
| **part** (majority rule) | 4 | 4 | 0.0 | **0** |
| **stoch** (unbiased random draw) | **12** | **12** | **0.49** (0.24–0.63) | 5 |

Under blending, the mutant is averaged into its neighbours within a few generations. This is
Jenkin's 1867 objection, reproduced. Under majority rule, a rare type loses at every boundary,
so neutral cells always die (0/12) and only a strong mutant sometimes survives (4/12). Under the
unbiased rule, **the mutant spreads from 1.4% to a median of 49% in 16 generations in 12 of 12
runs**, and a neutral cell survives in 5 of 12.

## Verdicts

| ID | Prediction | Result |
| --- | --- | --- |
| P1a | blend+ dissolves the mutant (mutant-majority matter < 1% in ≥ 10/12) | **Pass**, 12/12 (0 in all) |
| P1b | part+ grows more often than part0, and its median final share is higher | **Fail as worded.** It grew more often (4 vs 0), but both medians are 0 |
| P1c | part+ reaches share > 0.5 in ≥ 1 run, blend+ never does | **Fail.** part+ peaks at 0.17. blend+ never does |
| P1d | no frequency bias in part drift (both p₀) | **Fail.** p₀ 0.1: Δp −0.078 ± 0.012, the rare type shrinks in 12/12. p₀ 0.5: Δp +0.091 ± 0.032 |
| P1e | *Nₑ* (part) in 15–148 | p₀ 0.5: 132 (CI 62–391), **pass**. p₀ 0.1: 149 (107–238), **fail** by 1 |
| P1f | *Nₑ* (part) agrees across p₀ within 1.5× | **Pass**, ratio 1.12 |
| P1c-a | stoch: no frequency bias | **Pass.** p₀ 0.5: −0.018 ± 0.021. p₀ 0.1: −0.002 ± 0.019 |
| P1c-b | stoch: s+ grows more often than s0 | **Pass**, 12 vs 3 |
| P1c-c | stoch: 1–6 of 12 neutral single cells present at 3000 tu | **Pass**, 5 |
| P1c-d | stoch: *Nₑ* in 15–148 and agreeing within 1.5× | **Half.** They agree (410 vs 286, ratio 1.43), but **both are above 2*K*** (CIs 279–673 and 182–553) |

**What carries forward.** "stoch" is the inheritance rule for E2–E4. It is the first of the three
that passes a neutrality test. The majority rule's 0.5 result (P1d) is unexplained: a
frequency-dependent rule should be symmetric at p₀ ≈ 0.5. It is not followed up, since the rule
is dropped.

## Exploratory (not pre-registered): Lenia cells look like low-variance reproducers

Two E1c numbers are both too high for textbook branching-process theory with Poisson offspring
(offspring variance σ² = 1):

- **A neutral single cell survives too often.** Survival to *t* generations is about 2/(σ²*t*).
  At *t* ≈ 16 that gives ≈ 12% if σ² = 1. We see 5/12 = 42%.
- **A strong mutant almost never gets lost.** E1c s+ goes from logit share −4.25 to about 0 in
  3000 tu, a selection coefficient of very roughly *s* ≈ 0.26 per generation. Kimura/Haldane
  establishment ≈ 2*s*/σ² ≈ 0.41 if σ² = 1, but the mutant was still present in 12/12 (chance
  ≈ 2 × 10⁻⁵ at 0.41).

**Correction (2026-11-18, before E2).** These two observations are **not** independent evidence.
Both say the same thing: drift per generation is weaker than a census of ~74 cells implies,
that is, *Nₑ* > *K*, which is P1c-d. The "0.41" above uses Haldane's 2*s* with *Nₑ* = *N*. With the
measured *Nₑ* (~300) instead, Kimura's single-copy formula gives
u ≈ 1 − exp(−2 *Nₑ* *s* /*K*) ≈ 0.88, which is consistent with 12/12 (P ≈ 0.2).

Fixation theory also does not need the generation time. In time units, the diffusion has
drift *s*ₜ *p*(1−*p*) and variance *p*(1−*p*)/*D* per tu, where *D* = *Nₑ*τ. The pooled E1c
neutral runs give **D ≈ 62,000 tu**. So the clean test is to predict mutant outcomes from *D*
and from *s*ₜ measured independently, with no tracker and no τ at all. That is E2
([`../E2-diffusion-test/protocol.md`](../E2-diffusion-test/protocol.md)).

Whether Lenia cells really reproduce with low offspring variance, or the tracker's τ is too
short, remains open. It only matters for interpreting *Nₑ*/*K*, not for the test.

## Next

- **E2**: measure offspring variance σ² and generation time from tracked family trees in a
  full world. Measure *s* from logistic fits of the s+ runs and of new δ levels.
- **E3** (fixation test) uses *Nₑ* and *s* from E1c/E2. Its prediction is Kimura with the
  measured σ², not Poisson.

No claims enter `claims.md` until this PR merges and a hostile review has read it.
