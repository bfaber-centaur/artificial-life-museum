# POPGEN T3: competition at neighbour scale (results)

Protocol [`protocol.md`](protocol.md) (committed 01c7af9 before any run). Runner `run_t3.py`, data
`t3.jsonl` (20 runs, no duplicates), scores `analyse_t3.py` → `t3_results.json`.

## Verdict

| ID | Prediction | Result |
| --- | --- | --- |
| PT3-1 | Constant dosing relapses with mostly resistant matter in ≥ 4/8 pairs | **Pass, 8/8.** Progression at 235–2657 tu, with resistant share 0.63–1.00 at progression. With crowding measured at neighbour scale, the resistant remnant regrows once the sensitive cells are gone, which T2 never showed. |
| PT3-2 | Adaptive beats constant in ≥ 5/8 pairs | **Fail.** 2 better, 5 worse, 1 tie. |
| PT3-3 | Untreated tumours hold the clone down in ≥ 3/4 seeds | **Pass, 4/4.** The clone falls from 0.12–0.23 of the matter to 0–0.015. |

**So the toy now has both ingredients adaptive therapy needs.** A resistant clone relapses under
constant dosing, and sensitive neighbours suppress it when untreated. Adaptive dosing still does
not win.

**Why (exploratory, not pre-registered).** The adaptive rule never gets to rest. It stops the
drug only when the burden halves, and the immune clone keeps the burden above B0/2, so the drug
was on for **99–100% of the time** in all 8 adaptive runs (5910–6000 of 6000 tu). The two arms
are nearly the same schedule. Their progression times differ through early chaotic divergence,
not through a treatment effect. Mean burden over the run is 0.84–1.12 B0 for constant and
0.97–1.12 B0 for adaptive, with no consistent winner.

**What a fair test needs next.** It needs a dosing rule that can actually pause against a
partly resistant tumour. For example, pause when the *sensitive* burden halves, or use a fixed
on/off cycle, or use thresholds relative to the burden at nadir. That rule should be
pre-registered before it is tried. Picking a rule after seeing these runs would risk tuning it
to the toy.

No claims enter `claims.md` until this PR merges and a hostile review has read it.
