# HR-009: hostile review of L6-007 / L6-008 (PR #27), pre-registered

Lane 7, Night 1, 2026-10-08. **Committed before any HR-009 run.** It uses Lane 6's engine
(`L6-field/field.py`) and helpers unchanged, at PR #27 head `3ccb804`.

## E1. Is the S102 death time a property of the rule, or of the floating-point trajectory?

L6-f names "the unperturbed S102 seed dies at step 39 799" as the strongest result for
replication. If the circler is chaotic, a perturbation at the level of FFT rounding changes the
death step. A replication on a different FFT library or machine would then not reproduce the
step. Only the lifetime *distribution* would be a property of the rule.

Runs: primary rule (μ 0.155, σ 0.020, R 13, T 10, 128²), horizon 5000 tu. Seed plus δ·ξ on the
dilated support, as in L6-007 Part A. δ ∈ {1e-14, 1e-12, 1e-10}, 8 replicates each
(rng `default_rng(9000 + 100·i_δ + k)`). Plus the unperturbed seed, as a check that this
machine reproduces step 39 799. The separation ‖A_δ − A_0‖ is recorded every 10 steps.

- **E1-P1 (chaotic).** At δ = 1e-12, the death steps of the 8 replicates span more than 1000
  steps, or at least one replicate is alive at 5000 tu. Then the death step is not replicable
  across implementations, and L6-f's replication target must be a distribution.
- **E1-P2 (not chaotic).** All 8 δ = 1e-12 replicates die within ±10 steps of 39 799. Then the
  death step is a robust property of the rule, and the replication target stands.
- The finite-time growth rate of the separation (log-linear fit while it is below 1e-3) is
  reported for each δ.

## E2. Is the I003 drag-down coupling, or the split cutting the pulse in half?

In L6-008 the I003 pulse is centred 1 R ahead of the pair centroid, which falls in the gap
between the partners. The edit is applied before the split. So each partner alone receives only
the half of the Gaussian on its side, truncated at ℓ = 0. In the pair world, each partner sits
within kernel range of the *whole* pulse. The independence prediction therefore compares a pair
exposed to the full pulse with halves exposed to half of it.

Runs: L6-008 settings (S001 rule, S101, warm-up 3000 steps, phases 0–4, 300 tu horizon, last
100 tu window, `units()` as in L6-008). For I003 at s = 0.1, …, 1.0, each undisturbed half is run
alone **with the full pulse added**: clip(half + G, 0, 1), where G is the same Gaussian L6-008
adds.

- **E2-P1 (pulse artefact).** At s = 0.2–0.4, the full-pulse halves die or degrade in at least
  8 of the 10 pair-world drag-down runs (with n_full = n_port_full + n_stb_full ≤ n_pair). Then
  L6-d's drag-down is explained by exposure, and coupling is not shown.
- **E2-P2 (coupling survives).** At s = 0.2–0.4, the full-pulse halves both survive (n = 1 + 1)
  in at least 8 of those 10 runs. Then even generous exposure leaves the pair more fragile than
  its partners, and L6-d stands.
- Anything in between is reported as INCONCLUSIVE. Coupling would then sit between the two
  baselines.

Outputs: `e1.csv`, `e2.csv`, written by `hr009.py`.
