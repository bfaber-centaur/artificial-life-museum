# L6-007: attractor geography of the coexistence rule (results)

Protocol: [`protocol.md`](protocol.md), pre-registered in commit `08f6ee5` before any run.
Runner: [`run.py`](run.py). Rule: μ 0.155, σ 0.020, R 13, T 10 (the S101–S103 coexistence rule),
plus two numerical variants, R 26 (σ 0.0205) and T 40 (σ 0.019).

    python research/experiments/L6-007-attractor-geography/run.py noise --variant primary|R26|T40
    python research/experiments/L6-007-attractor-geography/run.py paths
    python research/experiments/L6-007-attractor-geography/followup_circler.py   # exploratory

## Current interpretation (after HR-009, HR-009b and L3-003; all now on main)

This section governs. The pre-registered P1–P4 scoring below is unchanged, failed predictions
included. Older interpretive passages are kept and marked where they are superseded.

- **Divergence and collapse are different things.** Twin circlers that differ by 1e−12 diverge
  exponentially at R 13: about 0.20 per tu at T 10 (HR-009), slower at T 20 and T 40
  (0.08–0.10). At R 26 the divergence is slow (about 0.01 per tu) and decelerating, yet twins still
  decorrelate within about 3000 tu (HR-009b). So the circler's trajectory is chaotic at every
  setting tested. **Collapse** (the circler dying or filling the world) was observed only at
  **R 13, T 10**. L3-003 saw no collapse at R 13 with T 20 or T 40 (0 of 48 copies, to 8000 tu),
  at R 26 (0 of 29) or at R 39 (0 of 3), within the horizons tested.
- **What this README claims about S102** is limited to that: at R 13, T 10 the circler collapses
  after widely varying times, so there it is a transient, not an attractor. It does not claim
  the circler is a transient in the continuum rule or at other settings. It does not claim
  indefinite stability anywhere either, because every run at refined settings is censored.
- **The death at step 39 799** is one floating-point trajectory at R 13, T 10, not a
  characteristic lifetime. Independent engines reproduce it (L3-003) because they do the same
  arithmetic from the same start; a 1e−14 nudge moves it by thousands of tu (HR-009).

## Revision after hostile review HR-009 (PR #30) — partly superseded by the section above

Lane 7's HR-009 (preregistered, run on this PR's code at `3ccb804`) showed that twin circlers
differing by 1e−12 separate at about 0.2 per tu, and that death times at that tiny noise scatter
from 292 tu to beyond 5000 tu. I accept its findings. The pre-registered P1–P4 scoring below is
unchanged. What changes is the interpretation:

- The death at step 39 799 is **one floating-point trajectory**, not a lifetime of S102. Lane 6's
  two engines agree on it only because they do the same FFT arithmetic. The property of the rule
  is the lifetime *distribution*.
- Circler survival at a fixed horizon (Part A's circler rows, the R 26 circler row and the
  circler ends of Part B) is a draw from that distribution. It is not evidence of a basin.
- The claims at the end are rewritten to match (L6-f, L6-g and the replication target).

**Discretisation caveat (Lane 3, L3-003, PR #29, now merged).** An independent engine
reproduces step 39 799 and the transient at R 13, T 10. Lane 3's discriminating runs at μ 0.155,
σ 0.020 found **no deaths** in 0 of 48 copies at R 13 with T 20 or T 40 (to 8000 tu), and in 0 of 29
at R 26 (R 39: 0 of 3). So collapse was seen only in the **R 13, T 10 discretisation**. At
refined settings it was not observed within the horizons tested, which is not the same as
showing it never happens. Every S102 "transient" statement in this README (L6-f, the
lifetime follow-up, the circler rows of Part A and Part B) is scoped to R 13, T 10. At other
settings all runs are censored, so the circler is not shown to be an attractor there either. My
own T 40 variant (σ 0.019, not 0.020) did see circler deaths at noise ε ≥ 0.01. That is a different
σ and much larger noise, so it does not contradict Lane 3.

## Verdict

| Prediction | Result |
| --- | --- |
| P1: all ε ≤ 0.03 runs return at the primary rule (36/36) | **Refuted for the circler** (3/12). Holds for Orbium (12/12) and the ring (12/12, bitwise). |
| P2: no GLIDER/CIRCLER/STATIC run changes class between 1000 and 2000 tu | **Refuted.** 3 changes, all CIRCLER → DIED. Exploratory: the unperturbed circler dies at 3980 tu. |
| P3: at most 2 class changes along each blend path | **Refuted on all three paths** (4, 5 and 5 changes). |
| P4: each phenotype returns in ≥ 10/12 small-ε runs at R 26 and at T 40 | **Orbium passes both.** The circler passes at R 26 (12/12) and fails at T 40 (4/12). The ring fails both by the bitwise criterion (0/12), though it stays STATIC in every run. |

What this does to C038 ("one rule hosts three phenotypes"):

- **Orbium is an attractor** at this rule, by every test here: 18/18 return up to ε 0.1 at the
  primary rule, 12/12 at both variants, no late class change.
- **The S103 ring is an exact, robust fixed point at the primary rule**: every perturbed start up
  to ε 0.3 (24/24) relaxes back to the same binary state, bitwise. At R 26 and T 40 it is not one
  state but a family. Every perturbed start settles on its own distinct static body.
- **At R 13, T 10, the S102 circler is a transient, not an attractor.** Its trajectory is chaotic,
  and it collapses after widely varying times. At finer T or R no collapse was observed within
  the tested horizons (see "Current interpretation"). A 1% perturbation kills it in
  2 of 6 runs, and the unperturbed seed dies too in a longer exploratory run. HR-009 shows that
  even a 1e−14 perturbation changes when it dies, so lifetimes are spread widely (292 tu to more
  than 5000 tu over 37 starts pooled by Lane 7). C038 should be narrowed: at R 13, T 10 the
  circler is a long transient, not a third stable phenotype. At refined settings its status is
  open.

## Part A: noise around each seed

6 noise realisations per ε, uniform noise of amplitude ε on the seed's support dilated by 3 R/13
cells. "Ret" counts returns by the pre-registered signature test: same class, and mass and
gyradius within 1% and path speed within 2% of the unperturbed run. For the ring, the test is
bitwise equality up to a periodic shift. "Class" counts runs that end in the seed's class.
Classes are taken at 2000 tu (primary) or 1000 tu (variants).

| Seed | ε | primary ret / class | R 26 ret / class | T 40 ret / class |
| --- | --- | --- | --- | --- |
| Orbium | 0.01 | 6 / 6 | 6 / 6 | 6 / 6 |
| | 0.03 | 6 / 6 | 6 / 6 | 6 / 6 |
| | 0.1 | 6 / 6 | 5 / 5 (1 died) | 5 / 5 (1 died) |
| | 0.3 | 0 (6 died) | 0 (6 died) | 0 (5 died, 1 static) |
| circler | 0.01 | 1 / 4 (2 died) | 6 / 6 | 3 / 3 (2 died, 1 static) |
| | 0.03 | 2 / 4 (2 died) | 6 / 6 | 1 / 1 (4 died, 1 filled) |
| | 0.1 | 1 / 5 (1 died) | 6 / 6 | 4 / 4 (1 died, 1 filled) |
| | 0.3 | 0 (6 died) | 3 / 3 (2 died, 1 filled) | 0 (4 died, 2 static) |
| ring | 0.01–0.3 | 24 / 24 | 0 / 24 | 0 / 23 (1 died at ε 0.1) |

**Circler at the primary rule.** Of the 13 non-returns at ε ≤ 0.1, 5 died and 8 are still
circlers. Those 8 match the reference mass to within 0.15% and path speed to within 0.25%, but
their gyradius is 1.0–2.4% smaller, so the 1% gate fails them. I have not resolved whether that is
a slightly different circling body or a sampling artefact. The mass oscillates with an 8.9-step
period and the shape is sampled every 50 steps. The pre-registered gate stands either way, and the
deaths alone refute P1. All 5 deaths are *late*: each run was still a circler at 500 tu
(2 of them also at 1000 tu). *After HR-009:* the likeliest reading of the gyradius gap is
sampling different points of a chaotic orbit, and a 1% gate is too tight for a chaotic state.
"Every death comes after at least 500 tu" is true of this sample only. Lane 7 saw a death at
292 tu.

**Exploratory follow-up** (not pre-registered; [`followup_circler.py`](followup_circler.py),
[`circler-lifetimes.csv`](circler-lifetimes.csv)). **The registered S102 seed itself dies, at t = 3979.9 tu.**
Of the 12 perturbed starts, 4 die at 933.7, 977.6, 988.8 and 1291.0 tu (the same 4 that died in
Part A), and 8 are still circlers at 5000 tu (mass 0.5221–0.5232). So at R 13, T 10 the circler
is a long-lived state with a broad, start-dependent lifetime, not a stable one. The 2000 tu horizon of Part A,
and Night 0's 20 000-step runs, were too short to see the reference die. The project engine
`alm.lenia.Lenia` (single world, `specimens.load("S102").place(128)`) gives the same death step,
39 799. That is a second engine within Lane 6, not an independent replication. *After HR-009:*
the agreement is expected because both engines do the same pocketfft arithmetic. An engine with
a different FFT library or precision should not be expected to reproduce step 39 799. These 13
lifetimes are a sample, and the 8 survivors at 5000 tu are censored.

**Ring at R 26 and T 40.** It stays STATIC in 47 of 48 runs, but 0 match the unperturbed final
state, and all 49 STATIC finals (references included) are distinct from each other up to shift.
At R 26 the seed is the bilinear enlargement of S103, so it is not binary, and the finals hold
257–262 cells above 0.5. At T 40 the rule has σ 0.019, where S103 is not an exact fixed point;
there the finals have 60–63 such cells. So away from the primary settings the ring is a robust
*class* landing on a family of nearby static bodies, not a single attractor. The bitwise criterion
was written for the primary rule, where it holds. I report the P4 failure as pre-registered
rather than re-scoring it.

**Circler at R 26 vs T 40.** At R 26 the circler is *more* robust than at the primary rule
(18/18 return up to ε 0.1). At T 40 it is fragile, and it can turn static or fill the world. By
P4's rule it is NUMERICALLY_FRAGILE at T 40. Caveat: the R 26 seed is the bilinear enlargement,
which Night-1 D2 showed kills the circler at σ 0.020. At σ 0.0205 it survives, so the R 26 row
also depends on the σ offset. *After HR-009:* the R 26 horizon is 1000 tu, and half of the
circler deaths at the primary rule come later than that. So 18/18 at R 26 is weak evidence of
greater robustness, not evidence of an attractor at R 26.

## Part B: blends between seeds (primary rule, 2000 tu)

Start = (1 − λ)·A + λ·B, both seeds centred, λ = 0, 0.05, …, 1 ([`paths.csv`](paths.csv),
[`finals-paths.npz`](finals-paths.npz)). Final classes:

| λ | 0 | .05 | .10 | .15 | .20 | .25–.35 | .40–.50 | .55 | .60–.85 | .90 | .95 | 1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Orbium → circler | G | G | D | D | D | D | D | D | D | C | D | C |
| circler → ring | C | **D**¹ | C | C | D | D | F | S | S | S | S | S |
| Orbium → ring | G | G | G | D | S | D | D | F | S | S | S | S |

G glider, C circler, S static, D died, F filled. ¹ circler at 1000 tu, died before 2000 tu.

- No blend switches directly between two phenotypes. Between Orbium and the circler lies a wide
  dead zone (λ 0.10–0.85), and the circler's basin along this path is tiny and broken
  (λ 0.90 survives, 0.95 dies).
- Every path interleaves by the pre-registered count, so P3 is refuted. The classes show an
  isolated static body at λ 0.20 on Orbium → ring, and circler survival broken by deaths near
  both circler ends.
- *Narrowed after HR-009:* every class here is the state at 2000 tu, which is finite-horizon
  survival, not basin geography. Near the circler ends (circler → ring λ 0.05, Orbium → circler
  λ 0.90–1) the classes are draws from the circler's lifetime distribution, and a rerun on
  another machine could flip them. The interleaving that does not depend on the circler is on
  the Orbium → ring path: the dead zones, the filled point and the static island at λ 0.20.
  Their end states are absorbing (Orbium and the ring are attractors here, and death is final).
  Whether the λ assignments are sensitive to rounding was not checked in this experiment.
- The ring has the widest basin along both paths that reach it (λ ≥ 0.55–0.60). Orbium's reaches
  λ 0.05–0.10, and the circler's is no wider than one or two grid points.

## Failed and inconclusive

- P1, P2 and P3 are refuted at the primary rule, and P4 for the circler at T 40 and for the ring at
  both variants (bitwise criterion).
- Unresolved: whether the 8 surviving circlers with a 1–2.4% smaller gyradius are a distinct
  body or chaotic-orbit sampling (HR-009 favours sampling, untested).
- Numerical qualifications that stay attached to every claim here: the R 26 variant uses
  bilinear-enlarged seeds (the method that killed the circler at σ 0.020 in D2) and a shifted
  σ (0.0205). T 40 uses σ 0.019. All runs are float64 on a 128² (256² at R 26) torus with
  pocketfft.
- Not tested: other μ, σ in the coexistence band; noise outside the seed's support; larger
  worlds; horizons beyond 2000 tu for Orbium and the ring (only the circler was followed to
  5000 tu). Whether Orbium or the ring also decay on longer horizons is open.

## Claims proposed (for the archivist)

- **L6-e.** At the coexistence rule (R 13, T 10), Orbium returns from 18/18 noise perturbations
  up to ε 0.1, and S103 returns bitwise from 24/24 up to ε 0.3. Both are attractors in this
  test.
- **L6-f** (scoped to **R 13, T 10**). Observation: at μ 0.155, σ 0.020, R 13, T 10, 128², 1%
  noise kills S102 in 2/6 runs within 2000 tu, and the circler's lifetime from tiny-noise starts
  ranges from 292 tu to beyond 5000 tu (HR-009, L3-003). The unperturbed seed's death at step
  39 799 is one floating-point trajectory, not a characteristic lifetime. Interpretation: at this
  setting S102 is a transient, not an attractor. Separately, its trajectory diverges
  from a 1e−12 twin at every setting tested (HR-009b): exponentially at R 13 (0.08–0.20 per tu
  across T), slowly and decelerating at R 26 (about 0.01 per tu), with twins still decorrelating
  within about 3000 tu. That divergence is not
  collapse. No collapse was observed at R 13 with T 20 or T 40 (0/48), or at R 26 (0/29) or R 39
  (0/3), within 5000–8000 tu (L3-003). So neither "transient" nor "stable" is claimed at those
  settings.
- **L6-g** (narrowed). Blends between the three seeds never switch directly between phenotypes
  within 2000 tu. On the Orbium → ring path the classes interleave (dead zones, a filled point
  and a static island at λ 0.20). Classes near the circler ends are horizon samples of a chaotic
  transient, not basin geography.
- **Replication (done, L3-003, merged):** Lane 3 measured the lifetime distribution, as
  proposed, rather than matching step 39 799. It replicated the R 13, T 10 collapse and found
  none at refined settings.
