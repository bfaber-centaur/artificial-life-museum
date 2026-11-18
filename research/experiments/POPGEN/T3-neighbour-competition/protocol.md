# POPGEN T3: competition at the scale of neighbouring cells (pre-registered protocol)

**Written after the T1/T2 results ([`../T1-relapse/README.md`](../T1-relapse/README.md)) and before
any T3 run.**

## Why

In T1/T2 the "crowding cost of resistance" measures crowding with a 4 px Gaussian. That is
smaller than one cell (about 30 px), so it taxes resistant matter for its own density, even a
lone remnant in an empty world. As a result the remnants never regrew and adaptive dosing never
won. Adaptive therapy theory needs a different arrangement: resistant cells that are held back by
**sensitive neighbours** and grow freely once the neighbours are gone.

## Change from T2 (the only one)

`therapy.CROWD_SIGMA` = **30 px** instead of 4 px. Crowd = (local mass, Gaussian σ 30) / carrying
density, clipped to 1. Inside full tissue crowd ≈ 1, as before. Around a lone *division well*
cell it is about 0.2 (estimate: 210 mass over ~2πσ² ≈ 5700 px, against 0.196 per px). Everything
else is as T2: one resistant cell at g 0.3 when treatment starts, immune below g 0.4, c 0.3,
κ {0.3, 0.4}, seeds 1–4, 128², 6000 tu. That gives 4 seeds × (none + 4 treated) = 20 runs. The
c = 0 arms would be identical to T2's c = 0 (crowding is unused there), so they are not rerun.

## Predictions

Scoring is as in T1/T2.

| ID | Prediction |
| --- | --- |
| PT3-1 | **The remnant can now relapse.** Constant dosing progresses, with resistant share > 0.5 at progression, in at least 4 of 8 pairs. |
| PT3-2 | **Adaptive delays it.** Adaptive beats constant in at least 5 of 8 pairs. |
| PT3-3 | **The untreated tumour still holds the clone down.** In at least 3 of 4 seeds, the resistant share at 6000 tu is below its starting share. |

If PT3-1 fails because constant dosing still eradicates (no remnant survives), the toy's
resistant cells are too slow to outgrow the drug's removal of their sensitive descendants. That
outcome is reported as a property of the 213 #84→#83 rule line, not as a test of the theory.

## Files

`run_t3.py SEED` appends to `t3.jsonl`. Scoring uses `../T2-preexisting/analyse_t2.py`'s logic
(`analyse_t3.py`).

## Amendments

(none yet)
