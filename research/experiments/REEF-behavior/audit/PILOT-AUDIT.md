# Pilot audit P1–P6 (behavior lane, 2026-10-21)

Inputs: reef/field `91da893` (runs under Gate A addendum `3c3fdc4`, code `fe4ba1c`), per-step frames
from `/mnt/project-files/reef-field/runs/REEF-Pk-E/frames.npz`; every frames sha256 matches its
manifest. Scorer: reef/behavior (this commit), frozen §11 values plus D-013. Command per run:

    PYTHONPATH=src python research/experiments/REEF-behavior/score.py \
      research/experiments/REEF-field/runs/REEF-Pk-E --frames <frames.npz> \
      --out research/experiments/REEF-behavior/scores/REEF-Pk-E/score.json

Scores: `scores/REEF-Pk-E/score.json`. Per-step tracker rows (`trace.jsonl.gz`, 4–5 MB each) are in
the project folder `reef-behavior/scores/`; hashes in `scores/TRACES-SHA256SUMS`. Frame strips:
`P2-strip.png` (b = 0) and `P3-strip.png` (b = +1), encounter above, G-alone + S-alone below.
Front measurements: `front.json` (95th-percentile support radius about the ring centre, A > 0.01).

## Result

**All six pilots end the same way.** Kernel-range interaction (t_int) comes 0.6–0.8 tu before
support contact (t_c 6.1–6.8 tu). The glider and the ring then fuse into one body that never
separates. Within about 0.1–0.7 tu of contact the joint mass starts to grow. After 4–10 tu the body
breaks into an expanding colony of small dot- and ring-shaped bodies (median body mass ≈ 0.19–0.21,
about half an S103). Its front advances at 0.31–0.37 R/tu. At the end of the window (t_c + 20 tu)
there are 47–112 bodies and the mass is 26–50× the initial mass. The colony covers the whole torus
by 50 tu (≈ 300 bodies, mass ≈ 81). Both matched controls stay in class throughout. The glider-alone
control is a single GLIDER, and the ring-alone control stays bitwise fixed.

The scorer, following the frozen rules, gives **FISSION** for all six. That label is correct by
the rules and wrong as a description. Fill saturates at 0.22–0.24, just under the FILL threshold of
0.25, because the colony is a sparse lattice of small bodies; the world is nonetheless covered. Call
it contact-triggered proliferation / ignition. Any new class name needs a dated amendment (lead's call).

Snapshot and offset change only the onset. The flank b = +1 cases (P3, P6) ignite more slowly:
mass ≈ 1.0 at t_c + 5 against 2.3–4.1 for b ≤ 0. The fate is the same.

## Prediction check (PROTOCOL §10)

- Pr1 (t_int ≥ 0.5 tu before t_c): **holds** in 6/6 (0.6–0.8 tu). t_kr precedes t_int by 1.9–2.0 tu.
- Pr2 (head-on: ring survives, G_DEATH/CAPTURE likely): **fails**. The ring does not survive as S103.
- Pr3 (|b| = 1: DEFLECT or PASS, ±1 not mirror images): **fails** on class (all FISSION). The ±1
  onset timing does differ (b = −1 ignites fastest).
- Pr4 (snapshot changes class in ≤ 1 offset): holds (0 offsets).
- Pr5 (no FILL): holds by the letter (fill ≤ 0.24), **fails in substance**: the world is covered.

## Audit points (hostile)

1. **Torus margin is tiny.** The colony's support reaches N/2 from the ring centre at 27–30 tu,
   which is 0.2–3 tu after the window end (26.1–26.8). P1 and P4 have ≤ 0.3 tu margin at 1-tu
   sampling. The scorer's t_cen watches G bodies against ring images, not the colony against its
   own images, so this censoring is not automatic. Class at the window end is unaffected (FISSION
   from ~10–16 tu), but anything measured after ~26 tu on N256 is torus-contaminated. N512 is needed
   to follow the front.
2. **Identity is meaningless after ignition.** Cell ownership splits colony bodies into "G", "S"
   and "GS", but these are adjacency inheritances, not organisms. Report only topology and mass,
   and never "the glider survived as fragment X".
3. **Known precedent: this is probably the ring's response to a large addition.** The S103 dossier
   records that I003 frontal addition at 0.10 returns to S103 but ≥ 0.30 "fills the world". A whole
   glider (mass 0.49 against the ring's 0.38) arriving within kernel range is a large addition.
   The rival is that ignition is a generic property of S103 plus enough nearby mass, not anything
   glider-specific. The cheapest discriminator is a passive mass-matched blob (the GA state frozen,
   or a static mass) placed at the same contact offset, or a glider–glider collision at this rule.
4. **Numerical robustness is untested.** The ignition could depend on R13 or T10. The checks table
   (direct window, T20, R26, larger world) applies. T40 previously turned the isolated Orbium
   STATIC at this rule, so a T refinement may change the control, not only the encounter.
5. **No PASS/DEFLECT metric is available.** The glider merges at t_c and never separates, so
   heading Δ and lateral Δ are undefined in all six.

## Contrast selection (input to the lead; rule frozen in PROTOCOL §8)

All six look alike in class, so the rule picks the closest encounter (b = 0) and a flank or
no-contact case. Suggested: **P2** (GA, b = 0, fastest t_c) and **P6** (GB, b = +1, slowest
ignition, latest N/2 arrival). No pilot is a no-contact case.
