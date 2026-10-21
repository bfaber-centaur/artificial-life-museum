# REEF-behavior: body tracker, scorer and hostile review

Owner: Behavior and hostile-review lane of the Coexistence-Reef expedition (branch `reef/behavior`).
Launch packet: `expedition/reef-launch-2026-10-20` @ `51af137761512d66f7f73d4512e7bbc3b76f5b1f`;
mandate `research/expeditions/2026-10-20-reef-launch.md`. Contract: `research/experiments/REEF/PROTOCOL.md`
§6, §7 and the Gate A addendum §11 at reef/coordinator `6b142be`. This lane writes only this directory.

## Files

| file | what |
|---|---|
| [`track.py`](track.py) | torus components, per-cell label identity, topology and mass bookkeeping, support gap, superposition residual, periodic-image guard |
| [`score.py`](score.py) | `EncounterRecorder` (E + G-alone + S-alone in lockstep), `score_trace` (manifest `result`), `score_run_dir` (REEF-field run directories), CLI |
| [`test_track.py`](test_track.py), [`test_score.py`](test_score.py) | 22 tests (below) |
| [`baseline_thresholds.py`](baseline_thresholds.py), [`baseline/`](baseline/) | behavior-lane isolated-glider measurements used to check θ_s and debris |
| [`scores/`](scores/) | scored runs: `score.json` (result), `trace.jsonl` (per-step tracker rows), events, params |

Reproduce (repo root, NumPy only; SciPy is only needed by the field runner):

    PYTHONPATH=src python -m pytest -q research/experiments/REEF-behavior/
    PYTHONPATH=src python research/experiments/REEF-behavior/score.py \
        research/experiments/REEF-field/runs/<RUN_ID> --out research/experiments/REEF-behavior/scores/<RUN_ID>/score.json

## The measurement contract, as implemented

- **Support** `A ≥ θ_s = 0.01`; components 8-connected on the torus (sparse NumPy labelling, checked
  against brute-force torus BFS). Components lighter than **0.005 ΣA/R²** are debris: excluded from
  body counts, reported as `debris_mass`. `DEBRIS_HIGH` if debris > 0.01 at any sample.
- **Identity** is carried per cell: a support cell keeps last frame's label; new support cells take the
  majority label of labelled 8-neighbours. This is the protocol's "maximum overlap" at cell
  resolution. A body containing ≥ 0.005 of both labels is `merged`; one label in several bodies is
  `fragmented`; a label with no body is `lost`. **Per-label centroids are reported only when the
  label is `single`.** Merged/fragmented frames report topology (`G|S`, `GS`, `G|G|S`), owned mass
  per body, unowned/halo/debris (= unassigned) mass. After a release a label is `reacquired`, and
  `contact_lineage` keeps the fact that the body touched the other label.
- **Unwrapped tracks** are lifted per label by minimum-image increments of the owned-cell centroid,
  so a track stays continuous through edge crossings and through a merge.
- **t_int**: first sample with runner residual max|E − (G + S)| > θ_int = 1e-10 (float64, from the
  runner). **t_kr**: first sample where the controls' exact supports (A > 0) are < 2R apart; no
  interaction is possible before it, so `RESIDUAL_BEFORE_KERNEL_RANGE` flags a broken floor.
- **t_c**: first sample ≤ 30 tu where the two labels' support cells are 8-adjacent or share a body.
- **t_cen** (§11): first time a G body centroid comes within r_G + r_S + 3R of a ring image other than
  the one nearest at t = 0, or touches the ring again after a release. r = max support distance from
  the body centroid at t = 0 (G 0.91 R, S 0.45 R → 4.36 R).
- **Kinematics**: least-squares line through the unwrapped G centroid over the last 5 tu of the
  window vs the same fit of the G-alone control; signed heading change, lateral (positive = +90°
  from the control heading) and longitudinal offsets in R.
- **Classes** in order: CONTROL_FAILURE, FILL, NO_CONTACT, deaths (label body mass < 0.01), FISSION,
  CAPTURE (together for the whole last 5 tu; CONVERT if the joint body moves ≥ 0.02 R/tu), TEMP_BIND
  (together ≥ 2 tu, then apart), CONVERT (separate but G not GLIDER), RING_CHANGED, DEFLECT, PASS.
  Flags: RING_EXACT / RING_PERTURBED / RING_MOVED, SHIFT_LEAD/LAG, GLIDER_CHANGED, BRIEF_CONTACT,
  INTERACTION_WITHOUT_CONTACT, DEFLECTED_WITHOUT_CONTACT, TOGETHER_AT_END_NOT_CONTINUOUS. A censored
  run is `CENSORED` with `partial_class`.

## Tests (all pass, 22)

Labelling vs brute-force torus BFS; a body across both edges is one component; **translation** by a
known shift; **wrap** across both edges twice (2N + 7 steps, exact unwrapped displacement); **merge**
(topology `GS`, no per-label centroid, gap ≤ √2 at the merge frame); **split** (`G|G`, fragmented, no
forced centroid); merge-then-release (labels reacquired, track continuous, events `merge`, `split`);
debris/orphan bookkeeping; minimum-image gap; image guard; real S001 glider on a 64² world tracked
across edges (agrees with `alm.morphometrics.centroid` path < 0.5 cell); real far-apart S001 + S103
residual < 1e-12 with the ring box bitwise fixed; synthetic PASS, DEFLECT (signed), CAPTURE, G_DEATH,
NO_CONTACT, CENSORED (other image), CONTROL_FAILURE; a real sham scores NO_CONTACT.

## Validation on field controls (Gate A)

| run | source | class | control G | ring | debris max | residual max |
|---|---|---|---|---|---|---|
| REEF-SHAM (GA) | field `bc95885` command, rerun here; frames.npz sha256 `f31fc270…` identical to the field manifest | NO_CONTACT | single body throughout, 0.5485 R/tu, 72.325° | RING_EXACT, Δm 0 | 0.0006 | 1.3e-13 |
| REEF-SHAM-GB-behavior | same runner, `--snapshot GB`, same ring shift (not in the field registry) | NO_CONTACT | single body, 0.5485 R/tu, 72.321° | RING_EXACT | 0.0006 | 4.5e-13 |

Specks appear in 12.4% of samples (field: 13%); with the debris rule the controls never score FISSION.

## Threshold notes (isolated baselines, behavior lane)

`baseline_thresholds.py` (S001 cells, 100 tu settle at N256, 150 tu follow-up; settled sha256
`608e9ef7…`, this lane's own settle, not the field seed): halo (mass below θ_s) is 0.09% at
θ_s 0.01, 3.7% at 0.1 and 14% at 0.2; the exact support (A > 0) is at most 255 cells, so θ_s 0.01
sits within about a cell of the true edge. Detached satellites (≤ 0.002 ΣA/R²) appear at every θ_s from
0.001 to 0.2, so the threshold cannot remove them; the debris rule does. Heading over 150 tu wanders
slowly (70.2° → 71.8° between halves) while the 2–10 tu windowed heading sd is ~0.9°: comparisons
must be control-relative at matched times, never against a nominal heading.

## Known limitations

- Cell-level identity assumes bodies do not superpose. If a glider's support moved *through* the
  ring's cells, those cells would keep the S label and the glider could look absorbed. Real bodies
  cannot share cells additively under the clip, but any CAPTURE/G_DEATH call should be checked
  against the frames.
- E and G frames are float32 in the runner; thresholds at 0.01 are unaffected, but RING_EXACT is
  bitwise in float32 for each step (float64 checkpoints exist every 1 tu).
- t_cen checks G bodies against ring images only, not fragments against each other.
- After a merge, which fragment is "G" is decided by cell ownership; any class that depends on that
  attribution should be reviewed on frames.

## Results so far and rival status (updated against the evidence, 2026-10-21)

Scores: P1–P6 (pilots) and X1–X8 (discovery), tables in [`audit/pilot-table.md`](audit/pilot-table.md)
and [`audit/discovery-table.md`](audit/discovery-table.md), audit in [`audit/PILOT-AUDIT.md`](audit/PILOT-AUDIT.md),
literature in [`LITERATURE.md`](LITERATURE.md), exhibit in [`exhibit/`](exhibit/). Every glider encounter
with b/R in [−1.5, +1.5], under both snapshots, is FISSION + PROLIFERATION. A static mass-matched
blob placed in contact ignites the same way (X9, X10), and so does 0.75× (X12). Half that dose (X11),
or the full dose 2.1 R away (X7, X8), does not. Kernel-range interaction
comes 0.6–1.0 tu before contact, glider and ring fuse at contact, and an expanding colony follows
that freezes behind its front. All statements are OBSERVED at N256, R13, T10, finite
horizon t_c + 20 tu. Numerical checks are the numerics lane's; panel F shows their matrix and this lane's D-010 rescore of R26.

| rival (from [`RIVALS.md`](RIVALS.md)) | status | evidence | what would discriminate |
|---|---|---|---|
| Torus re-encounter produces the outcome | **excluded for the class**, remains for anything after ~27 tu | FISSION is reached at 10–16 tu. The colony's support reaches N/2 at 27–30 tu, after every scoring window (26.1–27.7). No G body comes near a ring image inside a window. | N512 or larger-world rerun (checks table) to follow the front past 27 tu |
| A control failure is read as an effect | **excluded** | glider-alone stays a single GLIDER through H in every run; ring-alone stays bitwise; no CONTROL_FAILURE | — |
| Labelling artifact (merge/identity) | **excluded for the class**, identity after ignition is meaningless | FISSION + PROLIFERATION use only body counts and total mass, not identity | — |
| Lattice re-lock / deflection artifact (G1) | **moot** | no run separates, so no deflection is measured | — |
| Snapshot (GA vs GB) or placement rounding matters | **excluded for the class** | GA and GB agree at every offset tested (P1–P6, X1–X6). Realized offsets are within 0.03 R of requested. | — |
| Sensitivity, not mechanism (G2) | **open** | not yet tested | `alm_check` direct window and clean replay (numerics lane) |
| R13 or T10 specific | **class survives T20, R26 (D-010) and N512; timing and mass do not** | numerics `e7d4ef6`: T20 FISSION with ignition 2–3 tu earlier and E mass +35–62% at t20; R26 judged against its own ring-alone (one static body, D-010/D-024) is FISSION + PROLIFERATION; disclosed variant with a 0.378–0.383 mass band is CONTROL_FAILURE from a pre-contact seed-relaxation dip (panel F, `exhibit/README.md`) | R26 per-step rows (checkpoint cadence 1 tu so far) |
| Any nearby mass ignites the ring (not glider-specific) | **supported: the glider is a delivery mechanism, not a requirement** | a static blob of the glider's mass, placed at the glider's position at t_c (X9 for P2's geometry, X10 for P3's), ignites the same colony: FISSION + PROLIFERATION, 79–87 bodies and mass ≈ 35 at t_c + 20. The same blob 2.1 R away evaporates without contact (X7, X8). Half the dose at the contact position (X11) evaporates in 0.3 tu, and the ring returns bitwise. | the ignition threshold at this position lies between 0.5× and 0.75× the glider's mass, 0.24–0.37 ΣA/R²: X12 at 0.75× ignites (113 bodies, mass 46 at t_c + 20). A finer dose ladder would narrow it. Prior: the S103 dossier's I003 additions (0.10 returns, ≥ 0.30 fills) |
| The colony is self-replication (Chan 2020-style) | **not supported** | interior freezes behind the front (P2: mean ΔA within 4 R falls from 0.12 to 0.011 per tu, 16 → 26 tu), bodies laid down by the front | count body divisions in the interior over time; check whether front speed is set by the front itself (pushed front), not by the trigger |
| Novel phenomenon | **no** | S103 dossier (fill under ≥ 0.30 addition), HR-009 (S102 fills the world at this rule), Chan 2019 §3.5.5 "Detonation" | — |
