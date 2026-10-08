# L6-007: attractor geography (status: in progress)

Protocol: [`protocol.md`](protocol.md), pre-registered in commit `08f6ee5` before any run.

## What is in so far

- **Part B raw data:** `paths.csv` and `finals-paths.npz` (63 blends between the three seeds,
  primary rule, 2000 tu). The analysis against P2 and P3 will come with Part A.
- **D2 rerun** (exploratory, added by amendment; [`d2_resize.py`](d2_resize.py),
  [`d2-resize.csv`](d2-resize.csv)). S102 at its registered rule (μ 0.155, σ 0.020, T 10),
  1000 tu, in Lane 6's engine (`field.py`, `alm.lenia` semantics):

  | R | block | nearest | bilinear | cubic |
  | --- | --- | --- | --- | --- |
  | 26 | CIRCLER, mass 0.5234 | CIRCLER, 0.5234 | died at 8.3 tu | CIRCLER, 0.5235 |
  | 39 | CIRCLER, 0.5234 | CIRCLER, 0.5234 | died at 6.0 tu | CIRCLER, 0.5235 |

  This agrees with Lane 3's `alm_check` result (C047, PR #18: same classes, masses 0.5234–0.5235,
  bilinear deaths at t = 9 and 6). C039 ("S102 does not survive doubling the resolution") is
  withdrawn. The Night-0 death came from the bilinear seed, not from the resolution. The S102
  dossier and the L6-field README are corrected.

Part A (noise robustness at three numerics) and the full write-up against P1–P4 follow in a
later PR.
