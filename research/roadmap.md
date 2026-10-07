# ALM roadmap: the standing program

From Night 1 (mandate of 2026-10-07) the Artificial Life Museum is a continuing project rather
than a one-night experiment. This file says what the program is for, who leads what, and what
each expedition tests first. It is a map, not a protocol: each lane writes and owns its own
preregistration, and this file links to it once it lands.

**Mission.** Understand the dynamics of classic 2-D Lenia organisms through reproducible
experiments, independent criticism and accessible exhibits. Grow a delightful, navigable museum
without sacrificing evidential discipline.

The unit of progress is unchanged from the [charter](charter.md): specimen + reproducible claim +
intervention + evidence. Success is measured in defensible understanding and the quality of the
experience built around it, not in PR count, parameter combinations or agent-hours.

## Where Night 0 left us

These are the starting facts each expedition builds on. Statuses are the ledger's, as of `main`
at `f72db9e`; [`claims.md`](claims.md) wins wherever this summary disagrees.

- **S001** (Orbium, poly/poly, μ 0.15, σ 0.015, R 13, T 10) glides stably and is replicated
  bitwise by two independent implementations (C001). Several of its apparent traits are lattice
  effects: the mass wobble vanishes with resolution (C003), the heading locks to grid directions
  (C011, C013), and the axis-travel "breathing" is absent at R 26 (C025). Its speed and survival
  edges depend on T (C009, C027).
- **Survival edges.** S001 has sharp, all-or-nothing kill edges for four standardized disturbances,
  independently checked (C023). Where mass is removed matters more than how much (C026).
- **Field specimens** (Lane 6, PR #11, merged 2026-10-07): at μ 0.155, σ 0.020 one rule supports a
  glider, a circler S102 and a static ring S103, chosen by history (C038). The coexistence holds at
  every numerical setting tried, but its σ band moves with T and R, and S102 dies at R 26 at its
  registered rule (C039). Under S001's own rule a bound pair S101 survives port injury by shedding
  to one Orbium (C041). All three are catalogued species, not new forms (C043).
- **Single-lane.** C038 and C040–C045 have not yet been reproduced by a second lane. They are the
  evidence the first two expeditions start from, so they are treated as provisional until that
  happens.

## Standing lanes

| Lane | Role | Night 1 posture |
| --- | --- | --- |
| 0 | Claims archivist | Ledgers every proposed claim; literature provenance (PR #15, open) |
| 1 | Reference naturalist | Numerical ecology, with the archivist on literature |
| 2 | Simulation & instrumentation | Idle unless an expedition needs a simulator change |
| 3 | Independent replication / numerical red team | Leads numerical ecology; replicates the attractor result |
| 4 | Disturbance laboratory | Supplies independent-organism baselines for pair dynamics |
| 5 | Morphometrics / behavior | Idle unless asked |
| 6 | Field exploration | Leads attractor geography and pair dynamics |
| 7 | Hostile reviewer | Reviews attractor geography and pair dynamics as work lands |
| 8 | Gallery (standing) | Specimen exhibits; visual conventions with Lanes 9 and 10 |
| 9 | Scientific illustrator (standing) | The attractor-geography figure; shared figure conventions |
| 10 | **Exhibition designer (new)** | The public museum |

The coordinator dispatches work and keeps this file current. It does not implement. Lanes with
nothing to do stay idle.

## Expedition 1 (primary): attractor geography

**Question.** Around the coexistence rule where S001's glider, the circler S102 and the static
ring S103 all persist, which starting conditions lead to which form, and is each form a genuine
attractor or only something that has not died yet?

**Lead:** Lane 6. **Replication:** Lane 3 (independent implementation). **Review:** Lane 7.
**Figure:** Lane 9.

**Scope, as mandated:**

- Map initial-condition sensitivity at fixed rules.
- Characterize persistence, transitions, collapse and numerical dependence (R, T, grid).
- Distinguish attractor evidence from finite-horizon survival.
- Seek independent replication of the strongest result.
- Publish data, scripts, claims and a clear scientific figure.

**First bounded test (question level).** At fixed rule (μ 0.155, σ 0.020), for a preregistered,
bounded family of starting states, which of the three forms does each start reach, and does that
answer stay the same when the observation horizon is extended and when one numerical setting
(R or T) is refined? Lane 6 fixes the family, horizons, classifier and stopping rule in its
preregistration before running.

**Preregistration:** _pending (Lane 6)._ Link added here when it lands.

**What would count.** A basin statement that holds at a longer horizon and a refined numerical
setting, reproduced by Lane 3 in a distinct implementation, survives Lane 7's review and is drawn
by Lane 9 from committed data. A result that holds only at one horizon or one setting is recorded
as finite-horizon or numerically fragile, not as an attractor.

## Expedition 2 (secondary): pair dynamics

**Question.** When the bound pair S101 survives an injury, is that because the two partners are
coupled, or simply because the uninjured partner was never affected?

**Lead:** Lane 6. **Baselines:** Lane 4 (independent-organism controls). **Review:** Lane 7.

**Scope, as mandated:** investigate S101 binding and injury response, include useful
independent-organism baselines, keep it bounded, and prefer decisive comparisons over broad
sweeps. C041 already names the trivial baseline: the port cut mostly removes one partner.

**First bounded test (question level).** Under the same injuries, does the injured partner (and
the uninjured one) fare differently when bound in S101 than when it is a lone Orbium given the
same edit? Lane 4 supplies the lone-organism arms with its standardized disturbances; Lane 6
supplies the pair arms. Lane 6 and Lane 4 fix the comparison, arms and outcome in their
preregistrations before running.

**Preregistrations:** _pending (Lane 6, Lane 4)._ Links added here when they land.

**What would count.** A difference between the bound and lone arms that exceeds the variation
across phases, with the "unaffected partner" explanation explicitly tested. No difference is a
result too and is recorded as one.

## Expedition 3: numerical ecology

**Question.** Which observed organism properties persist when resolution and timestep change,
and which belong to a particular discretization?

**Lead:** Lane 3. **With:** Lane 1 (reference naturalist) and the claims archivist (literature).

**Scope, as mandated:** finite-resolution behaviors are legitimate observations of the system
actually simulated, and stay in the record as such. They are not to be mistaken for
continuum-invariant properties. Night 0 already has several worked examples (C003, C009, C011,
C013, C025, C027, C039).

**First bounded test (question level).** For the properties already in the ledger for S001 and
S101–S103, which hold under a preregistered refinement in R and in T, which shift but persist,
and which vanish? The answer is an inventory that classifies each property, rather than a new
sweep. Lane 3 fixes the properties, refinements and tolerances in its preregistration; Lane 1 and
the archivist say where prior literature reports the same property.

**Preregistration:** _pending (Lane 3)._ Link added here when it lands.

**What would count.** Each listed property carries an explicit verdict (invariant within
tolerance, shifted, or discretization-specific) backed by runs at both settings, and the ledger
statuses are updated by the archivist accordingly.

## Public museum: Lane 10, exhibition designer

**Goal.** A small, static, browsable museum built from the existing specimen dossiers,
photographs, figures and claims. It favors one compelling first visitor journey over a large
application.

**Works with:** Lane 8 (gallery) and Lane 9 (figures) on visual conventions
([`figures/conventions.json`](figures/conventions.json) is the shared source). Lane 10 does not
re-simulate or redraw evidence: it arranges and explains what Lanes 8 and 9 produce.

**Rules.**

- Every exhibit links back to its scientific sources: claim IDs in `claims.md`, run IDs or
  manifests, and the dossier, figure or gallery entry it draws on.
- Statuses shown to visitors are the ledger's. An exhibit never states more certainty than the
  claim it cites, and provisional or single-lane results are labelled as such.
- Static output only: no server, job system or UI framework beyond what a static page needs.

**First milestone.** A visitor can enter the museum, follow one guided path through the existing
material (for example: meet Orbium, see which of its traits are the grid rather than the
creature, see where it breaks, then meet the three forms that share one rule), and reach the
evidence behind every exhibit in one click. Lane 10 proposes the path, location in the repository
and build command in its first PR.

## Periodic synthesis

A short synthesis, owned by the coordinator and delegated to a writing thread, at least once per
working session. It has five sections, each a few lines:

1. **New evidence:** claims added or upgraded, with IDs.
2. **Refutations:** claims refuted, narrowed or found numerically fragile, and failed or
   inconclusive experiments.
3. **Exhibits:** what was added to the gallery, figures or museum.
4. **Blockers:** what is stuck, and on whom.
5. **Next decisions:** what Bobby is being asked to decide.

Default location: `research/reports/synthesis-YYYY-MM-DD.md`.

## Operating discipline

- Preserve the existing lanes and source-of-truth conventions: `claims.md` for claims and
  statuses, specimen dossiers for specimens, `research/experiments/` for manifests and
  preregistrations, `research/gallery/` and `research/figures/` for exhibits and figures.
- Bounded tasks, independent PRs, explicit dependencies. Each mandate says what it waits on.
- Settled decisions stay settled unless new evidence reveals a defect. Settled so far: the S001
  rule definition; `INDEPENDENTLY_CHECKED` means two distinct implementations agree; dispute D1
  (heading lock at R 26) resolved in favour of C013; S101–S103 are catalogued species (C043).
- Review and reconcile evidence before upgrading a claim. The archivist changes statuses only on
  recorded evidence and appends history rather than rewriting it.
- Nothing merges automatically, neither scientific claims nor PRs. Bobby merges.
- Failed and inconclusive experiments are recorded, in the experiment directory and the ledger.
- Useful artifacts live in the repository, not only in chat.
- Idle lanes stay idle.

## Dependencies at a glance

| Work | Waits on |
| --- | --- |
| Attractor geography runs | Lane 6 preregistration |
| Attractor replication (Lane 3) | Lane 6's strongest result |
| Attractor review (Lane 7) | Lane 6 preregistration, then results |
| Attractor figure (Lane 9) | Lane 6 data committed; Lane 3 replication for the final version |
| Pair dynamics comparison | Lane 6 and Lane 4 preregistrations |
| Numerical ecology inventory | Lane 3 preregistration |
| Museum first milestone | existing gallery (G001–G003) and Figure A on `main`; picks up later exhibits as they merge |
| Ledger updates | each lane's proposed claims |

## Preregistrations index

| Expedition | Lane | Preregistration |
| --- | --- | --- |
| Attractor geography | 6 | pending |
| Pair dynamics | 6 | pending |
| Pair dynamics baselines | 4 | pending |
| Numerical ecology | 3 | pending |
