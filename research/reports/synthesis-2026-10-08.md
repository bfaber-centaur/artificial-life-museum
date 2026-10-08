# Synthesis, 2026-10-08

The periodic synthesis described in [`../roadmap.md`](../roadmap.md). Written at `main` `517f2b6`
(after PR #28). Statuses are the ledger's ([`../claims.md`](../claims.md)); anything marked
*proposed* is still in an open PR and has no ledger status yet.

## New evidence

**Merged**

- **Numerical ecology, L3-002 (PR #18; ledgered as C046–C051, PR #22).** For S001, S101 and S102
  from block-replicated seeds, mean properties at R 13 agree with R 39 to 0.5% (C046). The timestep
  is the main bias at T 10: speeds and turning rates run 10–18% low (C046), and S102's mass and size
  run 6.7% and 4.6% high (C049). S101's mass fluctuation has not converged in T (C050). S001
  survives T 640–2560 (C051). All of these are OBSERVED in a single engine.
- **S102 at R 26 and 39 (C047, INDEPENDENTLY_CHECKED for the eight seeds tested; PRs #18, #23,
  #25).** Block, nearest and cubic seeds circle for 1000 tu in both `alm_check` and `field.py`. Only
  the bilinear seed dies. This is resize-method dependence, not resolution dependence.
- **Lone-Orbium baselines, L4-002 (PR #20).** A reference dataset of 165 runs with no claim
  attached. Survival edges for a lone S001: I001 at 8–12%, I004 at 5.2–10.3%, and I003 between
  +27% and +36%.

**Open, proposed only**

- **Attractor geography, L6-007 (PR #27).** Orbium at the coexistence rule returns from noise up to
  ε 0.1 (18/18), and S103 returns bitwise up to ε 0.3 (24/24). S102 is not an attractor: P1 and P2
  are refuted. In an exploratory follow-up the unperturbed seed died at step 39 799, and 8 of 12
  perturbed starts survived past 5000 tu.
- **Pair coupling, L6-008 (PR #27).**
  - I004 port injury: H0 holds in 58/60 runs. C041's "fission" is the uninjured partner surviving.
  - I001 attenuation: H0 is not rejected.
  - I003 frontal mass: H1, the partners drag each other down, at s 0.2–0.4.
- **Hostile review, HR-009 (PR #30).**
  - **E1 (S102 lifetimes).** Copies perturbed by 1e−14 to 1e−10 separate at about 0.20 per tu.
    Their death times scatter from 292 tu to beyond 5000 tu. S102 is therefore a chaotic transient,
    and its exact death step belongs to one floating-point trajectory rather than to the rule.
  - **E2 (S101 frontal mass).** Each partner alone survives even the full I003 pulse at s 0.2–0.3,
    yet the pair dies or degrades, so coupling stands there. At s 0.4 the drag-down is explained by
    pulse exposure. The preregistered verdict is **INCONCLUSIVE** (6 of 10 runs, threshold 8).
- **Independent lifetime study, L3-003 (PR #29, draft).** The preregistration, Amendment 1 (the Q6
  lifetime distribution under δ = 1e−12) and the runner are committed. No results yet.

## Refutations, narrowings and failed predictions

- **C039 is REFUTED as worded** (dispute D2, resolved in favour of C047). The narrower fact, that
  the bilinear seed dies, stands.
- **S102 is not an attractor** (proposed, #27, and strengthened by HR-009 E1). L6-007's P1 and P2
  are refuted. C038 still calls S102 a phenotype that "persists" and has not been reworded.
- **P3 is refuted on all three blend paths.** P4 fails for the circler at T 40, and for the ring
  under the bitwise criterion at both variants (#27). HR-009 adds that the class sequence near
  the circler end of each blend path reflects the observation horizon, not basin geography.
- **C041's resilience is mostly a trivial effect** (proposed, #27, accepted by HR-009). The cut
  removes one partner, and the other survives as any lone Orbium would.
- **L6-f's claim that every death comes after at least 500 tu** is a property of the sample: HR-009
  saw a death at 292 tu.
- **The I003 coupling verdict is INCONCLUSIVE** under HR-009's preregistered rule, with a narrower
  positive observation at s 0.2–0.3.

## Outstanding disagreements

| Topic | Lane 6 (#27) | Lane 7 (#30) | How it closes |
| --- | --- | --- | --- |
| What to replicate for S102 | the death at step 39 799 | the lifetime distribution, since the exact step depends on the engine | Lane 6 revision; L3-003 Q6 already targets the distribution |
| Blend paths (P3) | class interleaving | circler-end classes are horizon samples; only the Orbium→ring and dead zones read as geography | Lane 6 revision |
| I003 coupling | H1 at s 0.2–0.4 | real at s 0.2–0.3 only; s 0.4 explained by exposure; s ≥ 0.5 unbracketed; overall INCONCLUSIVE | Lane 6 revision |
| I001 split-half fragility | used to discount the s 0.08 rescue and to call I003 conservative | both readings hold, but the fragility belongs in the claim as a design limit | Lane 6 revision |

There is also an untested hypothesis from HR-009: the front-loaded hazard and the smaller gyradius
of long survivors suggest that S102 has a fragile and a longer-lived circling state. No
experiment addresses it yet.

## PR dependencies

| PR | State | Waits on | Unblocks |
| --- | --- | --- | --- |
| #27 L6-007/L6-008 results | open | Lane 6's targeted revisions per HR-009. Bobby reported a merge conflict, but a local merge into `main` `517f2b6` was clean when this was written | ledger entries for L6-f, L6-g, L6-c, L6-d; rewording of C038 and C041 |
| #30 HR-009 | open | Lane 7 finalizing the review and its test | the scoped wording for #27; the lifetime comparison row for #29 |
| #29 L3-003 | draft, running | its own runs, stopping at the preregistered horizons (5000 tu at R 13, 8000 tu at R 26) | independent evidence on the S102 transient; whether that transient survives numerical refinement |
| Exhibit "the creature that eventually disappears" | not started | HR-009 E1 data (#30); #29 for an independent check | a museum room |
| Exhibit "when together is worse" | not started | L6-008 (#27) as scoped by HR-009 E2 (#30) | a museum room |

#27 and #30 change different files and can merge in either order. #29 runs on its own clock and
does not block #27 or #30. The archivist does not ledger anything from #27, #29 or #30 until
those PRs land.

## Exhibits

- **Merged since the roadmap:** G004 "Same cut, two fates" (C041) and G005 "Two steps apart"
  (C040) in the gallery (#17); Figure C, phenotypes under one rule, restamped against `main`
  (#16, #24, #28); the five-room museum tour in `museum/site/` (#21); the gallery's C039
  correction (#26).
- **Note for the curators:** G004's caption and museum Room 4 present S101's survival under port
  injury as C041 does. Once #27 lands, the "obvious objection" (the unaffected partner)
  becomes the finding.
- **Next, both explicitly provisional:** the two exhibits in the table above. They show several
  trajectories and their spread, not one canonical death time.

## Decisions for Bobby

1. **#27 and #30:** once Lane 6 has revised, accept HR-009's recommended wording for L6-f, L6-g
   and L6-d (and L6-c as written)?
2. **C038 and C041:** should the archivist narrow them as soon as #27 and #30 merge, or wait for
   L3-003 (#29) to give independent support for S102 as a transient?
3. **Next bounded questions:** the research lanes propose them after reconciliation. Candidates
   from your list: whether S102 has distinguishable short-lived and long-lived regimes (which
   HR-009 already hints at), what mechanism drives the pair's frontal-mass vulnerability, and the
   basin boundaries between the nearby Orbium and static-ring attractors.
