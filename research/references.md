# References

Deduplicated bibliography for the **Prior literature** fields in [`claims.md`](claims.md).
The claims archivist (Lane 0) maintains it. Each entry has a short key, a stable link, and the
claims that cite it. Relationship classes and the rules for using them are in
`claims.md` under "Literature provenance".

**How each source was read.** On 2026-10-07 the session's network policy blocked direct fetches of
arxiv.org, ar5iv, direct.mit.edu, content.wolfram.com and the other publisher hosts. Every source
below was therefore read only through web-search excerpts, except the Chakazul/Lenia catalog,
which is cloned locally. A locator marked *(excerpt)* comes from such an excerpt and should be
checked against the full text before anyone quotes it. Figure numbers differ between the arXiv
and journal versions of [Chan2019], so both are given where known.

## Primary Lenia sources

- **[Chan2019]** Bert Wang-Chak Chan. *Lenia — Biology of Artificial Life.* Complex Systems
  28(3):251–286, 2019. doi:[10.25088/ComplexSystems.28.3.251](https://doi.org/10.25088/ComplexSystems.28.3.251);
  arXiv:[1812.05433](https://arxiv.org/abs/1812.05433).
  Used for:
  - the resolution parameters R, T, P and the continuum limit;
  - the statement that patterns are minimally affected by shift, rotation, reflection and
    scaling at R > 12 (arXiv Fig. 6(d–g); journal Fig. 5(d–g)) *(excerpt)*;
  - Orbium statistics constant over R = 9–55 at T = 10, with a static niche of 557 loci
    (journal Fig. 6(a–b)) *(excerpt)*;
  - niche and locus definitions, and the μ–σ niche map with the Circium inset *(excerpt)*.

  The paper's Orbium rule (σ = 0.016, exponential kernel and growth) is **not** S001's rule
  (see C002). Cited by C003, C013, C038, C039.
- **[Chan2020]** Bert Wang-Chak Chan. *Lenia and Expanded Universe.* ALIFE 2020 Proceedings
  (vol. 32), p. 221 onward. doi:[10.1162/isal_a_00297](https://doi.org/10.1162/isal_a_00297);
  arXiv:[2005.03742](https://arxiv.org/abs/2005.03742). Used for: multiple phenotypes of
  aggregated solitons under multi-kernel and multi-channel rules *(excerpt)*. Those are expanded
  rules, not classic single-kernel Lenia. Cited by C038.
- **[LeniaCatalog]** Chakazul/Lenia repository, `Python/animals.json` at commit
  [`adfc542`](https://github.com/Chakazul/Lenia/blob/adfc542939266de7f4bb7ebb552e8499701ee107/Python/animals.json)
  (cloned to `.refs/Lenia`). Read in full. Entries used:

  | Code | Name | Rule |
  | --- | --- | --- |
  | `O2u` | *Orbium unicaudatus* | R 13, T 10, μ 0.15, σ 0.015, kn = gn = 1 (S001's rule) |
  | `O4i` | *Synorbium ignis* | μ 0.152, σ 0.0156 |
  | `OG2g` | *Gyrorbium gyrans* | μ 0.156, σ 0.0224 |
  | `C0la` | *Circium lithos apertus* | R 15, μ 0.16, σ 0.022 |

  Cited by C026, C038, C041, C042, C043.

## Lenia follow-up work

- **[Hamon2025]** G. Hamon, M. Etcheverry, B. W.-C. Chan, C. Moulin-Frier, P.-Y. Oudeyer.
  *Discovering sensorimotor agency in cellular automata using diversity search.* Science Advances,
  2025. doi:[10.1126/sciadv.adp0834](https://doi.org/10.1126/sciadv.adp0834);
  arXiv:[2402.10236](https://arxiv.org/abs/2402.10236) (2024). Companion site:
  <https://developmentalsystems.org/sensorimotor-lenia-companion/>.
  Used for:
  - the companion-site statements that Orbium "dies from perturbations by obstacles" and that
    collisions between several Orbium lead to death or explosion *(excerpt; companion site, not
    the paper text)*;
  - the paper's statement that hand-made and randomly found Lenia patterns are typically fragile
    to external perturbations *(excerpt)*.

  The obstacles are an added environment channel, not a mass edit. Cited by C023, C026, C041.
- **[Cool2026]** J. Cool, B. Hartl, M. Levin, S. Petti. *Agnosiophobia in a virtual agent:
  behavioral and dynamical architecture in Lenia.* arXiv:[2605.30708](https://arxiv.org/abs/2605.30708),
  2026 (preprint, not peer reviewed). Code: <https://github.com/jessescool/lenia-umwelt>.
  Used for:
  - informational occlusions whose extent and location push creatures toward death,
    metamorphosis or explosion *(excerpt)*;
  - O2u (Orbium, the S001 catalog rule) being the most robust of the four creatures tested
    *(excerpt)*.

  Cited by C023, C026, C040.
- **[Davis2024]** Q. Tyrell Davis. *Discretization-Dependent Dissolution of (Dis)Continuous
  Gliders: Non-Platonic Self-Organization in Complex Systems.*
  arXiv:[2401.13111](https://arxiv.org/abs/2401.13111), 2024. Preliminary study:
  arXiv:[2208.09444](https://arxiv.org/abs/2208.09444) (2022).
  Used for:
  - "non-Platonic" gliders that lose persistence under finer discretization (for example
    *Scutium gravidus*) *(excerpt)*;
  - Orbium tolerating kernel radius 65 and float64, but failing at large step sizes *(excerpt)*.

  Cited by C003, C039.
- **[Kojima2023]** H. Kojima, T. Ikegami. *Implementation of Lenia as a Reaction-Diffusion System.*
  arXiv:[2305.13784](https://arxiv.org/abs/2305.13784), 2023. Used for:
  - classic Lenia's clip preventing a pure differential-equation description *(excerpt)*;
  - Orbium vanishing at both dt = 0.5 and dt = 0.002 in classic Lenia *(excerpt)*.

  Cited by C042.
- **[Yevenko2024]** I. Yevenko. *Classifying the fractal parameter space of the Lenia Orbium.*
  ALIFE 2024 Proceedings, paper 14 (3 pp.). doi:[10.1162/isal_a_00728](https://doi.org/10.1162/isal_a_00728).
  Used for:
  - escape-time maps of *Orbium unicaudatus* stability over two parameters at a time
    *(excerpt)*;
  - many Orbium variants that "fundamentally rely on discretization to survive" *(excerpt)*.

  Cited by C038, C039.
- **[Hudcova2026]** B. Hudcová et al. *Visualizing the Structure of Lenia Parameter Space.*
  arXiv:[2601.01932](https://arxiv.org/abs/2601.01932), 2026. Used for: dynamical classes
  assigned per initial configuration over a μ–σ plane (about 10 000 systems), so that one rule
  can fall into different classes depending on the start (Fig. 3) *(excerpt)*. Cited by C038.

## Adjacent fields

- **[HoffmanMalletParet2010]** A. Hoffman, J. Mallet-Paret. *Universality of crystallographic
  pinning.* J. Dynamics and Differential Equations 22:79–119, 2010 (pages per Dialnet; journal
  and volume from memory, not confirmed in this search).
  arXiv:[0811.0093](https://arxiv.org/abs/0811.0093). Used for:
  - travelling fronts of bistable lattice reaction–diffusion equations on Z² that are pinned in
    some lattice directions while moving in nearby ones;
  - pinning in every rational direction near the sawtooth nonlinearity (earlier Mallet-Paret
    result), and generic horizontal/vertical pinning (Theorems 1.1–1.2) *(excerpt)*.

  These are fronts, not gliders, so this is an analogy only. Cited by C013.

## Search log

Each bounded search is recorded so that a later "no match" can be read against what was
actually searched.

### 2026-10-07: seed set C003, C013, C023, C026, C038–C043 (archivist)

All searches were web searches. Direct fetches were blocked (see above).

Queries covered:

- Chan 2019 on resolution, rotation invariance, niches and the taxonomy;
- Chan 2020 on multiple phenotypes;
- Lenia robustness, damage and self-repair;
- the sensorimotor-Lenia papers;
- the Lenia discretization papers (Davis, Kojima–Ikegami, Asymptotic Lenia);
- Lenia parameter-space papers (Yevenko, Hudcová);
- Particle Lenia's motivation;
- lattice anisotropy and direction pinning of travelling waves;
- Circium and static or fixed-point patterns.

Not searched:

- SmoothLife (Rafler 2011) beyond search snippets;
- Flow-Lenia;
- the Asymptotic Lenia glider-equation papers in detail;
- non-English sources.
