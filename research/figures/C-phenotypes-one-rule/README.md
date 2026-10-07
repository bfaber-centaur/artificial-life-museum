# Figure C: several phenotypes under one rule (PROVISIONAL)

![Figure C](figure-C.png)

[PNG](figure-C.png) · [SVG](figure-C.svg) · [PDF](figure-C.pdf) ·
plotted runs [`figure-C-data.csv`](figure-C-data.csv) · evidence matrix [`figure-C-matrix.csv`](figure-C-matrix.csv) ·
provenance [`figure-C.provenance.json`](figure-C.provenance.json)

> **Provisional evidence.** Everything plotted comes from Lane 6's PR #11, which has not been
> merged. It is read at the pinned commit `f40f303` with `git show`, and nothing from that PR is
> copied here. Every claim shown has one lane behind it. None has been reproduced by a second
> lane. The figure is meant to help judge PR #11, not to certify it.

## What it shows

| Claim | Status in `research/claims.md` | Where |
| --- | --- | --- |
| **C044**: Orbium's μ × σ neighbourhood is one continuum, apart from two circlers | OBSERVED | a |
| **C038**: one rule (μ 0.155, σ 0.020) supports a glider, a circler (S102) and a static ring (S103) | REPRODUCED (clean-process reruns, one lane) | b, c |
| **C039**: the circler dies at R = 26 at its own rule | NUMERICALLY_FRAGILE | b, c |
| **C040**: disturbances never switch glider and circler | OBSERVED | c (recovery column uses its runs) |
| **C042**: S103 is an exact fixed point of the clipped map | REPRODUCED (one lane) | c |
| **C043**: all three are catalogued species | OBSERVED | c |

The statuses are read from the ledger at build time (`figlib.ledger`). The build stops if any
of them changes. The figure is stamped with the ledger commit it was checked against.

## Caption

**a.** L6-001: S001's Orbium cells, run once under each of 441 rules (μ 0.100–0.200 by 0.005,
σ 0.008–0.028 by 0.001; T = 10, R = 13, 500 time units). Each marker is one run, placed at its
rule. Nothing is interpolated between grid points. The glider region is one connected block. Only
two rules give a circler. At μ 0.135, σ 0.018 the circler fills the world at about 850 tu, so it
is a transient. At μ 0.155, σ 0.022 it is still circling at 2000 tu and equals catalog OG2g.

**b. Resolution and timestep sensitivity.** L6-004: three seeds (Orbium cells, the S102 circler
seed, catalog OG2g cells) on a σ strip at μ 0.150 and μ 0.155. Each seed's base run (T10 R13) sits
directly above its resolution re-run (R 26: grid 2× finer, bold) and its timestep re-run (T 40:
step 4× finer), so shifts read vertically. The bottom three rows of each panel give, per setting,
the σ samples where the Orbium cells glide *and* the S102 seed circles (hatched). Grey ticks are
sampled σ without coexistence. The dashed line is σ = 0.020, the rule S102 and S103 are registered
under. Glider/circler coexistence appears at every setting, but its σ moves. At μ 0.155 the
circler's lower edge rises from σ 0.020 to 0.0205 at R 26, so **at R 26 the circler seed dies at its
own registered rule** (circled, C039). μ 0.160 was run only at T10 R13. It shows no coexistence and
is listed in `figure-C-data.csv` but not drawn.

| μ | T10 R13 | T10 R26 | T40 R13 |
| --- | --- | --- | --- |
| 0.150 | 0.0195, 0.0200 | 0.0195, 0.0200 | 0.0185 |
| 0.155 | 0.0200, 0.0205 | 0.0205 | 0.0190 |
| 0.160 | none | not run | not run |

**c.** At the registered rule (μ 0.155, σ 0.020), the evidence for each phenotype, split by
kind:
- **Persistence at a second T or R.** The three phenotypes coexist at this exact rule only at
  T10 R13. At T40 the Orbium cells settle into a *different* static body (mass 0.387, not S103's
  0.379). At R26 the S102 seed dies (C039).
- **Stronger tests by the same lane.** S102 and S103 have bitwise-identical clean-process
  reruns. S103 also returns bitwise to itself after 5–20% attenuation, which is evidence of an
  attracting fixed point. That evidence is from one phase and is recorded only as a table in
  its dossier, with no run file. The glider keeps its phenotype after ≤ 10% attenuation in both
  phases. The circler loses its phenotype in one of two phases at 5%.
- **Independent verification.** No phenotype has been reproduced by a second lane. Each is a
  catalogued species carried to this rule (C043).

## How to read the limits

- **Persistence is not an attractor.** A run that is still a glider after 500 or 1000 tu has
  persisted. That says nothing about the size of its basin, or whether a second code agrees.
  Only S103 has a direct return-to-self test, and it is single-phase.
- **Sampled grids.** Panel a has one run per rule, from one seed, at one T and R, with a 500 tu
  horizon. A cell that died might hold a creature from another seed. The phenotype boundaries
  sit somewhere between the plotted samples.
- **Classifier.** The phenotype labels re-apply Lane 6's own motion classes (`tables.py`,
  fixed before the T40 and R26 reruns) to the recorded speeds. The `outcome` column in
  `switch-T10-R13.csv` still holds the superseded "ROTATOR" labels, which Lane 6 says not to
  use, so it is ignored here.
- **One lane, one pinned commit.** If PR #11 changes, this figure is stale until it is rebuilt
  at the new head. When #11 merges, the paths stay the same and the figure can read from `main`.

## Alt text

Three-part figure, marked provisional. (a) A grid of 441 markers over μ (0.10–0.20) and
σ (0.008–0.028). Blue gliders form a diagonal band from low μ and σ up to about μ 0.16 and
σ 0.020. Grey dots (died) lie to the left, and dark squares (filled the world) to the right. Two
pink diamonds mark circlers at μ 0.135/σ 0.018 and μ 0.155/σ 0.022. (b) Two strip plots, for μ 0.150 and 0.155. Each seed's base run sits above
its R 26 and T 40 re-runs. Hatched boxes at the bottom mark where glider and circler coexist. At
μ 0.155 the band moves from σ 0.0200–0.0205 (base) to 0.0205 (R 26) and 0.019 (T 40). A red circle
marks the S102 seed dying at σ 0.020 at R 26. (c) A 3 × 7 table for the glider, circler S102 and static ring S103. The glider becomes a
different static body at T40. The circler dies at R26 and loses its phenotype at 5% attenuation
in one of two phases. The ring persists everywhere and returns bitwise after attenuation. The
"second lane reproduces" column reads "not yet" for all three.

## Sources (all at PR #11 commit `f40f303`)

| Data | Path | Used in |
| --- | --- | --- |
| L6-001 μ × σ sweep | `research/experiments/L6-field/musigma-T10.csv` | a |
| L6-004 σ strips | `…/bistab-T10-R13.csv`, `bistab-T10-R26.csv`, `bistab-T40-R13.csv` | b |
| L6-006 persistence | `…/persist-T10-R13.csv`, `persist-T40-R13.csv`, `persist-T10-R26.csv` | c |
| L6-005 disturbance runs | `…/switch-T10-R13.csv` (I001 rows, cases `orb@coex`, `gyr@coex`) | c |
| Clean reruns | `research/traces/S102-5bfac8f95f/`, `S103-1d8c158cdd/`, and the README's rerun table | c |
| S103 perturbations | `research/specimens/S103-static-ring.md` (table only) | c |

Blob IDs and SHA-256s of every file read are in `figure-C.provenance.json` (`pinned_inputs`).

## Reproduce

```bash
git fetch origin claude/night0-field-tmbx06        # makes commit f40f303 available locally
.venv/bin/python research/figures/C-phenotypes-one-rule/make_figure.py
```

The output is byte-for-byte deterministic.
