"""VIS-S1: survival survey of the pinned upstream 2-D catalog under ALM's own simulator.

Every catalog entry with params, poly/exp families (kn, gn in {1, 2}), T <= 40 and an RLE seed is placed
centred on its own periodic world and run for HORIZON time units. The classes below were fixed
before the first run (2026-11-07) and are applied mechanically:

  DIED        final mass < 0.05 x initial mass
  FILLED      final fill (fraction of cells > 0.1) > 0.25, or final mass > 4 x initial
  PERSISTED   otherwise; split into MOVER (net centroid travel >= 1 R over the last 50 tu)
              and STAY (less)

PERSISTED only means "still a bounded, non-empty pattern at the horizon", not "the catalogued
species". The survey is a field guide for choosing what to film, not a claim about the catalog.

Usage: python survey.py run [--jobs 2]   -> survey.jsonl + thumbs/
       python survey.py table            -> SURVEY.md
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402

from alm import rle  # noqa: E402
from alm.lenia import Lenia, Rule  # noqa: E402
from alm.specimens import ANIMALS_JSON, ANIMALS_SHA256  # noqa: E402

HERE = Path(__file__).resolve().parent
HORIZON = 100  # time units
KN = {1: "poly", 2: "exp"}


def catalog() -> list[dict]:
    raw = ANIMALS_JSON.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ANIMALS_SHA256
    out = []
    for i, e in enumerate(json.loads(raw)):
        p = e.get("params")
        if not p or "cells" not in e or p.get("T", 10) > 40 or p.get("kn", 1) not in KN or p.get("gn", 1) not in KN:
            continue
        out.append({"index": i, "code": e.get("code"), "name": e.get("name"), "params": p,
                    "cells": e["cells"]})
    return out


def rule_of(p: dict) -> Rule:
    return Rule(R=int(p["R"]), T=p["T"], mu=p["m"], sigma=p["s"],
                beta=tuple(float(Fraction(x)) for x in str(p["b"]).split(",")),
                kernel=KN[p.get("kn", 1)], growth=KN[p.get("gn", 1)])


def world_size(R: int, cells: np.ndarray) -> int:
    need = max(8 * R, 3 * max(cells.shape))
    n = 128
    while n < need:
        n *= 2
    return n


def place(cells: np.ndarray, n: int) -> np.ndarray:
    A = np.zeros((n, n))
    h, w = cells.shape
    y, x = (n - h) // 2, (n - w) // 2
    A[y:y + h, x:x + w] = cells / 255.0
    return A


def centroid(A: np.ndarray) -> np.ndarray:
    n = A.shape[0]
    th = 2 * np.pi * np.arange(n) / n
    m = A.sum()
    if m <= 0:
        return np.array([np.nan, np.nan])
    cy = np.angle((A.sum(1) * np.exp(1j * th)).sum()) % (2 * np.pi)
    cx = np.angle((A.sum(0) * np.exp(1j * th)).sum()) % (2 * np.pi)
    return np.array([cy, cx]) * n / (2 * np.pi)


def unwrap_track(c: np.ndarray, n: int) -> np.ndarray:
    d = np.diff(c, axis=0)
    d = (d + n / 2) % n - n / 2
    return np.vstack([c[:1], c[:1] + np.cumsum(d, axis=0)])


def run_one(e: dict) -> dict:
    rule = rule_of(e["params"])
    cells = rle.decode(e["cells"])
    n = world_size(rule.R, cells)
    sim = Lenia(rule, place(cells, n))
    steps = int(round(HORIZON * rule.T))
    every = max(1, int(round(rule.T / 2)))  # sample twice per tu
    m0 = float(sim.A.sum())
    cs, ms = [], []
    for s in range(steps + 1):
        if s % every == 0:
            cs.append(centroid(sim.A))
            ms.append(float(sim.A.sum()))
        if s < steps:
            sim.step()
    A = sim.A
    m1 = float(A.sum())
    fill = float((A > 0.1).mean())
    cs = np.array(cs)
    tail = int(50 * 2)
    travel = np.nan
    if np.isfinite(cs[-tail:]).all():
        u = unwrap_track(cs[-tail:], n)
        travel = float(np.hypot(*(u[-1] - u[0])) / rule.R)
    if m1 < 0.05 * m0:
        cls = "DIED"
    elif fill > 0.25 or m1 > 4 * m0:
        cls = "FILLED"
    else:
        cls = "MOVER" if travel >= 1 else "STAY"
    thumbs = HERE / "thumbs"
    thumbs.mkdir(exist_ok=True)
    np.save(thumbs / f"{e['index']:03d}.npy", (A * 255).round().astype(np.uint8))
    return {"index": e["index"], "code": e["code"], "name": e["name"], "rule": rule.to_dict(),
            "N": n, "steps": steps, "mass0": m0, "mass1": m1, "fill1": fill,
            "travel_R_last50": travel, "class": cls,
            "final_sha256": hashlib.sha256(np.ascontiguousarray(A).tobytes()).hexdigest()}


def main(argv: list[str]) -> int:
    if argv[:1] == ["run"]:
        jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2
        entries = catalog()
        # small worlds first so results arrive early
        entries.sort(key=lambda e: rule_of(e["params"]).R ** 2 * e["params"]["T"])
        out = HERE / "survey.jsonl"
        done = set()
        if out.exists():
            done = {json.loads(l)["index"] for l in out.read_text().splitlines()}
        todo = [e for e in entries if e["index"] not in done]
        print(f"{len(entries)} entries, {len(todo)} to run", flush=True)
        with Pool(jobs) as pool, out.open("a") as f:
            for r in pool.imap_unordered(run_one, todo):
                f.write(json.dumps(r) + "\n")
                f.flush()
                print(r["index"], r["code"], r["class"], flush=True)
        return 0
    if argv[:1] == ["table"]:
        rows = sorted((json.loads(l) for l in (HERE / "survey.jsonl").read_text().splitlines()),
                      key=lambda r: r["index"])
        from collections import Counter
        c = Counter(r["class"] for r in rows)
        lines = ["# VIS-S1 catalog survey (generated by `survey.py table`)", "",
                 f"{len(rows)} entries at {HORIZON} tu. " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())), "",
                 "| # | code | name | R | T | N | class | mass ratio | fill | travel (R, last 50 tu) |",
                 "|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            lines.append(f"| {r['index']} | `{r['code']}` | {r['name']} | {r['rule']['R']} | {r['rule']['T']} | {r['N']} | "
                         f"{r['class']} | {r['mass1'] / r['mass0']:.3f} | {r['fill1']:.3f} | {r['travel_R_last50']:.2f} |")
        (HERE / "SURVEY.md").write_text("\n".join(lines) + "\n")
        print(c)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
