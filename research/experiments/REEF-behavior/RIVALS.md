# Rival explanations for each outcome class (hostile review, before pilots)

Written 2026-10-21 by the behavior lane before any encounter state was examined. Each REEF outcome
class has rivals in four families: numerical, torus, labelling and control. Each rival comes with
the cheapest observation that would tell it apart from the real effect. The scorer already
records most of these observables (`scores/<run>/score.json`, `trace.jsonl`).

General rivals, for every class:

- **G1 Lattice artifact (numerical).** At R13 the glider's heading is lattice-locked and slowly
  wandering (70.2° → 71.8° over 150 tu in isolation). A small kick can move it onto a different
  lattice-locked path, and that path change can be most of a measured "deflection". *Discriminator:*
  R26 with block replication (checks table). Also test whether the post-contact heading lands on
  the same quantised value in GA and GB.
- **G2 Sensitivity, not mechanism (numerical).** Glider dynamics near contact may be chaotic, as
  S102 is under this rule (HR-009). Then the class depends on ulps, not geometry. *Discriminator:*
  `alm_check` direct window from the saved pre-interaction state. A class flip under round-off
  makes the result NUMERICALLY_FRAGILE, whatever the mechanism.
- **G3 Snapshot ≠ phase (control).** GA and GB are elapsed-time snapshots 0.5 tu apart, not phases.
  A GA/GB difference is a timing/sub-cell offset difference, not a "phase effect". Report it as a
  0.27 R (0.5 tu × 0.548 R/tu) arrival and sub-cell offset difference.
- **G4 Integer placement (control).** Ring offsets are rounded to cells. *Discriminator:* use the
  realized b/R, not the requested one, in every comparison. If two outcomes differ, check that the
  realized offsets actually differ in the stated direction.

| class | numerical rival | torus rival | labelling rival | control rival | discriminator |
|---|---|---|---|---|---|
| NO_CONTACT | the residual floor is set too high, so a real kernel-range effect is called none | t_c missed because contact happens after the 30 tu timeout on a wrapped approach | supports at θ_s 0.01 never 8-adjacent although A > 0 halos interact (contact defined too strictly) | — | report t_int and t_kr; INTERACTION_WITHOUT_CONTACT / DEFLECTED_WITHOUT_CONTACT flags; recheck the gap at θ = 0.001 |
| PASS | heading change below θ_defl only because the fit window (5 tu) averages a transient turn | the glider meets another ring image later (censoring guard missed) | after a brief merge the reacquired G is the wrong fragment | G-alone heading wanders ≥ 1° on its own over the window | kinematics vs control at matched times (not nominal heading); BRIEF_CONTACT flag; inspect frames for any merged interval |
| DEFLECT | lattice re-locking (G1); deflection angle quantised to lattice directions | apparent deflection from min-image unwrap error during a wrap | centroid of a reacquired glider shifted by ring cells it carried away (owned-cell centroid bias) | — | R26 and T20 replays; check that the post-contact heading equals one lattice-locked value in both snapshots; mass ratio ≈ 1 and GLIDER_CHANGED absent |
| RING_CHANGED | the ring is an exact fixed point of the *clipped* map, so any positive growth anywhere in the box changes it; a tiny clipped residue could pass the 1% tolerance or fail it on round-off | an image of the glider, not the primary, touched the ring | glider debris left adjacent to the ring is counted as ring mass (owned S by adjacency) | — | RING_EXACT before contact; owned-mass breakdown of the S body; frames at t_end; RING_MOVED needs ≥ 0.1 R |
| TEMP_BIND | a slow release driven by clip arithmetic, sensitive to T (T20 may change the dwell) | release followed by re-encounter on the torus (censored second contact) | flickering 8-adjacency at θ_s counted as "together" without real coupling | the glider slows near any mass (kernel attraction), so the same dwell would occur with a mass-matched non-ring obstacle | dwell time vs T20 and R26; together_intervals; dwell vs b/R should be smooth if mechanical; a passive-obstacle control is a later experiment, not in the pilots |
| CAPTURE | the joint body is a transient that would separate after the window (finite horizon only) | the glider is held between two ring images on N256 | cell identity says G merged, but the glider has dissolved and the ring only grew | the glider would have turned STATIC on its own (T40 gives a STATIC Orbium at this rule) | always say "through t_c + 20 tu"; extend the follow-up on a larger world; G mass owned vs total; G-alone stays GLIDER (CONTROL_FAILURE otherwise) |
| CONVERT | numerical drift into a known attractor (S102 circler or S103 ring) that exists at this rule anyway | — | joint-body motion is the centroid moving because mass redistributes, not translation | the converted phenotype also appears from a perturbed isolated glider (any kick converts) | compare with the catalog of this rule's phenotypes (L6-005: circler/ring masses 0.378698); a kick-only control (an S103-shaped mass removed after 1 tu) would separate contact from generic perturbation |
| FISSION | clip round-off splits a thin neck | — | specks above 0.005 count as bodies | the isolated glider also sheds bodies above 0.005 | debris_max and DEBRIS_HIGH; body masses at the end; persistence of the fragments for ≥ 1 tu |
| G_DEATH / S_DEATH / BOTH | T- or R-dependent fragility: at refinement the same contact may not kill | collision with a periodic image, not the primary ring (the S101 lesson) | absorption mislabelled: glider cells overrun ring cells and keep the S label (cell identity) | the control would have died (CONTROL_FAILURE catches it) | t_cen and image distances; the larger-world check; frames at the death; whole-world mass vs labelled mass |
| FILL | — | the filled world is a torus effect (growth wraps) | — | — | the larger world at unchanged R |

## What would most embarrass a positive claim

1. **The deflection is a lattice re-lock.** If GA and GB give the same post-contact heading even
   though their pre-contact geometry differs, and R26 gives a different angle, the "deflection" is
   about the grid, not the ring.
2. **Coupling is just survival of an untouched partner** (C041 lesson). RING_EXACT after contact
   means the ring returned bitwise. The interesting outcome is then about the glider alone, and
   the claim must not be phrased as a mutual interaction.
3. **Kernel-range interaction without contact.** If t_int precedes t_c by ≥ 0.5 tu (Pr1), the
   relevant event is the kernel overlap. The 8-adjacency "contact" is then a threshold artifact and
   should not be the headline time.
