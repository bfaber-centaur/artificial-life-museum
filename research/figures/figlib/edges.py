"""Survival edges from disturbance run tables.

An edge is reported only as the pair of sampled runs that bracket it: the largest
|ΔM/M₀| that recovered and the smallest that died, per (source, condition, phase).
Nothing is interpolated between them; plots draw the gap as unresolved.
"""
import csv
import math
from dataclasses import dataclass, field

OUTCOME_CODES = {"R": "RECOVERED", "D": "DIED", "T": "TRANSFORMED", "X": "EXPLODED"}


@dataclass
class Run:
    source: str        # who ran it, e.g. "Lane 4 ref"
    condition: str     # e.g. "T10 R13"
    intervention: str  # I001..I004
    phase: int         # 0..4 (phase replicate index)
    strength: float    # native intervention strength s
    dmass: float       # achieved ΔM/M₀ (signed fraction)
    outcome: str       # RECOVERED / DIED / ...
    file: str
    run_id: str = ""


@dataclass
class Edge:
    source: str
    condition: str
    intervention: str
    phase: int
    survive_abs: float   # largest |ΔM/M₀| that recovered (nan if none)
    die_abs: float       # smallest |ΔM/M₀| that died (nan if none)
    survive_run: str
    die_run: str
    n_runs: int
    monotone: bool       # no survivor above a death, no death below a survivor
    violations: list = field(default_factory=list)


def read_lane4(path, source, condition, t0_base=None):
    """Lane 4 L4-001 result CSVs (coarse.csv, bisect.csv, T20/, R26/)."""
    rows = list(csv.DictReader(open(path)))
    t0s = sorted({int(r["t0"]) for r in rows})
    base = t0_base if t0_base is not None else t0s[0]
    return [Run(source, condition, r["intervention"], int(r["t0"]) - base, float(r["strength"]),
                float(r["achieved_dmass_frac"]), r["class"], str(path), r["run_id"]) for r in rows]


def read_lane3(path, source, condition):
    """Lane 3 alm_check.disturb CSVs (research/traces/lane3/disturb-*.csv)."""
    out = []
    for r in csv.DictReader(open(path)):
        rid = f"{r['intervention']}-p{r['phase']}-s{float(r['s']):.6f}"
        out.append(Run(source, condition, r["intervention"], int(r["phase"]), float(r["s"]),
                       float(r["dM"]), OUTCOME_CODES[r["cls"]], str(path), rid))
    return out


def edges(runs):
    groups = {}
    for r in runs:
        groups.setdefault((r.source, r.condition, r.intervention, r.phase), []).append(r)
    out = []
    for (src, cond, iv, ph), rs in sorted(groups.items()):
        surv = [r for r in rs if r.outcome == "RECOVERED"]
        died = [r for r in rs if r.outcome == "DIED"]
        s_best = max(surv, key=lambda r: abs(r.dmass), default=None)
        d_best = min(died, key=lambda r: abs(r.dmass), default=None)
        sa = abs(s_best.dmass) if s_best else math.nan
        da = abs(d_best.dmass) if d_best else math.nan
        viol = [r.run_id for r in surv if d_best and abs(r.dmass) > da]
        viol += [r.run_id for r in died if s_best and abs(r.dmass) < sa]
        out.append(Edge(src, cond, iv, ph, sa, da, s_best.run_id if s_best else "",
                        d_best.run_id if d_best else "", len(rs), not viol, viol))
    return out
