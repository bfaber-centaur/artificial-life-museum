# Claims ledger

Every substantive claim gets a stable ID (`C001`, `C002`, ...) and exactly one
status. Claims are never deleted: a refuted claim stays here with its evidence.
Status changes are appended to the claim's history, not overwritten.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `OBSERVED` | Seen in at least one recorded run; not yet reproduced. |
| `CONJECTURED` | Hypothesis without direct supporting runs yet. |
| `REFUTED` | Contradicted by recorded evidence. |
| `REPRODUCED` | Re-observed from a clean process with the same inputs. |
| `NUMERICALLY_FRAGILE` | Changes or disappears under a modest timestep/resolution/boundary change. |
| `INDEPENDENTLY_CHECKED` | Reproduced by a second lane and/or a distinct execution path. |

## Template

Copy this block for each new claim.

```markdown
### C000 — <one-line statement>

- **Status:** CONJECTURED
- **Owner lane:**
- **Specimen / version:** (ID and dossier commit)
- **Simulator / version:** (package + git commit)
- **Parameters:** (R, T, mu, sigma, kernel peaks, grid size, dt, boundary)
- **Intervention:** (type, location, strength, timing)
- **Metric:** (definition, threshold, horizon; fixed before looking at results?)
- **Run IDs:**
- **Search / parameter bounds:**
- **Reproduction command:**
- **Known caveats:**
- **History:**
  - YYYY-MM-DD — CONJECTURED — <who, why>
```

## Claims

_None yet._
