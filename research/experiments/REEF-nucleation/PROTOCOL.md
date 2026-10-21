# Empty-world nucleation v1 — preregistered 2026-10-21

Independent follow-up branch based on PR #41's frozen head
190b2b9dbb056105db714f9eef88c3de1a8935cd. No original files or claims altered.
Commit this protocol, runner and tests before collecting simulation results.

## Question and interventions
Can a compact passive Gaussian seed nucleate an expanding colony without S103?
A positive result falsifies universal S103 necessity at this discrete rule. Negative
results only bound these seed families and horizons, not all possible nuclei.
Deterministic runs are experimental conditions, not statistical replicates.

Reuse alm.lenia and the REEF behavior component tracker. Primary rule: poly/poly,
beta=[1], mu=.155, sigma=.020, R13/T10/N256, float64 Euler with hard clipping,
periodic boundary. No input clipping allowed. Schedule seed 20261021, no stochastic
state noise. Single process, one numerical thread. Every run has H=25 tu; sample
mass and boundary guard every step, morphology and float64 snapshots each tu.

Family A: exact stored X9 masked blob, scaled by .25, .5, .75, 1, 1.25, 1.45.
At .5/.75/1 this matches the stored X11/X12/X9 inputs, including the one-cell
ring-overlap mask. Integer translation recentres the seed; no interpolation.
Family B: unmasked 4-sigma-truncated Gaussian with the same fractional centre,
peak parameter a=.680108174486775, sigma=s_X9*sqrt(dose), doses 1.5,2,3,4,6,8,12,16.
This extends target mass to ~7.8 R² without clipping. Width and mass covary;
this is a separate nucleation family, not a pure amplitude threshold. Record
actual mass, peak, gyradius and support radius rather than assuming nominal mass.

Controls: blank world; exact S103 alone at contact placement; original contact
pairs X11 (.5, expected non-growing), X12 (.75, expected colony), X9 (1, expected
colony). All have identical numerics, translations, horizon and measurement.
Family A .5/.75/1 are their matched blob-alone controls. A failed positive or
negative control invalidates the corresponding mechanistic comparison.

## Frozen operational outcomes
Mass M=sum(A)/R²; support A>=.01; bodies are torus-8-connected components with
support mass >=.005 R² (REEF convention). Radius is maximum support distance
from the initial blob centre, in R. It measures spread, not a fitted wave speed.
Use the last six integer-tu observations (five-tu window), and require at least
10 tu of observation. Score at H or the last observation strictly before censoring.

In order:
* EVAPORATION: M<1e-10 throughout the last five tu.
* EXPANDING_COLONY: throughout that window M>=max(2,4*M_initial) and bodies>=4;
  last-minus-first mass increase >=.5 and radius increase >=.5 R; final radius
  >= initial radius+2 R. This is an operational proliferating/spreading colony;
  it does not establish ring/dumbbell identity or a stationary interior.
* SUSTAINED_GROWTH: same mass floor and increase, without the colony topology/
  radius requirements. Finite-window only, not asymptotic growth.
* STABLE_LOCALIZED: positive mass >=.01, radius<=3 R throughout last five tu,
  mass range <=1% of mean and radius range<=.1 R. Allows bounded oscillation;
  does not assert a fixed point. Also record maximum per-tu state change.
* UNRESOLVED otherwise. Do not force transient or moving structures into a class.

Censor at the first step with any A>1e-12 within R cells of a boundary. This
conservative guard prevents opposite active edges coupling through wrap; discard
that step and later observations from classification. Report censoring separately,
including an early partial class; <10 tu gives UNRESOLVED. Never call saturation
on the torus a negative growth result. H remains finite even without censoring.

## Reproducibility and numerical checks
Write plan before stepping; immutable output directory; inputs/final/snapshots,
per-step mass/guard and per-tu morphology, state/file hashes, protocol and runner
hashes, git SHA/status, dependency versions, parameters and ordered conditions.
Source seed hashes must match their original sidecars. Preserve all outcomes.

Bounded pilot: primary 19 conditions (14 seeds + 5 controls), <=250 steps each.
After primary results, select the lowest nominal-dose empty-world colony and its
nearest lower-dose non-colony within that family (if no colony, use A1.45 and B16).
Check those plus the .5/.75 contact controls, ring and blank at N512/T10 and
N256/T20 over the same physical horizon. Also run that selected set through
alm_check direct convolution at N256/T10. Direct check has no FFT, same full
horizon and guard. Check class agreement, ignition evidence before censoring,
relative mass within 1% at common times, and radius within .1 R; disclose failures.
Exact rerun of primary selected states must reproduce final hashes. These checks
are not spatial-resolution convergence. A change under T20 implies numerical
fragility, not proof that either timestep is correct. No R26 claim is made.

If a bracket appears, do not infer monotonicity from a sparse ladder. Next smallest
experiment: bisect that within-family bracket with ring-presence pairing and own
numerical checks. If B alone grows, S103 is unnecessary in that family, but a
lower threshold caused by the ring is supported only by matched A comparisons.
If none grows, extend B width/dose once or test a compact multi-ring nucleus;
no global necessity conclusion. If numerics disagree, first resolve that contrast
with T40/T80 and direct arithmetic before refining a threshold.
