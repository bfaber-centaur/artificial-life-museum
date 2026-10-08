# L4-002: lone-Orbium baselines for L6-008, results

A reference dataset for Lane 6's L6-008. It is not evidence about pair coupling either way.
Pre-registered in [`protocol.md`](protocol.md) (commit 6f190fa, before any run). Data:
[`lone-baselines.csv`](lone-baselines.csv), 165 runs (33 conditions × phases t0 = 3000…3004).
Reproduce with `.venv/bin/python research/experiments/L4-002-lone-baselines/run_baselines.py`
(about 2 minutes on 4 cores).

## Result

A lone S001 Orbium, edited at the L6-008 settings, either stays one Orbium (n = 1, L4-001
RECOVERED) or dies (n = 0, DIED). No run of 165 was "other", EXPLODED or TRANSFORMED, and the
L6-008 unit count and the L4-001 class agree on every run.

Each cell lists the five phases t0 = 3000…3004 as n (1 = one Orbium, 0 = died):

| s | I001 attenuation | I004 port injury | I003 frontal addition |
| --- | --- | --- | --- |
| 0 (control) | 1 1 1 1 1 | | |
| 0.02 | 1 1 1 1 1 | | |
| 0.04 | 1 1 1 1 1 | | |
| 0.05 | | 1 1 1 1 1 | |
| 0.06 | 1 1 1 1 1 | | |
| 0.08 | 1 1 1 1 1 | | |
| **0.10** | **1 0 0 0 0** | 0 0 0 0 0 | 1 1 1 1 1 |
| 0.12–0.20 | 0 0 0 0 0 | | |
| 0.15–0.60 | | 0 0 0 0 0 | |
| 0.2, 0.3 | | | 1 1 1 1 1 |
| 0.4–1.0 | | | 0 0 0 0 0 |

Edges (mass terms from the achieved ΔM/M₀):

- **I001:** survives losing 8 % of its mass. At exactly 10 % it survives in 1 of 5 phases. It dies
  at 12 % and above.
- **I004:** survives losing 5.2 % of its mass from the port side and dies at 10.3 %.
- **I003:** survives a peak of 0.3 (+27 % mass) and dies at 0.4 (+36 %).

These are consistent with L4-001's edges (I001 at 10.0–10.3 %, I004 at 8–9 %, I003 at about +28 %),
as predicted. So within these grid steps, the edges do not shift between t0 = 1000 and t0 = 3000.
The one phase-dependent cell (I001 s = 0.10) sits on the edge L4-001 located at s* = 0.1016. Night 0 saw the same split for lone
Orbium at 0.10 (1 of 2 phases).

## Scope

This is a **reference dataset**: what each edit does to one Orbium on its own. It makes no claim
about coupling, protection, synergy or healing in the pair. That comparison, and any verdict, is
Lane 6's L6-008.

## Comparability with the pair edits

The three disturbances relate to the L6-008 pair edits in different ways:

| Disturbance | Status | Why |
| --- | --- | --- |
| I001 uniform attenuation | **Directly comparable** | It removes the same fraction s from every cell, so a pair edited at s and a lone Orbium edited at s receive the same per-cell edit. |
| I004 port injury | **Useful, with caveats** | *Mass units:* on the pair, s is a fraction of the pair's mass taken from the port side. That is about 2s of the port partner's own mass while 2s ≤ 1, so pair s maps to lone ≈ 2s, and this grid covers that for pair s ≤ 0.30. A lone Orbium survives losing 5.2 % from its port side and dies at 10.3 %. *Geometry:* the pair's cut line is parallel to the pair's heading and measured from the pair centroid, so the shape of what a partner loses is not the same as a lone port cut of equal mass. |
| I003 frontal addition | **Reference only, not a matched control** | On the pair, the blob is centred 1 R ahead of the pair centroid, between the partners, not on either one's front. The lone column only says what a blob of that size does when it hits one Orbium head-on. |

## Methods check against the preregistration

Checked against [`protocol.md`](protocol.md) (6f190fa):

- **Rule, world, engine:** S001 rule, 128² torus, `ref` engine, float64. As registered.
- **Phases and timing:** warm-up 3000 steps, edits after t0 = 3000…3004, a 3000-step horizon, and
  outcomes from the last 1000 steps (100 tu). As registered.
- **Strength grids:** the 33 conditions, including the control, × 5 phases make 165 rows in
  `lone-baselines.csv`. As registered.
- **Edits:** the `alm.disturb` L4-001 definitions, with the frame from the circular-mean centroid
  and the 10-step heading. As registered.
- **L6-008 n-units:** n = 0 if final mass < 0.01. n = 1 if net speed over the last 100 tu is
  > 0.2 R/tu and the mean mass there is within 5 % of 0.4358. Otherwise "other". As registered.
- **L4-001 class:** ±20 % bands over the last 100 tu. The protocol did not specify the window
  speed, so it is the mean of ten 10-tu block speeds, as in L4-001.

No deviations.

## Caveats

- Engine: the Lane 1 reference stepper (`ref`). L4-001 showed the Lane 2 engine agrees at every
  bracket end, but L4-002 was not re-run on it.
- Edits are placed with the circular-mean centroid, as in L4-001 and as L6-008 copied at 7bd1a42.
  In L4-001, switching to the size-independent centroid (amendment A3) moved three of 20 edges by
  one bisection step (0.003 in s). That is far smaller than these grid steps.
