# Empty-world nucleation control — 2026-10-21

## Result

**No empty-world nucleation was found in either preregistered Gaussian family.**
All 14 blob-alone seeds became exactly zero by 1.8 tu and stayed zero through
25 tu. The widest seed carried 7.796830 R² of mass, about 16 times the reference
blob. The contact positives ignited; the contact negative returned exactly to
S103. This supports S103-dependent ignition for these tested inputs, **not a
universal requirement for S103** and not a measured empty-world threshold.

This follow-up is separate from unmerged PR #41, based on its fixed commit
`190b2b9dbb056105db714f9eef88c3de1a8935cd`. No expedition evidence, protocol,
ledger, exhibit, or integration branch was modified. The new protocol and runner
were committed at `60bf052` before the primary experiment. Tests were subsequently
moved into `tests/` for normal repository test discovery; the simulation runner
and preregistered criteria were unchanged during collection.

## Design and observed results

See [PROTOCOL.md](PROTOCOL.md) for the frozen criteria, schedule seed, bounds,
selection rule and controls. Family A scales the exact masked X9 blob; family B
widens a Gaussian at fixed peak parameter. Family B changes width as well as
mass, so its doses are not interchangeable with family A's amplitude doses.

| Conditions | Initial mass, sum(A)/R² | Outcome |
|---|---:|---|
| A: .25, .5, .75, 1, 1.25, 1.45× | .121826–.706590 | All evaporate; exactly zero by .2–1.8 tu |
| B: 1.5, 2, 3, 4, 6, 8, 12, 16× | .730948–7.796830 | All evaporate; exactly zero by 1.0–1.7 tu |
| Blank | 0 | Remains zero |
| S103 alone | .378698 | Bitwise fixed through 25 tu |
| S103 + .5× blob | .622350 total | Returns bitwise to S103 |
| S103 + .75× blob | .744176 total | Expanding colony; 40.3805 mass at 19 tu |
| S103 + 1× blob | .866001 total | Expanding colony; 34.6780 mass at 20 tu |

The primary positive runs are censored at 19.5 and 20.8 tu, respectively, by the
conservative boundary guard. Their scores use only integer-tu samples strictly
before those times. These are already growing, multi-body, spreading colonies;
no claim here depends on later torus saturation. At N512 the selected .75×
positive remains uncensored through 25 tu (mass 69.2191). The operational colony
label does not independently establish that the bodies are static rings/dumbbells;
that morphological description belongs to the original expedition.

## Numerical checks and limits

The preregistered no-ignition selection was A1.45, B16, contact .5/.75, ring and
blank: six cases per check. Total work: **43 bounded runs**, including 19 primary
conditions and 24 check/replay runs. No full expedition rerun.

| Check | Outcome classes | Quantitative comparison at common integer-tu observations |
|---|---|---|
| Clean process replay | 6/6 agree | All six final-state hashes identical |
| N512, same R and inputs padded with zeros | 6/6 agree | Max relative mass discrepancy <4e-13; radii agree |
| `alm_check` direct convolution, no FFT | 6/6 agree | Max relative mass discrepancy <6e-13; radii agree |
| T20, same physical horizon | 6/6 agree | Three conditions fail frozen numeric tolerances |

For T20, the maximum relative mass discrepancies (where baseline mass >=.01)
are 31.0% for A1.45, 93.7% for B16, and 14.2% for contact .75. Maximum radius
differences are .041, .491 and .605 R. These maxima include short-lived
transients, not just the final state. Both selected empty seeds still evaporate.
The .75 contact run still expands. Thus the **classes survive the checks, while
transient quantitative dynamics remain NUMERICALLY_FRAGILE**. A coarse sampled
mass curve is not an ignition-time convergence study. No spatial-resolution
convergence check was performed, and checks do not cover all 14 empty seeds.

The independent arithmetic and larger-domain checks argue against an FFT or
periodic-boundary explanation for these selected outcomes. Agreement does not
prove the continuum limit or rule out finer dose/shape-sensitive basins.
Deterministic conditions are not independent random replicates: no success-rate
confidence intervals are appropriate.

## What this establishes

* At the exact historical contact shape/placement, removing S103 changes the
  .75× and 1× inputs from colony formation to evaporation. This is a causal
  ring-presence comparison under the specified discrete dynamics.
* The ring-contact transition remains bracketed by .5× and .75× blob amplitude
  (approximately .244 versus .365 R² of **added** mass). Two endpoint classes
  do not demonstrate a unique monotone threshold.
* Large total seed mass alone is not sufficient across these Gaussian inputs.
  Broad, high-mass seeds evaporate too. It is not justified to say the empty-world
  threshold is simply greater than 16×: ignition could be nonmonotone or depend
  on width, density, holes, or other structure.
* We have not distinguished a uniquely necessary S103 geometry from a nucleus
  supplied by other organized shapes. We also have not demonstrated that S103
  merely lowers a scalar mass threshold. The original alternative is narrowed,
  not globally resolved.

## Smallest useful next experiments (not run)

First, because quantitative refinement failed its frozen tolerances, repeat the
selected A1.45/B16/contact .5/.75 contrast with ring and blank at T40 and T80.
Keep identical initial arrays and physical horizon. This tests whether the
class distinction persists before attempting precise threshold estimates.

To challenge S103 necessity with new seeds, use a four-condition empty-world
mass-by-width cross: target masses .744176 and 1.488352 R², Gaussian sigma .5 R
and 1 R. Normalize amplitude on the lattice without clipping (all four should
be admissible; verify peaks before execution). These include mass matching to
the positive contact world's **total** mass and independently vary density,
unlike simply extending the constant-peak B ladder. Reuse the contact .75
positive, S103, and blank controls under each numerical setting. Any checked
colony without S103 falsifies its universal necessity; four further nulls still
would not prove necessity. If a contrast appears, bisect only within the same
shape family, then apply the existing arithmetic/domain checks.

## Reproduce

Python >=3.10 with NumPy and SciPy is sufficient for this runner and its focused
unittest suite. The full project's optional developer dependencies support pytest.
Run from the repository root on this branch. Each output directory must be new;
the runner deliberately refuses overwrites. To recreate checked-in output paths,
use a fresh checkout and move the existing `results/` aside first, or choose new
paths and pass that root to `audit.audit(Path(...))`.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m unittest discover -s tests -p test_reef_nucleation.py -v
python research/experiments/REEF-nucleation/run.py --out /tmp/reef-new/primary
python research/experiments/REEF-nucleation/run.py --out /tmp/reef-new/N512 --N 512 --cases A1.45 B16 contact0.5 contact0.75 ring blank
python research/experiments/REEF-nucleation/run.py --out /tmp/reef-new/T20 --T 20 --cases A1.45 B16 contact0.5 contact0.75 ring blank
python research/experiments/REEF-nucleation/run.py --out /tmp/reef-new/direct --engine direct --cases A1.45 B16 contact0.5 contact0.75 ring blank
python research/experiments/REEF-nucleation/run.py --out /tmp/reef-new/replay --cases A1.45 B16 contact0.5 contact0.75 ring blank
python -c "import sys; from pathlib import Path; sys.path.insert(0, 'research/experiments/REEF-nucleation'); from audit import audit; audit(Path('/tmp/reef-new'))"
```

For a planning-only invocation add `--plan-only` and use a separate output path.
To audit the delivered results without simulations:

```bash
python research/experiments/REEF-nucleation/audit.py
```

Records: each group has an ordered pre-run `plan.json` and `summary.json`; each
condition has exact float64 initial/final arrays, compressed float64 per-tu
snapshots, per-step mass/guard data, per-tu morphology and `result.json` with
hashes. Plans include protocol/runner/engine/tracker hashes, source base commit,
actual execution commit/status, dependency versions and deterministic schedule.
`results/audit.json` verifies recorded file hashes, lists actual seed mass/peak/
RMS radius/support radius, exact extinction times, and numerical comparisons.
Final arrays at a boundary stop are preserved for provenance but excluded from
classification. Ten focused regression tests pass; the original PR's reported
105-test result was not rerun or claimed as validation of this follow-up.
