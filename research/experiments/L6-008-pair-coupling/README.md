# L6-008: is the bound pair S101 coupled? (results)

Protocol: [`protocol.md`](protocol.md), pre-registered before any run. Runner:
[`run.py`](run.py). Data: [`pair-coupling.csv`](pair-coupling.csv) (165 runs: 3 disturbances ×
their strengths × 5 phases, plus 5 controls), [`validity.csv`](validity.csv).

    python research/experiments/L6-008-pair-coupling/run.py

## Revision after hostile review HR-009 (PR #30)

HR-009 E2 (Lane 7, preregistered) found a flaw I missed. The I003 pulse is centred in the gap
between the partners, so after the split each half receives only its own truncated half of the
Gaussian, while in the pair world each partner is within kernel range of the whole pulse. Lane 7
reran each undisturbed half with the **full** pulse. The pre-registered L6-008 verdicts below
are unchanged. The I003 reading is narrowed:

- **s 0.2 and 0.3:** in all 6 drag-down runs both halves survive even the full pulse, yet the
  pair dies or degrades. The drag-down stands at these two strengths.
- **s 0.4:** with the full pulse the halves also die or lose a partner, so the drag-down there is
  explained by pulse exposure.
- **s ≥ 0.5** ("rescue" to one Orbium, filled torus): neither baseline brackets the pair, and I
  no longer interpret these as coupling.
- HR-009's own pre-registered verdict on E2 is **INCONCLUSIVE** (6 of 10 drag-down runs survive the
  full-pulse baseline; its threshold was 8). That verdict stands. The narrower observation is a
  drag-down at s 0.2–0.3 under both baselines.

**Further caveat (2026-10-08, from L6-009, in a separate PR).** On a 128² world the gap pulse
splits the pair into two free Orbia, and the s 0.2 deaths happen when those two later collide on
the torus. On a 256² world the same edited states end as two Orbia in 5/5 phases (exploratory).
So the s 0.2 drag-down above is a finite-world artefact, and the s 0.3 deaths at the gap are
world-dependent too. L6-009 (to be proposed after this PR) narrows L6-d to placement-dependent,
near-field effects at s 0.3.

## Verdict

| Disturbance | Mismatches (strengths with ≥ 3 of 5 phases) | Pre-registered verdict | Reading |
| --- | --- | --- | --- |
| I004 port injury | 2 of 60 (none) | **H0** | The pair survives because the uninjured partner does. |
| I001 attenuation | 8 of 50 (only s = 0.08) | **H0 not rejected** | The one strong mismatch comes from the split-half baseline, not from coupling (see below). |
| I003 frontal mass | 24 of 50 (s = 0.2, 0.3, 0.4, 0.5, 0.9, 1.0) | **H1, coupling** (by L6-008's rule); HR-009 full-pulse check **INCONCLUSIVE** | Drag-down survives both baselines only at s 0.2–0.3. |

So **C041's fission under port injury is the trivial explanation**: the cut removes the port
partner and the starboard partner carries on as it would alone. The coupling that does show is
in the opposite direction from "binding protects". At s 0.2–0.3, a frontal mass pulse that each
partner survives on its own, even at full strength, kills or degrades the bound pair.

My expectation, written before the run, was H0 for I004 (confirmed) and coupling most likely
under I001 (not supported). I003 coupling was not predicted.

## Validity

- V1: half masses 0.434–0.439 in all 5 phases (gate 0.40–0.47). Pass.
- V2: mass within |ℓ| < 1 cell is 0.63–0.70% of the total (gate < 2%). Pass.
- V3: each undisturbed half, alone, becomes an Orbium in 5/5 phases, and the undisturbed pair stays
  a pair (n = 2 = 1 + 1). Pass. All 165 runs have a valid baseline.

## Outcomes

Each cell reads n_pair = n_port + n_starboard for phases t0 = 3000…3004; `*` marks a mismatch.
"o" is "other": a filled torus (mass ≈ 20) in 8 runs at s ≥ 0.7, and a non-Orbium moving body (mass 0.78) at I003 s = 0.2.

| s | I004 port injury |
| --- | --- |
| 0.05 | 2=0+1\* 1=0+1 2=0+1\* 1=0+1 1=0+1 |
| 0.10–0.50 | 1=0+1 in all 45 runs |
| 0.55 | 0=0+0 0=0+0 0=0+0 1=0+1 0=0+0 |
| 0.60 | 0=0+0 ×5 |

| s | I001 attenuation |
| --- | --- |
| 0.02–0.06 | 2=1+1 in all 15 runs |
| 0.08 | 2=1+0\* 2=0+0\* 2=0+0\* 1=0+0\* 2=0+0\* |
| 0.10 | 1=1+0 0=0+0 0=1+1\* 0=0+1\* 0=0+0 |
| 0.12 | 0=0+0 ×5 |
| 0.14 | 1=0+0\* 0=0+0 ×4 |
| 0.16–0.20 | 0=0+0 in all 15 runs |

| s | I003 frontal Gaussian |
| --- | --- |
| 0.1 | 2=1+1 ×5 |
| 0.2 | 0=1+1\* 0=1+1\* o=1+1\* 2=1+1 2=1+1 |
| 0.3 | 0=1+1\* 1=1+1\* 2=1+1 2=1+1 0=1+1\* |
| 0.4 | 2=1+1 1=1+1\* 1=1+1\* 0=1+0\* 0=1+1\* |
| 0.5 | 0=0+0 1=0+0\* 0=0+0 1=0+0\* 1=0+0\* |
| 0.6 | 0=0+0 1=0+0\* 1=0+0\* 0=0+0 0=0+0 |
| 0.7 | o=0+0\* 1=0+0\* 0=0+0 0=0+0 0=0+0 |
| 0.8 | 0=0+0 ×5 |
| 0.9 | 0=0+0 o=0+0\* o=0+0\* 0=0+0 o=0+0\* |
| 1.0 | o=0+0\* 0=0+0 o=0+0\* o=0+0\* o=0+0\* |

### I004: H0

In 58 of 60 runs the pair ends as exactly what its two halves give alone: from s = 0.10 to 0.50
the port half dies and the starboard half lives, in both worlds. The surviving Orbium reaches
single-Orbium mass within 0.7 tu of the cut at s ≥ 0.15 (`rec_pair_tu`), which is just the
leftover port tissue fading. The only mismatches are at s = 0.05 in 2 phases, where the pair keeps
both partners while the port half alone dies. A lone, relaxed Orbium survives I004 at 0.05
(Lane 4, L4-002), so this is the split half being fragile, not rescue.

### I001: one strong mismatch, explained by the baseline

At s = 0.08 every phase mismatches, and in the "rescue" direction: the pair keeps two Orbia in
4 of 5 phases while both halves, run alone, die. But Lane 4's lone Orbium
([L4-002](../L4-002-lone-baselines/README.md), same phases) **survives** 0.08 in 5/5 phases. So at
0.08 the split halves are weaker than a real single organism. They start as cut-out, unrelaxed
bodies. Against the lone baseline the pair is close to independent: lone gives n = 1 at 0.08
(5/5) and at 0.10 only in phase 3000, which predicts 2, 2, 2, 2, 2 and 2, 0, 0, 0, 0. The pair gives
2, 2, 2, 1, 2 and 1, 0, 0, 0, 0. Only one strength mismatches in ≥ 3 phases, so by the
pre-registered rule H1 is not claimed. This is a limitation of the split-half design: it is a
conservative baseline for drag-down and a biased one for rescue.

### I003: coupling, in the drag-down direction

At s = 0.2, 0.3 and 0.4 each half, given exactly its share of the same added mass (the edit is
applied before the split), survives in 14 of 15 runs. Yet the pair dies or degrades in 10 of 15.
I first argued that because split halves are, if anything, more fragile than relaxed Orbia
(I001 above), this drag-down could not be a baseline artefact. That missed the half-pulse
exposure. After HR-009 the drag-down holds at s 0.2–0.3 only (see the revision at the top).
The observations below at s ≥ 0.5 are recorded but not interpreted as coupling. At s = 0.5–0.7 the halves die but the pair often ends as
**one** Orbium (6 runs, mismatch "rescue"). It reaches single mass only after 5–18 tu, which
suggests the two damaged partners fuse into one body rather than one partner surviving. At
s ≥ 0.7 the pair world fills the torus in 8 runs where both halves die. Under the S001 rule, the
pair's combined mass plus the pulse can tip the world into growth, and neither partner alone
can. HR-009 found that at s ≥ 0.8 full-pulse halves sometimes survive where the split halves and
the pair die, so neither baseline brackets these outcomes.

Possible mechanism, not tested: the pulse lands 1 R ahead of the pair centroid, which for a
side-by-side pair is the gap between the partners, where both kernels overlap.

## Claims proposed (for the archivist)

- **L6-c.** Under I004 port injury (s 0.05–0.60, 5 phases) S101's survival matches the
  independent-partner baseline in 58/60 runs. Its fission to one Orbium (C041) is the uninjured
  partner surviving, not coupling.
- **L6-d** (narrowed after HR-009). Under I003 frontal mass addition at s 0.2–0.3, the bound pair
  dies or degrades in 6/10 runs while each partner alone survives, both with its half of the
  pulse (L6-008) and with the full pulse (HR-009). At s ≥ 0.4 the outcome is explained by pulse
  exposure or is not bracketed by either baseline. HR-009's preregistered verdict on this test is
  INCONCLUSIVE, and the s 0.2–0.3 drag-down is a narrower observation within it.
- **I001, H0 not rejected.** The s = 0.08 mismatch (5/5) is attributed to the split-half baseline,
  based on Lane 4's lone baseline, not to coupling. Design limitation, to stay with the claim:
  split halves start unrelaxed and are more fragile than a lone Orbium. That makes the split a
  conservative null for drag-down and a biased one for rescue.

## Not tested

Other pair geometries or the 7 other pairs found in L6-003. Resolutions other than R 13 and time
steps other than T 10. Whether the I003 drag-down depends on where the pulse lands. What
mechanism makes the pair fragile at s 0.2–0.3.
