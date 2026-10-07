# L4-002: lone-Orbium baselines for L6-008, results

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

These match L4-001's edges (I001 at 10.0–10.3 %, I004 at 8–9 %, I003 at about +28 %), as predicted.
So the edges do not drift between t0 = 1000 and t0 = 3000. The one phase-dependent cell (I001
s = 0.10) sits on the edge L4-001 located at s* = 0.1016. Night 0 saw the same split for lone
Orbium at 0.10 (1 of 2 phases).

## How to use this against L6-008

- **I001** acts on the pair and a lone Orbium identically (the same fraction from every cell). If
  the partners are independent, a pair at s should keep 2 units where the lone column shows 1, and
  0 where it shows 0. The test is sharpest at s = 0.10: a lone Orbium survives 1 of 5 phases
  there.
- **I004** on the pair takes s × (pair mass) from the port side, which is about 2s of the port
  partner's own mass. The lone column says a port partner losing 10 % or more dies (pair
  s ≥ 0.05), and losing 5 % survives. If the partners are independent, every pair I004 run at
  s ≥ 0.05 should therefore end with n_pair = 1 (the starboard partner) wherever the cut stays on
  the port side. At s = 0.05 the port partner sits right at its own edge (10 % own-mass loss, lone
  dies at 10.3 %), so that strength is the most sensitive test.
- **I003** on the pair is centred 1 R ahead of the pair centroid, between the partners, not on
  either one's front. The lone column is only a reference for a blob of that size hitting one
  Orbium head-on. It is not a matched control.

## Caveats

- Engine: the Lane 1 reference stepper (`ref`). L4-001 showed the Lane 2 engine agrees at every
  bracket end, but L4-002 was not re-run on it.
- Edits are placed with the circular-mean centroid, as in L4-001 and as L6-008 copied at 7bd1a42.
  Amendment A3 of L4-001 shows this can move an edge by one bisection step (±0.003 in s) at most,
  which is far below these grid steps.
