# Reference dossier (Lane 1, Night 0)

Author: Lane 1, Reference Naturalist. Date: 2026-10-07.
Upstream reference: `Chakazul/Lenia` at `adfc542939266de7f4bb7ebb552e8499701ee107`
(2022-03-16, "upload LeniaF.py"), checked out under `.refs/Lenia/`.
Baseline specimen dossier: [`research/specimens/S001-orbium.md`](../specimens/S001-orbium.md).

This dossier keeps three kinds of statement apart, and every section says which it is using:

- **Paper says.** Taken from the Lenia paper (Chan 2019, *Complex Systems* 28(3), arXiv:1812.05433v3).
  Page and equation numbers refer to the arXiv v3 PDF.
- **Author exposition says.** The equations Bert Chan typeset in the reference web app
  (`JavaScript/Lenia.html`, lines ~455–700).
- **Implementation does.** What `Python/LeniaND.py` actually computes, with line numbers. Unless
  marked otherwise, line references are to that file.

## 0. Sources

The first version of this dossier was written without the paper, because this container's
network policy blocks arXiv and its mirrors. Bobby uploaded arXiv:1812.05433v3 on 2026-10-07, and
§1–§5 have since been checked against it. Paper-side statements now cite the PDF directly. The
check confirmed the inferred kn/gn story (§3.2) and added a fifth Orbium rule to §3.1: the paper's
own experiments use σ = 0.016 with exponential core functions.

## 1. Canonical update rule

### Paper says (§2.1.2–2.1.7, Eqs. 5–16, pp. 6–8)

- Discrete Lenia: Δx = 1/R, Δt = 1/T, Δp = 1/P. The neighbourhood is the closed discrete ball
  ‖x‖₂ ≤ R, normalised to the unit ball B₁[0] (Eq. 5).
- Potential: U = K ∗ A = Σ_n K(n) A(x+n) Δx² (Eq. 7). Growth: G = G(U) (Eq. 8). Update:
  A ← clip(A + Δt·G, 0, 1) (Eq. 9).
- Kernel core K_C (Eq. 10), listed **exponential first**: exp(α − α/(4r(1−r))), α = 4; then
  polynomial (4r(1−r))^α, α = 4; then rectangular 1_[1/4,3/4](r).
- Kernel shell K_S(r; β) = β_⌊Br⌋ · K_C(Br mod 1) (Eq. 11). Normalisation: K(n) = K_S(‖n‖)/|K_S| with
  |K_S| = Σ_N K_S Δx² (Eq. 12), so K ∗ A ∈ [0, 1]. The Δx² factors cancel, so this equals dividing
  the shell by its plain grid sum.
- Growth mapping (Eq. 13), again **exponential first**: 2·exp(−(u−μ)²/(2σ²)) − 1; then polynomial
  2·1_[μ±3σ](u)·(1 − (u−μ)²/(9σ²))^α − 1, α = 4; then rectangular 2·1_[μ±σ](u) − 1.
- Pseudocode (§2.2.1, p. 10): the kernel is built over the whole grid, divided by its sum and
  FFT'd. Each step is `clip(world + dt*growth_mapping(fftshift(real(ifft(K̂·Â)))), 0, 1)`. The
  pseudocode has **no explicit r < 1 cutoff**; `beta[floor(Br)]` would index out of range outside
  the unit disc. The implementation adds the cutoff.
- FFT convolution "automatically produces a periodic boundary condition" (p. 9).
- **The paper's own experiments used exponential/exponential at double precision** (§2.2.4,
  p. 11: "Kernel core and growth mapping: exponential").
- Euler framing (§3.1.2, Eqs. 19–20): DL is the Euler method for the ODE dA/dt = G(K∗A) clipped to
  [−A/dt, (1−A)/dt]. As T grows, structure measures (m, r_m) fall and dynamics measures
  (g, d_gm, s_m) rise towards a continuum limit (Fig. 7c–d).
- Scale invariance holds for R > 12 (§3.1.1). For Orbium, R ∈ {9…55} at T = 10 leaves m, g, r_m,
  d_gm and s_m constant (Fig. 7a–b).
- Core functions "usually alter the textures of a pattern but not its overall structure and
  dynamics". Orbium switched to polynomial shows "no visible effect" (§3.1.3, Fig. 6b).

### Author exposition says (`Lenia.html`)

- Space: the kernel radius is 1 unit, split into `R` cells, so Δx = 1/R. Time: 1 unit is split into
  `T` steps, so Δt = 1/T. The state is f(x) ∈ [0, 1].
- Update: Δf(x) = d(k ∗ f(x)) · Δt, where d is called the "delta" (later "growth") function.
- Neighbour sum: k ∗ f(x) = (1/N) Σ_{|u|≤1} k(u) f(x+u) with N = Σ_{|u|≤1} k(u). So the kernel is
  normalised to unit sum **on the discrete grid**, not as a continuous integral.
- Kernel with B rings ("layers"): k(u) = β_i · c(B·r − (i−1)) for (i−1)/B ≤ r ≤ i/B, r = |u|.
- Kernel core c(r), with q = 4r(1−r):
  - "Gaussian bump" (`bump4`): c(r) = exp(α(1 − 1/q)), α = 4;
  - "polynomial" (`quad4`): c(r) = q^α, α = 4;
  - plus trapezoid, step (SmoothLife) and "life" variants.
- Growth (delta) function d(n), with ℓ = |n − μ|:
  - Gaussian (`gaus`): 2·exp(−ℓ²/(2σ²)) − 1;
  - polynomial (`quad4`): 2·(1 − ℓ²/(9σ²))^α − 1 if ℓ ≤ 3σ, else −1;
  - plus trapezoid and step variants.

### Implementation does (`LeniaND.py`, 2-D, default flags)

```
A_{t+1} = clip( A_t + (1/T) · G( K ∗ A_t ; m, s ), 0, 1 )
```

- **Convolution** (`calc_once`, l.364–406; `calc_kernel`, l.408–434). The kernel is built on the
  full world grid with coordinates X = (i − MID)/R. It is normalised by its discrete sum, then
  applied by FFT: `potential = fftshift(real(ifftn(fftn(K/ΣK) · fftn(A))))`. Boundaries are
  therefore **periodic (torus)**.
- **Kernel shell** (`kernel_shell`, l.312–319): `K(r) = (r<1) · core(min(B·r mod 1, 1)) · b[min(floor(B·r), B−1)]`
  with B = len(b). The support is strictly r < 1.
- **Cores** (l.272–277): index 0 is `(4r(1−r))^4` (polynomial), 1 is `exp(4 − 1/(r(1−r)))`
  (exponential bump), 2 is step 1/4…3/4, and 3 is the Life staircase. Index = `kn − 1`.
- **Growth** (l.278–282): index 0 is `max(0, 1 − (n−m)²/(9s²))^4·2 − 1` (polynomial), 1 is
  `exp(−(n−m)²/(2s²))·2 − 1` (Gaussian), and 2 is step. Index = `gn − 1`.
- **Integrator.** Explicit Euler with hard clip. The alternatives are all off by default:
  - `is_soft_clip` (log-sum-exp clip with k = 1/dt);
  - `param_P` (quantise states to P levels);
  - `add_noise`;
  - `mask_rate` (random asynchronous update);
  - `is_multi_step` (Adams–Bashforth-2). **This is dead code:** the guard
    `if self.is_multi_step and self.field_old:` (l.381) can never become true, because `field_old`
    starts as `None` and is only ever assigned inside that same branch. Upstream therefore
    *always* integrates with Euler.
- **Precision.** The CPU path uses `np.fft` in float64/complex128. When a reikna GPU context
  compiles (l.333–347), `fftn`/`ifftn`/`fftshift` instead run in **complex64/float32**. Upstream
  "the reference" therefore has two numerically different execution paths, chosen silently by the
  hardware.
- **Grid defaults** (l.18–53). The window is 2^9 = 512 px with 4-px cells (`-p2`), so the world is
  **128 × 128**. The default kernel radius `DEF_R = 2^(S−6)·D·5` gives **20** at S = 7, D = 2.

### Agreement check

Paper, exposition and implementation agree on the rule shape: discrete kernel normalisation, ring
shell with β peaks, both core and growth families, Euler step of size 1/T, clip to [0, 1], and
periodic FFT boundaries. They differ in two places. The first is the **numbering of the families**
(§3.2). The second is the **default family**: the paper ran exponential, while the Python catalog
executes polynomial. A minor third difference is that the paper's neighbourhood is the closed
ball ‖n‖ ≤ R and the implementation's is r < 1. It does not matter, because both cores vanish at
r = 1.

## 2. Parameter conventions and catalog format

| Symbol (paper/JS) | `animals.json` key | Meaning | Implementation notes |
| --- | --- | --- | --- |
| R | `R` | kernel radius in cells | int; also the unit of length for all statistics |
| T | `T` | steps per unit time; Δt = 1/T | int |
| μ | `m` | growth centre | float |
| σ | `s` | growth width | float |
| β | `b` | ring peak heights | **string** of comma-separated fractions, e.g. `"1"`, `"1,2/3"`; parsed with `Fraction` (`Board.st2fracs`, l.198) |
| core | `kn` | kernel core, 1-based | `kernel_core[kn−1]`; see §3.2 |
| growth | `gn` | growth mapping, 1-based | `growth_func[gn−1]`; see §3.2 |

The cell RLE (`Board.ch2val`, `rle2arr`, l.107–192) works as follows:

- `.`/`b` = 0; `A`..`X` = 1..24; two-letter `pA`..`yO` = 25..255 via `(c0−'p')·24 + (c1−'A'+25)`;
  `o` = 255.
- A decimal prefix repeats the next token. `$` ends a row (a count before `$` inserts empty rows),
  and `!` ends the pattern.
- Values are **level/255**, so every catalog state is exactly representable as integers 0..255.
- Rows are axis 0 (y, downward) and characters are axis 1 (x). Short rows are right-padded with
  zeros.

Our decoder (`research/specimens/S001-orbium/reconstruct.py:rle2int`) was compared with upstream's
own `Board.rle2arr` (extracted with `ast`) on **all 548 2-D catalog entries: 0 mismatches**.

Placement (`Board.add`, l.204–221) centres the pattern in the world and copies only cells
> 1e−10, overwriting.

**Catalog R vs GUI R.** When the GUI loads an animal (`load_part`, l.1149–1197, `is_use_part_R=False`),
it keeps the *world's* R (20 by default) and rescales the pattern by `scipy.ndimage.zoom(R_world/R_animal, order=0)`
(nearest neighbour, l.231–237). So the creature a user sees on launching `LeniaND.py` is a 31 × 31
nearest-neighbour blow-up of the 20 × 20 catalog state, run at R = 20. Only codes prefixed with `~`
force the catalog R. For ALM, "the catalog state" means the stored array at the stored R. See
S001 for evidence that both versions survive with matching normalised mass.

## 3. Disputed semantics (resolve by experiment, not by reading)

### 3.1 Which Orbium rule is canonical? There are five on record

The same Orbium unicaudatus cells appear under different rules in different upstream sources, and the paper adds a rule of its own:

| Source (pinned commit) | Core / growth | μ | σ | R, T | Cells |
| --- | --- | --- | --- | --- | --- |
| **Paper** Figs. 6–7 (arXiv v3) | **exponential/exponential** (§2.2.4) | 0.15 | **0.016** | Fig. 6: R = 185, T = 10; Fig. 7: R = 9…55 or T = 4…2560 | not published |
| `Python/animals.json` (LeniaND, 2020), entry `O2u` | `kn=1, gn=1` → **polynomial/polynomial** as executed | 0.15 | **0.015** | 13, 10 | 20 × 20 RLE |
| `Python/old/animals.json` (Lenia.py, 2018–19), entry `O2(a)` | no kn/gn; old code defaults to kn = gn = 1 → polynomial as executed | 0.15 | **0.017** | 13, 10 | byte-identical RLE to `O2u` (checked) |
| `JavaScript/Lenia-LifeForms.js`, entry `O2(a)` | explicit `k=bump4; d=gaus` → **exponential/Gaussian** | 0.15 | **0.017** | 13, 10 | different encoding ("zip"), not compared |
| `Jupyter/Lenia.ipynb`, `R/Lenia.Rmd` (O. *bicaudatus*, not unicaudatus) | type 0 = polynomial/polynomial | 0.15 | 0.014 | 13, dt = 0.1 | inline float table |

**Our reproduction:** every (core, σ) combination recorded above, the paper's exp/σ = 0.016
included, keeps O2u alive and gliding for 5000 steps on
a 128² torus. Mass and speed shift monotonically with σ (S001 §Rule-variant sweep). Orbium does not
force a choice. The choice still changes every number Lane 4/5 will report, so ALM should fix one
rule and record it with every run.

**Recommendation:** use the `LeniaND.py` catalog entry **as executed by `LeniaND.py`**, i.e.
polynomial core, polynomial growth, μ = 0.15, σ = 0.015, R = 13, T = 10, β = [1]. It is the newest
catalog, the startup creature of the program (`ANIMAL_KEY_LIST['1'] = 'O2u'`, l.2017), and the
only one whose execution semantics we can reproduce bit-for-bit against upstream code (S001
§Cross-check). The paper's published state is not available, so the catalog cells are still the
only exact Orbium starting state. The paper's rule (exponential/exponential, σ = 0.016) applied to
those cells is the natural second rule for Lane 3/7 robustness checks, because it connects our
numbers to the paper's Figs. 6–7.

### 3.2 `kn`/`gn` numbering: the labels disagree with the code

- **Implementation does:** `kn = 1` → `kernel_core[0]` = **polynomial**; `kn = 2` → exponential.
  The same holds for `gn`.
- **The program's own UI label says the opposite.** `get_value_text` (l.2308–2309) prints
  `["Exponential","Polynomial",...][kn−1]`, so a user sees "Exponential" while the polynomial is
  running.
- **History:** in commit `1538c33` ("Update Lenia.py to match the paper") the label list was
  swapped from `["Polynomial","Exponential",...]`, which matched the code, to
  `["Exponential","Polynomial",...]`. The lambda dictionaries were not reordered.
- **Paper says:** Eqs. 10 and 13 list exponential first, and §2.2.4 states the paper's runs used
  exponential/exponential. That **confirms** the reading. In paper order, "first family" means
  exponential, while the catalog's `kn = 1` executes polynomial. The paper does not use `kn`/`gn`
  numbers itself.
- **Consequence:** any ALM code that maps `kn = 1` → exponential by reading the paper or the UI
  will silently run a different rule from upstream. Lane 2 should key families by name
  (`poly`/`exp`), not by number, and should record the name in every trace.

### 3.3 Mass "oscillation" of Orbium is lattice aliasing, not physiology (conjecture with support)

See S001 §Lattice-heading observation. The dominant mass period equals the time to cross one grid
column or row at the creature's heading. Rotating the start state changes the heading, and the
period and amplitude move with it. Lane 5 should not report Orbium's mass period as an intrinsic
oscillation without this control.

## 4. What existing upstream statistics measure

**Paper says (§2.4.2, pp. 13–14).** The measures are defined over A and the positive-growth field
G|G>0, with integrals ∫·dx (dx² = 1/R² in DL):

- mass m = ∫A [mg];
- volume V_m = ∫_{A>0} dx [mm²]; density ρ_m = m/V_m;
- growth g = ∫_{G>0} G [mg/s];
- centroid x̄_m; growth centre x̄_g; growth-centroid distance d_gm = |x̄_g − x̄_m| [mm];
- linear speed s_m = |dx̄_m/dt| [mm/s]; angular speed ω_m = d/dt arg(dx̄_m/dt) [**rad**/s];
- mass asymmetry m_Δ = ∫_{c>0}A − ∫_{c<0}A with c = dx̄_m × (x − x̄_m);
- angular mass I_m = ∫A (x − x̄_m)²; gyradius r_m = √(I_m/m);
- Hu/Flusser moment invariants.

The paper lists "degree of chaos (e.g. Lyapunov exponent, attractor dimension)" only as a
**meta-measure** over time series, not as a per-step statistic. Survival vocabulary (§2.3.2,
§3.5.4): a lifeform dies by **explosion** (mass expands without bound) or **evaporation** (mass
shrinks away). Persistence classes (§4.2.1) are transient, quasi-stable, stable, metastable,
chaotic and Markovian.

**Implementation does** (below). It matches the paper for m, g, d_gm, s_m, m_Δ and r_m, up to the
R² normalisation. It reports ω in degrees, not radians. It has no volume, density or moment
invariants. Its "Lyapunov exponent" is not the paper's meta-measure.

`Analyzer` (l.441–823) is run every step after `center_world()` (l.2489–2492). Units: length in
kernel radii ("mm"), time in T-step units ("s"), mass in "mg" = Σ cell value / R².

| Key | UI name | Implementation does | Caveats |
| --- | --- | --- | --- |
| `m` | Mass | ΣA / R² | normalised, so it is comparable across R |
| `g` | Growth | Σ max(G, 0) / R², G = growth-field value (not ΔA) | counts only positive growth, before clipping |
| `r` | Gyradius | √(Σ A·‖x − x̄‖² / ΣA), x in R units | centroid is **non-periodic**: valid only because the world is recentred every step |
| `d` | Mass-growth distance | ‖x̄_mass − x̄_growth‖ (R units) | growth centroid uses max(G, 0) |
| `s` | Speed | ‖Δx̄‖ · T per step, after undoing the recentring roll | R units per time unit |
| `w` | Angular speed | Δ(heading of Δx̄) · T, wrapped to ±180°, deg/time | forced to 0 for gen ≤ 2 |
| `m_a` | Mass asymmetry | (mass right − mass left of the line through last→current centroid) / R² | 2-D only; sign depends on y-down image coordinates |
| `x`, `y` | Position | centroid · R + accumulated integer shift (cells); y is sign-flipped | |
| `l` | "Lyapunov exponent" | running mean of **log \|Σ(A_new − A)/dt\|** | **not a Lyapunov exponent.** It is the log of net mass change rate, averaged from gen 1. Do not cite it as chaos evidence |
| `k`, `w_k` | Rotational symmetry / speed | argmax over k ≥ 2 of an EMA of polar-FFT power of A around the world centre; phase drift of that mode | **off by default** (`is_calc_symmetry = False`); polar sampling is nearest-pixel |
| PSD | power spectrum | Welch/periodogram of a stat series, nfft = 512, fs = T | **off by default** (`is_calc_psd = False`) |
| recurrence plot | | thresholded distance matrix of the stat series | display only |

Bookkeeping that matters for ALM:

- **Recentring.** `center_world` rolls the world by `int(x̄·R)` cells **every step**, whatever
  the auto-centre display flag says. This is exact on a torus (dynamics unchanged). It keeps the
  non-periodic centroid valid.
- **Upstream's own survival criterion.** The search mode (`do_search`, l.1314–1336) treats a run
  as **dead** if mass < 1e−10 (`is_empty`). It treats a run as **exploded** if any non-zero cell
  touches the outermost rows/columns of the (recentred) world (`is_full`, l.596–601). A run
  succeeds if neither happens by **t = 25 time units** (250 steps at T = 10). This criterion has
  no shape or locomotion test, and a mass-filling "full" state also counts as failure. It is a
  useful precedent for Lane 4, and too weak to serve as ALM's recovery definition.
- **Stats segments.** Series are trimmed to 64·⌈T/10⌉ samples for the first 128·⌈T/10⌉ gens and
  512·⌈T/10⌉ after that (`add_stats`, l.789–809). Stats on screen are windowed, not whole-run.
- The **JS app** has a different, richer instrument panel: growth volume, growth density,
  growth-centroid speed and rotation, moment-based shape. None of it is in the Python statistics.

## 5. Taxonomy and provenance (avoid "rediscovering")

- `Python/animals.json` (sha256 `09cf0a83…a848d206`) holds **614 rows**: **548 specimens** and
  **66 taxon headers** (`code` starting with `>`, level digit after it). The hierarchy is
  class → order → family → …. The classes are **Exokernel, Mesokernel, Endokernel**. The families
  are Orbidae (O), Scutidae (S), Pterifera (P), Helicidae (H), Circidae (C), Echinidae (E),
  Geminidae (G), Ctenidae (Ct), Uridae (U), Kronidae (K), Quadridae (Q), Volvidae (V), Dentidae
  (D), Radiidae (R), Bullidae (B), Lapillidae (L), Folidae (F), Amoebidae (A), Tubiformes (T),
  plus SmoothLife and Game-of-Life emulations (`kn = 3/4`).
- Rules in the catalog: `(kn, gn)` = (1, 1) for 523 entries, (4, 3) for 16 (Life), (2, 2) for 5,
  and a handful of others. R values cluster at 27, 13, 18, 36 and 10.
- Codes. **Paper says** (§3.2.4) the form is "BGUs": rank B, genus/family initial G, number of
  units U, species initial s. In the catalog, the leading digit equals `len(b)` in about 90 % of
  entries; when the digit is absent, rank is 1. A `:n` suffix
  selects the n-th entry sharing a code (`get_animal_id`, l.1115–1123).
- Other upstream catalogs: `Python/found/*.json` (search results by rank), `animals3D.json`,
  `animals4D.json`, `old/animals.json`, and the JS `Lenia-LifeForms.js`. Multi-kernel and
  multi-channel species (`LeniaNDK.py`, `LeniaNDKC.py`) and `LeniaF.py` are **out of Night-0
  scope**.
- **Before calling any candidate "uncatalogued"**, Lane 6/7 should:
  1. find catalog entries with the same `(kn, gn, len(b))`, nearby `m, s`, and R scaled out;
  2. run them under the candidate's rule;
  3. compare normalised mass, gyradius, speed and symmetry.

  A name lookup is not enough, because the catalog lists the same cells under several rules (§3.1).

## 6. Hand-offs

- **Lane 2 (simulator):** reproduce `reconstruct.py:step` semantics: periodic FFT convolution,
  kernel normalised by discrete sum, strict r < 1, Euler + hard clip, float64. Key core/growth by
  name. Record rule, R, T, μ, σ, β, grid size, dtype and catalog sha256 in every trace.
- **Lane 3 (red team):** the cheapest distinct execution path is upstream's own `Automaton`, which
  `xcheck_upstream.py` already drives headless. Upstream's GPU path is float32 and worth one
  comparison run. Resolution probe: R = 13 native vs the GUI's R = 20 nearest-neighbour blow-up
  (S001).
- **Lane 4 (disturbance):** upstream's survival test is mass > 0, no border contact and t ≥ 25.
  Use it as a lower bar only.
- **Lane 5 (morphometrics):** the "Lyapunov" stat is mislabelled (§4), and Orbium's mass period is
  heading-dependent lattice aliasing (§3.3).
- **Coordinator / claims ledger:** proposed entries are listed at the end of S001. Lane 1 has not
  edited `research/claims.md`.
