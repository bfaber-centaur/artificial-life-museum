# L6-007: attractor geography of the coexistence rule (pre-registered protocol)

Lane 6 (Field Exploration), Night 1, 2026-10-07. **Written and committed before any L6-007 run.**
The commit that adds this file is the pre-registration timestamp. Later changes go under
"Amendments" with a reason and never rewrite this text.

## Question

C038 says one rule supports three phenotypes: glider (Orbium), circler (S102) and static ring
(S103). That rests on single runs of up to 1000 time units (tu) from one seed each. Two
questions:

1. **Attractor or finite-horizon survival?** Does each phenotype pull nearby states back to
   itself, and does it stay put over a horizon twice as long as Night 0's?
2. **Initial-condition geography.** Along straight lines between the three seeds, how are the
   outcomes arranged? One sharp boundary per path, or interleaving?

## Fixed inputs

| Item | Value |
| --- | --- |
| Primary rule ("coex") | R 13, T 10, μ 0.155, σ 0.020, β [1], poly kernel core, poly growth, Euler + hard clip, float64, periodic torus, 128² |
| Seeds | `orbium` = S001 cells; `circler` = S102 cells; `ring` = S103 cells (all from `research/specimens/`, centred) |
| Engine | `research/experiments/L6-field/field.py` (batched; bitwise equal to `alm.lenia.Lenia`) |
| Horizon | 2000 tu (20 000 steps at T 10) |
| Checkpoints | class recorded at 250, 500, 1000 and 2000 tu, each from the 100 tu window ending there |

Numerical variants (noise test only, horizon 1000 tu, checkpoints at 250/500/1000). Their
rules were chosen from Night-0 data (L6-004) as the σ where glider and circler both persisted:

| Variant | Grid | Rule change | Seeds resized |
| --- | --- | --- | --- |
| `R26` | R 26, 256² | σ 0.0205 (S102 dies at 0.020 at R 26, C039) | bilinear zoom ×2 (`scipy.ndimage.zoom`, order 1), clip [0, 1] |
| `T40` | R 13, 128², T 40 | σ 0.019 | none |

## Classes (same rules as L6-field, fixed in Night 0)

From the checkpoint window. died: final mass ΣA/R² < 0.01. filled: > 25% of cells > 0.1, or
mass > 30 × 0.4358. Otherwise, by net speed v_net and path speed v_path (R per tu, centroid
sampled every step): GLIDER v_net > 0.2; CIRCLER v_net < 0.1 and v_path > 0.2; STATIC
v_path < 0.02; OTHER for anything else.

**Signature** of a localized run: (windowed mean mass, windowed mean gyradius, v_path) over the
last checkpoint window. The **reference signature** of each phenotype is that of its
unperturbed seed run under the same numerics.

## Part A: noise robustness (attractor evidence)

For each seed s ∈ {orbium, circler, ring}, noise amplitude ε ∈ {0.01, 0.03, 0.1, 0.3} and
replicate k = 0..5: A₀ = clip(seed + ε·ξ·𝟙[support], 0, 1). Here ξ is i.i.d. uniform on
[−1, 1], drawn from `numpy.random.default_rng(1000·i_s + 100·i_ε + k)`, and support is the
seed's cells dilated by 3 cells (so noise also lands just outside the body). Plus one
unperturbed run per seed. That makes 3 × (4 × 6 + 1) = 75 runs per numerics.

A run **returns** if its final class equals its seed's phenotype and its signature is within
1% (mass, gyradius) and 2% (v_path) of the reference signature. A ring run must instead be
bitwise identical to the reference final state up to a periodic translation.

## Part B: interpolation paths (geography), primary rule only

For each pair (orbium–circler, circler–ring, orbium–ring), A₀(λ) = (1 − λ)·P + λ·Q, with both
seeds centred, λ = 0, 0.05, …, 1 (21 points). That makes 63 runs. Record the class sequence
along λ and the number of class changes.

## Predictions (fixed now)

- **P1 (attractors).** At the primary rule, every ε ≤ 0.03 run returns, for all three seeds
  (36/36). Refuted for a phenotype if any of its 12 small-ε runs fails to return.
- **P2 (horizon).** No run classified GLIDER, CIRCLER or STATIC at 1000 tu changes class by
  2000 tu (primary rule, Parts A and B). Each change found is reported as a finite-horizon
  transient.
- **P3 (geography).** Each of the three paths has at most 2 class changes. More than 2 counts as
  interleaving and is reported, not explained away.
- **P4 (numerics).** At R26 and T40, each phenotype still returns for ε ≤ 0.03 in at least
  10/12 runs. A phenotype failing this is NUMERICALLY_FRAGILE as an attractor at that setting.

No P-value machinery: runs are deterministic. Thresholds above are the decision rules.

## What would change C038

- P1 and P2 hold: C038 can be stated as three attractors (at T 10, R 13), not three survivors.
- P1 fails for a phenotype: that phenotype is a saddle or marginal state at this rule, and C038
  is narrowed.
- P4 fails: attractor status is resolution or timestep dependent, recorded as such.

## Outputs

`run.py` in this directory writes `noise-<variant>.csv`, `paths.csv` and `finals-*.npz`.
`README.md` reports results against P1–P4 with every failure listed.

## Amendments

- 2026-10-07 23:45 UTC, after all L6-007 runs had started and before any result was read: added
  `d2_resize.py`, an exploratory (not pre-registered) rerun of Lane 3's four S102 seed-resize
  methods (block, nearest, bilinear, cubic) at R 26 and R 39 in Lane 6's engine, requested for
  dispute D2 (C039 vs C047). It does not change P1–P4. Part A's R26 variant keeps the bilinear
  seeds as pre-registered.
- 2026-10-08 02:00 UTC, after Part A results were read: added `followup_circler.py`, an
  exploratory (not pre-registered) 5000 tu rerun of the unperturbed circler and its ε 0.01 and
  0.03 starts, to time the late deaths seen in Part A. It does not change how P1–P4 are scored.
