# POPGEN E2: does diffusion theory predict which single mutants take hold? (pre-registered protocol)

**Written before any E2 run.** It uses only the E1c data already on this branch to fix *D*.
This is the plan's E3 fixation test, moved earlier and done in time units. See the correction
in [`../E1-inheritance-drift/README.md`](../E1-inheritance-drift/README.md).

## Theory

For a two-type population with **unbiased particulate inheritance** ("stoch", E1c), we assume the
mutant share *p* follows the Wright–Fisher diffusion in time:

    dp = sₜ p(1−p) dt + sqrt(p(1−p)/D) dW

- *D* = *Nₑ*τ (tu) sets the strength of drift. It is fixed now from the pooled E1c neutral runs
  (sdrift0.5 and sdrift0.1, 24 runs): F(t) = 1 − exp(−t/*D*) fitted on t ∈ (0, 2000], giving
  **D = 61,659 tu**. A 2000-resample bootstrap over the 24 runs gives a CI, which is reported and
  propagated.
- *s*ₜ(δ) (per tu) is measured independently in Phase A.

**No tracker, no generation time, no free parameter is fitted to the Phase B outcomes.**

## Phase A: selection coefficients (head-to-head)

Arms "h{δ}": stoch mode, residents g₀ 0.5, mutants g₀ + δ. Every cell is mutant with probability
0.5. δ ∈ {0.02, 0.05, 0.1, 0.2}, 4 replicates each (worlds 1, 2 × rng 301, 302), 1500 tu.
*s*ₜ(δ) = the mean over replicates of the least-squares slope of logit *p*(t) on t ∈ [100, 1500].

## Phase B: single mutant cells

Arms "m{δ}": as E1c's s+, but δ ∈ {0.02, 0.05, 0.1}. That gives 24 replicates per δ: worlds 1, 2 ×
12 cell choices (rng 1–12). Runs last 3000 tu. E1c's s+ (δ 0.2, 12 runs) and s0 (δ 0, 12 runs)
are included as two more conditions.

**Outcome.** A replicate is "taken hold" if its mutant share is ≥ 0.05 at 3000 tu.

**Prediction.** For each δ, simulate the diffusion above (Euler–Maruyama, dt 1 tu, absorbing at
0 and 1, 20,000 paths), starting at the replicates' mean realised starting share, with *D* and
*s*ₜ(δ). That gives the predicted probability π(δ) of share ≥ 0.05 at 3000 tu. For δ 0, *s*ₜ = 0.

| ID | Prediction |
| --- | --- |
| P2a | *s*ₜ increases with δ (strictly, across the four δ). |
| P2b | **Diffusion theory predicts take-hold.** For each of the 5 conditions (δ 0, 0.02, 0.05, 0.1, 0.2), the observed count lies inside the central 95% binomial interval of Binomial(n, π(δ)). Pass if all 5 do. "Partial" if 4 do. |
| P2c | The observed take-hold fraction increases with δ (Spearman ρ > 0 over the 5 conditions). |

**If P2b fails**, the direction matters. Too many take-holds means drift in Lenia is weaker for
rare types than the neutral-share estimate of *D* says (for example, because cells reproduce
with low variance). Too few means the opposite. Either is reported as found.

## Files

`run_e2.py ARM WORLD_SEED RNG_SEED` (reuses `../E1-inheritance-drift/run_e1.py`'s machinery) →
`e2.jsonl`. `analyse_e2.py` → `e2_results.json`, with `D` and its bootstrap computed from
`../E1-inheritance-drift/e1.jsonl`.

## Amendments

(none yet)
