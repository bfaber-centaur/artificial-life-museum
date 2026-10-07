"""Headless experiment runner and CLI.

    python -m alm.run --specimen S001 --steps 5000 --every 10

writes ``research/traces/<run_id>/``:

- ``manifest.json``  provenance: code commit (+dirty flag), specimen, rule,
  grid, dt, seed, interventions (scheduled and applied), state hashes,
  environment and the reproduction command;
- ``trace.csv``      periodic measurements, one row per sample;
- ``series.npz``     per-step mass and unwrapped centroid (for spectra);
- ``summary.json``   baseline statistics over a post-transient window;
- ``states.npz``     initial and final state, plus pre/post snapshots around
  every intervention;
- ``final.png``      greyscale render of the final state.

The run ID is ``<specimen>-<hash>``, where the hash covers the full
configuration and the code commit: same ID means same inputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shlex
import sys
import time
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np

from . import measure as feat
from . import interventions as ivs
from . import provenance, specimens
from .lenia import GROWTHS, KERNEL_CORES, Lenia

DEFAULT_OUT_ROOT = specimens.REPO_ROOT / "research" / "traces"


@dataclass
class RunConfig:
    specimen: str = "S001"
    steps: int = 2000
    every: int = 10
    size: int = 128
    seed: int = 0
    burn_in: int = 1000  # summary window starts here (clamped to steps // 2)
    # Rule overrides; None keeps the specimen's own value. R is fixed by the specimen.
    T: float | None = None
    mu: float | None = None
    sigma: float | None = None
    kernel: str | None = None
    growth: str | None = None
    interventions: list[tuple[int, ivs.Intervention]] = field(default_factory=list)
    features: tuple[str, ...] = feat.DEFAULT

    def rule_overrides(self) -> dict:
        names = ("T", "mu", "sigma", "kernel", "growth")
        return {k: getattr(self, k) for k in names if getattr(self, k) is not None}

    def to_dict(self) -> dict:
        return {
            "specimen": self.specimen,
            "steps": self.steps,
            "every": self.every,
            "size": self.size,
            "seed": self.seed,
            "burn_in": self.burn_in,
            "rule_overrides": self.rule_overrides(),
            "interventions": [
                {"step": s, **iv.to_dict()} for s, iv in sorted(self.interventions, key=lambda x: x[0])
            ],
            "features": list(self.features),
        }

    def command(self) -> str:
        args = ["python", "-m", "alm.run", "--specimen", self.specimen]
        args += ["--steps", str(self.steps), "--every", str(self.every), "--size", str(self.size)]
        args += ["--seed", str(self.seed), "--burn-in", str(self.burn_in)]
        for k, v in self.rule_overrides().items():
            args += [f"--{k}", str(v)]
        for s, iv in sorted(self.interventions, key=lambda x: x[0]):
            args += ["--intervene", ivs.to_spec(s, iv)]
        if tuple(self.features) != feat.DEFAULT:
            args += ["--features", ",".join(self.features)]
        return shlex.join(args)


@dataclass
class RunResult:
    run_id: str
    manifest: dict
    summary: dict
    rows: list[dict]
    final: np.ndarray
    run_dir: Path | None


def run(
    config: RunConfig,
    out_root: Path | str | None = DEFAULT_OUT_ROOT,
    run_id: str | None = None,
    log=None,
) -> RunResult:
    """Run one experiment. ``out_root=None`` keeps everything in memory."""
    if config.every < 1 or config.steps < 0:
        raise ValueError("need steps >= 0 and every >= 1")
    for s, _ in config.interventions:
        if not 0 <= s <= config.steps:
            raise ValueError(f"intervention step {s} outside [0, {config.steps}]")

    spec = specimens.load(config.specimen)
    rule = replace(spec.rule, **config.rule_overrides())
    A0 = spec.place(config.size)
    sim = Lenia(rule, A0)
    rng = np.random.default_rng(config.seed)
    R, ny, nx = rule.R, *A0.shape

    code = provenance.code_version()
    cfg = config.to_dict()
    if run_id is None:
        h = provenance.config_hash({"config": cfg, "commit": code["git_commit"], "dirty": code["git_dirty"]})
        run_id = f"{config.specimen}-{h[:10]}"

    schedule: dict[int, list[ivs.Intervention]] = {}
    for s, iv in config.interventions:
        schedule.setdefault(s, []).append(iv)

    n = config.steps
    mass = np.empty(n + 1)
    xs = np.empty(n + 1)
    ys = np.empty(n + 1)
    snapshots: dict[str, np.ndarray] = {"initial": A0.copy()}
    applied = []
    rows: list[dict] = []
    last_c = feat.periodic_centroid(A0)
    pos = [last_c[0], last_c[1]]
    last_sample = None
    started = time.time()

    def intervene(t):
        for iv in schedule.get(t, []):
            pre = sim.A.copy()
            post = np.clip(np.asarray(iv.apply(pre.copy(), sim, rng), dtype=np.float64), 0.0, 1.0)
            if post.shape != pre.shape:
                raise ValueError(f"{iv.name} changed the state shape")
            sim.A = post
            k = len(applied)
            snapshots[f"iv{k}_pre"] = pre
            snapshots[f"iv{k}_post"] = post.copy()
            applied.append(
                {
                    "index": k,
                    "step": t,
                    **iv.to_dict(),
                    "mass_before": float(pre.sum()) / R**2,
                    "mass_after": float(post.sum()) / R**2,
                    "l1_change": float(np.abs(post - pre).sum()) / R**2,
                    "max_abs_change": float(np.abs(post - pre).max()),
                }
            )

    G = None
    for t in range(n + 1):
        if t > 0:
            G = sim.step()
        intervene(t)
        A = sim.A
        c = feat.periodic_centroid(A)
        if not math.isnan(c[0]):
            if not math.isnan(last_c[0]):
                pos[0] += float(feat.wrap(c[0] - last_c[0], nx))
                pos[1] += float(feat.wrap(c[1] - last_c[1], ny))
            last_c = c
        mass[t] = A.sum() / R**2
        xs[t], ys[t] = pos
        if t % config.every == 0 or t == n:
            row = {"step": t, "time": t * rule.dt}
            row.update(feat.compute(config.features, A, sim))
            row["growth"] = float(np.maximum(G, 0).sum()) / R**2 if G is not None else float("nan")
            row["x_cells"], row["y_cells"] = pos
            if last_sample is None:
                row["speed"] = float("nan")
            else:
                ts, px, py = last_sample
                row["speed"] = math.hypot(pos[0] - px, pos[1] - py) / R / ((t - ts) * rule.dt)
            last_sample = (t, pos[0], pos[1])
            rows.append(row)
            if log:
                log(f"t={t} mass={row['mass']:.6f} speed={row['speed']:.4f}")
    snapshots["final"] = sim.A.copy()

    summary = summarize(mass, xs, ys, rows, rule, config.burn_in)
    manifest = {
        "run_id": run_id,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "wall_seconds": round(time.time() - started, 3),
        "simulator": code,
        "upstream_reference": {"repo": "Chakazul/Lenia", "commit": specimens_ref()},
        "specimen": spec.to_dict(),
        "rule": rule.to_dict(),
        "grid": {"shape": [ny, nx], "boundary": "periodic", "dtype": "float64"},
        "integrator": "euler+clip[0,1]",
        "timestep": {"T": rule.T, "dt": rule.dt, "steps": n, "total_time": n * rule.dt},
        "seed": config.seed,
        "config": cfg,
        "interventions_applied": applied,
        "measurements": {"file": "trace.csv", "every": config.every, "columns": list(rows[0])},
        "initial_state_sha256": provenance.state_sha256(A0),
        "final_state_sha256": provenance.state_sha256(sim.A),
        "environment": provenance.environment(),
        "reproduction": {
            "checkout": code["git_commit"],
            "command": config.command(),
            "note": "run from repo root after ./scripts/bootstrap.sh; same commit + command reproduces final_state_sha256 on the same platform",
        },
    }

    run_dir = None
    if out_root is not None:
        run_dir = Path(out_root) / run_id
        write(run_dir, manifest, summary, rows, snapshots, mass, xs, ys)
    return RunResult(run_id, manifest, summary, rows, sim.A, run_dir)


def specimens_ref() -> str:
    from . import LENIA_REFERENCE_SHA

    return LENIA_REFERENCE_SHA


def dominant_period(series: np.ndarray, pad: int = 16) -> float:
    """Period (in samples) of the largest non-DC peak of a detrended series."""
    x = np.asarray(series, dtype=np.float64)
    if len(x) < 8 or not np.isfinite(x).all() or x.std() == 0:
        return float("nan")
    x = (x - x.mean()) * np.hanning(len(x))
    spec = np.abs(np.fft.rfft(x, n=pad * len(x)))
    freqs = np.fft.rfftfreq(pad * len(x))
    spec[freqs < 2.0 / len(x)] = 0  # drop DC and the slowest drift
    return float(1.0 / freqs[int(np.argmax(spec))])


def summarize(mass, xs, ys, rows, rule, burn_in) -> dict:
    n = len(mass) - 1
    start = min(burn_in, n // 2)
    w = slice(start, n + 1)
    alive = mass * rule.R**2 > feat.ALIVE_MASS
    dead_steps = np.flatnonzero(~alive)
    dx, dy = xs[n] - xs[start], ys[n] - ys[start]
    span = (n - start) * rule.dt
    speed_cells = math.hypot(dx, dy) / (n - start) if n > start else float("nan")
    gyr = [r["gyradius"] for r in rows if start <= r["step"] and "gyradius" in r]
    m = mass[w]
    return {
        "window_steps": [start, n],
        "alive_final": bool(alive[-1]),
        "first_dead_step": int(dead_steps[0]) if len(dead_steps) else None,
        "mass_mean": float(m.mean()),
        "mass_sd": float(m.std()),
        "mass_min": float(m.min()),
        "mass_max": float(m.max()),
        "mass_dominant_period_steps": dominant_period(m),
        "speed_R_per_time": math.hypot(dx, dy) / rule.R / span if span > 0 else float("nan"),
        "speed_cells_per_step": speed_cells,
        "heading_deg_image": math.degrees(math.atan2(dy, dx)) % 360,
        "net_displacement_cells": math.hypot(dx, dy),
        "gyradius_mean": float(np.mean(gyr)) if gyr else float("nan"),
        "notes": "heading measured from +x toward +y with y pointing down (image rows)",
    }


def _render(A: np.ndarray, path: Path) -> None:
    from PIL import Image

    Image.fromarray(np.rint(np.clip(A, 0, 1) * 255).astype(np.uint8), mode="L").save(path)


def write(run_dir: Path, manifest, summary, rows, snapshots, mass, xs, ys) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=True) + "\n")
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n")
    with open(run_dir / "trace.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        for r in rows:
            wr.writerow({k: (f"{v:.9g}" if isinstance(v, float) else v) for k, v in r.items()})
    np.savez_compressed(run_dir / "series.npz", mass=mass, x_cells=xs, y_cells=ys)
    np.savez_compressed(run_dir / "states.npz", **snapshots)
    _render(snapshots["final"], run_dir / "final.png")


def parse_args(argv=None) -> tuple[RunConfig, argparse.Namespace]:
    ap = argparse.ArgumentParser(prog="python -m alm.run", description=__doc__.split("\n\n")[0])
    ap.add_argument("--specimen", default="S001", help=f"one of {specimens.ids()}")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--every", type=int, default=10, help="sampling interval in steps")
    ap.add_argument("--size", type=int, default=128, help="square grid side in cells")
    ap.add_argument("--seed", type=int, default=0, help="RNG seed handed to interventions")
    ap.add_argument("--burn-in", type=int, default=1000, help="summary window start step")
    ap.add_argument("--T", type=float, default=None, help="override steps per unit time")
    ap.add_argument("--mu", type=float, default=None)
    ap.add_argument("--sigma", type=float, default=None)
    ap.add_argument("--kernel", choices=KERNEL_CORES, default=None)
    ap.add_argument("--growth", choices=GROWTHS, default=None)
    ap.add_argument(
        "--intervene", action="append", default=[], metavar="STEP:NAME[:k=v,...]",
        help=f"schedule an intervention; registered: {sorted(ivs.REGISTRY)}",
    )
    ap.add_argument("--features", default=",".join(feat.DEFAULT), help=f"registered: {sorted(feat.REGISTRY)}")
    ap.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    ap.add_argument("--run-id", default=None, help="override the derived run ID")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    T = a.T
    if T is not None and float(T).is_integer():
        T = int(T)
    cfg = RunConfig(
        specimen=a.specimen, steps=a.steps, every=a.every, size=a.size, seed=a.seed,
        burn_in=a.burn_in, T=T, mu=a.mu, sigma=a.sigma, kernel=a.kernel, growth=a.growth,
        interventions=[ivs.parse(s) for s in a.intervene],
        features=tuple(x for x in a.features.split(",") if x),
    )
    return cfg, a


def main(argv=None) -> int:
    cfg, a = parse_args(argv)
    res = run(cfg, out_root=a.out_root, run_id=a.run_id)
    if not a.quiet:
        print(json.dumps({"run_id": res.run_id, "run_dir": str(res.run_dir), **res.summary}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
