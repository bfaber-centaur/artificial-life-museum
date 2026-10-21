# Coexistence-Reef Safari — ALM Night 2 (2026-10-20)

**Status:** Expedition directive / proposed protocol, not executed evidence.
**Repo:** `bfaber-centaur/artificial-life-museum`. This stays in the **existing** repo.
**Resource allocation:** No fixed cross-project inference share. Inference is abundant; elapsed time, per-session compute, attention and integration capacity govern the plan. Reserve roughly 15–20% of ALM effort for checking, reconciliation, an earned exhibit and a reproducible handoff.
**Current execution authorization:** Bobby authorized the expedition on October 20, 2026 (Pacific), after calibration PRs #37–39 merged. Follow [the concrete launch mandate](2026-10-20-reef-launch.md), which supersedes the measurements-only gate and supplies lane ownership, controls, bounded exploration and stopping rules. Authorization does not establish that workers have started; record actual execution separately.

## Prior art inside ALM — read before starting

- [Night 1 synthesis](../reports/synthesis-2026-10-08.md), [claims ledger](../claims.md), [roadmap](../roadmap.md), [gallery](../gallery/README.md).
- [PR #35](https://github.com/bfaber-centaur/artificial-life-museum/pull/35) preserves **one-organism** Orbium/ring blending and off-gap S101 pulse work. Its integration notes retain the unreviewed / unverified scientific status. Do not duplicate or overwrite it to manufacture novelty.
- The shared coexistence rule around **μ=0.155, σ=0.020** exhibits an Orbium-like glider, circler S102, and static ring S103. S102's collapse at R13/T10 is numerical-setting-dependent; do not assume it represents a continuum-law transient.
- Small-torus repeat encounters previously masqueraded as coupling-induced death in S101. This expedition explicitly controls that failure.

## Pick one rich habitat

**The glider–ring contact zone at the coexistence rule.** This is not another sweep of the S102/ring *single-organism blend coordinate*. Put an independently stable moving Orbium-like glider and S103 ring into **the same world under the same rules**. Ask: what does *first contact* do to either phenotype, and how does the answer change with relative offset and phase?

Observable possibilities are deflection, survival, a changed ring, temporary binding, persistent capture, fission, fusion, conversion, collapse, or nothing. None is a promised discovery.

## Field protocol: bounded, preregistered, independent

1. **Arrival / controls:** pin a clean main commit. At μ=.155, σ=.020, establish **separate isolated control runs** for both specimens in the actual toroidal world to be used (start at 256², justify size). Use settled starting states with reproducible transformations and hashes. S001's *native* μ=.150, σ=.015 trajectory is not a same-rule control. If either dies alone, pause the encounter study.
2. **Approach geometry:** measure actual glider direction, then place S103 on the predicted course with initially disjoint bodies (about 3–5 kernel radii before contact). Primary transverse offsets in radii: `b/R = -1.5, -1, -0.5, 0, 0.5, 1, 1.5`. Start with **≤6 pilot encounters**; preregister the subsequent offset × phase grid *before* broad runs. Use actual available phases rather than inventing continuously steerable headings.
3. **Score first contact separately from later collisions.** Record before/contact/after states, total/component mass, tracked unwrapped centroids, separation, contact time, speed, and moving/static classification with fixed rules. Flag any later collision caused by torus wrapping. Keep isolated controls matched to seeds and follow-up horizon.
4. **If there is a real signal:** on 2–4 preselected contrasts, verify with a genuinely independent engine/numerical route, a changed timestep `T`, a changed resolution `R`, and a larger-world or encounter-window control. Keep μ,σ fixed for primary refinement; if tuning them to match phenotype, label it a *separate* condition.
5. **If no signal:** publish the honest null. A pivot to S102 × S103 requires a separate scientific decision by Bobby and matched controls; it is not an automatic continuation. No species claims from a GIF.

## Warm lanes and stop gates

- Field leader (pre-registration, encounter runner); independent numerics; behavior naturalist; hostile reviewer; claims archivist; optional scientific illustrator. Activate only substantive responsibilities with explicit ownership and evidence handoffs; calibrate computational concurrency from measurements.
- **Gate A:** isolated controls valid + known Night 1 result reproduced.
- **Gate B:** ≤6 pilot encounters recorded, with independent matched controls.
- **Gate C:** targeted sweep + all checks for any claimed interesting behavior.
- **Gate D:** committed experiment IDs, manifests, plots/animated evidence with replay provenance, a report in `research/reports/`, ledger additions with explicit status, and a clean handoff before inference expires.
- If the engines disagree, or apparent death depends on torus size, report the disagreement/artifact as the main result; do not optimize it away.
- Reconcile historical claims against already-merged later evidence through dated, history-preserving amendments; retain original verdicts. Merging archived work never upgrades a claim. Do not call any discovery 'novel' absent catalog comparison and independent reproduction.

## Scientific preparation notes — added 2026-10-20

- At the fixed coexistence rule, the existing `L6-field/persist-T40-R13.csv` records Orbium becoming STATIC. Refinement must re-establish isolated moving/static controls; retuning sigma is a separate condition.
- `field.py` shares `alm` kernel/growth and measures a whole-world centroid. It is not an independent engine or a two-body tracking solution. `alm_check` is independently implemented, but its FFT route shares NumPy arithmetic; its direct-convolution path supplies different arithmetic.
- S103 has no internal phase at the primary fixed point. Use actual glider phases and measured headings, with explicit resizing, world size, horizons and re-encounter censoring.

## Original coordinator brief (use the concrete launch mandate above)

You lead **ALM Coexistence-Reef Night 2**. Read the existing Night 1 synthesis and PR #35 first. Your safari is glider–ring *contact* at μ=.155, σ=.020, not repeated one-body blend scans. Freeze the pilot and matched-control contract before exploration. Preserve raw runs and failed predictions, independently check surprising outcomes, rule out torus repeat-collision artifacts, and create only earned exhibits. Use an expedition-specific branch, keep earlier work intact, and reserve final inference for a durable scientific field report.
