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
