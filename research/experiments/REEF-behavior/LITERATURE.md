# Catalog and literature check: contact-triggered expanding colony (behavior lane, 2026-10-21)

**Question (lead, D-018 item 4).** Is it already known that, at this rule, an expanding front leaves
a lattice of ring- or dumbbell-shaped bodies behind it? Is it known that a glider's contact with a
static ring triggers one?

**Bounded search, and its limits.** I searched the repository (claims ledger, dossiers, L6/HR reports).
I re-read Chan 2019 and Chan 2020 in full text with keyword search, and checked one 2026 Lenia
collision paper by its abstract. I looked up pattern-formation reviews by title and abstract only.
An unsuccessful search is not proof of novelty, and nothing here claims novelty.

Local copies for this check: Chan 2019 arXiv 1812.05433v3 (sha256 `05986383…`), Chan 2020 arXiv
2005.03742 (sha256 `7ab354ea…`), both downloaded from arxiv.org into this lane's scratch space.
`research/references.md` (Lane 0) already lists both as [Chan2019] and [Chan2020].

## What the pilots show (the thing being compared)

All six pilots P1–P6 follow the same sequence. Kernel-range interaction comes first, then contact
at t_c 6.1–6.8 tu, then glider and ring fuse. The fused mass grows, then breaks up from the inside
into small bodies, median 0.19–0.21 ΣA/R². The colony's edge advances at 0.31–0.37 R/tu, and the
whole 256² torus is covered by 50 tu. Behind the front the interior freezes. In P2 the mean |ΔA|
per tu within 4 R of the ring centre falls from 0.12 at 16 tu to 0.011 at 26 tu, while the body
count there levels off near 50. So the bodies are laid down and then stop changing; I saw no
evidence of discrete individuals dividing. That reading rests on two runs and the inner region
only (`audit/PILOT-AUDIT.md`).

## In-repository precedent (strongest)

| source | what it says | relation |
|---|---|---|
| `research/specimens/S103-static-ring.md`, perturbation table | I003 frontal addition (+x side): "0.10 returns to S103; ≥ 0.30 fills the world" | **Direct precedent.** S103 was already known to turn into a world-filling state when enough mass is added at its edge. A glider (0.49 ΣA/R², 1.3× the ring) arriving within kernel range is a large addition. |
| `research/reports/synthesis-2026-10-08.md` l. 30; `research/reports/hostile-review.md` l. 501 (HR-009, S102 at this same rule) | "Of 24 copies perturbed by 1e−12, 10 stop circling within 5000 tu: 9 die and 1 fills the world." | World-filling is a known end state of the coexistence rule (μ 0.155, σ 0.020, R13). |
| `research/experiments/L6-field/README.md` l. 95–116; claims ledger l. 1537–1558 | other catalog forms (`OG2r`, `O8?`, `1P4odl`) "fill the world" under their own rules | Filling is common across Lenia rules; these are not this rule. |

**Consequence.** That the coexistence rule has a space-filling state, and that S103 can be pushed
into it, was known before the expedition. The new observation is narrower and still OBSERVED: at
N256, R13, T10, every pilot geometry with contact (b/R ∈ {−1, 0, +1}, two snapshots) triggered it.

## Published Lenia literature

- **Chan 2019** (arXiv 1812.05433v3; Complex Systems 28(3), 2019, doi 10.25088/ComplexSystems.28.3.251).
  - §3.5.5 *Particle Reactions*, pdf p. 29, lists Orbium–Orbium collision outcomes, including
    "Detonation, the resultant mass explodes into infinite growth." This is the closest named
    precedent: a collision that turns into unbounded growth. But it is Orbium–Orbium, under
    unspecified rules, with no description of a lattice left behind.
  - §3.5.4 *Infinite Growth*, pdf p. 28: "Explosion or evaporation is the uncontrolled infinite
    growth, where the mass quickly expands or shrinks in all directions".
  - §3.3.1 *Landscapes*, pdf p. 21: "Class 2 (cyclic “savannah”) produces regional, periodic
    immobile patterns (e.g. Circium)". S103 is Circium-like, and the frozen lattice our front
    leaves behind looks like a regional immobile pattern. That supports the hypothesis that the
    coexistence rule sits where an immobile patterned state and the empty state are both stable,
    but it is an interpretation, not a test. Fig. 9's inset shows Circium's niche; the repository's
    S103 dossier already places the coexistence rule near it.
  - pdf p. 2: in original (single-kernel) Lenia, "self-replication that is yet to be discovered".
    Our colony does not show self-replication either (see above), so this does not make it a
    self-replicator.
- **Chan 2020** (arXiv 2005.03742, ALIFE 2020), pdf p. 6. In extended (multi-kernel/channel) Lenia,
  self-replication "kicks start a wave of autocatalysis and causes exponential growth. Reproducing
  solitons occupy all available space sooner or later." That is space filling by replication in
  *extended* rules; our rule is single-kernel and shows lattice laying rather than division. It
  resembles our result but is a different mechanism.
- **Gupta 2026**, *Collision-based logic in Lenia and its composition boundary*, arXiv 2609.01348
  (abstract only). It covers Orbium–Orbium collisions for logic gates. The abstract does not
  mention collisions with static bodies or unbounded growth, so it neither confirms nor
  contradicts this result.

## Pattern-formation analogues (by abstract; a mechanism to test, not a claim)

- **Pearson 1993**, *Complex Patterns in a Simple System*, Science 261:189–192 (1993), doi 10.1126/science.261.5118.189 (arXiv
  patt-sol/9304003). In the Gray–Scott model, patterns form in response to finite-amplitude
  perturbations; some spots grow and divide, filling the domain. **Shared:** a finite perturbation
  is needed (our empty background is stable, since the controls stay clean) and the spots end up
  filling space. **Different:** Pearson's spots replicate by dividing, while ours are laid down by
  an advancing front.
- **Knobloch 2015**, *Spatial localization in dissipative systems*, Annu. Rev. Condens. Matter
  Phys. 6:325–359 (doi 10.1146/annurev-conmatphys-031214-014514). When a homogeneous state and a
  periodic pattern are both stable, a localized patch of pattern is a bound pair of fronts. Inside
  a "pinning region" patches of many sizes persist; outside it the patch grows or shrinks.
  **Testable analogue:** S103 may be a pinned localized state of the immobile lattice, and the
  glider's mass may push the joint body past the size or amplitude at which the front depins and
  invades. Prediction: a passive mass-matched blob (X7/X8) above a threshold mass should ignite
  the same front. Below it, the ring should relax back to S103, as the 0.10 addition does in the
  dossier.
- **van Saarloos 2003**, *Front propagation into unstable states*, Phys. Rep. 386, 29 (2003), doi 10.1016/j.physrep.2003.08.001 (arXiv
  cond-mat/0308540). Fronts invading a linearly stable state are of the *pushed* type, with a speed
  set by the nonlinear front. Our invaded state (empty) is stable, so the 0.31–0.37 R/tu front
  should be pushed. Its speed should then not depend on the triggering geometry once the front has
  formed; the six pilots' front speeds agree within about ±9%, consistent with this, but untested.

## Verdict for the exhibit and the ledger

- The colony is **not** novel as a phenomenon class. World-filling at this rule (S102 HR-009),
  S103's fill under large frontal addition (S103 dossier), and collisional "detonation" (Chan 2019
  §3.5.5) are all prior.
- The observation that is new to this repository is that **glider contact reliably ignites S103
  into an expanding, freezing lattice** at the pilot geometries. It is OBSERVED, with numerical
  checks pending.
- Nicknames are not earned. Addendum after D-020: a static blob of the glider's mass placed in
  contact also ignites (X9, X10), and half that dose does not (X11). The precise statement is
  therefore "S103 plus enough mass in contact ignites (threshold between 0.24 and 0.37 ΣA/R² at this
  position; X12 at 0.75× ignites); a glider is one way to deliver it". That is the dossier's I003 result restated with a
  moving source.

## Provenance check (2026-10-21 ~07:20Z, at the lead's request)

Each citation was checked for existence against a primary index. Nothing was removed.

| citation | checked against | recorded |
|---|---|---|
| Gupta 2026 | https://arxiv.org/abs/2609.01348 and the arXiv API | "Collision-based logic in Lenia and its composition boundary", Chakshu Gupta, submitted 1 Sep 2026, arXiv:2609.01348v1 [cs.ET]. Cited from the abstract only. |
| Pearson 1993 | Crossref (doi 10.1126/science.261.5118.189) and https://arxiv.org/abs/patt-sol/9304003 | "Complex Patterns in a Simple System", John E. Pearson, Science 261:189–192, 9 Jul 1993; arXiv submitted 17 Apr 1993. Cited from the abstract. |
| Knobloch 2015 | Crossref (doi 10.1146/annurev-conmatphys-031214-014514); annualreviews.org returned 403 | "Spatial Localization in Dissipative Systems", E. Knobloch, Annu. Rev. Condens. Matter Phys. 6:325–359, 2015. Cited from the abstract. |
| van Saarloos 2003 | arXiv API, cond-mat/0308540 | "Front propagation into unstable states", Wim van Saarloos, journal-ref Phys. Rep. 386, 29 (2003), doi 10.1016/j.physrep.2003.08.001. Cited from the abstract. |
| Chan 2019, Chan 2020 | full-text PDFs from arxiv.org (sha256 above), quoted passages located by pdf page | already in `research/references.md` as [Chan2019] and [Chan2020] |
