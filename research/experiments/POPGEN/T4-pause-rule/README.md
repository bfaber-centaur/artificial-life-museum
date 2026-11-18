# POPGEN T4: a dosing rule that actually pauses (results)

Protocol: [`protocol.md`](protocol.md), committed before any T4 run. Runner `run_t4.py`, data
`t4.jsonl` (8 runs, adaptive_sensitive at κ 0.3/0.4 × seeds 1–4), scores `analyse_t4.py` →
`t4_results.json`. Constant and untreated arms are reused from T3 (same pre-treatment states,
asserted by the runner).

## Headline

**The new rule pauses, and it keeps the sensitive cells around, but it does not delay
progression. It makes progression earlier in 7 of 8 pairs.** Switching the drug off when the
*sensitive* mass halves (instead of the total) fixes T3's problem: the drug is on 38–68% of the
time instead of 99–100%. At progression the tumour is less resistant than under constant dosing
in 7 of 8 pairs (median resistant share 0.73 vs 0.98). But each pause lets the sensitive cells
regrow fast enough to push total burden past 1.25 B0 before the drug bites again, so the
pre-registered endpoint is hit sooner (median 479 tu vs 1553 tu).

## Verdicts

| ID | Prediction | Result |
| --- | --- | --- |
| PT4-1 | drug on < 80% of the time in ≥ 6/8 runs | **Pass**, 8/8 (2258–4051 of 6000 tu) |
| PT4-2 | adaptive progresses later than constant in ≥ 5/8 pairs | **Fail**, 1/8 (seed 3, κ 0.4) |
| PT4-3 | lower resistant share at progression in ≥ 5/8 pairs | **Pass**, 7/8 |

## Exploratory (not pre-registered)

The endpoint counts sensitive regrowth as progression, which a clinician would simply treat.
Using instead the first time the **resistant** mass alone exceeds 1.25 B0, adaptive is later in
5 of 8 pairs (κ 0.3: 3/4; κ 0.4: 2/4), and mean burden over 6000 tu is about the same
(1.03–1.14 B0 adaptive vs 0.84–1.12 constant). That is a coin flip, not a win. So in this toy,
competition from sensitive cells is real (T3: untreated tumours keep resistance near 0) but
too weak, or too slow, to hold resistant cells back during a pause.

## What it means

The therapy room now has a clean, honest negative: **adaptive therapy needs more than
"resistant cells exist and sensitive cells compete"**. The competition has to be strong
enough relative to regrowth. A follow-up would measure that competition directly (resistant
growth rate with vs without sensitive neighbours) and sweep it. Not run here.

No claims enter `claims.md` until this PR merges and a hostile review has read it.
