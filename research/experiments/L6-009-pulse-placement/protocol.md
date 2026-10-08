# L6-009: why is the bound pair fragile to a frontal pulse? (pre-registered protocol)

Lane 6, Night 1, 2026-10-08. **Written and committed before any L6-009 run.** Later changes go
under "Amendments". This is Q2 of `/mnt/project-files/lane6/next-questions.md`, run as the
coordinator's default while Bobby chooses.

## Background

L6-008 plus HR-009 E2: under I003 (Gaussian pulse, peak s, width 0.25 R, centred 1 R ahead of the
pair centroid) at s 0.2–0.3, S101 dies or degrades in 6/10 runs, while each partner alone survives
the same full pulse. The pulse centre falls in the gap between the partners.

## Competing explanations

- **(a) Overlap overload.** The pulse sits where both partners' kernels overlap, so the potential
  there is pushed out of the growth window and the damage spreads to both partners. Fragility
  should depend on the pulse being in the gap.
- **(b) Binding disruption (fusion).** The pulse pulls the partners together, they merge, and the
  merged body is not viable. The partners' lateral spread should collapse before death.
- **(c) Placement-independent.** Something about the pair as a whole (for example its slower
  speed, 0.473 vs 0.479 R/tu, so the pulse dwells longer). Fragility should not depend on where
  across the front the pulse lands.

## Fixed inputs

Same as L6-008: S001 rule (R 13, T 10, μ 0.15, σ 0.015, poly/poly, Euler + clip, float64), 128²
torus, S101 warmed for 3000 steps, phases t0 = 3000…3004, horizon 300 tu, outcome from the last
100 tu, `units()` and the frame (centroid, heading from the 10-step centroid displacement, port
normal) exactly as in L6-008's `run.py`.

**Pulse placement.** At each phase, let ℓ_P be the lateral coordinate of the port half's centroid
(cells with ℓ > 0, as in L6-008). The pulse is centred at

    c + 1 R · ĥ + f · ℓ_P · n̂,   f ∈ {0, 0.25, 0.5, 0.75, 1.0}

so f = 0 is L6-008's I003 (gap centre) and f = 1 is directly ahead of the port partner. Strengths
s ∈ {0.2, 0.3}. Starboard offsets are not run; the pair is assumed mirror-symmetric enough that
port offsets are representative (a stated limitation).

**Worlds per (s, f, phase).** The pair with the pulse added, clip(A + G), and each undisturbed half
alone with the same full pulse, clip(half + G) (HR-009's full-pulse baseline). That gives
2 × 5 × 5 = 50 pair worlds and 100 half worlds.

**Tracking (pair worlds only, first 100 tu).** Every 10 steps: mass, the number of components
above 0.1 (8-connected, periodic), and the lateral spread σ_ℓ (the mass-weighted RMS of ℓ about the
current centroid, using the t0 heading). The undisturbed pair's σ_ℓ over the same window is the
reference σ_ℓ⁰.

## Outcomes and decision rules

A **drag-down** is a run with n_pair < n_port_full + n_stb_full (an "other" pair outcome with
both halves surviving also counts).

- **(a) supported** if, pooling both strengths, drag-downs occur in ≥ 6 of 10 runs at f = 0 and
  in ≤ 2 of 10 at f = 1.0.
- **(c) supported** if the drag-down counts at f = 0 and f = 1.0 differ by ≤ 2 (of 10) and the
  count at f = 0 is ≥ 4.
- Anything else is reported as **placement-dependent but not clean**, with the counts per f.
- **(b) supported** if, in at least 2/3 of all drag-down runs, before the pair's mass first falls
  below 50% of its starting value, either the component count drops from 2 to 1 or σ_ℓ falls below
  0.6 σ_ℓ⁰. **(b) is rejected** if this happens in ≤ 1/3 of drag-down runs. (b) is judged
  independently of (a) and (c), since fusion could be how overload or a placement-independent cause
  acts.
- If the f = 0 runs do not reproduce L6-008/HR-009's 6 drag-downs out of 10 (they use the same
  pulse and the same code path), that is reported first, and the comparison is treated as suspect.

Deterministic runs, so no p-values. The thresholds above are the decision rules.

## Expected (stated now, so a surprise is visible)

I expect (a) with (b) as its mechanism: the gap is where the kernels overlap, and a pulse there
should pull mass between the partners.

## Outputs

`placement.csv` (one row per (s, f, phase), outcomes for the three worlds), `tracks.csv` (pair
tracks), written by `run.py`. `README.md` reports the verdicts.

## Amendments

_None._
