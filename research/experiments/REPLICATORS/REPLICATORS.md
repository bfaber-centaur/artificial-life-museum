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

## Round 2: heredity and selection (C090–C092, G045–G046)

**GenomeLenia** (`genome.py`, our modified rule). Every pixel's matter carries a number g, its
position on the line from *division well* (g 0) to *division uncontrolled* (g 1), and the rule
at that pixel is the rule at g: each kernel's potential is mixed as (1 − g)·well + g·uncontrolled,
and μ, σ are interpolated. Matter that persists keeps its g; newly grown matter inherits the
mass-weighted g of its neighbourhood (2-px Gaussian). Optional mutation adds a small smooth
noise field to g every 10 time units. At g ≡ 0 or 1 this is exactly Chan's rule (10⁻¹²). A
*neutral* arm fixes the rule and keeps g only as a marker, with the same mutations.

**Selection for faster division (C090, C091, G045).** From one cell at g 0.3, with mutation,
the mean genome rises to 0.47–0.55 in 2000 time units; with g as a neutral marker it reaches
0.36–0.43. All four paired seeds end higher when the genome matters. Started at g 0.7, where the
growth speed has nearly levelled off (C073), the gap shrinks to 0.03–0.06. Nobody asked these
cells to grow faster. Faster dividers simply leave more descendants.

**The fast genome invades (C092, G046).** Grown *well* tissue placed against grown
*uncontrolled* tissue: by t 1000 the uncontrolled genome has spread into the well half (mean
0.34–0.38 there) while the uncontrolled half stays at 0.98–0.99, in 3 seeds.

A first inheritance rule that re-averaged *all* matter each step was dropped before the runs
above: it diffused genomes through the dot lattice like heat.

## Round 3: how far selection goes (C110–C111, G060–G061)

On a 512² world for 6000 time units, a single cell at genome 0.1 evolves to 0.65–0.69 (the
neutral marker reaches 0.31–0.35). The climb is fast for the first 1000 time units and then
slows. Runs that started at 0.7 stayed at 0.68–0.69. Selection seems to level off near 0.7,
where the growth-speed curve of C073 flattens: past that point, faster division barely pays.
The cells did not evolve all the way to *uncontrolled*. Two seeds per arm; whether 0.7 is a
resting point or a slow approach to 1 is still open.

## Not done / next

- Start above 0.7 (0.9, 1.0) and run longer, to tell a resting point from a slow climb.
- Let more of the rule mutate (kernel shells, R) instead of one line between two rules.
- The 2-channel *mitosis* creature (found/221 #35) and the egg-laying three-channel *egg*
  (233 #11; dies in our engine at 256², C071 shows its relatives are fragile).

## Files

- `common.py` (torus labelling, catalogue loader), `scout.py` → `scout_N256.jsonl`
  (8 named dividers, 600 tu), `population.py` → `population.jsonl` (division well, 512², 3000 tu).
- `record.py` (stores a run as uint8 frames), `tree.py` (tracker + family tree), `film_tree.py`
  → G029. `interp.py` (the λ line), `growth.py` → `growth.jsonl` (C073), `film_ladder.py` → G030.
- `replicate3d.py` → `replicate3d.jsonl` (C074, C075), `film3d.py` → G031.
- `summarize.py` prints every number quoted here. `states/` is gitignored.
- Round 3: `evolve.py … 512 6000 0.1 0.03` (C110), `chart_evolve.py` → G061, `film_genome.py long` → G060.
- Round 2: `genome.py` (GenomeLenia), `evolve.py` → `evolve.jsonl` (C090, C091), `invasion.py` →
  `invasion.jsonl` (C092), `film_genome.py` → G045, G046.
- Exploration helpers: `peek.py`, `peek3d.py`, `lineage.py` (first tracker, superseded by
  `tree.py`), `film_lineage.py`, `interp.jsonl` (first λ scan, body counts).
