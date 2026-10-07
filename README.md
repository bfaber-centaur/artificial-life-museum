# artificial-life-museum

the search for mr wobbles

A small scientific field station in classic 2-D Lenia. Read
[`research/charter.md`](research/charter.md) for the mission and rules, and
[`research/claims.md`](research/claims.md) for the claims ledger.

## Setup

```bash
./scripts/bootstrap.sh
source .venv/bin/activate
pytest
```

The bootstrap creates `.venv/`, installs this package from `pyproject.toml`,
and checks out the pinned upstream reference `Chakazul/Lenia@adfc542` under
`.refs/Lenia/` (gitignored, never modified).

## Layout

- `src/alm/` — ALM's own headless Lenia kernel and instruments
- `tests/` — pytest suite
- `research/` — charter, claims ledger, specimens, experiments, traces, reports
