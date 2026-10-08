# Artificial-Life Museum — Night 0

## Mission

Stand up a small scientific field station in **classic 2-D Lenia** and return with at least one experimentally defensible behavioral claim about a known organism — plus, if fortune smiles, a genuinely interesting specimen of our own.

The unit of progress is **not code written** and not “cool GIF found.” It is a **specimen + reproducible claim + intervention + evidence**.

Working motto:

> Sir Wobbles must earn his name.


## Fixed project environment

### Repository

All Night-0 work belongs in exactly one active repository:

```text
bfaber-centaur/artificial-life-museum
```

Treat that repository as the durable scientific record: code, tests, experiment manifests, specimen dossiers, claims, traces, plots, and reports all live there.

Do **not** create additional coordination, experiment, or setup repositories during Night 0.

The upstream Lenia repository is a **pinned external reference**, not a second project repository and not a fork:

```text
Chakazul/Lenia
commit: adfc542939266de7f4bb7ebb552e8499701ee107
```

Clone it locally under:

```text
.refs/Lenia/
```

`.refs/` is intentionally gitignored.

Do not modify upstream Lenia in place. If the project later establishes that simulator-internal changes are necessary, earn that fork explicitly with a concrete experimental need.

### Runtime / toolset

Use modern Python 3 in a local virtual environment.

Initial scientific stack:

```text
numpy
scipy
pillow
matplotlib
imageio
pytest
```

Do **not** install upstream `Python/requirements.txt` wholesale. Its dependency pins are historical and are not the runtime contract for this project.

The project's own dependencies should become authoritative through a committed `pyproject.toml` as one of the first coordinator/infrastructure commits.

The upstream Lenia checkout is used for:

- semantic/reference archaeology;
- canonical organism data such as `animals.json`;
- behavioral comparison;
- independent cross-checking where practical.

It is **not** the primary runtime architecture for ALM.

### Baseline bootstrap

The cloud environment should be recoverable with a repository-owned bootstrap script. Until that exists, the intended bootstrap semantics are:

```bash
set -euxo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel

python -m pip install \
  numpy \
  scipy \
  pillow \
  matplotlib \
  imageio \
  pytest

LENIA_SHA=adfc542939266de7f4bb7ebb552e8499701ee107

mkdir -p .refs
if [ ! -d .refs/Lenia/.git ]; then
  git clone https://github.com/Chakazul/Lenia.git .refs/Lenia
fi

git -C .refs/Lenia fetch origin "$LENIA_SHA"
git -C .refs/Lenia checkout --detach "$LENIA_SHA"

mkdir -p \
  research/specimens \
  research/experiments \
  research/traces \
  research/reports

python - <<'PY'
import numpy, scipy, PIL, matplotlib, imageio
print("ALM environment ready")
print("numpy:", numpy.__version__)
print("scipy:", scipy.__version__)
PY

echo "Lenia reference: $(git -C .refs/Lenia rev-parse HEAD)"
```

The coordinator should turn this into:

```text
scripts/bootstrap.sh
pyproject.toml
```

and from then on the expected setup path is simply:

```bash
./scripts/bootstrap.sh
```

### Architectural decision

Build the actual Night-0 experimental kernel under this repository, e.g.:

```text
src/alm/
```

Do not make ALM's scientific runtime depend on importing or wrapping the entire upstream interactive Lenia program.

Lane 2 should implement the smallest headless classic-2D Lenia semantics needed for the experiments. Lane 3 should independently cross-check those semantics against upstream behavior and/or a distinct implementation path.

This separation is intentional: simulator agreement is evidence; shared implementation is not.

### Initial repository shape

Prefer this minimal layout:

```text
artificial-life-museum/
  pyproject.toml
  scripts/
    bootstrap.sh
  src/
    alm/
  tests/
  research/
    charter.md
    claims.md
    specimens/
    experiments/
    traces/
    reports/
  .refs/Lenia/        # local only, gitignored
```

The current `.gitignore` already excludes:

```text
.venv/
.refs/
__pycache__/
.pytest_cache/
```

Do not add orchestration infrastructure merely to support agent parallelism. Git branches/PRs, small scripts, files, and explicit research contracts are sufficient for Night 0.


## Scope boundary

For Night 0:

- Use classic 2-D Lenia.
- Prefer the original Chakazul/Lenia implementation and canonical catalog as the reference source.
- Start from a known, stable lifeform (Orbium is the obvious baseline).
- Headless/reproducible experiments matter more than UI.
- Do not build a general ALife platform.
- Do not jump to multichannel Lenia, Flow Lenia, 3-D, open-ended evolution, foundation-model novelty metrics, or a museum frontend unless the core experiment is already complete.
- Do not call a form “new” merely because we have not recognized it. “Uncatalogued candidate” is fine.

## Organizing question

**Which measurable properties of a Lenia specimen predict whether it survives a standardized disturbance?**

Night 0 does not need a grand theory. One trustworthy local result is enough.

Examples of acceptable claims:

- survival changes sharply across a particular perturbation-strength interval;
- two visually similar states have meaningfully different recovery behavior;
- one simple pre-perturbation feature predicts recovery within a bounded neighborhood;
- a behavior disappears under a modest numerical-resolution change, revealing an artifact;
- a candidate organism exhibits a repeatable response not seen in the baseline organism.

“Looks robust” is not a claim.

## Required shared artifacts

Create these early so lanes can coordinate without depending on chat history:

```text
research/
  charter.md
  claims.md
  specimens/
  experiments/
  traces/
  reports/
```

### `claims.md`

Every substantive claim gets an ID and one of:

- OBSERVED
- CONJECTURED
- REFUTED
- REPRODUCED
- NUMERICALLY_FRAGILE
- INDEPENDENTLY_CHECKED

Each claim records:

- exact specimen/version;
- simulator/version;
- parameters;
- intervention;
- metric;
- run IDs;
- search or parameter bounds;
- known caveats.

### Specimen dossier

Each specimen gets:

- stable ID;
- provenance;
- complete initial state or exact reconstruction instructions;
- Lenia parameters;
- preview/render;
- baseline behavior metrics;
- tested perturbations;
- claims supported/refuted;
- numerical-stability notes;
- nickname only after the stable ID exists.

## Overnight organization

Run several coherent lanes in parallel. Keep them opinionated and independent; reconcile by evidence rather than by consensus.

### Lane 0 — Coordinator / Archivist

Own the charter, shared interfaces, claim ledger, and integration.

Responsibilities:

- preserve provenance;
- prevent scope expansion;
- make disputed interpretations explicit;
- require run IDs and reproduction commands;
- assign fresh-context reproduction when a claim becomes interesting;
- produce the morning report.
- keep literature provenance for substantive claims: when a claim is reproduced, independently
  checked or proposed as new, run one bounded search of the Lenia literature, the catalog and
  adjacent work, and record it in the claim's **Prior literature** field and in
  `research/references.md` (rules in `claims.md`, "Literature provenance"). Literature agreement
  is never reproduction, and a failed search is never novelty.

Do not become the main implementer.

### Lane 1 — Reference Naturalist

Read the original Lenia paper/repository closely enough to identify:

- canonical equations and parameter conventions;
- a known baseline organism and exact starting state;
- what existing statistics/instruments already measure;
- taxonomy/provenance needed to avoid “rediscovering” known forms.

Deliver a short reference dossier. Separate “paper says” from “implementation does.”

### Lane 2 — Simulation & Instrumentation

Create the smallest reliable headless experimental runner around the reference implementation, or reproduce the required semantics faithfully.

Every run must emit:

- simulator commit/version;
- specimen ID;
- parameters;
- random seed if any;
- timestep / grid settings;
- intervention;
- per-step or periodic measurements;
- final state;
- reproduction command.

Prefer machine-readable traces.

### Lane 3 — Independent Replication / Numerical Red Team

Challenge the simulator.

At minimum:

- reproduce the baseline organism independently or through a distinct execution path;
- vary timestep and/or spatial resolution enough to detect obvious numerical artifacts;
- check boundary-condition assumptions;
- compare a few summary traces against Lane 2.

If the two implementations disagree, that disagreement becomes the highest-priority specimen.

### Lane 4 — Disturbance Laboratory

Define a small standardized perturbation battery before looking for exciting results.

Start with 2–4 interventions such as:

1. **Localized deletion:** zero or attenuate a circular patch at a controlled location/radius.
2. **Mass attenuation:** multiply the whole state by a factor.
3. **Localized addition:** add a bounded Gaussian patch, clipping according to Lenia semantics.
4. **Geometric injury:** remove or displace a controlled fraction of one side of the organism.

Sweep strength coarsely, then binary-search or locally refine interesting transitions.

Define “survival/recovery” numerically before using it:
for example bounded mass, persistent coherent localization, and resumed displacement over a fixed post-intervention horizon.

### Lane 5 — Morphometrics / Behavior

Measure interpretable features, not a giant feature soup.

Good initial candidates:

- total mass;
- centroid;
- translational velocity;
- radius / second spatial moment;
- anisotropy;
- approximate rotational symmetry;
- compactness or occupied area;
- oscillation period / dominant temporal frequency;
- recovery time after intervention.

Try to explain a transition with the smallest useful feature set.

### Lane 6 — Field Exploration

Only after the baseline is reproducible, search a bounded neighborhood of organism/rule parameters or initial conditions.

Goals:

- find alternate stable phenotypes;
- find unusual but repeatable responses to the standard disturbance battery;
- identify candidates that differ behaviorally, not merely cosmetically.

Every candidate must be re-run from a clean process and saved as a specimen dossier.

This lane is authorized to propose nicknames.

### Lane 7 — Hostile Reviewer

Continuously attack emerging claims.

Ask:

- Is the metric just measuring translation?
- Did the intervention accidentally change total mass more than intended?
- Is “recovery” merely a new stable blob?
- Is the result tied to one grid size?
- Did visible morphology bias the interpretation?
- Is the “new” specimen already catalogued?
- Could a trivial baseline explain the result?
- Did anyone choose the threshold after seeing the answer?

Convert criticism into executable tests whenever possible.

## The Night-0 experiment

### Baseline

Use a canonical stable Lenia lifeform, preferably Orbium unless the reference lane finds a better baseline with cleaner provenance.

Run long enough to establish:

- bounded/stable mass behavior;
- expected locomotion or periodic behavior;
- approximate steady morphology;
- sensitivity to timestep/resolution.

### Perturbation assay

For each chosen perturbation type:

1. choose a fixed intervention phase/time;
2. sweep perturbation strength;
3. measure survival/recovery over a fixed horizon;
4. repeat enough nearby runs to distinguish a sharp transition from numerical noise;
5. save representative before/during/after states;
6. minimize any surprising case.

The ideal overnight result is something like:

> For specimen S001 under intervention I002, recovery is robust below strength X, fails above Y, and the transition is reproduced in two execution paths. Feature F changes before visible collapse and predicts the outcome across the tested neighborhood.

The numbers can be humble. The epistemics should be strong.

## Discovery protocol: earning “Sir Wobbles”

A candidate gets a nickname only when all of these are true:

1. It has a stable specimen ID and serialized state.
2. It survives a clean-process rerun.
3. Its interesting behavior survives at least one modest numerical-resolution/timestep perturbation.
4. The behavior is demonstrated by an intervention or measurable prediction, not only appearance.
5. A reference check has failed to identify it as an obvious canonical specimen.
6. A second lane independently reproduces the behavior.

If a candidate fails one of these, keep it. Failed organisms are part of the natural-history collection.

## Stop conditions

Night 0 is successful if **any one** of these happens:

- a known organism has a clean, replicated disturbance-response curve;
- an apparent robustness claim is killed by a numerical artifact and documented clearly;
- a behavioral predictor survives hostile review;
- an uncatalogued candidate earns a specimen dossier and a replicated behavioral claim.

Night 0 is *not* improved by adding a web UI, distributed job queue, general experiment DSL, large taxonomy, or elaborate novelty model before one of those occurs.

## Morning deliverable

Write `research/reports/night-0.md` containing:

1. **What exists now** — runnable infrastructure and specimen count.
2. **Best result** — the strongest checked claim, with exact run IDs.
3. **Best failure** — the most instructive refutation or artifact.
4. **Best creature** — candidate specimen, whether or not it earned a nickname.
5. **Disagreements** — unresolved semantic/numerical disputes.
6. **Evidence gallery** — a few plots/renders/traces, not dozens.
7. **Reproduction** — the shortest commands a fresh researcher needs.
8. **Next three experiments** — chosen for information value, not breadth.

Finish with a one-paragraph recommendation:
**continue this organism/question, pivot to another phenomenon, or stop.**

## Coordinator launch instruction

You are coordinating Night 0 in:

```text
bfaber-centaur/artificial-life-museum
```

Treat this as a scientific investigation, not a feature-development sprint.

Your first job is to make the repository self-recovering: commit `pyproject.toml`, `scripts/bootstrap.sh`, the research directory skeleton, and this charter (or an equivalent checked-in `research/charter.md`). Keep the pinned upstream Lenia checkout external under `.refs/Lenia/`.

Then spawn the lanes above as persistent specialists where useful. Give each lane a clear ownership boundary and have it work through branches/PRs or similarly legible handoffs. Let lanes disagree. Preserve their outputs in the repository.

When interpretations diverge, prefer running the discriminating experiment over discussing the disagreement. Keep contexts warm enough to accumulate domain expertise, but periodically assign a fresh-context worker to reproduce important results.

Do not optimize for token thrift. Optimize for durable evidence.

Do not create another repository, general orchestration framework, job system, dashboard, or museum UI during Night 0 unless a completed scientific result demonstrates a concrete need.

The overnight priority ordering is:

1. reproducible baseline organism;
2. trustworthy headless simulator;
3. independent semantic/numerical cross-check;
4. standardized perturbation assay;
5. one checked behavioral claim;
6. bounded exploration for interesting specimens;
7. exposition.

If something genuinely weird, stable, and reproducible appears:

you are permitted to call it **Sir Wobbles**.
