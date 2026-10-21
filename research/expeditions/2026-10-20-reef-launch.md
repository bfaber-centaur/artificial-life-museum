# Coexistence-Reef: authorized expedition launch

**Authorization:** Bobby authorized the expedition on October 20, 2026 (Pacific): “we're ready for the expedition … let us off into the wilds”. This lifts the measurements-only gate for the scoped work below. Authorization is not evidence that workers have started.
**Repository:** bfaber-centaur/artificial-life-museum.
**Scientific baseline:** main `ca260c1944bd531b0f882a517cad284c9547c3b1`, after PRs #35–39. Pin the launch-packet commit separately in every lane.
**Status:** execution mandate, not executed encounter evidence. This supplements the original Reef directive and supersedes its measurements-only gate. Research merges remain human decisions.

## Mission and discretion

Lead one coherent expedition: **at mu=.155, sigma=.020, what does first contact with S103 do to a moving Orbium-like glider and to the ring, relative to their matched isolated futures?**

The most informative contrasts are passage/deflection versus capture or transformation, and contact-induced failure versus an isolated-control or numerical failure. A clean null, a failed coexistence premise, or an exposed torus artifact is a complete result. S001, S101–S103 are catalogued forms.

The bounded discovery lane explores glider phase and transverse offset around an informative pilot. Preserve room for a strange encounter without promoting appearance into a claim.

You may implement missing instruments, run controls and encounters, retry broken runs, investigate an anomaly, and stop unproductive work without asking Bobby. Commit decisions before the runs they govern. Escalate a change of scientific question, rule retuning, specimen substitution, or an unresolved scientific ambiguity that changes the interpretation. Routine coding, placement, scheduling and analysis choices are yours.

Do not automatically pivot to S102, resume off-gap pulse/blend scans, build orchestration infrastructure, or rewrite the engines. Keep raw evidence and failed predictions. Integrate on an expedition branch; do not merge to main.

## Read once, then use exact evidence

Read README.md, research/charter.md, research/roadmap.md, research/reports/synthesis-2026-10-08.md, relevant claims C038–C043 and C046–C051, the original Reef directive, and research/reports/reef-environment-measurements-2026-10-20.md. Follow references where a decision depends on code/results.

PR #35 is now merged but its off-gap and boundary work remains exploratory/unverified. Later merged closeout evidence outranks stale ledger summaries; add dated amendments without erasing old verdicts. C039's general resolution-death interpretation was refuted; resize method matters. S102 refined survivors are finite-horizon observations. The S101 on-gap pulse unbound two living Orbia; later torus collisions explained apparent death. C041's port-injury resilience was largely the untouched partner.

Reuse alm, alm_check, L6-field utilities, specimen dossiers and existing rendering. field.py shares alm kernel/growth and supplies whole-world measurements, not an independent engine or body tracker. alm_check FFT is independently implemented but uses the same NumPy FFT arithmetic. Its direct convolution supplies a different arithmetic route.

## Organization and ownership

Keep one coordinator and three substantive specialist threads warm. Start the specialists together; seed validation, numerical preparation, and tracking/review design can proceed independently. Each thread has its own checkout and resources: exchange committed SHAs and artifacts, never assume shared local files.

| Lane / branch | Ownership | First assignment and interface |
|---|---|---|
| Coordinator / reef/coordinator | research/experiments/REEF/ coordination files; integrated report; claims and references; final integration | Freeze protocol and interfaces, assign work, review evidence, import named commits, resolve disagreements. Own the shared manifest schema. Do not become the main runner. |
| Field / reef/field | research/experiments/REEF-field/ | Validate and export settled seeds, phase states and matched-control manifests; build encounter runner; perform six pilots then the bounded exploration. Consume the reviewed tracker and return raw states/traces. |
| Numerics / reef/numerics | research/experiments/REEF-numerics/ | Reproduce the S103 fixed-point check and prepare alm_check replay from serialized inputs. Check selected encounters with FFT/direct arithmetic and numerical/world changes. Own independent verdicts, not field code. |
| Behavior and hostile review / reef/behavior | research/experiments/REEF-behavior/ | Implement minimal torus-aware body tracking; test known translation, wrapping, merging and splitting cases. Specify measurable outcomes and rival explanations. Audit pilot traces, perform bounded catalog/literature checking, and prepare one earned exhibit. |

No lane edits another lane's files. Put reusable new code in the owning experiment directory initially. Coordinator approves shared-source changes explicitly and records ownership. Coordinator alone edits claims and the integrated report. Every handoff includes commit, input hashes, command, output paths, caveats and the next dependency.

## Before encounters: freeze a runnable contract

Create research/experiments/REEF/PROTOCOL.md, DECISIONS.md, STATUS.md and a machine-readable run manifest. Record predictions, classifications, thresholds, censoring and pilot geometry before encounter results are examined.

Primary semantics: float64, existing poly/poly kernel/growth, Euler plus clip, mu=.155, sigma=.020, R13, T10, periodic boundaries. Start with N256 for isolated controls. Preserve the full numeric rule and seed transforms in manifests.

1. Reproduce S103's existing exact fixed-point test as the known-result check. Run the existing relevant engine tests; obtain the charter's pinned upstream reference for skipped comparison tests if accessible, otherwise report the missing check without claiming it passed.
2. Establish the S001-derived moving phenotype under the coexistence rule. Its native-rule trajectory is not a control. Use an existing documented coexistence seed if available, preserving provenance; otherwise settle the catalog seed under the fixed rule. Save the state and hash after a declared settling procedure.
3. Use a provisional 100-tu settling interval and 100-tu assessment interval. The field lane may extend once to 500 tu total if a transient remains, documenting the reason. Derive moving/static thresholds and mass/morphology tolerance from isolated baselines, then freeze them before encounters. These are operational finite-horizon acceptance criteria, not an attractor test.
4. Validate both isolated phenotypes through the complete intended approach plus follow-up horizon. Measure actual unwrapped heading and speed. Export two genuinely distinct glider phase snapshots if periodicity supports that interpretation. Otherwise use two explicitly named elapsed-time snapshots; do not invent a phase cycle. S103 has no internal phase at its primary fixed point.
5. The tracker must distinguish initial labels from later connected components. During merger/splitting or identity ambiguity, report component topology and unassigned mass; do not force two centroids to persist. Define support threshold, contact, interaction onset and class thresholds explicitly. Kernel-range interaction can precede visible support overlap.
6. Use measured support, heading and speed to choose geometry. Begin with disjoint supports and about 3–5R clear approach distance. Prefer translations over interpolated rotation. Record integer rounding and realized offset. If N256 cannot provide a useful uncontaminated window, move the primary setup to N512 before pilots and rerun matched controls; record this choice, without changing physical seed size.
7. Default target: 20 tu of post-first-contact observation, with an approach timeout of 30 tu. Validate that these are useful with isolated geometry before freezing them. Track periodic images and unwrapped trajectories; censor before a possible distinct torus re-encounter, using a conservative guard where attribution is ambiguous. A boundary crossing alone is not a second encounter. A no-contact timeout and a censored outcome remain valid records.
8. Time one short real runner segment with tracking and checkpoint output. This fills the calibration omission; do not restart a benchmark campaign.

Gate A passes when moving/static controls, serialization, tracking and the first-contact/censoring contract are usable. Coordinator plus reviewer can pass this gate without another human approval. If the fixed-rule moving control cannot be established within the bounded preparation, stop encounters and report that scientific crux to Bobby.

## First experiments and bounded exploration

**Gate B: six pilot geometries maximum.** Use b/R = -1, 0, +1 crossed with the two declared glider snapshots. Place the ring relative to each snapshot's measured heading. For each encounter run the glider alone and ring alone with identical states, transformations, rule, numerics, world and scheduled horizon. Share a control only when every relevant input and measurement contract is identical, and record the mapping. Interleave encounter/control jobs with a fixed recorded schedule seed.

Score component count, total/component mass, displacement, speed/heading change relative to control, ring change, contact/interaction times, and censor reason. Store before/contact/after arrays. A “miss” is not a null response to contact.

After reviewing all six, choose two contrasting cases for independent checking: the clearest candidate effect and its nearest observed different outcome; if all look alike, choose the closest encounter and a flank/no-contact case. Commit the selection rule and chosen IDs before checking. Independent reruns test reproducibility; deterministic timesteps and frames are not independent statistical replicates.

**Discovery allowance: at most 12 additional encounter geometries**, each with matched controls. Before running them, commit the local offset/snapshot grid and the question it distinguishes. Use offsets within the original [-1.5R,+1.5R] range. Prefer narrowing a transition or testing an explanation over filling a grid. Numerical checks and necessary clean reruns are separate from this geometry allowance, but still obey time limits. No automatic expansion because CPU is cheap.

## Minimum checking and promotion

For both selected contrasts, require:
- a clean-process exact-input replay;
- alm_check FFT implementation replay;
- a direct-convolution window starting from the same saved pre-interaction state and including the outcome-defining event; extend if 20 tu is insufficient, or label the check incomplete;
- timestep T20 at fixed mu/sigma;
- R26 with explicit block replication, doubling N to preserve world size in R units;
- a larger world at unchanged R and unchanged seed size, preserving initial physical separation and phase.

Each altered setting needs its own matched isolated controls. Separate effects of changing T, R and world size. Never tune sigma to rescue the comparison silently. Existing T40 evidence includes a STATIC Orbium outcome at this rule: if refinement changes the isolated phenotype, report the resulting limitation on comparison and any numerical fragility, rather than calling encounter behavior converged.

Use quantitative observables and event classifications with tolerances fixed before independent results. Long trajectories need not remain bitwise equal across arithmetic routes. If a small mismatch changes the outcome, investigate and report sensitivity; do not average it away.

Exploration produces OBSERVED candidates with exact scope. REPRODUCED requires a clean rerun; INDEPENDENTLY_CHECKED requires the independent evidence relevant to the stated claim, with every failed or omitted check disclosed. Refinement failures warrant narrowing or NUMERICALLY_FRAGILE. “Persistent capture” means only capture through a stated, uncontaminated horizon. Novelty requires catalog/literature comparison; an unsuccessful search is not proof. Earn nicknames under the charter's criteria.

## Time, compute, stop and pivot rules

Default expedition window: up to six elapsed hours from coordinator start, finishing earlier when the question is answered. Stop adding exploratory geometries after hour four. Protect at least the final 15–20% of total effort for checking, reconciliation, an earned exhibit and reproducible handoff; start independent checks earlier rather than leaving all checking to the end. Log start/deadline in UTC and Pacific. Do not fill time just to consume inference.

Use two simulation processes per session by default, numerical-library thread variables set to one. Four processes require a short check with the actual instrumented workload. Plan using the slower measured host. The eight-minute calibration estimate excluded tracker/I/O and is not an expedition-duration promise. Save bounded checkpoints, selected states and hashes; avoid bulk frame dumps in git.

Workers may retry an infrastructure failure, make one documented repair, investigate a discriminating anomaly, record a null, or stop a broken run. Preserve failed outputs and corrected versions. Stop new encounters if controls fail, tracking loses attribution needed for the claim, or torus contamination cannot be excluded. Continue useful diagnosis and reporting. Escalate changes of rule/specimen/question to Bobby; if unavailable, bank the evidence rather than silently pivoting.

Use abundant inference for competing mechanistic explanations, a discriminating next experiment, code inspection, independent reproduction and readable exposition. Do not multiply identical agents or grow the sweep to spend tokens.

## Deliverables and handoff

The coordinator keeps STATUS.md current at gates and meaningful failures. Escalations contain the scientific crux, exact evidence, two options and a recommendation; avoid routine status questions.

Finish with:
- committed preregistration, decision log, complete run registry including nulls/failures/censoring, exact code/environment versions and hashes;
- independently checked contrasts with an explicit comparison matrix, or a clear account of why none earned promotion;
- research/reports/reef-expedition-2026-10-20.md: strongest result, best failure, remaining disagreement, next three experiments and shortest reproduction commands;
- dated, history-preserving claim amendments limited to relevant C038/C041/on-gap wording and new evidence; no repository-wide cleanup;
- one evidence-backed exhibit with matched-control panels, time/length scales, world/numerical settings, run IDs and finite-horizon captions; a failure/null exhibit is welcome;
- one integration PR from reef/coordinator, importing reviewed lane commits with dependencies and validation legible. Preserve full histories. Bobby merges.

If time expires or access fails, leave a reproducible partial handoff. Never report launched, completed, checked or merged work unless it actually happened.
