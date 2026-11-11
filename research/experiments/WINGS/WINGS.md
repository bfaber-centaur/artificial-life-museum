# WINGS: worlds beyond classic 2-D Lenia (2026-11-11)

Bobby asked for a wider search than classic Lenia ("go wild"). The species hunt
(SPECIES-scout, C063) had found only catalogued body plans inside classic 2-D Lenia, so this
round changes the physics instead of the parameters. Each world got its own simulator here,
written from the paper's equations (no upstream code is imported), a scout or a specimen, one
intervention, and a ledger entry. Nothing here is claimed as a new species. Every model is
published, and the labels say whose result each behaviour is.

| World | Simulator | Specimen | Intervention | Claim | Exhibit |
| --- | --- | --- | --- | --- | --- |
| Flow-Lenia (mass-conserving; Plantec et al. 2023) | `flow_lenia.py` | FL-43 ring-cell colony | patch mass ×1…×16; conservation switched off | C064, C065 | G022, G028 |
| Gray-Scott reaction-diffusion (Pearson 1993) | `other_worlds.GrayScott` | one dividing spot, F 0.0367 k 0.0649 | wipe half the world; dt/2 | C066 | G023 |
| Particle Lenia (Mordvintsev et al. 2022) | `other_worlds.ParticleLenia` | 200-particle spinning body | mirror; remove 50 particles; dt/2 | C067 | G024 |
| SmoothLife (Rafler 2011) | `other_worlds.SmoothLife` | SL-32 glider | dt/2, dt/4, resolution ×2, a still ring in its path | C068 | G025 |
| 3-D Lenia (Chan's animals3D.json) | `nd_lenia.py` | 36 catalogued species | flatten to the 2-D mid-slice | C069, C070 | G026 |
| Three-channel Lenia (Chan's found/233.json) | `nd_lenia.py` | 12 "aquarium" creatures | zero one channel; dt/10 | C069, C071 | G027 |

## What we found

**Conservation makes individuals (C064, C065).** Sixty random 10-kernel Flow-Lenia rules, one
noise patch each (`flow_scan.py`, G028), give droplets, membranes, crystals inside a membrane,
spoked wheels and, in a few rules, colonies of separate small bodies. In FL-43 the patch splits
into ring cells, and the number of cells follows the mass: 4, 6–7, 14–15, 28–29 and 51–57
cells for patches of mass 200, 390, 800, 1570 and 3190, about one cell per 58 units of mass
across 20 runs. Mass is conserved to 1.3 × 10⁻¹². Remove the conservation law and keep
everything else, and the same patch grows 21-fold into a world-wide maze of 225–231 fragments.

**Spots that divide (C066).** A single Gray-Scott spot becomes 301–305 spots tiling the
world by t 40000. Wipe half the world at t 20000 and the survivors divide back into it: 289–292
spots at t 30000, 302–303 at t 40000, the same as the controls. Half the timestep changes the
counts by under 2 %.

**A pinwheel made of particles (C067).** 200 Particle Lenia particles from random positions
assemble into a spiky body that keeps spinning at about 0.2 rad per 100 time units in 4 of 5
seeds, clockwise in some and anticlockwise in others. The rule does not pick the direction: at
half the timestep two seeds chose the other way. Remove a quarter of the particles and the
smaller body slows to 0.02–0.12 and sometimes reverses.

**A SmoothLife glider (C068).** 80 random SmoothLife rules (`sl_scan.py`) mostly gave
labyrinths. Five left a few isolated bodies, and in rule 32 one of them moved. Cut out, it
glides for 1000 time units at three timesteps and at double resolution. Its speed is stable in
the timestep (0.268 → 0.258 cells per time unit) but not in resolution (+46 % per outer
radius at ×2), so the speed is a numerical property, not the continuum's. Aimed at a still
ring, it absorbs the ring and leaves on a new heading.

**A third dimension (C069, C070).** Our N-D engine is checked against `alm.lenia` (10⁻¹²) and
runs Chan's 36 3-D species: 33 persist for 100 time units. Flatten each species to the 2-D slice
through its middle and run that slice under the same rule: 47 of 101 slices grow more than
twofold (most fill with dust), 42 die and 12 keep their mass. 28 of 36 species have no slice
that keeps its mass. A 3-D body is not a stack of 2-D bodies, and the same numbers make a
different world in 2-D.

**Many chemicals (C069, C071).** The engine also runs Chan's multi-channel, multi-kernel
"found" creatures: 161 of 205 sampled persist. The twelve three-channel aquarium creatures
(lithos, gyrans, tardus, egg, and lithos with one to four gyrans attached) all survive a
tenfold smaller timestep, and every one dies when any one of its three channels is zeroed.
No channel is optional.

## Not done / next

- A mass-matched control for the channel knockouts (scale all channels down instead of
  zeroing one).
- Flow-Lenia with several channels, and moving Flow-Lenia bodies: none of the 60 single-channel
  rules made a body that travels far.
- Particle Lenia parameter scan (other body types: gliders, "worms").
- Resolution convergence for the SmoothLife glider's speed.
- Neural cellular automata (needs training; no GPU stack here).

## Files

- Simulators: `nd_lenia.py`, `flow_lenia.py`, `other_worlds.py`; tests in `tests/test_wings.py`.
- Scouts and experiments: `flow_scan.py`, `flow_rings.py`, `gs_mitosis.py`, `pl_rotor.py`,
  `sl_scan.py`, `sl_glider.py`, `nd_survey.py`, `flatten.py`, `mc_knockout.py`; each writes a
  `.jsonl` with final-state hashes. `summarize.py` prints every number quoted here.
- Films: `film_wings.py` (G022–G024) and `ex_wings_more.py` (G025–G027); `film_wings.py verify`
  replays and checks hashes. `flow_sheet.py` makes G028 from `flow_scan.py`'s states.
- `states/` (gitignored) holds final states from the scouts.
