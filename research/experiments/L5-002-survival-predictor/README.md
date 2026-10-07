# L5-002: does an early morphometric feature predict S001 survival across disturbances?

Lane 5, 2026-10-07. Pre-registration: [`PREREGISTRATION.md`](PREREGISTRATION.md), committed in
`ca0783b` before any feature was computed on a disturbed state. Amendment A1 (empty states) was
committed in `b331585`, before any model was fitted.

**Answer: no.** No `alm.morphometrics` feature, and no pair of features, measured within 2
time units of the edit predicts survive vs die across Lane 4's four disturbances. A feature does
separate the outcomes later, but only once the dying creature is visibly collapsing. Near the
edge, a creature that will die and one that will survive have the same bulk shape, to under 1%,
for about 2 time units after the edit.

## Setup (as pre-registered)

- **Data:** Lane 4's L4-001 base-condition runs (S001, R = 13, T = 10, N = 128, `ref`
  engine): 410 coarse + 80 bisection runs. Survive means RECOVERED and die means anything else,
  using Lane 4's labels unchanged. Every disturbed state was rebuilt with Lane 4's own code. The
  sanity gate passed: max |rebuilt − Lane 4| post-edit mass is 5.0e−7, at the CSV's print
  precision.
- **Candidates:** 23 features. These are mass, gyradius and area ratios to the unperturbed
  control, anisotropy and elongation-harmonic shifts, and the mass trend, each at lags 0, 5, 10
  and 20 steps (0–2 time units) after the edit.
- **Models:** single-feature threshold, and two-feature logistic regression.
- **Test:** leave-one-intervention-out (train on three disturbances, predict the fourth). The
  score is balanced accuracy on the held-out disturbance's 30 near-edge runs, taking the worst of
  the four folds. The pass bar was 0.90.

## Result 1 (pre-registered): nothing passes

| Predictor | Worst fold | Mean of folds | Per fold, near-edge (all runs) |
| --- | --- | --- | --- |
| **best single:** area ratio at 2 tu (F3_k20) | **0.70** | 0.80 | I001 0.70 (0.91), I002 0.92 (0.99), I003 0.75 (0.61), I004 0.83 (0.97) |
| 2nd single: anisotropy shift at 2 tu (F4_k20) | 0.53 | 0.72 | |
| post-edit mass (F1_k0, Lane 4's failed predictor) | 0.50 | 0.53 | I001 0.50 (0.83), I002 0.50 (0.94), I003 0.50 (0.50), I004 0.60 (0.94) |
| best pair: anisotropy shift at 0 + area ratio at 2 tu | 0.54 | 0.68 | |

Following the pre-registered selection rule, the answer is "no set of size ≤ 2 predicts across
disturbances". The full ranking is in `results.json`. Because no model was selected, the
pre-registered unseen-disturbance check had nothing to test. I005 was still generated (below).

## Why (exploratory, not pre-registered)

**Edge values** ([`edge_values.md`](edge_values.md)). This compares each feature at the last
survivor with the same feature at the first death, as a mean over the five phases:

| Feature | I001 | I002 | I003 | I004 |
| --- | --- | --- | --- | --- |
| mass ratio at edit | 0.900 / 0.897 | 0.960 / 0.947 | 1.280 / 1.283 | 0.918 / 0.914 |
| mass ratio at 2 tu | 0.999 / 0.999 | 0.987 / 0.561 | 0.992 / 0.991 | 0.994 / 0.991 |
| area ratio at 2 tu | 0.851 / 0.811 | 0.975 / 0.684 | 0.868 / 0.868 | 0.861 / 0.841 |
| gyradius ratio at 2 tu | 1.017 / 1.029 | 0.992 / 0.866 | 0.999 / 0.999 | 0.994 / 0.997 |

For uniform attenuation, frontal addition and the port cut, the run that will die has
**regrown to 99% of control mass by 2 tu**. It is indistinguishable from the survivor to within
0.3%. The edge value of every feature also moves from one disturbance to another by more than
the survive/die gap within a disturbance. That is why a cut learned on three disturbances misses
the fourth. Central deletion (I002) is the exception: it kills fast, and by 2 tu its dying run
is already at 56% mass.

**Divergence time** ([`divergence.md`](divergence.md)). Each edge pair (last survivor, first
death) was stepped side by side for 400 steps:

| Disturbance | First step where gyradius differs > 1% | First step where mass differs > 1% |
| --- | --- | --- |
| I001 attenuation | 20 | 23–24 |
| I003 frontal addition | 25–27 | 25–40 |
| I004 port cut | 21–24 | 24–34 |
| I002 central deletion | 6–7 | 0 (the two edits delete different pixel sets) |

The earliest possible window for any bulk-morphometric predictor opens at about 2 tu. Lane 4
reports that collapse is underway by 3–8 tu.

**A late rule works, but it only detects the collapse.** Re-running the same analysis with lags
30, 40 and 60 steps (`features-exploratory-lags.csv`, `results-exploratory-lags*.json`) gives one
clean rule: **mass at 6 tu ≥ 98% of the unperturbed control → survives.** It scores 1.00 in every
held-out fold. It was then frozen and applied to the unseen rear-deletion disturbance I005, where
it also scores 1.00 on all 205 runs. But at 6 tu, 64 of the 68 near-edge dying runs have already
lost more than 20% of their mass. The rule detects a collapse that has already started. At 3 tu
(lag 30), 31 of 68 dying runs are still within ±20% of baseline mass.

## The unseen disturbance I005 (new data)

**Rear deletion:** zero a disc of radius s·R centred 0.5 R behind the centroid (`i005.py`).
Lane 4's runner and classifier were used unchanged (`gen_i005.py`, `i005-runs.csv`). The grid is
s = 0…1 in steps of 0.025, across 5 phases, for 205 runs.

S001 survives s ≤ 0.15 at every phase (except s = 0.15 at t0 = 1003) and dies at s ≥ 0.175. In
mass terms, the last survivors lost 4.6–5.7% of their mass and the first deaths lost 5.6–7.6%,
depending on phase. This puts rear deletion close to central deletion (dies at 5.2%) and below
the port cut (8–9%). All classes are
RECOVERED or DIED, and there are no intermediate outcomes. The edge has not been bisected.

## Proposed claims (for the coordinator)

1. **No early bulk-morphometric predictor of S001 survival transfers across disturbances.** No
   single feature and no pair from the 23 pre-registered `alm.morphometrics` features at 0–2 time
   units after the edit reaches 0.90 held-out balanced accuracy near the edge in
   leave-one-disturbance-out tests. The best is the area ratio at 2 tu, with a worst fold of 0.70.
   OBSERVED (pre-registered negative). Single engine (`ref`), single resolution (R = 13).
2. **Near the edge, the creature that will die looks like the survivor until about 2 time units
   after the edit.** For I001, I003 and I004 the edge pair differs by < 1% in mass and gyradius
   for the first 20–27 steps, and the dying run regrows to 99% of control mass first. OBSERVED,
   exploratory. This fits Lane 4's report that collapse time grows logarithmically near the
   edge, which suggests an unstable edge state. The outcome is carried by a small unstable
   mode, not by bulk morphology.
3. **S001's edge under rear deletion lies between about 5% and 7% mass loss** (I005, 5
   phases, coarse grid only). OBSERVED. New disturbance; Lane 4's code and classifier.

## Next experiment, chosen for information value

Find the unstable direction itself. Take the difference between the edge-pair states at a fixed
lag, average it over phases and disturbances, and test whether the projection of a disturbed
state onto that direction at lag 0 predicts the outcome across disturbances. If it does, the
predictor is "distance from the edge state along its unstable mode". That would be an
interpretable feature, but it is not a morphometric one.

## Reproduction

```bash
P=research/experiments/L5-002-survival-predictor
.venv/bin/python $P/measure.py                    # features.csv (pre-registered lags), about 15 s
.venv/bin/python $P/analyze.py                    # results.json, pre-registered result
.venv/bin/python $P/edge_values.py                # edge_values.md
.venv/bin/python $P/divergence.py                 # divergence.md
.venv/bin/python $P/gen_i005.py                   # i005-runs.csv, about 2.5 min on 4 cores
.venv/bin/python $P/measure.py --extra $P/i005-runs.csv --out $P/features-i005.csv
.venv/bin/python $P/measure.py --lags 0,30,40,60 --out $P/features-exploratory-lags.csv
.venv/bin/python $P/measure.py --extra $P/i005-runs.csv --lags 0,30,40,60 --out $P/features-i005-exploratory-lags.csv
.venv/bin/python $P/analyze.py --features $P/features-exploratory-lags.csv --tag=-exploratory-lags \
    --i005 $P/features-i005-exploratory-lags.csv
```

These scripts need Lane 4's `alm.disturb` and `L4-001-disturbance-battery/run.py` (PR #5).

## Caveats

- Each disturbance has five phases, so 30 near-edge runs per fold. A worst fold of 0.70 is
  several errors, not one.
- The bisection runs sit within 1/256 in strength of the edge. That is a demanding test set:
  any small systematic offset of a transferred threshold fails it.
- One engine, one resolution, one heading plateau (68.2°). The heading-dependent anisotropy at
  R = 13 (L5-axis-breathing) is held fixed here, not tested.
- The exploratory 6 tu rule was found after looking at the data. Its unseen-disturbance score
  (I005, 1.00) is genuine out-of-sample evidence, but only for a collapse detector.
