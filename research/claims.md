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
- **Prior literature:** (optional; see Literature provenance)
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
  at the other and at the [Disputes](#disputes) table. The archivist does not pick a
  winner; the status changes only when new evidence lands.

### Literature provenance

The claims archivist keeps a **Prior literature** field on substantive claims. It records what
published work already says about the same behaviour.

- **When:** a claim reaches REPRODUCED or INDEPENDENTLY_CHECKED, or a lane proposes something as
  new. The archivist runs one bounded search when that finding lands. There is no timed sweep and
  no exhaustive survey.
- **Where:** the searches cover the original Lenia papers, the Chakazul catalog, later Lenia
  papers, and adjacent fields where a mechanism might already be known. Every source gets a key
  in [`references.md`](references.md), which also logs each search's date, queries and gaps.
- **Each entry gives:**
  - the reference key;
  - a precise locator (section, figure or page);
  - an evidence grade, one of:
    - *full text*: read in the paper at a named version;
    - *code*: checked in the authors' code, which supports rule and method only;
    - *excerpt*: seen only in search excerpts, so unverified;
  - one relationship class;
  - a **conditions** note. The note says either *same conditions* (same rule, specimen and
    intervention) or *similar outcome only*, and names what differs. Rule, numerics and
    intervention are each compared.
- An *excerpt*-only entry is provisional. It is rechecked when the full text becomes reachable,
  and downgraded or removed if the full text does not support it.

| Relationship | Meaning |
| --- | --- |
| `PREVIOUSLY REPORTED` | The source describes the same behaviour. A *similar outcome only* note says how far the conditions match. |
| `CONSISTENT WITH` | The source reports something our claim agrees with or would predict, but not the claim itself. |
| `RELATED` | The source covers the same question or a nearby mechanism without bearing directly on the claim. |
| `CONTRADICTORY` | The source reports, under conditions it names, something our claim says should not happen. The disagreement is recorded, not resolved, as with lane disputes. |
| `NO MATCH FOUND IN SEARCHED SOURCES` | Nothing was found in the logged search. This is never evidence of novelty. |

Rules:

- Literature never changes a claim's status. Agreement with a paper is not reproduction of our
  experiment, and only our own runs move a status.
- A failed search supports no novelty claim. "New" needs a positive comparison, such as C043's
  catalog check, and even then is worded as "not found in …".

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

## Disputes

| Dispute | Claims | Lanes | State |
| --- | --- | --- | --- |
| D1: does S001's heading stay lattice-locked at R = 26? | C012 vs C013 | Lane 3 vs Lane 7 | **resolved 2026-10-07** in favour of C013. Lane 3's finer, longer sweep (PR #8 @ `5f316f3`, `heading-R26-fine-long.csv`) found 20 settled headings from 46 starts and Lane 3 withdrew C012. |
| D2: does S102 at its registered rule survive refinement to R = 26? | C039 vs C047 | Lane 6 vs Lane 3 | **resolved 2026-10-07** in favour of C047. Lane 6 reran Lane 3's four seed resizes in `field.py` (`d2_resize.py`, `d2-resize.csv` in `research/experiments/L6-007-attractor-geography/` (PR #23 @ `413003d`, merged as `7a4ea3b`)): block, nearest and cubic seeds are healthy circlers at R 26 and 39 for 1000 tu, and only the bilinear seed dies (8.3 and 6.0 tu). Lane 6 conceded C039 and proposed REFUTED. The refutation rests on Lane 3's merged evidence (PR #18); Lane 6's rerun (merged in PR #23) independently checks it for these eight seeds. The death is resize-method dependence, not resolution dependence. |

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
| Lane 3 PR #8 @ `5f316f3`: corrected claim 3, new claim 7 (L4-001 replication) | C012, C013, C023, C026, C027 |
| Lane 4 L4-001 README proposed claims 1 / 2 / 3 / 4 / 5 (PR #5 @ `7bd1a42`) | C023 / C026 / C028 / C029 / C030 |
| Lane 4 protocol amendment A3 (size-independent centroid) | C023 |
| Lane 5 L5-002 README proposed claims 1 / 2 / 3, plus the exploratory 6 tu rule (PR #9 @ `bd86e76`; claims 1–2 reworded @ `f6239f6`) | C031 / C032 / C034, C033 |
| Lane 7 hostile-review HR-008 (L5-002 review, edge-state λ) | C029, C031, C032 |
| Lane 5 L5-003 README proposed claims 1 / 2 / 3 (PR #9 @ `f6239f6`) | C035 / C036 / C037 |
| Lane 6 L6-field README proposed claims L6-a / L6-b / L6-c / L6-d / L6-e (PR #11 @ `83c8bff`, merged as `f72db9e`) | C038, C039 / C040 / C041 / C043 / C045 |
| Lane 6 S103 dossier (fixed point), L6-field negative results | C042, C044 |
| Lane 6 L6-005 control runs at t0 = 3000/3002 | C023 caveat |
| Lane 7 hostile-review HR-007 (C023 world size, thresholds) | C023, C026 |
| Lane 9 wording note (C026 title overstates the 10% uniform survival) | C026 |
| Lane 6 | not started |
| Lane 3 L3-002 README proposed claims 1 / 2 / 3 / 4 / 5 / 6 (PR #18, merged as `56ae421`; wording scoped in `ab125c4`) | C046 / C047 (D2 with C039) / C048 / C049 / C050 / C051 |
| Lane 6 L6-007 D2 rerun of the S102 seed resizes (PR #23 @ `413003d`, merged as `7a4ea3b`) and Lane 6's concession of C039 | C039, C047 (D2 resolved; C047 INDEPENDENTLY_CHECKED for the eight seeds) |
| Lane 4 L4-002 lone-Orbium baselines (PR #20, merged as `560472c`) | none: a reference dataset with no claim proposed; not evidence for or against pair coupling (that is Lane 6's L6-008) |
| REEF expedition 2026-10-20 (reef/coordinator integration PR; lanes reef/field, reef/numerics, reef/behavior) | C052 / C053 / C054 / C055; amendments to C038, C041 |
| VIS-talk lightning-talk thread 2026-11-07 (`research/experiments/VIS-talk/`, gallery G007–G013) | C056 / C057 / C058 |
| VIS-talk round two 2026-11-07 (gallery G014–G018) | C059 / C060 |
| Species hunt 2026-11-10 (`research/experiments/SPECIES-scout/`, gallery G021) | C063 (C061–C062 reserved by the open fractal PR #44) |
| Replicators thread 2026-11-14 (`research/experiments/REPLICATORS/`, gallery G029–G031) | C072 / C073 / C074 / C075 |
| Evolution soup thread 2026-11-14 (`research/experiments/SOUP/`, gallery G032–G034) | C076 / C077 / C078 |
| Collision zoo 2026-11-14 (`research/experiments/ZOO/`, gallery G035–G037, museum room 78) | C080 / C081 / C082 / C083 |
| Collision zoo round 2, 2026-11-14 (`research/experiments/ZOO/`, gallery G047–G048, room 78) | C093 / C094 / C095; history line on C081 |

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
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  - [Chan2019] §3.1.1 and Fig. 7(a–b), p. 17 *(full text)*. **CONSISTENT WITH.** For R = 9–55
    at T = 10, Orbium's mass, gyradius and speed "remain constant". Each data point there is
    averaged over 300 steps, so a wobble would average out and was not measured.
    Similar outcome only: μ 0.15, σ 0.016, with core functions not stated.
  - [Davis2024] p. 20 and Fig. 5 *(full text)*. **RELATED.** Davis classes its Orbium as
    "Platonic": finer discretization does not destroy it. The paper is about persistence, not
    wobble amplitude. Its Orbium uses a Gaussian kernel and Gaussian growth (p. 11), not S001's
    rule.
  - [Cool2026] "Measuring recovery", p. 2 *(full text)*. **RELATED.** At finite resolution a
    creature's pixels "fluctuate slightly at each step, and differently so depending on the
    creature's angle relative to the axes of grid symmetry". This is a qualitative remark about
    S001's rule at higher resolution, not a measurement.
  - Wobble amplitude falling with R: **NO MATCH FOUND IN SEARCHED SOURCES.**
- **History:**
  - 2026-10-07 — OBSERVED — Lane 1 proposed the lattice account from three start rotations.
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on agreement of Lane 7 (`ref`) and Lane 3 (`alm_check`).
  - 2026-10-07 — caveat added — Lane 7 HR-005: amplitude–R relation confounded with heading; exponent dropped.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.

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
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  - [Chan2019] §3.1.2 and Fig. 7(c–d), p. 17 *(full text)*. **PREVIOUSLY REPORTED** (direction
    of the effect). At R = 13 over T = 4–2560, mass and gyradius go down and speed goes up as T
    increases, approaching a limit. Chan reads Lenia as the Euler discretization of an ODE.
    Similar outcome only: μ 0.15, σ 0.016, with core functions not stated. The paper gives no
    percentage at T = 10, so our 16–17% speed deficit and 2.6% mass excess are not compared.
  - [Kojima2023] §2.1.2–2.1.3 and Figs. 2–3, pp. 4–5 *(full text)*. **RELATED.**
    - Classic Lenia's Orbium "disappeared both when the size of the time step was large
      (dt = 0.5) and when it was small (dt = 0.002)". Removing the upper clip rescued it at small
      dt.
    - This is in tension with Chan 2019 Fig. 7(c), which runs to T = 2560. Kojima states neither
      the kernel nor the horizon.
    - Our T range stops at T = 320 (dt ≈ 0.003). Whether S001 survives at T ≥ 500 is an open
      numerical-ecology test, not settled by either paper.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3.
  - 2026-10-07 — refined — Lane 7 HR-005: deficit 16.6% under a geometric fit.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate (from the Chan 2019 full-text pass).
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.
  - 2026-10-07 — supported — direct runs at T 640–2560 land on the extrapolated limit (C051, same
    engine); L3-002 extends the timestep bias to S101 and S102 (C046). Status unchanged.

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
  thousands of steps. The baseline heading also depends on T (C009). The lock weakens but
  persists at R = 26 (C013).
- **History:**
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on agreement of Lane 3 and Lane 7 at R = 13.

### C012 — At R = 26 the heading lock mostly disappears

- **Status:** REFUTED (withdrawn by Lane 3)
- **Dispute:** D1, resolved in favour of C013. Lane 7 (HR-005) points out that
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
  - 2026-10-07 — REFUTED — Lane 3 (PR #8 @ `5f316f3`): with 1° steps over 32 000 steps the 46
    starts settle on 20 headings, on plateaus 2–5° wide; the 2.5° sweep had stepped over them.

### C013 — At R = 26 the heading lock persists, weaker: 46 start rotations settle on 17 headings

- **Status:** INDEPENDENTLY_CHECKED
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
- **Second independent sweep (Lane 3, PR #8 @ `5f316f3`):** `alm_check`, 1° steps over 0–45°,
  3200 time units (32 000 steps). Distinct headings within 0.1°: 22 at t = 800, 20 at t = 1600,
  2400 and 3200; 39 of 46 starts share a heading with a neighbour; largest empty gap 5.6°
  (9.3° at R = 13). Settled headings hold to ±0.03° from t = 1600 to 3200. The 17-vs-20 count
  difference is clustering tolerance and horizon. Data: `research/traces/lane3/heading-R26-fine-long.csv`;
  command `python -m alm_check.heading --R 26 --step 1 --max-angle 45 --horizon 3200 --tag=-fine-long`.
- **Known caveats:** exploratory, not preregistered; not yet run on `alm`. Lane 3's
  `nearest_rational_slope` labels at R = 26 are off by up to 0.9°, so they are not evidence of
  rational-slope locking at R = 26 (HR-005).
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  - [Chan2019] §3.1.1 (p. 15) and Fig. 6(d–g) (p. 16) *(full text)*. **RELATED.**
    - "Minimally affected by rotation" for R > 12 comes from one visual test: a pattern rotated
      77° at **R = 185** with exponential cores, showing "no visible effect".
    - It does not measure the long-run heading at R ≈ 13–26, so it neither supports nor
      contradicts a slow lock onto discrete headings.
  - [Cool2026] "Measuring recovery", p. 2 *(full text)*, and repository README *(code)*.
    **RELATED.** The authors note that a creature's pixels fluctuate "differently so depending on
    the creature's angle relative to the axes of grid symmetry". They use S001's rule at R = 52
    in float32. They describe the effect but do not measure heading lock.
  - [HoffmanMalletParet2010] §1 and Theorems 1.1–1.2 *(full text)*. **RELATED** (adjacent field).
    Travelling fronts on the Z² lattice are pinned in some lattice directions while moving in
    nearby ones. These are fronts, not gliders: a candidate mechanism family, not prior evidence.
  - Heading lock of Lenia gliders to lattice directions: **NO MATCH FOUND IN SEARCHED SOURCES.**
- **History:**
  - 2026-10-07 — OBSERVED — Lane 7.
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, plateau headings matched in Lane 3's data
    (HR-005). D1 stays open until Lane 3 restates or defends C012.
  - 2026-10-07 — D1 resolved — Lane 3's 32 000-step 1° sweep agrees; Lane 3 withdrew C012.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.

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
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  - [Chan2019] Fig. 7(a–b), p. 17 *(full text)*. **PREVIOUSLY REPORTED** (mean statistics).
    - For R = 9–55 at T = 10, Orbium's mass, growth, gyradius, growth–centroid distance and
      speed "remain constant", each averaged over 300 steps, and the niche stays static.
    - Similar outcome only: μ 0.15, σ 0.016, with core functions not stated, against S001's
      poly/poly rule at σ 0.015.
    - Anisotropy is not reported there.
- **History:**
  - 2026-10-07 — mean mass INDEPENDENTLY_CHECKED, rest OBSERVED — archivist.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate (from the Chan 2019 full-text pass).
  - 2026-10-07 — extended — L3-002 finds R 13 within 0.5% of R 39 for S101 and S102 too (C046). Status unchanged.

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

### C023 — S001 has a single sharp, all-or-nothing survival edge for each of four standardized disturbances

- **Status:** INDEPENDENTLY_CHECKED at T = 10, R = 13 (Lane 4 on `ref` + `alm`; Lane 3 on
  `alm_check` with its own battery code). The exact I003 and I004 edge values are
  NUMERICALLY_FRAGILE in T (C027).
- **Owner lane:** Lane 4
- **Sources:** `research/experiments/L4-001-disturbance-battery/protocol.md` (preregistered at
  `aa4cd5c`) and `results/summary.md`, `results/bisect-brackets.csv` (commit `12d9265`, PR #5,
  open). Lane 4's own wording is proposed claim 1 in
  `research/experiments/L4-001-disturbance-battery/README.md` (PR #5 @ `7bd1a42`), which replaced
  the archivist's provisional title.
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
- **Lane 4's statement (README, mass terms):** I001 survives ≤ 10.0% loss, dies ≥ 10.3% (all phases);
  I002 survives 3.9–4.0%, dies 5.2–5.4%; I004 edge at 7.8–9.1% loss; I003 edge at +27.5–28.7% gain.
  Below the edge, recovered bodies correlate with the unperturbed control at r ≥ 0.990; above it,
  mass collapses 30–80 steps after the edit.
- **Run IDs:** `L4-001-<I>-s<strength 6dp>-t<t0>-N<N>-<engine>[-T20|-R26][-cL]` (deterministic; the
  format changed in amendment A2), rows in `results/coarse.csv`, `results/bisect.csv`,
  `results/bisect-brackets.csv`, `results/check-*.csv`
- **Search / parameter bounds:** coarse grids 0–0.95 or 0–1.00 by 0.05; phases t0 = 1000–1004
- **Reproduction command:** `research/experiments/L4-001-disturbance-battery/reproduce.sh` (stages `base`, `checks`, `a1`, `states`, `analyze`)
- **A1 (Lane 4, single phase t0 = 100 time units):** T = 20: I001 +3%, I002 unchanged in mass, I003
  +11%, I004 +11%. R = 26 (zoomed 2×, N = 256): I001 −3%, I002 unchanged in mass, I003 and I004
  unchanged. Agrees with Lane 3's T = 40 and R = 26 runs (C027).
- **A3 (Lane 4):** with a size-independent centroid (`disturb.local_centroid`, suffix `-cL`),
  40/40 bracket ends agree between N = 128 and 192 (`check-ref-N128-cL.csv`, `check-ref-N192-cL.csv`).
  Against the original brackets the same three runs flip, so those three edges sit one bisection
  step lower; the I002 edge does not move in mass units. Same finding as HR-007.
- **Robustness re-runs (commit `0e2cbe2`, `results/check-*.csv`):** the archivist compared each
  re-run's class with the `ref` bisection bracket (`s_ok` → RECOVERED, `s_fail` → DIED):
  - `alm` engine, N = 128 (`check-alm-N128.csv`): **40 of 40 bracket ends match.**
  - 5000-step horizon on `ref` (`check-ref-N128-H5000.csv`): 8 of 8 match; no late class changes.
  - N = 192 torus on `ref` (`check-ref-N192.csv`): 37 of 40 match. Three `s_ok` runs DIE at N = 192:
    I002 s = 0.0594 at t0 = 1000, I002 s = 0.0781 at t0 = 1004, I003 s = 0.3156 at t0 = 1003. So the
    edge sits up to one bisection step lower on the larger torus for some phases. Lane 4 has not
    commented on this yet.
- **Independent replication (Lane 3, PR #8 @ `5f316f3`):** `alm_check.disturb` re-implements the
  battery from `protocol.md` alone (no Lane 2 or Lane 4 code), bisected to 1/1280. The archivist
  checked `disturb-T10-R13-brackets.csv` against Lane 4's `bisect-brackets.csv`: **all 20 of
  Lane 3's s\* fall inside Lane 4's brackets.** Across 1260 runs (T10/R13, T40/R13, T10/R26) every
  failure is DIED. At R = 26 every edge stays put and the phase spread shrinks 3–6× (I003
  0.0078 → 0.0023, I004 0.0094 → 0.0016): I001 0.0988–0.0996, I002 0.0809–0.0902 R,
  I003 0.3074–0.3098, I004 0.0801–0.0816.
- **World size (Lane 7 HR-007, PR #7 @ `a2a1d2a`):** the 3 N = 192 deaths are not a torus effect.
  The creature states at t0 agree to 9e−6. The circular-mean centroid used to place I002–I004
  has an N-dependent bias (≈ 0.007/0.012 cells at N = 128, 0.003/0.005 at 192). Moving the edit
  by that much adds a fourth pixel to the I002 disc (ΔM −3.97% → −5.3%) or shifts the I003
  Gaussian. Swap test: at N = 128 with N = 192's centroid, all 3 die. With a bias-corrected
  centroid, **40 of 40 classes agree between N = 128 and 192**; the same 3 survive-side runs then
  die at N = 128 too. Files: `research/experiments/HR007-c023-world-size/` (`swap.csv`, `refined.csv`).
- **Thresholds (HR-007):** the ±20% bands never bind. Survive-side runs stay inside the band;
  failures reach mass < 0.01 within 46 (I001), 74 (I003) and 48 (I004) steps of the edit, with
  no long slowing-down near the edge (`deathtime.txt`).
- **Known caveats:** the I002/I003 bracket positions depend on the centroid estimator at the
  bisection resolution, so each edge is known to ±1 bisection step (±0.003 in s), as Lane 4 now
  states. Report I002 as removed mass, not
  radius: at R = 13 three central cells (3.9–4.0% of mass) survive and four (5.2–5.4%) die at
  every phase (Lane 3, HR-007). I003 and I004 shift 11–13% at T = 40 (C027). Phase replicates
  are consecutive steps and sample only a thin line through the 2-D sub-pixel phase (HR-002, open).
  Lane 6's control runs (L6-005, `research/experiments/L6-field/switch-T10-R13.csv`, PR #11 @
  `83c8bff`, own copy of the I001–I004 code and a batched stepper matching `alm` bitwise) apply
  I001 s = 0.10 at t0 = 3000 and 3002: the creature survives at 3000 but **dies at 3002**
  (archivist checked the CSV). That phase lies outside Lane 4's five, so the "survives 10.0% at
  every phase" wording holds only for t0 = 1000–1004; the I001 edge sits within about 0.002 of
  0.10 and its phase dependence is not fully sampled. Amendment A1 preregisters T = 20 and R = 26 re-runs, not yet reported. Lane 7
  (HR-002) objects that five consecutive t0 sample only a thin slice of the 2-D lattice phase,
  and that post-recovery heading should be recorded (C011). Recovery is judged against
  T = 10 / R = 13 baseline numbers, which are themselves discretisation-dependent (C009, C010).
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  - [Chan2019] §4.2.4, p. 39 *(full text)*. **RELATED.** Lenia patterns are "surprisingly
    resilient" and "absorb deformations". This is a qualitative remark with no intervention scale
    and no thresholds.
  - [Hamon2025] arXiv v1, Movies S3–S4, pp. 23–24 *(full text)*. **RELATED.** Orbium "dies from
    perturbations by obstacles", and collisions of several Orbium lead "to death/explosion".
    Similar outcome only: movies of an added obstacle channel, with no strength scale.
  - [Cool2026] p. 4 *(full text)*. **RELATED.**
    - Informational occlusions push creatures toward "death, metamorphosis, or explosion",
      depending on their extent and location.
    - Similar outcome only: S001's rule at R = 52 in float32, but no mass is removed.
    - Their metamorphosis outcomes do not contradict C023's lack of TRANSFORMED runs, because
      the perturbation differs.
  - Sharp, phase-stable kill edges for graded disturbances: **NO MATCH FOUND IN SEARCHED SOURCES.**
- **History:**
  - 2026-10-07 — OBSERVED — archivist, from Lane 4's generated summary at `12d9265`.
  - 2026-10-07 — REPRODUCED — archivist, `alm` bracket re-runs match 40/40 (`0e2cbe2`); N = 192
    shifts 3 of 40 bracket ends.
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on Lane 3's 20/20 replication (`5f316f3`);
    N = 192 shift explained as centroid-estimator bias (HR-007, `a2a1d2a`).
  - 2026-10-07 — restated — Lane 4 proposed claim 1 (`7bd1a42`) adopted as the statement; A1 and
    A3 results added. Lane 4 proposed REPRODUCED + INDEPENDENTLY_CHECKED; status unchanged.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.

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

### C026 — Where mass is removed matters more than how much: at R = 13 (t0 = 1000–1004) S001 survives losing 10% uniformly but dies from about 5% removed at its centre

- **Status:** INDEPENDENTLY_CHECKED
- **Owner lane:** Lane 4 (data), Lane 3 (replication), Lane 7 (statement, HR-007)
- **Sources:** L4-001 `results/coarse.csv` (achieved ΔM/M₀), Lane 3 lane3/README "Lane 4 disturbance
  battery, replicated" (PR #8 @ `5f316f3`), hostile-review HR-007 (PR #7 @ `a2a1d2a`)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref` and `alm` (Lane 4); `alm_check` (Lane 3)
- **Parameters:** baseline rule, T = 10, R = 13, 128²; t0 = 1000–1004
- **Intervention:** I001 uniform attenuation; I002 central disc deletion; I004 port-side cut; I003 frontal addition
- **Metric:** achieved mass change ΔM/M₀ at the RECOVERED → DIED edge (C023 classes)
- **Result:** edges in mass units: uniform −10.0% (I001), central −5.2 to −5.4% (I002; −3.9 to
  −4.0% survives), port side ≈ −8 to −9% (I004). **Adding** ≈ +28% mass ahead of the creature
  also kills (I003). A "fraction of mass lost" predictor cannot explain these edges.
- **Run IDs:** as C023 (`L4-001-*-N128-ref`, `-alm`); Lane 3 `research/traces/lane3/disturb-T10-R13*.csv`
- **Search / parameter bounds:** four interventions, five phases, R = 13 (R = 26 and T = 40 in C023/C027)
- **Reproduction command:** as C023; `python -m alm_check.disturb --T 10 --R 13`
- **Robustness (Lane 4 README):** the ordering centre < side < uniform holds at T = 20, R = 26 and N = 192.
- **Known caveats:** one specimen; three geometries, not a fitted spatial law (Lane 4). Lane 4
  proposed REPRODUCED; the archivist keeps INDEPENDENTLY_CHECKED because Lane 3's separate code
  measured the same mass edges. I004 shifts with T (C027). At R = 26 the I002 edge is
  −4.6 to −5.0% → −5.3 to −5.6% (Lane 3). The "survives 10% uniformly" wording holds only at
  R = 13, t0 = 1000–1004: at R = 26 the I001 edge is 9.88–10.0% (Lane 3
  `disturb-T10-R26-brackets.csv`: s_ok 0.0984–0.0992, s_fail 0.0992–0.1000) and s = 0.100 dies
  (Lane 4 `results/R26/bisect-brackets.csv`: s_ok 0.0969, s_fail 0.1000); Lane 6 has s = 0.10
  dying at t0 = 3002 (C023).
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  - [Cool2026] "Sensitivity to occlusion is spatially structured" and Fig. 4, pp. 4–5
    *(full text)*. **RELATED** (downgraded from CONSISTENT WITH after the full-text read).
    - What they found: a persistent 3×3 *informational* occlusion is lethal to O2u where
      "concentrated thinly at the center of its leading edge and expand[ing] into its core". O2u
      uses S001's rule, at R = 52 in float32.
    - Why that is not support: the occlusion hides cells from the kernel and removes **no
      mass**. C026 concerns where mass is removed, so the location dependence they report is a
      different perturbation that happens to have a similar shape.
  - [Hamon2025] Movies S3–S4 *(full text)*. **RELATED.** Orbium is fragile to obstacles and
    collisions. No location dependence is reported.
  - Mass-unit edges by location (≈ 5% central vs 10% uniform at R = 13): **NO MATCH FOUND IN
    SEARCHED SOURCES.**
- **History:**
  - 2026-10-07 — INDEPENDENTLY_CHECKED — archivist, on C023's two-implementation data.
  - 2026-10-07 — Lane 4 proposes the same claim (README claim 2, `7bd1a42`).
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.
  - 2026-10-07 — title scoped to R = 13, t0 = 1000–1004 (status unchanged) — Lane 9 wording note:
    the 10% uniform figure sits on the R = 26 edge and fails at t0 = 3002.

### C027 — The frontal-addition (I003) and port-side-injury (I004) kill edges move 11–13% when the timestep is quartered (T = 10 → 40)

- **Status:** NUMERICALLY_FRAGILE
- **Owner lane:** Lane 3
- **Sources:** lane3/README claim 7 and table (PR #8 @ `5f316f3`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check.disturb` @ `5f316f3`
- **Parameters:** R = 13, 128²; T = 10 vs T = 40; bands centred on each condition's own s = 0
  control (L4-001 amendment A1)
- **Intervention:** L4-001 battery I001–I004, t0 = 100 time units + five 0.1-unit offsets
- **Metric:** bisected transition s\* (bracket 1/1280)
- **Result:** I003 0.3090–0.3168 → 0.3348–0.3566 (+11%); I004 0.0793–0.0887 → 0.0887–0.1004
  (+13%). Both shifts exceed the T = 10 phase spread, so they are discretisation-sensitive by A1's
  rule. I001 0.1004–0.1027 → 0.1020–0.1082 (+4%) and I002 0.0598–0.0871 → 0.0605–0.0871 barely move.
- **Run IDs:** `research/traces/lane3/disturb-T40-R13.csv`, `disturb-T40-R13-brackets.csv`
- **Search / parameter bounds:** T ∈ {10, 40}
- **Reproduction command:** `python -m alm_check.disturb --T 40 --R 13`
- **Known caveats:** single path; Lane 4's own A1 run (T = 20, R = 26) is not yet reported. Consistent
  with C009: the T = 10 creature is slower and, by this measure, more fragile than the Δt → 0 one.
- **History:**
  - 2026-10-07 — NUMERICALLY_FRAGILE — Lane 3; archivist ledgered.

### C028 — Post-edit total mass does not predict S001's survival across disturbance types

- **Status:** OBSERVED
- **Owner lane:** Lane 4
- **Sources:** L4-001 README proposed claim 3 (PR #5 @ `7bd1a42`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`; `src/alm/disturb.py` @ `7bd1a42`
- **Parameters:** baseline rule, T = 10, R = 13, 128²; t0 = 1000–1004
- **Intervention:** I001 vs I002 near their edges
- **Metric:** ΣA/R² immediately after the edit (`mass_after_edit`) vs class
- **Result:** surviving I001 states at s = 0.10 have 0.392–0.393; dying I002 states near the edge
  have 0.412–0.414 (archivist check: every DIED I002 run with ≤ 11% removed has 0.400–0.414, all
  heavier than the surviving I001 runs). Lane 4 also reports that peak potential, positive-growth
  mass and one-step mass change give no single threshold separating all four interventions.
- **Run IDs:** rows in `results/coarse.csv` and `results/bisect.csv`
- **Search / parameter bounds:** four interventions, five phases
- **Reproduction command:** `reproduce.sh analyze`
- **Known caveats:** follows from C026; single engine. The search for a predictor is open (Lane 5),
  with bracket-end states saved in `research/experiments/L4-001-disturbance-battery/states/`.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 4.

### C029 — Near the uniform-attenuation edge, S001's collapse time grows like −7.0·ln(s − s*) steps (passage near an unstable edge state)

- **Status:** REPRODUCED
- **Owner lane:** Lane 4
- **Sources:** L4-001 README proposed claim 4 and "Exploratory" section (PR #5 @ `7bd1a42`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`; `explore_separatrix.py` @ `7bd1a42`
- **Parameters:** baseline rule, T = 10, R = 13, 128²; t0 = 1000 only
- **Intervention:** I001, s from s* + 4.5e−4 down to s* + 1e−12 (s* = 0.101098876141)
- **Metric:** step at which mass falls below 0.01
- **Result:** death step rises from 49 to 196 steps, fitting ≈ −14 − 7.0·ln(s − s*), i.e. one
  unstable direction growing at about 1.4 per time unit. A lingering state (131 steps after an
  edit at s* + 1e−11) is saved as `states/edge-I001-t1000.npz` for Lane 6.
- **Run IDs:** `results/separatrix-I001-t1000.csv`
- **Search / parameter bounds:** one intervention, one phase
- **Reproduction command:** `explore_separatrix.py`, `plot_separatrix.py`
- **Known caveats:** exploratory, not preregistered; single engine and phase; the fit is on one
  sequence. Lane 7 (HR-007) independently reports no long slowing-down at the bisection
  resolution (≈ 28 → 46 steps), which is consistent: the logarithmic growth only becomes large
  far below 1/256.
- **Reproduction by Lane 7 (HR-008, PR #7 @ `afb8c30`):** `research/experiments/HR008-edge-mode/edge_mode.py`
  re-bisects I001 at t0 = 1000 to s* = 0.101098876142 (Lane 4: 0.101098876141) and fits λ = 1.55/tu
  from collapse-time scaling and 1.82/tu from survivor/death pair separation (Lane 4's 7.0 steps
  per e-fold ≈ 1.43/tu). I003 behaves the same way (s* = 0.308763771041; λ = 1.78 and 1.64/tu).
  I004 does not: collapse is a flat 48 steps at every offset, because the cut removes whole cells.
  Lane 7 drives Lane 4's runner and `alm.disturb` on `ref`, so this is REPRODUCED, not independent.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 4.
  - 2026-10-07 — REPRODUCED — Lane 7 HR-008 (same engine, own bisection and fits); extended to I003.

### C030 — Within about 1e−6 below the uniform-attenuation edge, S001's survival is non-monotone ("death islands"), and the island positions depend on the engine

- **Status:** NUMERICALLY_FRAGILE
- **Owner lane:** Lane 4
- **Sources:** L4-001 README proposed claim 5 (PR #5 @ `7bd1a42`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref` and `alm`
- **Parameters:** baseline rule, T = 10, R = 13, 128²; t0 = 1000
- **Intervention:** I001, linear scan of 41 strengths over s* − 4e−7 … s*
- **Metric:** class (RECOVERED / DIED)
- **Result:** ref `RRRRRRRRRRRRRRRRRRRRRRDDDDRRDDDDDDDRRRRRR`; alm
  `RRRRRRRRRRRDDDDRDDDDDDDRRRRRRDDDDDDDDDDDD`. Both engines show islands; their locations differ.
  Survivors near the edge make a large mass excursion (up to 0.48) before recovering.
- **Run IDs:** `results/separatrix-scan-I001-t1000-ref.csv`, `separatrix-scan-I001-t1000-alm.csv`
- **Search / parameter bounds:** 41 points, 4e−7 wide, one phase
- **Reproduction command:** `explore_separatrix.py`
- **Known caveats:** the existence of fine structure reproduces across two engines; its location
  does not, so only the existence is a candidate claim. These offsets are far below any physical
  perturbation precision and below the float-rounding divergence between engines.
- **History:**
  - 2026-10-07 — NUMERICALLY_FRAGILE — Lane 4; archivist ledgered.

### C031 — No survive/die cut on an early bulk morphometric transfers between S001 disturbance types

- **Status:** OBSERVED (preregistered negative result)
- **Owner lane:** Lane 5
- **Sources:** `research/experiments/L5-002-survival-predictor/README.md` proposed claim 1 (PR #9 @
  `bd86e76`, open); preregistration `PREREGISTRATION.md` committed in `ca0783b` before any feature
  was computed on a disturbed state; amendment A1 (empty states) in `b331585` before any model was fitted
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`; disturbed states rebuilt with Lane 4's `alm.disturb` (max |rebuilt − Lane 4|
  post-edit mass 5.0e−7); features from `alm.morphometrics`
- **Parameters:** baseline rule, T = 10, R = 13, 128²; heading plateau 68.2°
- **Intervention:** L4-001 I001–I004, 410 coarse + 80 bisection runs (C023)
- **Metric:** 23 features (mass, gyradius, area ratios to control; anisotropy and a₂ shifts; mass trend) at
  lags 0, 5, 10, 20 steps (0–2 time units). Models: single-feature threshold, two-feature logistic.
  Leave-one-intervention-out; score = balanced accuracy on the held-out intervention's 30 near-edge runs,
  worst of four folds; pass bar 0.90 (preregistered).
- **Result:** nothing passes. Best single: area ratio at 2 tu, worst fold 0.70 (mean 0.80). Post-edit mass
  (C028's predictor): worst fold 0.50. Best pair: 0.54. Each feature's edge value moves between
  interventions by more than its survive/die gap within one.
- **Run IDs:** `features.csv`, `results.json` (L5-002 directory); underlying runs as C023
- **Search / parameter bounds:** 23 features × 4 lags; sets of size ≤ 2
- **Reproduction command:** `measure.py`, then `analyze.py` (L5-002 directory; needs Lane 4's PR #5 code)
- **Known caveats:** single engine, one resolution, one heading plateau. The five phases are
  consecutive steps, so each fold holds about 5 independent edges, not 30 independent runs. Within
  one disturbance the same features rank near-edge outcomes almost perfectly (direction-free AUC
  ≥ 0.93–0.96 for F6_k5, F1_k0, F2_k10; Lane 7 `HR008-edge-mode/within_auc.csv`), but that mostly
  tracks strength s. Lane 7 checked the preregistration order and found it clean, and notes the
  negative was largely predictable because collapse starts no earlier than about 5 tu. A
  non-morphometric coordinate is tested in C035–C037.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5, preregistered.
  - 2026-10-07 — reworded — Lane 5 (`f6239f6`) after HR-008: "no transferable cut", not "no early
    information".

### C032 — For attenuation (I001) and frontal addition (I003), S001's edge behaves like an unstable edge state: the doomed run tracks its survivor twin to < 1% for about 2 time units

- **Status:** REPRODUCED
- **Owner lane:** Lane 5
- **Sources:** L5-002 README proposed claim 2, `divergence.md`, `edge_values.md` (PR #9 @ `bd86e76`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`; Lane 4's `alm.disturb`
- **Parameters:** baseline rule, T = 10, R = 13, 128²; edge pairs (last survivor, first death) for five phases
- **Intervention:** I001, I003, I004 (I002 is the exception, below)
- **Metric:** first step at which the pair's gyradius or mass differs by > 1%; feature ratios at 2 tu
- **Result:** gyradius diverges at 20 (I001), 25–27 (I003), 21–24 (I004) steps; mass at 23–40 steps. The
  dying run regrows to 99% of control mass by 2 tu and matches the survivor to within 0.3%. I002 kills
  fast: gyradius diverges at 6–7 steps and the dying run is at 56% mass by 2 tu.
- **Run IDs:** `divergence.md`, `edge_values.md` (generated by `divergence.py`, `edge_values.py`)
- **Search / parameter bounds:** 400 steps side by side; four interventions × five phases
- **Reproduction command:** `divergence.py`, `edge_values.py` (L5-002 directory)
- **Edge-state evidence (Lane 7 HR-008):** one dominant unstable rate λ ≈ 1.5–1.8/tu, estimated two
  ways per disturbance for I001 and I003 (C029). The I001 and I003 lingering states correlate only
  0.90 with each other after alignment, so a single shared edge state is not established.
- **Known caveats:** exploratory, not preregistered; `ref` engine for both lanes (hence REPRODUCED,
  though Lane 5 calls it independently checked). **Does not apply to I002 or I004** at R = 13:
  those edits remove whole cells, so the edge pair is two different discrete edits, and I004's
  doomed runs die at step 48 with no approach to an edge state. The divergence-table rows for
  I002/I004 compare discrete edits, not trajectories straddling a saddle. Lane 4's death islands
  (C030) show the one-mode picture fails at fine scales.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5 (originally stated for I001, I003, I004).
  - 2026-10-07 — narrowed and REPRODUCED — Lane 5 (`f6239f6`) restricted it to I001/I003 after
    Lane 7 HR-008 measured λ two ways and showed I004 has no edge-state approach.

### C033 — "Mass at 6 time units ≥ 98% of control" classifies every S001 outcome, including on an unseen disturbance, but only because collapse has already begun

- **Status:** OBSERVED
- **Owner lane:** Lane 5
- **Sources:** L5-002 README "A late rule works" (PR #9 @ `bd86e76`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`; Lane 4's runner and classifier unchanged
- **Parameters:** baseline rule, T = 10, R = 13, 128²
- **Intervention:** I001–I004 (training folds); I005 rear deletion (held out, C034)
- **Metric:** same leave-one-out protocol as C031, with lags 30, 40, 60 steps added after the fact
- **Result:** the rule scores 1.00 in every held-out fold. Frozen, it scores 1.00 on all 205 I005 runs.
  But at 6 tu, 64 of 68 near-edge dying runs have already lost more than 20% of their mass, so it is
  a collapse detector, not an early predictor. At 3 tu, 31 of 68 dying runs are still within ±20%.
- **Run IDs:** `features-exploratory-lags.csv`, `features-i005-exploratory-lags.csv`,
  `results-exploratory-lags.json`, `results-exploratory-lags-with-i005.json`
- **Search / parameter bounds:** lags 0, 30, 40, 60 steps
- **Reproduction command:** see the L5-002 README "Reproduction" block (last two `measure.py` lines and `analyze.py --i005`)
- **Known caveats:** found after looking at the data (exploratory); the I005 score is genuine
  out-of-sample evidence for the detector. Single engine.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5.

### C034 — Under rear deletion (I005), S001's survival edge lies between about 5% and 7% mass loss

- **Status:** OBSERVED
- **Owner lane:** Lane 5
- **Sources:** L5-002 README proposed claim 3 and "The unseen disturbance I005" (PR #9 @ `bd86e76`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`; Lane 4's runner and classifier unchanged; I005 in `i005.py`
- **Parameters:** baseline rule, T = 10, R = 13, 128²; t0 = 1000–1004
- **Intervention:** I005 rear deletion: zero a disc of radius s·R centred 0.5 R behind the centroid;
  s = 0…1 by 0.025
- **Metric:** L4-001 classes
- **Result:** survives s ≤ 0.15 (except t0 = 1003), dies s ≥ 0.175. In mass terms, the last survivors lost
  4.6–5.7% and the first deaths 5.6–7.6% (archivist checked `i005-runs.csv`: 34 RECOVERED, 171 DIED,
  nothing else). This places rear deletion near central deletion (≈ 5%, C026) and below the port cut (8–9%).
- **Run IDs:** `i005-runs.csv` (205 runs)
- **Search / parameter bounds:** coarse grid (0.025 in s); bisected later in L5-003
  (`research/experiments/L5-003-edge-direction/i005-bisect.csv`, 15 runs, committed in `f2ccfdb` before
  any projection): edge ≈ 0.161 at t0 = 1000
- **Reproduction command:** `.venv/bin/python research/experiments/L5-002-survival-predictor/gen_i005.py`
- **Known caveats:** single engine; coarse grid (0.025 in s); phases overlap in mass terms. Extends C026.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5.

### C035 — A coordinate along the edge-pair split direction, read at 2 time units, passes the preregistered hold-one-disturbance-out test, but only ties a shape-deficit null on the unseen disturbance

- **Status:** OBSERVED (preregistered; narrow pass)
- **Owner lane:** Lane 5
- **Sources:** `research/experiments/L5-003-edge-direction/README.md` proposed claim 1 (PR #9 @ `f6239f6`,
  open); preregistration `PREREGISTRATION.md` committed in `846ed50` before any state was projected; no amendments
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`; Lane 4's L4-001 states; exact Fourier sub-pixel shift into the comoving frame
- **Parameters:** baseline rule, T = 10, R = 13, 128²; 68.2° heading plateau
- **Intervention:** I001–I004 (folds), I005 (held out; I005 bisection in `f2ccfdb`, labelled before projection)
- **Metric:** u_k = normalised mean unit difference (death − survivor) of edge pairs over the training
  disturbances at lag k; c_k = ⟨state − control, u_k⟩; threshold stump; worst-fold near-edge balanced
  accuracy, bar 0.90; smallest passing lag selected. Null: shape-deficit coordinate.
- **Result:** lag 20 (2 tu): worst fold 0.90, mean 0.97, 2 errors in 120 near-edge runs (null 0.78 / 0.90).
  Lags 0–10 fail (0.50). Frozen on I005 (cut 1.259): 0.977 on 220 runs, 0.929 on 25 near-edge; the null
  scores the same. At lag 20, 53 of 68 near-edge dying runs are still inside Lane 4's ±20% mass band.
- **Run IDs:** `coords.csv`, `directions.json`, `directions.npz`, `results.json`, `i005-bisect.csv` (L5-003 directory)
- **Search / parameter bounds:** lags 0, 5, 10, 20, 30 steps
- **Reproduction command:** `bisect_i005.py`, `project.py`, `score.py` (L5-003 directory; needs PR #5 code)
- **Known caveats:** the worst fold sits exactly on the bar (one error among I001's 5 near-edge
  survivors); about 5 independent edges per fold. The direction mixes a real edge mode (I001, I003)
  with pixel-quantized edits (I002, I004, I005). It reads the divergence early but does not predict
  before it begins. No advantage over the null on the unseen disturbance. One engine, R, heading.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5, preregistered.

### C036 — At 2 time units, S001's survive/die split directions for attenuation, frontal addition, port cut and rear deletion are similar (cosine 0.82–0.92); central deletion's is not (0.12–0.25)

- **Status:** OBSERVED
- **Owner lane:** Lane 5
- **Sources:** L5-003 README proposed claim 2 (PR #9 @ `f6239f6`, open)
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`
- **Parameters:** as C035, lag 20
- **Intervention:** I001–I005
- **Metric:** pairwise cosine between per-disturbance mean split directions
- **Result:** I001–I003 0.92, I001–I004 0.82, I001–I005 0.88, I003–I004 0.88, I003–I005 0.90, I004–I005
  0.83; I002 with any other 0.12–0.25. At lag 10 all cosines are ≤ 0.46. The shared pattern is mostly core loss.
- **Run IDs:** `directions.json` (L5-003 directory)
- **Search / parameter bounds:** lags 10 and 20 reported
- **Reproduction command:** `project.py` (L5-003 directory)
- **Known caveats:** descriptive; does not show a shared edge state (C037). Single-pair directions
  within one disturbance agree less (0.53–0.60) than the averages across disturbances.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5.

### C037 — No evidence yet that a single unstable mode's coordinate predicts S001's survival better than a shape-deficit null

- **Status:** OBSERVED (exploratory)
- **Owner lane:** Lane 5
- **Sources:** L5-003 README proposed claim 3 and "Scoped to the genuine edge state" (PR #9 @ `f6239f6`,
  open), prompted by Lane 7 HR-008
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `ref`
- **Parameters:** as C035
- **Intervention:** directions built from I001 only, I003 only, or both (the two edits with a measured edge state, C032)
- **Metric:** near-edge balanced accuracy of the transferred cut
- **Result:** lag 20: I001 → I003 0.75 (null 0.78); I003 → I001 0.50 (null 0.50); I001+I003 → I004 / I005 /
  I002 0.73 / 0.64 / 1.00 (null 0.93 / 0.93 / 1.00). Lag 30: no better than the null anywhere except
  I001+I003 → I004 (0.83 vs 0.80). The I001 and I003 split directions align (cosine 0.92) but their cuts
  do not transfer.
- **Run IDs:** `results-scoped-exploratory.json`, `x_*` columns of `coords.csv` (preregistered columns byte-identical)
- **Search / parameter bounds:** lags 20 and 30
- **Reproduction command:** `score_scoped.py` (L5-003 directory)
- **Known caveats:** exploratory, after the preregistered result. Proposed next tests: smooth edits on
  both sides (R = 26) or an adjoint (left-eigenvector) projection.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 5.

Claims C038–C045 come from Lane 6 (field exploration, PR #11 @ `83c8bff`; merged 2026-10-07 as `f72db9e`, whose only later change, `f40f303`, adds `1P4odl` to L6-e as already ledgered in C045). **None has been
reproduced by a second lane yet.** Statuses below reflect Lane 6's own evidence only; clean-process
bitwise reruns count as REPRODUCED, never as INDEPENDENTLY_CHECKED. Common setup unless stated:
ALM semantics (poly/poly, β = [1], Euler + hard clip, float64, periodic), 128² at R = 13 (scaled
with R), stepped by `research/experiments/L6-field/field.py` (batched; built from `alm.lenia.kernel`
and `alm.lenia.growth`, bitwise equal to `alm.lenia.Lenia` at 300 steps for S001), with clean
reruns through Lane 2's runner. Motion classes (fixed before the T = 40 and R = 26 reruns): died
(mass < 0.01), filled (> 25% of cells above 0.1 or mass > 30 × Orbium), GLIDER (net speed > 0.2 R/tu),
CIRCLER (net < 0.1 and path speed > 0.2), STATIC (path speed < 0.02), OTHER. Tables are recomputed by
`tables.py`; an earlier aliasing-prone "ROTATOR" class in the raw CSVs is superseded.

### C038 — One rule (S001's, with μ = 0.155, σ = 0.020) supports three phenotypes chosen by history: an Orbium glider, a circler (S102) and a static ring (S103)

- **Status:** REPRODUCED (clean-process reruns); not yet reproduced by a second lane
- **Owner lane:** Lane 6
- **Sources:** `research/experiments/L6-field/README.md` proposed claim L6-a; specimen dossiers
  `research/specimens/S102-circler.md`, `S103-static-ring.md` (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** S001 (Orbium cells), S102 seed (`gyrator-seed-u8.csv`), S103 seed
  (`static-seed-u8.csv`), rebuilt by `make_seeds.py`; catalog OG2g cells as a check
- **Simulator / version:** `field.py` @ `83c8bff`; `alm.run` for clean reruns
- **Parameters:** μ = 0.155, σ = 0.020, R = 13, T = 10, 128² (L6-004 also μ 0.150/0.160 over a σ strip)
- **Intervention:** none (different starting seeds)
- **Metric:** motion class after 1000 tu (T10/R13) or 500 tu (T40/R13, T10/R26)
- **Result:** all three persist ≥ 500 tu at T10/R13. Glider and circler coexist at every numerical
  setting tested, but the σ band moves: T10/R13 σ 0.0195–0.0205 (depending on μ); T10/R26 σ
  0.0195–0.0205; T40/R13 σ 0.0185–0.0190. S103 is unchanged at every setting (C042).
- **Run IDs:** `bistab-T10-R13.csv`, `bistab-T10-R26.csv`, `bistab-T40-R13.csv`, `persist-*.csv`;
  traces `S102-5bfac8f95f` (T 10, final sha256 `10d65755…`, second process identical),
  `S102-7b439113e1` (T 40), `S103-1d8c158cdd`, `S103-4982ff6f4d`
- **Search / parameter bounds:** μ ∈ {0.150, 0.155, 0.160}; σ strip in 0.0005 steps; T ∈ {10, 40}; R ∈ {13, 26}
- **Reproduction command:** `make_seeds.py`; `bistability.py` (~1 h on 4 cores); `persistence.py --T 10 --R 13`
- **Known caveats:** the coexistence is robust, but its σ location is NUMERICALLY_FRAGILE (shifts by
  0.0005–0.0015 with T or R). The T shift is a timestep dependence. The R = 26 shift was measured
  from bilinearly resized seeds, so it may mix resolution dependence with resize-method
  dependence; it has not been rerun with other resizes. S102 at its registered rule dies at
  R = 26 only from a bilinear seed; block, nearest and cubic seeds survive (C047; C039 REFUTED,
  D2). At T = 40, Orbium at
  this rule became a different static body (mass 0.3873, not S103's 0.3787), not followed up. All
  three phenotypes are catalogued species (C043). Lane 6's top suggested follow-up is a second-lane
  reproduction in `alm_check`.
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  PR #11 has merged; the underlying claims are still single-lane (not yet reproduced by a second lane).
  - [Chan2019] §3.7.2 and Fig. 17, pp. 35–36 *(full text)*. **PREVIOUSLY REPORTED** (the
    phenomenon, in another genus). Two *Paraptera* species coexist at one rule (μ 0.3,
    σ ∈ [0.0468, 0.0483]), and "just outside the coexistence … slowly transform into each
    other".
    - Similar outcome only: a different genus and rule.
    - The glider + circler + ring triple at μ 0.155, σ 0.020 is not reported there.
  - [Chan2019] Fig. 9, p. 21 *(full text, figure inspected)*. **RELATED.** The μ–σ map draws the
    Orbium (O2) and Gyrorbium (OG2) niches as adjacent bands near σ ≈ 0.02. Overlapping regions
    are painted over each other, so the figure cannot confirm or rule out coexistence. The
    earlier "to check" item is closed as undeterminable from this figure.
  - [Chan2019] Fig. 7(d), p. 17 *(full text)*. **CONSISTENT WITH** C038's caveat. Orbium's niche
    expands as T increases, so niche boundaries depend on T, as C038's σ band does.
  - [LeniaCatalog] **RELATED.** The catalog rules for `O2u` (0.15/0.015) and `OG2g` (0.156/0.0224)
    bracket the coexistence rule. Neither entry uses it.
  - [Hudcova2026] Method (p. 1) and Fig. 3(c–d), p. 2 *(full text)*. **CONSISTENT WITH.**
    - At a fixed rule, the phase reached (stable, metastable or unclassified) depends on the
      size of the initial noise patch, and solitons appear near the stable–metastable transition.
    - Similar outcome only: whole-grid phases, not species. Gaussian growth, Δt = 0.1, an
      exponential-bump kernel at R = 13, and a 100×100 grid.
    - It is a 3-page abstract whose algorithm details are marked "TODO".
  - [Chan2020] p. 6, "Differentiation" *(full text)*. **PREVIOUSLY REPORTED** (the phenomenon,
    in expanded rules).
    - In multi-channel "Aquarium" rules, "one genotype produces multiple phenotypes of aggregated
      solitons", among them gyrating and stationary ones. Each phenotype can switch to another
      "upon collision or after self-replication".
    - Similar outcome only: multi-channel rules, not classic single-kernel Lenia.
  - [Yevenko2024] *(excerpt)*. **RELATED.** Maps Orbium stability around its rule.
- **History:**
  - 2026-10-07 — REPRODUCED — Lane 6 (clean-process bitwise reruns); awaiting a second lane.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.
  - 2026-10-21 — amendment (status unchanged) — REEF coordinator, expedition `research/reports/reef-expedition-2026-10-20.md`. The three phenotypes coexist *as separate, isolated bodies*. Put into one N256 world, a settled glider that touches S103 fuses with it and ignites a world-covering colony in 12/12 encounters across b/R ∈ [−1.5, +1.5] (C052). "Coexist" in this claim therefore means co-persistence under one rule in separate worlds, not peaceful co-residence.

### C039 — The circler S102 at its registered rule (μ 0.155, σ 0.020) does not survive doubling the resolution

- **Status:** REFUTED as worded (superseded by C047). The narrower fact, that the *bilinearly resized* seed
  dies at R 26 and 39, is INDEPENDENTLY_CHECKED (Lane 6 `field.py`, PR #11, at R 26; Lane 3
  `alm_check`, PR #18, at R 26 and 39). That is a resize-method dependence of the initial
  condition, not a resolution dependence: from block, nearest or cubic seeds S102 persists at
  R 26 and 39 (C047), with mean properties within 0.5% of R 13 over 300 tu (C046).
- **Owner lane:** Lane 6
- **Sources:** L6-field README L6-004 and L6-006; `research/specimens/S102-circler.md` (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** S102 seed (`gyrator-seed-u8.csv`)
- **Simulator / version:** `field.py` @ `83c8bff`
- **Parameters:** μ 0.155, σ 0.020; T10/R13, T40/R13, T10/R26
- **Intervention:** none
- **Metric:** motion class
- **Result:** CIRCLER at T10/R13 (mass 0.523, turning 95°/tu) and T40/R13 (mass 0.497, 109°/tu);
  **DIED** at T10/R26. At R = 26 the circler lives at σ 0.0205.
- **Run IDs:** `persist-T10-R13.csv`, `persist-T40-R13.csv`, `persist-T10-R26.csv`, `bistab-T10-R26.csv`
- **Search / parameter bounds:** three numerical settings
- **Reproduction command:** `persistence.py --T {10,40} --R {13,26}`
- **Known caveats:** single lane. The phenotype persists at a nearby σ at R = 26, so this is a shift of
  its band, not its absence. Lane 6 resized the seed bilinearly (`persistence.py` line 49,
  `ndimage.zoom(..., order=1)`).
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  PR #11 has merged; the underlying claims are still single-lane (not yet reproduced by a second lane).
  - [Chan2019] Fig. 7(b), p. 17 *(full text)*. **RELATED.** Orbium's niche stays static over
    R = 9–55 at T = 10. That is Orbium, not the circler, so it is not a contradiction.
  - [Davis2024] p. 18 (definition) and p. 20 *(full text)*. **RELATED** (downgraded from
    CONSISTENT WITH on 2026-10-08 after dispute D2).
    - Davis defines a pattern–rule pair as non-Platonic if it fails at some discretization but
      persists at a coarser one. *Scutium gravidus*, *Triscutium solidus* and an *H. natans*
      wobbler meet that definition.
    - The R = 26 death in this claim comes from the *bilinearly resized* seed. Block, nearest and
      cubic seeds of S102 persist at R = 26 and 39 (C047: Lane 3 `alm_check` and Lane 6 `field.py`). So the death is
      a resize-method dependence of the initial condition, not a resolution dependence of the
      rule–pattern pair, and S102 does not meet Davis's definition with respect to R on our data.
    - Similar outcome only: other species and Gaussian-family rules. Davis's Orbium is Platonic.
  - [Yevenko2024] *(excerpt)*. **RELATED** (downgraded from CONSISTENT WITH on 2026-10-08, for
    the same reason; excerpt-only, so provisional). Reports Orbium variants that "rely on
    discretization to survive".
- **Dispute:** **D2** with C047 (Lane 3), resolved 2026-10-07 in favour of C047. See [Disputes](#disputes).
- **History:**
  - 2026-10-07 — NUMERICALLY_FRAGILE — Lane 6.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.
  - 2026-10-07 — disputed (D2) — Lane 3 L3-002 (PR #18). Lane 3 reproduces the bilinear-seed death in
    `alm_check`; its block, nearest and cubic seeds survive. Status unchanged pending Lane 6.
  - 2026-10-07 — REFUTED — Lane 6 reran the four resizes in `field.py` (`d2_resize.py`, `d2-resize.csv` in `research/experiments/L6-007-attractor-geography/` (PR #23 @ `413003d`, merged to `main` as `7a4ea3b`)) and got Lane 3's result:
    only the bilinear seed dies. Lane 6 conceded and proposed REFUTED (relayed by the coordinator). The
    "circler lives at σ 0.0205 at R 26" result and the C038 band shift were measured from bilinear seeds
    and have not been rerun with other resizes.
  - 2026-10-08 — Prior literature: Davis2024 and Yevenko2024 downgraded to RELATED after D2 showed the R = 26
    death depends on the seed resize method (C047, PR #22). The status change itself is carried by PR #22 — archivist.
  - 2026-10-08 — REFUTED (basis restated) — PR #18 merged (`56ae421`). The refutation rests on Lane 3's merged
    evidence: preregistered block seeds persist at R 26 and 39 through 300 tu, and in the exploratory
    follow-up block, nearest and cubic seeds persist through 1000 tu. Lane 6's `field.py` rerun
    (`413003d`) corroborates the eight outcomes; it is on `main` via PR #23 (`7a4ea3b`).
  - 2026-10-08 — Lane 6's rerun merged in PR #23 (`7a4ea3b`); C047 is now INDEPENDENTLY_CHECKED for those eight seeds (status unchanged) — archivist.

### C040 — At the coexistence rule, Lane 4's disturbances never switch a glider into a circler or back (0/316); a port injury switched the circler into the static ring S103 in 2 of 38 runs

- **Status:** OBSERVED; not yet reproduced by a second lane
- **Owner lane:** Lane 6
- **Sources:** L6-field README proposed claim L6-b, L6-005 (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** Orbium and S102 seed at the coexistence rule; S001-rule Orbium as control
- **Simulator / version:** `field.py`; I001–I004 copied from Lane 4 (`claude/night0-disturbance-np4adr`
  @ `7bd1a42`, `src/alm/disturb.py`) into `disturb_helpers.py`
- **Parameters:** μ 0.155, σ 0.020, T 10, R 13, 128²; t0 = 3000 and 3002 steps; 500 tu horizon
- **Intervention:** L4-001 I001–I004 full coarse grids × 2 phases (strengths and classes fixed before these runs)
- **Metric:** Lane 6 motion class after the horizon
- **Result:** across the Orbium-at-coex and circler-at-coex cases, no GLIDER ↔ CIRCLER switch. Circler
  + I004 at s = 0.15 and 0.25, t0 = 3002 → STATIC with mass 0.378698 = S103 (archivist checked
  `switch-T10-R13.csv` via `tables.py`). Orbium at coex + I003 ≥ 0.45 FILLED the world in 22/40 runs
  instead of dying. Robustness to I001: ring 20%, glider 10%, circler < 5% in every phase.
- **Run IDs:** `research/experiments/L6-field/switch-T10-R13.csv`
- **Search / parameter bounds:** two phases; T10/R13 only
- **Reproduction command:** `disturb_switch.py` (~1 h); `tables.py bistab-T10-R13.csv switch-T10-R13.csv`
- **Known caveats:** single T/R and two phases only. The circler → ring switch occurred in one phase only.
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  PR #11 has merged; the underlying claims are still single-lane (not yet reproduced by a second lane).
  - [Chan2019] §3.5.3 and Fig. 12(j), pp. 26–27 *(full text)*. **RELATED.** Spontaneous
    metamorphosis among morphological–behavioural templates in shape-shifting species. It is
    unprompted, not triggered by a disturbance.
  - [Cool2026] pp. 4–5 *(full text)*. **RELATED.** Occlusions can push a creature into
    metamorphosis; K4s "transforms into … an oscillating structure". Different intervention and
    species.
  - [Chan2020] p. 6 *(full text)*. **RELATED.** In multi-channel rules, a phenotype "can switch to
    another phenotype … upon collision". Expanded rules.
  - Glider ↔ circler switching (or its absence) under graded disturbances: **NO MATCH FOUND IN
    SEARCHED SOURCES.**
- **History:**
  - 2026-10-07 — OBSERVED — Lane 6.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.

### C041 — Under S001's own rule, a bound Orbium pair (S101) survives port injury of 10–50% by shedding to a single Orbium, where a single Orbium dies at 10%

- **Status:** OBSERVED; not yet reproduced by a second lane
- **Owner lane:** Lane 6
- **Sources:** L6-field README proposed claim L6-c and L6-002/003; `research/specimens/S101-orbium-pair.md` (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** S101 seed (`pair-seed-u8.csv`), formed from 7 of 175 two-Orbium starts
  (4 different relative rotations); equals catalog `O4i` Synorbium ignis under the S001 rule
- **Simulator / version:** `field.py`; clean reruns via `alm.run`
- **Parameters:** S001 baseline rule (μ 0.15, σ 0.015, R 13, T 10), 128²
- **Intervention:** L4-001 I004 port injury, s = 0.10–0.50, two phases; other interventions as in the README table
- **Metric:** Lane 6 motion class and final mass
- **Result:** pair: 18/18 runs at I004 0.10–0.50 end as one Orbium (mass 0.4358). Single Orbium control:
  36/36 die at I004 ≥ 0.10 (archivist checked the control rows). The pair glides at gyradius 0.813 R,
  mass 0.8736, 0.472 R/tu; it persists at T 40 (mass 0.8642, 0.508 R/tu) and R 26 (0.8738, 0.472).
- **Run IDs:** `S101-3ffd856fba` (T 10, final sha256 `107c9d26…`, second process identical),
  `S101-046982cbd6` (T 40); `seeds-pairs` outputs; L6-005 pair rows
- **Search / parameter bounds:** 175 pair starts (5 rotations × 35 offsets); I004 grid × 2 phases
- **Reproduction command:** `make_seeds.py`; `disturb_switch.py`; `python -m alm.run --specimen S101 …`
- **Known caveats (Lane 6's own trivial baseline):** I004 cuts along the heading and the partners sit side
  by side, so the cut mostly removes one partner. The claim is only that the coupling does not drag
  the uninjured partner down, not that the pair heals. I002 "robustness" is trivial (the disc sits
  in the gap). Disturbance runs at T10/R13 only. The pair's speed is ~7% lower at T 10 than T 40 (cf. C009).
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  PR #11 has merged; the underlying claims are still single-lane (not yet reproduced by a second lane).
  - [Chan2019] §3.5.5 (pp. 28–29) and Fig. 12(k) (p. 26) *(full text)*.
    - **PREVIOUSLY REPORTED** for how the pair forms: two colliding Orbium "fuse … into one
      Synorbium".
    - **CONSISTENT WITH** the shedding: Chan lists "Fission, one Synorbinae breaks into …
      Orbium" and "Absorption, only one Orbium survives".
    - Similar outcome only: Chan's rule is not stated per reaction, and Chan reports reactions
      to collisions, not to port injury.
  - [LeniaCatalog] `O4i` *Synorbium ignis*. **PREVIOUSLY REPORTED** as a species (C043), with
    catalog rule 0.152/0.0156, not S001's.
  - A pair surviving port injury by shedding to one Orbium: **NO MATCH FOUND IN SEARCHED
    SOURCES.**
- **History:**
  - 2026-10-07 — OBSERVED — Lane 6.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-21 — amendment (status unchanged; no earlier line rewritten) — REEF coordinator. Later merged evidence narrows this claim: L6-008 (PR #27, on `main`) found the port-injured pair ends as its two halves run alone in 58/60 runs, so the "resilience" is largely the untouched partner carrying on (accepted by HR-009, PR #30). Separately, the Night 1 "on-gap I003 pulse kills the pair" reading was withdrawn: the on-gap pulse at s 0.2–0.3 unbinds S101 into two living Orbia, and their later deaths were collisions on the 128² torus (HR-009c; 256² reruns keep two Orbia). Off-gap and boundary results in PR #35 remain exploratory/unverified. Neither the ledger nor this amendment changes C041's status.

### C042 — S103 is an exact fixed point of the clipped Lenia map: it is T-independent and returns bitwise to itself after attenuation up to 20%

- **Status:** REPRODUCED (clean-process reruns); not yet reproduced by a second lane
- **Owner lane:** Lane 6
- **Sources:** `research/specimens/S103-static-ring.md` (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** S103 seed (`static-seed-u8.csv`; = catalog `C0la` resized from R 15 to 13)
- **Simulator / version:** `alm.run` (Lane 2 runner) and `field.py`
- **Parameters:** μ 0.155, σ 0.020, R 13; T 10 and T 40; R 26 (resized seed)
- **Intervention:** none; L6-005 quick check with I001–I004 at one phase
- **Metric:** final-state sha256 vs initial; mass
- **Result:** final sha256 = initial sha256 (`a81efdac…`) at T 10 (10 000 steps) and T 40 (20 000 steps);
  a second process agrees. Mass 0.3787, gyradius 0.387 R. Mechanism: every full cell has G(U) ≥ +0.028
  and is held at 1 by the clip; every empty cell has G(U) ≤ −0.125 and is held at 0. After I001 ≤ 0.20 it
  returns bitwise; it dies at ≥ 0.30. Static with the same mass at R 26.
- **Run IDs:** `S103-1d8c158cdd` (T 10), `S103-4982ff6f4d` (T 40); `persist-*.csv`; `tests/test_lane6_specimens.py`
- **Search / parameter bounds:** T ∈ {10, 40}, R ∈ {13, 26}
- **Reproduction command:** `.venv/bin/python -m alm.run --specimen S103 --steps 10000 --every 10 --burn-in 5000`
- **Known caveats:** a creature of the hard clip; a Lenia variant without clipping would not have it in
  this form. The I001–I004 check used one phase.
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  PR #11 has merged; the underlying claims are still single-lane (not yet reproduced by a second lane).
  - [LeniaCatalog] `C0la` *Circium lithos apertus* (R 15, 0.16/0.022). **PREVIOUSLY REPORTED** as a
    catalogued species (C043).
  - [Chan2019] §3.5.2 (p. 27) and Table 2 (p. 28) *(full text)*. **RELATED.** The epithet *lithos* names
    the "Frozen" stationary gait (SF; "negligible or no fluctuation", example *Pentafolium
    lithos*). §3.3.1 calls Circium-type class-2 patterns "periodic immobile".
  - [Chan2020] p. 6 *(full text)*. **RELATED.** It glosses the epithet *lithos* as "stationary".
    That fits C0la being static, but neither paper says *Circium lithos* is an exact fixed point.
  - [Kojima2023] §2.1.1 and §2.1.3, pp. 3–5 *(full text)*. **RELATED.**
    - The clip "cannot be expressed in a differential equation".
    - At dt = 0.1 the upper clip is "necessary to maintain the pattern".
    - Both are consistent with a clip-held fixed point being possible, but say nothing about
      static rings.
  - A bitwise fixed point held by the clip: **NO MATCH FOUND IN SEARCHED SOURCES.**
- **History:**
  - 2026-10-07 — REPRODUCED — Lane 6.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.
  - 2026-10-07 — Prior literature re-verified against arXiv full texts after the network change (status unchanged) — archivist.
  - 2026-10-07 — T-independence agrees with Lane 3's `alm_check` at T 10–80 (C048, INDEPENDENTLY_CHECKED
    for that part). The attenuation part has no second lane, so the status is unchanged.

### C043 — S101, S102 and S103 are catalogued species carried to nearby rules, not new forms

- **Status:** OBSERVED (any novelty claim for S101–S103 is REFUTED)
- **Owner lane:** Lane 6
- **Sources:** L6-field README proposed claim L6-d and "Reference check" (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** S101–S103 seeds; catalog cells `O4i`, `OG2g`, `C0la` (`.refs/Lenia` @ `adfc542`)
- **Simulator / version:** `field.py`
- **Parameters:** each candidate's rule
- **Intervention:** none (catalog cells placed in the candidate's rule)
- **Metric:** settled mass, gyradius, speed / path speed
- **Result:** S101 vs `O4i`: mass 0.8736 / 0.8737, gyradius 0.8152 / 0.8154, speed 0.4727 / 0.4723. S102 vs
  `OG2g`: 0.5223 / 0.5228, 0.5158 / 0.5155, path 0.497 / 0.498. S103 vs `C0la` (resized): 0.378698 /
  0.378698, both static. No nickname proposed (discovery-protocol criterion 5 fails for all three).
- **Run IDs:** `persist-*.csv`, `catalog-neighbours.csv`
- **Search / parameter bounds:** single-shell catalog entries with μ ∈ [0.09, 0.21], σ ∈ [0.006, 0.030]
- **Reproduction command:** `persistence.py`; `catalog_neighbours.py`
- **Known caveats:** single lane.
- **Prior literature** (search and full-text verification 2026-10-07; grades and versions in `references.md`):
  PR #11 has merged; the underlying claims are still single-lane (not yet reproduced by a second lane).
  - [LeniaCatalog] `O4i`, `OG2g`, `C0la`. **PREVIOUSLY REPORTED.** These are the catalog entries the
    claim matches. Similar outcome only: the catalog rules sit near, not at, S101–S103's rules:

    | Specimen | Our rule | Catalog rule |
    | --- | --- | --- |
    | S101 | 0.15/0.015 | 0.152/0.0156 |
    | S102 | 0.155/0.020 | 0.156/0.0224 |
    | S103 | R 13, 0.155/0.020 | R 15, 0.16/0.022 |

    The claim's own wording, "carried to nearby rules", already says this.
  - [Chan2019] §3.5.5 and Fig. 12(k) *(full text)*. **PREVIOUSLY REPORTED.** Synorbium forms from
    two fusing Orbium. S101 also formed from two-Orbium starts (C041).
- **History:**
  - 2026-10-07 — OBSERVED — Lane 6; novelty REFUTED by its own reference check.
  - 2026-10-07 — Prior literature added (status unchanged) — archivist, literature-provenance mandate.
  - 2026-10-07 — Prior literature verified against Chan 2019 full text and authors' code (status unchanged) — archivist.

### C044 — Around S001, Orbium's μ × σ neighbourhood is one continuum: no other phenotype arises from Orbium cells, soups or rescaled Orbia except a circler at two rules and the bound pair

- **Status:** OBSERVED; not yet reproduced by a second lane
- **Owner lane:** Lane 6
- **Sources:** L6-field README L6-001, L6-002, L6-003 (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** S001 cells; random soups; resized/rescaled S001; two-Orbium starts
- **Simulator / version:** `field.py` @ `83c8bff`
- **Parameters:** L6-001: μ 0.100–0.200 (0.005) × σ 0.008–0.028 (0.001), 441 rules, T 10, R 13, 500 tu.
  L6-002/003: S001 rule.
- **Intervention:** none (initial-condition search)
- **Metric:** motion class over the last 100 tu
- **Result:** 441 rules: 212 died, 165 filled, 64 localized, of which 62 are Orbium (mass 0.322–0.493,
  speed 0.43–0.59 R/tu, varying smoothly). Two circlers: μ 0.155/σ 0.022 (= `OG2g`, ≥ 2000 tu) and
  μ 0.135/σ 0.018 (`OG2r`-like, fills the world at ≈ 850 tu, a transient). Soups: 96/96 died. Resize ×
  rescale: Orbium or death (135 starts). Pairs: 7/175 bound (S101), 14 two separate Orbia, 67 one
  Orbium, 84 both died, 2 filled, 1 chaotic merged blob alive at 500 tu (not followed up).
- **Run IDs:** `musigma-T10.csv`, `soup-*.csv`, `seeds-*.csv`
- **Search / parameter bounds:** as Parameters; one T, one R; 500 tu horizon
- **Reproduction command:** `sweep_musigma.py`, `sweep_soup.py`, `sweep_seeds.py zoom|pairs`
- **Known caveats:** a bounded negative: one specimen's cells, one resolution, one timestep, a 500 tu
  horizon. Lane 5's component count splits Orbium's tail, so it was not used as a phenotype test.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 6.

### C045 — Under ALM semantics, four catalog entries (`O2bi`, `O2p`, `OG2r`, `O8?`) do not persist under their own catalog rules

- **Status:** OBSERVED; not yet reproduced by a second lane
- **Owner lane:** Lane 6
- **Sources:** L6-field README proposed claim L6-e and "Reference check" (PR #11 @ `83c8bff`, merged 2026-10-07 as `f72db9e`)
- **Specimen / version:** catalog cells from `.refs/Lenia/Python/animals.json` @ `adfc542`
- **Simulator / version:** `field.py` (ALM semantics as in `research/specimens/S001-orbium/reconstruct.py`)
- **Parameters:** each entry's own catalog rule (R, T, μ, σ, β)
- **Intervention:** none
- **Metric:** motion class
- **Result:** `O2bi` and `O2p` die; `OG2r` and `O8?` fill the world. The archivist's read of
  `catalog-neighbours.csv` finds a **fifth** non-persisting entry that the claim does not name: `1P4odl`
  (fate `filled`). The remaining 12 of the 17 entries are `localized`.
- **Run IDs:** `research/experiments/L6-field/catalog-neighbours.csv`
- **Search / parameter bounds:** 17 single-shell entries with μ ∈ [0.09, 0.21], σ ∈ [0.006, 0.030]
- **Reproduction command:** `catalog_neighbours.py`
- **Known caveats:** a disagreement with the upstream catalog, not resolved. The cells may need settings
  the catalog does not record, or may be transients. Flagged for Lanes 1 and 3; do not cite `OG2r`,
  `O2bi`, `O2p` or `O8?` as stable until checked.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 6.

### C046 — For S001, S101 and S102 from block-replicated seeds, mean properties at R = 13 agree with R = 39 to 0.5% over 300 tu, while speeds and turning rates at T = 10 are timestep-biased by 10–18%

- **Status:** OBSERVED (preregistered; single engine)
- **Owner lane:** Lane 3
- **Sources:** `research/experiments/L3-002-property-persistence/README.md` proposed claim 1 and
  label table; protocol `PREREGISTRATION.md` (PR #18, merged as `56ae421`; wording scoped in `ab125c4`; preregistration `6c52536`
  and runner `fc93152` committed before the runs)
- **Specimen / version:** S001 (Orbium cells), S101 (`pair-seed-u8.csv`), S102 (`gyrator-seed-u8.csv`),
  S103 (`static-seed-u8.csv`); seeds scaled to R = 26 and 39 by block replication
- **Simulator / version:** `alm_check` (`src/alm_check/persistence.py` @ `fc93152`)
- **Parameters:** each specimen's registered rule (S001, S101: μ 0.15, σ 0.015; S102, S103: μ 0.155,
  σ 0.020); ladder T ∈ {10, 20, 40, 80} at R 13, R ∈ {13, 26, 39} at T 10, corner R 26 / T 40;
  128 × (R/13) torus
- **Intervention:** none
- **Metric:** preregistered: e_R = |X(R13) − X(R39)| / X(R39); e_T = |X(T10) − X∞| / X∞ with
  X∞ = 2·X(T80) − X(T40) (first-order Richardson); labels CONTINUUM-STABLE / DISCRETISATION-BIASED /
  NOT-CONVERGED by the rule fixed in `PREREGISTRATION.md`
- **Result:** e_R ≤ 0.47% for every mean property of the three moving specimens. e_T at T 10: S001
  speed 15.3%, S101 speed 9.8%, S102 turning rate 18.0% (94.8 vs X∞ 115.5°/tu) and path speed
  11.1%. All four specimens persisted and kept their registered phenotype class in all 28 runs.
  The corner matches the sum of the separate T and R effects within 1% for every mean property
  (not for the mass fluctuation).
- **Run IDs:** `research/traces/lane3/L3-002/runs.csv`, `labels.csv` (one `.json` and `.npz` per run)
- **Search / parameter bounds:** the seven conditions above; four specimens
- **Reproduction command:** `.venv/bin/python -m alm_check.persistence`
- **Known caveats:** single engine. **Scope:** the four registered specimens, seeds scaled up by
  integer block replication, R = 13, 26 and 39, and a 300 tu run with statistics over t = 100–300.
  Agreement between R = 13 and R = 39 shows the measured values stop changing over that range; it
  is not proof of a continuum limit. The preregistered X∞ uses first-order Richardson from T 40/80,
  which understates the limit when the effective order is below 1 (Lane 7 HR-005 on C009). The
  preregistered S001 speed error is 15.3%. Separately, the exploratory T 2560 runs (C051) give speed
  0.5714, which would put the T 10 deficit at about 16.1% (archivist's arithmetic from
  `s001_small_dt.txt`); that is additional evidence and does not replace the preregistered value.
  S102 from bilinear seeds dies at R ≥ 26, a resize-method effect (C047).
- **Prior literature** (bounded search 2026-10-07; entries in `references.md`):
  - [Chan2019] arXiv:1812.05433 v3, §3.1.1–3.1.2 and Fig. 7, p. 17. **CONSISTENT WITH**, similar
    outcome only: Orbium's measures "remain constant" over R 9–55, while structure falls and
    dynamics rise with T toward a limit. Chan's rule is μ 0.15, σ 0.016 with core functions not
    stated in the caption, and covers Orbium only.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3 (L3-002); extends C009 and C014 to S101 and S102.
  - 2026-10-08 — title and caveats scoped to the tested specimens, resize, resolutions and horizon (status
    unchanged) — archivist, after Bobby's review of PR #18 and Lane 3's `ab125c4`.

### C047 — S102 at its registered rule persists at R = 26 and R = 39 from block-replicated, nearest-neighbour or cubic seeds; only the bilinear seed dies

- **Status:** INDEPENDENTLY_CHECKED for the eight seeds tested (block, nearest, bilinear and cubic
  resizes × R 26 and 39; μ 0.155, σ 0.020, T 10; one seed position; 1000 tu): Lane 3 `alm_check`
  (PR #18) and Lane 6 `field.py` (PR #23) give the same eight outcomes. Exploratory in both lanes;
  only the block seeds through 300 tu are preregistered (C046).
- **Owner lane:** Lane 3
- **Sources:** L3-002 README proposed claim 2 and "Disagreement with C039"; `s102_resize_check.py`,
  `s102_resize_check.txt` (PR #18, merged as `56ae421`; wording scoped in `ab125c4`); Lane 6 rerun `d2_resize.py`, `d2-resize.csv` in `research/experiments/L6-007-attractor-geography/` (PR #23 @ `413003d`, merged as `7a4ea3b`)
- **Specimen / version:** S102 seed (`gyrator-seed-u8.csv`), resized by R/13 four ways
- **Simulator / version:** `alm_check` (`World`, `Rule` from `alm_check.lenia`); Lane 6 `field.py` (`Batch`)
- **Parameters:** μ 0.155, σ 0.020, T 10, R ∈ {26, 39}, 128 × (R/13) torus, 1000 tu
- **Intervention:** none (seed resize method varied: block, `ndimage.zoom` order 0, 1, 3, clipped to [0, 1])
- **Metric:** death = mass/R² < 0.01; otherwise mean mass over the last 100 tu
- **Result:** block, nearest and cubic seeds alive at 1000 tu at both R (mass 0.5234–0.5235; 0.5223
  at R 13). Bilinear seed died at t = 9 (R 26) and t = 6 (R 39). In L3-002 proper (block seeds)
  S102 stayed a circler at R 26, R 39 and the corner (C046). Lane 6's `field.py` rerun of the same eight
  seeds: block, nearest and cubic are CIRCLER at 1000 tu (mass 0.5234–0.5235, path speed ≈ 0.50 R/tu);
  bilinear DIED at 8.3 tu (R 26) and 6.0 tu (R 39).
- **Run IDs:** `s102_resize_check.txt`; L3-002 `runs.csv` S102 rows; Lane 6 `d2-resize.csv`
- **Search / parameter bounds:** four resize methods × two resolutions; one seed position
- **Reproduction command:** `.venv/bin/python research/experiments/L3-002-property-persistence/s102_resize_check.py`
- **Known caveats:** exploratory in both lanes; one seed position. Lane 6's original
  `persistence.py` (`ndimage.zoom(..., order=1)`, line 49 on `main`) used bilinear, which is why C039
  saw a death. Lane 6's rerun corroborates these eight seeds under this one rule, seed position and
  horizon; it is not a replication of the rest of L3-002. Lane 3 reads the result as initial-condition sensitivity
  and passes it to the attractor-geography expedition (Lane 6).
- **Dispute:** **D2** with C039, resolved 2026-10-07 in favour of this claim. See [Disputes](#disputes).
- **Prior literature** (bounded search 2026-10-07; entries in `references.md`):
  - [Davis2024] arXiv:2401.13111 v1, definition p. 18. **RELATED**: Davis calls a pattern
    "non-Platonic" if it fails at a finer discretization but persists at a coarser one. S102 at
    its registered rule does not meet it with respect to R, except from the bilinear seed. Davis's Lenia gliders use Gaussian rules and do
    not include a circler.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3 (L3-002 exploratory follow-up); contests C039 (D2).
  - 2026-10-07 — INDEPENDENTLY_CHECKED — Lane 6 reproduced all eight outcomes in `field.py` (`413003d`); D2 resolved.
  - 2026-10-08 — held at OBSERVED — archivist: Lane 6's evidence is not yet on `main`, and Bobby asked that
    dependent claims not land before their evidence. Upgrade when L6-007's D2 rerun merges.
  - 2026-10-08 — INDEPENDENTLY_CHECKED (eight seeds only) — archivist: Lane 6's rerun merged in PR #23 (`7a4ea3b`).
    Not a check of any other seed position, rule, horizon or of the rest of L3-002.

### C048 — S103 is a bitwise fixed point at every timestep tested (T 10–80), but block-scaled to R = 26 or 39 it relaxes to a different static body

- **Status:** OBSERVED (R statement, single engine); INDEPENDENTLY_CHECKED (T statement, with C042:
  `field.py`/`alm` and `alm_check`)
- **Owner lane:** Lane 3
- **Sources:** L3-002 README proposed claim 3 and label table (PR #18, merged as `56ae421`; wording scoped in `ab125c4`)
- **Specimen / version:** S103 seed (`static-seed-u8.csv`)
- **Simulator / version:** `alm_check` (`persistence.py` @ `fc93152`)
- **Parameters:** μ 0.155, σ 0.020; T ∈ {10, 20, 40, 80} at R 13; R ∈ {26, 39} at T 10; corner R 26 / T 40
- **Intervention:** none
- **Metric:** exact fixed point (final state equals seed); mass, gyradius
- **Result:** fixed point at T 10, 20, 40 and 80 (mass 0.378698 at each). Block-scaled to R 26 it
  settles static at mass 0.380599 (+0.5%) and to R 39 at 0.374835 (−1.0%), neither equal to the scaled seed.
  Whether those bodies are themselves exact fixed points was not tested.
  The preregistered rule labels mass and gyradius NOT-CONVERGED (R).
- **Run IDs:** `research/traces/lane3/L3-002/labels.csv` S103 rows
- **Search / parameter bounds:** seven conditions
- **Reproduction command:** `.venv/bin/python -m alm_check.persistence`
- **Known caveats:** the R-scaled ring depends on the seed resize too. Lane 6's bilinear seed at
  R 26 settled static at mass 0.378748 (`persist-T10-R26.csv`), against 0.380599 from Lane 3's
  block seed (archivist's comparison). The two lanes agree it stays static; they do not yet have a
  common R 26 state to compare bitwise. So the R statement mixes resolution dependence with
  resize-method dependence; the T statement involves no resize.
- **History:**
  - 2026-10-07 — T statement INDEPENDENTLY_CHECKED (agrees with Lane 6's C042 in a distinct
    engine), R statement OBSERVED — archivist, from L3-002.

### C049 — At T = 10, S001's and S101's mass and gyradius are within 2.3% of their Δt → 0 values; S102's are 6.7% and 4.6% high

- **Status:** OBSERVED (preregistered; single engine)
- **Owner lane:** Lane 3
- **Sources:** L3-002 README proposed claim 4, label table and "Reading the labels honestly" (PR #18, merged as `56ae421`; wording scoped in `ab125c4`)
- **Specimen / version:** S001, S101, S102 (as C046)
- **Simulator / version:** `alm_check` (`persistence.py` @ `fc93152`)
- **Parameters:** as C046
- **Intervention:** none
- **Metric:** e_T as in C046
- **Result:** e_T: S001 mass 2.3%, gyradius 0.05%; S101 mass 1.5%, gyradius 0.2%; S102 mass 6.7%,
  gyradius 4.6%. Preregistered labels: S101 mass and gyradius CONTINUUM-STABLE; S001 mass and
  gyradius NOT-CONVERGED (T); S102 mass and gyradius DISCRETISATION-BIASED (T).
- **Run IDs:** `labels.csv`
- **Search / parameter bounds:** as C046
- **Reproduction command:** as C046
- **Known caveats:** the preregistered labels stand as the result. Lane 3's first wording ("S101 and
  S001 … continuum-stable within 2.5%") was stronger than those labels; its revised claim 4
  (`ab125c4`) now matches them. "CONTINUUM-STABLE" means the property passed the rule on this ladder
  (T ≤ 80, R ≤ 39, 300 tu), not that a continuum value is established. Lane 3 attributes S001's label to a strict convergence
  test (mass) and a missing flatness clause for T (gyradius), and proposes a 0.5% T-flatness clause
  for later tests. Separately, the exploratory small-dt runs (C051) show S001 mass approaching about
  0.4249; that does not change the preregistered NOT-CONVERGED (T) label.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3 (L3-002); title set by the archivist to the measured values.

### C050 — S101's relative mass fluctuation grows about 5× from T = 10 to T = 80 and has not converged

- **Status:** OBSERVED (preregistered measurement; single engine)
- **Owner lane:** Lane 3
- **Sources:** L3-002 README proposed claim 5 and bottom line 5 (PR #18, merged as `56ae421`; wording scoped in `ab125c4`)
- **Specimen / version:** S101 (`pair-seed-u8.csv`)
- **Simulator / version:** `alm_check` (`persistence.py` @ `fc93152`)
- **Parameters:** S001 rule; T ∈ {10, 20, 40, 80} at R 13; R 26, R 39 at T 10
- **Intervention:** none
- **Metric:** sd/mean of mass over the measurement window
- **Result:** 1.31e−3 (T 10), 1.02e−3 (T 20), 5.04e−3 (T 40), 6.28e−3 (T 80): ×4.8 from T 10 to 80,
  not monotone. It shrinks with R (4.6e−4 at R 26, 1.3e−4 at R 39). Label NOT-CONVERGED (T).
- **Run IDs:** `labels.csv` (S101 `mass_rel_sd`)
- **Search / parameter bounds:** as C046
- **Reproduction command:** as C046
- **Known caveats:** cause not investigated; Lane 3 lists it as a follow-up candidate. The dip at
  T 20 means "grows with T" is not monotone growth.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3 (L3-002).

### C051 — S001 survives at T = 640, 1280 and 2560 and approaches mass 0.4249 and speed 0.571 R/tu, consistent with C009's extrapolated limit

- **Status:** OBSERVED (single engine; exploratory, not preregistered)
- **Owner lane:** Lane 3
- **Sources:** L3-002 README proposed claim 6 and "S001 at very small timesteps"; `s001_small_dt.py`,
  `s001_small_dt.txt` (PR #18, merged as `56ae421`; wording scoped in `ab125c4`). Prompted by the archivist's Kojima 2023 note.
- **Specimen / version:** S001, dossier commit `65c03cc`
- **Simulator / version:** `alm_check`
- **Parameters:** baseline with T ∈ {640, 1280, 2560} (dt 0.0016, 0.00078, 0.00039), 300 tu
- **Intervention:** none
- **Metric:** alive at t = 300; mass and speed
- **Result:** alive at all three. Mass 0.4252 / 0.4250 / 0.4249; speed 0.5691 / 0.5707 / 0.5714 R/tu.
  Consistent with C009's extrapolated limit (mass ≈ 0.4249, speed ≈ 0.572).
- **Run IDs:** `s001_small_dt.txt`
- **Search / parameter bounds:** three timesteps; 300 tu horizon
- **Reproduction command:** `.venv/bin/python research/experiments/L3-002-property-persistence/s001_small_dt.py`
- **Known caveats:** same engine as C009, so this confirms C009's extrapolation but is not a second
  lane. The 300 tu horizon is shorter than C009's 400.
- **Prior literature** (bounded search 2026-10-07; entries in `references.md`):
  - [Chan2019] arXiv:1812.05433 v3, §3.1.2 and Fig. 7(c–d), p. 17. **CONSISTENT WITH**, similar
    outcome only: Orbium runs to T = 2560 with measures approaching a limit, under μ 0.15, σ 0.016.
  - [Kojima2023] arXiv:2305.13784 v1, §2.1.2 and Fig. 2, p. 4. **CONTRADICTORY**, similar outcome
    only: an Orbium "disappeared … when [dt] was small (dt = 0.002)". Kojima uses Gaussian growth
    and does not state the kernel, R or grid, so the conditions are not shown to match. Lane 3 did
    not check which rule Kojima ran.
- **History:**
  - 2026-10-07 — OBSERVED — Lane 3 (L3-002 exploratory follow-up).

### C052 — At the coexistence rule, first contact between the settled glider and S103 fuses them and ignites a world-covering colony of small static bodies; isolated controls stay in class (bitwise ring at N256, R13)

- **Status:** INDEPENDENTLY_CHECKED for contact, fusion and ignition (FISSION + PROLIFERATION in the t_c + 20 window, through 25 tu) on P2 and P3 via `alm_check` direct convolution; clean replay bitwise. World coverage by ~50 tu is OBSERVED (`alm` only, including N512). T20 keeps the class but not its timing (C053); R26 is a weaker check (non-fixed-point ring, D-024; scored from per-step rows, numerics 8f17849). The other ten encounters are OBSERVED.
- **Owner lane:** REEF expedition (field runs, behavior scoring, numerics checks; coordinator ledger)
- **Sources:** `research/reports/reef-expedition-2026-10-20.md`; `research/experiments/REEF/` (PROTOCOL v1 + §11, DECISIONS D-014–D-024); `REEF-field/README.md`; `REEF-behavior/audit/pilot-table.md`, `audit/discovery-table.md`; `REEF-numerics/checks/MATRIX.md`
- **Specimen / version:** glider = S001 cells settled 500 tu under the coexistence rule (GA sha256 `982b7939…`, GB `63e381b8…`, elapsed-time snapshots 0.5 tu apart); ring = S103 (`1e9aa713…` at N256)
- **Simulator / version:** `alm` via `REEF-field/runner.py` @ `fe4ba1c`; checks `alm_check` (FFT, direct) via `REEF-numerics/replay.py` and `check_runner`
- **Parameters:** μ 0.155, σ 0.020, poly/poly, β [1], R 13, T 10, Euler + clip, float64, periodic N 256; checks also T 20, R 26 (2×2 block, N 512), N 512 at R 13
- **Intervention:** none; the ring is placed 4 R ahead (clear gap 3.97–4.03 R) at transverse offset b/R ∈ {−1.5, −1.25, −1, 0, +1, +1.25, +1.5}
- **Metric:** PROTOCOL §7 classes and §11 thresholds, frozen before encounters; scored on [0, t_c + 20 tu]; PROLIFERATION flag added post hoc (D-016)
- **Result:** 12/12 encounters (P1–P6, X1–X6) score FISSION + PROLIFERATION: interaction onset (residual > 1e-10) 0.6–1.0 tu before support contact; contact at 6.1–7.7 tu; the bodies never separate; 47–114 bodies and mass ×26–50 at the window end; the N256 torus is covered by ≈ 50 tu. Matched G-alone stays GLIDER (0.548 R/tu) and S-alone stays bitwise fixed. No run censored inside its window. Not observed: pass, deflection, capture, glider death.
- **Run IDs:** REEF-P1-E…REEF-P6-E, REEF-X1-E…REEF-X6-E, controls REEF-CTRL-GA/GB and REEF-P*/X*-S; checks REEF-P2/P3-E-{replay,chkfft,direct,T20,R26,N512}
- **Search / parameter bounds:** b/R ∈ [−1.5, +1.5] (mandate bound), two snapshots, one approach distance, N256
- **Reproduction command:** see the report's "Shortest reproduction"
- **Known caveats:** finite horizon (t_c + 20 tu at N256; colony meets its own images ≈ 27–30 tu); ignition timing and colony mass are NUMERICALLY_FRAGILE (C053); R26's ring is not a fixed point at R26 (C048), so that check is weaker (D-024); one rule, one ring size; no offset beyond 1.5 R; cell identity is meaningless after ignition; both routes were scored with the same tracker (`REEF-behavior/score.py`); the direct route covers 3–25 tu, 1.1–1.7 tu short of the scoring window end.
- **Prior literature:** [Chan2019] §3.5.5, pdf p. 29, "Detonation, the resultant mass explodes into infinite growth" — **PREVIOUSLY REPORTED** (the phenomenon, Orbium–Orbium, rule unstated). [Chan2019] §3.3.1, pdf p. 21, Class 2 "regional, periodic immobile patterns (e.g. Circium)" — **CONSISTENT WITH** the frozen lattice. In-repo: S103 dossier I003 ≥ 0.30 fills the world; HR-009 world-filling S102 copy at this rule. Novelty: not claimed. Details `REEF-behavior/LITERATURE.md`.
- **History:**
  - 2026-10-21 — INDEPENDENTLY_CHECKED (qualitative, P2/P3) — REEF coordinator, from the integration PR evidence.

### C053 — The ignition time and colony mass of C052 depend on timestep and resolution

- **Status:** NUMERICALLY_FRAGILE
- **Owner lane:** REEF numerics
- **Sources:** `REEF-numerics/checks/MATRIX.md`, README §7; panel `REEF-behavior/exhibit/F-check-matrix.png`
- **Specimen / version:** as C052, encounters P2 and P3
- **Simulator / version:** `alm` (T20, R26 runs), each with its own matched controls
- **Parameters:** T 20 (R 13, N 256); R 26 by 2×2 block replication at N 512 (same physical world)
- **Intervention:** none
- **Metric:** ignition = first time E mass ≥ 2× (G-alone + S-alone) and ≥ 5 bodies (D-017, frozen before checks); §9 tolerances t_c ± 0.5 tu, masses ± 1%
- **Result:** T20: ignition 3.1 tu (P2) and 2.1 tu (P3) earlier; E mass at 20/25 tu +62%/+48% (P2), +35%/+27% (P3); P3 t_c −0.55 tu. R26: ignition 4.3 tu (P2) and 0.9 tu (P3) earlier; mass +41%/+32% (P2), +28%/+16% (P3). Both outside the frozen tolerance; class unchanged.
- **Run IDs:** REEF-P2/P3-E-T20, REEF-P2/P3-E-R26 and their controls
- **Search / parameter bounds:** one refinement step each in T and R
- **Reproduction command:** `REEF-numerics/README.md` §7
- **Known caveats:** T20's isolated glider is 7.7% faster than T10's; T40 previously made it STATIC at this rule, so further T refinement may change the comparison itself.
- **History:**
  - 2026-10-21 — NUMERICALLY_FRAGILE — REEF numerics checks, ledgered by the coordinator.

### C054 — A passive, mass-matched Gaussian placed in contact with S103 ignites the same colony; at half the mass it does not, and the same mass 9–12 cells away evaporates without effect

- **Status:** OBSERVED (single engine `alm`; N256, with X11/X12 also at N512; preregistered as discovery geometries X7–X12, D-018/D-020/D-022)
- **Owner lane:** REEF field (runs), behavior (scores)
- **Sources:** `REEF-field/README.md` F-007–F-009; `REEF-behavior/audit/discovery-table.md`
- **Specimen / version:** S103 at the P2/P3 positions; isotropic Gaussian a·exp(−r²/2s²), s = 4.3907 cells, truncated at 4s, a = 0.68011 (mass 0.4873, gyradius 0.477 R), scaled for doses
- **Simulator / version:** `alm` via `REEF-field/discovery.py` @ `18cb4c0`, `9e34a08`, `12e56d7`
- **Parameters:** as C052
- **Intervention:** blob replaces the glider, centred at the G-alone centroid at t = 5.5 tu (X7, X8) or at t_c (X9–X12)
- **Metric:** as C052
- **Result:** X7/X8 (at 5.5 tu position): blob evaporates in 1.4 tu, never touches; final world = ring-alone bitwise. X9/X10 (full dose at contact position): FISSION + PROLIFERATION (79/87 bodies). X12 (0.75×, 0.37 ΣA/R²): FISSION + PROLIFERATION (113 bodies). X11 (0.5×, 0.24): NO_CONTACT, ring returns bitwise. Blob alone dies in every control.
- **Run IDs:** REEF-X7-E … REEF-X12-E with blob-alone and ring-alone controls
- **Search / parameter bounds:** one shape, one width, three doses at one position; two positions at full dose
- **Reproduction command:** see the report
- **Known caveats:** single engine (`alm`). World size checked: X11 and X12 rerun at N512 (numerics extra check, reef/numerics `1a01fce`, README §8) give the same outcomes (X11 E final = S-alone final bitwise; X12 ignites at 4.2 tu, mass identical to N256 to < 1e-9 rel until the N256 colony meets its images at 22.7 tu). The I003 result in the S103 dossier is a different shape and placement and is consistent but not directly comparable. X9–X12 zero one blob-tail cell overlapping a full ring cell (−1.5e-6 ΣA/R², D-021).
- **History:**
  - 2026-10-21 — OBSERVED — REEF expedition.

### C055 — Away from its own periodic images, the colony's front advances at about 0.39 R/tu

- **Status:** OBSERVED (single engine beyond 25 tu; two runs)
- **Owner lane:** REEF numerics
- **Sources:** `REEF-numerics/README.md` §7
- **Specimen / version:** encounters P2, P3 replayed at N 512, R 13
- **Simulator / version:** `alm`
- **Parameters:** as C052 at N 512
- **Intervention:** none
- **Metric:** slope versus time of r95, the 95th-percentile distance of encounter support cells (A > 0.01) from the ring centre (numerics README §7)
- **Result:** after ≈ 5 tu of acceleration, 0.39 ± 0.02 R/tu (P2 20–55 tu, P3 23–53 tu; r95 7 → 19 R), about 70% of the glider's speed; it slows only near the torus half-width (19.7 R at N512). From-ignition fits at N256 (0.31–0.37) include the acceleration.
- **Run IDs:** REEF-P2-E-N512, REEF-P3-E-N512 (long)
- **Search / parameter bounds:** two runs, one world size
- **Reproduction command:** `REEF-numerics/README.md` §7
- **Known caveats:** not checked with another arithmetic route over the long window; fragile timing (C053) may carry over to front speed under refinement (T20 front 0.38/0.32 vs 0.36/0.33 at N256 fits).
- **History:**
  - 2026-10-21 — OBSERVED — REEF numerics, ledgered by the coordinator.

### C056 — Under the S001 rule, 40 random 80 × 80 noise patches: 27 die, 4 leave a single Orbium-mass survivor, and 9 fill the world with a frozen lattice

- **Status:** OBSERVED
- **Owner lane:** VIS-talk thread (lightning-talk exhibits)
- **Sources:** `research/gallery/exhibits/G010-soup/soup-scan.json`, gallery G010
- **Specimen / version:** none (random initial states)
- **Simulator / version:** `alm` (`alm.lenia.Lenia`), scan rendered at the commit in G010's `provenance.json`
- **Parameters:** S001 rule (R 13, T 10, μ 0.15, σ 0.015, poly/poly, β [1]), 256² periodic, float64, Euler + clip
- **Intervention:** none. Initial state: 80 × 80 square of i.i.d. uniform [0, 0.3) values (`numpy.random.default_rng(seed).random`), centred, seeds 0–39
- **Metric:** at 100 tu: died if mass < 0.05 × one settled Orbium's mass; filled if fill (A > 0.1) > 0.15; otherwise k = round(mass / one Orbium's mass). Classes fixed before the 40-seed scan, after a 6-seed amplitude pilot
- **Result:** 27 died, 4 with k = 1, 9 filled. Seed 5's survivor is visibly an Orbium-like glider (film); the other three k = 1 survivors were not inspected
- **Run IDs:** `G010:scan:0` … `G010:scan:39` (final hashes in `soup-scan.json`); films `G010:seed0`, `G010:seed5`, `G010:seed1`
- **Search / parameter bounds:** one recipe (side 80, amplitude 0.3), one world size, one horizon. Pilot (6 seeds each, `research/experiments/VIS-talk/pilot_soup.py`): side 26 at amplitudes 0.5 and 1.0, side 40 at 0.25, 0.3, 0.35, 0.5 and 1.0, and side 80 at 0.25 all died; side 80 at 0.35 filled 1/6. The scan's recipe (side 80, 0.3) was chosen after the pilot, whose seeds 0–5 it re-runs
- **Reproduction command:** `.venv/bin/python research/experiments/VIS-talk/film.py G010`
- **Known caveats:** counts are for this recipe only; "Orbium-mass" is a mass count, not an identification; the filled state resembles the reef lattice (C052) but under a different rule, and the two were not compared; not checked by a second route
- **Prior literature:** Orbium emerging from random initial patches: Chan 2019 §2.3.1 (pdf p. 12). Not novel as a phenomenon
- **History:**
  - 2026-11-07 — OBSERVED — VIS-talk thread.

### C057 — 509 of 526 catalogue entries (poly/exp families, T ≤ 40) persist as bounded patterns for 100 tu in ALM's simulator; 4 die and 13 fill their world

- **Status:** OBSERVED
- **Owner lane:** VIS-talk thread (catalogue survey VIS-S1)
- **Sources:** `research/experiments/VIS-talk/survey.py`, `survey.jsonl`, `SURVEY.md`
- **Specimen / version:** every entry of `Chakazul/Lenia@adfc542` `Python/animals.json` (sha256 pinned in `alm.specimens`) with params, `kn`/`gn` in {1, 2} and T ≤ 40
- **Simulator / version:** `alm` (`alm.lenia.Lenia`)
- **Parameters:** each entry's own catalogued rule; seed placed centred on a zero periodic world of side the smallest power of two ≥ max(8 R, 3 × seed size) and ≥ 128 (65 at 128², 355 at 256², 100 at 512², 6 at 1024²)
- **Intervention:** none
- **Metric:** at 100 tu, fixed before the first run: DIED final mass < 0.05 × initial; FILLED fill (A > 0.1) > 0.25 or mass > 4 × initial; otherwise PERSISTED, split by net periodic-centroid travel over the last 50 tu (≥ 1 R MOVER, else STAY)
- **Result:** MOVER 261, STAY 248, FILLED 13, DIED 4. Died: `O2bi` Orbium bicaudatus ignis, `H4?` Tetrahelicium(?), `2PN+c`, `KN+c`. Filled: mostly the catalogue's own "Cateno-" growers, plus `OG2r`, `3GH2l`, `1P8o`, `3F4l?`, `~4T2v`
- **Run IDs:** one row per catalogue index in `survey.jsonl` (with final sha256)
- **Search / parameter bounds:** one horizon, one world size per entry, one placement
- **Reproduction command:** `cd research/experiments/VIS-talk && ../../../.venv/bin/python survey.py run --jobs 2 && ../../../.venv/bin/python survey.py table`
- **Known caveats:** PERSISTED means a bounded non-empty pattern at 100 tu, not the catalogued shape or behaviour; STAY includes rotators and oscillators; a death may reflect our placement or world size rather than the species (the four deaths were not investigated); kn/gn 3–4 entries and T > 40 entries were excluded
- **History:**
  - 2026-11-07 — OBSERVED — VIS-talk thread.

### C058 — Two S001 Orbia meeting head-on or at a right angle show four of Chan's collision outcomes (scatter, annihilation, absorption, fusion into one bound body), depending on offset

- **Status:** OBSERVED
- **Owner lane:** VIS-talk thread (lightning-talk exhibits)
- **Sources:** `research/gallery/exhibits/G009-orbium-collisions/outcomes.json`, gallery G009
- **Specimen / version:** S001 settled 1000 steps on 128², integer-rolled to centre, 48² crop; partner = `np.rot90` of it by 180° (head-on) or 90° (right angle)
- **Simulator / version:** `alm`
- **Parameters:** S001 rule, 256² periodic, float64, Euler + clip; each body starts 5 R from the meeting point; head-on transverse offsets b = 0, 0.25, 0.5, 0.75, 1 R; right angle with the partner crossing A's line b = 0, 0.5, 1, −0.5 R beyond the meeting point
- **Intervention:** none
- **Metric:** at 120 tu, k = round(mass / one Orbium's mass); k = 2 with one connected component of A > 0.01 → "fused into one bound pair"; k = 2 otherwise → "scattered"; k = 1 → "one survives"; k = 0 → "both die". Fixed before the final runs; an earlier version of the rule, counting components at A > 0.1, split single Orbia into two and was replaced
- **Result:** head-on b 0, 0.75, 1 R: scattered; b 0.25 R: both die; b 0.5 R: fused. Right angle b 0: fused; b 0.5, 1, −0.5 R: one survives
- **Run IDs:** `G009:<label>` in `provenance.json` (final hashes)
- **Search / parameter bounds:** one Orbium phase, one starting distance, nine geometries, single runs
- **Reproduction command:** `.venv/bin/python research/experiments/VIS-talk/film.py G009`
- **Known caveats:** collision outcomes depend on phase and exact offset, so each geometry is one sample; whether the fused bodies are S101 (C041) was not checked; on a 256² torus debris can meet again
- **Prior literature:** Chan 2019 §3.5.5 (pdf pp. 28–29) lists deflection, reflection, absorption, annihilation, detonation, fusion and parallelism. Not novel
- **History:**
  - 2026-11-07 — OBSERVED — VIS-talk thread.

### C059 — An exactly symmetric soup under the S001 rule loses its symmetry through float64 FFT rounding: the mirror difference grows from 2 × 10⁻¹³ at 5 tu to 1 by 40 tu

- **Status:** OBSERVED
- **Owner lane:** VIS-talk thread
- **Sources:** gallery G014, `research/gallery/exhibits/G014-kaleidoscope/asymmetry.csv`
- **Specimen / version:** none. `d4_soup(seed=4)` in `ex_bizarre.py`: an 80 × 80 patch of uniform [0, 0.3) noise with all 8 square symmetries, centred on 256², asserted exactly invariant under `rot90` and transpose at t = 0
- **Simulator / version:** `alm.lenia.Lenia` (numpy pocketfft, float64)
- **Parameters:** S001 rule, 256² periodic, Euler + clip
- **Intervention:** none
- **Metric:** max over cells of max(|A − rot90 A|, |A − Aᵀ|), every 2 steps
- **Result:** 0 at t = 0; 1.8e-13 at 5 tu; 2.7e-10 at 15 tu; 2.3e-5 at 25 tu; 1 at 40 tu. The colony is growing over the same window (mass 3.0 → 54 R²)
- **Run IDs:** `G014:d4-soup-seed4`
- **Search / parameter bounds:** one seed filmed. Pilot of 24 D4 soups (seeds 0–11 at amplitudes 0.3, 0.35): 8 filled the world and all 8 were fully asymmetric (difference 1) by 100 tu; 16 died
- **Reproduction command:** `.venv/bin/python research/experiments/VIS-talk/film.py G014`
- **Known caveats:** the size and timing of the break depend on the FFT implementation and summation order; the exact growth rate was not fitted
- **History:**
  - 2026-11-07 — OBSERVED — VIS-talk thread.

### C060 — An S001 Orbium gliding into a half-world whose μ differs by ±0.01 crosses; by ±0.02 or more (0.12, 0.13, 0.17, 0.18) it dies at the boundary

- **Status:** OBSERVED
- **Owner lane:** VIS-talk thread
- **Sources:** gallery G018
- **Specimen / version:** S001 settled 1000 steps, 48² crop, pasted at row 40, column 128 of 256²
- **Simulator / version:** `FieldLenia` (`ex_bizarre.py`), bitwise equal to `alm.lenia.Lenia` at uniform parameters (checked at render)
- **Parameters:** S001 rule except μ = X in rows 128–255 (σ unchanged); X ∈ {0.12, 0.13, 0.14, 0.16, 0.17, 0.18}; periodic, so walls at rows 128 and 0
- **Intervention:** spatial step in μ (a modified rule, not classic Lenia)
- **Metric:** at 120 tu, final mass > 0.5 × one Orbium → crosses; else dies
- **Result:** crosses for 0.14 and 0.16; dies for 0.12, 0.13, 0.17, 0.18
- **Run IDs:** `G018:mu<X>`
- **Search / parameter bounds:** one phase, one approach angle, six values of X; a σ-wall prototype (σ 0.018, 0.021, 0.025) gave mixed results and is not filmed
- **Reproduction command:** `.venv/bin/python research/experiments/VIS-talk/film.py G018`
- **Known caveats:** a "cross" is a mass test, not a shape test; uniform-rule survival bounds for Orbium are a different question (the Orbium is not at μ = X before the wall)
- **History:**
  - 2026-11-07 — OBSERVED — VIS-talk thread.

### C061 — In classic 1-D Lenia's discrete limit (R = 2, T = 1) a single cell grows Wolfram's Rule 90 (the Sierpinski triangle) to within 7.5 × 10⁻⁶; the only elementary rules reached exactly are 0, 4, 5, 72, 90, 128 and 160

- **Status:** OBSERVED
- **Owner lane:** VIS-talk thread (fractal round)
- **Sources:** gallery G019; `research/experiments/VIS-talk/eca_reach.py`
- **Specimen / version:** none; one cell set to 1 on a zero 1 × 1024 ring
- **Simulator / version:** `alm.lenia.Lenia` unchanged, on a 1 × N world (the kernel then only sees offsets along the row)
- **Parameters:** poly kernel core, R = 2 (weight 1/2 at offsets ±1, 0 at the cell itself), exp growth μ = 0.5, σ = 0.1, T = 1; 511 steps
- **Intervention:** none (rule choice)
- **Metric:** max |A − Rule 90| over all 512 rows, Rule 90 computed independently by integer XOR; for the reachable set, all eight neighbourhoods must map to 0 or 1 within 10⁻³ over a μ × σ grid for both growth families
- **Result:** max difference 7.45 × 10⁻⁶, identical after thresholding at 0.5. Reached set {0, 4, 5, 72, 90, 128, 160}; Rule 90 is the only one of Wolfram's class 3. Why the set is small: a birth (0 → 1) needs G(u) = +1 exactly, which only happens at u = μ, so at most one neighbour sum can cause births; and the kernel is mirror-symmetric with zero self-weight, so left–right asymmetric rules such as Rule 30 and Rule 110 are out of reach.
- **Run IDs:** `G019:rule90`; melt grid `G019:melt:T<T>:s<σ>`; sweep `G019:sweep:T1:s<σ>`
- **Search / parameter bounds:** reachability only at R = 2, T = 1, binary states, single kernel, β = [1]; μ on 401 points in [0, 1], σ on 300 log-spaced points in [0.005, 1]. The melt grid (T 1, 2, 4 × σ 0.10, 0.17, 0.20, 0.30) is descriptive only: the triangle persists at T = 2 and T = 4 for σ = 0.17 with intermediate cell values, and dissolves as σ widens
- **Reproduction command:** `.venv/bin/python research/experiments/VIS-talk/film.py G019` (verify: `film.py verify G019`); `python research/experiments/VIS-talk/eca_reach.py`
- **Prior literature:** Chan 2019 §2.1.6 embeds Game of Life in discrete Lenia (R = T = P = 1, rectangular core and growth); this is the same move in 1-D. No Lenia paper we hold mentions Rule 90 or Sierpinski patterns. Chan 2019 §3.3.1 maps Wolfram's four classes onto Lenia's μ–σ landscapes, which is a different statement.
- **Known caveats:** T = 1 is far from the Orbium regime (T = 10); the reached set depends on the 10⁻³ exactness tolerance and the sampled grid (the analytic argument above covers births but not every keep-state case)
- **History:**
  - 2026-11-08 — OBSERVED — VIS-talk thread (fractal round).

### C062 — In 2-D Lenia with R = 2, T = 1 and growth centred on the weight of one diagonal neighbour, a single cell's state at every step is exactly the outer product of two Rule 90 rows

- **Status:** OBSERVED
- **Owner lane:** VIS-talk thread (fractal round)
- **Sources:** gallery G020
- **Specimen / version:** none; one cell set to 1 on a zero 512² torus
- **Simulator / version:** `alm.lenia.Lenia` unchanged
- **Parameters:** poly kernel R = 2, poly growth μ = k[1,1] = 0.0800471273… (normalised weight of one diagonal neighbour), σ = 0.004, T = 1; 255 steps
- **Intervention:** none (rule choice)
- **Metric:** max |A_t − r_t ⊗ r_t| over all 256 frames, r_t = Rule 90 row from one cell (integer XOR)
- **Result:** 0.0 at every step, and every frame is exactly 0 or 1. The reason: with A = a(y)a(x), the diagonal-neighbour sum factorises into (a(y−1) + a(y+1))(a(x−1) + a(x+1)), which equals 1 only when both factors are 1
- **Run IDs:** `G020:diag`
- **Search / parameter bounds:** one seed, one world size, 255 steps. A 1,200-rule random search at R 2–5, T 1–3 from 1–9-cell seeds found symmetric growing crystals and textures but no other exact fractal
- **Reproduction command:** `.venv/bin/python research/experiments/VIS-talk/film.py G020` (verify: `film.py verify G020`)
- **Known caveats:** discrete limit only; the product structure holds for product-form seeds and is not claimed for other starts
- **History:**
  - 2026-11-08 — OBSERVED — VIS-talk thread (fractal round).

### C063 — Four bodies (Orbium, a crescent glider, two shapeshifting stars) keep their motion class for 200 tu when moved into each of the four poly/exp kernel × growth combinations

- **Status:** OBSERVED
- **Owner lane:** species-hunt thread
- **Sources:** `research/experiments/SPECIES-scout/convergence.py`, `convergence.jsonl`, `convergence-matrix.png`; gallery G021
- **Specimen / version:** S001 (Orbium) on 256²; crescent = SPECIES-scout R4 soup `default_rng([1, 56])` world 2; star A = R5 soup `[1, 27]` world 3; star B = R5 soup `[1, 55]` world 0. Each is settled 200 tu under its home rule. Seeded runs are bitwise equal to the scout runs (`convergence.py check`)
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** home rules: Orbium poly/poly μ 0.15 σ 0.015 R13; crescent poly/exp μ 0.2817 σ 0.0406 R13 b=[1]; star A exp/exp μ 0.1803 σ 0.0204 R18 b=[1,1/6,11/12]; star B exp/exp μ 0.1722 σ 0.0158 R18 b=[1,1/6,2/3]; T10, N256. Transplant: same R, T, μ and shells, with kernel ∈ {poly, exp} × growth ∈ {poly, exp} and σ = home σ × f, for f = 0.70 … 1.30 in steps of 0.03
- **Intervention:** change of kernel core and growth curve (each is still classic Lenia)
- **Metric:** `scout.classify` at 200 tu: BODY means 1–3 compact components each < 6 R across, with subclass GLIDER / STATIC / OSC from the 20-tu shift-correlation
- **Result:** every body survives in all 4 families, in its home motion class (Orbium and crescent GLIDER, stars OSC), within a σ window. That window contains the home σ (f = 1.00) in 15 of 16 cells; the exception is star A under poly/poly (OSC only at f 0.79–0.88). Windows: Orbium f 0.88–1.30, crescent 0.94–1.12 (narrowest), star A 0.73–1.06, star B 0.79–1.09. Each body's nearest catalogue cousin is O2u, the hollow Pterifera (P4cf/P5cf), and 3R5m *Asterium metamorpha* for both stars
- **Run IDs:** `convergence.jsonl` rows (body, fam, i) with final_sha256
- **Search / parameter bounds:** one seed per body, one μ, one R; σ only; 200 tu horizon; 256² world
- **Reproduction command:** `PYTHONPATH=src:research/experiments/SPECIES-scout .venv/bin/python research/experiments/SPECIES-scout/convergence.py run`
- **Known caveats:** "same motion class" is a coarse test, not a shape test. Thumbnails in `convergence-matrix.png` show the same shape by eye, except star A under poly/poly (a rounder ring at f 0.88). Single implementation. 200 tu is short next to the catalogue's persistence standard. Not novel: the body plans are catalogued; the observation is that they recur when the kernel and growth curves change
- **History:**
  - 2026-11-10 — OBSERVED — species-hunt thread.

### C064 — In Flow-Lenia rule FL-43 a noise patch condenses into separate ring cells, and the number of cells follows the mass: about one cell per 58 units of mass, from 4 to 57 cells

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/flow_rings.py`, `flow_rings.jsonl`; scout `flow_scan.py`, `flow_scan.jsonl`; gallery G022
- **Specimen / version:** none catalogued; FL-43 = `FlowRule.random(default_rng([7, 43]))` (10 kernels), noise patches from `default_rng([17, k])`
- **Simulator / version:** `research/experiments/WINGS/flow_lenia.py` (our numpy implementation of Plantec et al. 2023: Sobel gradients, reintegration tracking, dt 0.2, s 0.65, dd 5, θ_A 2, n 2)
- **Parameters:** R 13, 256² torus, 3000 steps (600 time units)
- **Intervention:** initial mass, via patch side p ∈ {20, 28, 40, 56, 80} (mass ≈ p²/2), 4 noise seeds each
- **Metric:** components of A > 0.05 (torus-merged) at the end; fixed before the runs
- **Result:** cells 4/4/4/4, 7/6/7/6, 15/15/14/15, 28/29/28/28, 55/57/51/53; mass per cell 48–66 (least-squares n = mass / 58.1). Total mass drift ≤ 1.3 × 10⁻¹² relative in every run.
- **Run IDs:** `flow_rings.jsonl` keys `size-<p>-s<k>` with final_sha256
- **Search / parameter bounds:** one rule out of a 60-rule scout; most scout rules made one droplet, membrane or crystal (contact sheet in the WINGS notes)
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/flow_rings.py sizes`
- **Known caveats:** components are counted, not checked to be rings one by one; at p 28 some cells are doubled up (mass per cell up to 66). One grid, one dt; the Flow-Lenia code is ours, not the authors'.
- **Prior literature:** Plantec et al. 2023 (Flow-Lenia) report that mass conservation yields bounded, individual creatures; a per-rule body size is implied there, not measured for this rule.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C065 — Switch off mass conservation (classic update A ← clip(A + dt U) with FL-43's kernels) and the same noise patch fills the world: mass ×21 and 225–231 fragments by 300 time units

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/flow_rings.py` (`classic` arm), `flow_rings.jsonl`; gallery G022
- **Specimen / version:** as C064, p 40, seeds 0–3
- **Simulator / version:** `flow_lenia.FlowLenia(conserve=False)`
- **Parameters:** as C064, 1500 steps (300 time units)
- **Intervention:** remove the flow / reintegration step (the conservation law), keep kernels and affinity
- **Metric:** total mass ratio, components of A > 0.05, cover
- **Result:** mass ×20.6–21.2, cover 0.28–0.29, 225–231 components in all 4 seeds (with conservation: 14–15 cells, C064)
- **Run IDs:** `flow_rings.jsonl` keys `classic-s<k>`
- **Search / parameter bounds:** one rule, one patch size, 4 seeds
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/flow_rings.py classic`
- **Known caveats:** the affinity U ∈ [−1, 1] is used as the growth field without retuning; a classic-Lenia rule tuned for these kernels might behave differently.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C066 — A single Gray-Scott spot (F 0.0367, k 0.0649) divides until about 300 spots tile the world; wipe half the world at t 20000 and division refills it to the control count by t 40000

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/gs_mitosis.py`, `gs_mitosis.jsonl`; gallery G023
- **Specimen / version:** one 10 × 10 seed, noise from `default_rng([11, seed])`, seeds 0–2
- **Simulator / version:** `research/experiments/WINGS/other_worlds.GrayScott` (Pearson 1993; Du 0.2, Dv 0.1, 5-point Laplacian, Euler)
- **Parameters:** 256² torus, dt 1, 40000 time units
- **Intervention:** at t 20000 reset x < 128 to u 1, v 0 (`wipe`); numerical arm dt 0.5
- **Metric:** spots = 8-connected components of v > 0.2, every 500 time units
- **Result:** control 1 → 54–60 (t 10000) → 237–258 (t 20000) → 301–305 (t 40000). Wipe: 122–136 right after → 289–292 at t 30000 → 302–303 at t 40000 (control 301–305). dt 0.5 within 2 % of dt 1 at every listed time (237–254 vs 237–258 at t 20000; 304–307 at t 40000).
- **Run IDs:** `gs_mitosis.jsonl` (arm, seed) with final_v_sha256
- **Search / parameter bounds:** one (F, k), one world size, 3 seeds
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/gs_mitosis.py 0 1 2`
- **Known caveats:** dividing spots are Pearson's (1993) result; the claim is only about these runs. A dividing pair counts as one spot until it separates.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C067 — 200 Particle Lenia particles at the published default parameters assemble into a body that spins at about 0.2 rad per 100 time units; the direction is not fixed by the rule, and removing a quarter of the particles slows the spin to 0.02–0.12

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/pl_rotor.py`, `pl_rotor.jsonl`; gallery G024
- **Specimen / version:** 200 particles uniform in [−6, 6]² from `default_rng([19, k])`, k 0–4
- **Simulator / version:** `research/experiments/WINGS/other_worlds.ParticleLenia` (Mordvintsev, Niklasson & Randazzo 2022; analytic gradient, unit-tested against finite differences)
- **Parameters:** μ_k 4, σ_k 1, w_k 0.022, μ_G 0.6, σ_G 0.15, c_rep 1, dt 0.1, 2000 time units
- **Intervention:** at t 1000: mirror x → −x (`mirror`); delete 50 particles chosen by `default_rng([23, k])` (`cull`); numerical arm dt 0.05
- **Metric:** mean change of each particle's polar angle about the centroid per 100 time units; mean of the last 5 windows
- **Result:** control |spin| 0.195–0.201 in 4 of 5 seeds (0.138 in k 4), sign + in 2, − in 3. Mirror: exactly the negated spin. Cull: |spin| 0.017–0.117 by t 2000, in 2 of 5 seeds with the opposite sign. dt 0.05: the same speed reached in 3 of 5 seeds, but the direction differs from dt 0.1 in 2 of them (0 and 2), and seeds 3, 4 were still slower at t 2000.
- **Run IDs:** `pl_rotor.jsonl` (arm, k) with final_sha256
- **Search / parameter bounds:** one parameter set, one particle count, 5 seeds, 2000 time units
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/pl_rotor.py`
- **Known caveats:** the mirror arm is a symmetry check, not a finding. Spin direction depends on the integration step, so it is a property of the run, not of the rule.
- **Prior literature:** Mordvintsev et al. 2022 show rotating particle bodies at these parameters.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C068 — A SmoothLife glider (rule SL-32) survives 1000 time units at dt 0.1, 0.05 and 0.025 and at double resolution, but its speed in units of the outer radius is 46 % higher at double resolution

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/sl_glider.py`, `sl_glider.jsonl`; scout `sl_scan.py`, `sl_scan.jsonl`; gallery G025
- **Specimen / version:** 40 × 40 window at (116, 167) of the scout's rule-32 world at step 1500 (`sl_glider.build`)
- **Simulator / version:** `research/experiments/WINGS/other_worlds.SmoothLife` (Rafler 2011 transition, smooth time step)
- **Parameters:** ra 8.830, ri ra/3, b 0.2552–0.2983, d 0.2057–0.2950, α_n 0.028, α_m 0.147; 192² torus (384² and ra ×2 for `res2`)
- **Intervention:** timestep (0.1 → 0.05 → 0.025); resolution ×2; a still ring from the same world placed 60 cells ahead (`ring`)
- **Metric:** components of A > 0.5 every 10 time units; speed = slope of the unwrapped centroid
- **Result:** alive at every check in all four arms. Speed 0.268 / 0.266 / 0.258 cells per time unit (0.0303 / 0.0302 / 0.0292 ra per time unit) at dt 0.1 / 0.05 / 0.025; 0.784 cells (0.0444 ra) per time unit at double resolution. `ring`: glider and ring merge by t 200 and a single body moves off on a new heading.
- **Run IDs:** `sl_glider.jsonl` arms with final_sha256
- **Search / parameter bounds:** 80 random rules in the scout; 5 of them left 1–3 isolated bodies, and rule 32 is the only one where one was seen to move
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/sl_glider.py`
- **Known caveats:** the speed is not converged in resolution, so it should not be quoted as a property of the continuum rule. Gliders in SmoothLife are Rafler's result.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C069 — Our independent N-D Lenia keeps 33 of Chan's 36 catalogued 3-D species alive for 100 time units, and 161 of 205 sampled multi-channel / multi-kernel "found" creatures

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/nd_lenia.py`, `nd_survey.py`, `nd_survey_3d.jsonl`, `nd_survey_found.jsonl`; gallery G026, G027
- **Specimen / version:** upstream `animals3D.json` (all 36 entries with params) and the first 12 entries of each 2-D `found/<D><C><K>.json` (pinned adfc542)
- **Simulator / version:** `nd_lenia.NDLenia`, written from upstream `LeniaNDKC.py` (CPU path); 1-channel 2-D equals `alm.lenia.Lenia` to 10⁻¹² (`tests/test_wings.py`)
- **Parameters:** each entry's own; 64³ (3-D) or 256² (2-D) torus; 100 time units
- **Intervention:** none (re-implementation check)
- **Metric:** DIED (< 1 % of start mass), FILLED (cover > 0.5), else PERSISTED
- **Result:** 3-D: 33 PERSISTED, 3 DIED. Found 2-D (first 12 entries of each of the 19 parseable 2-D files, fewer where a file is shorter): 161 PERSISTED, 41 DIED, 3 FILLED.
- **Run IDs:** survey rows with final_sha256
- **Search / parameter bounds:** first 12 entries per found file; 233p could not be parsed by upstream's own reader either
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/nd_survey.py 3d` and `nd_survey.py found <stem> 12`
- **Known caveats:** persistence only, not shape. Some found entries are Chan's work-in-progress (unnamed), so a death is not a disagreement with upstream until upstream is run on it.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C070 — Flattened to 2-D, Chan's 3-D species mostly do not survive as bodies: of 101 non-empty mid-slices run under the same rule, 47 grew over 2× (most fill with dust), 42 died and 12 kept their mass

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/flatten.py`, `flatten.jsonl`; gallery G026
- **Specimen / version:** all 36 `animals3D.json` entries
- **Simulator / version:** `nd_lenia.NDLenia`
- **Parameters:** settle 20 time units in 64³; slice through the centroid normal to each axis; 2-D run 100 time units on 128²
- **Intervention:** dimension 3 → 2 (same R, T, μ, σ, shells; the kernel becomes a disk)
- **Metric:** final / initial mass: < 0.01 DIED, > 2 GREW, else KEPT. **These three bins were set after looking at the first results** (the script's own pre-set outcome field missed growth below 50 % cover).
- **Result:** GREW 47, DIED 42, KEPT 12, empty slice 7. 28 of 36 species have no slice that keeps its mass. Slices that keep their mass include Sphaerome lithos (1Sp1l, all three) and Ovome ellipsis (3Ov1e), which becomes a small 2-D ring. 3-D controls: 35 of 36 persisted.
- **Run IDs:** `flatten.jsonl` slices with final_sha256
- **Search / parameter bounds:** one slice position per axis, one world size
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/flatten.py`
- **Known caveats:** a 2-D kernel normalised over a disk weighs the slice differently from the ball; this is the point of the test, not a confound. "KEPT" means mass only.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C071 — Each of Chan's twelve three-channel "aquarium" creatures (found/233 entries 0–11) dies within 200 time units when any one of its three channels is zeroed, and all twelve survive a tenfold smaller timestep

- **Status:** OBSERVED
- **Owner lane:** wings thread (WINGS, 2026-11-11)
- **Sources:** `research/experiments/WINGS/mc_knockout.py`, `mc_knockout.jsonl`; gallery G027
- **Specimen / version:** found/233.json entries 0–11 (code 5N7KKM: limus, gyrans, paragyrans, lithos, tardus, paratardus, lithos+n gyrans, 2lithos+gyrans, egg)
- **Simulator / version:** `nd_lenia.NDLenia`
- **Parameters:** 3 channels, 15 kernels, R 24, dt 1 (upstream reads T = 1 from params[0]); 256² torus; settle 20 time units
- **Intervention:** zero channel 0, 1 or 2 after settling; numerical arm dt 0.1
- **Metric:** as C069 over 200 time units
- **Result:** control 12/12 PERSISTED (mass ratio 1.0, egg 1.2); every knockout 36/36 DIED; dt 0.1 12/12 PERSISTED
- **Run IDs:** `mc_knockout.jsonl` (index, arm) with final_sha256
- **Search / parameter bounds:** 12 creatures of one family; whole-channel knockouts only
- **Reproduction command:** `.venv/bin/python research/experiments/WINGS/mc_knockout.py`
- **Known caveats:** knocking out a channel also removes a third or more of the mass; a mass-matched control (scaling all channels down) was not run.
- **Prior literature:** Chan 2020 (multi-channel Lenia) describes these creatures; we did not find a channel-knockout test there.
- **History:**
  - 2026-11-11 — OBSERVED — wings thread.

### C072 — One cell of Chan's "division well" (found/213 #84) on a 384² torus becomes 81 tracked cells in 2000 time units, through 135 divisions, 14 generations deep

- **Status:** OBSERVED
- **Owner lane:** replicators thread (REPLICATORS, 2026-11-14)
- **Sources:** `research/experiments/REPLICATORS/record.py`, `tree.py`, `film_tree.py`; gallery G029 (`tree.json`)
- **Specimen / version:** found/213.json entry 84 ("division well", code Found #94), cells as in the catalogue, centred
- **Simulator / version:** `research/experiments/WINGS/nd_lenia.NDLenia`
- **Parameters:** 1 channel, 3 kernels, R 15, T 10 (dt 0.1), poly kernel and growth; 384² torus; 2000 time units
- **Intervention:** none (a growth record)
- **Metric:** cells = local maxima of the field blurred by a 4-px Gaussian (above 0.05), sampled every time unit; linked by nearest neighbour (≤ 8 px, up to 3 missing frames); a new peak within 30 px of a cell is a daughter only if she and the continuing mother both last ≥ 10 frames (else flicker or peak jump). Tracker settings fixed on a 400-tu test run before this run.
- **Result:** 135 divisions, 51 tracks ended early, deepest generation 14, 81 cells at t 2000 (1 cell until t ≈ 95; 8 at t 750; 49 at t 1500). 2159 candidate births were dropped as flicker.
- **Run IDs:** `G029-family-tree/tree.json` (initial and final state sha256 prefixes c140d22989efafa3, 405175b7c50cb1f4)
- **Search / parameter bounds:** one run, one world size
- **Reproduction command:** `.venv/bin/python research/experiments/REPLICATORS/record.py 213 84 384 2000 states/well384.npz` then `film_tree.py states/well384.npz OUT "…"` (from that folder)
- **Known caveats:** the counts depend on the tracker's thresholds; the tracker cannot tell a merger from a cell that fades. Single floating-point trajectory.
- **Prior literature:** Chan found and named this creature (found/213.json; Chan 2020, multi-kernel Lenia). We did not find a lineage analysis of it.
- **History:**
  - 2026-11-14 — OBSERVED — replicators thread.

### C073 — Moving every rule number from Chan's "division well" (213 #84) to "division uncontrolled" (213 #83) shortens the time for one well cell to cover half of a 256² torus about fifteen-fold, from 1175–1530 to 85–95 time units, with no step where the median rises

- **Status:** OBSERVED
- **Owner lane:** replicators thread (REPLICATORS, 2026-11-14)
- **Sources:** `research/experiments/REPLICATORS/interp.py`, `growth.py`, `growth.jsonl`; gallery G030
- **Specimen / version:** 213 #84's cells in every arm; seed 0 = exact, seeds 1–2 = ±10⁻³ uniform jitter on occupied cells
- **Simulator / version:** `nd_lenia.NDLenia`
- **Parameters:** rule(λ): each kernel's shell heights b, μ and σ = (1 − λ)·well + λ·uncontrolled (R 15, T 10, three kernels); λ 0, 0.1, …, 1; 256² torus
- **Intervention:** the rule (λ); numerical arm T 20 (dt 0.05) at λ 0, 0.5, 1
- **Metric:** occupancy = fraction of cells where the field blurred by a 4-px Gaussian exceeds 0.05, every 5 time units; t50 = first time occupancy ≥ 0.5 (defined before the runs)
- **Result:** median t50 by λ (seeds 0–2): 1335, 560, 355, 230, 180, 140, 130, 110, 100, 90, 90 (ranges λ 0: 1175–1530; λ 1: 85–95). Plateau occupancy 0.59–0.66 at λ 0 and 0.99–1.00 at λ 1. dt 0.05: 1155, 155, 90 at λ 0, 0.5, 1.
- **Run IDs:** `growth.jsonl` (lam, seed, dtfac) with final-state sha256 prefix
- **Search / parameter bounds:** one straight line between two catalogue rules; one world size; 3 seeds
- **Reproduction command:** `.venv/bin/python growth.py 256 2500 1 SEED 0 0.1 … 1.0` and `growth.py 256 2500 2 0 0 0.5 1.0` (from `research/experiments/REPLICATORS`); `summarize.py` prints the table
- **Known caveats:** intermediate rules are ours, not catalogue entries; seed 0 at λ 0.8 (115) is slower than at 0.7 (110), so single runs are not monotone, only the medians. "Fills" includes the fine dot lattice that appears at high λ.
- **History:**
  - 2026-11-14 — OBSERVED — replicators thread.

### C074 — Chan's 3-D "self-replicate... unstable" (found/312 #21) buds from one body into 4 by t 100 and keeps multiplying until its periodic box is packed, at two timesteps and in 64³, 80³ and 96³ boxes

- **Status:** OBSERVED
- **Owner lane:** replicators thread (REPLICATORS, 2026-11-14)
- **Sources:** `research/experiments/REPLICATORS/replicate3d.py`, `replicate3d.jsonl`, `film3d.py`; gallery G031 (`replicator3d.json`)
- **Specimen / version:** found/312.json entry 21, cells centred
- **Simulator / version:** `nd_lenia.NDLenia` (D = 3)
- **Parameters:** 1 channel, 2 kernels, R 15, T 10 (dt 0.1); boxes 64³, 80³, 96³ (film); 300–320 time units
- **Intervention:** box size; numerical arm T 20 at 64³
- **Metric:** bodies = 26-connected components (torus) of the field blurred by 1.5 voxels above 0.08, every 10 time units (5 in the film); total mass
- **Result:** 64³: 1 → 4 (t 100) → 13 (t 200), mass 1062 → 42 812 (×40) at t 300, box full. 64³ dt 0.05: 1 → 4 (t 100) → 16 (t 250), mass ×37. 80³: 4 at t 100, 31 at t 250, mass ×78. 96³ (film): up to 53 bodies, mass 1062 → 128 634 (×121) at t 320. Counts fall once the box fills because bodies touch.
- **Run IDs:** `replicate3d.jsonl` (N, dtfac) and `G031-replicating-in-3d/replicator3d.json`, with state sha256 prefixes
- **Search / parameter bounds:** one creature; three box sizes
- **Reproduction command:** `.venv/bin/python replicate3d.py 312 21 64 300 1` (and `… 64 300 2`, `… 80 300 1`); film `film3d.py 312 21 96 320 OUT replicator3d` (from `research/experiments/REPLICATORS`)
- **Known caveats:** Chan named it "unstable"; the claim is about these runs only. Body counts in a packed box are not meaningful.
- **Prior literature:** Chan 2020 reports self-replication in multi-kernel and 3-D Lenia; this creature and its name are his.
- **History:**
  - 2026-11-14 — OBSERVED — replicators thread.

### C075 — Chan's 3-D "divide" (found/312 #7) splits into four bodies by t 50 and stays at four through t 300 in 64³ and 96³ boxes at dt 0.1; at dt 0.05 a fifth body appears after t 100

- **Status:** OBSERVED
- **Owner lane:** replicators thread (REPLICATORS, 2026-11-14)
- **Sources:** `research/experiments/REPLICATORS/replicate3d.py`, `replicate3d.jsonl`
- **Specimen / version:** found/312.json entry 7, cells centred
- **Simulator / version:** `nd_lenia.NDLenia` (D = 3)
- **Parameters:** 1 channel, 2 kernels, R 16, T 10; boxes 64³ and 96³; 300 time units
- **Intervention:** box size; numerical arm T 20 at 64³
- **Metric:** as C074
- **Result:** 64³ and 96³: 1 body → 4 at t 50 → 4 at every sample to t 300; mass 1730 → 5800–6100 (on average each daughter holds about 0.85 of the founder's mass). dt 0.05 (64³): 4 at t 50 and t 100, then 5 from t 150 with mass rising to 7400–8300, so "stops at four" depends on the timestep.
- **Run IDs:** `replicate3d.jsonl` (stem 312, idx 7)
- **Search / parameter bounds:** one creature; two box sizes
- **Reproduction command:** `.venv/bin/python replicate3d.py 312 7 64 300 1` (and `… 96 300 1`, `… 64 300 2`)
- **Known caveats:** not robust in the timestep (above); we did not run past 300 time units.
- **History:**
  - 2026-11-14 — OBSERVED — replicators thread.

### C076 — In a Flow-Lenia soup whose cells carry mutating genomes, genome diversity falls when genomes blend and rises when they are inherited whole, in 4 of 4 paired worlds

- **Status:** OBSERVED
- **Owner lane:** evolution soup thread (SOUP, 2026-11-14)
- **Sources:** `research/experiments/SOUP/soup.py`, `run.py`, `diversity.py`, `diversity.jsonl`, `runs.jsonl`, `SOUP.md`; gallery G033
- **Specimen / version:** none; 16 founder genomes (kernel set's own weights h + N(0, 0.25), clipped) on a Voronoi patchwork of uniform(0, 0.3) noise, `default_rng([99, seed])`, seeds 0–3
- **Simulator / version:** `SOUP/soup.Soup` (our parameter-embedded Flow-Lenia: genome = the 10 growth weights h_k per cell, transported with the matter; written from Plantec et al. 2023, not the authors' code)
- **Parameters:** kernel set 16 (`Kernels(default_rng([7, 16]))`, K 10, R 13); 256² torus; dt 0.2, s 0.65, dd 5, θ 2, n 2; genome halo 4; one mutation (disc r 10, N(0, 0.15) on all 10 weights) every 20 steps; 12 000 steps = 2400 time units
- **Intervention:** heredity. `blend`: a cell's genome is the mass-weighted mean of the parcels that arrive. `dominant`: it is the genome of the largest single arriving parcel. Each seed is run under both from the identical start with the identical mutation rng
- **Metric:** genome spread = mass-weighted RMS distance of cell genomes (A > 0.05) from their mass-weighted mean, every 40 steps
- **Result:** start 0.58–0.67. Blend at 2400 tu: 0.409, 0.322, 0.398, 0.391 (seeds 0–3). Dominant: 0.819, 0.812, 0.841, 0.839. Every blend run is below its start and every dominant run above it from 1000 tu on (blend 0.41–0.49, dominant 0.70–0.74 at 1000 tu)
- **Run IDs:** `runs.jsonl` B16s0–B16s3, D16s0–D16s3 (final_sha256)
- **Search / parameter bounds:** one kernel set (chosen as the liveliest of 60 in `scout.py`), one world size, one mutation rate, 4 seeds
- **Reproduction command:** `SOUP_OUT=… .venv/bin/python research/experiments/SOUP/run.py B16s<k> --rule 16 --seed <k> --steps 12000 --every 40 [--inherit dominant]` (D16s<k> with `--inherit dominant`), then `summarize.py diversity`
- **Known caveats:** part of the rise under `dominant` is accumulation of mutations that are never averaged away, not selection; dominant heredity also makes bodies into genome mosaics, which changes how they move. Single implementation.
- **Prior literature:** the blending-inheritance objection is Fleeming Jenkin's (1867, *North British Review*); parameter localisation in Flow-Lenia is Plantec et al. 2023.
- **History:**
  - 2026-11-14 — OBSERVED — evolution soup thread.

### C077 — In the same soup, blending ends with one body holding 68–89 % of all matter in bodies after 2400 time units (4 of 4 worlds); inheriting genomes whole keeps 70–150 bodies, the largest holding 18–47 %

- **Status:** OBSERVED
- **Owner lane:** evolution soup thread (SOUP, 2026-11-14)
- **Sources:** `research/experiments/SOUP/species.py` (`bodies`), `summarize.py bodies`; gallery G032
- **Specimen / version:** as C076
- **Simulator / version:** as C076
- **Parameters:** as C076
- **Intervention:** heredity, as C076
- **Metric:** final state; bodies = 8-connected components of A > 0.05 on the torus with mass ≥ 5; share = largest body's mass / total body mass
- **Result:** blend (seeds 0–3): 24, 17, 10, 7 bodies; largest share 0.68, 0.82, 0.70, 0.89; top three 0.91–0.98. Dominant: 130, 70, 102, 150 bodies; largest share 0.18, 0.47, 0.27, 0.24. In the film of seed 0 (G032) the large blend body is seen engulfing a colony of small dot-shaped bodies, which survive under dominant heredity
- **Run IDs:** as C076
- **Search / parameter bounds:** as C076
- **Reproduction command:** as C076, then `summarize.py bodies`
- **Known caveats:** a "body" is a thresholded component; touching bodies count as one. The comparison is between whole worlds and does not say which part of the dynamics (heredity itself, or the mosaic bodies it produces) causes the condensation.
- **History:**
  - 2026-11-14 — OBSERVED — evolution soup thread.

### C078 — A single mutant patch in a one-species soup is gone within 1000 time units under blending (12 of 12), but under whole-genome inheritance 10 of 12 persist and 4 end with more matter than they started with

- **Status:** OBSERVED
- **Owner lane:** evolution soup thread (SOUP, 2026-11-14)
- **Sources:** `research/experiments/SOUP/mutant.py`, `mutant.jsonl`, `summarize.py mutant`
- **Specimen / version:** none; one species (every genome = kernel set 16's own weights h) settled 2000 steps from uniform(0, 0.3) noise, `default_rng([99, 1000])`
- **Simulator / version:** as C076
- **Parameters:** as C076 but no background mutation; 256²; 5000 steps (1000 tu) after the mutation
- **Intervention:** one mutant disc (radius 10, centred on a mass-weighted random cell; h + N(0, 0.15) per weight, clipped), mutants 0–11 from `default_rng([555, k])`; each then run under `blend` and `dominant` from the same mutated state
- **Metric:** mutant mass = matter (A > 0.05) whose genome lies more than halfway from h towards the mutant along the mutation direction, every 50 steps
- **Result:** start 49–86. Blend: 0 at 1000 tu in 12 of 12 (0 by 500 tu in 10 of 12). Dominant at 1000 tu: 10 of 12 above 0 (21.6–124.5); mutants 2, 4, 7, 10 grew (60.5→124.5, 57.2→112.5, 77.8→98.8, 51.3→107.1); mutants 1 and 11 died out
- **Run IDs:** `mutant.jsonl` (mutant, mode, final_sha256)
- **Search / parameter bounds:** one kernel set, one settled world, 12 mutations, 1000 tu
- **Reproduction command:** `SOUP_OUT=… .venv/bin/python research/experiments/SOUP/mutant.py 0 12`, then `summarize.py mutant`
- **Known caveats:** under blending the mutant's genome is not destroyed but diluted (the matter-weighted genome total is conserved; `tests/test_soup.py`); the metric counts only matter that is still more than half mutant. Growth under `dominant` may be drift as much as advantage; we did not replicate the growers.
- **Prior literature:** Jenkin 1867 (as C076).
- **History:**
  - 2026-11-14 — OBSERVED — evolution soup thread.
### C080 — Two S001 Orbia that collide produce six kinds of outcome, depending on angle and offset: glance off, touch and part, one dies, fuse into a two-lobed glider, both die, or detonate into a world-filling labyrinth

- **Status:** OBSERVED
- **Owner lane:** collision-zoo thread (ZOO, 2026-11-14)
- **Sources:** `research/experiments/ZOO/zoocore.py`, `atlas.py`, `atlas-O.jsonl`, `atlas-O20.jsonl`, `chamber.py`, `summarize.py`; gallery G035
- **Specimen / version:** catalogue O2u (as S001's rule executes it), settled 100 tu alone on 384², cropped 41×41; each heading made by rotating the settled patch (`scipy.ndimage.rotate`, order 1) and re-settling 30 tu alone on 256²; velocities and masses are measured after settling, not assumed
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** S001 rule (poly/poly, μ 0.15, σ 0.015, R 13, T 10); 384² torus. Numerical arm: T 20, everything else equal
- **Intervention:** two settled Orbia placed so that their straight-line paths pass at impact parameter b (in R) in the relative frame, with about 2.5 R of empty space between them at the start (`place_pair`). Angle between headings θ = 15°…180° in 15° steps (180° = head-on), b = −2…+2 R in 0.25 R steps: 12 × 17 = 204 collisions
- **Metric:** at contact + 25 tu (rounded up to 5 tu): components of A ≥ 0.1 on the torus heavier than 0.15 × one Orbium. EXPLODE: total mass > 2 × the pair or support > 25 % of the world; ANNIHILATE: mass < 0.15 Orbium; one component heavier than 1.3 Orbium: FUSE, else SURVIVOR; two components: SCATTER if the pair was ever one component, else MISS; ≥ 3: MULTIPLY. Classes were defined before the T 10 run and not changed after
- **Result:** T 10: MISS 62, SURVIVOR 71, SCATTER 33, ANNIHILATE 23, FUSE 12, EXPLODE 3, MULTIPLY 0. Survivors keep 0.97–1.00 of one Orbium's mass (one body vanishes, the other is untouched); fused bodies weigh 1.94–1.98 Orbia and glide at Orbium speed as a two-lobed body; detonations (θ 60° b +0.75; θ 75° b +0.75, +1.0) reach 53–63 × the pair's mass 25 tu after contact and fill the 384² world with a labyrinth by about 70 tu (mass ×210). T 20: the same six classes (SURVIVOR 59, MISS 59, SCATTER 32, FUSE 29, ANNIHILATE 19, EXPLODE 6), detonations again at θ 75° b +0.75 and +1.0 plus four new cells (θ 75°, 105°, 120°). Cell by cell only 110 of 204 (54 %) agree between T 10 and T 20, and 60 of the 142 contact cells
- **Run IDs:** `atlas-O.jsonl` / `atlas-O20.jsonl` rows (theta, b_R) with final_sha256; `chamber.py` replays all 204 T 10 rows and matched every hash
- **Search / parameter bounds:** one species, one rule, one settled seed per heading, one world size, one horizon (contact + 25 tu); later fates beyond that horizon not classified (spot checks: fused bodies keep gliding for 120 tu)
- **Reproduction command:** `PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/atlas.py run O` (and `run O20`); `.venv/bin/python research/experiments/ZOO/summarize.py`
- **Known caveats:** the *repertoire* of outcomes survives halving the timestep; the *map* (which outcome at which θ, b) does not, so read G035 as a picture of one discretisation, not as the continuous-time answer. Heading after rotation drifts up to 5°, so the nominal θ is approximate (lattice locking, C013); the measured headings are in each row. The classifier is coarse: "SURVIVOR" does not say which Orbium survived, and SCATTER vs MISS depends on the 0.1 threshold
- **Prior literature:** Chan 2019 §3.5.5 (Complex Systems 28(3)) names Orbium–Orbium collision outcomes, including detonation, qualitatively and under unspecified rules (see `research/experiments/REEF-behavior/LITERATURE.md`). What is new here is the map under the exact S001 rule and its timestep check
- **History:**
  - 2026-11-14 — OBSERVED — collision-zoo thread.

### C081 — In the Pteryx rule (μ 0.38, σ 0.07) any contact between two Pteryx arcs detonates; a still Circium ring is swallowed when it meets an arc's wing tip and detonates the arc when it meets the body

- **Status:** OBSERVED
- **Owner lane:** collision-zoo thread (ZOO, 2026-11-14)
- **Sources:** `research/experiments/ZOO/atlas.py` worlds P and PC, `atlas-P.jsonl`, `atlas-P6-dense.jsonl`, `atlas-PC.jsonl`, `summarize.py`; gallery G037
- **Specimen / version:** catalogue P6al, P7al, P8al, P10al (atlas P), P6al–P10al (atlas PC) and C0v (Circium ventilans), all catalogued under this one rule; each settled 100 tu alone, rotated copies re-settled 30 tu
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** poly/poly, μ 0.38, σ 0.07, R 13, T 10; 512² torus
- **Intervention:** pair placement as in C080. Atlas P: every pair of {P6al, P7al, P8al, P10al, C0v}, θ ∈ {60°, 120°, 180°}, b = −8…+8 R in 2 R steps. Atlas PC: each of P6al…P10al head-on at a still C0v, b = −9…+9 R in 0.25 R steps. A first denser pass of P6al × P6al (θ 30°…180°, b −3…+3 R) is kept as `atlas-P6-dense.jsonl`
- **Metric:** C080's classifier; for C0v rows "SURVIVOR" means one body left, whose mass is compared with the arc's
- **Result:** Pteryx × Pteryx: 270 rows, EXPLODE 204, MISS 66, nothing else (dense pass: 82 of 82 EXPLODE). Pteryx × C0v (PC): for every species the outcome along b is miss | swallow | detonate | swallow | miss. The swallow windows are 0.75–1 R wide on each side, centred at |b| ≈ 3.75 (P6al), 4.25 (P7al), 4.75 (P8al), 5.25 (P9al), 5.75 (P10al) R, moving out by 0.5 R per segment, i.e. with the wing tip; every b between them detonates. A swallowing arc gains 118–141 cells of mass (one ring is 146; one outlier at P7al b −4.25 gains 58)
- **Run IDs:** rows with final_sha256 in the three jsonl files
- **Search / parameter bounds:** head-on only for the ring scan; one world size; contact + 25 tu horizon; one timestep (not checked at T 20)
- **Reproduction command:** `PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/atlas.py run P` (and `run PC`)
- **Known caveats:** EXPLODE is decided 25 tu after contact (mass > 2 × the pair); all of them were far past that (15–60 ×). Not checked at a smaller timestep or larger grid
- **History:**
  - 2026-11-14 — OBSERVED — collision-zoo thread.
  - 2026-11-14 — OBSERVED — ring scan repeated at T 20: 361 of 365 rows keep their class (C095).

### C082 — A Hexapteryx (P6al) that swallows k Circium rings becomes the catalogued Pteryx with 6 + k segments, for k = 1–4 (shape correlation 0.993–0.998, mass within 0.3 %)

- **Status:** REPRODUCED
- **Owner lane:** collision-zoo thread (ZOO, 2026-11-14)
- **Sources:** `research/experiments/ZOO/feed.py`, `feed-alt.json`, `feed-altfilm.json`, `ladder_match.py`, `ladder_match.json`; gallery G036 (`ladder.png`)
- **Specimen / version:** catalogue P6al (start), C0v (food), P7al–P10al (comparison); all settled 100 tu alone
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** the C081 rule, 512² torus
- **Intervention:** a keeper stamps one settled C0v 3 R ahead of the arc's leading edge and (lateral half-width + 0.95) R to its side, alternating sides; after the arc is one body again it digests 40 tu; a meal counts only if the arc grew by 0.5–1.5 ring masses, otherwise the keeper rewinds and tries offsets +0.8, +1.1, +0.7, +1.25, +0.6, +1.4 R (every try is logged). Meals 1–4 were all accepted at the first offset
- **Metric:** mass; best normalised cross-correlation of the fed arc's 141×141 window against each catalogue body over rotations (0.5° steps) and all shifts
- **Result:** after k = 1, 2, 3, 4 meals the arc weighs 894.1, 1030.5, 1165.5, 1299.1 against P7al 894, P8al 1029, P9al 1163, P10al 1296. Its correlation with P(6+k)al is 0.9978, 0.9986, 0.9955, 0.9934; with every other rung it is at most 0.89. Two clean processes (`feed-alt`, `feed-altfilm`) give bitwise-equal states at every meal
- **Run IDs:** sha256 per meal in `feed-alt.json` / `feed-altfilm.json`
- **Search / parameter bounds:** one start, one feeding protocol, k ≤ 4 checked by shape (beyond P10al the catalogue has only P24al)
- **Reproduction command:** `PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/feed.py run --meals 30 --alternate --tag=-alt`, then `ladder_match.py` (needs `--tag=-altfilm`, made with the same command plus `--film`)
- **Known caveats:** placement is a hand intervention (a keeper), not something that happens in a free world. Same implementation, so REPRODUCED and not independently checked; not tested at T 20 by shape (the T 20 feeding run shows the same mass steps, C083)
- **Prior literature:** the Pteryx ladder (P6al…P10al, P24al) is Chan's catalogue; we did not find it reported that rings feed one rung to the next
- **History:**
  - 2026-11-14 — REPRODUCED — collision-zoo thread.

### C083 — Fed one Circium at a time, a Hexapteryx keeps adding one segment per meal up to 21 (one-sided feeding) or 31 segments (alternating sides); feeding then stops working, by detonation or by meals that add no segment

- **Status:** OBSERVED
- **Owner lane:** collision-zoo thread (ZOO, 2026-11-14)
- **Sources:** `research/experiments/ZOO/feed.py`, `feed-run1.json`, `feed-alt.json`, `feed-T20.json`, `summarize.py`; gallery G036
- **Specimen / version:** as C082
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** the C081 rule, 512² torus, T 10; numerical arm T 20 (seeds settled at T 10)
- **Intervention:** C082's keeper protocol, 30 meals offered
- **Metric:** segments estimated from mass with the catalogue ladder (134.9 per segment from P6al→P10al); a meal "grows" if mass rises by 0.5–1.5 ring masses and one body remains
- **Result:** alternating sides, T 10: 25 meals grow the arc (4 retries in all) to mass 4144, about 31 segments; it still glides at 4.68 cells/tu (P6al: 4.63); at meal 26 every offset detonates it. One side, T 10: 15 meals to about 21 segments, then the ring is eaten without growth at 5 offsets and detonates at 2. One side, T 20: 18 meals (11 retries) to about 25 segments, then 6 offsets detonate and 1 eats without growth
- **Run IDs:** sha256 per meal in the feed logs
- **Search / parameter bounds:** one start, three protocols, one world size; segment counts beyond 10 are mass estimates, not shape checks
- **Reproduction command:** `PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/feed.py run --meals 30 [--alternate] [--T 20] --tag=-<name>`
- **Known caveats:** where the climb ends depends on the feeding protocol and the timestep, so no top rung is claimed. The arc straightens as it grows (G036), so the fixed offsets may simply stop finding the tip; a better keeper might go higher
- **History:**
  - 2026-11-14 — OBSERVED — collision-zoo thread.

### C084 — On a sphere, two Orbia launched side by side and parallel always meet; on the flat torus they never do. Of 16 sphere runs, 14 touch (all 12 with a start gap of at least 3 R), and the meeting ends three ways: both glide on (9), they fuse into one body with the bound pair's mass (4), or one dies (3)

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (GEOM, 2026-11-14)
- **Sources:** `research/experiments/GEOM/sphere.py` (`meet`, `flat`), `meet.jsonl`, `flat.jsonl`, `summarize.py`; gallery G038
- **Specimen / version:** S001 cells, cubic-interpolated onto each world (`geomlenia.patch_sampler`; on the square lattice it returns the cells exactly)
- **Simulator / version:** `geomlenia.GraphLenia`: classic Lenia with the kernel as a sparse matrix over any point set (equal to `alm.lenia.Lenia` on the square torus to 6 × 10⁻¹³, `tests/test_geom.py`). Sphere = icosahedral geodesic grid (locally a hex lattice, 12 five-fold defects), about one cell per unit area, kernel weights × spherical-Voronoi cell area, rows normalised; distance = great-circle distance
- **Parameters:** S001 rule (poly/poly, μ 0.15, σ 0.015, R 13, T 10); sphere radius ρ = 30, 40, 60, 80 cells (2.3–6.2 R); start gap 2, 3, 4, 6 R along a meridian, both animals heading along the equator's direction (parallel: both perpendicular to the arc joining them); 2000 steps. Flat control: same pairs on the 256² square torus with `alm.lenia.Lenia`
- **Intervention:** world geometry
- **Metric:** blobs = cells with A > 0.1 linked within 2.5 cells; "touch" = one blob (checked every 10 steps); at the end, each blob with mass > 0.2 R² is one body
- **Result:** flat: 0 of 4 pairs touch, both Orbia glide on (total mass 0.8706 R² at gaps 3–6 R, 0.8742 at 2 R). Sphere: 14 of 16 touch, first at 3–17 tu (later on bigger spheres); the two that never touch are the 2 R starts on the two biggest spheres. Outcomes after 200 tu: two bodies 9, one fused body 4 (ρ 30 at 3 and 4 R, ρ 40 at 3 R, ρ 80 at 6 R), one survivor 3. Fused bodies: mass 0.841–0.849 R², gyradius 0.794–0.810 R, against 0.414–0.429 R² for a lone Orbium on these spheres; the flat bound pair S101 (*Synorbium ignis* under the S001 rule) has 0.8737 R² and 0.8154 R. G038's film run (ρ 40, gap 3 R) fuses within 7 tu. G038's "planet" run (8 Orbia, random positions ≥ 4 R apart and headings, ρ 60) keeps 2 bodies (0.87 R² in all) after 80 tu
- **Run IDs:** `meet.jsonl` and `flat.jsonl` rows (rho, sep_R) with final_sha256; G038 provenance.json
- **Search / parameter bounds:** one rule, one start heading per pair, 4 radii × 4 gaps, 200 tu
- **Reproduction command:** `cd research/experiments/GEOM && PYTHONPATH=../../../src ../../../.venv/bin/python sphere.py meet` (and `sphere.py flat`; numbers: `summarize.py`)
- **Known caveats:** the fused body is matched to S101 by mass and gyradius only, not by shape or speed (on the flat torus, C094 finds that nine of twelve Orbium–Orbium fusions settle into S101 by mass, gyradius and speed). Which outcome a pair gets depends on contact geometry and is not predicted here (no monotone pattern in ρ or gap). One grid per radius; the icosahedral grid has its own lattice directions (see C087)
- **Prior literature:** none found for Lenia on curved surfaces. Geodesics on a sphere all cross, which is why the meeting is expected; the outcome mix is the observation
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C085 — Orbia travel along geodesics: two parallel Orbia on a sphere close, and on the hyperbolic plane spread apart, exactly as the geodesic law sin(d/2ρ) = sin(a/2ρ)·cos(s/ρ) or sinh(d/2κ) = sinh(a/2κ)·cosh(s/κ) predicts, within 0.27 R until they touch or leave the world

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (GEOM, 2026-11-14)
- **Sources:** `research/experiments/GEOM/pair.py`, `pair.jsonl`, `summarize.py`; gallery G038, G039
- **Specimen / version:** S001 cells as in C084
- **Simulator / version:** `geomlenia.GraphLenia`. Sphere as in C084. Hyperbolic plane = the {3,7} triangle tiling subdivided like the icosphere (locally hex, seven-fold defects), exact hyperbolic cell areas as kernel weights, hyperbolic distance; disk of geodesic radius 4 κ (κ 26) or 3 κ (κ 39), empty beyond (rows near the rim keep the interior normalisation)
- **Parameters:** S001 rule. Sphere ρ 40, 60, 80 cells × gap a = 3, 4, 6 R; hyperbolic curvature radius κ = 26, 39 cells (2 R, 3 R) × a = 2, 3, 4 R; up to 600 steps
- **Intervention:** world geometry
- **Metric:** d = geodesic distance between the mass centres of the two halves (Einstein midpoint on the hyperboloid; normalised mean on the sphere); s = distance from each seed point to its centre after 2 tu plus the accumulated centre path, averaged over the two; prediction from the seeded a and that s. Compared every 1 tu while d > 2.5 R and, on the sphere, before the first closest approach
- **Result:** hyperbolic, 6 runs: separation grows 3.0–5.1 × over 5.9–7.3 R of travel; largest |d − law| 0.23 R (κ 39, a 2 R), 0.03–0.14 R in the other five. Sphere, 9 runs: separation closes to 1.4–1.6 R; |d − law| at most 0.27 R (ρ 40, a 6 R), at most 0.08 R in the other eight; at contact the bodies stop at 1.4–1.6 R where the law gives 0.9–1.6 R. In the flat control (C084) the separation does not change
- **Run IDs:** `pair.jsonl` rows (world, L, sep_R) with final_sha256
- **Search / parameter bounds:** two curvatures each side of flat, 3 gaps, one start heading; travel 3–8 R before contact or the rim
- **Reproduction command:** `cd research/experiments/GEOM && PYTHONPATH=../../../src ../../../.venv/bin/python pair.py run` (one run: `pair.py one hyperbolic 26 3`)
- **Known caveats:** worlds are small next to the hyperbolic plane's growth: the animals reach the rim of the κ 26 disk within about 7 R of travel. One case in the sweep (ρ 80, a 3 R) never touches: the pair closes to 1.60 R as predicted, then swings between 1.7 and 3 R for 29 R of travel, which the law (non-interacting) does not describe. That geodesic motion holds at R/κ = 0.5 is the observation; we did not look for a curvature at which it fails
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C086 — Orbium keeps gliding on a sphere whose radius is 0.54 R (7 cells, circumference 3.4 R, smaller than its own kernel): it wraps into a band round the planet; at 0.46 R and below it stops being a glider

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (GEOM, 2026-11-14)
- **Sources:** `research/experiments/GEOM/sphere.py` (`curvature`), `curvature.jsonl`, `summarize.py`; gallery G038 `tiny-planets.png`
- **Specimen / version:** S001 cells as in C084, seeded by the exponential map at one point (cells farther than 60 cells cut, irrelevant on small spheres)
- **Simulator / version:** `geomlenia.GraphLenia` on the icosahedral grid (C084)
- **Parameters:** S001 rule; ρ = 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 25 cells (362–7842 cells); 3000 steps (300 tu)
- **Intervention:** world size (curvature)
- **Metric:** area-weighted mass / R²; speed = angular speed of the mass centre × ρ over the last 50 tu; bodies as in C084
- **Result:** ρ 7–25 (0.54–1.92 R): one body, gliding at 0.470–0.479 R/tu (flat S001: 0.479); mass falls smoothly with ρ, 0.433 → 0.384 R² (flat 0.4353). ρ 6 (0.46 R): two blobs of saturated cells, mass 0.564 R², speed 0.086 R/tu. ρ 5 (0.38 R): mass 0.324 R², speed 0.009 R/tu (almost still). Nothing died in 300 tu
- **Run IDs:** `curvature.jsonl` rows (rho) with final_sha256; G038 runs `G038:tiny-planet-rho*` (same hashes)
- **Search / parameter bounds:** 11 radii, one start, 300 tu
- **Reproduction command:** `cd research/experiments/GEOM && PYTHONPATH=../../../src ../../../.venv/bin/python sphere.py curvature`
- **Known caveats:** small spheres are coarse (642 cells at ρ 7), so the grid's own effects are larger there; the cell spacing is fixed at about 1 so R/ρ grows while R stays 13 cells. The ρ 6 and 5 bodies were not classified beyond mass and speed
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C087 — The heading lock (C011) is not special to square grids: on a hexagonal lattice Orbium also settles onto a few lattice-symmetric headings (29 of 31 starts on 6 headings), while on an amorphous glass of irregular cells it does not lock, its heading wanders, and 14 of 16 die within 600 tu

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (GEOM, 2026-11-14)
- **Sources:** `research/experiments/GEOM/heading.py`, `heading_hex.csv`, `heading_glass.csv`, `summarize.py`; square-grid comparison H001-X1 (`research/experiments/H001-lattice-wobble/x1_R13.csv`, C011); gallery G040
- **Specimen / version:** S001 cells, cubic-interpolated and rotated by θ counter-clockwise (`geomlenia.seed_torus`)
- **Simulator / version:** `geomlenia.GraphLenia` on a 128 × 128 torus at one cell per unit area: hex = triangular lattice (spacing √(2/√3), 16 422 cells); glass = 16 384 uniform random points relaxed 120 times by soft repulsion (`glass_torus(128, 0)`, one realisation)
- **Parameters:** S001 rule; θ = 0–30° by 1° (hex: this covers the lattice's symmetry domain), 0–30° by 2° (glass); 8000 steps (800 tu)
- **Intervention:** start rotation; lattice type
- **Metric:** heading of the periodic-centroid velocity in 1000-step windows (as H001-X1); "settled" = last two windows within 0.05°; alive = mass > 1 at the end
- **Result:** hex: 31/31 alive, 29 settled on 6 headings, 80.76° (×12), 84.26° (×2), 86.09° (×2), 86.89° (×4), 93.10° (×5), 95.74° (×4); two pairs (86.89/93.10, 84.26/95.74) are mirror images about 90°, a mirror line of the lattice; the median miss from the rotated start heading (68.2° + θ) is 1.9°, at most 12.6°. Square (C011, H001-X1): 40/46 settled on 10 headings, median miss 2.4°, at most 7.9°. Glass: 2/16 alive at 800 tu, none settled; 5 died within 100 tu and all 14 within 600 tu; the two survivors' window headings span the compass (e.g. 135°, 232°, 272°, 104°, 110°, 98°, 139°, 6°)
- **Run IDs:** rows of `heading_hex.csv`, `heading_glass.csv` (lattice, rot)
- **Search / parameter bounds:** R 13 only; one glass realisation; one start position
- **Reproduction command:** `cd research/experiments/GEOM && PYTHONPATH=../../../src ../../../.venv/bin/python heading.py hex 1 30 > heading_hex.csv` (and `heading.py glass 2 30 > heading_glass.csv`)
- **Known caveats:** the glass result is about this discretisation at R 13: random cell positions give the kernel a quenched noise (pilots on glass realisations 1 and 2 survived 150 tu with mass swings about 5× those on the hex lattice), and a finer glass (larger R) was not tried, so "glass frees the heading" is not separated from "glass is noisy". The hex plateaus are not identified with lattice vectors
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C093 — Without a keeper there is no climb: 64 of 64 Hexapteryxes loose among eight Circium rings detonate, after 30–385 time units; 6 eat one ring first and none eats two

- **Status:** OBSERVED
- **Owner lane:** collision-zoo thread (ZOO round 2, 2026-11-14)
- **Sources:** `research/experiments/ZOO/forage.py`, `forage-K8.jsonl`, `forage-K60.jsonl`, `summarize.py`; gallery G047
- **Specimen / version:** catalogue P6al, rotated to a random heading and re-settled (`atlas.body`); catalogue C0v, settled
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** the C081 rule, 512² torus, T 10
- **Intervention:** none after setup. Setup per seed (`default_rng([23, seed, K, N])`): one arc at a random place and heading, K rings at random places at least 4 R apart and 6 R from the arc's start. K = 8 for seeds 0–63; K = 60 for seeds 0–15
- **Metric:** census every 5 tu (components of A ≥ 0.1 on the torus: the arc is the heaviest > 400 cells, rings 80–250 cells); a run ends when total mass > 4 × start or support > 20 % of the world. A ring disappearing is a meal if the arc stays 60–250 cells heavier for the next 20 tu, "destroyed" if it stays within 60 cells, else a detonation
- **Result:** K = 8: all 64 runs detonated (median 80 tu, range 30–385). First encounter: detonation 56, meal 6 (the arc becomes a 7-segment arc, mass ≈ 886), ring destroyed without growth 2. Every arc that ate later detonated on its next ring. K = 60: all 16 detonated by 55 tu with no meal
- **Run IDs:** forage rows (seed, K) with init and final sha256
- **Search / parameter bounds:** one start species, two ring densities, one world size, one timestep; rings never move, so an arc meets only what lies on its straight path
- **Reproduction command:** `PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/forage.py SEED 8 3000` for SEED 0–63
- **Known caveats:** 6 of 64 (9 %) is about half of what the tip windows' share of the contact width would suggest (6 of 33 contact rows in the P6al scan, 18 %); small numbers and random headings. The census can call a detonation onset a meal, so meals are counted only when the arc's mass holds for 20 tu
- **History:**
  - 2026-11-14 — OBSERVED — collision-zoo thread.

### C094 — Nine of the twelve fused bodies in the Orbium collision atlas settle into S101, the registered bound Orbium pair (mass, gyradius and speed equal to S101's within 0.0011 R², 0.0008 R and 0.0008 R/tu)

- **Status:** OBSERVED
- **Owner lane:** collision-zoo thread (ZOO round 2, 2026-11-14)
- **Sources:** `research/experiments/ZOO/fused_check.py`, `fused_check.json`; gallery G048
- **Specimen / version:** the 12 FUSE rows of `atlas-O.jsonl` (C080), each replayed (hash checked at the row's classification time); S101 settled 500 tu alone on the same torus
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** S001 rule, 384² torus, T 10
- **Intervention:** none beyond C080's collision; run to contact + 300 tu
- **Metric:** mean over the next 50 tu of mass ΣA/R², gyradius (R) and speed (R/tu); best normalised correlation against settled S101 over 1° rotations and all shifts
- **Result:** S101: 0.8731, 0.8151, 0.4727. Nine bodies: mass 0.8735–0.8742, gyradius 0.8143–0.8155, speed 0.4719–0.4726, correlation 0.964–0.984. The other three: θ 60° b −0.5 shed a lobe and is one Orbium (mass 0.436); θ 90° b −0.5 is near but not on S101 (0.8461, 0.7961, 0.4585); θ 165° b 0 detonated after the 25 tu classification window (mass 184 R²)
- **Run IDs:** `fused_check.json` rows with replay_ok
- **Search / parameter bounds:** one timestep, contact + 300 tu
- **Reproduction command:** `PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/fused_check.py`
- **Known caveats:** correlations stay below 0.99 because the bodies glide at lattice-locked headings that differ from S101's reference run; the scalar statistics are the stronger match. C080's "FUSE" class is therefore mostly S101, but not always, and a fused body can still detonate later
- **Prior literature:** S101 is the catalogued Synorbium ignis (O4i) carried to S001's rule (S101 dossier); its dossier found it from 7 of 175 two-Orbium starts placed side by side. This finds it from collisions
- **History:**
  - 2026-11-14 — OBSERVED — collision-zoo thread.

### C095 — The tip-or-belly map of C081 survives halving the timestep: 361 of 365 ring-scan rows keep their outcome at T 20

- **Status:** OBSERVED
- **Owner lane:** collision-zoo thread (ZOO round 2, 2026-11-14)
- **Sources:** `research/experiments/ZOO/atlas.py` world PC20, `atlas-PC20.jsonl`, `summarize.py`
- **Specimen / version:** as C081, every body settled and rotated anew at T 20
- **Simulator / version:** `alm.lenia.Lenia`
- **Parameters:** the C081 rule at T 20, 512² torus
- **Intervention:** as C081's ring scan (P6al–P10al head-on at C0v, b −9…+9 R in 0.25 R steps)
- **Metric:** C080's classifier
- **Result:** 361 of 365 rows agree with T 10. The four changes are all on the +b side, one 0.25 R step at a swallow window's edge: P8al +4.25 and P9al +4.75 swallow at T 10 but detonate at T 20; P9al +5.5 and P10al +6.0 miss at T 10 but swallow at T 20. So the +b windows sit about a quarter radius further out at T 20. Every belly hit detonates at both timesteps
- **Run IDs:** `atlas-PC20.jsonl` rows with final_sha256
- **Search / parameter bounds:** head-on only; one grid
- **Reproduction command:** `PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/atlas.py run PC20`
- **Known caveats:** not checked at a larger grid or R
- **History:**
  - 2026-11-14 — OBSERVED — collision-zoo thread.

### C096 — A cone point with a 60° deficit acts as a lens: two Orbia that pass it side by side on parallel courses converge and touch, 3 of 3, following the straight lines of the cut-and-glued sheet within 0.28 R; on the flat control they never touch

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (GEOM round 2, 2026-11-14)
- **Sources:** `research/experiments/GEOM/cone.py`, `cone.jsonl`, `summarize.py`; gallery G049
- **Specimen / version:** S001 cells as in C084, seeded in a flat chart unfolded around the meridian opposite the seam (`geomlenia.seed_cone`)
- **Simulator / version:** `geomlenia.GraphLenia` on `geomlenia.cone(sectors, 150)`: a hex lattice (one cell per unit area) cut into 60° sectors around a lattice point and re-glued with 5 (300°, deficit), 6 (flat control) or 7 (420°, excess) sectors; the hex lattice is 6-fold symmetric about that point, so the seams are invisible to the lattice. Exact cone geodesic distance; apex cell area sectors/6; world radius 150 cells
- **Parameters:** S001 rule; start 6 R before the apex at chart heights ±b, both heading straight past it; gap 2b = 3, 4, 6 R; up to 800 steps
- **Intervention:** world geometry (one conical point)
- **Metric:** d = cone geodesic distance between the two halves' mass centres; prediction = distance between the two unfolded straight lines after the same path length (s = s0 + path, as C085), which on the 300° cone cross at radius 2b; stop at contact (d < 1.6 R or one blob) or within 2.5 R of the edge
- **Result:** 300°: all 3 pairs close and touch at 15–21 tu, with their centres 2.0, 3.1, 5.3 R from the apex (the lines cross at 3, 4, 6 R); |d − lines| ≤ 0.28 R while d > 2.5 R. Flat: no pair touches before the edge (31–32 tu); the gaps end at 2.1, 3.9, 6.4 R from 3, 4, 6 R, a drift of up to 0.54 R from straight lines
- **Run IDs:** `cone.jsonl` rows (sectors, b_R) with final_sha256
- **Search / parameter bounds:** one deficit angle (60°, the only one the hex lattice glues seamlessly), 3 gaps, one start distance
- **Reproduction command:** `cd research/experiments/GEOM && PYTHONPATH=../../../src ../../../.venv/bin/python cone.py run`
- **Known caveats:** the flat control's drift (up to 0.54 R over 9 R of travel) is the heading lock (C087) and sets the precision of the comparison; what happens after contact is not scored here (in G049's film the pair fuses). This is the geometry of a cosmic string (a conical deficit); no claim is made beyond the geometry
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C097 — A cone point with a 60° excess (a saddle point) acts as a diverging lens: parallel Orbia pairs that pass it spread to 11.4–14.5 R apart from 3–6 R, matching the unfolded straight lines within 0.71 R

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (GEOM round 2, 2026-11-14)
- **Sources:** as C096; gallery G049
- **Specimen / version:** as C096
- **Simulator / version:** as C096, 7 sectors (420°)
- **Parameters:** as C096
- **Intervention:** world geometry
- **Metric:** as C096
- **Result:** gaps 3, 4, 6 R grow to 11.37, 13.21, 14.45 R after about 9 R of travel past the apex (straight lines: 11.63, 12.50, 13.75 R); |d − lines| ≤ 0.28, 0.71, 0.70 R. Flat control as C096 (2.1–6.4 R). Both animals survive every pass (total mass 0.868–0.874 R²)
- **Run IDs:** `cone.jsonl` rows (7, b_R)
- **Search / parameter bounds:** as C096
- **Reproduction command:** as C096
- **Known caveats:** the error is about that of the flat control (heading lock), so the agreement is good to about 0.5 R, not better
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C098 — An Orbium aimed dead centre at the 60°-excess saddle point dies there (19 tu); offset by 0.25 R or more it passes, and every shot at the 60°-deficit point and the flat control survives (12 shots)

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (GEOM round 2, 2026-11-14)
- **Sources:** `research/experiments/GEOM/cone.py` (`apex`), `cone.jsonl` rows with `apex_shot`; gallery G050
- **Specimen / version:** as C096, one Orbium
- **Simulator / version:** as C096
- **Parameters:** S001 rule; start 6 R before the apex at chart height b = 0, 0.25, 0.5, 1 R, heading straight past it; 300°, 360°, 420°; until within 2.5 R of the edge (31–32 tu) or death
- **Intervention:** world geometry; aim
- **Metric:** total mass / R² every 1 tu (died = below 0.01); closest approach of the mass centre to the apex
- **Result:** 420°, b = 0: mass 0.40 R² at 17 tu, 0.21 at 18 tu, 0 at 19 tu, with the centre within 0.21 R of the apex. 420° at b = 0.25, 0.5, 1 R and all 8 shots at 300° and 360°: one body at the end (0.417–0.428 R²), mass never below 0.414 R², closest approach 0.17–1.2 R
- **Run IDs:** `cone.jsonl` rows (sectors, b_R, apex_shot) with final_sha256
- **Search / parameter bounds:** one start distance and heading per aim, one seed
- **Reproduction command:** `cd research/experiments/GEOM && PYTHONPATH=../../../src ../../../.venv/bin/python cone.py apex`
- **Known caveats:** a single knife-edge case: the only death needs a dead-centre aim, and offsets were tried only on one side. Why the excess point kills and the deficit point does not was not studied
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C102 — On a Klein bottle, Orbium cannot feel the twist: through 18 and 45 passages of the twisted seam in 1000 tu its path stays within 0.18 cells of the same Orbium on an ordinary torus and its mass within 2 × 10⁻⁴ of it; only the bottle's chart shows it as its mirror image after every odd passage

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (KLEIN, round 3, 2026-11-14)
- **Sources:** `research/experiments/KLEIN/klein.py`, `kb.py twist`, `twist.jsonl`, `summarize.py`; gallery G053
- **Specimen / version:** S001 cells, placed as registered (k = 0) and turned a quarter turn (k = 1), exact `np.rot90`
- **Simulator / version:** `klein.Klein`: the Nx × Ny Klein bottle (left and right edges glued straight, top and bottom glued with a flip, (x, y + Ny) ~ (−x, y)) run as its double cover, an Nx × 2Ny torus stepped by `alm.lenia.Lenia` and kept glide-symmetric (A[y + Ny, x] = A[y, −x]) by copying the mirrored lower half over the upper half after each step; `tests/test_klein.py` checks that a plain step keeps the symmetry to 1e-12, so the copy only removes round-off
- **Parameters:** S001 rule; Klein bottle 128 × 128; control: the same seed alone on the 128 × 256 torus (the cover without the mirror twin); 10 000 steps
- **Intervention:** world topology (non-orientable)
- **Metric:** the bottle's animal followed continuously on the cover, compared with the torus animal: path difference, mass in an 80 × 80 window around each; seam passages; heading on the cover and as drawn on the chart
- **Result:** k = 0 passes the twisted seam 45 times, k = 1 18 times, each travelling 479.5 R. Max path difference 0.176 and 0.177 cells, max mass difference 1.7 × 10⁻⁴ and 1.3 × 10⁻⁵ (mass 73.5). On the cover the heading stays on one lattice-locked direction (291.2–293.8° and 21.2–23.9°, as on the torus); on the chart it alternates between the two mirror lock families (≈ 21.8° and ≈ 68.2° modulo 90°) at each passage
- **Run IDs:** `twist.jsonl` rows k = 0, 1 with final_sha256 and torus_final_sha256
- **Search / parameter bounds:** one bottle size, two headings, one seed position
- **Reproduction command:** `cd research/experiments/KLEIN && PYTHONPATH=../../../src ../../../.venv/bin/python kb.py twist`
- **Known caveats:** this is the expected result for a flat world, which a Klein bottle is everywhere; the remaining differences are round-off, carried along the neutral translation direction. Orbium is bilaterally symmetric, so the mirror image is not a different animal; a handed creature that travels was not found (the catalogued spinners in C104 turn in place)
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C103 — In a world 23–26 cells (1.8–2.0 R) high, an Orbium heading across the short way survives on a torus, 32 of 32, but not on a Klein bottle, 3 of 32 (23 fill the world, 6 die): across the glued edge it meets its own mirror image instead of its own copy

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (KLEIN, round 3, 2026-11-14)
- **Sources:** `research/experiments/KLEIN/kb.py narrow`, `narrow.jsonl`, `summarize.py`; gallery G054
- **Specimen / version:** S001 cells turned k = 0, 1, 2, 3 quarter turns (k = 0, 2: locked heading 22° off the short direction; k = 1, 3: 22° off the long direction), centred at mid-height and x = 0, 16, 32, 48
- **Simulator / version:** as C102 (`klein.Klein`, `klein.Torus`, both `alm.lenia`)
- **Parameters:** S001 rule; width 128, heights 18–40 cells; same seed on the Klein bottle and on the torus of the same size; 4000 steps (400 tu)
- **Intervention:** world topology at fixed size
- **Metric:** outcome at 400 tu, counting bodies on the double cover for the bottle: glider (every body within 10 % of Orbium's mass), filled (mass > 5 Orbia), died (mass < 1), other
- **Result:** heading across the short way, heights 23–26: torus 32/32 gliders; Klein 3 gliders, 23 filled, 6 died. Heading along the long way, 23–26: torus 32/32, Klein 31/32 (1 died). Height 27: across-the-short-way seeds die on both (8/8 each), along-the-long-way seeds live on both. Heights 28–40: 208/208 gliders on each. Heights 18–21: no glider on either; height 22: Klein 3/16, torus 0/16 (all 16 fill)
- **Run IDs:** `narrow.jsonl` (736 rows: kind, ny, k, x0, final_sha256)
- **Search / parameter bounds:** one width, 4 headings × 4 positions per height, one length of run
- **Reproduction command:** `cd research/experiments/KLEIN && PYTHONPATH=../../../src ../../../.venv/bin/python kb.py narrow`
- **Known caveats:** below 2.2 R the kernel reaches across the short way, so the animal overlaps the neighbour that lies across the glued edge; on the torus that neighbour is itself, moving in step, on the bottle it is its mirror image, sliding the other way. The mechanism of the failure (when the fill starts, what it looks like) was filmed for one seed (G054) but not studied
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.

### C104 — A spinner beside its own mirror image does not swim: the catalogued spinners Gyropteron arcus and Gyrorbium gyrans on Klein bottles 2.5–8 R high keep their turning rate and drift at most 0.0046 R/tu, as on tori of the same size

- **Status:** OBSERVED
- **Owner lane:** strange-geometries thread (KLEIN, round 3, 2026-11-14)
- **Sources:** `research/experiments/KLEIN/kb.py spin`, `spin.jsonl`, `summarize.py`
- **Specimen / version:** catalogue cells `PG1a` (Gyropteron arcus) and `OG2g` (Gyrorbium gyrans), `alm.specimens.from_catalog`, each under its own catalogue rule; both turn in place (handed: the mirror image turns the other way)
- **Simulator / version:** as C102
- **Parameters:** width 8 R, heights 1.5–8 R, the spinner placed on the line x = 0, so on the bottle its mirror image (turning the other way) sits directly across the twisted edge, at distance equal to the height; 400 tu
- **Intervention:** world topology (mirror-image vs same-handed neighbour)
- **Metric:** net drift of the followed body over the last three quarters of the run; path speed; turning rate
- **Result:** PG1a: Klein drift 0.0015–0.0046 R/tu, torus 0.0008–0.0027, against a path speed of 0.361–0.364 R/tu; turning −32.0 to −32.4°/tu on both. OG2g: Klein drift 0.0003–0.0007, torus 0.0002–0.0023 R/tu, path speed 0.475–0.486 R/tu, turning −95.5 to −97.3°/tu. At heights 1.5 and 2 R both spinners grow without bound on both worlds
- **Run IDs:** `spin.jsonl` (36 rows)
- **Search / parameter bounds:** two spinners, one position, 9 heights
- **Reproduction command:** `cd research/experiments/KLEIN && PYTHONPATH=../../../src ../../../.venv/bin/python kb.py spin`
- **Known caveats:** this tests the vortex-pair idea (two vortices turning opposite ways push each other along) and finds no effect at the distances where the spinners survive; closer pairs are not reachable this way because both worlds grow at 2 R and below
- **History:**
  - 2026-11-14 — OBSERVED — strange-geometries thread.
