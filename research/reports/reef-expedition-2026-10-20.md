# Coexistence-Reef expedition: what happens when the glider meets the ring

**Expedition:** authorized by Bobby 2026-10-20 (Pacific). Mandate [`../expeditions/2026-10-20-reef-launch.md`](../expeditions/2026-10-20-reef-launch.md) at launch commit `51af137761512d66f7f73d4512e7bbc3b76f5b1f`. Ran 2026-10-21 05:50Z–(see STATUS) UTC.
**Integration branch:** `reef/coordinator`, importing `reef/field`, `reef/numerics`, `reef/behavior` with full histories.
**Coordination files:** [`../experiments/REEF/PROTOCOL.md`](../experiments/REEF/PROTOCOL.md) (frozen before encounters; Gate A addendum §11), [`DECISIONS.md`](../experiments/REEF/DECISIONS.md) (D-001…), [`STATUS.md`](../experiments/REEF/STATUS.md).
**Status of this report:** finite-horizon evidence at one rule. Every encounter claim below is scoped to μ 0.155, σ 0.020, poly/poly, Euler + clip, float64, periodic torus, and to the windows stated. Nothing here has been merged to `main`.

## 1. Strongest result

**First contact between the settled coexistence-rule glider and S103 fuses them and ignites an expanding colony that covers the world.** It happened in every encounter we ran: 12 of 12 glider encounters (P1–P6, X1–X6) across transverse offsets b/R ∈ [−1.5, +1.5] and two glider snapshots, at N256, R13, T10. In every case the matched isolated controls stayed in class: the glider kept gliding (0.548 R/tu, 72.3°) and the ring stayed bitwise fixed.

The sequence is the same each time ([panel A](../experiments/REEF-behavior/exhibit/A-P2-main.png)):

1. **Kernel-range overlap** at t_kr ≈ 3.6–4.2 tu.
2. **Interaction onset**, measured as the encounter minus the sum of its two controls exceeding 1e-10 (≈ 770× the sham floor), at t_int 5.5–6.1 tu. That is 0.6–1.0 tu *before* visible support contact, as preregistered (Pr1, 12/12).
3. **Contact and fusion** at t_c 6.1–7.7 tu. The two bodies never separate again.
4. **Ignition.** The fused body grows and breaks up from inside into small static ring and dumbbell bodies (median ≈ 0.2 ΣA/R², about half an S103). An advancing front lays the bodies down, and behind it the interior freezes (P2: mean |ΔA| per tu within 4 R falls from 0.12 to 0.011). At the end of the scored window (t_c + 20 tu) there are 47–114 bodies and mass is 26–50× the controls. By 50 tu about 300 bodies cover the N256 torus (mass ≈ 81).

Under the classes frozen before any encounter, every run scores **FISSION**. A descriptive flag added afterwards (D-016), **PROLIFERATION**, says what that class understates. The fill fraction saturates at 0.22–0.24, just under the frozen FILL threshold of 0.25, because the colony is a sparse lattice.

**Independent checking (P2 head-on and P3 flank, chosen by the rule frozen in §8; matrix in [`REEF-numerics/checks/MATRIX.md`](../experiments/REEF-numerics/checks/MATRIX.md), [panel F](../experiments/REEF-behavior/exhibit/F-check-matrix.png)):**

| check | P2 | P3 | what it shows |
|---|---|---|---|
| clean-process replay | bitwise (159 checkpoints) | bitwise | reproducible |
| `alm_check` FFT | bitwise | bitwise | independent implementation, **same arithmetic** |
| `alm_check` direct, 3→25 tu | same class, t_int/t_c/ignition identical, mass within 1e-12 rel | same | **different arithmetic agrees**; divergence grows ~0.7/tu after ignition (6e-9 at 25 tu) |
| N512, R13, same separation | identical to N256 through 25 tu | identical | not a torus artifact inside the window |
| T20, own controls | FISSION; ignition 3.1 tu earlier, mass +48–62% | FISSION; ignition 2.1 tu earlier, mass +27–35%, t_c −0.55 | outcome survives; **timing and mass outside the frozen tolerance** |
| R26 (2×2 block, N512), own controls | FISSION + PROLIFERATION (111 bodies); ignition 4.3 tu earlier, mass +32–41% | FISSION (63 bodies); ignition 0.9 tu earlier, mass +16–28% | outcome survives, but against a ring that is itself relaxing at R26 (D-010, D-024, C048): a weaker check |

So the qualitative outcome, contact → fusion → world-covering colony, holds across arithmetic, world size, timestep and resolution. The *when* and *how much* do not: ignition time and colony mass are numerically fragile in T and R.

**Mechanism test (the most informative discovery runs).** Replacing the glider with a static, mass-matched Gaussian blob (0.487 ΣA/R², same gyradius) showed three things:

- **Placed where the glider is at t = 5.5 tu (X7, X8), 9–12 cells from the ring:** the blob evaporates in 1.4 tu without touching it. The ring returns bitwise, and the final world equals ring-alone bitwise. Nearby mass that decays does nothing.
- **Placed in contact, where the glider is at t_c (X9, X10):** the same ignition and colony (79–87 bodies at the window end).
- **Dose at the contact position:** 0.5× (0.24 ΣA/R², X11) does not ignite, and the ring returns bitwise. 0.75× (0.37, X12) and 1.0× (0.49) ignite. The glider carries 0.49.

The ring is the excitable partner. **The glider is a delivery vehicle for enough mass in contact, not a necessary ingredient.** This agrees with the Night 0 S103 dossier: a frontal Gaussian addition (I003) of 0.10 returns S103, while ≥ 0.30 "fills the world". That was a different shape and placement, so it is consistent with our bracket, not directly comparable.

**Novelty: not novel as a phenomenon.** Chan 2019 §3.5.5 (pdf p. 29) lists "Detonation, the resultant mass explodes into infinite growth" among Orbium collision outcomes. §3.3.1 (pdf p. 21) describes Class 2 "regional, periodic immobile patterns (e.g. Circium)". In-repo, S103's I003 fill and HR-009's world-filling S102 copy at this same rule were already known. What is new is narrow and OBSERVED/checked at this rule: the specific trigger (first contact of the settled coexistence glider with S103), the dose bracket for passive mass in contact, and the front-laid frozen lattice. See [`REEF-behavior/LITERATURE.md`](../experiments/REEF-behavior/LITERATURE.md), with a citation-existence check for every source.

## 2. Best failure

**Our own predictions.** Before any encounter, the lead predicted that head-on contact would most likely end in glider death or capture with the ring surviving (Pr2, 60%), and that |b| = 1 R would be a grazing pass or deflection (Pr3). Both failed outright: no run ended in death, capture, deflection or a pass. Everything ignited, even at the widest allowed offset of 1.5 R. The protocol's outcome vocabulary (PASS, DEFLECT, TEMP_BIND, CAPTURE, …) was built for particle-like collisions. The true outcome was a phase change of the whole world, and the frozen classes could name it only as FISSION. We kept the frozen labels and added PROLIFERATION openly, after the fact.

Other recorded failures and repairs:
- The field lane's preregistered "one component" glider acceptance failed: the isolated glider sheds single-cell specks in about 13% of steps at every threshold. Debris rule: components < 0.005 ΣA/R² (D-012).
- The first 200-tu settle assessment failed on heading drift (1.55°), so the settle took the one allowed extension to 500 tu.
- No intrinsic glider period was found, so GA and GB are elapsed-time snapshots 0.5 tu apart, not phases.
- The R26 check needed a ruling (D-024). A mass band the lead had paraphrased, never frozen, would have marked its control as failed during the ring's own pre-contact relaxation.
- X9–X11 needed one placement repair: one blob-tail cell zeroed so the encounter equals blob plus ring exactly (D-021).

## 3. Remaining disagreement and open ends

- **How strong is R26?** The behavior lane's mass-band variant scores R26 as CONTROL_FAILURE. The primary rule (one static body) scores FISSION. The disagreement is about whether a ring that is not a fixed point at R26 is a fair control. We report both labels and count R26 as a weaker check, not a clean pass.
- **Timing.** Ignition time is fragile in T and R (T20 −2.1 to −3.1 tu, R26 −0.9 to −4.3 tu). Any statement about *when* the reef ignites is NUMERICALLY_FRAGILE.
- **The transition in offset lies outside the mandate's range.** No glancing pass was found up to |b| = 1.5 R. Wider offsets were not run.
- **Mechanism.** The front-laid frozen lattice resembles depinning of a localized pattern in a bistable system (Knobloch 2015) and pushed fronts (van Saarloos 2003). These are testable analogues only, cited from abstracts. Self-replication is *not* supported: the interior freezes, and no division was seen.
- **Horizon.** Beyond about 25 tu, only alm results exist for the colony, and at N256 the colony meets its own periodic images at about 27–30 tu. At N512 the front holds at ≈ 0.39 ± 0.02 R/tu after about 5 tu of acceleration, then slows near the torus half-width.

## 4. Next three experiments

1. **Dose ladder and shape at the contact position.** Bisect 0.24–0.37 ΣA/R² and vary blob width at fixed mass. Is the trigger total mass, peak amplitude, or overlap with the ring's kernel shell? This is the cleanest test of the "excitable ring" interpretation.
2. **Empty-world nucleation threshold without S103.** Does a large enough compact mass ignite the colony on its own, so that the empty state is merely metastable? The blob-alone controls evaporated at 0.49, so is there any dose that ignites alone? This separates "S103 is the nucleus" from "the rule's empty state is metastable".
3. **Front law at N1024 with the direct route over a short window.** Measure front speed and lattice spacing away from torus images, and test whether ignition timing converges as T → ∞ (T20, T40, T80 with matched controls). T40 previously made the isolated glider STATIC, so that refinement may change the comparison itself.

## 5. Shortest reproduction

```bash
git checkout reef/coordinator      # or the integration PR head
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]' scipy
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd research/experiments/REEF-field   # field lane (each step was run from the commit in its registry)
python settle.py && python controls.py && python torus_margin.py 256 && python torus_margin.py 512
python jobs.py plan && python jobs.py run --protocol-addendum 3c3fdc4b12cb064061d899b2a6e42290ceb452c9          # P1–P6
python discovery.py plan && python discovery.py run --protocol-addendum a0698db9b26547ed8692c49fcca073f81832e666  # X1–X8
python discovery.py plan-reserve && python discovery.py run --jobs jobs-reserve.json --protocol-addendum 2a1c60ae5b32ea93090d94da36a91657a8577f6d  # X9–X11
python discovery.py plan-x12 && python discovery.py run --jobs jobs-x12.json --protocol-addendum e8bc4b0a1eb57b5bb3b68cb1a09ee95fe26214c9         # X12
cd -   # behavior lane: tracker tests and scoring
PYTHONPATH=src python -m pytest -q research/experiments/REEF-behavior/
PYTHONPATH=src python research/experiments/REEF-behavior/score.py research/experiments/REEF-field/runs/REEF-P2-E --out P2.json  # needs frames.npz: regenerated by the run above, or copied from the project folder reef-field/runs/
# numerics lane: replay and §9 checks, REEF-numerics/README.md §7
```

The lane READMEs carry the authoritative commands and every input hash: [`REEF-field/README.md`](../experiments/REEF-field/README.md) (26-run registry), [`REEF-behavior/README.md`](../experiments/REEF-behavior/README.md), [`REEF-numerics/README.md`](../experiments/REEF-numerics/README.md). Per-step frames are kept out of git (≈ 1.4 MB per run), and their sha256 is in each manifest.

## 6. Ledger changes

Added C052–C055. Dated, history-preserving amendments to C038 (coexistence means separate worlds) and C041 (later L6-008 and HR-009c evidence; on-gap wording). No earlier line was rewritten and no existing status changed.
