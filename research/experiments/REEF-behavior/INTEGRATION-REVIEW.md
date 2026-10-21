# Hostile review of the REEF integration (behavior lane, 2026-10-21 ~08:05Z)

**Reviewed:** `reef/coordinator` @ `57d56ea`, which imports reef/behavior `77a0054` (the import leaves
`research/experiments/REEF-behavior/` unchanged), reef/field `0141e90` and reef/numerics `e7d4ef6`. Scope as
requested:
1. `research/reports/reef-expedition-2026-10-20.md`
2. `research/claims.md` C052–C055 and the dated amendments to C038 and C041
3. `museum/rooms/65-reef.html`

I checked every number against this lane's `audit/pilot-table.md`, `audit/discovery-table.md`, `scores/*/score.json`,
the gzipped traces in project files `reef-behavior/scores/`, and numerics `checks/MATRIX.md`, `matrix.json` and README §7.

## Verdict: **changes needed** (all wording or scope; no result changes)

Nothing here overturns a result. The fixes are two wrong ranges, one misread FILL number, a check scope that
reaches past what the independent route covered, a misattribution of the R26 variant, and interpretation stated as
fact in a few places. Once R1–R9 below are applied, I approve.

## Ledger mechanics: pass

- The claims.md diff against reef/behavior has **0 removed lines**. The C038 and C041 amendments are appended as new dated
  history lines marked "status unchanged", and no earlier line was rewritten. That is append-only, as required.
- C052–C055 are new entries, and their provenance row was added to the sources table.

## Is C052 INDEPENDENTLY_CHECKED defensible? Yes, if it is scoped to what the direct route covered

The ledger rule (claims.md l. 49) allows INDEPENDENTLY_CHECKED only where **distinct implementations** agree.

- The FFT `alm_check` run is bitwise identical but uses the same arithmetic.
- N512, T20 and R26 all run on `alm` itself.
- So the status rests on **one** route: `alm_check` direct convolution. It is a distinct implementation, run by
  another lane, and it agrees on class, t_int, t_c and ignition, with masses within 1e-12.
- **That route covers 3 → 25 tu only**, which stops 1.1 tu (P2, window end 26.1) and 1.7 tu (P3, 26.7) short of the
  scoring window. It therefore checks contact, fusion, ignition and FISSION + PROLIFERATION inside about the scoring window. It does
  **not** check "world-covering", which happens around 50 tu and only on `alm`. The N512 long runs are also `alm`.

R26 being weaker does not undermine the status, because the status never depended on R26. The status line does lean on
R26 rhetorically, though. R26 is a weaker check for two reasons:
- the R26 ring is not a fixed point, so D-024 judges it as one static body;
- its class cells were scored from float64 checkpoints at 1-tu cadence, because the `--save-rows` traces were not
  published.

Both checks used the same scorer (this lane's `score.py`), so the check is independent in the simulation, not in the
scoring. That is a small risk, because FISSION and PROLIFERATION use only body counts and total mass, but it should be
stated.

**R5 below gives the exact wording change.**

## Required changes

**Report (`reef-expedition-2026-10-20.md`)**

- **R1. §1 step 1 and step 2 quote pilot-only ranges for "12 of 12".** Across P1–P6 and X1–X6:

  | quantity | report says | correct value | source |
  |---|---|---|---|
  | t_kr | 3.6–4.2 | **3.6–4.5** | X1, X5, X6 = 4.4–4.5 |
  | t_int | 5.5–6.1 | **5.5–6.8** | X1 6.7, X5/X6 6.8 |

  The t_c range (6.1–7.7) and t_int − t_c (0.6–1.0) are correct.
- **R2. §1: "The fill fraction saturates at 0.22–0.24, just under the frozen FILL threshold of 0.25".**
  - The frozen FILL test is judged on the scoring window. At window end the fill is **0.09–0.17** (P3 0.091 … X2 0.166;
    `scores/*/score.json` `observables.fill`).
  - 0.22–0.24 is the ~50 tu value, outside every window. I did not compute it and cannot verify it.
  - Say "0.09–0.17 at window end, and it saturates at 0.22–0.24 by ~50 tu (field lane)". As written, the reader is
    told FILL was nearly reached when it was not.
- **R3. R26 (table row and §3).**
  - (a) Add that the R26 classes come from the 1-tu-cadence checkpoint rescore. The per-step t_c is numerics'; the
    R26 row in panel F says this.
  - (b) The P3 R26 cell should read FISSION + PROLIFERATION (`scores/REEF-P3-E-R26-D010/score.json` carries the flag).
  - (c) §3 calls the mass band "the behavior lane's mass-band variant" and frames a "disagreement". That is not
    accurate. The band was the lead's 07:30 paraphrase, which I implemented on request; I accept D-024. Reword to:
    "a disclosed variant (D-024): requiring ring-alone mass in 0.378–0.383 scores CONTROL_FAILURE, because the R26
    ring-alone relaxes below the band at 4–11 tu, before contact; the open question is how strong a control a
    non-fixed-point ring is". §2 already describes this correctly.
- **R4. Interpretation stated as fact.**
  - "The ring is the excitable partner" (§1) should be prefixed "We interpret this as …". It is the most economical
    reading of X7–X12, but the empty-world nucleation test (your next experiment 2) has not been run.
  - "Nearby mass that decays does nothing" should read "the same mass 9–12 cells away decays without effect". It was
    tested at one distance and one dose.
- **R5. §1 "holds across arithmetic, world size, timestep and resolution".**
  - Scope it: "contact → fusion → ignition holds through 25 tu across arithmetic (direct route, 3–25 tu), world size
    (N512), timestep (T20) and, as a weaker check, resolution (R26, D-024)".
  - The *world-covering* stage is `alm` only.

**Claims**

- **R6. C052 title and status.**
  - Title: the claim "isolated controls stay in class" is bitwise only at N256/R13. Either scope it ("at N256, R13")
    or add "(R26: one static body, D-024)".
  - Status: change it to "INDEPENDENTLY_CHECKED for contact, fusion and ignition (FISSION + PROLIFERATION in the
    t_c + 20 window, through 25 tu) on P2 and P3 via `alm_check` direct; world coverage by ~50 tu is OBSERVED
    (`alm` only); T20 keeps the class but not its timing; R26 is a weaker check (non-fixed-point ring, D-024; 1-tu
    checkpoint scoring)".
  - Add to the caveats: "same scorer for both routes".
- **R7. C055 metric line.** C055 says "radius enclosing 95% of colony mass". Numerics README l. 113 defines r95 as the
  **95th-percentile distance of E support cells (A > 0.01)** from the ring centre. That is a cell count, not mass.
  Copy the numerics definition.
**Museum room (`65-reef.html`)**

- **R8. "about half a time unit before they visibly touch".** That is P2 (0.6). The range is 0.6–1.0, so say "half a
  time unit to one time unit before".
- **R9. "Two of them were rerun … with a second implementation using a different arithmetic route, and in a world
  twice as wide; all agreed".**
  - The second implementation's different-arithmetic route covered 3–25 tu only, not the world-covering stage.
    Suggested: "… all agreed through the first 25 time units, when the colony is already growing; the world-covering
    stage was watched with one engine". (R5 again.)
  - "from 0.37 of the glider-mass unit upward" mixes units. Say "masses from 0.37 upward ignite it and 0.24 does not;
    the glider carries 0.49 (same units)".
  - "So the ring is the excitable partner" needs "We read this as …" (R4).

## Checked and correct (no change)

- **Mass and body counts.** 12/12 FISSION + PROLIFERATION. Bodies 47–114 at window end. E mass ×26–50 the controls.
  ~300 bodies and mass ≈ 81 at 50 tu (traces: 291–317 bodies, 80.2–81.8). Median body ≈ 0.2 ΣA/R².
- **Interaction floor.** The 1e-10 floor is ≈ 770× the sham (sham max 1.3e-13).
- **Censoring.** No run is censored inside its window (t_cen ≥ 30.3 vs window end ≤ 27.7).
- **Blob runs X7–X12.** All match (C054's 0.75× amplitude is 0.75× mass at fixed width, so its 0.37 is consistent); `discovery-table.md`. X11 and X7/X8 return to ring-alone bitwise. The I003
  comparison is correctly labelled "consistent, not directly comparable".
- **T20 and R26 deltas.** All match `matrix.json`: ignition −3.1/−2.1 and −4.3/−0.9; masses +62/48, +35/27, +41/32,
  +28/16 %; P3 T20 t_c −0.55.
- **Literature.** The quotes and pdf pages match `LITERATURE.md`. Novelty is correctly not claimed, and the analogues
  are labelled abstract-only and testable.
- **Report §2 and §3.** Prediction failures (Pr2, Pr3) are reported as failures, and the post-hoc PROLIFERATION flag
  is disclosed.
- **Panel captions** in the museum carry the finite horizon, rule and window. "Reef is a description, not a species"
  is correct.

## Re-check of `57d56ea..0cb5c08` (2026-10-21 ~08:05Z): **approve**

I read the full diff (report, claims.md, `65-reef.html` and the regenerated `museum/site/` pages).
- **R1–R9 are all applied as specified.** C052 uses the scoped status wording verbatim, and the same-scorer caveat
  and the 3–25 tu direct-window caveat are in its caveats. C055 copies the numerics r95 definition. The R26 variant is
  attributed to D-024, and P3 R26 reads FISSION + PROLIFERATION. The FILL sentence now gives 0.09–0.17 at window end.
  The t_kr and t_int ranges are corrected. The museum text is scoped to 25 tu, the units are fixed, and the
  interpretation is labelled.
- **Ledger:** the only removed claims.md lines are C052's title, status and caveats and C055's metric. Both claims are
  new in this PR, so no dated history line was changed. C038/C041 are untouched since 57d56ea. No `museum/` or
  `research/` file still links the old C052 anchor. The site pages' ledger sha256 was regenerated (`7bd9e567d5c0`).
- **No residual changes.** The numerical checks are not re-run here. Every number I can check against this lane's
  tables and `matrix.json` matches.
