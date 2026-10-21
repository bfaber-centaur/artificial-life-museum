# REEF protocol: first contact between a coexistence-rule glider and S103

**Owner:** Coordinator lane (expedition lead thread). **Mandate:** [`../../expeditions/2026-10-20-reef-launch.md`](../../expeditions/2026-10-20-reef-launch.md) at launch commit `51af137761512d66f7f73d4512e7bbc3b76f5b1f`.
**Version:** v1, frozen 2026-10-21 before any encounter run. Numeric thresholds marked **[A]** are frozen in the Gate A addendum (§10), from isolated baselines only, before any encounter state is examined. Any later change is a dated amendment in [`DECISIONS.md`](DECISIONS.md); this file is not rewritten silently.

## 1. Question

At μ = 0.155, σ = 0.020, what does first contact with S103 do to a moving Orbium-like glider and to the ring, relative to their matched isolated futures?

A clean null, a failed coexistence premise, or an exposed torus artifact is a complete result.

## 2. Fixed rule and numerics (primary)

| item | value |
|---|---|
| kernel / growth | poly / poly (catalog kn = gn = 1, as `alm` executes it), β = [1] |
| μ, σ | 0.155, 0.020 (never retuned inside this protocol) |
| R, T | 13, 10 (dt = 0.1 tu) |
| update | Euler + hard clip to [0, 1], float64 |
| boundary | periodic torus |
| world | N = 256 (19.69 R) to start; N = 512 only by the §6 rule |
| engine | `alm.lenia` (primary); `field.Batch` is the same arithmetic |
| threads | `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`; ≤ 2 simulation processes per thread |

Coordinates: arrays are indexed `A[y, x]`; x = column, y = row. Heading θ = atan2(Δy, Δx) in degrees, in array coordinates. Lengths are reported in R, times in tu (1 tu = T steps).

## 3. Specimens and seeds

- **G (glider):** S001 Orbium cells (registered `alm.specimens`), settled under the §2 rule. The native-rule (μ 0.150, σ 0.015) trajectory is **not** a control. Prior expectation (L6-006 `persist-T10-R13.csv`): GLIDER, mass ≈ 0.487, speed ≈ 0.548 R/tu, heading ≈ 72°. That row is a prior, not this expedition's baseline.
- **Settling (field lane):** place S001 cells centred in N256, run 100 tu, then assess 100 tu. If a transient remains (mass trend or speed trend outside the [A] tolerance), extend once to 500 tu total and record the reason. Save the settled state (`.npy`, float64) and its sha256.
- **Snapshots:** if the assessed glider has a measurable period P (mass or morphology autocorrelation peak), export **GA** at phase 0 and **GB** at phase P/2. Otherwise export **GA** and **GB** as two named elapsed-time snapshots 0.5 tu apart and say so. No invented phase cycle.
- **Ring:** S103 exact cells (`research/specimens/S103-static-ring/initial-cells-u8.csv`, levels/255). S103 has no internal phase. The known-result check (numerics lane) reproduces its exact fixed point first.
- **Transforms:** translations by integer cells only (np.roll on the torus). No interpolated rotation, no resizing at R13/N256. Every manifest records the full rule, seed hash, transform and realized offset.

## 4. Geometry

For each glider snapshot, take its measured unit heading ĥ (from the isolated control, unwrapped centroid over the assessment interval) and normal n̂ = (−ĥ_y, ĥ_x) in (x, y). The glider is placed at a fixed reference position; **only the ring moves** between offsets, so one glider-alone control per snapshot can serve all three offsets if its inputs are identical (mapping recorded).

Ring centre = glider centroid + d·ĥ + b·n̂, rounded to the nearest integer cell. Record the requested and realized (d, b) in R.

- d is chosen so the **clear gap** between the glider support and the ring support, measured along ĥ before the run, is 4 R (accepted range 3–5 R after rounding).
- Pilot offsets: b/R ∈ {−1, 0, +1} × {GA, GB} → six pilots **P1–P6** (P1 GA −1, P2 GA 0, P3 GA +1, P4 GB −1, P5 GB 0, P6 GB +1).
- Discovery geometries (≤ 12, §8) stay within b/R ∈ [−1.5, +1.5].

## 5. Runs, controls, horizons

Every encounter E has matched isolated controls with identical states, transforms, rule, numerics, world and scheduled horizon: **G-alone** (glider only) and **S-alone** (ring only at the same realized position). A control is shared only when every input and measurement contract is identical; the mapping is in the run registry.

- Scheduled horizon H = 50 tu for every encounter and control (approach timeout 30 tu + 20 tu post-contact). If isolated validation shows this window is not useful, it is changed in the Gate A addendum before pilots.
- Sampling: per-step whole-world mass; tracker output every 0.1 tu (1 step); full-state checkpoints every 1 tu (float32 npz is acceptable for checkpoints; float64 for states used as replay inputs). Store before (t = 0), contact, contact + 10 tu and final arrays in float64.
- Job order is interleaved by a fixed schedule seed **20261020** (`random.Random(20261020).shuffle` of the job list), recorded with the order.
- **Sham calibration (not a geometry):** one encounter-shaped run with the ring at the position farthest from the glider's path for H, used to measure the pre-interaction round-off floor of the superposition residual (§6.3).

## 6. Measurement contract (tracker owned by behavior lane)

1. **Support:** cells with A > θ_s **[A]** (proposal 0.01; the behavior lane may justify another value from isolated baselines). Components: 8-connected on the torus.
2. **Labels:** initial labels G and S are assigned at t = 0 and carried by maximum-overlap matching. Later connected components are reported as components, not forced onto labels. On merger, split or ambiguity, report component count, topology (which labels each component inherits), per-component mass and unassigned mass; no forced two-centroid persistence.
3. **Interaction onset t_int:** the first sample where max |A_E − (A_G-alone + A_S-alone)| exceeds θ_int **[A]**, set at ≥ 100× the sham floor. Kernel-range interaction can precede support overlap; this is why the residual is the onset measure.
4. **Contact t_c:** the first sample where a G-labelled support cell is 8-adjacent to, or merges with, an S-labelled support cell.
5. **Unwrapped trajectories:** per-label centroids unwrapped through boundary crossings; a boundary crossing alone is not a second encounter.
6. **Censoring:** from the measured headings and speeds, compute the earliest time t_cen at which any body (or fragment) could come within the interaction distance (sum of support radii + R + a 2 R guard) of a *periodic image* it has not already met, or of the ring a second time after separating. Outcomes are scored at min(t_c + 20 tu, t_cen, H). A run whose window ends at t_cen before t_c + 20 tu is **CENSORED** and keeps its partial classification. If N256 cannot give t_cen ≥ t_c + 20 tu for the pilot geometry, the primary setup moves to N512 before pilots (same seed size, controls rerun), recorded as a decision.

## 7. Outcome classes (scored at the end of the window, relative to controls)

| class | rule |
|---|---|
| NO_CONTACT | no t_c within 30 tu (timeout); still a valid record, with t_int if any |
| PASS | 2 components carrying G and S; G is GLIDER; S within ring tolerance **[A]**; heading change vs control < θ_defl **[A]** and lateral displacement vs control < δ_lat **[A]** |
| DEFLECT | as PASS, but heading change ≥ θ_defl or lateral displacement ≥ δ_lat; signed |
| RING_CHANGED | both persist as separate bodies, S outside ring tolerance (mass or gyradius) |
| TEMP_BIND | one component (or separation < contact distance) for ≥ 2 tu, then 2 components again inside the window |
| CAPTURE | one component, or G not GLIDER and within contact distance of S, through the end of the window (finite-horizon only) |
| CONVERT | final bodies' phenotypes differ from {GLIDER, S103} (e.g. a single new static/moving body, or circler) |
| FISSION | > 2 components at the end of the window |
| G_DEATH / S_DEATH / BOTH_DEATH | component mass < 0.01 (ΣA/R²) for the named body |
| FILL | > 25% of cells above 0.1 |
| CENSORED | window cut by t_cen (partial class attached) |
| CONTROL_FAILURE | a matched control leaves its validated class; the encounter is not scored |

A run can carry one primary class plus flags (e.g. RING_CHANGED + DEFLECT). Phenotype classes for single bodies reuse the L6-field motion classes (GLIDER net speed > 0.2 R/tu; STATIC path speed < 0.02; CIRCLER net < 0.1 and path > 0.2).

Scored observables per run: component count over time, total and per-component mass, unwrapped displacement, speed and heading change relative to control, ring mass/gyradius change, t_int, t_c, censor reason, and the stored arrays.

## 8. Gates and exploration

- **Gate A** (coordinator + behavior reviewer, no further human approval): isolated G and S validated through H, serialization round-trips bitwise, tracker tests pass (translation, wrap, merge, split), and the §6 contract is usable at the chosen N. If the fixed-rule moving control cannot be established within bounded preparation, encounters stop and the crux goes to Bobby.
- **Gate B:** six pilots P1–P6 with matched controls, all reviewed before selection.
- **Contrast selection rule (frozen now):** pick the clearest candidate effect and its nearest observed different outcome. If all six look alike, pick the closest encounter (b = 0) and a flank or no-contact case. Selection and IDs are committed before any check runs.
- **Discovery allowance:** ≤ 12 more geometries, each with matched controls; the offset/snapshot grid and the question it distinguishes are committed first. Prefer narrowing a transition or testing an explanation over filling a grid. None after 09:50Z.

## 9. Independent checks for each selected contrast

| check | what it tests | pass rule (frozen now) |
|---|---|---|
| clean-process exact-input replay | reproducibility | sha256 of final state identical |
| `alm_check` FFT replay | independent implementation, same arithmetic | expected bitwise; any difference investigated |
| `alm_check` direct window from the saved pre-interaction state through the outcome-defining event (≥ 20 tu, or labelled incomplete) | different arithmetic | same class; t_c within 0.5 tu; heading change within max(5°, 30%); masses within 1% |
| T20, fixed μ/σ, own matched controls | timestep | same class; quantitative tolerances as above in R/tu units |
| R26, 2×2 block replication, N doubled | resolution | same, with its own controls |
| larger world, unchanged R and seed size, same initial separation and phase | torus/world size | same, with its own controls |

If refinement changes the isolated phenotype (T40 at this rule previously gave a STATIC Orbium), report that as a limitation and possible numerical fragility rather than calling the encounter converged. If a small arithmetic mismatch changes the outcome, investigate and report the sensitivity.

Status labels: OBSERVED (exploration, exact scope), REPRODUCED (clean rerun), INDEPENDENTLY_CHECKED (the relevant independent evidence above, every failed or omitted check disclosed), NUMERICALLY_FRAGILE (a refinement changes the outcome).

## 10. Preregistered predictions (coordinator, before any encounter)

These are recorded so they can fail.

- **Pr1.** t_int precedes t_c by ≥ 0.5 tu in every contact pilot (kernel-range interaction before support contact).
- **Pr2.** Head-on (b = 0) for both snapshots: the ring survives within tolerance and the glider does not pass through unchanged; most likely outcome is G_DEATH or CAPTURE (my estimate 60%), otherwise a large deflection.
- **Pr3.** |b| = 1 R: grazing contact giving DEFLECT or PASS; the ±1 outcomes are not mirror images because the heading is not lattice-symmetric.
- **Pr4.** Snapshot (GA vs GB) changes the class in at most one of the three offsets.
- **Pr5.** No pilot gives FILL.

## 11. Gate A addendum (to be filled before pilots)

_Pending field and behavior handoffs: θ_s, θ_int (with sham floor), ring tolerance, θ_defl, δ_lat, glider acceptance tolerances, N, H, t_cen for each pilot geometry._
