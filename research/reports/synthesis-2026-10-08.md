# Synthesis, 2026-10-08

The periodic synthesis described in [`../roadmap.md`](../roadmap.md). Written at `main` `517f2b6`
(after PR #28) and refreshed at 03:50 UTC with the open-PR heads below. Statuses are the ledger's
([`../claims.md`](../claims.md)). Anything marked *proposed* is still in an open PR and has no
ledger status yet.

| Open PR | Head read |
| --- | --- |
| #27 L6-007/L6-008 | `e1f8760` |
| #29 L3-003 | `8c3c082` |
| #30 HR-009 | `c063d73` |
| #32 museum Room 6 | `c5527d6` |
| #33 Figure D | `8f1236e` |
| #34 gallery G006 | `32e0167` |

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

- **S102's lifetime belongs to R 13, T 10 (L3-003, PR #29, complete).**
  - At R 13, T 10, Lane 6's death step (39 799) and all 12 of Lane 6's noisy fates reproduce
    exactly. Of 24 copies perturbed by 1e−12, 10 stop circling within 5000 tu: 9 die and 1 fills the
    world. **TRANSIENT**, in agreement with Lane 7.
  - Refining either knob removes the collapse within the preregistered horizons. At R 26, 0 of 29
    runs end; at R 39, 0 of 3. At R 13 with T 20 and with T 40 (Q7, Amendment 2), 0 of 24 copies
    end in 8000 tu at each setting.
  - Every refined run is censored, so no refined setting is shown to be an attractor.
  - The exact match at R 13 shows that `alm_check` and `field.py` perform the same floating-point
    arithmetic (both are numpy `rfft2` steppers). It does not make the death step a property of the
    rule.
- **Attractor geography, L6-007 (PR #27, revised after HR-009).**
  - Orbium at the coexistence rule returns from noise up to ε 0.1 (18/18).
  - S103 returns bitwise up to ε 0.3 (24/24) at the primary rule.
  - S102 is a chaotic transient at R 13, T 10, not an attractor (P1 and P2 refuted). The step 39 799
    death is framed as one floating-point trajectory, and the transient claim is scoped to R 13, T 10
    after L3-003.
- **Pair coupling, L6-008 (PR #27).**
  - I004 port injury: H0 holds in 58/60 runs. C041's "fission" is the uninjured partner surviving.
  - I001 attenuation: H0 is not rejected. The split-half fragility is stated as a design limit.
  - I003 frontal mass: H1 by L6-008's own rule. The narrower reading after HR-009 is a drag-down at
    s 0.2–0.3 only. #27 now caveats this with L6-009, below.
- **The s 0.2 pair death is a 128² artifact (L6-009, Lane 6, independently confirmed in HR-009c,
  PR #30).**
  - A pulse aimed at the gap unbinds S101 into two intact Orbia. At 40 tu the world holds 0.868–0.873
    mass, two Orbia's worth.
  - On the 128² torus those two Orbia later collide and die (7 of 10 states dead at 300 tu). On a
    256² world all 10 end as two Orbia.
  - HR-009c withdraws E2's "coupling stands at s 0.2–0.3" for the on-gap pulse. E2's preregistered
    INCONCLUSIVE verdict is unchanged.
  - L6-009's own PR is not open yet. Its write-up is a caveat in #27's L6-008 README.
- **Chaos weakens under refinement (HR-009b, exploratory, PR #30).** Twin circlers separate at 0.20
  per tu at T 10, 0.096 at T 20, 0.077 at T 40 and about 0.01 at R 26. Chaos and collapse are
  separable: the refined circlers are still chaotic but have not collapsed. Whether weaker chaos
  causes the absence of collapse is untested.

## Refutations, narrowings and failed predictions

- **C039 is REFUTED as worded** (dispute D2, resolved in favour of C047). The narrower fact, that
  the bilinear seed dies, stands.
- **S102 is not an attractor at R 13, T 10, and its collapse does not survive refinement**
  (proposed, #27, #29, #30). C038 still calls S102 a phenotype that "persists" and has not been
  reworded.
- **S102's death time is not a rule-level property.** The step 39 799 death is one floating-point
  trajectory (HR-009 E1), and the finite lifetime itself is specific to R 13, T 10 (L3-003).
- **P3 is refuted on all three blend paths.** P4 fails for the circler at T 40, and for the ring
  under the bitwise criterion at both variants (#27). Classes near the circler end of each blend
  path reflect the observation horizon, not basin geography.
- **C041's resilience is mostly a trivial effect** (proposed, #27, accepted by HR-009). The cut
  removes one partner, and the other survives as any lone Orbium would.
- **The I003 "together is worse" result at s 0.2 is withdrawn** as a 128² collision artifact
  (L6-009, HR-009c). E2 stays INCONCLUSIVE.
- **L6-f's claim that every death comes after at least 500 tu** is a property of the sample. HR-009
  saw a death at 292 tu and L3-003 one at 164 tu.

## Outstanding disagreements

| Topic | Lane 6 (#27) | Lane 7 (#30) / Lane 3 (#29) | How it closes |
| --- | --- | --- | --- |
| What remains of I003 coupling (L6-d) | the on-gap s 0.3 deaths are world-dependent too; L6-009 narrows L6-d to placement-dependent, near-field effects at s 0.3 (off-gap drag-down in 4/5 phases on both world sizes) | HR-009c: all 10 on-gap s 0.2–0.3 states end as two Orbia on 256², so recommends "an on-gap pulse splits S101 into two intact Orbia; survival depends on the world, not on coupling". The off-gap effects are exploratory and not independently checked | L6-009's own PR, then a Lane 7 check of the off-gap drag-down |
| #27's headline | the PR title still reads "S101 drag-down at I003 s 0.2–0.3" | HR-009c withdraws the s 0.2–0.3 on-gap reading | Lane 6 retitles, or the ledger wording settles it |
| Why S102 collapses only at R 13, T 10 | not addressed | L3-003: the T 10 step is necessary at R 13, and R 26 shows the grid matters too; HR-009b: chaos weakens with refinement | a discriminating experiment, not yet proposed |

The earlier disagreements over the replication target (death step vs lifetime distribution), blend
paths, and I001 fragility are settled by #27's revision.

There is also an untested hypothesis from HR-009: the front-loaded hazard and the smaller gyradius
of long survivors suggest that S102 has a fragile and a longer-lived circling state. No experiment
addresses it yet.

## PR dependencies

| PR | State | Waits on | Unblocks |
| --- | --- | --- | --- |
| #27 L6-007/L6-008 | open, revised after HR-009 and L3-003 | Bobby's review; L6-009's own PR for the final L6-d wording | ledger entries for L6-f, L6-g, L6-c, L6-d; rewording of C038 and C041 |
| #29 L3-003 | open, complete | Bobby's review | the ledger's scoping of the S102 transient to R 13, T 10 |
| #30 HR-009 (with HR-009b, HR-009c) | open | Bobby's review | the scoped wording for #27 |
| L6-009 | no PR yet | Lane 6 | the final L6-d claim |
| #33 Figure D (provisional) | open | nothing for merge; redrawn when L6-009 and the ledger land | #32 |
| #32 museum Room 6 (provisional) | open | #33 merging first (it carries #33's figure) | — |
| #34 gallery G006 (provisional) | open | nothing for merge | — |

#27, #29 and #30 change different files and can merge in any order. The archivist does not ledger
anything from #27, #29, #30 or L6-009 until those PRs land.

## Exhibits

- **Merged since the roadmap:**
  - G004 "Same cut, two fates" (C041) and G005 "Two steps apart" (C040) in the gallery (#17);
  - Figure C, phenotypes under one rule, restamped against `main` (#16, #24, #28);
  - the five-room museum tour in `museum/site/` (#21);
  - the gallery's C039 correction (#26).
- **Open, all marked provisional:**
  - **Figure D (#33).** S101 under port injury and frontal addition, beside its lone partners. S102
    lifelines and a survival estimate. Red caveats on the figure for the 128² artifact and for
    R 13, T 10 only.
  - **Museum Room 6, "Still being argued" (#32).** Bobby's two exhibits, built on Figure D, plus
    Figure C in Room 4.
  - **Gallery G006, "the circler that eventually disappears" (#34).** Twelve 5000 tu circlers at
    R 13, T 10, five of which collapse.
- **Note for the curators:** the "when together is worse" story is now mostly a finite-world
  effect. Room 6's text and Figure D panel b predate HR-009c's withdrawal. Figure D draws the caveat,
  but Room 6 still presents the s 0.2–0.3 window as the case where only the pair dies. G004's
  caption and Room 4 still present S101's port-injury survival as C041 does.

## Decisions for Bobby

1. **#27, #29 and #30:** review and merge? The wording they now agree on is that S102 is a chaotic
   transient at R 13, T 10 that does not collapse at refined settings within the horizons tested,
   and that C041's resilience is the uninjured partner.
2. **Room 6 and Figure D before L6-009:** merge them as provisional now, with the caveat drawn, or
   hold them until the "together is worse" text is revised?
3. **C038 and C041:** with #29 complete, should the archivist narrow them as soon as #27, #29 and
   #30 merge?
4. **Next bounded questions:** the research lanes propose them after reconciliation. From your
   list, the S102 question has changed: rather than short-lived vs long-lived regimes at R 13, T 10,
   the sharper question is why collapse needs the T 10 step. The pair's frontal-mass
   "vulnerability" may reduce to the placement-dependent near-field effect in L6-009. The basin
   boundaries between Orbium and the static ring are untouched.
