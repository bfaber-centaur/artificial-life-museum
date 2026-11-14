# ZOO: the collision zoo (2026-11-14)

Thread "Build a creature collision zoo". Goal: ecology by collision. Take catalogued creatures
that share one rule, aim them at each other at many angles and offsets, and map what comes out.

## What is here

| File | What it does |
| --- | --- |
| `zoocore.py` | torus components, settle / rotate / re-settle a body, `place_pair` (straight-line paths that pass at impact parameter b in the relative frame), outcome classifier |
| `atlas.py` | worlds and the atlas runner. `run O` (Orbium, S001 rule), `run O20` (same at T 20), `run P` (Pteryx rule), `run PC` (each Pteryx head-on at a still Circium, fine b) |
| `atlas-*.jsonl` | one row per collision: classes, products, masses, measured headings, final sha256 |
| `chamber.py` | bubble-chamber sheets: replays rows, max-over-time exposure, checks hashes |
| `feed.py` | the keeper: feeds a Hexapteryx one Circium ring at a time, rewinding meals that did not grow it |
| `feed-*.json` | feeding logs (every try, sha256 per accepted meal) |
| `ladder_match.py` | fed arc vs catalogue P6al–P10al: best normalised correlation over rotations and shifts |
| `forage.py`, `forage-K8.jsonl`, `forage-K60.jsonl` | free-world foraging, no keeper (round 2) |
| `fused_check.py`, `fused_check.json` | fused Orbium pairs vs S101 (round 2) |
| `aquarium.py`, `aq-bombard.jsonl` | gyrans thrown at a lithos in Chan's 3-channel aquarium (notes only) |
| `exhibits.py` | gallery G035–G037, G047–G048 |
| `summarize.py` | prints every number quoted in C080–C083, C093–C095 and museum room 78 |
| `zoofilm.py`, `eat_check.py`, `aq_tracks.py`, `aq_peek.py`, `rot_test.py`, `settle_test.py`, `grid.py` | scouting tools (quick films, text grids) |

`states/` (gitignored) caches settled bodies and feeding snapshots; everything is rebuilt
deterministically if it is missing.

## Worlds

Collisions only make sense between animals that live under the same rule. In the pinned
catalogue (`animals.json`) few species share one: Orbium (O2u) is alone under the S001 rule;
P6al, P7al, P8al, P9al, P10al, P24al (the *arcus labens* Pteryx ladder) and C0v (Circium
ventilans) share μ 0.38, σ 0.07, R 13, T 10; Chan's twelve three-channel aquarium creatures
(found/233.json 0–11) share one 15-kernel rule.

## Findings

1. **Two Orbia (C080).** 204 collisions (θ 15°…180°, b −2…+2 R). Six outcomes: miss/deflect 62,
   one dies 71, touch and part 33, both die 23, fuse into a two-lobed glider 12, detonate 3. At
   T 20 the same six appear but only 54 % of cells agree: the repertoire is robust, the map is
   not. Chan 2019 §3.5.5 named these outcomes qualitatively.
2. **Pteryx world (C081).** Two arcs that touch always detonate (204/204 contact rows, plus
   82/82 in the first dense pass). A still Circium ring detonates an arc when it meets the body
   and is swallowed when it meets a wing tip; the swallow window sits at |b| ≈ 3.75 R for P6al and
   moves out 0.5 R per segment.
3. **Eating climbs the ladder (C082).** A Hexapteryx that swallows k rings becomes P(6+k)al:
   shape correlation 0.993–0.998 against the right rung, ≤ 0.89 against the others; masses
   within 0.3 %. One ring (146 cells) is about one segment (135 cells).
4. **How far (C083).** Alternating sides: 25 meals, about 31 segments, then every offset
   detonates. One side: 21 segments, then rings are eaten without growth. T 20, one side: about
   25. The top rung depends on protocol and timestep.
5. **Aquarium (notes only).** 24 bombardments of a lithos by 1–4 gyrans over 1500 tu: the rock
   always survives, no gyrans ever stays bound (no lithos+gyrans compound forms), and crowded
   gyrans kill each other. With one gyrans both survive in all 6 seeds. Movers in this world
   curve (limus, egg) or spin (gyrans), so the straight-line aiming used elsewhere does not
   apply; a proper aquarium atlas needs a different placement scheme.

## Round 2 (2026-11-14, same thread)

6. **No keeper (C093).** `forage.py`: one P6al at a random heading among K still rings, no
   intervention. K = 8, 64 seeds: all detonate (median 80 tu); first encounters are 56
   detonations, 6 meals, 2 rings destroyed; nobody eats twice. K = 60: all 16 detonate by 55 tu.
   G047 films seed 62 (meal at t 110, detonation at t 205).
7. **Fusion makes S101 (C094).** `fused_check.py`: 9 of the 12 C080 FUSE bodies settle into S101
   (mass, gyradius, speed within 0.001); one sheds a lobe, one sits near S101, one detonates
   late. G048.
8. **Tip-or-belly at T 20 (C095).** `atlas.py run PC20`: 361 of 365 rows agree with T 10; the
   four changes are one-step shifts at the +b swallow windows.

## Ideas not done

- Pteryx × Pteryx below the detonation threshold (is there *any* gentle contact?).
- Foraging with moving food (rings never move, so an arc only meets what is on its line).
- Later fates in the O atlas beyond contact + 25 tu.
- Coexistence world (glider, S102 circler, S103 ring) beyond the reef's glider–ring result.
