# SOWHAT: the "So what?" wing

Thread "Build a 'So what?' museum wing", 2026-11-15, requested by Bobby after a friend asked
whether any of this work matters outside the screen. Museum rooms 85–87, claims C112–C115,
gallery G062–G065, sources in `research/references.md` under "The ‘So what?’ wing".

The wing is mostly a guided tour of other people's work, labelled **evidence**, **tool** or
**analogy** (the rules are on room 85). The three small demos below exist so that each room
has one thing a visitor can watch, and so that the numbers the rooms quote go through the
ledger like every other number in the museum. None of them is a discovery: each reproduces a
textbook result, and the claims say so.

## Demos

| Demo | Code | Data | Claim | Gallery | Room |
| --- | --- | --- | --- | --- | --- |
| Drift vs selection (Moran, Wright-Fisher) | `drift.py` | `moran.jsonl`, `fates.jsonl` | C112 | G062 | 85 |
| Gray-Scott feed/kill atlas | `turing.py` | `atlas.jsonl` (+ `atlas.npz`, not committed) | C113 | G063 | 86 |
| SIR epidemic: mixed, lattice, shortcuts | `epidemic.py` | `epidemic.jsonl`, `threshold.jsonl` | C114, C115 | G064, G065 | 87 |

`summarize.py` prints every number the rooms and claims quote. `tests/test_sowhat.py` checks
the formulas, that the batched Gray-Scott equals WINGS's `GrayScott` step for step, and that
lattice infection is local.

## Reproduce

```bash
cd research/experiments/SOWHAT
../../../.venv/bin/python drift.py moran moran.jsonl           # ~10 s
../../../.venv/bin/python drift.py fates fates.jsonl           # <1 s
../../../.venv/bin/python turing.py atlas OUT/atlas.npz atlas.jsonl   # ~10 min, 100 worlds
../../../.venv/bin/python epidemic.py runs epidemic.jsonl      # ~10 s
../../../.venv/bin/python epidemic.py threshold threshold.jsonl  # ~30 s
../../../.venv/bin/python summarize.py
# pictures
../../../.venv/bin/python plots.py drift drift.png             # G062
../../../.venv/bin/python plots.py atlas OUT/atlas.npz atlas.png   # G063
../../../.venv/bin/python film.py epidemic epidemic.mp4 epidemic.gif  # G064 (+ epidemic-t120.png)
../../../.venv/bin/python plots.py threshold threshold.png     # G065
```

## Choices worth knowing

- **Drift.** The Moran runs use the embedded jump chain (only count-changing events), which
  has exactly the same fixation probability as the full process and is much faster. The
  Wright-Fisher paths are recomputed from a fixed seed by `plots.py`, not stored.
- **Atlas.** Same equations and constants as `../WINGS/other_worlds.py` (Du 0.2, Dv 0.1, dt 1),
  batched over 100 (F, k) pairs on a 128² torus for 10,000 steps. Every world gets the same
  eight seeded squares; Pearson used one central square. The `kind` labels in `atlas.jsonl`
  come from simple thresholds in `turing.describe` (cover, number and size of v > 0.2 parts,
  fraction of pixels that changed between steps 9000 and 10,000). They are a drawing aid and
  were checked by eye against the picture; they are not Pearson's classes.
- **Epidemic.** One contact model, three contact patterns. β and γ were chosen after a short
  scan (β 0.1, 0.15, 0.2, 0.3, four seeds each, not committed) so that all three worlds have a
  large epidemic: at β 0.1 the lattice is near its take-off threshold and often fizzles, which
  became claim C115 instead. Runs start from a 3 × 3 block of nine infectious people to cut
  down on early chance extinction.

## Ideas not done

- An adaptive-therapy toy: GenomeLenia's "division uncontrolled" invasion (C092) with a drug
  that kills only well-behaved cells, dosed continuously or on and off.
- A trained neural cellular automaton next to Lenia (needs a differentiable framework).
- Run ASAL-style automated search over our Lenia rule space and push its finds through the
  ledger.
