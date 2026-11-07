"""F-001/F-002: settle S001 cells under the coexistence rule, export GA/GB snapshots and S103.

Usage (repo root): python research/experiments/REEF-field/settle.py
Writes settle.json, settle-series.npz and seeds/*.npy(+.json) next to this file.
"""

from __future__ import annotations

import json
import time

import numpy as np

from reefcore import HERE, N, RULE, fit_motion, provenance, recentre, save_state, s103_state, track
from alm import specimens
from alm.lenia import Lenia
from alm.morphometrics import centroid, dominant_period
from alm.provenance import state_sha256

T = int(RULE.T)


def assess(res, t0, t1):
    mass, pos, ncomp = res["mass"], res["pos"], res["ncomp"]
    mid = (t0 + t1) // 2
    m = mass[t0 : t1 + 1]
    comps = [ncomp[t] for t in sorted(ncomp) if t0 <= t <= t1]
    whole = fit_motion(pos, t0, t1)
    h1, h2 = fit_motion(pos, t0, mid), fit_motion(pos, mid, t1)
    m1, m2 = mass[t0 : mid + 1].mean(), mass[mid : t1 + 1].mean()
    dh = (h2["heading_deg"] - h1["heading_deg"] + 180) % 360 - 180
    drift = {
        "mass_rel_change": float(abs(m2 - m1) / m1),
        "speed_rel_change": float(abs(h2["speed_R_per_tu"] - h1["speed_R_per_tu"]) / h1["speed_R_per_tu"]),
        "heading_change_deg": float(dh),
    }
    trips = {
        "mass": drift["mass_rel_change"] > 0.002,
        "speed": drift["speed_rel_change"] > 0.005,
        "heading": abs(drift["heading_change_deg"]) > 0.5,
    }
    accept = {
        "alive": bool(m.min() > 0),
        "one_component": bool(all(c == 1 for c in comps)),
        "mass_rsd_lt_1pct": bool(m.std() / m.mean() < 0.01),
        "speed_gt_0.1": bool(whole["speed_R_per_tu"] > 0.1),
        "straightness_gt_0.99": bool(whole["straightness"] > 0.99),
    }
    vy, vx = whole["vy_cells_per_step"], whole["vx_cells_per_step"]
    return {
        "window_steps": [t0, t1],
        "motion": whole,
        "halves": [h1, h2],
        "mass_mean": float(m.mean()),
        "mass_rsd": float(m.std() / m.mean()),
        "mass_min": float(m.min()),
        "mass_max": float(m.max()),
        "mass_halves": [float(m1), float(m2)],
        "ncomp_values": sorted(set(comps)),
        "dominant_mass_period_steps": dominant_period(m),
        "grid_crossing_period_steps": {"1/|vx|": 1 / abs(vx), "1/|vy|": 1 / abs(vy)},
        "drift": drift,
        "transient_trips": trips,
        "transient_remains": bool(any(trips.values())),
        "acceptance": accept,
        "accepted": bool(all(accept.values())),
    }


def main():
    t_start = time.time()
    s001 = specimens.load("S001")
    A0 = s001.place(N)
    out = {"procedure": "README F-001/F-002", "provenance": provenance(),
           "seed": {"specimen": s001.to_dict(), "placed_sha256": state_sha256(A0), "offset": [118, 118]}}

    end = 2000
    res = track(A0, end + 10, keep=set(range(end, end + 11)))
    a = assess(res, 1000, 2000)
    out["assessment"] = [a]
    series = {"mass_0": res["mass"], "pos_0": res["pos"]}
    if a["transient_remains"]:
        out["extension"] = "transient test tripped at 200 tu: " + ", ".join(k for k, v in a["transient_trips"].items() if v)
        res2 = track(res["states"][end], 3010, keep=set(range(3000, 3011)))
        # re-index: res2 step s corresponds to absolute step 2000 + s
        res2_abs = {"mass": np.concatenate([res["mass"][:end], res2["mass"]]),
                    "pos": np.concatenate([res["pos"][:end], res2["pos"] - res2["pos"][0] + res["pos"][end]]),
                    "ncomp": {**{t: c for t, c in res["ncomp"].items() if t < end},
                              **{t + end: c for t, c in res2["ncomp"].items()}}}
        a2 = assess(res2_abs, 4000, 5000)
        out["assessment"].append(a2)
        series = {"mass_0": res2_abs["mass"], "pos_0": res2_abs["pos"]}
        end = 5000
        states = {t + 2000: s for t, s in res2["states"].items()}
    else:
        out["extension"] = None
        states = res["states"]
    final_a = out["assessment"][-1]

    # Snapshots (F-004). GA = state at `end`; GB = P/2 if an intrinsic period exists, else +5 steps.
    pos = series["pos_0"]
    per = final_a["dominant_mass_period_steps"]
    gc = final_a["grid_crossing_period_steps"]
    grid = any(abs(per - g) / g < 0.10 for g in gc.values())
    intrinsic = bool(np.isfinite(per) and not grid)
    kB = int(round(per / 2)) if intrinsic else 5
    if kB > 10:
        raise SystemExit(f"intrinsic half-period {kB} steps exceeds kept states; rerun with more kept steps")
    ks = {"period_steps": per, "explained_by_grid_crossing": grid, "intrinsic_period": intrinsic}
    seeds = HERE / "seeds"
    seeds.mkdir(exist_ok=True)
    snaps = {}
    for name, t in (("GA", end), ("GB", end + kB)):
        B, roll = recentre(states[t])
        meta = save_state(seeds / f"{name}.npy", B, {
            "name": name, "kind": ("phase snapshot" if intrinsic else "named elapsed-time snapshot (not an intrinsic phase)"),
            "source_step": t, "source_tu": t / T, "source_state_sha256": state_sha256(states[t]),
            "integer_roll_yx": list(roll), "centroid_yx_after_roll": list(centroid(B)),
            "fractional_centroid_yx": list(map(float, np.mod(centroid(B), 1.0))),
            "mass_R2": float(B.sum() / RULE.R**2), "rule": RULE.to_dict(), "N": N,
            "heading_deg": final_a["motion"]["heading_deg"],
            "speed_R_per_tu": final_a["motion"]["speed_R_per_tu"],
        })
        snaps[name] = meta
    out["snapshots"] = {"GB_minus_GA_steps": kB, "period_test": ks, **snaps}

    # S103 export and local fixed-point check.
    R0 = s103_state(N)
    sim = Lenia(RULE, R0)
    sim.step()
    one = state_sha256(sim.A) == state_sha256(R0)
    for _ in range(999):
        sim.step()
    thousand = state_sha256(sim.A) == state_sha256(R0)
    meta = save_state(seeds / "S103.npy", R0, {
        "name": "S103", "kind": "catalogued clip fixed point, placed centred",
        "cells_sha256_int16le": specimens.load("S103").cells_sha256, "rule": RULE.to_dict(), "N": N,
        "centroid_yx": list(centroid(R0)), "mass_R2": float(R0.sum() / RULE.R**2),
        "fixed_point_after_1_step": one, "fixed_point_after_1000_steps": thousand,
    })
    out["S103"] = meta
    out["wall_s"] = time.time() - t_start

    np.savez_compressed(HERE / "settle-series.npz", **series)
    (HERE / "settle.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({"assessment": [{k: x[k] for k in ("motion", "mass_mean", "mass_rsd", "drift",
                      "transient_remains", "accepted", "dominant_mass_period_steps",
                      "grid_crossing_period_steps", "ncomp_values")} for x in out["assessment"]],
                      "kB": kB, "S103_fixed": [one, thousand], "wall_s": out["wall_s"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
