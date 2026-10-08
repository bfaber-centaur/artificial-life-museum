# L6-007: attractor geography of the coexistence rule (results)

Protocol: [`protocol.md`](protocol.md), pre-registered in commit `08f6ee5` before any run.
Runner: [`run.py`](run.py). Rule: μ 0.155, σ 0.020, R 13, T 10 (the S101–S103 coexistence rule),
plus two numerical variants, R 26 (σ 0.0205) and T 40 (σ 0.019).

    python research/experiments/L6-007-attractor-geography/run.py noise --variant primary|R26|T40
    python research/experiments/L6-007-attractor-geography/run.py paths
    python research/experiments/L6-007-attractor-geography/followup_circler.py   # exploratory

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
- **The S102 circler is a finite-horizon survivor, not an attractor.** A 1% perturbation kills
  it in 2 of 6 runs after more than 900 tu of circling, and in the exploratory follow-up the
  unperturbed registered seed itself dies at 3980 tu. C038 should be narrowed: under this rule the
  circler is a long transient (lifetimes from about 900 to more than 5000 tu), not a third stable
  phenotype.

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
(2 of them also at 1000 tu).

**Exploratory follow-up** (not pre-registered; [`followup_circler.py`](followup_circler.py),
[`circler-lifetimes.csv`](circler-lifetimes.csv)). **The registered S102 seed itself dies, at t = 3979.9 tu.**
Of the 12 perturbed starts, 4 die at 933.7, 977.6, 988.8 and 1291.0 tu (the same 4 that died in
Part A), and 8 are still circlers at 5000 tu (mass 0.5221–0.5232). So the circler is a long-lived
state with a broad, start-dependent lifetime, not a stable one. The 2000 tu horizon of Part A,
and Night 0's 20 000-step runs, were too short to see the reference die. The project engine
`alm.lenia.Lenia` (single world, `specimens.load("S102").place(128)`) gives the same death step,
39 799. That is a second engine within Lane 6, not an independent replication.

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
also depends on the σ offset.

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
- Every path interleaves: an isolated static body at λ 0.20 on Orbium → ring, and circler
  survival broken by deaths near both circler ends. P3 is refuted.
- The ring has the widest basin along both paths that reach it (λ ≥ 0.55–0.60). Orbium's reaches
  λ 0.05–0.10, and the circler's is no wider than one or two grid points.

## Failed and inconclusive

- P1, P2 and P3 are refuted at the primary rule, and P4 for the circler at T 40 and for the ring at
  both variants (bitwise criterion).
- Unresolved: whether the 8 surviving circlers with a 1–2.4% smaller gyradius are a distinct
  body.
- Not tested: other μ, σ in the coexistence band; noise outside the seed's support; larger
  worlds; horizons beyond 2000 tu for Orbium and the ring (only the circler was followed to
  5000 tu). Whether Orbium or the ring also decay on longer horizons is open.

## Claims proposed (for the archivist)

- **L6-e.** At the coexistence rule (R 13, T 10), Orbium returns from 18/18 noise perturbations
  up to ε 0.1, and S103 returns bitwise from 24/24 up to ε 0.3. Both are attractors in this
  test.
- **L6-f.** S102 is not an attractor at its registered rule. 1% noise kills it in 2/6 runs, every
  primary-rule death comes after at least 500 tu of circling, and (exploratory) the unperturbed
  seed dies at 3979.9 tu while 8/12 perturbed starts survive 5000 tu. C038 should call the
  circler a long transient.
- **L6-g.** Blends between the three seeds never switch directly between phenotypes. Each path
  interleaves classes (4–5 changes), with dead zones and an isolated static island.
- **Strongest result for replication (Lane 3):** the unperturbed S102 seed dying at
  t = 3979.9 tu (39 799 steps) at μ 0.155, σ 0.020, R 13, T 10, 128², plus the ε 0.01 deaths
  (rng seeds 1000 and 1003, at 933.7 and 977.6 tu). These separate attractor from finite-horizon
  survival.
