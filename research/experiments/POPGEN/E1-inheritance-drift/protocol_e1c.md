# POPGEN E1c: unbiased particulate inheritance (pre-registered protocol)

**Written after E1a/E1b's results and before any E1c run.** The only run before this commit was
a 20 tu smoke test of the new mode, whose row was deleted.

## Why

E1b found that majority-rule particulate inheritance ("part") is **not neutral**. With p₀ 0.1,
the rare neutral type shrank in 12 of 12 replicates (mean Δp −0.078 ± 0.012). In E1a, a single
neutral cell was lost in 12 of 12. Majority rule penalises a type wherever it is the local
minority, at every cell boundary. That is positive frequency dependence, like surface tension.
It is built into the inheritance rule, not into Lenia, and it would bias any fixation test.

## Change

Mode **"stoch"**: new matter is type 1 with probability L̂ (the neighbourhood's mass-weighted type
share), drawn fresh for each pixel at each step. The expected type of new matter therefore
equals the local share: rare types are not penalised in expectation, and labels stay 0 or 1.
Everything else is as in E1a/E1b: same starting worlds, same cells chosen, same lengths, same
estimators (τ 183 tu, *K* 74). The random stream for each run is seeded with 1000 × world seed
+ rng seed.

| Arm | As | Replicates |
| --- | --- | --- |
| s+ | part+ (one δ +0.2 cell) | 12 |
| s0 | part0 (one neutral cell) | 12 |
| sdrift0.5 | drift0.5 | 12 |
| sdrift0.1 | drift0.1 | 12 |

## Predictions

| ID | Prediction |
| --- | --- |
| P1c-a | **The bias is gone.** At both p₀, the mean of *p*(2000) − *p*ᵢ is within ±2 SE of 0. |
| P1c-b | **Selection is still visible.** More s+ replicates grow than s0 replicates. |
| P1c-c | **Neutral single cells are lost at about the neutral rate.** Over about 16 generations, a neutral lineage started by one of ~74 cells survives with probability of order 2/(generations) ≈ 10–15% (branching-process scale, rough). We predict 1–6 of 12 s0 replicates still present at 3000 tu. (This prediction is coarse. Its job is to catch a large bias like the one in "part", where 0 of 12 survived.) |
| P1c-d | *Nₑ* from sdrift is within 0.2*K*–2*K* at both p₀, and the two estimates agree within 1.5×. |

If P1c-a fails, the stochastic rule is still biased (for example by noise at interfaces), and
E3 waits for an inheritance rule that passes a neutrality test.

## Amendments

(none yet)
