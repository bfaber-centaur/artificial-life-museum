# References

Deduplicated bibliography for the **Prior literature** fields in [`claims.md`](claims.md).
The claims archivist (Lane 0) maintains it. Each entry gives:

- a short key;
- a stable public link;
- the version that was read and how it was obtained;
- the claims that cite it.

Relationship classes and the rules for using them are in `claims.md`, under "Literature
provenance".

## Evidence grades

Every locator in `claims.md` carries one of three grades:

| Grade | Meaning |
| --- | --- |
| *full text* | Read in the paper itself, at the version named below. Section, figure and page are checked. |
| *code* | Checked in the authors' public code at the commit named below. This supports statements about the rule and methods only, never the paper's results. |
| *excerpt* | Seen only in web-search excerpts because the paper could not be opened. The locator and wording are unverified. |

Downloaded copies are kept out of git in `.refs/papers/`, which is ignored through `.refs/`.
Readers should use the public links.

## Retrieval log

### 2026-10-07 verification pass (archivist; requested by Bobby)

**Full text obtained:**

| Source | Version | Obtained from | Local copy | Status |
| --- | --- | --- | --- | --- |
| Chan (2019) | arXiv 1812.05433**v3** (stamped 4 May 2019; pdfTeX build 7 May 2019; 49 pp.) | PDF supplied with the Night 0 charter (project file `uploads/hearth/264e3c61-…`) | `.refs/papers/chan2019-arxiv1812.05433v3.pdf` | Read for every cited section; Fig. 9 also inspected as an image |

**Code obtained** (`git clone` over HTTPS works):

| Source | Repository | Commit | Local copy |
| --- | --- | --- | --- |
| Cool et al. (2026) | [jessescool/lenia-umwelt](https://github.com/jessescool/lenia-umwelt) | `58e8903` (2026-07-26) | `.refs/papers/src-lenia-umwelt-jessescool/` |
| Davis (2022/2024) | [riveSunder/DisContinuous](https://github.com/riveSunder/DisContinuous) | `53809de` (2023-07-29) | `.refs/papers/src-DisContinuous-rivesunder/` |
| Davis (2022/2024) | [riveSunder/yuca](https://github.com/riveSunder/yuca) | `ab59bff` (2026-08-28) | `.refs/papers/src-yuca-rivesunder/` |

**Blocked.** Each host was tried once. `curl` through the environment proxy returned
`CONNECT tunnel failed, response 403`, and WebFetch returned `EGRESS_BLOCKED`. The blocked hosts:

- arXiv: `arxiv.org` (abs and pdf), `export.arxiv.org`, `ar5iv.labs.arxiv.org`.
- Publishers: `content.wolfram.com` (Complex Systems PDF), `direct.mit.edu`, `doi.org`,
  `pmc.ncbi.nlm.nih.gov`, `europepmc`.
- Mirrors and aggregators: `pdfs.semanticscholar.org`, `scholar.archive.org`, `zenodo.org`,
  `core.ac.uk`, `hal.science`, `researchgate.net`, `openreview.net`, `alphaxiv.org`,
  `huggingface.co`, `web.archive.org`.
- Project sites: GitHub Pages (`*.github.io`), `lenia-explorer.vercel.app`, `bit.ly`.

Only `github.com` (over git), `raw.githubusercontent.com` and `pypi.org` were reachable.

**What that left (round 1):** Hudcová, Davis and Cool were excerpt-only. Davis and Cool had
their rules checked from code.

### 2026-10-07 verification pass, round 2 (network opened by Bobby)

Bobby widened the network policy. `curl -sS -L https://arxiv.org/pdf/2401.13111` then returned
HTTP 200, and the arXiv pages listed only v1 for each paper below.

| Source | Version | Local copy | Status |
| --- | --- | --- | --- |
| Hudcová et al. (2026) | arXiv 2601.01932**v1** (5 Jan 2026; 3 pp., Late Breaking Abstract) | `.refs/papers/hudcova2026.pdf` | Read in full |
| Cool et al. (2026) | arXiv 2605.30708**v1** (29 May 2026; 10 pp.) | `.refs/papers/cool2026.pdf` | Cited sections read |
| Davis (2024) | arXiv 2401.13111**v1** (23 Jan 2024; 49 pp.) | `.refs/papers/davis2024.pdf` | Methods, Lenia results and Fig. 5 read |
| Kojima & Ikegami (2023) | arXiv 2305.13784**v1** (23 May 2023; 9 pp.) | `.refs/papers/kojima2023.pdf` | §1.2 and §2.1 read |
| Hamon et al. (2024) | arXiv 2402.10236**v1** (24 pp.; preprint of the Science Advances paper) | `.refs/papers/hamon2024.pdf` | Introduction and supplementary movie list read |
| Chan (2020) | arXiv 2005.03742**v1** (7 May 2020; 9 pp.) | `.refs/papers/chan2020.pdf` | Cited passages read |
| Hoffman & Mallet-Paret (2010) | arXiv 0811.0093**v1** (55 pp.) | `.refs/papers/hoffman2010.pdf` | Abstract, §1 and Theorems 1.1–1.2 read |

Still unread:

- **Yevenko (2024):** excerpt only. `doi.org/10.1162/isal_a_00728` still returned 403.
- **The journal version of Chan (2019):** not needed. All locators cite arXiv v3.

## Primary Lenia sources

- **[Chan2019]** Bert Wang-Chak Chan. *Lenia — Biology of Artificial Life.* Complex Systems
  28(3):251–286, 2019. doi:[10.25088/ComplexSystems.28.3.251](https://doi.org/10.25088/ComplexSystems.28.3.251);
  arXiv:[1812.05433](https://arxiv.org/abs/1812.05433).

  **Read:** arXiv v3, *full text*. All section and figure numbers below are arXiv v3. The
  journal version was not read, and its numbering may differ.

  Used for:

  - **§3.1.1 "Spatial Invariance" (p. 15), Fig. 6(d–g) (p. 16).**
    - Quote: "For sufficiently fine space resolution (R > 12), patterns … are minimally affected
      by … shift, rotation, reflection and scaling."
    - Fig. 6 is a single visual test. Orbium (μ 0.15, σ 0.016) at **R = 185**, T = 10, double
      precision, **exponential** core functions, is flipped or "rotated 77° … with no visible
      effect".
  - **Fig. 7(a–b), p. 17.**
    - Orbium (μ 0.15, σ 0.016), R ∈ {9 … 55}, T = 10; each data point is averaged over 300 steps.
    - Mass, growth, gyradius, growth–centroid distance and speed "remain constant".
    - The niche "remain[s] static (total 557 loci)".
    - The caption does not say which core functions were used.
  - **§3.1.2 and Fig. 7(c–d), p. 17.**
    - R = 13, T ∈ {4 … 2560}.
    - As T increases, structure measures (mass, gyradius) go down and dynamics measures
      (growth, growth–centroid distance, speed) go up, each approaching a limit.
    - The niche expands as T increases (14 182 loci).
  - **§3.3.1–3.3.2 and Fig. 9, p. 21.**
    - Definitions of niche and locus, and a μ–σ map of rank-1 niches (142 338 loci).
    - Class 2 ("savannah") produces "regional, periodic immobile patterns (e.g. Circium)".
    - Read as an image, the map draws the Orbium (O2) and Gyrorbium (OG2) niches as
      **adjacent** bands near σ ≈ 0.02, μ ≈ 0.15–0.18. Coloured regions are drawn over one
      another, so the figure cannot show whether they overlap.
  - **§3.5.3 "Metamorphosis", Fig. 12(j), pp. 26–27.** Spontaneous switching among
    "morphological-behavioral templates".
  - **§3.5.2 "Gaits" (p. 27), Table 2 (p. 28).** "Fixation (F)" means negligible or no fluctuation. The
    frozen-stationary cell SF ("Frozen") is exemplified by *Pentafolium lithos*.
  - **§3.5.5 "Particle Reactions" (pp. 28–29), Fig. 12(k) (p. 26).** Two Orbium "fuse together into an
    intermediate, then stabilize into one Synorbium". Other listed outcomes are "Absorption,
    only one Orbium survives" and "Fission, one Synorbinae breaks into multiple Synorbinae or
    Orbium".
  - **§3.7.2 "Cross-Sectional Study", Fig. 17 (p. 35) and text (p. 36).** In genus *Paraptera* at μ = 0.3, two
    species (P4as, P4cp) **coexist** over σ ∈ [0.0468, 0.0483]. "Just outside the
    coexistence … they slowly transform into each other."
  - **§4.2.4 "Plasticity", p. 39.** "Lenia patterns are surprisingly resilient … absorb
    deformations … react to head-to-head collisions." Qualitative only, with no thresholds.

  The paper's Orbium (σ = 0.016, exponential cores in Fig. 6) is **not** S001's rule, which is
  poly/poly with σ = 0.015 (see C002).

  Cited by C003, C009, C013, C014, C038, C039, C040, C041, C042.

- **[Chan2020]** Bert Wang-Chak Chan. *Lenia and Expanded Universe.* ALIFE 2020 Proceedings
  (vol. 32), p. 221 onward. doi:[10.1162/isal_a_00297](https://doi.org/10.1162/isal_a_00297);
  arXiv:[2005.03742](https://arxiv.org/abs/2005.03742).

  **Read:** arXiv v1, *full text*, for the passages below.

  - **p. 5:** "In multi-kernel or multi-channel rules, Orbium-like individuality becomes a
    common phenomenon."
  - **p. 6, "Differentiation":** in multi-channel "Aquarium" rules, "one genotype produces
    multiple phenotypes of aggregated solitons, each having own stable structure and behavior".
    The listed phenotypes include "gyrating (gyrans), stationary (lithos)". Each "can switch to
    another phenotype in specific occasions, e.g. upon collision or after self-replication".

  These are expanded rules, not classic single-kernel Lenia.

  Cited by C038, C040, C042.

- **[LeniaCatalog]** Chakazul/Lenia repository, `Python/animals.json` at commit
  [`adfc542`](https://github.com/Chakazul/Lenia/blob/adfc542939266de7f4bb7ebb552e8499701ee107/Python/animals.json)
  (cloned to `.refs/Lenia`).

  **Read:** in full.

  Entries used:

  | Code | Name | Rule |
  | --- | --- | --- |
  | `O2u` | *Orbium unicaudatus* | R 13, T 10, μ 0.15, σ 0.015, kn = gn = 1 (S001's rule) |
  | `O4i` | *Synorbium ignis* | μ 0.152, σ 0.0156 |
  | `OG2g` | *Gyrorbium gyrans* | μ 0.156, σ 0.0224 |
  | `C0la` | *Circium lithos apertus* | R 15, μ 0.16, σ 0.022 |

  Cited by C026, C038, C041, C042, C043.

## Lenia follow-up work

- **[Hamon2025]** G. Hamon, M. Etcheverry, B. W.-C. Chan, C. Moulin-Frier, P.-Y. Oudeyer.
  *Discovering sensorimotor agency in cellular automata using diversity search.* Science
  Advances, 2025. doi:[10.1126/sciadv.adp0834](https://doi.org/10.1126/sciadv.adp0834);
  arXiv:[2402.10236](https://arxiv.org/abs/2402.10236).

  **Read:** arXiv v1, *full text* for the passages below. The journal version was not read.

  - **Introduction:** glider-like structures "typically remain quite fragile to external
    perturbations such as collision with other patterns".
  - **Supplementary movie list, pp. 23–24:**
    - Movie S3: "Orbium … fragile to external perturbations … collision between several orbium
      leading to death/explosion".
    - Movie S4: "Orbium … dies from perturbations by obstacles".

  These are movies with no strength scale. The obstacles are an added environment channel, not a
  mass edit.

  Cited by C023, C026.

- **[Cool2026]** J. Cool, B. Hartl, M. Levin, S. Petti. *Agnosiophobia in a virtual agent:
  behavioral and dynamical architecture in Lenia.*
  arXiv:[2605.30708](https://arxiv.org/abs/2605.30708) v1, 2026. Preprint; the repository says
  "to appear at ALIFE 2026". Code: [jessescool/lenia-umwelt](https://github.com/jessescool/lenia-umwelt)
  @ `58e8903`.

  **Read:** arXiv v1, *full text* for the cited sections. Methods also checked in *code*.

  **Paper:**
  - **"System and Methods" (Eq. 1–2), p. 2.** Standard clipped Euler Lenia. The occlusion is
    purely informational: occluded cells are excluded from the potential, and the potential is
    renormalised. No mass is removed.
  - **"Measuring recovery", p. 2.** The authors note that at finite resolution a creature's
    pixels fluctuate "differently so depending on the creature's angle relative to the axes of
    grid symmetry".
  - **p. 3.** Creatures are "upscaled to higher resolution than Chan's originals".
  - **"Lenia creatures avoid regions of occlusion", p. 4.** Depending on extent and location,
    occlusion pushes creatures toward "death, metamorphosis, or explosion". O2u shows "the most
    robust agnosiophobia" and survived longest.
  - **"Sensitivity to occlusion is spatially structured", Fig. 4, pp. 4–5.** A **persistent 3×3
    occluded region** is placed at each nonzero pixel. "Perturbations lethal to O2u are
    concentrated thinly at the center of its leading edge and expand into its core."

  **Code:**
  - `O2u` runs with S001's poly/poly rule (kn = gn = 1), dt = 1/T and a clip.
  - Runs use `--scale 4` (R = 52) in float32.

  Cited by C003, C013, C023, C026, C040.

- **[Davis2024]** Q. Tyrell Davis. *Discretization-Dependent Dissolution of Gliders in
  (Dis)Continuous Systems: Non-Platonic Self-Organization in Complex Systems.*
  arXiv:[2401.13111](https://arxiv.org/abs/2401.13111) v1, 2024. The paper's code is
  [RiveSunder/DiscoGliders](https://github.com/RiveSunder/DiscoGliders). Related repositories
  checked in round 1: [riveSunder/DisContinuous](https://github.com/riveSunder/DisContinuous) @
  `53809de` and [riveSunder/yuca](https://github.com/riveSunder/yuca) @ `ab59bff`.

  **Read:** arXiv v1, *full text* for the cited parts.

  - **p. 11 (Eq. 6) and Fig. 5 caption, p. 38.** The "Orbium" rule uses a Gaussian kernel shell
    (μK 0.5, σK 0.15) and Gaussian growth (μG 0.15, σG 0.015). That is not S001's poly/poly rule.
  - **p. 18, definition.** A pattern–rule pair is **non-Platonic** if, at some discretization
    where it does not persist, a *coarser* discretization exists where it does. Otherwise it is
    Platonic.
  - **Methods, pp. 16–17.** A random walk over Δt ∈ [0.01, 1], kernel radius, and float16, 32
    or 64.
  - **"Lenia", p. 20.** Of five Lenia gliders in four rule sets:
    - Orbium and the *H. natans* glider are **Platonic**: coarser discretization never restores
      persistence.
    - *Scutium gravidus*, *Triscutium solidus* and the *H. natans* wide wobble glider are
      **non-Platonic**.

  Round 1's excerpt that "Orbium fails at large step sizes" comes from the 2022 preliminary study
  (arXiv:[2208.09444](https://arxiv.org/abs/2208.09444)). It agrees with Orbium being Platonic,
  because coarse runs failing is the Platonic case.

  Cited by C003, C039.

- **[Kojima2023]** H. Kojima, T. Ikegami. *Implementation of Lenia as a Reaction-Diffusion
  System.* arXiv:[2305.13784](https://arxiv.org/abs/2305.13784) v1, 2023.

  **Read:** arXiv v1, *full text* for §1.2 and §2.1.

  - **§1.2, Eq. 3, p. 2.** Classic Lenia with a clip to [0, 1] and Gaussian growth. The paper
    does not state the kernel, R or grid.
  - **§2.1.1, p. 3.** The clip "cannot be expressed in a differential equation".
  - **§2.1.2, Fig. 2, p. 4.** The Orbium pattern "disappeared both when the size of the time step
    was large (dt = 0.5) and when it was small (**dt = 0.002**)".
  - **§2.1.3, Fig. 3, pp. 4–5.** Removing the *upper* clip lets the pattern persist at
    dt = 0.002, but at dt = 0.1 the clip is needed.

  Kojima's small-dt disappearance sits uneasily with Chan 2019 Fig. 7(c), which runs Orbium to
  T = 2560 (dt ≈ 0.0004). The two papers' kernels, horizons and survival criteria are not stated
  well enough to reconcile them. That makes it a numerical-ecology question for us, not a ledger
  dispute.

  Cited by C009, C042.

- **[Yevenko2024]** I. Yevenko. *Classifying the fractal parameter space of the Lenia Orbium.*
  ALIFE 2024 Proceedings, paper 14 (3 pp.).
  doi:[10.1162/isal_a_00728](https://doi.org/10.1162/isal_a_00728).

  **Read:** *excerpt*. The full text was still unreachable after the network change
  (`doi.org` returned 403).

  Used for: escape-time maps of Orbium stability over pairs of parameters, and Orbium variants
  that "fundamentally rely on discretization to survive".

  Cited by C038, C039.

- **[Hudcova2026]** B. Hudcová, F. Dušek, M. Tuccio, C. Hongler. *Visualizing the Structure of
  Lenia Parameter Space.* arXiv:[2601.01932](https://arxiv.org/abs/2601.01932) v1, 2026. This is
  a 3-page **Late Breaking Abstract**. Website: <https://lenia-explorer.vercel.app/>.

  **Read:** arXiv v1, *full text* (all of it).

  **Method (p. 1):**
  - Classic single-channel Lenia, Δt = **0.1**, Gaussian growth G = 2e^(−(x−μ)²/2σ²) − 1.
  - Initial configurations are uniform-noise patches shaped as random Voronoi polygons, of areas
    10² … 90² on a 100×100 grid, with 64 configurations per area.
  - Each configuration runs about 7000 steps and is classed as:
    - stable: the trajectory enters a loop;
    - metastable: the centre of mass settles;
    - unclassified: neither.

  **Results (p. 2):**
  - Fig. 3: four system classes, defined by how the phase proportions change with patch size.
    In Fig. 3(c–d) one system goes "from stable to metastable phase as the patches of noise
    increase in size", with solitons "around the transition region".
  - Fig. 4 shows the μ–σ plane for 8 kernels. The example kernel is the exponential bump at
    R = 13.
  - The authors report soliton families beyond Chan's Fig. 9 range.

  **Limits:**
  - "Exact algorithmic details … are provided in the documentation TODO".
  - The phases describe whole-grid dynamics. They do not identify species.

  Cited by C038.

## Adjacent fields

- **[HoffmanMalletParet2010]** A. Hoffman, J. Mallet-Paret. *Universality of crystallographic
  pinning.* J. Dynamics and Differential Equations 22:79–119, 2010. Pages are per Dialnet; the
  journal and volume are from memory and not confirmed. arXiv:[0811.0093](https://arxiv.org/abs/0811.0093) v1.

  **Read:** arXiv v1, *full text* of the abstract, §1 and the theorem statements.

  - Earlier work showed "crystallographic pinning occurs in every direction θ0 for which tan θ0
    is rational" for a sawtooth-like nonlinearity (§1).
  - Theorems 1.1–1.2 show that pinning occurs in the horizontal direction under a generic
    condition (Condition B).

  These are bistable travelling **fronts** on Z², not gliders, so the paper is an analogy only.

  Cited by C013.

## Search log

### 2026-10-07: seed set C003, C013, C023, C026, C038–C043 (archivist)

All searches were web searches; direct fetches were blocked.

Queries covered:

- Chan 2019 on resolution, rotation invariance, niches and taxonomy;
- Chan 2020 on multiple phenotypes;
- Lenia robustness, damage and self-repair;
- the sensorimotor-Lenia papers;
- the Lenia discretization papers (Davis, Kojima–Ikegami, Asymptotic Lenia);
- the Lenia parameter-space papers (Yevenko, Hudcová);
- Particle Lenia's motivation;
- lattice anisotropy and direction pinning of travelling waves;
- Circium and static or fixed-point patterns.

Not searched:

- SmoothLife (Rafler 2011) beyond search snippets;
- Flow-Lenia;
- the Asymptotic Lenia glider-equation papers in detail;
- non-English sources.

### 2026-10-07: verification pass (archivist)

See the retrieval log above. Chan 2019 was re-read in full. Its Fig. 7 bears directly on C009 and
C014, so those claims gained entries. No new literature search was run.

### 2026-10-07: verification pass, round 2 (archivist)

The network was opened, so every cited arXiv paper was read at v1. Yevenko (2024) is still excerpt-only. No new literature search was run.
