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
| 06:31Z | X1–X8 ran (field c10b3f9). |
| 07:02Z | X1–X8 scored: ignition at every offset to ±1.5 R; passive blob 4–6 cells away evaporates without contact (D-019). Literature: Chan 2019 'Detonation' is prior art. |
| 07:06Z | Reserve X9–X11 committed (D-020): blob at the contact position, and a half-dose. |
| 06:00Z | Numerics Gate A items delivered (8ebf557): S103 fixed point, upstream tests ran (105/0/0), replay tool. R26 ring not a fixed point (D-010). |

## Gates

| gate | state |
|---|---|
| A: isolated controls, serialization, tracker, contact/censor contract | PASSED 06:13Z (D-014) |
| B: six pilots | DONE 06:26Z: 6/6 FISSION + PROLIFERATION (D-015, D-016) |
| Contrast checks | P2, P3 selected 06:35Z |
| Discovery (≤ 12) | X1–X8 done (D-019); X9–X11 committed (D-020); 1 unused |
| Report / exhibit / integration PR | not started |

## Lane heads

| lane | branch | latest reviewed commit | note |
|---|---|---|---|
| coordinator | reef/coordinator | (this commit) | protocol v1 |
| field | reef/field | c10b3f9 | pilots + X1–X8 run |
| numerics | reef/numerics | 8ebf557 | Gate A items done; waits on field states |
| behavior | reef/behavior | 4f5d328 | scores, LITERATURE.md, exhibit panels |
