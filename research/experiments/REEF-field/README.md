# REEF-field: settled seeds, isolated controls and the encounter runner

Owner: Field lane of the Coexistence-Reef expedition (branch `reef/field`). Launch packet:
`expedition/reef-launch-2026-10-20` @ `51af137761512d66f7f73d4512e7bbc3b76f5b1f`; mandate
`research/expeditions/2026-10-20-reef-launch.md`. This lane writes only this directory.

Rule throughout (unless a later dated entry says otherwise): poly kernel, poly growth, β [1],
μ 0.155, σ 0.020, R 13, T 10, Euler + hard clip, float64, periodic torus, N 256. Engine:
`alm.lenia.Lenia` unchanged. `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`, at most two
simulation processes.

## Decision log (each entry committed before the runs it governs)

### F-001 (2026-10-21 ~06:05Z): glider settling procedure and transient test

No coexistence-rule Orbium *state* is archived (L6-field `bistab-*.npz` hold 128² finals, not a
documented seed with a settle record), so the S001 catalog cells are settled under the fixed rule.

- Seed: `alm.specimens.load("S001").cells` (O2u, 20×20 levels), placed centred on N 256 with
  `Specimen.place` (offset (118, 118)). Only the rule changes: μ 0.150→0.155, σ 0.015→0.020.
- Settle: steps 0–1000 (100 tu). Assess: steps 1000–2000 (100 tu). Per-step mass (Σ/R²) and
  unwrapped periodic centroid (`alm.morphometrics.centroid`, min-image increments). Components
  (A > 0.1, 8-connected, torus-aware, L6 `field.components`) every 10 steps.
- Acceptance as a moving glider over the assessment window: alive, exactly one component at
  every sample, mass rsd < 1%, least-squares speed > 0.1 R/tu, straightness (net / path length of
  the per-tu track) > 0.99.
- Transient test, comparing the two 50-tu halves of the assessment window: relative change of
  mean mass > 0.2%, relative change of fitted speed > 0.5%, or change of fitted heading > 0.5°.
  If any trips, extend **once** to 500 tu total: settle to step 4000, assess steps 4000–5000 with
  the same criteria. If it still trips, report the drift as a caveat; do not retune.
- The exported settled seed is the state at the end of the (final) assessment window.

### F-002 (same commit): snapshots and S103

- Orbium has no known intrinsic oscillation; its mass wobble is a grid-crossing artifact (S001
  dossier). Two snapshots are therefore **named elapsed-time snapshots**, not phases, unless the
  periodicity analysis below finds a recurrence up to translation that is not explained by
  grid crossing. Snapshot `GA` = the settled seed (end of assessment). Snapshot `GB` = the state
  k steps later, k ∈ 1..10 chosen to maximise the torus distance of the fractional centroid
  (sub-cell lattice offset) from `GA`'s. Both are re-centred by an **integer** roll so the
  centroid lies within half a cell of the grid centre; the roll is recorded.
- Periodicity analysis (reported, not used to choose): dominant period of mass over the
  assessment window and the grid-crossing periods 1/|vx|, 1/|vy| in steps.
- S103: `alm.specimens.load("S103").place(256)`, hashed; one-step and 1000-step bitwise
  fixed-point check at N 256 (a local check, not the Numerics lane's verdict).

### F-003 (same commit): isolated controls

Glider from `GA` and from `GB`, and S103, each alone on N 256 for 100 tu (covers a 30-tu
approach timeout + 20-tu follow-up with margin). Measured: unwrapped track, fitted speed and
heading per 10-tu window, mass, component count, and minimum-image distance of the track from
every periodic image of a candidate ring site (for the torus re-encounter window). Exact float64
states saved at 0 and every 10 tu; hashes recorded.
