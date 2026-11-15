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

  Cited by C003, C009, C013, C014, C038, C039, C040, C041, C042; C046 and C051 in PR #22.

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

  Cited by C003, C039; C047 in PR #22. On 2026-10-08 the C039 entry was downgraded from CONSISTENT WITH to
  RELATED: S102's R = 26 death occurs only from a bilinearly resized seed (dispute D2, C047), so it is
  a resize-method dependence of the initial condition, not evidence that S102 is non-Platonic in R.

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

  Cited by C009, C042; C051 in PR #22 (CONTRADICTORY, similar outcome only: S001 survives at
  dt = 0.0016–0.00039 under its own poly/poly rule).

- **[Yevenko2024]** I. Yevenko. *Classifying the fractal parameter space of the Lenia Orbium.*
  ALIFE 2024 Proceedings, paper 14 (3 pp.).
  doi:[10.1162/isal_a_00728](https://doi.org/10.1162/isal_a_00728).

  **Read:** *excerpt*. The full text was still unreachable after the network change
  (`doi.org` returned 403).

  Used for: escape-time maps of Orbium stability over pairs of parameters, and Orbium variants
  that "fundamentally rely on discretization to survive".

  Cited by C038, C039 (RELATED since 2026-10-08, as for Davis2024).

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

**Field survey.** A map of current (2022–2026) Lenia and Lenia-like research, grouped by
question with gaps for the museum, is in [`lenia-research-survey-2026-11.md`](lenia-research-survey-2026-11.md).
Its entries are abstract-grade and are not yet cited by any claim.

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

## The ‘So what?’ wing (2026-11-15)

Sources for museum rooms 85–87 ("So what?" wing thread). Metadata (authors, year, title,
journal, volume, pages) of every DOI below was checked against the Crossref API on
2026-11-15; arXiv entries against the arXiv API. **Read** says what was read. A fourth grade is
used here: *abstract* = the publisher abstract via PubMed or arXiv, not the full paper. Where
the wing says more than the abstract, that sentence is marked *from memory* below, so a later
reader knows what to check first. These sources mostly support museum prose, not claims; claims
that cite them say so in their **Prior literature** field.

**Population genetics and digital evolution (room 85).**

- **[Haldane1927]** J. B. S. Haldane. *A mathematical theory of natural and artificial selection,
  part V.* Math. Proc. Camb. Phil. Soc. 23:838–844. [doi:10.1017/S0305004100015644](https://doi.org/10.1017/S0305004100015644).
  Read: metadata. The ≈ 2s survival result is standard textbook attribution (from memory). C112.
- **[Moran1958]** P. A. P. Moran. *Random processes in genetics.* Math. Proc. Camb. Phil. Soc.
  54:60–71. [doi:10.1017/S0305004100033193](https://doi.org/10.1017/S0305004100033193). Read: metadata; the process and its
  fixation formula as given in Patwa & Wahl 2008 (from memory). C112.
- **[Kimura1962]** M. Kimura. *On the probability of fixation of mutant genes in a population.*
  Genetics 47:713–719. [doi:10.1093/genetics/47.6.713](https://doi.org/10.1093/genetics/47.6.713). Read: metadata. C112.
- **[Ohta1973]** T. Ohta. *Slightly deleterious mutant substitutions in evolution.* Nature
  246:96–98. [doi:10.1038/246096a0](https://doi.org/10.1038/246096a0). Read: metadata. C112.
- **[PatwaWahl2008]** Z. Patwa, L. M. Wahl. *The fixation probability of beneficial mutations.*
  J. R. Soc. Interface 5:1279–1289. [doi:10.1098/rsif.2008.0248](https://doi.org/10.1098/rsif.2008.0248). Read: metadata (review). C112.
- **[Lenski2003]** R. E. Lenski, C. Ofria, R. T. Pennock, C. Adami. *The evolutionary origin of
  complex features.* Nature 423:139–144. [doi:10.1038/nature01568](https://doi.org/10.1038/nature01568). Read: abstract
  (complex functions evolved by building on simpler ones only when those were also favoured;
  no single intermediate essential; some deleterious mutations were stepping stones). The name
  EQU for the most complex rewarded function is from memory.
- **[Wilke2001]** C. O. Wilke, J. L. Wang, C. Ofria, R. E. Lenski, C. Adami. *Evolution of digital
  organisms at high mutation rates leads to survival of the flattest.* Nature 412:331–333.
  [doi:10.1038/35085569](https://doi.org/10.1038/35085569). Read: abstract (40 ancestor pairs; 12 disparate pairs competed; in each,
  higher mutation rate switched the winner to the slower, flatter genotype).
- **[OfriaWilke2004]** C. Ofria, C. O. Wilke. *Avida: a software platform for research in
  computational evolutionary biology.* Artificial Life 10:191–229.
  [doi:10.1162/106454604773563612](https://doi.org/10.1162/106454604773563612). Read: metadata.
- **[Adami2006]** C. Adami. *Digital genetics: unravelling the genetic basis of evolution.* Nat.
  Rev. Genet. 7:109–118. [doi:10.1038/nrg1771](https://doi.org/10.1038/nrg1771). Read: metadata (review).
- **[Blount2008]** Z. D. Blount, C. Z. Borland, R. E. Lenski. *Historical contingency and the
  evolution of a key innovation in an experimental population of* Escherichia coli. PNAS
  105:7899–7906. [doi:10.1073/pnas.0803151105](https://doi.org/10.1073/pnas.0803151105). Read: abstract (Cit+ in one of 12 populations by
  31,500 generations; replays from frozen clones; potentiation by 20,000 generations).
- **[Nowell1976]** P. C. Nowell. *The clonal evolution of tumor cell populations.* Science
  194:23–28. [doi:10.1126/science.959840](https://doi.org/10.1126/science.959840). Read: metadata.
- **[GreavesMaley2012]** M. Greaves, C. C. Maley. *Clonal evolution in cancer.* Nature
  481:306–313. [doi:10.1038/nature10762](https://doi.org/10.1038/nature10762). Read: metadata (review).
- **[Gatenby2009]** R. A. Gatenby, A. S. Silva, R. J. Gillies, B. R. Frieden. *Adaptive therapy.*
  Cancer Res. 69:4894–4903. [doi:10.1158/0008-5472.CAN-08-3658](https://doi.org/10.1158/0008-5472.CAN-08-3658). Read: abstract.
- **[Zhang2017]** J. Zhang, J. J. Cunningham, J. S. Brown, R. A. Gatenby. *Integrating evolutionary
  dynamics into treatment of metastatic castrate-resistant prostate cancer.* Nat. Commun.
  8:1816. [doi:10.1038/s41467-017-01968-5](https://doi.org/10.1038/s41467-017-01968-5). Read: abstract (pilot trial: 10 of 11 patients
  kept stable oscillations; median TTP at least 27 months vs ~16.5 with standard dosing;
  cumulative drug 47% of standard; compared with published studies and a contemporaneous
  population, not randomised).
- **[Wolfram2024a]** S. Wolfram. *Why does biological evolution work? A minimal model for
  biological evolution and other adaptive processes.* Stephen Wolfram Writings, 3 May 2024.
  [link](https://writings.stephenwolfram.com/2024/05/why-does-biological-evolution-work-a-minimal-model-for-biological-evolution-and-other-adaptive-processes/).
  Read: full text fetched 2026-11-15 (mutations accepted if lifetime does not shrink; plateaus
  punctuated by jumps, often from one mutation; links to computational irreducibility). Not
  peer reviewed. The follow-up "Foundations of biological evolution: more results & more
  surprises" (5 December 2024) is named on that page; not read.

**Morphogenesis, bodies and robots (room 86).**

- **[Turing1952]** A. M. Turing. *The chemical basis of morphogenesis.* Phil. Trans. R. Soc. B
  237:37–72. [doi:10.1098/rstb.1952.0012](https://doi.org/10.1098/rstb.1952.0012). Read: metadata. C113.
- **[Pearson1993]** J. E. Pearson. *Complex patterns in a simple system.* Science 261:189–192.
  [doi:10.1126/science.261.5118.189](https://doi.org/10.1126/science.261.5118.189). Read: metadata; already the source of WINGS's Gray-Scott
  (C066). C113.
- **[KondoAsai1995]** S. Kondo, R. Asai. *A reaction–diffusion wave on the skin of the marine
  angelfish* Pomacanthus. Nature 376:765–768. [doi:10.1038/376765a0](https://doi.org/10.1038/376765a0). Read: abstract (stripes
  keep their spacing by rearranging as the fish grows; a Turing-system simulation predicts
  the rearrangements).
- **[KondoMiura2010]** S. Kondo, T. Miura. *Reaction-diffusion model as a framework for
  understanding biological pattern formation.* Science 329:1616–1620.
  [doi:10.1126/science.1179047](https://doi.org/10.1126/science.1179047). Read: metadata (review).
- **[Sheth2012]** R. Sheth et al. *Hox genes regulate digit patterning by controlling the
  wavelength of a Turing-type mechanism.* Science 338:1476–1480.
  [doi:10.1126/science.1226804](https://doi.org/10.1126/science.1226804). Read: abstract (progressive loss of distal Hox genes on a
  Gli3-null background gives more, thinner digits; Hox dose modulates wavelength).
- **[Raspopovic2014]** J. Raspopovic, L. Marcon, L. Russo, J. Sharpe. *Digit patterning is
  controlled by a Bmp-Sox9-Wnt Turing network modulated by morphogen gradients.* Science
  345:566–570. [doi:10.1126/science.1252960](https://doi.org/10.1126/science.1252960). Read: abstract.
- **[Durant2017]** F. Durant et al. *Long-term, stochastic editing of regenerative anatomy via
  targeting endogenous bioelectric gradients.* Biophys. J. 112:2231–2243.
  [doi:10.1016/j.bpj.2017.04.011](https://doi.org/10.1016/j.bpj.2017.04.011). Read: abstract (brief bioelectric perturbation gives a constant
  ratio of two-headed regenerates; normal-looking regenerates re-cut in water give the same
  ratio; stored in resting-potential patterns, not histology or polarity genes; reversible).
- **[Levin2021]** M. Levin. *Bioelectric signaling: reprogrammable circuits underlying
  embryogenesis, regeneration, and cancer.* Cell 184:1971–1989.
  [doi:10.1016/j.cell.2021.02.034](https://doi.org/10.1016/j.cell.2021.02.034). Read: metadata (review).
- **[Mordvintsev2020]** A. Mordvintsev, E. Randazzo, E. Niklasson, M. Levin. *Growing neural
  cellular automata.* Distill 5(2):e23. [doi:10.23915/distill.00023](https://doi.org/10.23915/distill.00023). Read: full text
  (interactive article) fetched 2026-11-15: growing, persistent and regenerating models;
  persistent models "often develop some regenerative capabilities without being explicitly
  trained".
- **[Kriegman2020]** S. Kriegman, D. Blackiston, M. Levin, J. Bongard. *A scalable pipeline for
  designing reconfigurable organisms.* PNAS 117:1853–1859. [doi:10.1073/pnas.1910837117](https://doi.org/10.1073/pnas.1910837117).
  Read: abstract. That the builds used frog (*Xenopus*) skin and heart cells is from memory.
- **[Kriegman2021]** Same authors. *Kinematic self-replication in reconfigurable organisms.*
  PNAS 118:e2112672118. [doi:10.1073/pnas.2112672118](https://doi.org/10.1073/pnas.2112672118). Read: abstract.
- **[Rubenstein2014]** M. Rubenstein, A. Cornejo, R. Nagpal. *Programmable self-assembly in a
  thousand-robot swarm.* Science 345:795–799. [doi:10.1126/science.1254295](https://doi.org/10.1126/science.1254295). Read: abstract.

**Epidemics, ecology and open-endedness (room 87).**

- **[KermackMcKendrick1927]** W. O. Kermack, A. G. McKendrick. *A contribution to the
  mathematical theory of epidemics.* Proc. R. Soc. A 115:700–721.
  [doi:10.1098/rspa.1927.0118](https://doi.org/10.1098/rspa.1927.0118). Read: metadata. C114.
- **[Keeling1999]** M. J. Keeling. *The effects of local spatial structure on epidemiological
  invasions.* Proc. R. Soc. B 266:859–867. [doi:10.1098/rspb.1999.0716](https://doi.org/10.1098/rspb.1999.0716). Read: abstract. C114, C115.
- **[WattsStrogatz1998]** D. J. Watts, S. H. Strogatz. *Collective dynamics of ‘small-world’
  networks.* Nature 393:440–442. [doi:10.1038/30918](https://doi.org/10.1038/30918). Read: abstract ("infectious diseases spread more
  easily in small-world networks than in regular lattices"). C114.
- **[Ferguson2005]** N. M. Ferguson et al. *Strategies for containing an emerging influenza
  pandemic in Southeast Asia.* Nature 437:209–214. [doi:10.1038/nature04017](https://doi.org/10.1038/nature04017). Read: abstract
  (elimination feasible with geographically targeted prophylaxis plus social distancing if
  R0 below 1.8).
- **[Grimm2005]** V. Grimm et al. *Pattern-oriented modeling of agent-based complex systems:
  lessons from ecology.* Science 310:987–991. [doi:10.1126/science.1116681](https://doi.org/10.1126/science.1116681). Read: abstract;
  "test against several patterns at once" is the method's core idea as we remember it.
- **[NowakMay1992]** M. A. Nowak, R. M. May. *Evolutionary games and spatial chaos.* Nature
  359:826–829. [doi:10.1038/359826a0](https://doi.org/10.1038/359826a0). Read: metadata only (no PubMed abstract); the description
  in room 87 is from memory.
- **[LehmanStanley2011]** J. Lehman, K. O. Stanley. *Abandoning objectives: evolution through the
  search for novelty alone.* Evol. Comput. 19:189–223. [doi:10.1162/EVCO_a_00025](https://doi.org/10.1162/EVCO_a_00025). Read:
  metadata.
- **[Wang2019]** R. Wang, J. Lehman, J. Clune, K. O. Stanley. *Paired Open-Ended Trailblazer
  (POET).* arXiv:[1901.01753](https://arxiv.org/abs/1901.01753) v1. Read: abstract.
- **[Hughes2024]** E. Hughes et al. *Open-endedness is essential for artificial superhuman
  intelligence.* arXiv:[2406.04268](https://arxiv.org/abs/2406.04268) v1 (position paper). Read: abstract. The authors'
  Google DeepMind affiliation is from memory.
- **[Kumar2024]** A. Kumar, C. Lu, L. Kirsch, et al. *Automating the search for artificial life
  with foundation models* (ASAL). arXiv:[2412.17799](https://arxiv.org/abs/2412.17799) v1. Read: abstract (substrates Boids,
  Particle Life, Game of Life, Lenia, NCA; reports previously unseen Lenia and Boids
  lifeforms). Affiliations (Sakana AI, MIT) from memory.

**Who else evolves things in Lenia (survey, 2026-11-15).** One arXiv search (`all:Lenia`,
`all:"Flow-Lenia"`, newest first, 100 results; plus title searches for "sensorimotor" and
"Biomaker") to answer Bobby's question "is anyone doing this kind of modelling with Lenia, and
what are they asking?". Read: abstracts via the arXiv API for all; full text (arXiv PDF) where
marked. This is a survey for museum prose, not a claim search.

- **[Chan2023]** B. W.-C. Chan. *Towards large-scale simulations of open-ended evolution in
  continuous cellular automata.* GECCO '23 companion; arXiv:[2304.05639](https://arxiv.org/abs/2304.05639) v1. Read: full
  text. Evolution inside one Lenia world: reproduction by self-replication, selection by
  differential survival, localized genomes. Runs "go through a phase of diversity and
  creativity, gradually converge to domination by fast expanding patterns" (abstract); §3:
  "eventually the world converges to either total extinction, or domination by expanding
  patterns". Relevant to C110, C111 (GenomeLenia's climb towards fast division).
- **[Plantec2025]** E. Plantec, G. Hamon, M. Etcheverry, B. W.-C. Chan, P.-Y. Oudeyer,
  C. Moulin-Frier. *Flow-Lenia: emergent evolutionary dynamics in mass conservative continuous
  cellular automata.* Artificial Life 31(2):228–248 (2025); arXiv:[2506.08569](https://arxiv.org/abs/2506.08569) v1 (earlier version
  arXiv:2212.07906). Read: full text. Parameters embedded in the matter allow multi-species
  worlds; evolutionary activity (Bedau & Packard; Droop & Hickinbotham) falls with mutation
  rate (power law, slope −0.5 non-neutral, −0.71 count-based, §5); dissipative and food
  variants show higher activity, but the ordering reverses when activity is divided by total
  mass (§5). Our SOUP engine follows this paper's parameter embedding.
- **[Michel2025]** T. Michel, M. Cvjetko, G. Hamon, P.-Y. Oudeyer, C. Moulin-Frier. *Exploring
  Flow-Lenia universes with a curiosity-driven AI scientist: discovering diverse ecosystem
  dynamics.* Proc. ALIFE 2025, 633–643; arXiv:[2505.15998](https://arxiv.org/abs/2505.15998) v4. Read: abstract (IMGEP over
  whole-ecosystem metrics such as evolutionary activity; scaling study over six spatial scales).
- **[Papadopoulos2025]** V. Papadopoulos, E. Guichard. *MaCE: general mass conserving dynamics for
  cellular automata.* arXiv:[2507.12306](https://arxiv.org/abs/2507.12306) v1. Read: abstract ("hints of intrinsic evolution in
  resource-constrained environments").
- **[FaldorCully2024]** M. Faldor, A. Cully. *Toward artificial open-ended evolution within Lenia
  using quality-diversity* (Leniabreeder). arXiv:[2406.04235](https://arxiv.org/abs/2406.04235) v1. Read: abstract.
- **[Hamon2025]** G. Hamon, M. Etcheverry, B. W.-C. Chan, C. Moulin-Frier, P.-Y. Oudeyer.
  *Discovering sensorimotor agency in cellular automata using diversity search.* Sci. Adv.
  11(44):eadp0834 (2025); arXiv:[2402.10236](https://arxiv.org/abs/2402.10236) v1. Read: abstract.
- **[SayamaNehaniv2024]** H. Sayama, C. L. Nehaniv. *Self-reproduction and evolution in cellular
  automata: 25 years after Evoloops.* arXiv:[2402.03961](https://arxiv.org/abs/2402.03961) v2 (review). Read: abstract.
- **[Baid2025]** N. Baid et al. *Guiding evolution of artificial life using vision-language
  models* (ASAL++). arXiv:[2509.22447](https://arxiv.org/abs/2509.22447) v1. Read: abstract.
- **[Cool2026a]** J. Cool, B. Hartl, M. Levin, S. Petti. *Agnosiophobia in a virtual agent:
  behavioral and dynamical architecture in Lenia.* arXiv:[2605.30708](https://arxiv.org/abs/2605.30708) v1. Read: abstract.
- **[Cvjetko2026]** M. Cvjetko et al. *The artificial experimentalist: discovery and control of
  self-organizing phenomena with autotelic reinforcement learning.* arXiv:[2608.26116](https://arxiv.org/abs/2608.26116) v2. Read: abstract.
- **[Akhtyrchenko2026]** M. Akhtyrchenko, M. I. Katsnelson, A. Ustyuzhanin. *Directing open-ended
  evolution in artificial life via multi-scale path divergence.* arXiv:[2606.17091](https://arxiv.org/abs/2606.17091) v2. Read: abstract.

*What the survey did not find:* no paper in these results measures fixation or loss of
individual mutants against a neutral control, or tests treatment-like dosing schedules, in
Lenia or Flow-Lenia. NO MATCH FOUND IN SEARCHED SOURCES is not a novelty claim: the search was
arXiv only, and the population-genetics literature on Avida and other digital systems has done
both kinds of experiment.

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

### 2026-10-08: L3-002 (PR #18) and dispute D2 (archivist)

No new search was run. Lane 3's timestep and resolution results (C046–C051, ledgered in PR #22) were
checked against the papers already read (Chan 2019 Fig. 7, Kojima 2023 §2.1.2, Davis 2024 p. 18).

Two kinds of discretization effect are kept apart:

- *Resolution or timestep dependence*: a property changes as R or T is refined from the same
  continuum initial condition. L3-002 finds R = 13 converged to 0.5% and T = 10 biased by 10–18%
  (C046).
- *Resize-method dependence*: the outcome changes with how a seed is resampled to a new R. S102's
  R = 26 death (C039) is of this kind (C047).

Only the first kind bears on Davis's Platonic/non-Platonic definition, so the C039 entries for
Davis 2024 and Yevenko 2024 were downgraded to RELATED.

### 2026-11-15: the "So what?" wing (rooms 85–87)

One bounded pass for museum prose, not a literature review. Candidate sources were named from
memory for each field Bobby listed, then each was checked: Crossref API for DOI metadata,
PubMed E-utilities for abstracts, the arXiv API for preprints, and direct fetches of the
Distill article and Wolfram's essay. Every DOI resolved to the expected paper. Publisher pages
(science.org, pnas.org) returned 403, so no full texts beyond the two web articles were read;
statements beyond an abstract are flagged *from memory* in the entries above. The literature
fields of C112, C114 and C115 cite these sources as PREVIOUSLY REPORTED or CONSISTENT WITH; C113
cites Pearson 1993. Nothing here changes a status.

### 2026-11-15: who else evolves things in Lenia (population-dynamics round)

arXiv API searches `all:Lenia` (100 newest), `all:"Flow-Lenia"`, `ti:sensorimotor AND
ti:cellular`, `ti:Biomaker`, `all:"continuous cellular automata" AND all:evolution`. Abstracts of
the 18 most relevant results read; full text of Chan 2023, Plantec et al. 2025 and MaCE 2025
(arXiv PDFs). Entries are under "Who else evolves things in Lenia". No paper in these results
used a neutral-marker control or a dosing schedule in Lenia (NO MATCH FOUND IN SEARCHED SOURCES,
arXiv only). C116 cites the population-genetics sources of the "So what?" wing; C120 is
recorded as CONTRADICTORY in outcome to Zhang et al. 2017, not in conditions.
