# L6-009: why is the bound pair fragile to a frontal pulse? (results)

Protocol: [`protocol.md`](protocol.md), pre-registered before any run. Runner: [`run.py`](run.py).
Data: [`placement.csv`](placement.csv) (50 pair worlds, each with two full-pulse half worlds),
[`tracks.csv`](tracks.csv) (pair tracks, first 100 tu). Exploratory follow-up:
[`followup_bigworld.py`](followup_bigworld.py), [`bigworld.csv`](bigworld.csv).

    python research/experiments/L6-009-pulse-placement/run.py
    python research/experiments/L6-009-pulse-placement/followup_bigworld.py   # exploratory

## Verdict

| Rule | Result |
| --- | --- |
| Reproduces L6-008/HR-009 at f = 0 | **Yes**: 6 drag-downs out of 10, outcome for outcome. |
| (a) placement: ≥ 6/10 drag-downs at f = 0 and ≤ 2/10 at f = 1 | **Supported** (6 and 0). |
| (c) placement-independent | **Rejected.** |
| (b) fusion before death | **Not assessable as pre-registered** (see below). What the tracks show is the opposite: the gap pulse *unbinds* the pair. |

**The finding that matters, from the exploratory follow-up:** at s 0.2 and f = 0, the pulse does
not kill the pair. It splits it into **two free Orbia**, which glide apart on different headings.
On the 128² torus they meet again later (around 50–57 tu) and annihilate. On a 256² torus, the
same five edited states end as two intact Orbia in **5/5** phases (mass 0.8715, the sum of two
singles). So the s 0.2 "drag-down" in L6-008, which HR-009 accepted as coupling, is a
**finite-world collision artefact**. The split halves cannot reproduce it because each is alone in
its world. At s 0.3 and f = 0, 2 of 5 big-world runs still die, but late (death inside the
200–300 tu window), and in different phases from the 128² deaths. That again points to collisions
between the two freed partners, not damage from the pulse.

What remains as near-field coupling:

- **Drag-down at s 0.3, f = 0.25** (pulse slightly toward the port partner). The pair dies within
  about 8 tu in 4/5 phases, on both the 128² and the 256² world, while the starboard partner alone
  survives the full pulse. This is fast and is not a collision with a distant partner.
- **Rescue at s 0.3, f = 0.5–1.0** (pulse on the port partner). In 8 of 15 runs the port partner
  dies alone with the full pulse but survives inside the pair, which ends as two Orbia. This is not
  covered by any decision rule above, so it is recorded as an observation.

## Outcomes (128², 300 tu)

Each cell reads n_pair | n_port_full + n_starboard_full for phases 0–4. `*` marks a drag-down.

| s | f = 0 | 0.25 | 0.5 | 0.75 | 1.0 |
| --- | --- | --- | --- | --- | --- |
| 0.2 | 0\|1+1\* 0\|1+1\* o\|1+1\* 2\|1+1 2\|1+1 | 2\|1+1 ×5 | 2\|1+1 ×5 | 2\|1+1 ×5 | 2\|1+1 ×5 |
| 0.3 | 0\|1+1\* 1\|1+1\* 2\|1+1 2\|1+1 0\|1+1\* | 0\|1+1\* 0\|0+1\* 0\|0+1\* 0\|0+1\* 1\|0+1 | 2\|0+1 1\|0+1 1\|0+1 2\|0+1 2\|0+1 | 1\|1+1\* 2\|0+1 2\|0+1 2\|0+1 2\|0+1 | 2\|1+1 ×4, 2\|0+1 |

Drag-downs pooled over both strengths: 6, 4, 0, 1 and 0 for f = 0, 0.25, 0.5, 0.75 and 1.0.

## Why (b) could not be scored

The rule was that the component count drops from 2 to 1, or σ_ℓ falls below 0.6 σ_ℓ⁰, before mass
halves. Two things break it:

1. The undisturbed S101 is a single component above 0.1 (its partners touch), so "2 → 1" does not
   describe fusion.
2. After the gap pulse the partners separate. σ_ℓ grows from 9 to more than 30 cells within
   20 tu, then wraps around the torus and falls to about 4 when the partners pass each other on
   the far side.

The σ_ℓ criterion is therefore met by the letter in the f = 0 runs, but by separation and
wrap-around, not by fusion. I record (b) as not assessable rather than "supported". Direct
inspection (component positions every 2 tu) shows fission within 4 tu of the edit, then two
independent gliders.

## Big-world follow-up (exploratory, not pre-registered)

The same edited states, centred and zero-padded to 256², 300 tu, scored with `units()`:

| s | f | 256² outcome, phases 0–4 | 128² (main run) |
| --- | --- | --- | --- |
| 0.2 | 0 | 2 2 2 2 2 | 0 0 o 2 2 |
| 0.3 | 0 | 2 0 2 0 2 (deaths late) | 0 1 2 2 0 |
| 0.2 | 0.25 | 2 2 2 2 2 | 2 2 2 2 2 |
| 0.3 | 0.25 | 0 0 0 0 2 | 0 0 0 0 1 |

A 256² torus still lets two gliders meet eventually. So this shows the deaths depend on the world,
not that freed partners never collide.

## What this does to L6-d

L6-d (narrowed after HR-009 to drag-down at s 0.2–0.3) should be narrowed again:

- At **s 0.2** there is no drag-down. The gap pulse unbinds the pair into two viable Orbia, and
  the deaths are collisions on a 128² world.
- The s 0.3 gap-pulse deaths are world-dependent and probably collisions too.
- The robust coupling effects are fast and depend on placement: drag-down when the pulse sits
  slightly off-gap (s 0.3, f 0.25), and rescue of a directly hit partner (s 0.3, f 0.5–1.0).

L6-008 and HR-009 E2 both used 128² worlds, where a split pair can re-collide within the 300 tu
horizon. L6-c (port injury) is not affected, because there only one partner survives.

## Claims proposed (for the archivist)

- **L6-h.** A Gaussian pulse (s 0.2, width 0.25 R) centred in the gap 1 R ahead of S101 splits the
  bound pair into two free Orbia. The lateral spread passes 33 cells within 20 tu in 10/10 runs at
  s 0.2 and 0.3 on 128², and at s 0.2 all 5 big-world runs end as two Orbia. The s 0.2
  "drag-down" deaths in L6-008/HR-009 are later collisions on a 128² torus (0 deaths in 5 phases
  on 256²).
- **L6-i.** At s 0.3 the pair's response depends on where the pulse lands. Slightly off-gap
  (f 0.25) the pair dies within about 8 tu where the starboard partner alone survives (4/5 phases,
  both world sizes). On a partner (f 0.5–1.0), the pair keeps a partner alive that dies alone
  (8/15).

## Not tested

Starboard offsets (mirror symmetry assumed). Longitudinal placement. Other widths. World sizes
other than 128² and 256² for the off-gap effects. Why the off-gap pulse is lethal.
