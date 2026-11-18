# POPGEN E1: blending vs particulate inheritance, and neutral drift (pre-registered protocol)

ALIFE 2027 research track, question A. Follows E0 ([`../E0-census/README.md`](../E0-census/README.md)),
which found turnover at carrying capacity and showed that GenomeLenia inheritance **blends**.
Bobby approved this step on 2026-11-17. **Written and committed before any E1 run.** The only
code run before this commit was a 200-tu smoke test of `popgen.TwoType` (one labelling, both
modes, δ 0). Later changes go under "Amendments".

## Model

`../popgen.py` `TwoType`: GenomeLenia with a per-pixel label *L* (0 resident, 1 mutant). The rule at
a pixel is GenomeLenia's at g = g₀ + δ·*L*. The two inheritance modes are:

- **blend**: `genome.py`'s rule, under which labels become fractions.
- **part** (particulate): new matter takes the **majority** type of its neighbourhood, and a pixel
  keeps whichever label carries more of its mass, so labels stay exactly 0 or 1.

**Starting worlds.** The final (t 5000) uint8 snapshots of the two E0 runs at 256², g_r 0.5
(seeds 1 and 2; *K* 75 and 73). Residents are g₀ 0.5. **Cells** are labelled whole:
`popgen.label_cells` takes the Voronoi regions of `tree.peaks` on the torus.

**Generation time.** τ = 1000 / 5.455 = **183 tu**, the mean births per cell per 1000 tu in those two
E0 runs (5.81 and 5.10).

## E1a: one strong mutant, blending vs particulate

A single randomly chosen cell becomes a mutant with δ = +0.2 (g 0.7, the level where selection
in GenomeLenia levels off, C111).

| Arm | Mode | δ | Replicates |
| --- | --- | --- | --- |
| blend+ | blend | +0.2 | 12 |
| part+ | part | +0.2 | 12 |
| part0 | part | 0 (neutral control) | 12 |

The replicates are 6 cell choices (rng seeds 1–6) × 2 starting worlds. Each arm uses **the same
12 starting cells**. Runs last 3000 tu (about 16 generations). Every 10 tu we record the type-1
share (mass-weighted mean label), the mass share of matter with *L* > 0.5 ("mutant-majority
matter") and the mixed share (0.1 < *L* < 0.9).

| ID | Prediction |
| --- | --- |
| P1a | **blend+ dissolves the mutant:** at 3000 tu, mutant-majority matter is < 1% of the world in at least 10 of 12 replicates. |
| P1b | **part+ shows selection:** at 3000 tu, the mutant share is above its starting share in more part+ replicates than part0 replicates, and the median final share of part+ exceeds that of part0. |
| P1c | part+ fixes or nearly fixes (share > 0.5 at 3000 tu) in at least 1 replicate, and blend+ never does (mutant-majority matter > 0.5). |

## E1b: neutral drift and effective population size

Particulate mode, δ 0, g₀ 0.5. Each cell is type 1 with probability *p₀*.

| *p₀* | Replicates |
| --- | --- |
| 0.5 | 12 (rng seeds 101–106 × 2 worlds) |
| 0.1 | 12 (rng seeds 201–206 × 2 worlds) |

Runs last 2000 tu (about 11 generations), with the share *p*(t) recorded every 10 tu.

**Estimator (fixed now).** For each replicate, *p*ᵢ = its realised starting share. Let
F(t) = mean over replicates of (*p*(t) − *p*ᵢ)² / (*p*ᵢ(1 − *p*ᵢ)). Fit F(t) = 1 − exp(−t / (*Nₑ* τ))
by least squares on t ∈ (0, 2000]. The 95% CI comes from 2000 bootstrap resamples of
replicates. A replicate that fixes or is lost before 2000 tu stays in the mean, which keeps the
estimator unbiased under the Wright–Fisher variance formula.

| ID | Prediction |
| --- | --- |
| P1d | **No frequency bias from majority-rule inheritance:** at both *p₀*, the mean of *p*(2000) − *p*ᵢ is within ±2 standard errors of 0. |
| P1e | *Nₑ* lies between 0.2*K* and 2*K* (15–148) at both *p₀*. |
| P1f | *Nₑ* at *p₀* 0.1 and 0.5 agree within a factor of 1.5. (12 replicates give wide CIs. If the CIs overlap but the point estimates differ by more than 1.5×, this is scored "inconclusive", not "passed".) |

## Not decided by this protocol

- How *Nₑ* depends on world area (E1 at 384²). That runs only if E1b passes P1d.
- The fixation test E3 uses E1b's *Nₑ* and E2's *s*. Its protocol is written after both.

## Files

`run_e1.py ARM WORLD_SEED RNG_SEED [TU]` appends to `e1.jsonl`. `analyse_e1.py` writes
`e1_results.json`.

## Amendments

(none yet)
