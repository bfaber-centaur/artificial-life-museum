# Visual specimens for the lightning talk (2026-11-07)

**Asked by:** Bobby, 2026-11-07: "do a little more diving and find some truly visually interesting
things" for a lightning talk on the museum in about two weeks.
**Thread:** VIS-talk. Code: [`../experiments/VIS-talk/`](../experiments/VIS-talk/). Exhibits:
gallery G007–G013 ([`../gallery/README.md`](../gallery/README.md)). Museum: Room 8
(`museum/rooms/68-field-trip.html`). Ledger: C056–C058.

## What was done

1. **Catalogue survey (VIS-S1).** Every entry of the pinned upstream catalogue with poly/exp
   kernel and growth families and T ≤ 40 (526 entries) was run for 100 tu in ALM's own simulator,
   each in its own world, with classes fixed before the first run
   ([`survey.py`](../experiments/VIS-talk/survey.py), [`SURVEY.md`](../experiments/VIS-talk/SURVEY.md)).
   509 persisted, 13 filled their worlds (mostly the catalogue's own "Cateno-" growers), and 4
   died: `O2bi`, `H4?`, `2PN+c`, `KN+c` (C057; the deaths were not investigated).
2. **Seven films** made by [`film.py`](../experiments/VIS-talk/film.py), each recording rule,
   world, initial-state and final-state sha256 and the command in its `provenance.json`.
3. **Clean-process replay.** `film.py verify` re-ran every filmed simulation in a new process
   and matched every final-state hash (37 runs across G007–G013). The 40-seed soup scan's hashes
   are recorded in `soup-scan.json` but were not replayed separately.

## Shortlist for the talk (best first)

| # | Visual | File for the projector | Why it works | Honest one-liner |
|---|---|---|---|---|
| 1 | The reef at 1024² | `G008-the-reef/reef-world.mp4` | one touch fills a world | "One glider touches one ring and the world crystallises. Checked for the first 25 time units; after that it's one engine." |
| 2 | First contact close-up | `G008-the-reef/reef-contact.mp4` | the moment of ignition, big | "Fusion, then a front." |
| 3 | Frozen lattice detail | `G008-the-reef/reef-lattice-detail.png` | looks like a polycrystal | "Domains of aligned rings, in one run; we haven't measured them." |
| 4 | Spiral that draws itself | `G013-spiral/spiral.mp4` | hypnotic | "A catalogued species (Chan 2019) at a world size where it can wind several times." |
| 5 | Bestiary of 16 species | `G007-bestiary/bestiary.mp4` | variety in one slide | "All Chan's species, all alive in our own simulator: 509 of 526 survived our survey." |
| 6 | Same recipe, three fates | `G010-soup/soup.mp4` | life from noise | "Random noise: 27 of 40 die, 4 make a glider, 9 take over." |
| 7 | Collisions | `G009-orbium-collisions/collisions.mp4` | particle-physics feel | "Chan's collision zoo, reproduced: one sample per angle." |
| 8 | Anatomy of a step | `G011-anatomy-of-a-step/anatomy.mp4` | explains Lenia in 10 seconds | "The whole rule: sense a ring, grow or shrink." |
| (9) | Six growers | `G012-growers/growers.mp4` | labyrinths, ring lattice | "Catalogued growers; the labyrinths only *look* like Turing patterns." |

A suggested five-minute order: 8 (what Lenia is) → 5 (the zoo) → 6 (where creatures come from)
→ 7 (what happens when they meet) → 1–3 (our own expedition's result, with the scope caveat) →
4 (closing image).

## What is new and what is not

Nothing here is a new phenomenon, and the captions say so:

- **Primordial soup → Orbium:** Chan 2019 §2.3.1 (pdf p. 12).
- **Collision outcomes** (deflection, absorption, annihilation, fusion, detonation): Chan 2019
  §3.5.5 (pdf pp. 28–29).
- **Growing chains and spiral elongation:** Chan 2019 §3.5.4 (pdf p. 28).
- **Reef ignition:** "detonation" in Chan 2019 §3.5.5; the expedition's narrow new content is in
  C052–C055.

What is ours: the measured counts (C056–C058), the survey's persistence table (C057), and the
1024² extension of the reef encounter, which is single-engine and outside C052's checked window.
Chan 2019 was read from the copy in the project uploads (arXiv 1812.05433v3); section numbers
and printed page numbers are from that copy.

## Observations worth following up

1. **The S001 rule also freezes into a world-filling lattice from noise** (9 of 40 soups, G010).
   It looks like the coexistence-rule reef (G008). Is it the same kind of state? A comparison of
   body size and spacing, and a check that an S001-rule Orbium can ignite it, would say.
2. **The reef lattice forms domains** with boundaries between differently aligned regions
   (G008 detail). Measuring domain size against the front speed (C055) would turn the picture into
   a claim.
3. **Four catalogue deaths** in the survey (`O2bi`, `H4?`, `2PN+c`, `KN+c`). Each may be our
   placement or world size; worth one look each before anyone calls them simulator differences.
4. **Fused Orbium pairs** in G009: are they S101 (C041)? A tracker comparison would answer it.

## Limits

- Every film is a single `alm` run at one resolution and timestep. The only second-route check
  behind any of these pictures is the expedition's (C052, 3–25 tu).
- G012 is downsampled (Lanczos) and is not one pixel per cell. G011's U and G panels use
  different colour maps (disclosed). All other exhibits map A linearly onto `inferno`, one cell to
  one or more whole pixels.
- GIFs are 64–128 colour previews; use the MP4s on a projector.

## Reproduce

```bash
./scripts/bootstrap.sh                                  # needs .refs/Lenia for the catalogue
.venv/bin/python research/experiments/VIS-talk/film.py G007 G008 G009 G010 G011 G012 G013   # ~12 min, 1 process
.venv/bin/python research/experiments/VIS-talk/film.py verify                               # replay, compare hashes
cd research/experiments/VIS-talk && ../../../.venv/bin/python survey.py run --jobs 2 && ../../../.venv/bin/python survey.py table   # ~1 h
```
