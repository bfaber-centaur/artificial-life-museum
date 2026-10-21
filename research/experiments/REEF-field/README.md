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

### F-004 (2026-10-21 ~06:10Z): adopt protocol v1 (reef/coordinator `5a6cce6`)

Protocol v1 governs these runs where it differs from F-001–F-003:
- Snapshots (replaces the GB choice rule in F-002): if the assessed glider has a measurable
  period P that is **not** explained by grid crossing (dominant mass period within 10% of
  1/|vx| or 1/|vy| counts as grid crossing), GA = phase 0 and GB = P/2. Otherwise GA = the
  settled seed and GB = GA + 5 steps (0.5 tu), labelled elapsed-time snapshots. The sub-cell
  fractional centroid of each is still recorded.
- Isolated controls run H = 50 tu (D-005), plus gyradius, and window noise (sd over 1-tu
  windows) for mass, speed, heading and gyradius. The 100-tu run of F-003 is kept as a
  longer validation of GA only.
- One manifest per run in `runs.jsonl` (schema `REEF/manifest.schema.json`).

## Results log

### R-001 (2026-10-21 06:12Z): settle (commit `586b134`, `python settle.py`, 16 s)

- 200-tu assessment tripped the **heading** transient test only: fitted heading 70.6° over
  steps 1000–2000 with a 1.55° change between halves (mass and speed changes 4e-5 and 9e-5).
  Extended once, as F-001 allows: assessment steps 4000–5000 (400–500 tu) gives heading
  **72.30°**, speed **0.5484 R/tu** (0.7129 cells/step), mass **0.48728** (rsd 0.12%),
  straightness 0.999999, half-to-half drift 0.02° / 5e-6 / 7e-6. Matches the L6-006 prior
  (0.487, 0.548, ~72°). The heading creeps toward ~72° over hundreds of tu; this is consistent
  with the known lattice heading lock at R 13, not tested further here.
- **Preregistered acceptance criterion failed as written:** "exactly one component (A > 0.1)" is
  false at 13% of samples (counts 1–3). Diagnosis: transient **single-cell specks** shed at
  the tail (mass ≤ 0.001 ΣA/R², ≤ 2.24 cells from the main body); the count flickers the same
  way at every threshold from 0.1 down to 1e-6 because the clip leaves exact zeros. All other
  acceptance criteria pass. Consequence for the protocol: a raw component count would score
  this isolated glider as FISSION; the tracker needs a minimum component mass/size or a merge
  distance (proposal sent to the lead). Not retuned; reported.
- Period test: dominant mass period 4.61 steps = grid-crossing 1/|vx| 4.61 steps, so no
  intrinsic period. **GA** = state at step 5000, **GB** = step 5005 (0.5 tu later), named
  elapsed-time snapshots, each integer-rolled to the grid centre. Hashes in
  `seeds/*.npy.json` and `settle.json`.
- S103 placed centred on N 256: bitwise fixed after 1 and 1000 steps (local check).
