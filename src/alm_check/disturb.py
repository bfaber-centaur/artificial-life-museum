"""Independent replication of Lane 4's L4-001 disturbance battery.

Implemented from research/experiments/L4-001-disturbance-battery/protocol.md
(pre-registered protocol, including amendment A1) on the alm_check stepper,
without reading Lane 4's or Lane 2's code. Everything is in time units and R
units so the same battery runs at any T and R:

  t0       = 100 time units + phase offsets of 0.1 time unit (= 1000..1004 steps at T = 10)
  horizon  = 200 time units after t0; window = last 50; speed blocks of 10 time units
  heading  = wrapped centroid displacement over the 1 time unit before t0

Usage:
    .venv/bin/python -m alm_check.disturb --T 10 --R 13 [--interventions I001 ...]
"""

from __future__ import annotations

import argparse
import csv
import os
from multiprocessing import Pool

import numpy as np

from .lenia import REPO, Rule, World, gyradius, periodic_centroid, place
from .sweeps import OUT, scaled_orbium

T0_TU, H_TU, WIN_TU, BLOCK_TU = 100.0, 200.0, 50.0, 10.0
PHASES = 5
REF_T10_R13 = dict(mass=0.4358, gyr=0.4376, speed=0.4796)  # Lane 1 dossier values, per protocol
GRIDS = {
    "I001": np.round(np.arange(0, 0.951, 0.05), 4),
    "I002": np.round(np.arange(0, 1.001, 0.05), 4),
    "I003": np.round(np.arange(0, 1.001, 0.05), 4),
    "I004": np.round(np.arange(0, 0.951, 0.05), 4),
}


def wrap(d, n):
    return (d + n / 2) % n - n / 2


# ------------------------------------------------------------ interventions


def frame(A, prev_c):
    """Centroid (cy, cx), heading (hy, hx) unit vector, from the centroid 1 time unit earlier."""
    n = A.shape[0]
    cy, cx = periodic_centroid(A)
    d = np.array([wrap(cy - prev_c[0], n), wrap(cx - prev_c[1], n)])
    return np.array([cy, cx]), d / np.hypot(*d)


def apply(kind, s, A, c, h, R):
    """Return the edited copy of A (h = (hy, hx) unit heading)."""
    n = A.shape[0]
    idx = np.arange(n)
    dy = wrap(idx[:, None] - c[0], n)
    dx = wrap(idx[None, :] - c[1], n)
    A = A.copy()
    if kind == "I001":
        return (1 - s) * A
    if kind == "I002":
        A[dy**2 + dx**2 < (s * R) ** 2] = 0
        return A
    if kind == "I003":
        fy, fx = c + R * h
        ey = wrap(idx[:, None] - fy, n)
        ex = wrap(idx[None, :] - fx, n)
        w = 0.25 * R
        return np.clip(A + s * np.exp(-(ey**2 + ex**2) / (2 * w**2)), 0, 1)
    if kind == "I004":
        if s <= 0:
            return A
        # port normal n = (-h_x, h_y) in (x, y) => lateral = dx * (-h_y) + dy * h_x
        lat = dx * (-h[0]) + dy * h[1]
        target = s * A.sum()
        flat_lat, flat_a = lat.ravel(), A.ravel()
        order = np.argsort(-flat_lat, kind="stable")
        cum = np.cumsum(flat_a[order])
        k = int(np.searchsorted(cum, target))  # first index where cum >= target
        k = min(k, len(order) - 1)
        thresh = flat_lat[order[k]]
        A[lat >= thresh] = 0
        return A
    raise ValueError(kind)


# ------------------------------------------------------------ runs


def warm_states(rule: Rule, n: int):
    """Step the catalog creature to each phase t0; return [(t0_step, A, prev_centroid)]."""
    T = int(rule.T)
    w = World(place(scaled_orbium(rule.R), n), rule)
    t0s = [int(round(T0_TU * T)) + k * max(1, T // 10) for k in range(PHASES)]
    look = int(round(T))  # 1 time unit back for heading
    out, hist = [], {}
    need = {t - look for t in t0s} | set(t0s)
    for s in range(1, max(t0s) + 1):
        w.step()
        if s in need:
            hist[s] = (w.A.copy(), periodic_centroid(w.A))
    for t in t0s:
        out.append((t, hist[t][0], hist[t - look][1]))
    return out


def post_run(A, rule: Rule):
    """Run the horizon after an edit; return window metrics."""
    T, R = rule.T, rule.R
    n = A.shape[0]
    H, W, B = int(round(H_TU * T)), int(round(WIN_TU * T)), int(round(BLOCK_TU * T))
    w = World(A, rule)
    prev = periodic_centroid(w.A)
    disp = np.zeros((H, 2))
    masses, gyrs = [], []
    dead = False
    for s in range(1, H + 1):
        w.step()
        m = w.A.sum()
        if m <= 1e-12:
            dead = True
            break
        c = periodic_centroid(w.A)
        disp[s - 1] = wrap(c[0] - prev[0], n), wrap(c[1] - prev[1], n)
        prev = c
        if s > H - W and (s - (H - W)) % max(1, int(round(T))) == 0:  # every 1 tu = "10-step samples" at T=10
            masses.append(m / R**2)
            gyrs.append(gyradius(w.A, *c) / R)
    if dead:
        return dict(end_mass=0.0, win_mass_min=0.0, win_mass_max=0.0, win_gyr_min=np.nan,
                    win_gyr_max=np.nan, win_speed=0.0, win_mass_mean=0.0, win_gyr_mean=np.nan)
    blocks = disp[H - W:].reshape(-1, B, 2).sum(axis=1)
    speed = float(np.mean(np.hypot(blocks[:, 0], blocks[:, 1])) / BLOCK_TU / R)
    return dict(end_mass=float(w.A.sum() / R**2), win_mass_min=min(masses), win_mass_max=max(masses),
                win_gyr_min=min(gyrs), win_gyr_max=max(gyrs), win_speed=speed,
                win_mass_mean=float(np.mean(masses)), win_gyr_mean=float(np.mean(gyrs)))


def classify(m, ref, band=0.2):
    if m["end_mass"] < 0.01:
        return "D"
    if m["end_mass"] > 2 * ref["mass"]:
        return "X"
    lo, hi = 1 - band, 1 + band
    ok = (lo * ref["mass"] <= m["win_mass_min"] and m["win_mass_max"] <= hi * ref["mass"]
          and lo * ref["gyr"] <= m["win_gyr_min"] and m["win_gyr_max"] <= hi * ref["gyr"]
          and lo * ref["speed"] <= m["win_speed"] <= hi * ref["speed"])
    return "R" if ok else "T"


_CTX = {}


def _init(rule_kw, n):
    rule = Rule(**rule_kw)
    _CTX.update(rule=rule, n=n, warm=warm_states(rule, n))


def _job(args):
    kind, phase, s = args
    rule, warm = _CTX["rule"], _CTX["warm"]
    t0, A, prev_c = warm[phase]
    c, h = frame(A, prev_c)
    E = apply(kind, s, A, c, h, rule.R)
    m = post_run(E, rule)
    m.update(intervention=kind, phase=phase, t0=t0, s=float(s),
             dM=float((E.sum() - A.sum()) / A.sum()))
    return m


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", type=float, default=10)
    ap.add_argument("--R", type=float, default=13)
    ap.add_argument("--interventions", nargs="*", default=list(GRIDS))
    ap.add_argument("--bisect-steps", type=int, default=6, help="halvings of the 0.05 bracket (6 -> 1/1280)")
    a = ap.parse_args(argv)
    rule_kw = dict(T=a.T, R=a.R)
    n = 2 * int(round(64 * a.R / 13))
    tag = f"T{a.T:g}-R{a.R:g}"
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    with Pool(os.cpu_count(), initializer=_init, initargs=(rule_kw, n)) as pool:
        # control first: sets the reference for non-baseline discretisations (amendment A1)
        ctrl = pool.map(_job, [("I001", p, 0.0) for p in range(PHASES)])
        if (a.T, a.R) == (10, 13):
            ref = dict(REF_T10_R13)
        else:
            ref = dict(mass=np.mean([c["win_mass_mean"] for c in ctrl]),
                       gyr=np.mean([c["win_gyr_mean"] for c in ctrl]),
                       speed=np.mean([c["win_speed"] for c in ctrl]))
        print(tag, "reference", ref)
        coarse = pool.map(_job, [(k, p, s) for k in a.interventions for p in range(PHASES)
                                 for s in GRIDS[k]], chunksize=1)
        for r in coarse:
            r["cls"] = classify(r, ref)
        # bisect each (intervention, phase) bracket in parallel, one halving per round
        brackets = {}
        for k in a.interventions:
            for p in range(PHASES):
                rows = sorted((r for r in coarse if r["intervention"] == k and r["phase"] == p),
                              key=lambda r: r["s"])
                fail = next((r["s"] for r in rows if r["cls"] != "R"), None)
                if fail is not None and fail > 0:
                    brackets[(k, p)] = [round(fail - 0.05, 4), fail]
        bis = []
        for _ in range(a.bisect_steps):
            jobs = [(k, p, sum(b) / 2) for (k, p), b in brackets.items()]
            res = pool.map(_job, jobs, chunksize=1)
            for (k, p, mid), r in zip(jobs, res):
                r["cls"] = classify(r, ref)
                bis.append(r)
                brackets[(k, p)][0 if r["cls"] == "R" else 1] = mid
    OUT.mkdir(parents=True, exist_ok=True)
    rows = coarse + bis
    keys = ["intervention", "phase", "t0", "s", "dM", "cls", "end_mass", "win_mass_min",
            "win_mass_max", "win_gyr_min", "win_gyr_max", "win_speed"]
    with open(OUT / f"disturb-{tag}.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, keys, extrasaction="ignore")
        wr.writeheader()
        for r in rows:
            wr.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    with open(OUT / f"disturb-{tag}-brackets.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["intervention", "phase", "s_ok", "s_fail", "s_star"])
        for (k, p), (lo, hi) in sorted(brackets.items()):
            wr.writerow([k, p, f"{lo:.6f}", f"{hi:.6f}", f"{(lo + hi) / 2:.6f}"])
    for (k, p), (lo, hi) in sorted(brackets.items()):
        print(tag, k, p, f"s* = {(lo + hi) / 2:.4f}  [{lo:.4f}, {hi:.4f}]")
    nonmono = [(r["intervention"], r["phase"], r["s"]) for r in coarse if r["cls"] == "R"
               and (r["intervention"], r["phase"]) in brackets and r["s"] > brackets[(r["intervention"], r["phase"])][1]]
    print(tag, "non-monotone recoveries above the bracket:", nonmono)
    print(tag, "coarse classes:", {k: "".join(r["cls"] for r in sorted(
        (r for r in coarse if r["intervention"] == k and r["phase"] == 0), key=lambda r: r["s"])) for k in a.interventions})


if __name__ == "__main__":
    main()
