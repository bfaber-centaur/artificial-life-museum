# Lenia Morning Field Guide

*A cheat sheet for looking at the Artificial-Life Museum's creatures before coffee.*

This is a **field guide for ALM**, not a replacement for Bert Chan's Lenia taxonomy.  
Use the catalog taxon when we know it; use the museum labels below as quick behavioral/ecological tags.

## The calibration animal

### S001 — *Orbium unicaudatus*

**Catalog:** `O2u`  
**Taxon:** Exokernel → Orbiformes → Orbidae → Haplorbinae  
**Museum label:** 🌿 **Garden species** — canonical, maintained, boring in the best possible way.

Pinned ALM baseline:

- grid: 128 × 128, periodic torus
- `R = 13`, `T = 10`
- `μ = 0.15`, `σ = 0.015`, `β = [1]`
- polynomial kernel core + polynomial growth
- Euler update, float64, hard clip to [0, 1]
- stable mass ≈ 0.4358
- gyradius ≈ 0.4376 R
- speed ≈ 0.480 R / time unit
- heading ≈ 68° in its catalog orientation
- survives at least 5000 baseline steps

One memorable trap: its ≈4.32-step mass oscillation is a **lattice/orientation artifact**, not a heartbeat.

When confused by a new creature, compare it to Orbium first.

---

## Museum field labels

These are intentionally informal. They describe **how we encountered or use a specimen**, not its canonical biological-style taxon.

### 🌿 Garden species

Known, well-behaved catalog organisms that we deliberately keep around as references.

Use them for:

- simulator checks;
- perturbation calibration;
- morphometric baselines;
- asking whether a "new" behavior is actually unusual.

**Default example:** S001 Orbium.

A garden species is not uninteresting. A beautifully measured ordinary organism is our ruler.

### 🫥 Cryptofauna

Something repeatable may be there, but it is easy to miss or misclassify:

- faint / low-mass forms;
- long transients;
- intermittent localization;
- structures hiding inside apparently noisy fields;
- states that look dead until a longer run;
- subtle alternate attractors.

The cryptofauna rule: **do not promote from "huh" to "creature" from a GIF.**

Ask for a clean rerun, a saved state, a trace, and a modest timestep/resolution change.

### ⛈️ Storm species

A specimen or phenotype whose identity is revealed by disturbance.

Think:

- survives a deletion that kills neighbors;
- loses a chunk and regrows;
- deforms, then resumes locomotion;
- crosses into another stable phenotype;
- has a sharp recovery/failure threshold.

"Storm species" should mean **measured robustness**, not merely "looked tough."

The interesting object is usually the response curve:
**intervention strength → recovery / transition / death**.

### 🧭 Wanderer

Persistent locomotion is central to its phenotype.

Check that apparent travel is not:

- world recentering;
- toroidal wraparound;
- coarse-sampling aliasing;
- shape oscillation moving the centroid without true translation.

### 🪼 Shapeshifter

A reproducible transition between visibly or quantitatively distinct stable behaviors.

Especially interesting when a small rule/parameter change or controlled injury switches the phenotype.

Save **both states** and the transition conditions. "It changed shape" is not enough.

### 🦴 Fossil

A failed organism worth keeping.

Examples:

- dies reproducibly at a particular parameter;
- collapses after injury;
- survives visually but fails the recovery metric;
- once looked promising but was refuted.

Fossils are part of the museum. Negative boundaries often tell us more than another survivor.

### ✨ Mirage

A beautiful result that disappears under a modest numerical or measurement check.

Common causes:

- timestep;
- spatial resolution;
- float precision;
- grid orientation;
- boundary effects;
- bad centroid unwrapping;
- threshold chosen after seeing the answer.

Mirages are also specimens — just specimens of our instruments.

---

## What am I actually looking for?

When a render or GIF is interesting, run this mental pass:

1. **Persistence** — does localized structure remain for long enough to call it a state rather than a transient?
2. **Identity** — is the same qualitative object present after motion, rotation, or oscillation?
3. **Mass** — bounded, drifting, collapsing, or exploding?
4. **Motion** — translation, rotation, oscillation, or merely centroid wobble?
5. **Shape** — radius, anisotropy, symmetry, compactness: what is changing before your eyes notice?
6. **Response** — after a standardized injury, does it recover, transform, or fail?
7. **Threshold** — is there a narrow perturbation interval where behavior flips?
8. **Numerics** — does the story survive a modest timestep/resolution change?
9. **Provenance** — catalog creature, nearby variant, search result, or genuinely uncatalogued candidate?
10. **Prediction** — after watching once, can we predict something and then test it?

The last one is the difference between a cool GIF and natural history.

---

## Five anti-self-deception reminders

**Alive is not recovered.**  
Upstream's historical search criterion can count a surviving blob as success. ALM recovery should include coherent localization/behavior, not just nonzero mass.

**Pretty is not new.**  
The classic 2-D catalog already contains 548 specimens across many families. Check nearby rules and morphometrics before saying "uncatalogued."

**Same cells do not imply same organism-in-practice.**  
The upstream catalog contains the same starting cells under multiple rule choices. Record cells **and** rule parameters.

**A period is not automatically physiology.**  
Orbium's most obvious mass period follows orientation relative to the grid. Treat periodicity as guilty of being numerical until tested.

**The torus lies if you sample too slowly.**  
Centroid displacement wraps. Sample often enough that displacement between samples stays well below half the world width.

---

## Existing status words beat vibes

Keep the claims ledger vocabulary intact:

- **OBSERVED** — happened in a recorded run.
- **CONJECTURED** — explanation or generalization not yet tested.
- **REPRODUCED** — repeated under the intended setup.
- **INDEPENDENTLY_CHECKED** — reproduced through a genuinely distinct path.
- **NUMERICALLY_FRAGILE** — materially changes under a reasonable numerical check.
- **REFUTED** — a proposed claim failed its discriminating test.

A cute museum label and a claim status answer different questions.

Example:

> **S001 · 🌿 Garden · *Orbium unicaudatus* · REPRODUCED**  
> Translating canonical baseline; no intervention.

---

## Before anybody earns a proper name

"Sir Wobbles" rules still apply.

A candidate needs:

1. stable specimen ID + serialized/reconstructible state;
2. clean-process rerun;
3. survival of at least one modest numerical perturbation;
4. measurable/interventional behavior, not appearance alone;
5. catalog check;
6. independent reproduction.

Until then, whimsical descriptive labels are welcome; **proper names are provisional**.

---

## A good five-minute morning order

1. Read the coordinator's `research/reports/night-0.md`.
2. Look at **best creature** and **best failure** before the whole gallery.
3. Check the corresponding claim IDs and run IDs.
4. Watch the evidence once without interpretation.
5. Then ask: *what prediction would distinguish the fun story from the boring story?*

Only after that go creature-shopping through the GIFs.

---

## Tiny notation card

Classic 2-D Lenia is a continuous-valued field `A ∈ [0,1]`.

At each step, roughly:

`A ← clip(A + Δt · G(K * A), 0, 1)`

where:

- `K` is the neighborhood kernel;
- `K * A` is the local weighted neighborhood field;
- `G` maps that neighborhood value to growth or decay;
- `R` sets spatial scale;
- `T` sets temporal scale (`Δt = 1/T`);
- `μ, σ` locate and shape the growth window;
- `β` describes kernel-ring weights.

The "organism" is not a separately coded object. It is a **persistent dynamical pattern maintained by the rule**.

That is why injury, recovery, attractors, numerical artifacts, and natural-history language are all surprisingly useful here.

---

## Seed for the family-facing museum README

Later, tell the story as a lineage rather than a software manual:

**Conway's Game of Life** — binary cells, tiny local rules, startling emergent creatures  
→ **continuous cellular automata / SmoothLife** — soften the cell states and neighborhoods  
→ **Lenia** — smooth fields with kernels and growth laws; moving, deformable, animal-ish patterns  
→ **Artificial-Life Museum** — stop merely admiring the creatures and start doing natural history: catalog them, injure them, measure them, reproduce claims, and occasionally name something ridiculous.

That version gets pictures, almost no notation, and one central question:

> **What does it mean to learn something true about a creature made entirely of mathematics?**
