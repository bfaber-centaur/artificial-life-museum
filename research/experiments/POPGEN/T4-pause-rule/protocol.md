# POPGEN T4: an adaptive rule that can pause (pre-registered protocol)

**Written after T3's results and before any T4 run.**

## Why

In T3 everything adaptive therapy needs was present: resistant relapse under constant dosing
(8/8) and suppression of the clone when untreated (4/4). But the Zhang et al. 2017 rule (stop
when the *total* burden halves) never paused, because the immune clone kept the burden above
B0/2. The drug was on 99–100% of the time, so the comparison was empty.

## Change from T3 (the only one)

A new adaptive rule switches on the **sensitive** burden S (matter with g ≥ 0.4, the type the drug
can kill):

- **off** when S ≤ ½ S₀, where S₀ is the sensitive burden when treatment starts;
- **on** again when the *total* burden ≥ B0 (as in Zhang's rule).

In a clinic this would need a marker of sensitive cells (for example ctDNA of a sensitive clone).
Here it is read directly. Everything else is T3: crowding σ 30 px, c 0.3, one resistant cell at
g 0.3, immune below 0.4, κ {0.3, 0.4}, seeds 1–4, 128², 6000 tu. The constant and none arms are
**reused from T3** (`../T3-neighbour-competition/t3.jsonl`). Their pre-treatment states are
identical: same seed, same code path. This is checked by asserting that T4's grown state hashes
to the same B0 and t_start as T3's. That gives 8 new runs.

## Predictions

Scoring is as in T1–T3. "Adaptive better" means it progresses later than constant, or not at
all when constant does.

| ID | Prediction |
| --- | --- |
| PT4-1 | The rule actually pauses: the drug is on for < 80% of the time in at least 6 of 8 runs. |
| PT4-2 | **Adaptive (sensitive-triggered) beats constant in at least 5 of 8 pairs.** |
| PT4-3 | At progression or at 6000 tu, the adaptive tumour's resistant share is lower than the constant tumour's in at least 5 of 8 pairs. |

The candidate rule is this one only. No second rule will be tried and reported as "the" result.
If PT4-2 fails, that is the answer for this toy.

## Files

`run_t4.py SEED` → `t4.jsonl`. `analyse_t4.py` → `t4_results.json`.

## Amendments

(none yet)
