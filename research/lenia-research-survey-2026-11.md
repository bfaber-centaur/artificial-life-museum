# Who is working on Lenia now? (survey, 2022–2026)

Compiled 2026-11-15 for Bobby's question: "anyone doing this kind of modelling using Lenia? what
questions are they asking?" This is a map of the field, not a claims source. Nothing here changes
a status in `claims.md`.

**How it was checked.** The arXiv API was queried for every paper mentioning "Lenia" (32 hits,
2018–2026) plus searches on "continuous cellular automata", Particle/Flow/Sensorimotor Lenia and
neural-CA evolution and ecology. Crossref was queried for "Lenia" (to catch ALIFE proceedings
and journals). Every entry below was resolved by its arXiv id or DOI on 2026-11-15, and its
summary comes from the abstract returned by that API (grade *abstract*, as in
`references.md`). Three entries have no abstract available and are marked *title only* or
*project page*. Affiliations are given only where an author list makes them obvious, and
"from memory" marks the rest. Sources already in `references.md` are marked **[in refs]**.

## 1. Can Lenia evolve on its own? (open-ended evolution, populations)

This is the biggest cluster, and the one closest to our soup, replicator and reef work.

| Source | Question | Key finding |
| --- | --- | --- |
| Chan 2023, *Towards large-scale simulations of open-ended evolution in continuous CA*, arXiv:[2304.05639](https://arxiv.org/abs/2304.05639) (GECCO '23; Google) | Can Lenia run never-ending evolution with reproduction by self-replication and selection by "differential existential success"? | Runs go through a phase of diversity, then **converge to domination by fast-expanding patterns**. Chan proposes environment design, mass conservation and energy constraints as fixes. |
| Plantec et al. 2023, *Flow-Lenia: towards open-ended evolution…*, arXiv:[2212.07906](https://arxiv.org/abs/2212.07906), doi:[10.1162/isal_a_00651](https://doi.org/10.1162/isal_a_00651) (ALIFE 2023; Inria Flowers + Chan) | Can creatures with different rules share one world? | Mass conservation plus **rule parameters that flow with the matter** gives multi-species worlds where neighbouring rules can mix. |
| Plantec et al. 2025, *Flow-Lenia: emergent evolutionary dynamics…*, *Artificial Life* 31(2):228–248, doi:[10.1162/artl_a_00471](https://doi.org/10.1162/artl_a_00471), arXiv:[2506.08569](https://arxiv.org/abs/2506.08569) | Does that multi-species world actually evolve? | Measured with Bedau's **evolutionary activity** framework and other metrics; reports emergent evolutionary dynamics. |
| Michel et al. 2025, *Exploring Flow-Lenia universes with a curiosity-driven AI scientist*, arXiv:[2505.15998](https://arxiv.org/abs/2505.15998), doi:[10.1162/isal.a.896](https://doi.org/10.1162/isal.a.896) (ALIFE 2025, pp. 633–643) | Can automated search find **ecosystem-level** dynamics rather than single creatures? | IMGEP on whole-world metrics (evolutionary activity, compression, matter distribution) covers far more than random search; a scaling study over six spatial scales finds **macro-scale organization with no analogue at the base scale**. |
| Papadopoulos & Guichard 2025, *MaCE: general mass-conserving dynamics for CA*, arXiv:[2507.12306](https://arxiv.org/abs/2507.12306) | Can mass conservation be bolted onto any CA? | Yes. In Lenia it yields many solitons and "hints of intrinsic evolution in **resource-constrained** environments". |
| Suzuki, Asakura & Arita 2023, *Lenia in a petri dish: interactions between organisms and their environment in a Lenia with growth based on resource consumption*, doi:[10.1162/isal_a_00613](https://doi.org/10.1162/isal_a_00613) (ALIFE 2023) | What happens when growth costs a local resource? | *Title only* (no abstract via Crossref; MIT Press returned 403). A web excerpt of the authors' earlier Japanese paper says the resource cap strongly shapes morphology and that population-level interactions appear. Unverified. |
| Faldor & Cully 2024, *Toward artificial open-ended evolution within Lenia using quality-diversity* (Leniabreeder), arXiv:[2406.04235](https://arxiv.org/abs/2406.04235), doi:[10.1162/isal_a_00827](https://doi.org/10.1162/isal_a_00827) (ALIFE 2024; Imperial) | Can an outside evolutionary algorithm keep finding new creatures? | Quality-diversity search, with hand-set or unsupervised diversity measures, evolves a diverse population of autonomous patterns; the authors report evidence suggesting **unbounded diversity**. |
| Lorantos & Spector 2025, *Adaptive exploration in Lenia with intrinsic multi-objective ranking*, arXiv:[2506.02990](https://arxiv.org/abs/2506.02990) | Which fitness pressures keep a Lenia population exploring? | Ranking on distinctiveness, sparsity and homeostasis keeps selecting novel individuals. |
| Adachi et al. 2024, *Flow-Lenia.png*, arXiv:[2408.06374](https://arxiv.org/abs/2408.06374) | Can compressibility serve as a complexity target? | A GA hits requested complexity levels in Flow-Lenia; higher targets look more intricate. |
| Akhtyrchenko et al. 2026, *Directing open-ended evolution via multi-scale path divergence*, arXiv:[2606.17091](https://arxiv.org/abs/2606.17091) | Can a physics-style formula replace black-box novelty scores? | MSPD (how heterogeneous local rules are across scales) works as a fitness on Flow-Lenia and transfers to Life-like CA and Particle Life++. |
| Jain, Shrestha & Nichele 2023, *Capturing emerging complexity in Lenia*, arXiv:[2305.09378](https://arxiv.org/abs/2305.09378) | Which fitness functions capture long-term complexity when evolving kernels? | Three variance-based fitnesses compared over 500–2500 generations; evolved kernels drift toward Gaussian-like shapes. |
| Sayama & Nehaniv 2024, *Self-reproduction and evolution in CA: 25 years after evoloops*, arXiv:[2402.03961](https://arxiv.org/abs/2402.03961) | Review | Credits continuous CA with reviving self-reproduction research; lists open challenges. |
| Etcheverry et al. 2023, *Meta-diversity search in complex systems*, arXiv:[2312.00455](https://arxiv.org/abs/2312.00455) | Recipe for open-endedness | Lenia as an artificial "chemistry" inside Minecraft, explored by a discovery assistant ("Holmes") that learns new ways to measure diversity. |

## 2. Can a foundation model be the naturalist? (automated discovery)

| Source | Question | Key finding |
| --- | --- | --- |
| Kumar et al. 2024, ASAL, arXiv:[2412.17799](https://arxiv.org/abs/2412.17799) (Sakana/MIT, from memory) **[in refs]** | Can a vision-language model search for life? | Finds previously unseen Lenia and Boids lifeforms by matching prompts, maximizing novelty, and illuminating whole spaces. |
| Baid et al. 2025, ASAL++, arXiv:[2509.22447](https://arxiv.org/abs/2509.22447) | Can a second model invent the next target, making the search open-ended? | In Lenia, one-new-prompt-per-step gives more novelty; matching the whole prompt sequence gives more coherent lineages. |
| Khajehabdollahi et al. 2025, *Expedition & Expansion*, arXiv:[2509.03863](https://arxiv.org/abs/2509.03863) (Inria Flowers) | Novelty search plateaus; can language goals jump it to new regions? | In Flow-Lenia, VLM-written "expeditions" find more diversity, and their discoveries become stepping stones for later search. |
| Hong & Song 2026, *Expanding the mathematical foundations of artificial life…*, doi:[10.1162/isal.a.1034](https://doi.org/10.1162/isal.a.1034) (ALIFE 2026) | What lies outside the hand-picked kernel/growth families and flat geometry? | 28 kernels × 16 growth functions, on flat, **spherical, toroidal and hyperbolic** grids, plus LLM-written expressions; 291 niches, **50 new moving solitons**, and an LLM-found curvature-coupled term standard Lenia cannot express. |
| Papadopoulos et al. 2024, *Looking for complexity at phase boundaries*, arXiv:[2402.17848](https://arxiv.org/abs/2402.17848) (EPFL) | Are interesting rules near phase transitions? | A "Phase Transition Finder" more than doubles the rate of interesting Lenia behaviour. |
| Hudcová et al. 2026 **[in refs]**, Davis & Bongard 2022, arXiv:[2204.07541](https://arxiv.org/abs/2204.07541) | Mapping the rule space | Davis & Bongard rediscover gliders in 17/17 Lenia CA by selecting rules that both explode and vanish unpredictably. |

## 3. Are Lenia creatures agents? (agency, sensing, control)

| Source | Question | Key finding |
| --- | --- | --- |
| Hamon et al. 2025, Sensorimotor Lenia, *Science Advances*, arXiv:[2402.10236](https://arxiv.org/abs/2402.10236) **[in refs]** | Can search plus gradient descent find creatures that keep themselves together and navigate obstacles? | Yes. Diversity search, curriculum and gradient descent systematically find rules whose creatures move, keep their bodies and navigate obstacles, and they generalize to unseen scale changes, random updates and perturbations. |
| Cvjetko et al. 2026, *The artificial experimentalist* (CARL), arXiv:[2608.26116](https://arxiv.org/abs/2608.26116) (Inria, Tufts) | Can an RL agent **steer** creatures with tiny local nudges? | It finds solitons across many rules, steers their heading with few interventions, and lets humans guide them through mazes in real time. |
| Cool et al. 2026, *Agnosiophobia in a virtual agent* **[in refs]**, doi:[10.1162/isal.a.1012](https://doi.org/10.1162/isal.a.1012) (ALIFE 2026) | How do creatures respond when part of the world is hidden from their sensing? | Creatures move away from occluded regions ("agnosiophobia"), or die, metamorphose or explode, and lethal spots concentrate at the leading edge. |
| Horibe et al. 2023, *Adaptive behaviours of Particle Lenia*, arXiv:[2305.16706](https://arxiv.org/abs/2305.16706), doi:[10.1162/isal_a_00631](https://doi.org/10.1162/isal_a_00631) | Is Particle Lenia adaptive under perturbation? | Configurations are temporally unstable yet have multiple stable states, a candidate model for an autopoietic agent. |
| Davis 2024 (*Non-Platonic autopoiesis…*), arXiv:[2407.21086](https://arxiv.org/abs/2407.21086), doi:[10.1162/isal_a_00786](https://doi.org/10.1162/isal_a_00786); Strozzi 2022, arXiv:[2205.00209](https://arxiv.org/abs/2205.00209) | What counts as an individual? | Davis: an Asymptotic Lenia glider survives only at coarse resolution, with fractal instability maps. Strozzi: an essay on telling a soliton from its environment. |

## 4. Can gliders compute?

| Source | Question | Key finding |
| --- | --- | --- |
| Gupta 2026, *Collision-based logic in Lenia and its composition boundary*, arXiv:[2609.01348](https://arxiv.org/abs/2609.01348) | Can fixed-rule Lenia compute by collisions, like Life? | Orbium is the only glider found that survives a collision intact; collisions build an **INHIBIT gate** that works at all 24 breathing phases, and two in series make an AND-NOT chain. Open problem: re-routing a deflected signal to a second gate. |

## 5. What is Lenia mathematically? (theory and numerics)

| Source | Question | Key finding |
| --- | --- | --- |
| Calcaterra & Boldt 2023, *Existence of life in Lenia*, IJDSDE 13(3):218–230, arXiv:[2203.14390](https://arxiv.org/abs/2203.14390) | Does Lenia's update even define a well-posed flow? | Standard theorems fail (discontinuous vector field), but arc-field theory proves Euler curves converge to a unique flow. |
| Kojima, Yevenko & Ikegami 2025, *The glider equation for Asymptotic Lenia*, arXiv:[2508.04167](https://arxiv.org/abs/2508.04167) | Can gliders be solved for rather than searched for? | Derives a glider condition and uses it as a loss; gradient descent finds gliders, including faster ones; links Lenia to neural field models. |
| Yevenko, Kojima & Nehaniv 2025, arXiv:[2508.02935](https://arxiv.org/abs/2508.02935), doi:[10.1162/isal.a.834](https://doi.org/10.1162/isal.a.834) (ALIFE 2025) | Can dynamical-systems theory measure complexity? | Explains four solution classes; global attractor of fractal dimension > 4; Kaplan–Yorke dimension as a complexity measure. |
| Davis & Bongard 2022, *Step size is a consequential parameter*, arXiv:[2205.12728](https://arxiv.org/abs/2205.12728); *Glaberish*, arXiv:[2205.10463](https://arxiv.org/abs/2205.10463); Kojima & Ikegami 2023 **[in refs]**; Davis 2024 **[in refs]**; Yevenko 2024 **[in refs]** | Are creatures properties of the equations or of the simulation? | Some gliders die at too-small *and* too-large step sizes. Same theme as our REEF-M0 calibration. |

## 6. Neural CA and particle crossovers

| Source | Question | Key finding |
| --- | --- | --- |
| Mordvintsev, Niklasson & Randazzo 2022, *Particle Lenia and the energy-based formulation*, [project page](https://google-research.github.io/self-organising-systems/particle-lenia/) (no paper) | Lenia with particles instead of a grid | Particles descend a repulsion-plus-growth energy; easy to scale to 3-D. Our C067 pinwheel uses it. |
| Zhang, Risi & Darlow 2025, Petri Dish NCA, [project page](https://sakanaai.github.io/pdnca/) (Sakana) | Can NCAs that keep **learning by gradient descent while they compete** complexify open-endedly? | Early signs of emergent complexity and cooperation. *Project page*; no arXiv id found. |
| Berdica et al. 2026, *Evolving many worlds* (PBT-NCA), arXiv:[2604.11248](https://arxiv.org/abs/2604.11248) | PD-NCA collapses to frozen or noisy states; can meta-evolution prevent that? | Population-based training rewarding novelty and diversity produces travelling waves, **spore-like colonization** and migrating macro-structures. |
| Randazzo & Mordvintsev 2023, *Biomaker CA*, arXiv:[2307.09320](https://arxiv.org/abs/2307.09320) (Google) | Can CA "plants" grow, reproduce with variation and form biomes in a nutrient-starved world? | Stable and unstable biomes; meta-evolution and interactive evolution of plant models. |
| Barbieux & Canaan 2024, *Coralai*, arXiv:[2406.09654](https://arxiv.org/abs/2406.09654) | NCA ecosystems with merging and mutation | Competition between sessile and mobile organisms, **resource depletion–recovery cycles**, symbiosis. |
| Sinapayen 2023, arXiv:[2305.13043](https://arxiv.org/abs/2305.13043) | Can NCA replicators mutate without being trained to? | Self-replicating patterns with inheritable spontaneous mutations and exponential genetic drift, even when deterministic. |
| Kim et al. 2026, *Neural Particle Automata*, arXiv:[2601.16096](https://arxiv.org/abs/2601.16096); Zhang et al. 2026 (ALIFE 2026), arXiv:[2606.23115](https://arxiv.org/abs/2606.23115); Faldor & Cully 2024, CAX, arXiv:[2410.02651](https://arxiv.org/abs/2410.02651) | Tools and inductive biases | Learnable particle CA; mass conservation pushes NCA reservoirs toward criticality; a JAX CA library. |

Outliers: Kayama's *Semantic Lenia* (arXiv:[2608.11657](https://arxiv.org/abs/2608.11657)) borrows
Lenia's homeostasis idea for steering LLM text, and Kayama 2025 (*Artificial Life and Robotics*,
doi:[10.1007/s10015-025-01081-7](https://doi.org/10.1007/s10015-025-01081-7), *title only*) studies
metamorphic transitions under dynamic growth.

## Who the groups are

- **Inria Flowers (Bordeaux)**: Oudeyer, Moulin-Frier, Hamon, Etcheverry, Plantec, Michel, Cvjetko,
  often with Chan. Flow-Lenia, Sensorimotor Lenia, curiosity-driven discovery, CARL.
- **Bert Chan** (Lenia's author; Google): no first-author Lenia paper found after the 2023 GECCO
  paper; co-author on Flow-Lenia, Sensorimotor Lenia and meta-diversity search.
- **Sakana AI**: ASAL, Petri Dish NCA.
- **Google self-organising systems** (Mordvintsev, Randazzo, Niklasson): Particle Lenia, Biomaker CA.
- **Tokyo / Ikegami lab and collaborators** (Kojima, Yevenko, Nehaniv): Asymptotic Lenia theory.
- **Davis & Bongard (Vermont)**: numerics, Glaberish, rule evolution.
- **Imperial (Faldor & Cully)**: quality-diversity, CAX.
- **EPFL (Hongler, Papadopoulos, Hudcová)**: phase boundaries, MaCE, parameter-space maps.
- **Levin lab (Tufts)** appears as co-author on Cool 2026 and CARL.

## Gaps the museum could fill

1. **Ecology numbers, not just pictures.** Nobody we found counts Lenia individuals over time
   the way ecologists do (births, deaths, carrying capacity, predator–prey cycles, extinction
   times). Flow-Lenia work uses evolutionary activity and whole-world metrics. We already have
   a tracker (reef behaviour lane) and an evolution soup, so a census of a soup, with a
   population curve and a carrying-capacity fit, would be new as an exhibit.
2. **Predator–prey.** No Lenia or Flow-Lenia paper in this search reports predation. Coralai and
   PD-NCA report competition and cycles in neural CA, not in Lenia.
3. **Chan's "fast expanders win" result as a reproducible test.** Our soup's early-takeover
   charts look like the same outcome. Testing Chan's proposed fixes (resource cost, mass
   conservation) one at a time would answer a question he left open.
4. **Resource-limited growth.** Suzuki et al. 2023 and MaCE point at it; neither is something we
   could read in full. A resource channel in our engine is cheap.
5. **Spatial structure and drift.** Our "So what?" wing showed lattice vs mixed epidemics and
   Moran drift. No Lenia paper tests how world geometry or patchiness changes which lineage wins.
6. **Overlaps to cite, not repeat.** Gupta 2026 builds collision logic from Orbium (relevant to
   our collision zoo, C080–C083). Hong & Song 2026 run Lenia on spherical, toroidal and
   hyperbolic grids (relevant to our strange-geometries rooms). Davis, Kojima and Calcaterra
   cover the numerics our REEF-M0 calibration measured.
