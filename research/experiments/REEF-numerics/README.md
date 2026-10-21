# REEF-numerics: known-result check, replay and refinement tools

Numerics lane of the Coexistence-Reef expedition. Mandate: `research/expeditions/2026-10-20-reef-launch.md`
at launch commit `51af137761512d66f7f73d4512e7bbc3b76f5b1f`; protocol v1 at `reef/coordinator` `5a6cce6`
(§9 owns the pass rules). This lane owns independent verdicts, not field code.

**Arithmetic caveat for every verdict here:** `alm_check` FFT is a separate implementation but uses the
same NumPy `rfft2`/`irfft2` arithmetic as `alm`, and is bitwise equal to it. Only `alm_check` direct
(real-space wrap correlation via `scipy.ndimage`, no FFT) is a different arithmetic route.

Environment: Python 3.13, NumPy 2.5.4, SciPy 1.18.1, `OMP/OPENBLAS/MKL_NUM_THREADS=1`, ≤ 2 simulation
processes. Built by `./scripts/bootstrap.sh`, which also cloned the pinned upstream
`Chakazul/Lenia @ adfc542939266de7f4bb7ebb552e8499701ee107` into `.refs/Lenia` (D-008).

## 1. Engine tests (2026-10-21, at 51af137)

`.venv/bin/python -m pytest -rs -q` → **105 passed, 0 skipped, 0 failed** (56 s). The upstream reference
was present, so the upstream-comparison tests (`tests/test_lenia.py` catalog tests and
`tests/replication/test_alm_check.py` upstream test) ran and passed rather than skipping. The Lane 2
trace comparison test also ran (its trace is on this branch).

## 2. S103 exact fixed point (C042) reproduced

| run | world | T | steps | initial sha256 | final sha256 | fixed |
|---|---|---|---|---|---|---|
| `S103-f66b8aa11f` | 128² | 10 | 10 000 | `a81efdac…2745` | `a81efdac…2745` | bitwise |
| `S103-3f198bd27e` | 128² | 40 | 20 000 | `a81efdac…2745` | `a81efdac…2745` | bitwise |
| `S103-9e8562d310` | **256²** | 10 | 10 000 | `1e9aa713…23be0` | `1e9aa713…23be0` | bitwise |

Full N256 hash: `1e9aa71324e5bc12a1fed999dfe9596e2eedf72a04161646409b6d787e823be0` (equals the REEF-M0
smoke). The N128 hash equals the original runs `S103-1d8c158cdd` / `S103-4982ff6f4d`. Traces in
`s103/traces/` (run IDs differ from the originals only because the code commit is hashed into them).

`s103/s103_check.py` → `s103/s103_check.json` repeats the test on all three routes at N128 and N256:
bitwise fixed for 20 steps on `alm`, `alm_check` FFT **and `alm_check` direct**. Growth margins: every
full cell has G ≥ +0.02762 and every empty cell G ≤ −0.12531 (FFT and direct agree to 2e-15). A
deterministic map with A₁ = A₀ bitwise is fixed for all later steps on that route.

## 3. Replay tool: `replay.py`

Takes a float64 state + REEF manifest (`REEF/manifest.schema.json`), checks the state's sha256 against
`inputs.initial_state_sha256` (or `--start-sha` for a window starting later), refuses a dirty tree,
and steps it on `alm`, `alm_check` FFT and `alm_check` direct, **each in a fresh process** (so the `alm`
route is also the clean-process exact-input replay). Writes per-tu float64 states (`<engine>.npz`,
not committed), `divergence.csv` (per tu, each route vs `alm`: bitwise flag, max/mean |ΔA|, mass
difference, support XOR at A > 0.01) and `replay.json` (one schema-shaped manifest per route, run IDs
`<base>-replay|-chkfft|-direct`, per-tu hashes).

```
python research/experiments/REEF-numerics/replay.py --manifest M.json --state A0.npy --tu 20 \
    --out OUT --run-id REEF-P2-E [--start-sha SHA] [--engines alm,check_fft,check_direct]
```

**Validation (20 tu, N256, coexistence rule, commit 3a12ffa):** `validation/replay-S00{1,3}/`.

| input | alm final sha256 | alm_check FFT | alm_check direct |
|---|---|---|---|
| S001 raw cells (`5cfb2443…`) | `28a3b09c11bafc52…` (= REEF-M0 smoke at 200 steps) | bitwise every tu | differs from tu 1; max \|ΔA\| ≤ 1.2e-12 over 20 tu, 5.2e-13 at tu 20 (= M0 smoke); support XOR 0; mass Δ ≤ 6e-15 R² |
| S103 (`1e9aa713…`) | `1e9aa713…` (fixed) | bitwise | bitwise |

S001 here is the raw catalog seed under the coexistence rule, an arithmetic test input, not the field
lane's settled glider and not a control.

## 4. Refinement variants: `make_variants.py`

From the t = 0 states of an encounter E and its controls G-alone, S-alone (same N), writes `T20`
(T = 20), `R26` (2×2 `np.kron`, R = 26, N doubled) and `N<big>` (default 512: one common roll puts an
all-zero band on the seam, then embeds at the centre, so separation, phase and lattice orientation are
unchanged) — each with its own E/G/S states and manifests (`status: "prepared"`, not a schema enum
value; nothing is simulated). Checks E = G + S before and after. Tested on a toy pair
(`validation/variants-toy/`, not an expedition geometry): superposition preserved in all three,
mass ratio 1/4/1.

Replaying each toy S-alone variant for 5 tu: T20 and N512 rings stay bitwise fixed on all three routes.

## 5. Finding: block-replicated S103 at R26 is not an exact fixed point

`s103/s103_r26_block.py` → `.json`/`.csv`. The kron seed (`db14953d…`) has 28 full cells with G < 0
and 25 empty cells with G > 0 (min G_full −0.408, max G_empty +0.399), so it is not a clip fixed point.
Over 300 tu at R26/T10/N512 it stays a compact non-moving body (centroid shift ≤ 0.12 cell) but never
freezes: in tu 200–300 max |ΔA| per tu is 0.024–0.063 and mass fluctuates 0.3784–0.3826 R². This is
consistent with C048's "settles static at 0.380599" at the class level and answers its open question
("whether those bodies are exact fixed points was not tested"): through 300 tu, no. OBSERVED, single
engine (alm), single seed method (block).

Consequence for the §9 R26 check: the R26 S-alone control is a fluctuating body, not a frozen one, so
ring tolerance and the interaction residual floor at R26 must come from its own controls/sham, and
"ring unchanged" cannot mean bitwise at R26.

## 6. Does GA stay GLIDER under the refinement settings? (lead request, 06:01Z)

`glider/glider_variants.py` on the field lane's `GA` (reef/field `5f21378`, state sha256 `982b7939…25f1`),
100 tu each, classes per 10-tu window (protocol §7 motion classes):

| setting | class (all 10 windows) | net speed R/tu | heading | mass R² |
|---|---|---|---|---|
| base T10 N256 | GLIDER | 0.548–0.549 | 72.3° | 0.486–0.488 |
| T20 N256 | GLIDER | 0.590–0.591 (+7.7%) | 72.1–72.3° | 0.482–0.485 (−0.8%) |
| N512 T10 (centred embed) | GLIDER | identical to base | 72.3° | identical to base |
| R26 kron N512 | GLIDER | 0.548–0.549 | 72.5–72.7° | 0.487–0.488 |

So the T20 check can compare phenotypes through at least 100 tu (unlike the earlier T40 STATIC
outcome); its glider is ~8% faster, consistent with Lane 3's timestep-fragile speed, so T20 encounter
geometry should be compared in its own controls' units. Single engine (alm). The `components` column
uses a quick seam-merge counter that is not the behavior lane's tracker; its counts > 1 are not evidence
of fragmentation.

## 7. §9 checks of the selected contrasts P2 and P3 (D-017)

Inputs: reef/field `91da893` runs `REEF-P2-E` (GA, b = +0.02 R) and `REEF-P3-E` (GA, b = +0.995 R),
their float64 checkpoints. Scorer: reef/behavior `4de401e` `score.py` (`EncounterRecorder` fed live,
every step, by `check_runner.py`). Ignition (D-017): E mass ≥ 2 × (G + S) and ≥ 5 bodies. Front:
r95 = 95th-percentile distance of E support (A > 0.01) from the ring centre; speed = least-squares
slope from ignition until r95 reaches 0.7 × (N/2)/R, plus sliding 5-tu slopes. Commands are in each
`checks/<run>/summary.json`; per-step series in `series.csv`; float64 checkpoints (every tu) are in
the project folder `reef-numerics/checks/<run>/checkpoints.npz`, not in git.
Matrix: [`checks/MATRIX.md`](checks/MATRIX.md) (`checks/make_matrix.py`).

**Arithmetic:** `alm_check` FFT is the same NumPy FFT arithmetic as alm. Only the direct window is a
different arithmetic route.

| check | P2 | P3 |
|---|---|---|
| clean-process exact-input replay (field `runner.py` at `fe4ba1c`, fresh process) | E/G/S final sha256 identical; all 159 checkpoints bitwise | same |
| alm_check FFT, 0–50 tu | bitwise at every 1-tu checkpoint (E, G, S) | same |
| alm_check direct, 3→25 tu from the saved t = 3 state (covers ignition) | FISSION; t_int 5.5, t_c 6.1, ignition 14.7 identical; E mass t20/t25 within 1e-12 rel; bodies 29/70 identical | FISSION; t_int 6.0, t_c 6.7, ignition 18.0 identical; same |
| T20 (own controls) | FISSION, t_c 5.6 (−0.5), **ignition 11.6 (−3.1)**, E mass t20 +62%, t25 +48%; front 0.378 vs 0.362 | FISSION, t_c 6.15 (−0.55), **ignition 15.9 (−2.1)**, mass +35%/+27%; front 0.321 vs 0.332 |
| R26 2×2 block, N512 (own controls) | scorer: CONTROL_FAILURE (S mass not constant, see §5); E ignites at **10.4 (−4.3)**, 95 bodies at t_c + 20, mass +41%/+32% | CONTROL_FAILURE (same reason); ignition **17.1 (−0.9)**, 60 bodies, mass +28%/+16% |
| N512, R13, same separation (own controls) | identical to N256 through 25 tu (class, times, masses, bodies) | same |

Direct-vs-alm divergence (`checks/direct_vs_alm.txt`): 0 at t = 3, ~1e-14 at contact, then grows
about ×30 per 5 tu after ignition (≈ 0.7 per tu): 4e-12 at t15, 1e-10 at t20, 6e-9 at t25 (P2), with
no support-cell change. Isolated glider differences stay < 1e-12. So the colony is sensitive to
round-off, as expected of a growing many-body system; extrapolated, cell-level details lose arithmetic
agreement around 50–60 tu, but aggregate observables agree to ~1e-10 through 25 tu.

Verdicts under the frozen §9 rules:
- Replay: PASS (bitwise). FFT: PASS (bitwise, not independent arithmetic). Direct: **PASS** for both.
- T20: **same class, quantitative FAIL** (t_c moves 0.5–0.55 tu, at or just past the 0.5 tu limit;
  masses differ ≫ 1% because ignition comes 2–3 tu earlier). The isolated controls stay in class
  (glider GLIDER, ring fixed). Ignition timing is NUMERICALLY_FRAGILE in T; the qualitative outcome
  (contact → fusion → expanding colony) is not.
- R26: the scorer's frozen S-control rule demands constant ring mass, which the R26 block ring never
  has (§5; S-alone mass spans 0.3759–0.3820, 1.6%, while staying one body). Per D-010 the R26 ring is
  judged against its own control: it stays one static body, and the encounter ignites into the same
  kind of colony (95 / 60 bodies at t_c + 20, mass ×30–40). So R26 gives the **same qualitative
  outcome but earlier ignition** (quantitative FAIL). Rows are being re-recorded with `--save-rows`
  (`checks/REEF-P{2,3}-E-R26-rows/`) so the behavior lane can re-score with an R26 ring rule.
- N512: **PASS**; N256 was not torus-affected through t_c + 20.

**Front speed in the big world (lead question).** N512 sliding 5-tu slopes of r95: P2 0.36 (15–20),
then 0.38–0.41 R/tu from 20 to 55 tu (r95 7 → 19 R); P3 0.34 (18–23), then 0.37–0.40 from 23 to
53 tu. The front settles to a roughly constant **≈ 0.39 R/tu** (±0.02) once past the first ~5 tu after
ignition, and only slows (0.3, then ~0) once r95 nears (N/2)/R = 19.7 R, i.e. when the colony meets
its own images. On N256 the same slow-down starts at r95 ≈ 10 R (= 9.8 R half-width) near 30 tu.
The from-ignition fit (0.33–0.36) includes the acceleration phase. The front speed is about 70% of the
glider speed (0.548). Single engine (alm) beyond 25 tu.
