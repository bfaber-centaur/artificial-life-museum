# SOUP: evolution in a conserved-matter soup

Thread "Evolve creatures in an open-ended soup", 2026-11-14. Claims C076–C078, gallery
G032–G034, museum room 77.

## The world

`soup.py` is Flow-Lenia (Plantec et al. 2023; our single-rule engine is
`../WINGS/flow_lenia.py`) with the rule *embedded in the matter*. Ten kernels are shared by the
whole world (built from `default_rng([7, k])` exactly as `FlowRule.random`, "kernel set k"). Each
cell also carries a **genome**: the ten weights h_k that say how much each kernel's growth
counts in that cell's affinity. The genome travels with the matter: we transport Q = A·g with the
same reintegration step as A, so a parcel of matter takes its genome wherever it goes. Every 20
steps one disc of radius 10 centred on a random bit of matter mutates (one random N(0, 0.15)
change to all ten weights, clipped to [0, 1]). Total matter is conserved to about 1e-12, so
bodies can only grow by taking matter from other bodies.

What happens where two parcels land in the same cell is **heredity**, and we built two kinds:

- `inherit="blend"`: the cell's genome is the mass-weighted average of what arrived. This is
  the natural choice and the one that falls out of transporting Q = A·g.
- `inherit="dominant"`: the cell takes the genome of the largest single parcel that arrived.
  Genomes are passed on whole; they never average (parcels that share one transport offset still
  merge, which is rare).

The affinity uses the genome smoothed over 4 cells (mass-weighted), so the empty space around a
body feels that body's rule.

## What we did

1. **Scout** (`scout.py`, `scout.jsonl`): the 60 kernel sets of the WINGS scout, each a 128²
   Voronoi patchwork of 12 founder genomes (the kernel set's own weights + N(0, 0.25)), 2000
   steps. Most worlds settle into a still mosaic within a few hundred time units: different
   genomes make different body plans under the same kernels (rings, worms, dots, membranes,
   hatched blobs; G034), but nothing moves and the mosaic just sits. We ranked by motion and
   ran the liveliest at 256² for 12 000 steps (2400 time units): kernel sets 4, 16, 38, 59.
   Kernel set 16 was the one where whole colonies changed hands.
2. **Heredity** (C076, C077): kernel set 16, 256², 16 founders, seeds 0–3, each run twice from
   the identical start, once per heredity (`run.py B16s<k>` / `D16s<k> --inherit dominant`).
3. **Jenkin's test** (C078, `mutant.py`): one species only, no background mutation; one mutant
   disc, then 1000 time units under each heredity from the same mutated state; 12 mutants.

## Findings

**Blending swamps variation; particulate heredity keeps it (C076).** Under blending the genome
spread falls in all 4 seeds (0.58–0.67 → 0.32–0.41 at 2400 tu); under particulate heredity it
rises in all 4 (→ 0.81–0.84). In the genome fan (G033) you can watch it happen: each mutation
leaves a bright wedge that tapers back into the mean as its matter mixes with the neighbours'.
This is Fleeming Jenkin's 1867 objection to Darwin (a new variant is halved at every mixing and
soon vanishes); particulate inheritance, Mendel's genes, is the answer, and it is the answer here
too.

**Blending ends in one giant body (C077).** In kernel set 16, blending worlds condense: at 2400
tu one body holds 68–89 % of all matter in bodies (7–24 bodies left). The same worlds under
particulate heredity keep 70–150 bodies, the largest holding 18–47 %. Film: G032. A blend body
that swallows another body also swallows its genome, so the giant's genome is an average of
everything it ate.

**One mutation, two fates (C078).** See the claim for numbers.

Species bookkeeping (`species.py`, the population and phylogeny panels) is a drawing
convention, not a species concept: bodies whose mean genomes lie within 0.25 of a species'
centroid join it, otherwise they found a new species whose parent is the nearest living one.

## Caveats

- One kernel set (16) for the heredity claims; other kernel sets mostly freeze, so the contrast
  there would mostly be about mutations sitting still.
- Under particulate heredity part of the rising spread is plain accumulation of mutations that
  are never averaged away; we do not claim the extra diversity is adaptive.
- "Dominant" heredity also changes the physics a little (a body becomes a mosaic of genomes,
  and its pieces pull in slightly different directions). The comparison is between two whole
  worlds, not a pure test of the inheritance rule alone.
- 2400 time units; nothing here is an equilibrium.

## Files

- `soup.py` engine; `run.py` one world → snapshots (`SOUP_OUT`, default `states/`, gitignored);
  `runs.jsonl` final-state hashes of every run we made (the v* and L* rows are exploration runs;
  B16s0 was run as L16 and renamed).
- `scout.py` → `scout.jsonl`; `mutant.py` → `mutant.jsonl`; `diversity.py` → `diversity.jsonl`.
- `species.py` (bodies, species), `plots.py` (G033), `viz.py` (colours, G034), `film.py` (G032).
- `summarize.py` prints every number quoted here and in C076–C078.
- Tests: `tests/test_soup.py`.
