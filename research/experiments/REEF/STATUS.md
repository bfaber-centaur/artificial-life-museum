# REEF status

Updated by the coordinator lane at gates and meaningful failures. Times UTC (Pacific in brackets).

| time | state |
|---|---|
| 05:50Z (22:50 PDT) | Launched. Launch commit 51af137 verified. |
| 05:51Z | Field, numerics and behavior/hostile-review threads started. |
| 05:58Z | PROTOCOL.md v1 frozen (thresholds marked [A] pending). No encounter run has happened. |

## Gates

| gate | state |
|---|---|
| A: isolated controls, serialization, tracker, contact/censor contract | open |
| B: six pilots | not started |
| Contrast checks | not started |
| Discovery (≤ 12) | not started |
| Report / exhibit / integration PR | not started |

## Lane heads

| lane | branch | latest reviewed commit | note |
|---|---|---|---|
| coordinator | reef/coordinator | (this commit) | protocol v1 |
| field | reef/field | — | settling the glider |
| numerics | reef/numerics | — | S103 check, tests, alm_check replay |
| behavior | reef/behavior | — | tracker + tests |
