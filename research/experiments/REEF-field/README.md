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

### F-005 (2026-10-21 ~06:25Z): runner, sham and timed segment (before running them)

- `runner.py` steps E, G-alone and S-alone in lockstep in one process (so the residual
  max|E − (G + S)| is exact per step and the lockstep G can be checked bitwise against the shared
  control `REEF-CTRL-<snap>`). It stores raw arrays for the tracker and does not classify.
  Encounters are refused without `--protocol-addendum <SHA>`.
- Sham (§5): GA at its reference position, ring shift (−82, −78) cells, chosen on a 2-cell grid
  to maximise the minimum torus distance from the GA-alone centroid track over H (8.74 R).
  `REEF-SHAM`, N 256, H 50. It doubles as the timed runner segment (tracking + checkpoints +
  frames). A second sham at N 512 (`REEF-SHAM-N512`, same relative placement) times the
  alternative world size.

Timestamp note: the "~06:05Z / ~06:10Z / ~06:25Z" labels on F-001, F-004 and F-005 were
estimates written ahead of time; the commit times are authoritative (F-001–F-003 `89696f3`
05:53:49Z, F-004 `586b134` 05:55:06Z, F-005 `5c2ec1b` 06:00:30Z). Each was still committed
before the runs it governs.

### R-002 (2026-10-21 06:03Z): isolated controls, geometry, torus margin, sham, timing

Commands (repo root, threads = 1): `python research/experiments/REEF-field/controls.py`
(commit `87d90e1`), `torus_margin.py 256` and `512`, `runner.py` for the shams (commit
`5c2ec1b`, clean tree), `register_prior.py` for the manifests. Registry: `runs.jsonl` (8 rows,
including a 1-tu runner smoke test `REEF-SHAM-try` whose frames file was deleted).

**Isolated controls, N 256, H 50 tu** (θ_s = 0.01; sd = across 50 one-tu windows):

| run | speed R/tu | heading ° | mass ΣA/R² | gyradius R | support radius R (max) |
|---|---|---|---|---|---|
| REEF-CTRL-GA | 0.54838 ± 0.00127 | 72.2966 ± 0.0863 | 0.48729 ± 0.00012 | 0.47743 ± 0.00012 | 1.021 |
| REEF-CTRL-GB | 0.54837 ± 0.00116 | 72.2957 ± 0.0901 | 0.48729 ± 0.00010 | 0.47743 ± 0.00012 | 1.021 |
| REEF-CTRL-GA-100tu | 0.54840 ± 0.00119 | 72.2990 ± 0.0848 | 0.48729 ± 0.00012 | 0.47743 ± 0.00012 | 1.021 |
| REEF-CTRL-S103 | 0 | – | 0.378698 (exact) | 0.38731 (exact) | 0.450 |

Whole-H least-squares fits: GA 0.548411 R/tu at 72.2940°, GB 0.548411 at 72.2942°,
straightness 0.999999. Per-step mass rsd 0.12%, per-step gyradius sd 0.00087 R (grid wobble).
Component count (A > θ_s) is 1 in 87%, 2 in 9.5%, 3 in 3.4% of steps: the single-cell specks of
R-001. S103 is bitwise unchanged through H.

**Pilot geometry (§4), N 256.** Glider fixed at its reference position; only the ring moves.
ĥ from each control's whole-H fit. Requested gap 4 R along ĥ (glider front 0.72 R, ring back
0.43 R ahead/behind its centre, so d = 5.15 R).

| pilot | snap | b req | ring roll (dy, dx) | d real R | b real R | gap real R | geometric t_c tu |
|---|---|---|---|---|---|---|---|
| P1 | GA | −1 | (60, 33) | 5.130 | −1.025 | 3.976 | 8.1 |
| P2 | GA | 0 | (64, 20) | 5.119 | +0.022 | 3.965 | 7.1 |
| P3 | GA | +1 | (68, 8) | 5.131 | +0.995 | 3.977 | 8.1 |
| P4 | GB | −1 | (61, 33) | 5.172 | −1.004 | 4.026 | 8.2 |
| P5 | GB | 0 | (65, 20) | 5.161 | +0.042 | 4.015 | 7.2 |
| P6 | GB | +1 | (69, 8) | 5.173 | +1.015 | 4.027 | 8.2 |

Ring roll is applied to the centred `seeds/S103.npy`; geometric t_c is when the undisturbed
G-alone support first becomes 8-adjacent to the placed ring support (no interaction modelled).

**Torus (§6.6).** D_int = r_G + r_S + R + 2 R = 4.47 R. On the undisturbed track no ring image
other than the primary comes within D_int before H (closest 4.97–7.00 R), so t_cen > 50 tu for
all six. Turning the track once at t_c by any angle (speed kept): the earliest image hit is
32.8–34.3 tu, after t_c + 20 (27.1–28.2 tu), so the scored window is safe for any single turn,
with ~4.6 tu to spare. Small left turns (+1.5° to +7.5°) hit an image at 42–44 tu, inside H.
At N 512 nothing hits before H for any turn. Not modelled: speed change, several turns,
fragments, return to the primary ring; the scorer must recompute t_cen on measured tracks.

**Sham and timing.** `REEF-SHAM` (N 256; ring roll (−82, −78), ≥ 8.74 R from the GA track):
residual max|E − (G + S)| 6.7e-16 at 1 tu, 2.6e-14 at 10 tu, 1.3e-13 at 50 tu (it grows with
t); no provisional contact; lockstep G final hash equals REEF-CTRL-GA's; lockstep S bitwise
fixed. `REEF-SHAM-N512`: residual 1.1e-13 at 50 tu. Wall time for one lockstep job (E + G + S,
500 steps, per-step labels and residual, per-step float32 frames, float64 checkpoints every
1 tu): N 256 8.3 s (6.8 s stepping), 411 MB peak RSS; N 512 33 s (27.5 s stepping). Outputs per
run: trace 13 KB, checkpoints 0.35–0.58 MB, frames 1.4–2.2 MB (frames kept out of git, copied
to the project folder `reef-field/runs/<id>/frames.npz`; sha256 in each manifest).

### F-006 (2026-10-21 06:12Z): pilot job list (Gate A addendum `6b142be` adopted)

`jobs.py plan` → `jobs-pilots.json`: P1–P6 at N 256, H 50, rolls from R-002, schedule
`random.Random(20261020).shuffle` → order **P5, P1, P6, P2, P3, P4**. Controls: G-alone =
REEF-CTRL-GA / REEF-CTRL-GB shared across offsets (D-004); `jobs.py run` checks that each
lockstep G reproduces the shared control's final sha256 bitwise. S-alone = REEF-P<k>-S, the
lockstep S at that realised ring position. Float64 arrays stored per run: t = 0, every 1 tu,
provisional contact step, contact + 10 tu, final (`checkpoints.npz`); float32 E and G every step
(`frames.npz`) for the tracker. Runner contact = one E support component overlapping both
control supports, which is the §6.4 adjacency/merge condition; the scored t_c is the tracker's.
Launch only after the Gate A pass: `python jobs.py run --protocol-addendum <SHA> --procs 2`.

### F-007 (2026-10-21 06:33Z): D-018 discovery grid X1–X8 (generator committed before runs)

`discovery.py plan` → `jobs-discovery.json`, `seeds/BLOB-X7.npy`, `seeds/BLOB-X8.npy` (the same
state, two files so each run names its own input). X1–X6 use the pilot placement code path
(checked: it reproduces the P1–P6 rolls exactly). Rolls: X1 GA −1.5 (58, 39), X2 GA −1.25
(59, 36), X3 GA +1.25 (69, 5), X4 GA +1.5 (70, 2), X5 GB −1.5 (59, 39), X6 GB +1.5 (71, 2).
Blob: a·exp(−r²/2s²) truncated at r ≤ 4 s, a = 0.68011, s = 4.3907 cells, mass 0.4873,
gyradius 0.4770 R, centred at the GA-alone centroid at step 55 (165.261, 139.565); X7 with the P2
roll (64, 20), X8 with the P3 roll (68, 8). Schedule `random.Random(20261020).shuffle` over
[X1..X8] → **X5, X1, X4, X2, X3, X7, X6, X8**. The runner gained stand-in seeds (`--snapshot
BLOB-X7`); the blob construction is copied into each manifest. Blob-alone controls are the lockstep
G (no shared control).

### F-008 (2026-10-21 07:10Z): D-020 reserve X9–X11 (generator committed before runs)

`discovery.py plan-reserve` → `jobs-reserve.json`, `seeds/BLOB-X9/X10/X11.npy`. The blob uses
X7's a = 0.680108 and s = 4.39073 cells exactly (not re-solved), truncated at r ≤ 4 s, centred at
the GA-alone centroid at step 61 (X9, X11; P2 roll (64, 20)) or step 67 (X10; P3 roll (68, 8)).
X11 = X9 with amplitude a/2. **Placement repair:** at these closer centres the blob's truncated
tail (2.6e-4 at that cell) reaches one cell the ring fills with 1.0, so blob + ring would exceed
the clip and E(0) ≠ G(0) + S(0). That one cell is zeroed in the blob (removed 2.6e-4 cell units,
≈ 1.5e-6 ΣA/R²), and the same masked blob is the blob-alone control. Resulting masses 0.48730 /
0.48730 / 0.24365 ΣA/R², gyradius 0.47701 R. The θ_s supports were already disjoint and
non-adjacent. Schedule over [X9, X10, X11] → **X9, X11, X10**.
