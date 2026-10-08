"""L3-002 runner: property persistence across R and T.

Protocol: research/experiments/L3-002-property-persistence/PREREGISTRATION.md
(fixed before this code was run). One run per specimen x condition; each writes a
summary row and per-time-unit series to research/traces/lane3/L3-002/.

    .venv/bin/python -m alm_check.persistence            # all 28 runs, then classify
    .venv/bin/python -m alm_check.persistence --classify # classify existing results only
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from multiprocessing import Pool

import numpy as np

from .lenia import REPO, Rule, World, gyradius, load_orbium, periodic_centroid, place

OUT = REPO / "research" / "traces" / "lane3" / "L3-002"
SPEC = REPO / "research" / "specimens"
HORIZON, WIN0 = 300.0, 100.0

SPECIMENS = {
    "S001": dict(mu=0.15, sigma=0.015, n=128, cls="glider", seed=None),
    "S101": dict(mu=0.15, sigma=0.015, n=192, cls="glider", seed="S101-orbium-pair"),
    "S102": dict(mu=0.155, sigma=0.020, n=128, cls="circler", seed="S102-circler"),
    "S103": dict(mu=0.155, sigma=0.020, n=128, cls="static", seed="S103-static-ring"),
}
CONDITIONS = {"B": (13, 10), "T20": (13, 20), "T40": (13, 40), "T80": (13, 80),
              "R26": (26, 10), "R39": (39, 10), "C": (26, 40)}


def seed_cells(spec: str) -> np.ndarray:
    s = SPECIMENS[spec]["seed"]
    if s is None:
        return load_orbium()
    return np.loadtxt(SPEC / s / "initial-cells-u8.csv", delimiter=",") / 255.0


def wrap(d, n):
    return (d + n / 2) % n - n / 2


def run_one(job) -> dict:
    spec, cond = job
    R, T = CONDITIONS[cond]
    k = R // 13
    sp = SPECIMENS[spec]
    cells = np.kron(seed_cells(spec), np.ones((k, k)))  # exact block replication
    n = sp["n"] * k
    A0 = place(cells, n)
    w = World(A0.copy(), Rule(R=R, T=T, mu=sp["mu"], sigma=sp["sigma"]))
    steps, w0 = int(HORIZON * T), int(WIN0 * T)
    mass, gyr = np.zeros(steps), np.full(steps, np.nan)
    disp = np.zeros((steps, 2))
    prev = periodic_centroid(w.A)
    for s in range(steps):
        w.step()
        m = w.A.sum()
        mass[s] = m / R**2
        if m <= 1e-12:
            mass[s:] = 0
            break
        c = periodic_centroid(w.A)
        disp[s] = wrap(c[0] - prev[0], n), wrap(c[1] - prev[1], n)
        prev = c
        if s >= w0:
            gyr[s] = gyradius(w.A, *c) / R
    win = slice(w0, steps)
    v_tu = disp.reshape(-1, T, 2).sum(axis=1)  # displacement per time unit (cells)
    vw = v_tu[int(WIN0):]
    net = float(np.hypot(*vw.sum(axis=0)) / (HORIZON - WIN0) / R)
    path = float(np.mean(np.hypot(vw[:, 0], vw[:, 1])) / R)
    ang = np.arctan2(vw[:, 0], vw[:, 1])
    turn = float(np.degrees(np.mean(np.abs(wrap(np.diff(ang), 2 * np.pi)))))
    mw = mass[win]
    row = dict(run_id=f"L3-002-{spec}-{cond}", specimen=spec, condition=cond, R=R, T=T, n=n,
               mu=sp["mu"], sigma=sp["sigma"], final_mass=float(mass[-1]),
               mass=float(mw.mean()), gyradius=float(np.nanmean(gyr[win])),
               net_speed=net, path_speed=path, turning_rate=turn,
               mass_rel_sd=float(mw.std() / mw.mean()) if mw.mean() > 0 else float("nan"),
               fixed_point=bool(np.array_equal(w.A, A0)))
    row["cls"] = phenotype(row)
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / f"{spec}-{cond}.npz", mass_per_step=mass, v_per_tu=v_tu,
                        final=w.A.astype(np.float32))
    with open(OUT / f"{spec}-{cond}.json", "w") as f:
        json.dump(row, f, indent=1)
    return row


def phenotype(r) -> str:
    if r["final_mass"] <= 0.01:
        return "dead"
    if r["net_speed"] >= 0.2:
        return "glider"
    if r["path_speed"] < 0.001:
        return "static"
    if r["net_speed"] < 0.05 and r["path_speed"] >= 0.2:
        return "circler"
    return "other"


# ------------------------------------------------------------ classification

PROPS = {"S001": ["mass", "gyradius", "net_speed", "mass_rel_sd"],
         "S101": ["mass", "gyradius", "net_speed", "mass_rel_sd"],
         "S102": ["mass", "gyradius", "turning_rate", "path_speed", "mass_rel_sd"],
         "S103": ["mass", "gyradius"]}


def load_rows():
    rows = {}
    for p in OUT.glob("*.json"):
        r = json.loads(p.read_text())
        rows[(r["specimen"], r["condition"])] = r
    return rows


def persists(rows, spec, cond):
    r = rows[(spec, cond)]
    if r["final_mass"] <= 0.01 or r["cls"] != SPECIMENS[spec]["cls"]:
        return False
    if spec == "S101":
        return r["mass"] >= 1.8 * rows[("S001", cond)]["mass"]
    return True


def label(x: dict, prop: str) -> dict:
    B, T20, T40, T80, R26, R39, C = (x[c] for c in CONDITIONS)
    xinf = 2 * T80 - T40
    e_T = abs(B - xinf) / abs(xinf) if xinf else float("inf")
    e_R = abs(B - R39) / abs(R39) if R39 else float("inf")
    conv_T = abs(T80 - T40) <= 0.5 * abs(T20 - B)
    conv_R = abs(R39 - R26) <= 0.5 * abs(R26 - B) or (R39 and abs(R39 - R26) / abs(R39) <= 0.005)
    pred_C = T40 + R26 - B
    sep = abs(C - pred_C) / abs(C) <= 0.01 if C else False
    if prop == "mass_rel_sd" and R39 < 1e-3 and T80 < 1e-3:
        lab = "vanishes with refinement"
    elif not (conv_T and conv_R):
        lab = "NOT-CONVERGED" + ("" if conv_T else " (T)") + ("" if conv_R else " (R)")
    elif e_T <= 0.02 and e_R <= 0.02:
        lab = "CONTINUUM-STABLE"
    else:
        which = [w for w, e in (("T", e_T), ("R", e_R)) if e > 0.02]
        lab = f"DISCRETISATION-BIASED ({', '.join(which)})"
    return dict(label=lab, x_inf_T=xinf, e_T=e_T, e_R=e_R, conv_T=bool(conv_T),
                conv_R=bool(conv_R), separable=bool(sep), pred_C=pred_C)


def classify():
    rows = load_rows()
    out = []
    for spec in SPECIMENS:
        ok = {c: persists(rows, spec, c) for c in CONDITIONS}
        whole = "persists everywhere" if all(ok.values()) else (
            "FINITE-RESOLUTION-ONLY (fails at " + ", ".join(c for c, v in ok.items() if not v) + ")")
        fp = {c: rows[(spec, c)]["fixed_point"] for c in CONDITIONS} if spec == "S103" else None
        for prop in PROPS[spec]:
            x = {c: rows[(spec, c)][prop] for c in CONDITIONS}
            res = dict(specimen=spec, property=prop, specimen_status=whole,
                       **{c: x[c] for c in CONDITIONS})
            if all(ok.values()):
                res.update(label(x, prop))
            else:
                res["label"] = "not labelled (specimen does not persist)"
            out.append(res)
        if fp is not None:
            out.append(dict(specimen=spec, property="fixed_point", specimen_status=whole,
                            label="yes at " + ", ".join(c for c, v in fp.items() if v)
                            + ("; no at " + ", ".join(c for c, v in fp.items() if not v)
                               if not all(fp.values()) else ""), **fp))
    keys = list(dict.fromkeys(k for r in out for k in r))
    with open(OUT / "labels.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, keys)
        wr.writeheader()
        for r in out:
            wr.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    with open(OUT / "runs.csv", "w", newline="") as f:
        rr = [rows[k] for k in sorted(rows)]
        wr = csv.DictWriter(f, list(rr[0]))
        wr.writeheader()
        for r in rr:
            wr.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    for r in out:
        print(r["specimen"], r["property"], "|", r["label"], "|", r["specimen_status"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--classify", action="store_true")
    a = ap.parse_args(argv)
    if not a.classify:
        jobs = [(s, c) for s in SPECIMENS for c in CONDITIONS]
        jobs.sort(key=lambda j: -CONDITIONS[j[1]][0] ** 2 * CONDITIONS[j[1]][1])  # big first
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        with Pool(os.cpu_count()) as p:
            for r in p.imap_unordered(run_one, jobs):
                print(r["run_id"], r["cls"], round(r["mass"], 5), round(r["net_speed"], 4))
    classify()


if __name__ == "__main__":
    main()
