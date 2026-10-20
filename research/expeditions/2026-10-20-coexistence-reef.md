# Coexistence-Reef Safari — ALM Night 2 (2026-10-20)

**Status:** Expedition directive / proposed protocol, not executed evidence.
**Repo:** `bfaber-centaur/artificial-life-museum`. This stays in the **existing** repo.
**Inference share:** ~15% of the three-project Claude budget. Preserve the other 85% for Graph Atlas and Tiny Games.

## Prior art inside ALM — read before starting

- [Night 1 synthesis](../reports/synthesis-2026-10-08.md), [claims ledger](../claims.md), [roadmap](../roadmap.md), [gallery](../gallery/README.md).
- [Draft PR #35](https://github.com/bfaber-centaur/artificial-life-museum/pull/35) parks **one-organism** Orbium/ring blending and off-gap S101 pulse work; it is *unreviewed*. Do not re-run, merge or overwrite it to manufacture novelty.
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
5. **If no signal:** publish the honest null, then (only if the remaining budget supports independent controls) try S102 × S103 at a numerically refined stable-survival setting. No species claims from a GIF.

## Warm lanes and stop gates

- Field leader (pre-registration, encounter runner); independent numerics; behavior naturalist; hostile reviewer; claims archivist; optional scientific illustrator. Do not spin up 20 agents for a 15% side mission.
- **Gate A:** isolated controls valid + known Night 1 result reproduced.
- **Gate B:** ≤6 pilot encounters recorded, with independent matched controls.
- **Gate C:** targeted sweep + all checks for any claimed interesting behavior.
- **Gate D:** committed experiment IDs, manifests, plots/animated evidence with replay provenance, a report in `research/reports/`, ledger additions with explicit status, and a clean handoff before inference expires.
- If the engines disagree, or apparent death depends on torus size, report the disagreement/artifact as the main result; do not optimize it away.
- Do not touch historical claims without new evidence. Do not call any discovery 'novel' absent catalog comparison and independent reproduction.

## Coordinator launch prompt

You lead **ALM Coexistence-Reef Night 2**. Read the existing Night 1 synthesis and PR #35 first. Your safari is glider–ring *contact* at μ=.155, σ=.020, not repeated one-body blend scans. Freeze the pilot and matched-control contract before exploration. Preserve raw runs and failed predictions, independently check surprising outcomes, rule out torus repeat-collision artifacts, and create only earned exhibits. Use an expedition-specific branch, keep earlier work intact, and reserve final inference for a durable scientific field report.
