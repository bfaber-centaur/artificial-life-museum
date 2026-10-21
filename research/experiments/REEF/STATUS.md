# REEF status

Updated by the coordinator lane at gates and meaningful failures. Times UTC (Pacific in brackets).

| time | state |
|---|---|
| 05:50Z (22:50 PDT) | Launched. Launch commit 51af137 verified. |
| 05:51Z | Field, numerics and behavior/hostile-review threads started. |
| 05:58Z | PROTOCOL.md v1 frozen (thresholds marked [A] pending). No encounter run has happened. |
| 06:10Z | Gate A addendum frozen (PROTOCOL §11); tracker delivered. |
| 06:13Z | **Gate A passed.** Pilots authorized. |
| 06:00Z | Numerics Gate A items delivered (8ebf557): S103 fixed point, upstream tests ran (105/0/0), replay tool. R26 ring not a fixed point (D-010). |

## Gates

| gate | state |
|---|---|
| A: isolated controls, serialization, tracker, contact/censor contract | PASSED 06:13Z (D-014) |
| B: six pilots | authorized 06:13Z |
| Contrast checks | not started |
| Discovery (≤ 12) | not started |
| Report / exhibit / integration PR | not started |

## Lane heads

| lane | branch | latest reviewed commit | note |
|---|---|---|---|
| coordinator | reef/coordinator | (this commit) | protocol v1 |
| field | reef/field | a91704f | controls, geometry, pilot jobs ready |
| numerics | reef/numerics | 8ebf557 | Gate A items done; waits on field states |
| behavior | reef/behavior | 5e98897 | tracker (22 tests), scorer, RIVALS.md |
