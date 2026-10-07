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
- `research/` — charter, claims ledger, specimens, experiments, traces, reports, and the
  illustrated specimen gallery ([`research/gallery/`](research/gallery/README.md))

## Running the simulator

```bash
.venv/bin/python -m alm.run --specimen S001 --steps 5000 --every 10
.venv/bin/python -m alm.plot research/traces/<run_id>
```

Each run writes `research/traces/<run_id>/` with a provenance manifest, a periodic
`trace.csv`, per-step series, states and a summary (format in
[`research/traces/README.md`](research/traces/README.md)). Rule overrides: `--T`, `--mu`,
`--sigma`, `--kernel {poly,exp}`, `--growth {poly,exp}`, `--size`.

Extension points:

- Interventions: subclass `alm.interventions.Intervention`, decorate with
  `@alm.interventions.register`, schedule with `--intervene STEP:NAME:k=v,...`.
  The runner re-clips to [0, 1], logs mass before/after and snapshots both sides.
- Measurements: `@alm.measure.register("name")` on a function `(A, sim) -> dict`,
  then `--features basic,name`.
- Python API: `alm.run.run(alm.run.RunConfig(...), out_root=None)` returns the trace
  rows, summary, manifest and final state without writing files.
