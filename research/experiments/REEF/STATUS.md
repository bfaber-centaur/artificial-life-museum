# REEF status

Updated by the coordinator lane at gates and meaningful failures. Times UTC (Pacific in brackets).

| time | state |
|---|---|
| 05:50Z (22:50 PDT) | Launched. Launch commit 51af137 verified. |
| 05:51Z | Field, numerics and behavior/hostile-review threads started. |
| 05:58Z | PROTOCOL.md v1 frozen (thresholds marked [A] pending). No encounter run has happened. |
| 06:10Z | Gate A addendum frozen (PROTOCOL §11); tracker delivered. |
| 06:13Z | **Gate A passed.** Pilots authorized. |
| 06:13Z | P1–P6 ran (44 s, field 91da893). |
| 06:26Z | Pilots scored: all six FISSION with proliferation (glider+ring fuse, colony covers torus). Pr2, Pr3 failed. |
| 06:35Z | Contrasts P2, P3 selected (D-017); discovery grid X1–X8 committed (D-018). |
| 06:00Z | Numerics Gate A items delivered (8ebf557): S103 fixed point, upstream tests ran (105/0/0), replay tool. R26 ring not a fixed point (D-010). |

## Gates

| gate | state |
|---|---|
| A: isolated controls, serialization, tracker, contact/censor contract | PASSED 06:13Z (D-014) |
| B: six pilots | DONE 06:26Z: 6/6 FISSION + PROLIFERATION (D-015, D-016) |
| Contrast checks | P2, P3 selected 06:35Z |
| Discovery (≤ 12) | X1–X8 committed 06:35Z |
| Report / exhibit / integration PR | not started |

## Lane heads

| lane | branch | latest reviewed commit | note |
|---|---|---|---|
| coordinator | reef/coordinator | (this commit) | protocol v1 |
| field | reef/field | 91da893 | pilots run |
| numerics | reef/numerics | 8ebf557 | Gate A items done; waits on field states |
| behavior | reef/behavior | 4de401e | pilot scores + audit |
