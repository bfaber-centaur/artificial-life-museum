# REPLICATORS: creatures that make copies of themselves (2026-11-14)

Bobby asked for fun, provocative finds. The east wing (WINGS, C064–C071) already shows
Gray-Scott spots that divide and Flow-Lenia ring cells that split by mass. This round looks
inside Lenia itself: Chan's own "found" catalogue (pinned upstream `found/*.json`) has
multi-kernel creatures whose names say what they do: *replicator*, *egg*, *division too slow*,
*division well*, *division uncontrolled*, *divide*, *self-replicate... unstable*. Nothing here is
a new species and none of these creatures is ours. What is ours: we follow every cell of a
dividing colony and draw its family tree, we measure how fast one cell fills a world as the
rule slides from Chan's "well" to his "uncontrolled", and we film a replicator in three
dimensions.

All runs use `../WINGS/nd_lenia.py` (checked against `alm.lenia` to 1e-12, C069).

## What we found

**A family tree (C072, G029).** One cell of *division well* (found/213 #84: one channel, three
kernels, R 15) on a 384² torus becomes 81 cells in 2000 time units: 135 divisions, 14
generations deep, and 51 cells whose track ended early (merged into a neighbour or faded: the
tracker does not tell which).
Each cell is followed frame by frame (`tree.py`); its colour is a neutral heritable marker that
drifts a little at every division, so sisters look alike and distant cousins do not.

**How fast a cell fills the world (C073, G030).** Chan's *division well* and *division
uncontrolled* (#83) have the same kernels with slightly different rings, centres and widths.
Slide every number along the straight line between them (λ 0 → 1) and start each world from the
same well cell. The time to cover half of a 256² torus falls from 1175–1530 time units at λ 0 to
85–95 at λ 1, about fifteen-fold, and the 3-seed median never rises along the way. Half the
timestep gives 1155, 155 and 90 at λ 0, 0.5 and 1. "Well" leaves about a third of the world
empty (plateau occupancy 0.59–0.66); "uncontrolled" packs it to 0.99 and fills the gaps between
cells with a fine lattice of dots. There is no switch: the growth rate rises smoothly.

**A replicator in 3-D (C074, G031).** found/312 #21, which Chan named *self-replicate...
unstable* (one channel, two kernels, R 15, 3-D), buds into 4 bodies by t 100 in a 64³ box and
into 53 bodies by t 320 in a 96³ box, while its mass grows about 120-fold until the box is
packed with foam. **One becomes four (C075).** Its neighbour found/312 #7, *divide*, splits
into four bodies and stays at four in 64³ and 96³ boxes, but at half the timestep a fifth
appears after t 100.

## Not done / next

- Heritable variation: give each cell its own rule parameters (Flow-Lenia's parameter
  localisation) so that daughters can differ, and see whether a faster divider takes over.
- Selection: put *well* and *uncontrolled* cells in the same world (different rules per cell
  needs the same machinery).
- The 2-channel *mitosis* creature (found/221 #35) and the egg-laying three-channel *egg*
  (233 #11; dies in our engine at 256², C071 shows its relatives are fragile).

## Files

- `common.py` (torus labelling, catalogue loader), `scout.py` → `scout_N256.jsonl`
  (8 named dividers, 600 tu), `population.py` → `population.jsonl` (division well, 512², 3000 tu).
- `record.py` (stores a run as uint8 frames), `tree.py` (tracker + family tree), `film_tree.py`
  → G029. `interp.py` (the λ line), `growth.py` → `growth.jsonl` (C073), `film_ladder.py` → G030.
- `replicate3d.py` → `replicate3d.jsonl` (C074, C075), `film3d.py` → G031.
- `summarize.py` prints every number quoted here. `states/` is gitignored.
- Exploration helpers: `peek.py`, `peek3d.py`, `lineage.py` (first tracker, superseded by
  `tree.py`), `film_lineage.py`, `interp.jsonl` (first λ scan, body counts).
