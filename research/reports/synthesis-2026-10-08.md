# Synthesis, 2026-10-08 (final)

This is the closing synthesis for October 8, the periodic synthesis described in
[`../roadmap.md`](../roadmap.md). It was written in closeout mode: no new questions, experiments,
exhibits or lanes. It reflects `main` at `96b0051` (after PRs #29, #30, #27, #33, #34 and #32). Claim statuses are the ledger's ([`../claims.md`](../claims.md)). Anything marked *proposed*
has no ledger entry yet.

## New evidence

**Merged earlier on Night 1**

- **Numerical ecology, L3-002 (PR #18; C046–C051, PR #22).**
  - For S001, S101 and S102 from block-replicated seeds, mean properties at R 13 agree with R 39 to
    0.5% (C046).
  - The timestep is the main bias at T 10. Speeds and turning rates run 10–18% low (C046), and
    S102's mass and size run 6.7% and 4.6% high (C049).
  - S101's mass fluctuation has not converged in T (C050), and S001 survives T 640–2560 (C051).
  - All of these are OBSERVED in a single engine.
- **S102 at R 26 and 39 (C047, INDEPENDENTLY_CHECKED for the eight seeds tested; PRs #18, #23,
  #25).** Block, nearest and cubic seeds circle for 1000 tu in both `alm_check` and `field.py`.
  Only the bilinear seed dies, so this is resize-method dependence, not resolution dependence.
- **Lone-Orbium baselines, L4-002 (PR #20).** A reference dataset of 165 runs, with no claim made
  from it.

**Merged in closeout, proposed claims (not yet ledgered)**

- **S102's collapse is specific to R 13, T 10 (L3-003, PR #29).**
  - At R 13, T 10, Lane 6's death step (39 799) and all 12 of its noisy fates reproduce exactly.
    The two engines do the same floating-point arithmetic, since both are numpy `rfft2` steppers.
  - Of 24 copies perturbed by 1e−12, 10 stop circling within 5000 tu: 9 die and 1 fills the world.
  - Refining either the grid or the timestep removes the collapse within the preregistered horizons.
    No runs end at R 26 (0 of 29), R 39 (0 of 3), T 20 (0 of 24) or T 40 (0 of 24).
  - Every refined run is censored at its horizon, so no refined setting is shown to be an attractor.
- **Hostile review HR-009, HR-009b and HR-009c (PR #30).**
  - At R 13, T 10, S102 is chaotic. Twins separate at 0.20 per tu, so its death step belongs to one
    floating-point trajectory.
  - The chaos weakens under refinement: 0.096 per tu at T 20, 0.077 at T 40, about 0.01 at R 26.
    Chaos and collapse are separable.
  - An I003 pulse aimed at the gap does not kill S101 at s 0.2–0.3. It unbinds the pair into two
    intact Orbia. They die only by colliding later on the 128² torus, and all 10 end as two Orbia
    on 256².
  - E2's coupling reading is withdrawn. Its preregistered verdict stays INCONCLUSIVE.

**Merged in closeout: L6-007 and L6-008 (PR #27, merged as `7cbf5ae`), proposed claims**

- **Orbium** at the coexistence rule returns from noise up to ε 0.1 (18/18).
- **S103** returns bitwise up to ε 0.3 (24/24) at the primary rule.
- **S102** collapses at R 13, T 10 and is not an attractor there: P1 and P2 are refuted. Its
  collapse is scoped to that discretisation.
- **S101 under I004 port injury:** H0 in 58 of 60 runs. The uninjured partner explains the
  apparent resilience.
- **S101 under I001:** H0 not rejected.
- **S101 under I003:** the on-gap coupling claim is withdrawn. L6-009's off-gap results are
  recorded as unverified leads, not claims.

## Refutations, narrowings and failed predictions

- **C039 is REFUTED as worded** (dispute D2). Only the bilinear-seed death stands.
- **S102 is not an attractor at R 13, T 10, and its collapse does not survive refinement** (#27,
  #29, #30). C038 still calls S102 a phenotype that "persists"; the ledger has not been updated.
- **Failed predictions in L6-007 (#27).**
  - P3 is refuted on all three blend paths. Near the circler end, the class sequence reflects the
    observation horizon, not basin geography.
  - P4 fails for the circler at T 40.
  - P4 fails for the ring under the bitwise criterion, at both variants.
- **C041's resilience is mostly trivial** (#27, accepted in HR-009). The cut removes one partner.
- **"Together is worse" under I003 is withdrawn** for the on-gap pulse. It was a 128² collision
  artifact (L6-009, HR-009c).
- **"Every death comes after at least 500 tu" (L6-f)** was a property of the sample. Deaths were
  seen at 292 tu in HR-009 and at 164 tu in L3-003.

## Open questions, recorded but not pursued (closeout)

- **Why S102's collapse needs the T 10 step at R 13**, and whether weaker chaos explains its
  absence at refined settings.
- **L6-009's off-gap leads (parked in draft #35).** At s 0.3, a pulse slightly off the gap kills the pair in 4 of 5
  phases on both world sizes. A pulse on one partner lets the pair keep a partner that dies alone
  (8 of 15). Neither is preregistered or independently checked.
- **HR-009's two-regime hypothesis** for S102 at R 13, T 10: a fragile and a longer-lived circling
  state.
- **Basin boundaries between Orbium and the static ring**, which were not tested.

## PR state at closeout

| PR | State | Note |
| --- | --- | --- |
| #29 L3-003 | merged | |
| #30 HR-009 | merged | |
| #27 L6-007/L6-008 | merged (`7cbf5ae`) | revised per Bobby's and Lane 7's reviews |
| #33 Figure D (provisional) | merged (`984354a`) | stays provisional |
| #32 museum Room 6 (provisional) | merged (`96b0051`) | stays provisional |
| #34 gallery G006 (provisional) | merged (`f29d733`) | stays provisional; shown at R 13, T 10 only |
| #35 L6-009 / L6-010 | draft, parked | exploratory work preserved; not to be resolved in closeout |
| ledger | not updated | C038 and C041 wording, and claims for L6-f, L6-c and L6-d, are for the archivist on resume |

## Decisions pending for Bobby

1. **C038 and C041.** Should the archivist narrow them on resume, now that #27, #29 and #30 have
   merged?
2. **Provisional exhibits (#32, #33, #34).** All three merged in closeout and stay labelled provisional. Revisit their text when the ledger records the Night 1 claims.
3. **Resuming.** The four open questions above are candidates for the next bounded tests, but
   none should run until you say so.
