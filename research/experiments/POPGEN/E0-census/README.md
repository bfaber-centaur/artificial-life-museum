# POPGEN E0: census and turnover at carrying capacity (results)

Protocol: [`protocol.md`](protocol.md), committed (2ffad00) before any run. Runner `run.py`, analysis
`analyse.py` → [`e0_results.json`](e0_results.json), validation sheets `validate.py`. The
exploratory tracer check is `tracer.py` → [`tracer.jsonl`](tracer.jsonl). Per-run census series
are in [`e0.jsonl`](e0.jsonl). The big per-frame peak files are kept outside the repo
(`$POPGEN_OUT`) and are re-created by `run.py` (hashes in `e0.jsonl`).

    for N in 128 256 384; do for g in 0 0.5; do for s in 1 2; do python run.py $N $g $s; done; done; done
    python run.py 128 0 2 8000; python run.py 256 0 2 8000; python run.py 128 0.5 1 8000   # stationarity rule
    python analyse.py
    python tracer.py 256 0.0 1; python tracer.py 256 0.5 1                                # exploratory

## Verdict

| Prediction | Result |
| --- | --- |
| **P0b (gate): turnover ≥ 0.05 per 1000 tu in every run** | **Passes, by a wide margin.** *r* is 1.5–1.8 per 1000 tu for *division well* (g_r 0) and 5.1–9.4 for g_r 0.5, in all 12 runs. A full world is far from frozen. |
| P0c: births balance deaths at *K* | **Passes** in all 12 runs (e.g. 384², g_r 0.5: 1313 births, 1312 deaths). |
| P0a: *K* ∝ area within 15% | **Passes for g_r 0** (*K* per 10⁴ px² = 7.6, 8.2, 8.3; spread 8%). **Fails for g_r 0.5** (13.4, 11.3, 11.2; spread 18%). Both failures come from the 128² world, which holds only 12–26 cells. 256² and 384² agree within 1%. |

| | 128² | 256² | 384² |
| --- | --- | --- | --- |
| *K*, g_r 0 (seeds 1, 2) | 12, 13 | 53, 55 | 122, 123 |
| *K*, g_r 0.5 | 18, 26 | 75, 73 | 165, 166 |
| births per cell per 1000 tu, g_r 0 | 1.61, 1.79 | 1.60, 1.54 | 1.55, 1.62 |
| births per cell per 1000 tu, g_r 0.5 | 6.37, 9.38 | 5.81, 5.10 | 5.31, 5.25 |
| mass per cell, g_r 0 | 215, 207 | 210, 208 | 209, 211 |

**What it means.** At carrying capacity a *division well* cell is replaced about every 600 tu,
and a g_r 0.5 cell about every 190 tu. There is plenty of birth and death for drift and
selection to work on, so **the dilution fallback is not needed**. E1–E3 should run at 256² or
larger, because 128² holds too few cells to sit at a steady *K*.

**Stationarity rule.** Three runs tripped the 10% trend rule at 5000 tu and were extended to
8000 tu as pre-registered. 256² g_r 0 seed 2 became stationary (trend 0.6%). The two 128² runs
still tripped it (trends 21% and 19%). With *K* = 13–18, 10% is 1–2 cells, so the rule is
reacting to noise in a tiny population, not to growth. Those two runs are reported as
non-stationary. They do not change any verdict, since P0b passes by a factor of 30 in them too.

## Tracker validation (partial; amendment A1)

The protocol asks for eye counts on 9 frames before counts are used. **This was done only
partly.** At 128², t 5000, the eye count is 11–12 cells against 12 peaks. At 256², t 5000, about
3 of 49 peaks are **cells caught mid-division** (one membrane, two lobes, two peaks), and 1–2 cells
cut by the image edge have their peak on the other side of the seam. That puts the agreement at
about ±6%, so the strict 5% criterion is not met. Counting the 120-cell 384² frames reliably by
eye at this resolution was not attempted.

So *K* carries about ±6% uncertainty, which is enough to matter for P0a's 15% margin at 128² but
not for the gate. The births in P0b could in principle include peaks that split for longer than
MINLIFE 10 tu without a real division. That is why we ran the tracker-free check below.

## Exploratory: a neutral tracer shows the full world mixing, and exposes blending inheritance

Not pre-registered. Starting from the 256² full world at t 5000 (seed 1), we set g = 1 on the
left half and 0 on the right. With a constant rule, g is only a tracer. If the world were frozen,
the tracer would stay in its half.

| g_r | tracer mass in the right half, t 100 / 500 / 1000 | share of all mass with 0.1 < g < 0.9 |
| --- | --- | --- |
| 0 | 0.12 / 0.19 / 0.35 | 0.25 / 0.69 / **0.94** |
| 0.5 | 0.05 / 0.13 / 0.21 | 0.14 / 0.41 / 0.61 |

The tracer spreads, which confirms without the tracker that the world is not frozen.

**But it also shows something that matters more for E1–E3: GenomeLenia inheritance blends.** New
matter takes the mass-weighted average genome of its neighbourhood, so within 1000 tu, 94% of
the matter carries an *intermediate* tracer value rather than 0 or 1. That is Fleeming Jenkin's
1867 objection to Darwin: under blending inheritance a rare variant is averaged away before
selection can act. Our soup ran into the same thing (C076–C077). Kimura's fixation formula
assumes **particulate** inheritance, where an individual is mutant or resident, not 3% mutant.

**Consequence for E1 (to go in its protocol, not done yet).** E1–E3 need a discrete, particulate
label: each pixel carries type 0 or 1, and new matter takes the type of the **mass-majority** of
its neighbourhood instead of the average. The blending rule stays as a comparison arm. "The
same mutant under blending vs particulate inheritance" is a cheap figure that should be in the
paper.

## Amendments

- **A1 (2026-11-15, after the runs):** tracker validation was partial (2 of 9 frames, ±6%), as
  described above. σ was not re-chosen, because the disagreement comes from cells mid-division,
  which no blur width fixes. The paper will define an individual as a tracker peak and report
  the division ambiguity. A full 9-frame count is left to the hostile review of E0.

No claims enter `claims.md` from E0 until this PR merges and the hostile review has read it.
