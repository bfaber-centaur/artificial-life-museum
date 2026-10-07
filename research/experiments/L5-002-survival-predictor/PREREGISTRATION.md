# L5-002: which early morphometric feature predicts S001 survival across disturbances? (pre-registration)

Lane 5, 2026-10-07. This file is committed **before any feature was computed on a disturbed
state**. Its git commit is the pre-registration timestamp. Later changes go under "Amendments" at
the end and never rewrite this text.

## Question

Lane 4 (L4-001, PR #5) found one sharp survive/die edge for each of four disturbances of S001.
Removed mass alone does not predict the outcome: losing 10% evenly survives, while losing 5% from
the centre kills. **What is the smallest set of `alm.morphometrics` features, measured on the
disturbed state or shortly after, that predicts survive vs die across all four disturbances?**

## Data

- **Runs and labels:** Lane 4's base-condition runs (R = 13, T = 10, N = 128, `ref` engine,
  circular-mean frame). These are `results/coarse.csv` (410 runs) and `results/bisect.csv`
  (80 runs). The label is Lane 4's primary class: **survive** = RECOVERED, **die** =
  anything else. Lane 4's labels are used as they are, and no run is re-classified.
- **States:** for every run, the disturbed state is rebuilt deterministically with Lane 4's own
  code (`run.warm`, `run.get_frame`, `alm.disturb.INTERVENTIONS`) and stepped with the same
  `ref` engine. **Sanity gate:** the rebuilt post-edit mass must match Lane 4's
  `mass_after_edit` to 1e−5 for every run. If any run fails, the analysis stops.
- **Control:** the unperturbed creature (s = 0) at the same t0 and lag.

## Candidate features (fixed now, nothing added later)

All features are measured with `alm.morphometrics` (R = 13) at lag k ∈ {0, 5, 10, 20} steps
after the edit (0, 0.5, 1, 2 time units). Lane 4 reports that dying runs collapse in 3–8 time
units, so every lag is earlier than the typical collapse.

| ID | Feature | Definition |
| --- | --- | --- |
| F1 | mass ratio | mass(k) / mass_control(k) |
| F2 | gyradius ratio | gyradius(k) / gyradius_control(k) |
| F3 | area ratio | occupied_area(k, threshold 0.1) / control's |
| F4 | anisotropy shift | anisotropy(k) − anisotropy_control(k) |
| F5 | elongation-harmonic shift | rotational_harmonics(k)[2] − control's |
| F6 | mass trend | mass(k) / mass(0), for k > 0 only |

That gives 5 × 4 + 3 = 23 candidate features.

## Models (fixed now)

- **Single feature:** a threshold stump. On the training set, choose the direction and cut
  that maximize balanced accuracy. The cut is the midpoint between adjacent sorted training
  values.
- **Pair of features:** logistic regression on the two features, standardized with training
  mean and sd, with L2 penalty 1.0 (scipy optimizer). Predict survive when p ≥ 0.5.
- Nothing larger than a pair is fitted.

## Evaluation (fixed now)

- **Primary: leave-one-intervention-out (LOIO).** For each of I001–I004, train on the other
  three interventions (all their runs) and test on the held-out one.
- **Primary metric:** balanced accuracy on the held-out intervention's **near-edge subset**.
  This subset is all its bisection runs plus, for each phase, the two coarse runs that bracket
  the edge (s_ok and s_fail). The far-from-edge runs are easy and would inflate accuracy, so
  they are reported only as a secondary metric (all held-out runs).
- **Score of a feature or pair:** the minimum near-edge balanced accuracy over the four folds,
  with the mean reported alongside.
- **Selection rule:** if the best single feature scores ≥ 0.90, the answer is that single
  feature. Ties are broken by the smaller lag, then by lower F number. Otherwise, the answer is
  the best pair if it scores ≥ 0.90. Otherwise the answer is "no set of size ≤ 2 predicts across
  disturbances", and that is reported as the result. The top five singles and top five pairs are
  reported either way.
- **Trivial baselines,** reported next to the answer: F1 at lag 0 (post-edit mass, Lane 4's
  failed predictor), and the majority class.
- **Lead time:** for the chosen feature's lag, report how many near-edge **die** runs still have
  mass(k) within Lane 4's ±20% band of the baseline mass. If most of them do, the prediction comes
  before the collapse is visible in Lane 4's own metric.

## Out-of-sample check on an unseen disturbance (fixed now, run after the model is frozen)

**I005, rear deletion:** zero every cell within s·R of the point 0.5 R *behind* the centroid
(c − 0.5 R·ĥ). It uses Lane 4's frame, ref engine, phases t0 = 1000…1004, horizon 2000 and Lane 4's
classifier unchanged. The grid is s = 0, 0.025, …, 1.0 (41 strengths × 5 phases). The selected
model, refit on **all** I001–I004 runs, is applied unchanged to I005. Report balanced accuracy on
all I005 runs and on its near-edge subset, defined as for I001–I004 but with the bracketing
grid points only, since there is no bisection.

I005 is the only new run set. It is generated with Lane 4's code and classifier, so Lane 4's
definitions apply. Lane 4 will be told about it.

## Known risks, stated in advance

- Each intervention has only five phases. Near-edge subsets are about 20 runs per intervention, so
  a balanced accuracy of 0.90 is about two errors.
- The features are correlated (F1/F3, F2/F4). The pair search is exhaustive over the 23 features
  (253 pairs), and that number is part of how the result should be read: the best of 253 pairs is
  optimistically biased. The I005 check is the guard against that bias.
- R = 13 lattice effects (L5-axis-breathing) mean anisotropy-based features may depend on
  heading. All Lane 4 runs share the 68.2° plateau, so that confound is held fixed, not tested.
