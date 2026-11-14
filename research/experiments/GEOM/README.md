# GEOM: Orbium on strange geometries (2026-11-14)

Strange-geometries thread. Question: what happens to classic Lenia's Orbium (S001, unchanged
rule) when space is not a flat square-tiled torus? Claims C084–C087, gallery G038–G040, museum
room 79.

## Engine

`geomlenia.py` runs classic Lenia on any point set. The kernel becomes a sparse matrix,

    W[i, j] ∝ K(d(i, j) / R) · area[j],   rows normalised to 1,   A ← clip(A + G(W A) / T, 0, 1)

with d the world's own geodesic distance. On the square torus it equals `alm.lenia.Lenia` to
6 × 10⁻¹³ (`tests/test_geom.py`). Worlds hold about one cell per unit area, so R = 13 is the same
physical size everywhere.

| world | builder | notes |
| --- | --- | --- |
| square torus | `square_torus(N)` | validation only |
| hex torus | `hex_torus(L)` | triangular lattice, spacing √(2/√3) |
| glass torus | `glass_torus(L, seed)` | random points relaxed by soft repulsion; amorphous |
| sphere | `icosphere(rho)` | icosahedral geodesic grid, spherical-Voronoi areas as weights |
| hyperbolic disk | `hyper_grid(kappa, rmax)` | {3,7} triangle tiling subdivided ν times per edge, exact hyperbolic triangle areas; empty beyond rmax, rim rows keep the interior normalisation |

`sphere(rho)` and `hyperbolic(...)` (relaxed random points) are kept but not used for claims:
like the glass, they are too noisy at R 13 (see C087).

Seeds: S001 cells through a cubic interpolant (`patch_sampler`), placed by the exponential map
(`seed_sphere`, `seed_disk`) or by rotation on a torus (`seed_torus`).

## Scripts

| script | output | claim |
| --- | --- | --- |
| `sphere.py meet` / `flat` | `meet.jsonl`, `flat.jsonl` | C084 |
| `pair.py run` | `pair.jsonl` | C085 |
| `sphere.py curvature` | `curvature.jsonl` | C086 |
| `heading.py hex 1 30`, `heading.py glass 2 30` | `heading_hex.csv`, `heading_glass.csv` | C087 |
| `film.py G038 G039` (drawing: `geomrender.py`), `compass.py` | gallery G038–G040 | |
| `cone.py run`, `cone.py apex` | `cone.jsonl` | C096–C098 (round 2) |
| `film.py G049 G050` | gallery G049–G050 | |
| `summarize.py` | prints every number quoted in C084–C087, room 79 and the captions | |

Run from the repository root with `PYTHONPATH=src` (or from this folder with
`PYTHONPATH=../../../src`). Memory: a hyperbolic world of 115 000 cells needs about 3 GB while its
kernel is built; run at most two at once in a 13 GB container.

## Findings in one line each

- **C084** On a sphere, parallel Orbia meet (14 of 16 pairs; never on the flat torus) and then
  glide on, fuse into a body with the bound pair S101's mass and size, or lose one animal.
- **C085** They meet (sphere) or spread (hyperbolic plane) exactly as geodesics do, within
  0.27 R: Orbium moves in straight lines of whatever world it lives in.
- **C086** Orbium still glides on a sphere of radius 7 cells (0.54 R); below that it turns into
  slow patches.
- **C087** The heading lock is not special to squares: a hex lattice locks Orbium onto its own
  few directions; an amorphous glass does not lock it but makes it flicker and sometimes die.

## Round 2: a lens made of nothing (C096–C098)

`cone(sectors, rmax)`: a hex lattice cut into 60° sectors around a lattice point and re-glued
with 5 (a cone, 60° deficit), 6 (flat) or 7 (a saddle point, 60° excess) sectors. The hex
lattice's six-fold symmetry about that point makes the seams invisible to the lattice, so the
only change is one point of concentrated curvature, like one vertex of the icosphere.

- **C096** Parallel pairs passing the cone point bend together and touch (3 of 3), following
  the straight lines of the cut-and-glued sheet within 0.28 R. Flat: never touch.
- **C097** Past the saddle point they spread from 3–6 R to 11–14 R, within 0.71 R of the lines.
- **C098** Aimed dead centre, Orbium dies at the saddle point; 0.25 R off centre it passes.
  Every shot at the cone point survives.

## Dead ends and lessons

- Relaxed random point sets ("glass") give the kernel a quenched noise: in pilots (1500 steps, every 100) Orbium's
  mass swung over 68–80 cells on glass against 72.7–74.9 on the hex lattice, and it sometimes
  dies (glass seed 0 at rotation 0 died between steps 400 and 800).
  Crystalline grids with area weights fix this, which is why the sphere and the hyperbolic plane
  use geodesic grids.
- A sinusoidal μ terrain (amplitude 0.004, period 256) barely steers Orbium at R 13: the lattice
  lock is stiffer than the terrain. Not pursued.
- Pool workers killed by the container's out-of-memory killer make `Pool.map` hang forever;
  `heading.py` now writes each run as it finishes.
