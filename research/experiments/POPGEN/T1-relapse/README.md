# POPGEN T1 and T2: adaptive therapy with immune resistant cells (results)

Protocols: [T1](protocol.md) (amendment A1: doses 0.3/0.4, decided before the main runs) and
[T2](../T2-preexisting/protocol.md) (T1 plus one resistant cell at g 0.3 when treatment starts;
amendment A1 records a smoke test only). Runners `run_t1.py` and `../T2-preexisting/run_t2.py`.
Data: `t1.jsonl`, `../T2-preexisting/t2.jsonl`. Scores: `t1_results.json`, `t2_results.json`.
Each grid is 40 runs: 4 seeds × c {0, 0.3} × κ {0.3, 0.4} × arms. T2's runs were executed twice
by accident (a container restart re-launched the queue). All 40 duplicate pairs had identical
final hashes, and the duplicates were removed.

    python run_t1.py SEED C ; python ../T2-preexisting/run_t2.py SEED C     # SEED 1-4, C 0 / 0.3
    python analyse_t1.py ; python ../T2-preexisting/analyse_t2.py

## Verdict

| Prediction | T1 (no resistance at start) | T2 (resistant clone at start) |
| --- | --- | --- |
| Constant dosing relapses with mostly resistant matter (c 0, ≥ 6/8) | **Fail**, 4/8. All four are at κ 0.4. At κ 0.3, constant dosing progresses within 107–280 tu on *sensitive* matter: the dose is too weak to hold the tumour at all. | **Pass**, 6/8. Resistant share at progression 0.53–0.87. |
| With the cost of resistance, adaptive beats constant (c 0.3, ≥ 5/8) | **Fail**, 0 better, 4 worse, 4 tied. | **Fail**, 0 better, 4 worse, 4 tied. |
| Without the cost, adaptive does not beat constant (c 0, ≤ 4/8) | **Pass**, 2 better, 3 worse, 3 tied. | **Pass**, 1 better, 1 worse, 6 tied. |
| T2 only: untreated tumour shrinks the clone with the cost, not without | | **Pass.** At c 0.3 the clone falls from 0.10–0.19 to 0–0.014 of the matter in 4/4 seeds. At c 0 the resistant share at 6000 tu is 0.14–0.46. |

**What happened with the cost switched on (c 0.3).** Constant dosing **eradicated** the tumour
in 8/8 runs in T1 and in 6/8 in T2. The other two T2 runs (κ 0.4, seeds 2 and 3) left a remnant
that is 100% resistant and sits at 0.17 B0 for 6000 tu without regrowing. Adaptive dosing never
eradicated at κ 0.3: it ended with a smaller, often mostly resistant tumour (resistant share
0.71–0.89 in T2). So in this toy, the competition that adaptive therapy needs also makes
resistant cells too weak to relapse, and maximum-tolerated-dose cures them.

At c 0, 6 of 8 T2 pairs are ties because the adaptive arm never switches off. The drug never
halves the burden, so adaptive equals constant.

## Why adaptive therapy cannot win here: the "crowding cost" is a density tax

`therapy.crowding_cost` (C122) measures crowding with a 4 px Gaussian. A *division well* cell is
about 30 px across, so a cell's **own** matter fills its neighbourhood: crowd ≈ 1 inside any
cell, whether or not it has neighbours. The "cost of resistance" is therefore not competition. It
is a flat tax of about 0.3·(1 − g) per tu on resistant matter, everywhere it is dense, including
a lone remnant in an empty world. That is why the T2 remnants never regrow, and why the cost
helps constant dosing rather than adaptive dosing.

**Next step (not done):** measure crowding at the scale of neighbouring cells. For example, use
a Gaussian of σ ≥ 30 px, or local mass with the cell's own peak region excluded. Then rerun T2,
so that a lone resistant cell pays nothing and only a resistant cell surrounded by sensitive
tissue is suppressed. That is the regime in which adaptive therapy theory predicts a benefit.
The particulate inheritance from E1c should also be used, since blending dilutes the resistant
clone in T2's untreated arm.

No claims enter `claims.md` until this PR merges and a hostile review has read it.
