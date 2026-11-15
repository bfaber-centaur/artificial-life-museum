# POPGEN E0: census and turnover at carrying capacity (pre-registered protocol)

Research track for the ALIFE 2027 paper, question A ("when does selection beat luck?"), chosen
by Bobby on 2026-11-15. Plan: [`research/paper/alife-2027-plan.md`](../../../paper/alife-2027-plan.md).
**Written and committed before any E0 run.** Later changes go under "Amendments" with a date.
The only code run before this commit was a 100-step speed check (dt 0.1; 2.9 ms/step at 128²,
12 ms/step at 256²). No population was simulated.

## Why this is a gate

Drift and fixation need births and deaths after the world is full. If a full GenomeLenia world
freezes (cells stop dividing and never die), there is nothing for drift or selection to act on,
and E1–E4 must add an explicit death process (the dilution fallback in the plan).

## System

`REPLICATORS/genome.py` GenomeLenia with a **constant rule** (`rule_g` = g_r), no mutation. The
rule is Chan's *division well* (found/213 #84, R 15, T 10) at g_r 0, and the midpoint of the
well→uncontrolled line at g_r 0.5. Every run starts from the catalogue's single cell, as in
`evolve.py`. Seeds 1 and 2 add uniform noise of ±10⁻³ on occupied pixels with that seed, as in
`population.py`.

| Factor | Levels |
| --- | --- |
| World (torus) | 128², 256², 384² |
| Rule g_r | 0, 0.5 |
| Seed | 1, 2 |

That is 12 runs of 5000 tu (50 000 steps each).

## Measurements (fixed now)

- **Cell census.** Every 1 tu, the cells are the peaks of `tree.peaks` (Gaussian σ 4 px, threshold
  0.05) on the field. *n*(t) is the number of peaks.
- **Tracks.** Peaks are linked with `tree.link` and `tree.build_tree` and their constants as
  merged (LINK 8, GAP 3, BIRTH 30, MINLIFE 10 frames). A **birth** is a confirmed division
  segment end. A **death** is a segment that ends `vanished`.
- **Window.** W = [3500, 5000] tu. *K* is the median of *n*(t) over W. **Stationarity rule:** if
  the least-squares trend of *n* over W changes *n* by more than 10% of *K* across the window, that
  run is extended to 8000 tu and W becomes [6500, 8000]. This is decided by the rule, not by
  hand.
- **Turnover.** *r* = (births in W) / (*K* × 1.5) per 1000 tu, which is the fraction of the
  population replaced per 1000 tu. Deaths in W are reported the same way.
- **Mass.** Total mass and mass per cell at *K*.
- **Snapshots.** The field is saved every 100 tu (uint8, outside the repo) for validation and
  figures.

## Tracker validation (before any count is used)

For each world size at g_r 0, seed 1, take the frames at t 1000, 3000 and 5000. Overlay the
peaks on the field and **count the cells by eye** from the image without the overlay first.

- **Pass:** the peak count is within 5% of the eye count in all 9 frames.
- **Fail:** σ is re-chosen on these frames (amendment, dated) and the census is recomputed from
  saved data before any prediction below is scored.

## Predictions

| ID | Prediction | Scored as |
| --- | --- | --- |
| P0a | *K* is proportional to world area: *K*/area agrees across 128², 256², 384² within 15% (for each g_r, seed-mean). | (max − min)/mean of *K*/area ≤ 0.15 |
| P0b (**gate**) | There is turnover at *K*: *r* ≥ 0.05 per 1000 tu in every run. | all 12 runs |
| P0c | Births and deaths balance at *K*: \|births − deaths\| in W ≤ 20% of births (or ≤ 3 events, whichever is larger). | per run |

**What follows from each outcome.**

- P0b passes: E1 uses the unmodified rule. Generation time at *K* (≈ 1/*r*) sets E1/E3 run
  lengths.
- P0b fails in all runs (frozen world): E1–E4 add a dilution death process, with a protocol
  amendment, and Bobby is told (decision point 2 in the plan).
- P0b fails in some runs only (e.g. g_r 0 freezes, g_r 0.5 does not): E1 uses only the
  conditions that pass, and the paper reports where turnover stops.

No claim enters `claims.md` from E0 until its PR merges.

## Files

- `run.py N G_R SEED [TU]` appends one record to `e0.jsonl` (census series, per-frame peaks
  compressed to a file outside the repo, hashes).
- `analyse.py` computes *K*, *r*, deaths, the stationarity rule and the P0 table from the saved
  peaks.
- `validate.py` makes the overlay sheets for the eye count.

## Amendments

(none yet)
