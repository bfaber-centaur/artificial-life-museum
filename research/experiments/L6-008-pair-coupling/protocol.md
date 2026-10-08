# L6-008: is the bound pair S101 coupled, or two Orbia side by side? (pre-registered protocol)

Lane 6 (Field Exploration), Night 1, 2026-10-07. **Written and committed before any L6-008 run.**
Later changes go under "Amendments".

## Question

C041 says S101 survives a 10–50% port injury by shedding to one Orbium. The trivial
explanation is that the cut removes the port partner and the starboard partner, untouched,
carries on as it would alone. This test compares each injured pair with an
**independent-partner baseline**: the same edited state, split into its two partners, each run
alone in its own world.

## Fixed inputs

| Item | Value |
| --- | --- |
| Rule | S001 rule: R 13, T 10, μ 0.15, σ 0.015, β [1], poly/poly, Euler + hard clip, float64 |
| Pair world | 128² torus, S101 cells centred, warm-up 300 tu (3000 steps) |
| Phase replicates | edit after step t0 = 3000, 3001, 3002, 3003, 3004 |
| Horizon | 300 tu after the edit; outcome from the last 100 tu |
| Engine | `research/experiments/L6-field/field.py`; disturbances `L6-field/disturb_helpers.py` (Lane 4 L4-001 definitions, copied from `7bd1a42`) |

Disturbances and strengths (fixed now):

| ID | Edit | Strengths s |
| --- | --- | --- |
| I001 | uniform attenuation A ← (1 − s)A | 0.02, 0.04, …, 0.20 (10) |
| I004 | port injury (removes mass s·M₀ from the port side) | 0.05, 0.10, …, 0.60 (12) |
| I003 | frontal Gaussian addition, peak s, 1 R ahead of the pair centroid, width 0.25 R | 0.1, 0.2, …, 1.0 (10) |
| none | control | 0 |

The frame (centroid, heading from the 10-step centroid displacement, port normal) is measured
on the pair at t0, as in L4-001.

## Splitting into partners

At t0 the pair is two Orbium bodies side by side across the heading. Each cell gets a lateral
coordinate ℓ = (x − c)·n̂, using the pair's frame. **Port partner** = cells with ℓ > 0,
**starboard partner** = cells with ℓ ≤ 0. The split is applied to the *edited* state.

Validity checks (reported, and they gate the comparison):

- V1: each half of the undisturbed state carries 0.40–0.47 of mass (ΣA/R²).
- V2: the mass within |ℓ| < 1 cell is < 2% of the total (the partners barely touch).
- V3: each undisturbed half, run alone, becomes an Orbium (class GLIDER, mass within 5% of
  0.4358) in all 5 phases. If V3 fails, the baseline is invalid and the run reports that
  instead of a coupling verdict.

## Outcome per world

Count of **Orbium units** n: 0 if died; 1 if a GLIDER with mass within 5% of 0.4358; 2 if a
GLIDER with mass within 5% of 0.8736 (bound pair) **or** two separate Orbium-mass components
(net mass within 5% of 0.8716); otherwise "other". The pair world gives n_pair. The two
partner worlds give n_port and n_starboard ∈ {0, 1, other}.

**Independence prediction:** n_pair = n_port + n_starboard.

## Hypotheses and decision rule

- **H0 (independent partners).** Every run with a valid baseline satisfies the independence
  prediction.
- **H1 (coupling).** A *mismatch* is a run with n_pair ≠ n_port + n_starboard. Coupling is
  claimed for a disturbance if mismatches occur at **≥ 2 strengths, each in ≥ 3 of 5 phases**.
  This rule ignores isolated mismatches right at a survival edge, where Night-0 work (C030, C032)
  shows phase sensitivity.
- The direction of each mismatch is reported: **rescue** (n_pair > sum: the pair keeps a
  partner alive that dies alone) or **drag-down** (n_pair < sum: being bound kills a partner that
  survives alone).
- For each run where the starboard (uninjured) partner survives in both worlds, its **recovery
  time** is also reported: the first time after the edit at which its 10-step windowed mass stays
  within 2% of 0.4358 (single) for 10 tu. This is descriptive only.

## Expected (stated now, so a surprise is visible)

For I004 I expect H0 to hold, i.e. the trivial explanation. For I001, Night 0 saw the pair at
s = 0.10 lose exactly one partner in one phase while a lone Orbium at 0.10 survived in one of two
phases. Symmetry breaking between identical partners would show as a mismatch there, so I001 is
the disturbance most likely to show coupling.

## Outputs

`run.py` writes `pair-coupling.csv` (one row per disturbance × strength × phase, with all three
worlds' outcomes) and `README.md` reports V1–V3, H0/H1 per disturbance, and every mismatch.

## Amendments

_None._
