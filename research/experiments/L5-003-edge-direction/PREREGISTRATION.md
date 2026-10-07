# L5-003: does one coordinate, along the edge state's unstable direction, predict S001 survival? (pre-registration)

Lane 5, 2026-10-07. This file is committed **before any state was projected onto any direction**.
Its git commit is the pre-registration timestamp. Changes go under "Amendments" at the end.

## Motivation

L5-002 found that no bulk morphometric predicts survival across disturbances. Near the edge, the
run that will die and the run that will survive match to < 1% for about 2 time units, then split.
Lane 4 reports that collapse time grows logarithmically near the edge. Both point to an **edge
state**: a saddle with one unstable direction u, whose sign decides survival.

**Hypothesis H1.** All four disturbances funnel through the same edge state. If so, the coordinate
of a disturbed state along u, estimated from three disturbances, predicts survival for the fourth,
and for an unseen fifth (I005).

## Data

- **I001–I004:** the same 490 L4-001 runs, labels and rebuilt states as L5-002 (`ref` engine, R = 13,
  T = 10, N = 128). The sanity gate is repeated.
- **I005** (rear deletion, from L5-002): the 205 coarse runs, plus a **new bisection**. For each
  phase, bisect the I005 coarse bracket to a width of 1/256 in s with Lane 4's runner and classifier
  unchanged, stopping early if the deleted pixel set stops changing (Lane 4's I002 rule). This set is
  generated and labelled before any projection is computed.

## Comoving frame (fixed now)

The creature translates, so states are compared in its own frame. Each state is translated so its
centroid (`alm.morphometrics.centroid`) sits at grid position (64, 64). The translation is an
exact periodic **Fourier sub-pixel shift**, not interpolation. No rotation is applied: every L4-001
and I005 run sits on the same 68.2° lattice plateau, so headings already agree. Call the shifted
state Â.

## The coordinate (fixed now)

At lag k ∈ {0, 5, 10, 20, 30} steps after the edit:

- **Edge pairs.** For each (disturbance, phase), take the final bisection bracket from coarse +
  bisection runs: the highest-strength survivor S and the lowest-strength death D.
- **Direction.** u_k = the normalized mean, over the training disturbances' edge pairs, of
  (D̂_k − Ŝ_k) / ‖D̂_k − Ŝ_k‖. This is the direction in which the edge pairs split at lag k.
- **Coordinate.** c_k(A) = ⟨Â_k − Ĉ_k, u_k⟩, where C is the unperturbed control at the same t0 and
  lag.
- **Classifier.** A threshold stump on c_k, fitted on the training runs exactly as in L5-002 (cut
  and direction maximize training balanced accuracy). Empty states are predicted "die", as in
  L5-002 amendment A1.

## Null coordinate (fixed now)

c⁰_k(A) = ⟨Â_k − Ĉ_k, Ĉ_k / ‖Ĉ_k‖⟩. This is the projection onto the creature's own shape, which is
roughly a mass deficit. It is scored the same way. If the edge direction does not beat this, it
carries no information beyond "how much creature is left".

## Evaluation (fixed now)

- **Primary: leave-one-disturbance-out over I001–I004**, as in L5-002. Within each fold, both u_k
  and the cut come from the three training disturbances only. The score is the worst-fold
  balanced accuracy on the held-out near-edge subset (bisection runs plus the two coarse bracket
  ends per phase).
- **Lag selection:** the smallest k whose worst-fold score is ≥ 0.90. If none qualifies, H1 fails
  at every pre-registered lag, and that is the result. The mean-over-folds score and the
  all-runs score are reported alongside.
- **Held-out I005:** with the selected k, refit u_k and the cut on **all** I001–I004 runs, freeze
  them, and apply them to I005. Report balanced accuracy on all I005 runs and on I005's near-edge
  subset (its bisection runs plus the coarse bracket ends).
- **Lead time:** for the selected k, the number of near-edge dying runs whose mass is still within
  Lane 4's ±20% baseline band, as in L5-002.
- **Secondary diagnostics,** reported and not used for selection:
  - the mean pairwise cosine similarity of the per-disturbance edge-pair directions at each lag.
    This is high if H1 is true.
  - the null coordinate's scores.

## Known risks, stated in advance

- I002 edge pairs differ by whole pixel shells, so their difference may be dominated by the
  edit rather than by u at small k.
- The bisection survivor and death are close in s but not on the separatrix, so u_k is only an
  estimate. Five phases per disturbance means 15 pairs per training fold.
- A single linear direction can only work if the trajectories really share one saddle. If each
  disturbance has its own edge state, H1 is false, and the cosine diagnostic should show it.
