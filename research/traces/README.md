# Traces

Machine-readable run outputs, one directory per run ID. Each trace records simulator commit, specimen ID, parameters, seed, grid/timestep, intervention, measurements, final state, and reproduction command.

## Format (written by `python -m alm.run`)

A run ID is `<specimen>-<hash10>`. The hash covers the full run configuration, the
code commit and the dirty flag, so equal IDs mean equal inputs. Reruns of the same
configuration on the same commit land in the same directory and should reproduce
`final_state_sha256` bit for bit.

| File | Contents |
| --- | --- |
| `manifest.json` | Provenance: `simulator` (package version, `git_commit`, `git_dirty`), `upstream_reference`, `specimen` (ID, source, cells hash), `rule` (R, T, dt, mu, sigma, beta, kernel, growth), `grid` (shape, periodic, float64), `integrator`, `timestep`, `seed`, `config`, `interventions_applied` (step, params, mass before/after, L1 change), `measurements` (columns, interval), initial/final state sha256, `environment`, `reproduction` (commit + command). |
| `trace.csv` | One row every `every` steps (and the last step). Columns below. |
| `series.npz` | Per-step `mass`, `x_cells`, `y_cells` (unwrapped centroid). Use for spectra and exact displacement. |
| `summary.json` | Statistics over `window_steps` (default from step 1000): alive flag, first dead step, mass mean/sd/min/max, dominant mass period, net speed and heading, mean gyradius. |
| `states.npz` | `initial`, `final`, and `iv<k>_pre` / `iv<k>_post` around each intervention. |
| `final.png`, `overview.png` | Render of the final state; quick-look plot from `python -m alm.plot <run_dir>`. |

### `trace.csv` columns (feature set `basic`)

| Column | Meaning |
| --- | --- |
| `step`, `time` | step count and time = step / T |
| `mass` | ΣA / R² (upstream `m` units) |
| `growth` | Σ max(G, 0) / R² for the update that produced this state (upstream `g`) |
| `peak` | max A |
| `area` | number of cells with A > 0.1, / R² |
| `gyradius` | radius of gyration about the periodic centroid, in R |
| `cx_cells`, `cy_cells` | periodic (circular-mean) centroid, wrapped to [0, N) |
| `x_cells`, `y_cells` | centroid unwrapped across the torus, tracked every step |
| `speed` | unwrapped displacement since the previous row / elapsed time, in R per unit time |
| `alive` | 1 if raw ΣA > 1e−10 (upstream's survival floor) |

Image convention: rows are y and point down; headings are measured from +x toward +y.
Extra columns appear when a run selects more feature sets (`--features basic,<name>`).
