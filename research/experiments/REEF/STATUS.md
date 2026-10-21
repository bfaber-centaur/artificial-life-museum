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
| 07:13Z | X9–X11 scored: full-dose passive blob in contact ignites; half dose does not (D-021). |
| 07:15Z | X12 (0.75× dose) committed and run (D-022, field 0141e90). Discovery allowance spent (12/12). Numerics: replay, chkfft, direct agree for P2/P3; T20/R26/N512 running. |
| 07:28Z | Numerics §9 matrix (e7d4ef6): replay, chkfft, direct, N512 pass; T20/R26 keep outcome, timing fragile (C053). |
| 07:45Z | R26 control ruling (D-024). |
| 07:55Z | Report, C052–C055, C038/C041 amendments, museum Room 7. |
| 08:00Z | Hostile integration review: changes R1–R9 applied; **approved** (reef/behavior a4cf403). |
| 08:05Z | Integration PR #41 opened (reef/coordinator → main). Bobby merges. |
| 08:13Z | R26 rescored from per-step rows; labels unchanged (D-025). |
| 08:30Z | Numerics final imported (1a01fce): N512 dose check confirms bracket (D-026). All lanes final. PR #41 CI green; awaiting Bobby. |
| 06:00Z | Numerics Gate A items delivered (8ebf557): S103 fixed point, upstream tests ran (105/0/0), replay tool. R26 ring not a fixed point (D-010). |

## Gates

| gate | state |
|---|---|
| A: isolated controls, serialization, tracker, contact/censor contract | PASSED 06:13Z (D-014) |
| B: six pilots | DONE 06:26Z: 6/6 FISSION + PROLIFERATION (D-015, D-016) |
| Contrast checks | DONE: see MATRIX.md, C052/C053 |
| Discovery (≤ 12) | DONE 12/12 (D-019–D-023) |
| Report / exhibit / integration PR | PR #41 open, review approved |

## Lane heads

| lane | branch | latest reviewed commit | note |
|---|---|---|---|
| coordinator | reef/coordinator | (this commit) | integration |
| field | reef/field | 0141e90 | done: 26-run registry |
| numerics | reef/numerics | 1a01fce | final |
| behavior | reef/behavior | ae899e2 | final; review approved |
