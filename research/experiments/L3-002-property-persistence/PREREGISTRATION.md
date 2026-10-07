# L3-002: Which specimen properties persist as R and T are refined? (pre-registration)

Lane 3 (Numerical Red Team), Night 1, numerical-ecology expedition. Written and committed
**before any run of this experiment**. The commit that adds this file is the pre-registration
timestamp. Later changes go under "Amendments" with a reason; the original text is not edited.

## Question

For each registered specimen (S001, S101, S102, S103), which of its catalogued properties are
**continuum-stable** (the same as the discretisation is refined), which are **discretisation-
biased** (they exist at every resolution and timestep but the baseline R = 13, T = 10 value is
off by more than 2%), and which are **finite-resolution-only** (they disappear or change kind
under refinement)?

Finite-resolution behaviours are legitimate observations of the R = 13, T = 10 system. This
test does not delete them; it labels them, so dossiers, claims and museum exhibits can say
which numbers describe "Lenia" and which describe "Lenia on this grid with this step".

## Why this test, and what it is not

Night 0 measured S001 under T and R changes (C009, C014, C016) and Lane 6 measured S101–S103
at three settings each (dossier tables, C039, C042). No one has put all four specimens on the
same refinement ladder with one pre-fixed classification rule. This test does that and nothing
more. It does not search rules (μ, σ), does not apply disturbances, and does not study the
coexistence band; those belong to the attractor-geography expedition (Lane 6).

## Prior literature (from the archivist, via the coordinator)

- Chan 2019 (arXiv:1812.05433v3), Fig. 7(c–d): at R = 13, mass falls, speed rises and the
  survival niche widens as T grows. This matches C009 and predicts S001's speed label.
- Chan 2019, Fig. 7(a–b): statistics are R-invariant over R = 9–55, but averaged over 300 steps.
  This test uses a fixed time window instead, and per-specimen labels.
- Davis 2024 (excerpt only) studies dissolution under dt and resolution changes, but for the
  Gaussian-family Orbium, not S001's poly/poly rule. Not directly comparable.

## Fixed inputs

| Item | Value |
| --- | --- |
| Engine | `alm_check` (Lane 3 independent stepper), FFT path, float64, periodic torus |
| Specimens and rules | S001 and S101: R-ladder base 13, μ 0.15, σ 0.015. S102 and S103: μ 0.155, σ 0.020 (coexistence rule). All: β [1], poly core, poly growth, Euler + hard clip [0, 1] |
| Seeds | `research/specimens/<id>/initial-cells-u8.csv` (S001: catalog cells), level/255, centred placement |
| Resolution change | integer zoom only: R = 13k for k = 1, 2, 3, seed upscaled by k×k **block replication** (nearest neighbour, exact; no interpolation choice) |
| World | N = 128k (S001, S102, S103) or 192k (S101), so the world is the same size in R units |
| Horizon | 300 time units. Statistics window: t ∈ [100, 300] |
| Randomness | none |

### Conditions (7)

| ID | R | T | Purpose |
| --- | --- | --- | --- |
| B | 13 | 10 | baseline (all dossier numbers) |
| T20, T40, T80 | 13 | 20, 40, 80 | timestep ladder → Δt → 0 extrapolation |
| R26, R39 | 26, 39 | 10 | resolution ladder |
| C | 26 | 40 | corner: are the T and R effects separable? |

28 runs in total (4 specimens × 7 conditions).

## Properties (fixed now)

Measured on every 1-step sample in the window unless stated.

| ID | Property | Definition | Applies to |
| --- | --- | --- | --- |
| P1 | persistence | mass ΣA/R² > 0.01 at t = 300 **and** the P2 class at t = 300 equals the specimen's registered class | all |
| P2 | phenotype class | from window means: **glider** if net speed ≥ 0.2 R/tu; **circler** if net speed < 0.05 and path speed ≥ 0.2; **static** if path speed < 0.001; **other** otherwise. S101's registered class is glider with mass ≥ 1.8× S001's mass at the same condition | all |
| P3 | mean mass ΣA/R² | window mean | all |
| P4 | mean gyradius / R | about the periodic centroid, window mean | all |
| P5 | net speed (R/tu) | window net centroid displacement / 200 tu / R | S001, S101 |
| P6 | turning rate (°/tu) | mean absolute rate of change of the 1-tu velocity direction | S102 |
| P7 | path speed (R/tu) | mean |1-tu centroid displacement| / R | S102 |
| P8 | relative mass fluctuation | window sd(mass) / mean(mass) | all except S103 |
| P9 | exact fixed point | final state bitwise equal to the placed seed | S103 |

Not measured: heading (already shown lattice-selected, C011–C013) and mass-oscillation period
(C003–C006).

Net and path speeds use per-step wrapped centroid displacements, summed (no aliasing).

## Classification rule (fixed now)

For each continuous property X (P3–P8) of a specimen that persists (P1) in all seven conditions:

- **Timestep limit** X∞ = 2·X(T80) − X(T40) (first-order Richardson; Euler is first order).
  Timestep error e_T = |X(B) − X∞| / |X∞|.
- **Resolution error** e_R = |X(B) − X(R39)| / |X(R39)|.
- **Converged** if |X(T80) − X(T40)| ≤ ½·|X(T20) − X(B)| (shrinking in T) **and**
  |X(R39) − X(R26)| ≤ ½·|X(R26) − X(B)| or |X(R39) − X(R26)| / |X(R39)| ≤ 0.5% (shrinking or
  already flat in R).

Labels:

1. **CONTINUUM-STABLE**: converged, e_T ≤ 2% and e_R ≤ 2%.
2. **DISCRETISATION-BIASED (T)** or **(R)** or **(T, R)**: converged, and e_T and/or e_R > 2%.
   The label names which.
3. **NOT-CONVERGED**: the convergence test fails. Reported with all values; no limit is quoted.
4. **FINITE-RESOLUTION-ONLY**: applies to the specimen as a whole when P1 fails at any
   refined condition (T20, T40, T80, R26, R39 or C). Its continuous properties are then
   reported per condition but not labelled.

P9 (S103) is reported as yes/no per condition. P8 is labelled with an absolute floor: if
P8 < 1e−3 at R39 and T80 the label is "vanishes with refinement" regardless of e_T and e_R.

**Separability** (reported, not used for labels): predicted X(C) = X(T40) + X(R26) − X(B);
the corner is "separable" if |X(C) − predicted| / |X(C)| ≤ 1%.

## Expected outcomes (written down so they can be wrong)

- S001: mass and gyradius CONTINUUM-STABLE or near the 2% line; speed DISCRETISATION-BIASED (T)
  at ≈ 16% (C009); mass fluctuation vanishes with refinement (C003).
- S101: same pattern as S001 (its dossier shows 7% speed change T 10 → 40).
- S102: FINITE-RESOLUTION-ONLY at its registered rule (C039 says it dies at R 26).
- S103: P9 yes at every T (C042); unknown at R 39.

## Outputs

- `research/traces/lane3/L3-002/<specimen>-<condition>.csv`: one row per run with every
  property, plus the per-tu mass and centroid series as `.npz`.
- `research/experiments/L3-002-property-persistence/README.md`: the persistence table
  (specimen × property → label, with the numbers behind it) and a figure.
- Proposed claims for the coordinator to ledger; nothing is written to `research/claims.md`
  by this lane.

## Run IDs and reproduction

Run ID `L3-002-<specimen>-<condition>` (for example `L3-002-S102-R26`). The runner
`src/alm_check/persistence.py` is added in a later commit, before any run.
Command: `.venv/bin/python -m alm_check.persistence`.

## Amendments

_None yet._
