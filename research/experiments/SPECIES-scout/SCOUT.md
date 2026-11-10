# SPECIES-scout (2026-11-10): where should a species hunt dig?

Scouting instrument only. No claim rests on this page. Every candidate listed here comes from one
float trajectory in a 256² world, restarted from a float32 snapshot. It still needs a seeded,
reproducible run before it can become a specimen.

## Method

`scout.py run REGION 60 --seed 1`: for each region, 60 random rules × 8 seeds, run for 200 tu at T = 10, N = 256,
using the same update as `alm.lenia` (batched FFT). Classes at the horizon: DIED, FILLED (> 25 % cells > 0.1),
CHAOS (not 1–3 compact components), BODY (1–3 components, each < 6R across). BODY is then split
by the shift-correlation between t−20 tu and t: GLIDER / STATIC / OSC.

| region | rules | sampling | seeds |
|---|---|---|---|
| R1 Orbium niche band | poly/poly, b=[1], R13 T10 | mu 0.11–0.30, sigma = mu × 0.07–0.20 | even: soup disk 1–2R; odd: S001 Orbium with level noise |
| R2 multi-ring | poly/poly, 2–3 shells from {1, 11/12 … 1/6}, R18 T10 | mu 0.12–0.42, same sigma ratio | soup |
| R4 exp-kernel / mixed families | exp/exp, exp/poly, poly/exp; 1–2 shells, R13 T10 | mu 0.10–0.40 | soup |

R3 (reef and fractal debris) was not simulated. The reef is a detonation that fills the world (C052–C055), and 9 of the 40
S001-rule soups in VIS-S1 also fill the world with a lattice. Debris there turns into lattice, not bodies.

## Result

| region | BODY worlds | rules with a BODY | DIED | FILLED | CHAOS |
|---|---|---|---|---|---|
| R1 | 15/480 (3.1 %) | 8/60 | 58 % | 18 % | 20 % |
| R2 | 17/480 (3.5 %) | 12/60 | 42 % | 45 % | 10 % |
| R4 | 5/480 (1.0 %) | 4/60 | 58 % | 27 % | 14 % |

Contact sheets: `sheet-R1.png`, `sheet-R2.png`, `sheet-R4.png`. 

- **R1** bodies are almost all Orbium-like gliders (mu 0.11–0.18), and almost all came from the mutated Orbium seeds, not from soups.
  Two double-loop oscillators (mu ≈ 0.173–0.178, sigma ≈ 0.026) persisted to 1000 tu. Their nearest catalogue rule is O4d
  *Parorbium dividuus* (distance 0.16), so they are probably relatives. A quatrefoil ring at mu 0.2145 filled the world by 1000 tu.
- **R2** bodies are mostly clip-saturated static discs and rings (cells at 1.0). They are not very lifelike, which suggests the sampled sigma
  is too wide for multi-ring kernels. Every R2 candidate has a catalogue entry at distance ≤ 0.12 (for example 3F9c, 3F7l, KN+c).
  This region is well charted.
- **R4** gave the most distinct find: a **crescent glider under poly kernel + exp growth** (mu 0.2817, sigma 0.0406, b=[1]).
  It kept gliding for 1000 tu (corr 0.99, 5.7 R per 20 tu). The pinned catalogue has **0 entries** with a mixed kernel/growth
  pair, and only 5 exp/exp entries.

`candidates.png` shows the six survivors at 1000 tu (`followup.py`).

## Recommendation

1. Dig into the **mixed kernel/growth families** (poly/exp and exp/poly). They are uncharted by the catalogue, and the first
   hit there is a clean glider.
2. Switch the method from random sampling to **parameter walks from living bodies**. Hit rates from soups are 1–3 %, and the R1 hits
   came almost entirely from Orbium seeds. Drift mu/sigma (and the kernel/growth mix) in small steps from a live body and
   record each change of form. This is how Chan's catalogue was built.
3. Narrow sigma to about mu × 0.07–0.13 for multi-ring kernels, to avoid saturated blobs.

## Phase 2 (2026-11-10): parameter walks in the mixed families

`walk.py run`: 4 starting bodies × 8 directions in (log mu, log sigma), 2 % per stage, 60 tu of settling per stage, N256.
Starts: the crescent (poly/exp at sigma 0.0406, exp/poly at 0.0395) and S001 Orbium moved to poly/exp and exp/poly at
mu 0.15, sigma 0.016 (the paper's exp/exp Orbium sigma). Strips: `strip-*.png`. Close-ups: `zoom.png`.

- **Novelty check on the crescent** (`crescent-vs-catalogue.png`): the same state also glides under exp/poly (sigma 0.0383–0.0406),
  under exp/exp (0.0406), and under plain poly/poly at sigma 0.043. So it is **not specific to the mixed family**. Its nearest
  catalogue rules are hollow Pterifera chains (P5cf, P4cf, P4sus), which are larger, multi-segment bodies. Whether the crescent is a known
  one-segment member is not settled.
- **The crescent's niche is tiny**: in 6 of 8 directions it dies within 1–3 steps of 2 %. Raising mu and sigma together turns it into a clip-saturated
  static disc, which persists over a 40 % range.
- **Orbium is nearly unchanged by the growth curve**. In both mixed families it keeps the Orbium shape across a niche of about ±15–25 % in mu
  and sigma. At low sigma it deforms into twin-bar and tilted-bar variants, and at the low-mu edge it breaks up into a field of
  saturated rings. No new form was found.

Reading: changing only the growth curve gives nearly the same species as the parent family. The kernel shape matters more.
Next: R5 = exp/exp **multi-ring** kernels, which the catalogue covers with a single entry.
