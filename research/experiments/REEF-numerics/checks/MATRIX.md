# §9 comparison matrix: P2 and P3

Pass rules (PROTOCOL §9, frozen in v1): replay sha256 identical; alm_check FFT expected bitwise;
direct/T20/R26/N512: same class, t_c within 0.5 tu, masses within 1% (heading change is not
defined: the glider merges at t_c in every pilot). Ignition time and front speed are the lead's
D-017 outcome observables and are reported with their differences, not given a frozen tolerance.

| run | route | class | t_c (tu) | ignition (tu) | E mass t20 | E mass t25 | front R/tu | Δt_c / Δm20 / Δm25 (rel) | §9 verdict | E final sha256 |
|---|---|---|---|---|---|---|---|---|---|---|
| P2 | alm reference (this lane, fresh process) | FISSION | 6.1 | 14.7 | 14.95 | 28.92 | 0.362 | — / — / — | reference | `3549322b1c7f` |
| P2 | alm_check FFT (same arithmetic) | FISSION | 6.1 | 14.7 | 14.95 | 28.92 | 0.362 | 0.0 / 0.0000 / 0.0000 | PASS (bitwise) | `3549322b1c7f` |
| P2 | alm_check direct, window 3→25 tu (different arithmetic) | FISSION | 6.1 | 14.7 | 14.95 | 28.92 | 0.362 | 0.0 / -0.0000 / -0.0000 | PASS | `466863da0c40` |
| P2 | T20, own controls | FISSION | 5.6 | 11.6 | 24.17 | 42.67 | 0.378 | -0.5 / 0.6172 / 0.4755 | same class; quantitative FAIL | `3f147e3dc9ce` |
| P2 | R26 2×2 block, N512, own controls | CONTROL_FAILURE | 6.1 | 10.4 | 21.11 | 38.16 | 0.369 | 0.0 / 0.4120 / 0.3194 | FAIL (class) | `56f495860a0d` |
| P2 | N512, R13, same separation, own controls | FISSION | 6.1 | 14.7 | 14.95 | 28.92 | 0.385 | 0.0 / 0.0000 / 0.0000 | PASS | `d56de785c980` |
| P3 | alm reference (this lane, fresh process) | FISSION | 6.7 | 18.0 | 7.51 | 18.24 | 0.332 | — / — / — | reference | `40b6a0eed32b` |
| P3 | alm_check FFT (same arithmetic) | FISSION | 6.7 | 18.0 | 7.51 | 18.24 | 0.332 | 0.0 / 0.0000 / 0.0000 | PASS (bitwise) | `40b6a0eed32b` |
| P3 | alm_check direct, window 3→25 tu (different arithmetic) | FISSION | 6.7 | 18.0 | 7.51 | 18.24 | 0.332 | 0.0 / 0.0000 / 0.0000 | PASS | `58caaaaba73a` |
| P3 | T20, own controls | FISSION | 6.2 | 15.9 | 10.17 | 23.15 | 0.321 | -0.5 / 0.3545 / 0.2690 | same class; quantitative FAIL | `1dab6e0db927` |
| P3 | R26 2×2 block, N512, own controls | CONTROL_FAILURE | 6.7 | 17.1 | 9.62 | 21.15 | 0.321 | 0.0 / 0.2811 / 0.1595 | FAIL (class) | `d0e29619a4d1` |
| P3 | N512, R13, same separation, own controls | FISSION | 6.7 | 18.0 | 7.51 | 18.24 | 0.366 | 0.0 / 0.0000 / 0.0000 | PASS | `7543775f6f45` |

Notes. Clean-process replay (field runner.py at fe4ba1c, fresh process): E/G/S final sha256 identical and all
159 checkpoints bitwise for both runs (clean_replay.json). Only alm_check direct is different arithmetic.
R26 "FAIL (class)" is the scorer's CONTROL_FAILURE: its frozen S-control rule needs constant ring mass, which the
R26 block ring never has (README section 5); judged against its own control (D-010) the ring stays one static body
and E ignites into the same colony, earlier. See README section 7.
