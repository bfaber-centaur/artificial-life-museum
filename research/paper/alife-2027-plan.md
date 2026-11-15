# Research plan: an ALIFE 2027 paper

Drafted 2026-11-15 for Bobby's choice of "museum plus one research thread". This is a plan, not
a claims source: nothing here changes a status in `claims.md`. Every experiment below gets its
own pre-registered `protocol.md`, committed before its first run, as in L6-009.

**Venue.** ALIFE 2027, Prague, July 19–23 2027 (General Chair Jitka Čejková; site
alife.vscht.cz). No call for papers yet. Past ALIFE deadlines fell in March–April, so this plan
works to an **internal submission-ready date of 1 March 2027**. From memory: ALIFE takes full
papers (about 8 pages) and short abstracts. We aim for a full paper.

## 1. Where we stand

Our population-level results so far, all on main:

| Result | What it says |
| --- | --- |
| C099–C101 (soup) | One mutant's first trial predicts nothing (Spearman 0.07). Genomes do differ (perm p 0.006), but **where a mutant lands matters about twice as much as what it is**. |
| C116–C118 (soup) | A **neutral marker** at the same 72 places grows in 31/72, against 37/72 for mutants. Against neutral, differences between genomes are not significant (p 0.065). |
| C090, C110–C111 (GenomeLenia) | Starting from **many cells**, selection clearly wins: mean genome 0.1 → 0.65–0.69, against 0.31–0.35 for a neutral marker, and it levels off near 0.7 from both sides. |
| C119–C124 (therapy toy) | Adaptive dosing did not beat constant dosing, because the resistant remnant never regrew. |

The soup and GenomeLenia results fit together. With **one** mutant, luck dominates; with a
**population** and many generations, selection wins. Population genetics has a precise theory of
where that switch happens. Nobody has asked whether Lenia obeys it.

## 2. Candidate central questions

| | Question | Builds on | Novelty (vs. survey) | Risk |
| --- | --- | --- | --- | --- |
| **A (recommended)** | **When does selection beat luck in Lenia?** Measure effective population size *Nₑ* and selection coefficient *s* for emergent, self-replicating Lenia cells, and test whether Kimura's fixation formula predicts which mutants take over. | Soup neutral (C116), GenomeLenia (C090, C110), Moran check (C112), family-tree tracker (C072) | High. No Lenia paper in the survey measures drift, *Nₑ* or fixation (gap 1 and 5). Digital-organism work (Avida) has tested fixation, but with coded individuals. Here individuality and reproduction are **emergent**. | Medium. Needs births and deaths at carrying capacity (gate E0). |
| B | **Which of Chan's fixes stops fast-expander takeover?** Add resource cost, mass conservation and patchy environments one at a time and measure diversity. | Soup (C076–C078), Chan 2023 | Medium. Flow-Lenia (Plantec 2023/2025) is already mass-conserving, so part of this is done. | Low–medium. A likely outcome is "resource cost helps", which is expected. |
| C | **Does a Lenia world have a carrying capacity and predator–prey cycles?** Census, logistic fits, a resource channel, a predator search. | Reef tracker, replicators | High (gaps 1, 2, 4), but predation has to be found first. | High. There is no predator yet. |
| D | **Can adaptive therapy work in Lenia?** Add regrowth of the resistant remnant and retest. | C119–C124 | Medium. It is a toy model of a known oncology idea. | Medium. The result depends heavily on the regrowth rule we choose. |

**Why A.** It turns our two honest nulls into data points rather than dead ends. C116 and C120
become "the low-*Nₑs* regime" in one curve. It has a sharp, falsifiable prediction from
textbook theory (Kimura 1962; the Moran process we already reproduced in C112), and either
outcome is publishable. "Population genetics holds for emergent individuals" is a clean positive
result. "It breaks, and here is why (fusion, correlated births, spatial clumping)" is a more
interesting one. B, C and D can each be a section or a follow-up paper, not the spine.

The rest of this plan assumes **A**. If Bobby picks another, sections 3–5 are rewritten before
any run.

## 3. Experiments for question A

The system is GenomeLenia (`REPLICATORS/genome.py`): cells of *division well* (g 0) to
*division uncontrolled* (g 1), with a per-pixel genome carried by matter. An "individual" is a
cell found by the peak tracker (`tree.py`). A neutral marker is a second tag field carried by
matter exactly like *g*, with no effect on the rule (as in C110's neutral control).

| ID | Experiment | Pre-registered prediction | What would falsify it |
| --- | --- | --- | --- |
| **E0** (gate) | **Census and turnover.** Count cells over time in 128², 256², 384² tori from one cell to full. Measure carrying capacity *K* and the birth and death rate at *K*. | *K* grows in proportion to world area (within 15%). At *K*, at least 5% of cells are replaced per 1000 tu. | No turnover at *K*: the world freezes and there is no drift to measure. **Fallback:** add a random dilution (cull a random cell at a fixed rate, like serial transfer in microbial evolution) and say so in the paper. |
| **E1** | **Neutral drift and *Nₑ*.** Tag a fraction *p₀* ∈ {0.1, 0.5} of cells at *K*; follow the tag frequency. Estimate *Nₑ* from Var(Δ*p*) = *p*(1−*p*)/*Nₑ* per generation. | Var(Δ*p*) scales with *p*(1−*p*). *Nₑ* is the same at both *p₀* within a factor of 1.5, lies between 0.2*K* and 2*K*, and doubles (±30%) when world area doubles. A single tagged cell fixes with probability 1/*N* (within 95% binomial CI). | *Nₑ* depends on *p₀*, or a single neutral cell's fixation chance is far from 1/*N*. |
| **E2** | **Selection coefficient.** Head-to-head 50/50 mixtures of genome *g* vs *g*+δ (δ ∈ {0.02, 0.05, 0.1}, *g* ∈ {0.2, 0.4, 0.6, 0.7}), no mutation. *s* is the slope of logit frequency per generation. | *s* > 0 for *g* ≤ 0.6, increasing with δ. *s* is indistinguishable from 0 near *g* 0.7 (the C111 resting point). | *s* has no consistent sign below 0.6, which would contradict C090/C110. |
| **E3** (core) | **Fixation test.** Introduce **one** mutant cell (δ from E2) into a resident population at *K*. Run enough replicates per condition to resolve the fixation probability (estimated 200–1000; most mutants are lost early, so most runs are short). Use 5 conditions spanning *Nₑs* ≈ 0.1 to 10. | In at least 4 of 5 conditions, the observed fixation probability lies inside the 95% CI of Kimura's *u* = (1−e⁻²ˢ)/(1−e⁻²ᴺᵉˢ), using *Nₑ* and *s* measured independently in E1/E2. For *Nₑs* < 0.5, fixation is indistinguishable from neutral 1/*N*. | Two or more conditions fall outside. That is a finding too: we then test which emergent feature breaks the theory (fusion of cells, sister cells dividing in step, spatial clumping). |
| **E4** | **Does world shape matter?** Repeat E3 at one *Nₑs* ≈ 2 on a square torus, a long thin strip of the same area, and a world with barriers. Evolutionary graph theory's isothermal result (Lieberman, Hauert & Nowak 2005, from memory) says regular structure leaves the fixation probability unchanged. | Fixation probability differs by less than the CI across the three shapes, while mean time to fixation is longer on the strip. | Shape changes the fixation probability, i.e. Lenia space acts like an amplifier or suppressor of selection. |
| **E5** | **Bridge back to the soup.** Estimate *Nₑ* and *s* for the soup's single-mutant setting (C099, C116). | The soup sits at *Nₑs* < 1, which is why C116 found luck ≈ mutants. | The soup's *Nₑs* is large, so its null needs another explanation. |

**Rigor steps, as for every lane.**

- Each E gets `protocol.md` committed before its first run, with analysis code fixed in advance.
  Changes go under "Amendments".
- The tracker is validated against hand-counted frames before E0 counts are used.
- Numerics: E3's main condition is rerun at dt/2 and on a second grid size. Any conclusion that
  flips is marked NUMERICALLY_FRAGILE.
- A hostile reviewer (Lane 7 style) reads each result before it is ledgered. Claims enter
  `claims.md` only after their PR merges, as append-only history lines.
- E1 and E3 are rerun with an independent implementation of the neutral tag and the fixation
  bookkeeping, so the core claim can reach INDEPENDENTLY_CHECKED.

## 4. Compute budget

These numbers come from `environment-limits` (REEF-M0): about 200–340 world-steps/s at 256²
per process, with 2 processes in parallel. N512 is about 4.5× slower. A *division well*
generation is about 140 tu (C072: 14 generations in 2000 tu).

- At *K* ≈ 80 cells, a neutral fixation takes on the order of *N* generations, about 10⁴ tu.
  At 256² that is about 6 minutes per fixed run.
- E3 needs about 5 × 500 replicates, but most mutants are lost within a few generations. Our
  rough estimate is 1–2 days of wall time per condition at 128²–256², run in background
  sessions.
- E0–E2 together are under a day.

Small worlds (128²) carry the replicate counts; 256²/384² check that the result scales.

## 5. Timeline to 1 March 2027

| Weeks | Dates | Work |
| --- | --- | --- |
| 1 | Nov 16–22 | Bobby picks the question. Write E0–E2 protocols. Build the census and validate the tracker. **E0 gate.** |
| 2–3 | Nov 23–Dec 6 | E1 (*Nₑ*), E2 (*s*). First hostile review. |
| 4–6 | Dec 7–27 | E3 protocol, then the fixation runs. |
| 7–8 | Dec 28–Jan 10 | E4 world shapes, E5 soup bridge. |
| 9–10 | Jan 11–24 | Independent reimplementation, numerics checks, ledger intake. |
| 11–13 | Jan 25–Feb 14 | Write the paper (8 pages), make the figures, release code and data. |
| 14–15 | Feb 15–Mar 1 | Hostile review of the manuscript, revise, buffer. |

If the official deadline lands later, the buffer goes to a second system (Flow-Lenia soup) for
generality, not to more polishing.

**Decision points for Bobby.** (1) The central question, now. (2) After E0, whether a
dilution fallback is acceptable. (3) After E3, whether the story is "theory holds" or "theory
breaks", which sets the paper's title.

## 6. Novelty check and what to read next

From the 2026-11 survey (`lenia-research-survey-2026-11.md`), all at abstract grade:

- **Chan 2023** (GECCO, arXiv 2304.05639) and **Plantec et al. 2023/2025** (Flow-Lenia) study
  evolution in Lenia through takeover and evolutionary-activity metrics. Neither abstract
  mentions neutral controls, *Nₑ* or fixation probabilities.
- **Faldor & Cully 2024** and **Lorantos & Spector 2025** evolve Lenia with an outside
  algorithm, so there is no in-world population to do genetics on.
- **Michel et al. 2025** search Flow-Lenia for ecosystem-level dynamics, but not drift.

**Before writing**, these need a full-text check, since an abstract can miss a drift control:
Chan 2023, Plantec 2025, MaCE 2025 and Suzuki et al. 2023 (MIT Press returned 403 to us). We
also need the digital-evolution precedent: Avida fixation and drift studies, and Lenski's
neutral Ara± markers. The paper should present itself as **the first test of fixation theory
with emergent individuals in a continuous CA**, not as the first test in digital life.

## 7. Risks

- **No turnover at *K*** (E0). The fallback is dilution, which is standard in experimental
  evolution but weakens "fully emergent".
- **Counting individuals is ambiguous** when cells fuse or fade. Fusion and fading go in the
  paper as events, with rates, not hidden in the tracker.
- **Generation time varies with genome**, so *s* per generation and *s* per tu differ. Both are
  reported, and Kimura is tested with the per-generation value.
- **Small effect at feasible *N***. If *K* is only tens of cells, *Nₑs* > 10 may need δ large
  enough to leave the linear range. In that case E3's range is cut to 0.1–5 and the paper says
  so.
