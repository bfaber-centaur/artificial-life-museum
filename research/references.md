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

**What that leaves:**

- **Hudcová et al. (2026):** full text not obtained. No arXiv mirror is reachable, and the code
  and data links in the paper are `bit.ly` short links, which are blocked. Excerpt-only.
- **Davis (2024):** full text not obtained. The GitHub repositories hold code, not the paper.
  They confirm only which rule the "Orbium" runs used (see the entry below).
- **Cool et al. (2026):** full text not obtained. The repository confirms the rule, the numerics
  and the intervention code. It does not confirm the reported results.

To finish the pass, either allow `arxiv.org` in the project's network settings (optionally also
`direct.mit.edu`) or upload the three PDFs to the project.

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

  **Read:** *excerpt*; not part of this pass.

  Used for: multiple phenotypes of aggregated solitons under multi-kernel and multi-channel
  rules. These are expanded rules, not classic single-kernel Lenia.

  Cited by C038.

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
  arXiv:[2402.10236](https://arxiv.org/abs/2402.10236). Companion site:
  <https://developmentalsystems.org/sensorimotor-lenia-companion/>.

  **Read:** *excerpt*; not a priority paper in this pass.

  Used for:

  - The companion site's statements that Orbium "dies from perturbations by obstacles" and
    that collisions of several Orbium end in death or explosion.
  - The paper's statement that discovered patterns are typically fragile to perturbation.

  Note that the obstacles are an added environment channel, not a mass edit.

  Cited by C023, C026.

- **[Cool2026]** J. Cool, B. Hartl, M. Levin, S. Petti. *Agnosiophobia in a virtual agent:
  behavioral and dynamical architecture in Lenia.*
  arXiv:[2605.30708](https://arxiv.org/abs/2605.30708), 2026. Preprint; the repository says
  "to appear at ALIFE 2026". Code: [jessescool/lenia-umwelt](https://github.com/jessescool/lenia-umwelt)
  @ `58e8903`.

  **Read:** paper *excerpt*; methods checked in *code*.

  Verified from the code:

  - **Rule.** Creatures come from Chan's catalog. `O2u` uses kn = gn = 1, implemented as the
    polynomial kernel (4r(1−r))⁴ and polynomial growth 2(1 − (u−μ)²/9σ²)⁴ − 1, with dt = 1/T
    and a clip to [0, 1] (`substrate/lenia.py`). That is **S001's rule**.
  - **Numerics.** Runs use `--scale 4`, so R = 52 on a 512² grid, in **float32**.
  - **Occlusion.** An occlusion renormalises the potential as
    U = K∗(A·(1−B)) / K∗(1−B) (README, `index.html`).
  - **Interventions.** The sweep code supports four types:
    - `erase`: zero an N×N square, which removes mass. This is the default, with a 2×2 square
      at base resolution.
    - `blind`: a persistent occlusion that removes no mass.
    - `blind_erase` and `additive`.
  - **Outcome classes.** "Recovered" means a return to a rotation-invariant "neighborhood" of
    the sorted activation profile. "Dead" means total mass below 0.01.
  - **Grid drift.** The README notes that "at finite grid resolution the creature's
    morphology … drifts (heading relative to grid axes, small phase shifts)".

  Excerpt only (these are the paper's results):

  - Occlusions push creatures to death, metamorphosis or explosion depending on their extent and
    location.
  - In the per-pixel sensitivity maps, small persistent occlusions on the leading edge or core
    usually destroy the creature.
  - O2u shows the most robust avoidance of the four creatures (O2u, S1s, K4s, K6s).

  Which intervention type the paper's maps used is therefore not confirmed.

  Cited by C013, C023, C026, C040.

- **[Davis2024]** Q. Tyrell Davis. *Discretization-Dependent Dissolution of (Dis)Continuous
  Gliders: Non-Platonic Self-Organization in Complex Systems.*
  arXiv:[2401.13111](https://arxiv.org/abs/2401.13111), 2024. Preliminary study:
  arXiv:[2208.09444](https://arxiv.org/abs/2208.09444) (2022). Code:
  [riveSunder/DisContinuous](https://github.com/riveSunder/DisContinuous) @ `53809de` and
  [riveSunder/yuca](https://github.com/riveSunder/yuca) @ `ab59bff`.

  **Read:** paper *excerpt*; rule checked in *code*.

  Verified from the code: the "Orbium" in this work (`get_orbium_config` in `yuca/configs.py`)
  uses a **Gaussian** kernel shell (μ 0.5, σ 0.15) and **Gaussian** growth (μ 0.15, σ 0.015) at
  R = 13. That is the exponential/exponential family, not S001's poly/poly rule.

  Excerpt only:

  - "Non-Platonic" gliders, for example *Scutium gravidus*, lose persistence under finer
    discretization.
  - Orbium tolerates kernel radius 65 and float64, but fails at large step sizes.

  Cited by C003, C039.

- **[Kojima2023]** H. Kojima, T. Ikegami. *Implementation of Lenia as a Reaction-Diffusion
  System.* arXiv:[2305.13784](https://arxiv.org/abs/2305.13784), 2023.

  **Read:** *excerpt*; not part of this pass.

  Used for: classic Lenia's clip prevents a pure differential-equation description.

  Cited by C042.

- **[Yevenko2024]** I. Yevenko. *Classifying the fractal parameter space of the Lenia Orbium.*
  ALIFE 2024 Proceedings, paper 14 (3 pp.).
  doi:[10.1162/isal_a_00728](https://doi.org/10.1162/isal_a_00728).

  **Read:** *excerpt*; not part of this pass.

  Used for: escape-time maps of Orbium stability over pairs of parameters, and Orbium variants
  that "fundamentally rely on discretization to survive".

  Cited by C038, C039.

- **[Hudcova2026]** B. Hudcová, F. Dušek, M. Tuccio, C. Hongler. *Visualizing the Structure of
  Lenia Parameter Space.* arXiv:[2601.01932](https://arxiv.org/abs/2601.01932), 2026.
  Website: `lenia-explorer.vercel.app` (unreachable from here).

  **Read:** *excerpt* only. The full text and code were blocked (see the retrieval log).

  Excerpts say:

  - The paper studies classic single-channel Lenia with **Δt = 0.1** and a **Gaussian** growth
    function; once the kernel is fixed, each system is set by (μ, σ).
  - Each initial configuration is run for about 7000 steps and classed as one of:
    - stable: enters a loop;
    - metastable: centre of mass settles;
    - unclassified: corresponds strongly to moving solitons.
  - Fig. 3 shows, for each system across a μ–σ plane, the proportion of initial configurations
    in each class.

  Not confirmed: the kernel shape, R, the grid size, and how the initial configurations were
  drawn.

  Cited by C038.

## Adjacent fields

- **[HoffmanMalletParet2010]** A. Hoffman, J. Mallet-Paret. *Universality of crystallographic
  pinning.* J. Dynamics and Differential Equations 22:79–119, 2010. Pages are per Dialnet; the
  journal and volume are from memory and not confirmed.
  arXiv:[0811.0093](https://arxiv.org/abs/0811.0093).

  **Read:** *excerpt*.

  Used for: travelling fronts of bistable lattice reaction–diffusion equations on Z² are pinned
  in some lattice directions while moving in nearby ones (Theorems 1.1–1.2). These are fronts,
  not gliders, so this is an analogy only.

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
