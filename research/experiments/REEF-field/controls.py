"""F-003/F-004: isolated controls, pilot geometry (protocol §4) and torus censoring times (§6.6).

Usage (repo root): python research/experiments/REEF-field/controls.py
Writes controls.json, controls-series.npz, geometry.json and appends manifests to runs.jsonl.
"""

from __future__ import annotations

import json
import time

import numpy as np

from reefcore import HERE, N, RULE, fit_motion, load_state, provenance, track
from alm.morphometrics import centroid, gyradius, min_image
from alm.provenance import state_sha256
from scipy.ndimage import binary_dilation

T, R = int(RULE.T), RULE.R
H = 50  # tu, D-005
STEPS = H * T
THETA_S = 0.01  # protocol §6.1 proposal; the clip makes the support identical down to 1e-6 (R-001)
GUARD = 2.0  # R, §6.6
B_LIST = (-1.0, 0.0, 1.0)
GAP = 4.0  # R, §4


def body_stats(A, c):
    """Gyradius (R) and support radius (R, max centroid distance of a cell with A > THETA_S)."""
    ys, xs = np.nonzero(A > THETA_S)
    dy = min_image(ys - c[0], A.shape[0])
    dx = min_image(xs - c[1], A.shape[1])
    return gyradius(A, c, R), float(np.hypot(dy, dx).max() / R) if len(ys) else np.nan


def window_noise(res, gyr):
    """Per-1-tu window statistics over the horizon: mean and sd across windows."""
    pos, mass = res["pos"], res["mass"]
    n = (len(mass) - 1) // T
    d = np.array([pos[(k + 1) * T] - pos[k * T] for k in range(n)])
    spd = np.hypot(d[:, 0], d[:, 1]) / R
    hd = np.degrees(np.arctan2(d[:, 0], d[:, 1]))
    m = np.array([mass[k * T : (k + 1) * T].mean() for k in range(n)])
    g = np.array([gyr[k * T : (k + 1) * T].mean() for k in range(n)])

    def ms(x):
        return {"mean": float(x.mean()), "sd": float(x.std(ddof=1)), "min": float(x.min()), "max": float(x.max())}

    return {"speed_R_per_tu": ms(spd), "heading_deg": ms(hd), "mass_R2": ms(m), "gyradius_R": ms(g),
            "per_step_mass_rsd": float(mass.std() / mass.mean()),
            "per_step_gyradius": ms(gyr)}


def run_control(name, A0, steps):
    gyr = np.empty(steps + 1)
    rad = np.empty(steps + 1)
    cs = {}

    def on_step(t, A):
        c = centroid(A)
        gyr[t], rad[t] = body_stats(A, c)

    t0 = time.time()
    res = track(A0, steps, comp_every=1, keep={0, steps}, on_step=on_step)
    wall = time.time() - t0
    comps = np.array([res["ncomp"][t] for t in range(steps + 1)])
    out = {
        "name": name,
        "steps": steps,
        "initial_state_sha256": state_sha256(A0),
        "final_state_sha256": state_sha256(res["final"]),
        "motion_fit": fit_motion(res["pos"], 0, steps),
        "noise_1tu": window_noise(res, gyr),
        "support_radius_R_max": float(np.nanmax(rad)),
        "support_radius_R_mean": float(np.nanmean(rad)),
        "ncomp_fraction": {int(k): float((comps == k).mean()) for k in np.unique(comps)},
        "displacement_R": list(map(float, (res["pos"][-1] - res["pos"][0]) / R)),
        "wall_s": wall,
    }
    return out, res, gyr, rad


def main():
    prov = provenance()
    GA, mGA = load_state(HERE / "seeds" / "GA.npy")
    GB, mGB = load_state(HERE / "seeds" / "GB.npy")
    S, mS = load_state(HERE / "seeds" / "S103.npy")
    out = {"provenance": prov, "theta_s": THETA_S, "H_tu": H}
    series = {}
    ctrl = {}
    for name, A in (("GA", GA), ("GB", GB)):
        o, res, gyr, rad = run_control(f"REEF-CTRL-{name}", A, STEPS)
        ctrl[name] = (o, res)
        out[name] = o
        series[f"{name}_mass"], series[f"{name}_pos"], series[f"{name}_gyr"] = res["mass"], res["pos"], gyr
        print(name, json.dumps({k: o[k] for k in ("motion_fit", "support_radius_R_max", "ncomp_fraction", "wall_s")}, default=float))
    o, res, gyr, rad = run_control("REEF-CTRL-GA-100tu", GA, 2 * STEPS)
    out["GA_100tu"] = o
    o, resS, gyrS, radS = run_control("REEF-CTRL-S103", S, STEPS)
    o["bitwise_fixed_through_H"] = o["final_state_sha256"] == o["initial_state_sha256"]
    out["S103"] = o
    print("S103", o["bitwise_fixed_through_H"], o["support_radius_R_max"])

    # Geometry (§4) and censoring (§6.6) per snapshot and offset.
    rS = out["S103"]["support_radius_R_max"]
    cS0 = np.array(centroid(S))
    ys, xs = np.nonzero(S > THETA_S)
    S_pts = np.stack([ys - cS0[0], xs - cS0[1]], 1)
    geo = {"theta_s": THETA_S, "gap_R_target": GAP, "guard_R": GUARD, "pilots": []}
    pid = 0
    for snap, A in (("GA", GA), ("GB", GB)):
        o, res = ctrl[snap]
        rG = o["support_radius_R_max"]
        mf = o["motion_fit"]
        hd = np.radians(mf["heading_deg"])
        h = np.array([np.sin(hd), np.cos(hd)])  # (y, x)
        nrm = np.array([h[1], -h[0]])  # n = (-h_y, h_x) in (x, y) -> (y, x) = (h_x, -h_y)
        cG = np.array(centroid(A))
        gy, gx = np.nonzero(A > THETA_S)
        G_pts = np.stack([gy - cG[0], gx - cG[1]], 1)
        front = float((G_pts @ h).max())
        back = float((S_pts @ h).min())
        for b in B_LIST:
            pid += 1
            d_req = GAP * R + front - back
            target = cG + d_req * h + b * R * nrm
            shift = np.rint(target - cS0).astype(int)
            cS = cS0 + shift
            rel = cS - cG
            d_real, b_real = float(rel @ h / R), float(rel @ nrm / R)
            # clear gap along h, with realised positions, among support cells overlapping laterally
            Sp = S_pts + cS
            gap = float(((Sp - cG) @ h).min() - front) / R
            # torus: centroid-distance criterion of §6.6 on the undisturbed G-alone track
            D_int = rG + rS + 1.0 + GUARD  # R
            pos = res["pos"]
            rel_t = (cS[None, :] - pos) / R  # ring minus glider, unwrapped glider, (steps+1, 2)
            Nr = N / R
            best = {}
            for ky in range(-4, 5):
                for kx in range(-4, 5):
                    dist = np.hypot(rel_t[:, 0] + ky * Nr, rel_t[:, 1] + kx * Nr)
                    best[(ky, kx)] = dist
            primary = best[(0, 0)]
            # first approach time on the primary image (centroid distance minimum)
            t_close = int(np.argmin(primary))
            others = np.min([v for k, v in best.items() if k != (0, 0)], axis=0)
            hit = np.nonzero(others < D_int)[0]
            t_cen = float(hit[0] / T) if len(hit) else None
            # geometric (non-interacting) support contact on the primary image
            t_c_geo = None
            Smask = np.zeros((N, N), bool)
            Smask[(Sp[:, 0].astype(int)) % N, (Sp[:, 1].astype(int)) % N] = True
            Sdil = binary_dilation(Smask, np.ones((3, 3)))
            geo["pilots"].append({
                "pilot": f"P{pid}", "snapshot": snap, "b_R_requested": b, "d_R_requested": d_req / R,
                "ring_shift_cells_yx": shift.tolist(), "ring_centroid_yx": cS.tolist(),
                "glider_centroid_yx": cG.tolist(), "heading_deg": mf["heading_deg"],
                "d_R_realized": d_real, "b_R_realized": b_real, "gap_R_realized": gap,
                "glider_front_R": front / R, "ring_back_R": back / R,
                "D_int_R": D_int, "t_closest_primary_tu": t_close / T,
                "min_dist_primary_R": float(primary.min()),
                "t_cen_tu": t_cen, "min_dist_other_images_R_over_H": float(others.min()),
                "_Sdil": Sdil,
            })
    # geometric contact time per pilot from the G-alone states (recomputed with kept-every-step)
    for snap, A in (("GA", GA), ("GB", GB)):
        pil = [p for p in geo["pilots"] if p["snapshot"] == snap]
        tc = {p["pilot"]: None for p in pil}

        def on_step(t, X, pil=pil, tc=tc):
            sup = X > THETA_S
            for p in pil:
                if tc[p["pilot"]] is None and (sup & p["_Sdil"]).any():
                    tc[p["pilot"]] = t / T

        track(A, STEPS, comp_every=10**9, on_step=on_step)
        for p in pil:
            p["t_c_geometric_tu"] = tc[p["pilot"]]
            p["t_c_plus_20_le_t_cen"] = (p["t_cen_tu"] is None) or (tc[p["pilot"]] is not None and tc[p["pilot"]] + 20 <= p["t_cen_tu"])
            del p["_Sdil"]
    out["geometry"] = geo
    np.savez_compressed(HERE / "controls-series.npz", **series)
    (HERE / "controls.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    for p in geo["pilots"]:
        print(json.dumps(p, default=float))


if __name__ == "__main__":
    main()
