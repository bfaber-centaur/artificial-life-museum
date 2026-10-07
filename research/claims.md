# Claims ledger

Every substantive claim gets a stable ID (`C001`, `C002`, ...) and exactly one
status. Claims are never deleted: a refuted claim stays here with its evidence.
Status changes are appended to the claim's history, not overwritten.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `OBSERVED` | Seen in at least one recorded run; not yet reproduced. |
| `CONJECTURED` | Hypothesis without direct supporting runs yet. |
| `REFUTED` | Contradicted by recorded evidence. |
| `REPRODUCED` | Re-observed from a clean process with the same inputs. |
| `NUMERICALLY_FRAGILE` | Changes or disappears under a modest timestep/resolution/boundary change. |
| `INDEPENDENTLY_CHECKED` | Reproduced by a second lane and/or a distinct execution path. |

## Template

Copy this block for each new claim.

```markdown
### C000 — <one-line statement>

- **Status:** CONJECTURED
- **Owner lane:**
- **Specimen / version:** (ID and dossier commit)
- **Simulator / version:** (package + git commit)
- **Parameters:** (R, T, mu, sigma, kernel peaks, grid size, dt, boundary)
- **Intervention:** (type, location, strength, timing)
- **Metric:** (definition, threshold, horizon; fixed before looking at results?)
- **Run IDs:**
- **Search / parameter bounds:**
- **Reproduction command:**
- **Known caveats:**
- **History:**
  - YYYY-MM-DD — CONJECTURED — <who, why>
```


Ledger conventions (added by the claims archivist, Lane 0):

- **Sources** names every lane proposal merged into the claim, with the file and the PR that
  carries it. A PR marked "open" had not merged when the claim was entered; its commit hash may
  change on merge, but the file path will not.
- **Run IDs** use the lane's own ID where one exists (Lane 2 `S001-<hash>`, Lane 7 `H001-…`).
  Lanes without run IDs are cited as script + output file + commit, which is enough to rerun.
- `INDEPENDENTLY_CHECKED` is used only where two lanes ran **distinct implementations** and got
  the same answer. Two lanes running the same stepper count as `REPRODUCED`.
- Where lanes disagree, each side gets its own claim and both carry a **Dispute** line pointing
  at the other and at the [Open disputes](#open-disputes) table. The archivist does not pick a
  winner; the status changes only when new evidence lands.

### Execution paths referred to below

| Path | Owner | Code | Notes |
| --- | --- | --- | --- |
| `ref` | Lane 1 | `research/specimens/S001-orbium/reconstruct.py` | numpy transcription of upstream `LeniaND.py`; also used by Lane 5 (first version), Lane 7 (`h001.py`) and Lane 4 (L4-001 `ref` engine) |
| `alm` | Lane 2 | `src/alm` (commit `1ed2696`) | `rfft2`, kernel at index (0, 0) |
| `alm_check` | Lane 3 | `src/alm_check` (PR #8, commit `263ec66`, open) | written without reading `src/alm`; FFT path and FFT-free real-space path |
| `upstream` | Lane 1 / Lane 3 | `Automaton` from `.refs/Lenia/Python/LeniaND.py` @ `adfc542` | CPU path, float64 |

Unless a claim says otherwise, the rule is the S001 baseline: Orbium O2u cells from
`research/specimens/S001-orbium/initial-cells-u8.csv` (dossier commit `65c03cc`), polynomial
core and polynomial growth, R = 13, T = 10 (dt = 0.1), μ = 0.15, σ = 0.015, β = [1],
Euler + clip [0, 1], float64, periodic 128 × 128 torus, no intervention, deterministic (no seed).

## Open disputes

| Dispute | Claims | Lanes | State |
| --- | --- | --- | --- |
| D1: does S001's heading stay lattice-locked at R = 26? | C012 vs C013 | Lane 3 vs Lane 7 | open on wording, not data. Lane 7 (HR-005) points to repeated plateaus in Lane 3's own `heading-R26.csv`; the archivist confirmed that 14 of Lane 3's 19 R = 26 headings in 0–45° match a Lane 7 heading to ≤ 0.01° (12.5°/15° → 53.28°, 30°/32.5° → 36.72°). Lane 3 has not yet restated its claim; rechecking (2026-10-07). |

## Lane intake index

| Lane proposal | Ledger |
| --- | --- |
| Lane 1 S001 dossier, proposed claim 1 (baseline glides stably) | C001 |
| Lane 1 S001 dossier, proposed claim 2 (survives every recorded rule) | C002 |
| Lane 1 S001 dossier, proposed claim 3 (wobble period set by grid crossing) | C003, C004, C005, C006 |
| Lane 2 L2-S001-baseline, proposed claim (glides stably under `alm`) | C001, C010 |
| Lane 3 lane3/README, claims 1 / 2 / 3 / 4 / 5 / 6 | C001 / C009, C010 / C011, C012 / C003, C005 / C017, C018 / C016 |
| Lane 3 lane3/README, heading-dependent speed | C015 |
| Lane 3 lane3/README, float32 note | C019 |
| Lane 5 L5-baseline, proposed claim 1 (means heading-invariant) | C007 |
| Lane 5 L5-baseline, proposed claim 2 (all oscillations are grid-crossing periods) | C008 |
| Lane 5 L5-baseline, finding 3 (major axis along heading) | C020 |
| Lane 7 hostile-review HR-001 (wobble), HR-001b (heading pinning) | C003, C004, C006, C011, C013 |
| Lane 7 hostile-review HR-003 (Lane 5 tooling, anisotropy bias) | C008, C014, C021 |
| Lane 7 hostile-review HR-005 (Lane 3 numerics) | C003, C006, C009, C013 (D1) |
| Lane 7 hostile-review HR-006 (heading-dependent means) | C007, C015, C022 |
| Lane 5 restated L5-baseline claims 1 and 2 (PR #9 @ `c5d2435`) | C022, C024 |
| Lane 5 L5-axis-breathing proposed claim (PR #9 @ `c5d2435`) | C025 |
| Lane 5 `symmetry_order` noise-floor fix (PR #9 @ `c5d2435`) | C021 history |
| Lane 4 L4-001 results at commit `12d9265` (PR #5, open; no claim proposed yet) | C023 |
| Lane 6 | not started |

## Claims

### C001 — S001 glides stably under the baseline rule for at least 20 000 steps

- **Status:** INDEPENDENTLY_CHECKED
- **Owner lane:** Lane 2 (run), Lane 3 (independent check), Lane 1 (first observation)
- **Sources:** Lane 1 `research/specimens/S001-orbium.md` claim 1 (PR #2/#3, merged); Lane 2
  `research/experiments/L2-S001-baseline.md` (PR #6, merged); Lane 3
  `research/experiments/lane3/README.md` claim 1 (PR #8, open); Lane 5 cross-check in
  `research/experiments/L5-baseline/README.md` (PR #9, open)
- **Specimen / version:** S001 Orbium O2u, dossier commit `65c03cc`, cells sha256 (int16le)
  `3dc9eb00…99673bc`
- **Simulator / version:** `alm` 0.1.0 @ `1ed2696` (run); checked against `alm_check` @
  `263ec66` (FFT and FFT-free paths), `upstream` `Automaton` @ `adfc542`, and `ref`
- **Parameters:** S001 baseline (above), 128² torus
- **Intervention:** none
- **Metric:** alive = raw ΣA > 1e−10 at the final step; mass = ΣA/R²; speed = net unwrapped
  centroid displacement over steps 1000–20000. Fixed before the run (Lane 2).
- **Result:** alive at step 20 000; mass 0.435804 ± 0.001113 (range 0.4332–0.4380); speed
  0.47941 R/time = 0.62323 cells/step; stationary across four 5000-step windows.
- **Run IDs:** `S001-37369303c7` (Lane 2; bitwise reproduced from a clean process). Lane 3:
  `python -m alm_check.compare_lane2 research/traces/S001-37369303c7` → final state at step
  20 000 **bitwise identical**; FFT-free path agrees to max|ΔA| ≈ 2e−6 (saturating, not
  growing); `upstream` agrees to 5.6e−7 at 2000 steps. Lane 1 `reference-trace.csv` agrees
  with `alm` to print precision (5.4e−7) over 4000 steps (`tests/test_run.py`).
- **Search / parameter bounds:** one rule, one grid (128²), one T, one orientation.
- **Reproduction command:** `.venv/bin/python -m alm.run --specimen S001 --steps 20000 --every 10 --size 128 --seed 0 --burn-in 1000`
- **Known caveats:** the bitwise match between `alm` and `alm_check` is expected because both
  use `rfft2` with the kernel at (0, 0); the FFT-free path is the numerically distinct check.
  The speed figure is a T = 10 number (C009, C010). The constant 68.2° heading is a lattice
  plateau, not an organism trait (C011).
- **History:**
  - 2026-10-07 — OBSERVED — Lane 1, `ref` 5000 steps, checked vs `upstream` for 2000 steps.
  - 2026-10-07 — REPRODUCED — Lane 2, `S001-37369303c7`, bitwise from a clean process.
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on Lane 3's four-path agreement (PR #8).

### C002 — S001 survives every rule variant recorded for these cells

- **Status:** OBSERVED
- **Owner lane:** Lane 1
- **Sources:** `research/specimens/S001-orbium.md` claim 2 and "Rule-variant sweep" (PR #2/#3, merged)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref` (`reconstruct.py` @ `65c03cc`)
- **Parameters:** R = 13, T = 10, μ = 0.15, 128²; poly/poly σ ∈ {0.014, 0.015, 0.016, 0.017};
  exp/exp σ ∈ {0.015, 0.016 (paper rule), 0.017}
- **Intervention:** none
- **Metric:** alive at step 5000; mean mass, gyradius, speed over steps 1000–5000 sampled every 50
- **Result:** alive in all 7 rules. Mass, size and speed rise monotonically with σ (poly/poly
  mass 0.4234 → 0.4550; speed 0.4635 → 0.5193 R/time).
- **Run IDs:** `reconstruct.py --steps 5000 --every 50 --kernel {poly,exp} --growth {poly,exp} --sigma S` (7 runs; table in dossier)
- **Search / parameter bounds:** the 7 rules above only; μ not varied; poly/exp mixed families not run.
- **Reproduction command:** as Run IDs
- **Known caveats:** single execution path; 5000-step horizon; Lane 3 did not sweep exp/exp.
  Consistent with the paper's "no visible effect" statement (Fig. 6b).
- **History:**
  - 2026-10-07 — OBSERVED — Lane 1.

### C003 — S001's mass wobble is a lattice-sampling artifact: its relative amplitude vanishes as the creature is resolved more finely

- **Status:** INDEPENDENTLY_CHECKED
- **Owner lane:** Lane 7 (preregistered test), Lane 3 (independent resolution sweep)
- **Sources:** Lane 1 dossier claim 3 (origin); Lane 3 lane3/README claim 4 (PR #8, open);
  Lane 7 `research/reports/hostile-review.md` HR-001 and
  `research/experiments/H001-lattice-wobble/` (PR #7, open)
- **Specimen / version:** S001, dossier commit `65c03cc`; cells zoomed by R/13
- **Simulator / version:** Lane 7: `ref` via `h001.py` @ `c1df640`. Lane 3: `alm_check` @ `263ec66`.
- **Parameters:** baseline rule with R varied, world ≈ 9.85 R wide. Lane 7: R ∈ {13, 20, 26, 39},
  bilinear zoom. Lane 3: R ∈ {5 … 52}, nearest-neighbour (z0) and bilinear (z1) zoom.
- **Intervention:** none (resolution change only)
- **Metric:** mass sd/mean. Lane 7: steps 1000–2999, preregistered P3 = "falls monotonically and
  ≥ 2× from R = 13 to 39" (commit `5f0326f`, before any run). Lane 3: t = 100–400.
- **Result:** Lane 7 2.56e−3 (R 13) → 1.04e−3 (20) → 5.31e−4 (26) → 1.27e−4 (39), a 20× drop.
  Lane 3 2.6e−3 (13) → 5.7e−4 (26) → 2.5e−4 (39) → 1.3e−4 (52), close to R⁻². Mean mass is
  resolution-stable (C014). A real breathing mode would not lose 95% of its relative amplitude.
- **Run IDs:** `H001-E1-R{13,20,26,39}` (`e1.csv`); Lane 3 `research/traces/lane3/resolution.csv`
  (`python -m alm_check.sweeps resolution`)
- **Search / parameter bounds:** R = 5–52; one T (10); rotation 0 for the R sweep.
- **Reproduction command:** `.venv/bin/python research/experiments/H001-lattice-wobble/h001.py e1`; `python -m alm_check.sweeps resolution`
- **Known caveats:** Lane 7's preregistered verdict is formally **MIXED** because P2 (period changes
  > 10% from R 13 to 39) failed as written (4.32 vs 4.03 steps); Lane 7 argues P2 was badly
  designed. The two lanes' amplitudes differ at R = 39 (1.27e−4 vs 2.5e−4); zoom method and
  window differ, and both show the same strong decrease. Lane 7 (HR-005) attributes the gap to
  heading: at fixed R = 13 the amplitude ranges 2.0e−3 (12.7°) to 1.0e−2 (axis) with heading,
  and Lane 3's resolution runs end on headings 64.3°–68.2°. So the R⁻² exponent is **not
  determined**; the robust statement is "falls about 20× from R = 13 to R = 39–52".
- **History:**
  - 2026-10-07 — OBSERVED — Lane 1 proposed the lattice account from three start rotations.
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on agreement of Lane 7 (`ref`) and Lane 3 (`alm_check`).
  - 2026-10-07 — caveat added — Lane 7 HR-005: amplitude–R relation confounded with heading; exponent dropped.

### C004 — S001 has a 4.32-step mass oscillation (as a property of the organism)

- **Status:** NUMERICALLY_FRAGILE
- **Owner lane:** Lane 7
- **Sources:** Lane 2 baseline (4.320-step dominant mass period); Lane 7 HR-001 proposed entry
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm` @ `1ed2696` (period); `ref` / `alm_check` (fragility)
- **Parameters:** baseline; R varied 13–52 for the fragility test
- **Intervention:** none
- **Metric:** dominant period of per-step mass (Hann-windowed rFFT) and its sd/mean
- **Result:** the period and amplitude change with R and with heading (C003, C006); the
  oscillation disappears in the continuum limit.
- **Run IDs:** `S001-37369303c7`; `H001-E1-R{13,20,26,39}`, `H001-E2-rot{0..45}`; Lane 3 `resolution.csv`
- **Search / parameter bounds:** as C003 and C006
- **Reproduction command:** as C003
- **Known caveats:** do not use mass fluctuation amplitude or period as an organism observable
  at any single R. Windowed **mean** mass is a good observable (C014).
- **History:**
  - 2026-10-07 — NUMERICALLY_FRAGILE — archivist, on C003 (Lane 7 recommendation).

### C005 — S001's dominant mass period equals the single-axis grid-crossing period 1/|v_x| (or a simple x–y beat) at its heading

- **Status:** REFUTED
- **Owner lane:** Lane 1 (proposed), Lane 3 and Lane 7 (tests)
- **Sources:** Lane 1 dossier claim 3 ("period set by grid-crossing", 4.32 at 68.2°, 14.3 at 40.4°)
  and its proposed test "period scales as 1/(speed · cos heading)"; Lane 3 README claim 4; Lane 7 HR-001
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check` @ `263ec66`; `ref` via `h001.py` @ `c1df640`
- **Parameters:** baseline with R ∈ 8–52 (Lane 3) and R ∈ {13, 20, 26, 39} (Lane 7)
- **Intervention:** none
- **Metric:** dominant mass period vs 1/|v_x| aliased into [0, 0.5] cycles/step, tolerance ≤ 3% (Lane 3)
- **Result:** Lane 3: holds in 6 of 17 persisting runs (8 counting beats); fails at R = 11, 16, 20,
  26 z1, 39 z0, 52 z1. Lane 7: the dominant line at R = 20 is (−1, −2) and at R = 26 is (−2, 1),
  not (1, 0). The wording is refuted as a general rule; the lattice account survives in C003/C006.
- **Run IDs:** Lane 3 `resolution.csv`; `H001-E1-R{13,20,26,39}`
- **Search / parameter bounds:** as above
- **Reproduction command:** `python -m alm_check.sweeps resolution`; `h001.py e1`
- **Known caveats:** holds at R = 13 rotation 0 (4.32 steps), which is where it was first seen.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 1, three start rotations at R = 13.
  - 2026-10-07 — REFUTED — archivist, on counterexamples from Lane 3 and Lane 7.

### C006 — S001's dominant mass period lies on a low-order lattice line f = m·v_x + n·v_y (|m|, |n| ≤ 2), folded into [0, 0.5] cycles/step

- **Status:** OBSERVED
- **Owner lane:** Lane 7
- **Sources:** `research/reports/hostile-review.md` HR-001; `research/experiments/H001-lattice-wobble/PREREGISTRATION.md` (PR #7, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref` via `h001.py` @ `c1df640`
- **Parameters:** E1: rotation 0, R ∈ {13, 20, 26, 39}. E2: R = 13, start rotations 0°, 3°, …, 45°.
- **Intervention:** none (start-state rotation, bilinear)
- **Metric:** preregistered: dominant rFFT peak within 0.002 cycles/step of a lattice line,
  steps 1000–2999; chance baseline from tolerance-window coverage.
- **Result:** P1 4/4 resolutions; P4 14/16 headings vs 1.45 expected by chance
  (P(≥ 14) = 2.5e−13). Misses: rotation 21° (near the diagonal) and 33° (error 0.00226).
- **Run IDs:** `H001-E1-R{13,20,26,39}` (`e1.csv`), `H001-E2-rot{0..45}` (`e2.csv`)
- **Search / parameter bounds:** |m|, |n| ≤ 2; R = 13–39; headings 21.8°–68.2°
- **Reproduction command:** `h001.py e1`, `h001.py e2`; `pytest -q tests/test_h001_lattice_wobble.py`
- **Known caveats:** single execution path. The account does not predict *which* line dominates.
  Not yet checked against Lane 3's 9 runs that missed the single-axis rule (C005); Lane 7
  (HR-005) asks Lane 3 to rescore them against this line set.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 7, preregistered (`5f0326f`).

### C007 — S001's baseline morphometric means are heading-invariant

- **Status:** REFUTED (at R = 13, for anisotropy and speed; see C022 for what survives)
- **Owner lane:** Lane 5
- **Sources:** `research/experiments/L5-baseline/README.md` proposed claim 1 (PR #4 merged; re-run
  on `alm` in PR #9, open); objections in Lane 7 HR-001 (point 1) and HR-003
- **Specimen / version:** S001, dossier commit `65c03cc`; start state rotated 0°, 23°, 45° (bilinear)
- **Simulator / version:** `ref` (PR #4, commit `1d85475`) and `alm` (PR #9); features
  `alm.morphometrics.snapshot(A, R=13)`, area threshold 0.1
- **Parameters:** baseline, 128², 4000 steps
- **Intervention:** none
- **Metric:** means over steps 1000–4000 (every step) of mass, gyradius, anisotropy, area, a₂, speed
- **Result:** means agree across headings 68.2°, 40.4°, 21.8° to 0.3% (mass), 0.15% (gyradius),
  1.2% (anisotropy). Mass 0.4358, gyradius 0.438 R, anisotropy 0.29, area 1.00 R², speed
  0.479 R/time. `ref` and `alm` agree on every summary statistic to 7.6e−5 relative.
- **Run IDs:** `research/experiments/L5-baseline/measure_s001.py` → `trace-rot{00,23,45}.csv`, `summary.csv`
- **Search / parameter bounds:** three start rotations; one R, T, grid
- **Reproduction command:** `.venv/bin/python research/experiments/L5-baseline/measure_s001.py`
- **Known caveats:** the 0° and 45° rows are lattice mirror images, so only **two** independent
  headings were tested (Lane 7). All three headings lie in 21.8°–68.2°; Lane 3 finds speed
  1.2% lower at axis-locked headings (C015). Mean anisotropy at R = 13 is biased 1.2% vs R ≥ 20
  (C014). The two paths share the feature code, so the original result is REPRODUCED, not
  independently checked.
- **Refuting evidence (Lane 7 HR-006, PR #7 @ `0fd42ee`):** `heading_means.py` (`ref`), 6000 steps,
  stats over steps 2000–5999, start rotations 0°, 27°, 55°, 70° at R = 13. The axis-travelling
  creature (heading −0.46°) has mean anisotropy **0.2649** vs 0.2953 at 68.2° (10% less
  elongated) and speed 0.4734 vs 0.4794 R/time (1.2% slower; Lane 3 independently finds the same
  speed drop, C015). Lane 5's three rotations all landed on 5/2-type or near-diagonal plateaus,
  so they never sampled the axis plateau. Output: `research/experiments/H001-lattice-wobble/heading_means.csv`.
  Lane 5 reproduced the low axis anisotropy on `alm` with its own feature code (0.2665 over steps
  2000–7999, `research/experiments/L5-axis-breathing/results.csv`, PR #9 @ `c5d2435`), so the
  refuting evidence is itself on two paths. Lane 5 accepted the refutation and restated its claim (C022).
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5, `ref` path.
  - 2026-10-07 — REPRODUCED — Lane 5, re-run on `alm` (PR #9).
  - 2026-10-07 — REFUTED — archivist, on Lane 7 HR-006 (axis-locked heading at R = 13); the
    statement holds at R = 26 and for mass and gyradius (C022).
  - 2026-10-07 — refutation accepted by Lane 5 (PR #9 @ `c5d2435`), which restated the claim as C022.

### C008 — Every S001 baseline feature oscillation has a grid-crossing period (or its alias or beat)

- **Status:** REFUTED
- **Owner lane:** Lane 5 (proposed), Lane 7 (counterexample)
- **Sources:** L5-baseline proposed claim 2 (PR #4/#9); Lane 7 HR-003 point 2 (PR #7, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref` / `alm` (Lane 5); `aniso_check.py` independent second-moment code (Lane 7)
- **Parameters:** baseline, rotation 0 (heading 68.2°)
- **Intervention:** none
- **Metric:** dominant period of each feature vs lattice lines |m|, |n| ≤ 2
- **Result:** the anisotropy period at rotation 0 is 8.015 steps (`summary.csv`, column
  `anisotropy_period`). The nearest lattice line is (−2, 1) at 8.64 steps, 0.009 cycles/step
  away (archivist recomputed from the `alm` velocity). Lane 7 reproduced the peak with
  independent code. The conclusion "the oscillations are lattice-driven" is supported by the
  resolution test instead: at R = 20 and 26 the 8.0-step component is gone and anisotropy sd falls
  4.8e−3 → 3.1e−3 → 1.4e−3.
- **Run IDs:** L5 `summary.csv`; `research/experiments/H001-lattice-wobble/aniso_check.txt`
- **Search / parameter bounds:** R = 13, 20, 26; three headings
- **Reproduction command:** `.venv/bin/python research/experiments/H001-lattice-wobble/aniso_check.py`
- **Known caveats:** refuted as worded (period matching); the lattice-artifact conclusion for
  fluctuations is carried by C003-style resolution evidence.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5.
  - 2026-10-07 — REFUTED — archivist, on Lane 7's counterexample from Lane 5's own data.
  - 2026-10-07 — refutation accepted by Lane 5 (PR #9 @ `c5d2435`), which restated the claim as C024.

### C009 — At T = 10, S001's speed is about 16% below its Δt → 0 limit and its mass 2.6% above

- **Status:** OBSERVED
- **Owner lane:** Lane 3
- **Sources:** lane3/README claim 2 (PR #8, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check` @ `263ec66`
- **Parameters:** baseline with T ∈ {1, 2, 3, 4, 5, 7, 10, 15, 20, 40, 80, 160, 320}, 128²
- **Intervention:** none
- **Metric:** mass, gyradius, speed over t = 100–400 time units; Richardson extrapolation
  (first-order Euler) from T = 160/320
- **Result:** speed 0.4794 R/time at T = 10 → limit ≈ 0.572 (0.570 from T = 80/160) by Lane 3's
  first-order Richardson extrapolation, i.e. 16% low. Lane 7 (HR-005) notes the successive
  differences shrink by ≈ 0.6×, not 0.5× (effective order ≈ 0.7, plausibly from the hard clip);
  geometric extrapolation gives ≈ 0.5745, i.e. 16.6% low (archivist rechecked the arithmetic
  from `timestep.csv`). Either way about 16–17%. Mass 0.4358
  → ≈ 0.4249. Gyradius stable to 0.1%. Heading also moves with T (68.2° at T = 10–15, 66.5–66.8°
  at T ≥ 80).
- **Run IDs:** `research/traces/lane3/timestep.csv` (`python -m alm_check.sweeps timestep`)
- **Search / parameter bounds:** T = 1–320
- **Reproduction command:** `python -m alm_check.sweeps timestep`
- **Known caveats:** single execution path; the limit depends on the assumed convergence order
  (above). Heading also changes with T, and speed depends on heading at R = 13 by up to 1.2%
  (C015), a small confound in the sweep.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.
  - 2026-10-07 — refined — Lane 7 HR-005: deficit 16.6% under a geometric fit.

### C010 — S001 travels at 0.479 R per time unit

- **Status:** NUMERICALLY_FRAGILE
- **Owner lane:** Lane 2 (value), Lane 3 (fragility)
- **Sources:** L2-S001-baseline; Lane 1 dossier; L5-baseline; lane3/README claim 2
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm` @ `1ed2696`; `alm_check` @ `263ec66`
- **Parameters:** baseline (T = 10); T varied in C009
- **Intervention:** none
- **Metric:** net unwrapped centroid displacement per time unit
- **Result:** 0.47941 R/time at T = 10 in four paths, but 0.414–0.566 across T = 4–320 (C009).
- **Run IDs:** `S001-37369303c7`; `research/traces/lane3/timestep.csv`
- **Search / parameter bounds:** as C009
- **Reproduction command:** as C001 and C009
- **Known caveats:** any speed claim, or speed comparison across rules or interventions, must
  state T and should be repeated at T ≥ 40.
- **History:**
  - 2026-10-07 — NUMERICALLY_FRAGILE — archivist, on Lane 3's timestep sweep.

### C011 — At R = 13, S001's travel heading locks onto a discrete set of lattice directions

- **Status:** INDEPENDENTLY_CHECKED
- **Owner lane:** Lane 3 and Lane 7
- **Sources:** lane3/README claim 3 "Heading lock" (PR #8, open); hostile-review HR-001b (PR #7, open)
- **Specimen / version:** S001, dossier commit `65c03cc`; start state rotated (bilinear)
- **Simulator / version:** `alm_check` @ `263ec66` (Lane 3); `ref` via `h001_explore.py` @ `c1df640` (Lane 7)
- **Parameters:** baseline, R = 13, 128². Lane 3: rotations 0–90° by 2.5° (37 runs), 800 time
  units, heading over t = 700–800. Lane 7: rotations 0–45° by 1° (46 runs), 8000 steps,
  heading in 1000-step windows; "settled" = change < 0.05° between the last two windows.
- **Intervention:** none (start-state rotation)
- **Metric:** late heading vs start rotation; continuum expectation is heading₀ − rotation
- **Result:** both lanes see a staircase of plateaus, symmetric under the lattice reflections.
  Shared plateaus: 68.20° (= atan 5/2, the baseline heading), 60.82°, ≈ 51.5°, ≈ 29.2°, 21.80°
  (= atan 2/5). Lane 7: 40 of 46 runs settle on 10 headings; no run ends in the gaps
  51.6–60.8°, 29.2–38.4°, 40.4–49.6°; near-diagonal runs wander 45° ± 1.3°.
- **Run IDs:** Lane 3 `research/traces/lane3/heading-R13.csv`; Lane 7 `H001-X1-R13-rot{0..45}` (`x1_R13.csv`)
- **Search / parameter bounds:** R = 13; rotations 0–90° (Lane 3), 0–45° (Lane 7)
- **Reproduction command:** `python -m alm_check.heading --R 13`; `h001_explore.py 13 1`
- **Known caveats:** heading at R = 13 is a grid property, so **heading and anything measured in
  the creature's frame are NUMERICALLY_FRAGILE as organism traits**. Some runs still drift after
  thousands of steps. The baseline heading also depends on T (C009). Behaviour at R = 26 is
  disputed (C012, C013).
- **History:**
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on agreement of Lane 3 and Lane 7 at R = 13.

### C012 — At R = 26 the heading lock mostly disappears

- **Status:** OBSERVED
- **Dispute:** D1, contradicted by C013. Lane 3 is rechecking. Lane 7 (HR-005) points out that
  Lane 3's own CSV repeats plateau headings at R = 26 (rotations 12.5°/15° → 53.28°, 30°/32.5° →
  36.72°, 65°/67.5° → 2.06°); the archivist confirmed these rows.
- **Owner lane:** Lane 3
- **Sources:** lane3/README claim 3 (PR #8, open)
- **Specimen / version:** S001, dossier commit `65c03cc`; cells upscaled bilinearly to R = 26, then rotated
- **Simulator / version:** `alm_check` @ `263ec66`
- **Parameters:** R = 26, T = 10, 256²; rotations 0–90° by 2.5° (37 runs); 800 time units, heading over t = 700–800
- **Intervention:** none (start-state rotation)
- **Metric:** late heading vs the continuum line heading₀ − rotation
- **Result:** heading follows the continuum line "with only a few short plateaus left"; speed
  0.4794–0.4798 at every angle.
- **Run IDs:** `research/traces/lane3/heading-R26.csv`
- **Search / parameter bounds:** 2.5° rotation step
- **Reproduction command:** `python -m alm_check.heading --R 26`
- **Known caveats:** Lane 3 notes some runs still drifting at t = 800 (up to 4.5°). Lane 7
  reports that a coarse 3° sweep hid the plateaus in its own data; Lane 3's step is 2.5°.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.

### C013 — At R = 26 the heading lock persists, weaker: 46 start rotations settle on 17 headings

- **Status:** INDEPENDENTLY_CHECKED (the plateau headings); the interpretation is disputed (D1)
- **Dispute:** D1, contradicts C012.
- **Owner lane:** Lane 7
- **Sources:** hostile-review HR-001b (PR #7, open)
- **Specimen / version:** S001, dossier commit `65c03cc`; cells zoomed bilinearly to R = 26, then rotated
- **Simulator / version:** `ref` via `h001_explore.py` @ `c1df640`
- **Parameters:** R = 26, T = 10, 256²; rotations 0–45° by 1° (46 runs); 8000 steps
- **Intervention:** none (start-state rotation)
- **Metric:** settled heading (change < 0.05° between the last two 1000-step windows)
- **Result:** 37 runs settle onto 17 headings, 9 still drifting; largest empty gap 6.1° (9.2° at
  R = 13). Plateaus of 2–4 consecutive rotations share one heading (rotations 10°–13° → 53.28°).
- **Run IDs:** `H001-X2-R26-rot{0..45}` (`x2_R26_fine.csv`); coarse sweep `x1_R26.csv`
- **Search / parameter bounds:** 1° rotation step, 0–45°
- **Reproduction command:** `h001_explore.py 26 1` (~25 min on 4 cores)
- **Independent check:** Lane 3's `alm_check` sweep (`heading-R26.csv`, distinct code and 2.5°
  grid) lands on the same plateau headings: 59.35, 53.28, 49.33, 46.54, 43.46, 42.09, 40.67,
  36.72, 30.65, 25.91°. The archivist compared the two files: 14 of Lane 3's 19 runs in 0–45°
  end within 0.01° of a Lane 7 final heading; the other 5 differ by 0.04–0.9° (3 of them still
  drifting by Lane 3's own measure).
- **Known caveats:** exploratory, not preregistered; not yet run on `alm`. Lane 3's
  `nearest_rational_slope` labels at R = 26 are off by up to 0.9°, so they are not evidence of
  rational-slope locking at R = 26 (HR-005).
- **History:**
  - 2026-10-07 — OBSERVED — Lane 7.
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, plateau headings matched in Lane 3's data
    (HR-005). D1 stays open until Lane 3 restates or defends C012.

### C014 — R = 13 is resolution-converged for S001's mean mass, size and speed (but not for mean anisotropy)

- **Status:** INDEPENDENTLY_CHECKED (mean mass); OBSERVED (speed, gyradius, anisotropy)
- **Owner lane:** Lane 3 and Lane 7
- **Sources:** lane3/README "Resolution (R) sweep" (PR #8); hostile-review HR-001 E1 and HR-003 point 3 (PR #7)
- **Specimen / version:** S001, dossier commit `65c03cc`; cells zoomed by R/13
- **Simulator / version:** `alm_check` @ `263ec66`; `ref` via `h001.py` / `aniso_check.py` @ `c1df640`
- **Parameters:** baseline with R varied (Lane 3 R = 8–52; Lane 7 R = 13–39)
- **Intervention:** none
- **Metric:** windowed means
- **Result:** mean ΣA/R² at R = 13 is within 0.03% of R = 52 (Lane 3) and within 2e−4 relative of
  R = 20–39 (Lane 7). Speed within 0.06% and gyradius within 0.03% of R = 52 (Lane 3). Mean
  anisotropy is 1.2% low at R = 13 (0.2953 vs 0.2989 / 0.2987 at R = 20 / 26; Lane 7).
- **Run IDs:** Lane 3 `resolution.csv`; `H001-E1-R{13,20,26,39}`; `aniso_check.txt`
- **Search / parameter bounds:** R = 8–52
- **Reproduction command:** `python -m alm_check.sweeps resolution`; `h001.py e1`; `aniso_check.py`
- **Known caveats:** T = 10 only. Fluctuations are not converged (C003).
- **History:**
  - 2026-10-07 — mean mass INDEPENDENTLY_CHECKED, rest OBSERVED — archivist.

### C015 — At R = 13, S001's speed depends on its locked heading by up to 1.2%

- **Status:** INDEPENDENTLY_CHECKED
- **Owner lane:** Lane 3
- **Sources:** lane3/README "Heading lock" (PR #8); Lane 7 HR-001b and HR-002 point 4 report ~0.2%
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check` @ `263ec66`
- **Parameters:** R = 13, rotations 0–90°
- **Intervention:** none
- **Metric:** speed over t = 700–800
- **Result:** 0.4794 R/time on the 5/2 and 2/5 plateaus, 0.4778 at ±12.68°, ≈ 0.474 near the
  axis. At R = 26: 0.4794–0.4798 at every angle.
- **Run IDs:** `research/traces/lane3/heading-R13.csv`, `heading-R26.csv`
- **Search / parameter bounds:** rotations 0–90° by 2.5°
- **Reproduction command:** `python -m alm_check.heading --R 13`
- **Independent check:** Lane 7 `heading_means.py` (`ref`, HR-006): 0.47941 at 68.2°, 0.47783 at
  12.67°, 0.47343 at −0.46° (R = 13); 0.47966 vs 0.47969 at 67.1° and −2.1° (R = 26).
- **Known caveats:** Lane 7's earlier ~0.2% figure (HR-001b) covered only headings 21.8°–68.2°.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on Lane 7 HR-006.

### C016 — S001 dies from the catalog cells at R ≤ 7 or T ≤ 3; survival at R = 8–10 is non-monotone and depends on how the cells are resampled

- **Status:** OBSERVED
- **Owner lane:** Lane 3
- **Sources:** lane3/README claim 6 (PR #8, open)
- **Specimen / version:** S001, dossier commit `65c03cc`; nearest-neighbour (z0) and bilinear (z1) resampling
- **Simulator / version:** `alm_check` @ `263ec66`
- **Parameters:** R = 5–52 at T = 10; T = 1–320 at R = 13
- **Intervention:** none
- **Metric:** fate "persists" = mass > 1e−10 at t = 400 and no blow-up
- **Result:** dies at R = 5, 6, 7 (both zooms) and T = 1, 2, 3. R = 8: z0 dies, z1 lives; R = 9 lives;
  R = 10: z0 dies, z1 lives; R ≥ 11 lives.
- **Run IDs:** `research/traces/lane3/resolution.csv`, `timestep.csv`
- **Search / parameter bounds:** as above
- **Reproduction command:** `python -m alm_check.sweeps resolution`; `... timestep`
- **Known caveats:** 400 time-unit horizon; single path.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.

### C017 — S001's statistics are identical on any periodic torus from 32² to 256²

- **Status:** OBSERVED
- **Owner lane:** Lane 3
- **Sources:** lane3/README claim 5, "Boundary and precision" (PR #8, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check` @ `263ec66`
- **Parameters:** baseline with N ∈ {32, 40, 44, 48, 52, 56, 64, 96, 128, 256}
- **Intervention:** none
- **Metric:** mass, speed, heading, gyradius
- **Result:** mass 0.435803, speed 0.47942, heading 68.198° at every N (differences ≤ 2e−5);
  gyradius +0.1% at N = 32 because the periodic gyradius is truncated at N/2.
- **Run IDs:** `research/traces/lane3/boundary.csv`
- **Search / parameter bounds:** N = 32–256
- **Reproduction command:** `python -m alm_check.sweeps boundary`
- **Known caveats:** single path; T = 10, R = 13.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.

### C018 — In a dead-edge (zero-padded) box S001 slides along the wall and parks alive in a corner

- **Status:** OBSERVED
- **Owner lane:** Lane 3
- **Sources:** lane3/README claim 5 (PR #8, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check` @ `263ec66`, real-space path with zero padding
- **Parameters:** baseline rule, 128² box with zero boundary
- **Intervention:** boundary condition change (not upstream semantics; upstream is always periodic)
- **Metric:** alive (mass > 1e−10), centroid, mass over 4000 steps
- **Result:** bitwise equal to the torus before wall contact (tested); reaches the bottom wall at
  ≈ step 100, sits in the corner at centroid (122, 122) from ≈ step 200, alive to step 4000 with
  mass 0.31–0.39 and ≈ 10% fluctuations.
- **Run IDs:** `research/traces/lane3/boundary.csv`
- **Search / parameter bounds:** one box size, one start position
- **Reproduction command:** `python -m alm_check.sweeps boundary`
- **Known caveats:** single run; candidate for Lane 6.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.

### C019 — S001's statistics are robust to float32 precision; its exact trajectory is not

- **Status:** OBSERVED
- **Owner lane:** Lane 3
- **Sources:** lane3/README "Boundary and precision" (PR #8, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check` @ `263ec66`, float32 vs float64
- **Parameters:** baseline
- **Intervention:** precision change
- **Metric:** mass, speed, heading
- **Result:** mass 0.435755 vs 0.435803 (−0.01%), speed +0.02%, heading 68.04° vs 68.20°.
- **Run IDs:** `research/traces/lane3/precision.csv`
- **Search / parameter bounds:** two precisions
- **Reproduction command:** `python -m alm_check.sweeps precision`
- **Known caveats:** single path.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.

### C020 — S001 is elongated along its direction of travel (major axis within 0.3° of heading; dominant rotational harmonic k = 2)

- **Status:** REPRODUCED
- **Owner lane:** Lane 5
- **Sources:** L5-baseline "What this says" item 3 (PR #4 merged; PR #9 open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref` and `alm`; `alm.morphometrics`
- **Parameters:** baseline, rotations 0°, 23°, 45°
- **Intervention:** none
- **Metric:** second-moment major axis minus heading; rotational harmonics, steps 1000–4000
- **Result:** major axis − heading = −0.05°, +0.27°, +0.05°; a₂ ≈ 0.216.
- **Run IDs:** `research/experiments/L5-baseline/summary.csv`
- **Search / parameter bounds:** three start rotations (two independent headings)
- **Reproduction command:** `.venv/bin/python research/experiments/L5-baseline/measure_s001.py`
- **Known caveats:** R = 13 only. Lane 7 found `rotational_harmonics` reaches 0.033 on an
  isotropic body from lattice sampling alone (C021); a₂ = 0.216 is well above that. From PR #9
  @ `c5d2435` the harmonics are radius-weighted; the regenerated a₂ is 0.216 ± 0.002 / 0.214 ±
  0.012 / 0.216 ± 0.002, so the claim is unchanged.
- **History:**
  - 2026-10-07 — REPRODUCED — Lane 5 (two stepping paths).

### C021 — `alm.morphometrics.symmetry_order` reports lattice symmetry (8, 4 or 6) for an isotropic body

- **Status:** OBSERVED
- **Owner lane:** Lane 7
- **Sources:** hostile-review HR-003 point 1 (PR #7, open; also posted on PR #4)
- **Specimen / version:** synthetic isotropic Gaussian, σ = 6 cells (not a Lenia specimen)
- **Simulator / version:** `alm.morphometrics` as of `1d85475`
- **Parameters:** 128² grid; centre (64, 64), (64.5, 64.5), (64.3, 64.7)
- **Intervention:** none
- **Metric:** `symmetry_order`, `rotational_harmonics`
- **Result:** order 8, 4 or 6 depending only on sub-pixel centre; harmonics up to 0.033.
- **Run IDs:** none recorded (snippet in HR-003)
- **Search / parameter bounds:** three centres
- **Reproduction command:** see HR-003; Lane 7 suggests a test that an isotropic Gaussian reports no symmetry order
- **Known caveats:** tooling claim about `alm.morphometrics` up to `1849dbe`. Any symmetry-order
  result needs a noise floor from isotropic controls.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 7.
  - 2026-10-07 — tool fixed — Lane 5 (PR #9 @ `c5d2435`): harmonics are radius-weighted, and
    `symmetry_order` returns 0 below `SYMMETRY_FLOOR = 0.05` (isotropic Gaussians sd 3–8 cells
    < 0.03, hard disk r = 8 < 0.04), with a test. The claim stays as a record of the old behaviour;
    results computed with the old function before `c5d2435` inherit it.

### C022 — S001's mass and gyradius means are heading-invariant to 0.2% at R = 13 and 26; at R = 26 anisotropy and speed are too

- **Status:** OBSERVED
- **Owner lane:** Lane 7 (with Lane 5's original data)
- **Sources:** hostile-review HR-006 (PR #7 @ `0fd42ee`, open); L5-baseline (C007) and Lane 5's
  restated claim 1 (PR #9 @ `c5d2435`, open): "mass and gyradius means heading-invariant to 0.2%
  at R = 13 across 21.8°, 40.4°, 68.2° and the axis plateau; speed to 1%"
- **Specimen / version:** S001, dossier commit `65c03cc`; start states rotated (bilinear), zoomed for R = 26
- **Simulator / version:** `ref` via `heading_means.py` @ `0fd42ee`
- **Parameters:** baseline rule, T = 10; R = 13 (rotations 0°, 27°, 55°, 70°) and R = 26 (0°, 67°)
- **Intervention:** none
- **Metric:** means over steps 2000–5999 of mass, gyradius, anisotropy, speed
- **Result:** R = 13: mass 0.43557–0.43611, gyradius 0.43764–0.43861 across headings −0.5°…68.2°.
  R = 26 (67.1° vs −2.1°): mass 0.43589/0.43588, gyradius 0.43755/0.43759, anisotropy
  0.2987/0.2993, speed 0.47966/0.47969.
- **Run IDs:** `research/experiments/H001-lattice-wobble/heading_means.csv`
- **Search / parameter bounds:** four headings at R = 13, two at R = 26
- **Reproduction command:** `heading_means.py 13 0 27 55 70; heading_means.py 26 0 67`
- **Known caveats:** on the diagonal plateaus the mass and gyradius means agree between Lane 5
  (`ref` and `alm`, `alm.morphometrics`) and Lane 7 (`ref`, own code) to 0.2%; the axis plateau and
  the R = 26 values come from Lane 7 alone, so the status stays OBSERVED. Only two headings at
  R = 26; T = 10 only.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 7.
  - 2026-10-07 — Lane 5 adopts the mass/gyradius restatement (PR #9 @ `c5d2435`).

### C023 — Each of four standardized disturbances has a single sharp RECOVERED → DIED edge for S001, at small strength, with no intermediate outcomes

- **Status:** OBSERVED
- **Owner lane:** Lane 4
- **Sources:** `research/experiments/L4-001-disturbance-battery/protocol.md` (preregistered at
  `aa4cd5c`) and `results/summary.md`, `results/bisect-brackets.csv` (commit `12d9265`, PR #5,
  open). Lane 4 has **not** yet proposed a claim; this entry was written by the archivist from the
  generated summary and will be replaced by Lane 4's own wording.
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref` (`reconstruct.py`), interventions in `src/alm/disturb.py` @ `12d9265`
- **Parameters:** baseline rule, 128² torus; intervention at t0 = 1000…1004 (five phase replicates),
  horizon 2000 steps
- **Intervention:** I001 mass attenuation A ← (1 − s)A; I002 central disc deletion, radius s·R;
  I003 frontal Gaussian addition, peak s, at 1.0 R ahead, w = 0.25 R; I004 port-side cut removing
  fraction s of mass. Placed in the creature frame at t0.
- **Metric:** preregistered classes on the last 500 steps: DIED (mass < 0.01), EXPLODED, RECOVERED
  (mass, gyradius, window speed within ±20% of the dossier baseline), TRANSFORMED. Sharp = all five
  phase s* within 0.05 and the coarse sweep monotone.
- **Result:** 410 coarse + 160 bisection runs; every run is RECOVERED or DIED, none TRANSFORMED or
  EXPLODED, and no run changes class under ±10% or ±30% bands. Transition s* (bisected to 1/256):
  I001 0.1016 at every phase (≈ 10% mass removed kills); I002 radius 0.061–0.086 R (1.6–7% mass);
  I003 peak 0.308–0.317 (≈ +28% mass); I004 0.080–0.089 of mass. All four are sharp by the
  preregistered rule (largest phase spread 0.025, I002).
- **Run IDs:** `L4-001-<intervention>-s<strength>-t<t0>-N128-ref` (deterministic), rows in
  `results/coarse.csv` and `results/bisect.csv`
- **Search / parameter bounds:** coarse grids 0–0.95 or 0–1.00 by 0.05; phases t0 = 1000–1004
- **Reproduction command:** see `research/experiments/L4-001-disturbance-battery/run.py` and `analyze.py`
- **Known caveats:** single execution path (`alm` re-run and N = 192 re-run are still to come per the
  protocol). Amendment A1 preregisters T = 20 and R = 26 re-runs, not yet reported. Lane 7
  (HR-002) objects that five consecutive t0 sample only a thin slice of the 2-D lattice phase,
  and that post-recovery heading should be recorded (C011). Recovery is judged against
  T = 10 / R = 13 baseline numbers, which are themselves discretisation-dependent (C009, C010).
- **History:**
  - 2026-10-07 — OBSERVED — archivist, from Lane 4's generated summary at `12d9265`.

### C024 — S001's short-period (2–15 step) feature fluctuations on the diagonal plateaus shrink with resolution

- **Status:** INDEPENDENTLY_CHECKED
- **Owner lane:** Lane 5 (restated claim 2), Lane 7 (independent check)
- **Sources:** L5-baseline restated claim 2 (PR #9 @ `c5d2435`, open), which replaces C008;
  hostile-review HR-003 point 2 (PR #7, open)
- **Specimen / version:** S001, dossier commit `65c03cc`; cells zoomed to R (bilinear)
- **Simulator / version:** Lane 5: `alm` + `alm.morphometrics` (`axis_breathing.py` @ `c5d2435`).
  Lane 7: `ref` + independent second-moment code (`aniso_check.py` @ `c1df640`).
- **Parameters:** baseline rule, T = 10, start rotation 0; R = 13 / 20 / 26 on 128 / 198 / 256 grids
- **Intervention:** none
- **Metric:** sd of anisotropy (1 − λmin/λmax) over the analysis window
- **Result:** Lane 7 4.8e−3 → 3.1e−3 → 1.4e−3; Lane 5 4.8e−3 → 3e−3 → 1e−3 (R = 13 / 20 / 26). The
  8.0-step anisotropy component at R = 13 is absent at R = 20 and 26.
- **Run IDs:** `research/experiments/L5-axis-breathing/results.csv` rows (R, 0);
  `research/experiments/H001-lattice-wobble/aniso_check.txt`
- **Search / parameter bounds:** three resolutions, one heading family (diagonal plateau)
- **Reproduction command:** `.venv/bin/python research/experiments/L5-axis-breathing/axis_breathing.py`; `aniso_check.py`
- **Known caveats:** anisotropy only; other features' fluctuations were checked for mass (C003) but
  not individually for gyradius or area. T = 10 only.
- **History:**
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, Lane 5 (`alm`) and Lane 7 (`ref`, own code) agree.

### C025 — S001 travelling along a grid axis at R = 13 "breathes": a slow, large shape oscillation (anisotropy 0.09–0.50) that is absent at R = 26

- **Status:** NUMERICALLY_FRAGILE
- **Owner lane:** Lane 5
- **Sources:** `research/experiments/L5-axis-breathing/README.md` (PR #9 @ `c5d2435`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`; cells zoomed and rotated (bilinear) as in H001 `initial_state`
- **Simulator / version:** `alm` (Lane 2) + `alm.morphometrics` @ `c5d2435`
- **Parameters:** baseline rule, T = 10; (R, start rotation) ∈ {(13, 0), (13, 70), (20, 0), (20, 70),
  (26, 0), (26, 67)}; grids 128 / 198 / 256
- **Intervention:** none (start-state rotation onto the axis plateau)
- **Metric:** anisotropy mean, sd, range and dominant period; per-step heading sd; steps 2000–7999
- **Result:** R = 13 axis run (heading 0.22°): anisotropy 0.267 ± 0.094, range 0.087–0.500, dominant
  period 140 steps (247 in a shorter preliminary window), heading sd 4.2° per step, speed 0.4751.
  On the 68.2° plateau: 0.295 ± 0.005, heading sd 1.6°. R = 26 run 2.06° off axis: 0.299 ± 0.010, no
  slow component. R = 20 did not land on the axis (−5.5°): 0.293 ± 0.012.
- **Run IDs:** `research/experiments/L5-axis-breathing/results.csv` (6 rows)
- **Search / parameter bounds:** one axis-locked run per R; 8000 steps
- **Reproduction command:** `.venv/bin/python research/experiments/L5-axis-breathing/axis_breathing.py`
- **Known caveats:** single stepping path for the oscillation itself; Lane 7's independent code
  agrees only on the mean anisotropy (0.2649 vs 0.2665, different windows). The period depends
  on the window (quasi-periodic). The R = 13 → 26 transition is unresolved because R = 20 missed
  the axis. Example of a behaviour that must not be nicknamed as a phenotype (fails the
  resolution criterion).
- **History:**
  - 2026-10-07 — NUMERICALLY_FRAGILE — Lane 5 proposed; archivist ledgered.
