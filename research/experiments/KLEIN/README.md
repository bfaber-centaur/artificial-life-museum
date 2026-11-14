# KLEIN: Orbium on a Klein bottle (2026-11-14)

Strange-geometries thread, round 3. Claims C102–C104, gallery G053–G054, museum room 79.

## Engine

`klein.py` runs classic Lenia on a Klein bottle with the museum's own simulator, exactly. The
Nx × Ny bottle (left and right edges glued straight; top and bottom glued with a flip,
(x, y + Ny) ~ (−x, y)) is run as its double cover: an ordinary Nx × 2Ny torus stepped by
`alm.lenia.Lenia`, kept glide-symmetric (A[y + Ny, x] = A[y, −x]). The radial kernel commutes
with the mirror, so the symmetry is preserved by the dynamics; after each step the mirrored lower
half is copied over the upper half, which only removes round-off (`tests/test_klein.py`: a plain
step keeps the symmetry to 1e-12). `Torus` is the control.

Bodies on the bottle are counted on the cover (the chart cuts them at the flipped edge).

## Scripts

| script | output | claim |
| --- | --- | --- |
| `kb.py twist` | `twist.jsonl` | C102 |
| `kb.py narrow` | `narrow.jsonl` | C103 |
| `kb.py spin` | `spin.jsonl` | C104 |
| `kfilm.py G053 G054` (drawing: `kview.py`), `kfilm.py verify` | gallery G053–G054 | |
| `summarize.py` | prints every number quoted in C102–C104 and room 79 | |

Run from this folder with `PYTHONPATH=../../../src` and the repo's `.venv`.

## Findings in one line each

- **C102** Orbium cannot feel the twist: through 45 passages it moves within 0.18 cells of the
  same animal on a torus. Only the chart shows it mirrored.
- **C103** In a world 23–26 cells high, heading across the short way, it survives on a torus
  (32/32) but not on a Klein bottle (3/32): across the glued edge it meets its own mirror image,
  sliding the other way, instead of a copy of itself moving in step. From 28 cells up, no
  difference.
- **C104** Catalogued spinners (PG1a, OG2g) beside their own mirror image do not start to swim
  (drift ≤ 0.0046 R/tu, unchanged turning).

## Dead ends and lessons

- No travelling handed creature was found. S101 (the bound Orbium pair) is not handed (its
  partners' stagger is 0.005 ± 0.033 R, and the mirror gives −0.005). The catalogued spinners
  (PG1a, OG2g, the Gyrogeminium family) are handed but circle in place (net drift ≤ 0.007 R/tu
  on a 256² torus), so none can be carried round the bottle to come back mirrored.
- The circler S102 on narrow bottles vs narrow tori (heights 20–60 cells): no difference worth
  claiming; below 32 cells both blow up under the coexistence rule.
- First drift measurement for the spinners followed "the largest body" on the cover, which swaps
  between the animal and its mirror twin and gave a fake drift of up to 0.25 R/tu; `kb.py spin`
  follows the nearest body.
