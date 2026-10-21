"""REEF-behavior: record an encounter with its matched controls, then score it.

Implements the measurement contract and outcome classes of research/experiments/REEF/PROTOCOL.md
§6-7 with the Gate A addendum §11 values (reef/coordinator 6b142be). Two halves, so scoring can
be re-run on a saved trace:

* ``EncounterRecorder(A_E0, A_G0, A_S0, params)`` follows the encounter E (labels G and S taken
  from the controls' initial supports) and both isolated controls in lockstep. Call
  ``update(A_E, A_G, A_S, t)`` once per sample (every step). It never steps a world.
* ``score_trace(rows, params)`` returns the manifest ``result`` object.
* ``score_run_dir(run_dir)`` reads a REEF-field runner directory (frames.npz, checkpoints.npz,
  trace.npz, manifest.json) and does both.

Units: lengths in R, times in tu, masses sum(A)/R^2, headings atan2(dy, dx) in degrees in array
coordinates. Signed lateral offset is positive toward +90 deg from the control heading.

    PYTHONPATH=src python research/experiments/REEF-behavior/score.py RUN_DIR [--out score.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from track import Tracker, TrackerConfig, superposition_defect, support_gap  # noqa: E402

CONTACT_GAP = np.sqrt(2) + 1e-9  # cells: 8-adjacent supports (PROTOCOL.md §6.4)


@dataclass(frozen=True)
class ScoreParams:
    """Defaults are the frozen Gate A values (PROTOCOL.md §11) for N256, R13, T10."""

    R: float = 13.0
    T: float = 10.0
    N: int = 256
    theta_s: float = 0.01
    body_mass: float = 0.005  # components lighter than this are debris
    debris_high: float = 0.01  # DEBRIS_HIGH flag if total debris exceeds this at any sample
    death_mass: float = 0.01  # a label owning less body mass than this is dead
    theta_int: float = 1e-10
    approach_timeout: float = 30.0
    post_contact: float = 20.0
    horizon: float = 50.0
    fit_window: float = 5.0  # tu: straight-line fit of the unwrapped centroid at the window end
    theta_defl: float = 1.0  # deg
    delta_lat: float = 0.1  # R
    shift_flag: float = 0.1  # R, longitudinal lead/lag
    glider_tol: float = 0.02  # relative mass and speed: "glider unchanged"
    ring_tol: float = 0.01  # relative mass and gyradius
    ring_moved: float = 0.1  # R
    glider_speed: float = 0.2  # R/tu net (L6-field GLIDER)
    static_speed: float = 0.02  # R/tu path (L6-field STATIC)
    bind_min: float = 2.0  # tu together, then apart: TEMP_BIND
    capture_last: float = 5.0  # tu together at the end of the window: CAPTURE
    censor_margin: float = 3.0  # R added to r_G + r_S for t_cen
    fill_frac: float = 0.25
    fill_level: float = 0.1
    g_kind: str = "glider"  # "passive": G is a static stand-in (D-018 X7/X8); no glider checks


def _lab(rec, lab):
    return rec["labels"][lab]


class EncounterRecorder:
    def __init__(self, A_E0, A_G0, A_S0, params: ScoreParams = ScoreParams(), t0: float = 0.0, residual=None):
        p = self.p = params
        cfg = TrackerConfig(theta=p.theta_s, debris_mass=p.body_mass, R=p.R)
        A_E0, A_G0, A_S0 = (np.asarray(a, float) for a in (A_E0, A_G0, A_S0))
        mG, mS = A_G0 >= p.theta_s, A_S0 >= p.theta_s
        if (mG & mS).any():
            raise ValueError("glider and ring supports overlap at t0")
        self.E = Tracker(A_E0, {"G": mG, "S": mS}, cfg, t0)
        self.G = Tracker(A_G0, {"G": mG}, cfg, t0)
        self.S = Tracker(A_S0, {"S": mS}, cfg, t0)
        s0 = _lab(self.S.records[0], "S")
        cy, cx = s0["centroid"]
        r = int(np.ceil(s0["radius"])) + 3  # box around the ring for the RING_EXACT test
        n = A_S0.shape[0]
        self._box = (np.arange(int(cy) - r, int(cy) + r + 1) % n, np.arange(int(cx) - r, int(cx) + r + 1) % n)
        self.rows = []
        self._row(A_E0, A_G0, A_S0, t0, residual)

    def update(self, A_E, A_G, A_S, t, residual=None):
        A_E, A_G, A_S = (np.asarray(a, float) for a in (A_E, A_G, A_S))
        self.E.update(A_E, t)
        self.G.update(A_G, t)
        self.S.update(A_S, t)
        return self._row(A_E, A_G, A_S, t, residual)

    def _row(self, A_E, A_G, A_S, t, residual):
        p = self.p
        e, g, s = self.E.records[-1], self.G.records[-1], self.S.records[-1]
        by, bx = self._box
        d = superposition_defect(A_E, A_G, A_S)
        row = {
            "t": t,
            **d,
            "residual": d["defect_max"] if residual is None else float(residual),
            # exact-support (A > 0) gap of the controls: interaction is impossible while > 2R
            "ctrl_exact_gap": support_gap(np.argwhere(A_G > 0), np.argwhere(A_S > 0), A_E.shape),
            "fill": float(np.mean(A_E > p.fill_level)),
            "ring_box_equal": bool(np.array_equal(A_E[np.ix_(by, bx)], A_S[np.ix_(by, bx)])),
            "E": {k: e[k] for k in ("topology", "n_bodies", "n_components", "support_gap", "total_mass",
                                    "halo_mass", "orphan_mass", "debris_mass", "unassigned_mass", "labels", "bodies")},
            "Gc": {**_lab(g, "G"), "n_bodies": g["n_bodies"], "debris_mass": g["debris_mass"], "total_mass": g["total_mass"]},
            "Sc": {**_lab(s, "S"), "n_bodies": s["n_bodies"], "debris_mass": s["debris_mass"], "total_mass": s["total_mass"]},
        }
        self.rows.append(row)
        return row

    def write(self, out_dir) -> Path:
        d = Path(out_dir)
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "trace.jsonl", "w") as f:
            for r in self.rows:
                f.write(json.dumps(r) + "\n")
        (d / "tracker-events.json").write_text(json.dumps({"E": self.E.events, "G": self.G.events, "S": self.S.events}, indent=1))
        (d / "score-params.json").write_text(json.dumps(asdict(self.p), indent=1))
        return d / "trace.jsonl"


# --- scoring --------------------------------------------------------------------------------


def _first(rows, pred):
    for r in rows:
        if pred(r):
            return r["t"]
    return None


def _fit(rows, t_end, W, get):
    """Least-squares straight line through a tracked point over [t_end - W, t_end].

    Returns (position at t_end, velocity in cells/tu) or None if the point is missing."""
    seg = [r for r in rows if t_end - W - 1e-9 <= r["t"] <= t_end + 1e-9]
    pts = [get(r) for r in seg]
    if len(seg) < 3 or any(q is None for q in pts):
        return None
    t = np.array([r["t"] for r in seg]) - t_end
    P = np.asarray(pts, float)
    X = np.stack([np.ones_like(t), t], 1)
    coef, *_ = np.linalg.lstsq(X, P, rcond=None)
    return coef[0], coef[1]


def _path_speed(rows, t_end, W, get):
    seg = [r for r in rows if t_end - W - 1e-9 <= r["t"] <= t_end + 1e-9]
    pts = [get(r) for r in seg]
    if len(seg) < 2 or any(q is None for q in pts):
        return None
    return float(np.sum(np.hypot(*np.diff(np.asarray(pts, float), axis=0).T)) / (seg[-1]["t"] - seg[0]["t"]))


def _g_point(r):
    lg = r["E"]["labels"]["G"]
    return lg.get("unwrapped") if lg["status"] == "single" else None


def _ang(v):
    return float(np.degrees(np.arctan2(v[0], v[1])))


def _dang(a, b):
    return float((a - b + 180) % 360 - 180)


def _together(r):
    gap = r["E"]["support_gap"]
    return r["E"]["labels"]["G"]["status"] == "merged" or (gap is not None and gap <= CONTACT_GAP)


def _runs(rows, pred):
    """Contiguous (start, end) time intervals where pred holds."""
    out, start, last = [], None, None
    for r in rows:
        if pred(r):
            start = r["t"] if start is None else start
            last = r["t"]
        elif start is not None:
            out.append((start, last))
            start = None
    if start is not None:
        out.append((start, last))
    return out


def censor_time(rows, p: ScoreParams, t_c):
    """§11 t_cen: first time a G-carrying body centroid comes within r_G + r_S + 3R of a ring image
    it has not met (any image but the one nearest at t0), or meets the ring again after a release.
    Returns (t_cen, reason)."""
    s0, g0 = rows[0]["Sc"], rows[0]["Gc"]
    ring = np.asarray(s0["unwrapped"])
    lim = g0["radius"] + s0["radius"] + p.censor_margin * p.R
    N = p.N
    imgs = [(jy, jx) for jy in range(-3, 4) for jx in range(-3, 4)]
    start = np.asarray(rows[0]["E"]["labels"]["G"]["unwrapped"])
    primary = min(imgs, key=lambda j: np.hypot(*(start - ring - np.array(j) * N)))
    released = False
    for r in rows:
        for b in r["E"]["bodies"]:
            if "G" not in b["owners"] or "S" in b["owners"]:
                continue
            q = np.asarray(b["unwrapped"])
            for j in imgs:
                if j != primary and np.hypot(*(q - ring - np.array(j) * N)) < lim:
                    return r["t"], f"G body within {lim / p.R:.2f} R of ring image {j} (primary {primary})"
        if t_c is not None and r["t"] > t_c:
            if not _together(r):
                released = True
            elif released:
                return r["t"], "second contact with the ring after a release"
    return None, None


def score_trace(rows, p: ScoreParams = ScoreParams()) -> dict:
    R, W = p.R, p.fit_window
    t_int = _first(rows, lambda r: r["residual"] > p.theta_int)
    t_kr = _first(rows, lambda r: r["ctrl_exact_gap"] < 2 * R)
    t_c = _first(rows, lambda r: r["t"] <= p.approach_timeout + 1e-9 and _together(r))
    t_cen, why = censor_time(rows, p, t_c)
    t_last = rows[-1]["t"]
    planned = (t_c + p.post_contact) if t_c is not None else p.horizon
    t_end = min(x for x in (planned, p.horizon, t_last, t_cen) if x is not None)
    censored = t_end < planned - 1e-9 and t_cen is not None and t_cen <= t_end + 1e-9
    truncated = t_last < min(planned, p.horizon) - 1e-9
    win = [r for r in rows if r["t"] <= t_end + 1e-9]
    end = win[-1]
    flags = []
    obs = {"t_end": end["t"], "planned_end": planned, "window_after_contact_tu": None if t_c is None else end["t"] - t_c}
    if truncated:
        flags.append("TRACE_TRUNCATED")
    debris_max = max(r["E"]["debris_mass"] for r in win)
    obs["debris_max"] = debris_max
    if debris_max > p.debris_high:
        flags.append("DEBRIS_HIGH")
    if t_int is not None and t_kr is not None and t_int < t_kr:
        flags.append("RESIDUAL_BEFORE_KERNEL_RANGE")  # should be impossible: check the floor
    obs["t_int_minus_t_c"] = None if (t_int is None or t_c is None) else t_int - t_c

    def out(cls):
        # D-016: post-hoc descriptive flag, never replaces the class
        ctrl = end["Gc"]["total_mass"] + end["Sc"]["total_mass"]
        if end["E"]["n_bodies"] > 10 and end["E"]["total_mass"] > 10 * ctrl and "PROLIFERATION" not in flags:
            flags.append("PROLIFERATION")
        return {
            "class": "CENSORED" if censored and cls != "CONTROL_FAILURE" else cls,
            "partial_class": cls if censored else None,
            "flags": flags,
            "t_int": t_int,
            "t_kr": t_kr,
            "t_c": t_c,
            "t_cen": t_cen,
            "censor_reason": why if censored else None,
            "observables": obs,
            "params": asdict(p),
        }

    # controls must stay in class through the whole window
    s0 = rows[0]["Sc"]
    fitG = _fit(win, end["t"], W, lambda r: r["Gc"].get("unwrapped"))
    g_ctrl_ok = all(r["Gc"]["status"] == "single" and r["Gc"]["n_bodies"] == 1 for r in win)
    if fitG is None or np.hypot(*fitG[1]) / R <= p.glider_speed:
        g_ctrl_ok = False
    if p.g_kind == "passive":  # blob-alone is validated to die; record when, never a GLIDER check
        g_ctrl_ok = True
        obs["control_G_lost_at"] = _first(rows, lambda r: r["Gc"]["status"] == "lost")
        flags.append("PASSIVE_STAND_IN")
    s_ctrl_ok = all(r["Sc"]["status"] == "single" and r["Sc"]["n_bodies"] == 1 and r["Sc"]["mass"] == s0["mass"] for r in win)
    if fitG is not None:
        obs["control_G_speed_R_tu"] = float(np.hypot(*fitG[1]) / R)
        obs["control_G_heading_deg"] = _ang(fitG[1])
    if not (g_ctrl_ok and s_ctrl_ok):
        flags.append(("G" if not g_ctrl_ok else "") + ("S" if not s_ctrl_ok else "") + "_CONTROL_OUT_OF_CLASS")
        return out("CONTROL_FAILURE")

    e = end["E"]
    lg, ls = e["labels"]["G"], e["labels"]["S"]
    bodies = e["bodies"]
    together_runs = _runs(win, _together)
    longest = max((b - a + 1 / p.T for a, b in together_runs), default=0.0)
    obs.update(
        n_bodies=e["n_bodies"],
        topology=e["topology"],
        contact_lineage=[b["contact_lineage"] for b in bodies],
        total_mass=e["total_mass"],
        unassigned_mass=e["unassigned_mass"],
        bodies=[{k: b[k] for k in ("owners", "mass", "owned_mass", "gyradius", "radius", "unwrapped")} for b in bodies],
        together_intervals=together_runs,
        together_longest_tu=longest,
        ring_box_bitwise_equal_at_end=end["ring_box_equal"],
        fill=end["fill"],
        G_mass=lg["mass"],
        S_mass=ls["mass"],
    )
    if end["fill"] > p.fill_frac:
        return out("FILL")

    # ring
    sb = [b for b in bodies if b["owners"] == "S"]
    ring_ok = None
    if ls["status"] == "single" and sb:
        b = sb[0]
        obs["ring_mass_rel"] = b["mass"] / s0["mass"] - 1
        obs["ring_gyr_rel"] = b["gyradius"] / s0["gyradius"] - 1
        obs["ring_shift_R"] = float(np.hypot(*np.subtract(b["unwrapped"], s0["unwrapped"]))) / R
        ring_ok = abs(obs["ring_mass_rel"]) <= p.ring_tol and abs(obs["ring_gyr_rel"]) <= p.ring_tol
        if end["ring_box_equal"]:
            flags.append("RING_EXACT")
        elif ring_ok:
            flags.append("RING_PERTURBED")
        if obs["ring_shift_R"] >= p.ring_moved:
            flags.append("RING_MOVED")

    # glider kinematics vs control (straight-line fits over the last fit_window)
    fitE = _fit(win, end["t"], W, _g_point) if p.g_kind == "glider" else None
    big_turn = False
    if fitE is not None:
        h = fitG[1] / np.hypot(*fitG[1])
        left = np.array([h[1], -h[0]])
        left = left if _dang(_ang(left), _ang(h)) > 0 else -left
        dpos = fitE[0] - fitG[0]
        obs.update(
            glider_speed_R_tu=float(np.hypot(*fitE[1]) / R),
            glider_heading_deg=_ang(fitE[1]),
            heading_change_deg=_dang(_ang(fitE[1]), _ang(fitG[1])),
            lateral_R=float(dpos @ left) / R,
            longitudinal_R=float(dpos @ h) / R,
            speed_ratio=float(np.hypot(*fitE[1]) / np.hypot(*fitG[1])),
            glider_mass_ratio=lg["mass"] / end["Gc"]["mass"],
        )
        big_turn = abs(obs["heading_change_deg"]) >= p.theta_defl or abs(obs["lateral_R"]) >= p.delta_lat
        if abs(obs["longitudinal_R"]) >= p.shift_flag:
            flags.append("SHIFT_LEAD" if obs["longitudinal_R"] > 0 else "SHIFT_LAG")
        if abs(obs["speed_ratio"] - 1) > p.glider_tol or abs(obs["glider_mass_ratio"] - 1) > p.glider_tol:
            flags.append("GLIDER_CHANGED")
    g_is_glider = fitE is not None and np.hypot(*fitE[1]) / R > p.glider_speed

    if t_c is None:
        if t_int is not None:
            flags.append("INTERACTION_WITHOUT_CONTACT")
        if big_turn:
            flags.append("DEFLECTED_WITHOUT_CONTACT")
        if ring_ok is False:
            flags.append("RING_CHANGED_WITHOUT_CONTACT")
        return out("NO_CONTACT")

    g_dead, s_dead = lg["mass"] < p.death_mass, ls["mass"] < p.death_mass
    if g_dead or s_dead:
        return out("BOTH_DEATH" if g_dead and s_dead else ("G_DEATH" if g_dead else "S_DEATH"))
    if e["n_bodies"] > 2:
        return out("FISSION")

    tail = [r for r in win if r["t"] >= end["t"] - p.capture_last - 1e-9]
    if all(_together(r) for r in tail) and end["t"] - p.capture_last >= (t_c or 0) - 1e-9:
        if lg["status"] == "merged":
            jp = _path_speed(win, end["t"], p.capture_last, lambda r: next(
                (b["unwrapped"] for b in r["E"]["bodies"] if "G" in b["owners"] and "S" in b["owners"]), None))
            obs["joint_path_speed_R_tu"] = None if jp is None else jp / R
            if jp is not None and jp / R >= p.static_speed:
                flags.append("JOINT_BODY_MOVING")
                return out("CONVERT")
        return out("CAPTURE")
    if _together(end):
        flags.append("TOGETHER_AT_END_NOT_CONTINUOUS")
    if _together(end):  # together at the end but not for the whole capture tail (D-013)
        released = any(b - a + 1 / p.T >= p.bind_min for a, b in together_runs[:-1])
        return out("TEMP_BIND" if released else "UNRESOLVED_BIND")
    if longest >= p.bind_min:
        if big_turn:
            flags.append("DEFLECT")
        if ring_ok is False:
            flags.append("RING_CHANGED")
        return out("TEMP_BIND")
    if together_runs:
        flags.append("BRIEF_CONTACT")  # together, but for less than bind_min
    if not g_is_glider:
        gp = _path_speed(win, end["t"], W, _g_point)
        obs["glider_path_speed_R_tu"] = None if gp is None else gp / R
        flags.append("G_NOT_GLIDER")
        return out("CONVERT")
    if ring_ok is False:
        if big_turn:
            flags.append("DEFLECT")
        return out("RING_CHANGED")
    if big_turn:
        obs["deflection_sign"] = int(np.sign(obs["heading_change_deg"]))
        return out("DEFLECT")
    return out("PASS")


# --- REEF-field run directories ---------------------------------------------------------------


def record_run_dir(run_dir, params: ScoreParams | None = None, frames=None) -> EncounterRecorder:
    """Track a REEF-field runner directory. E and G come from frames.npz (float32, every step); S
    is the float64 t=0 checkpoint, verified bitwise against every S checkpoint; the residual is the
    runner's float64 per-step value from trace.npz."""
    d = Path(run_dir)
    man = json.loads((d / "manifest.json").read_text())
    N, R, T = man["world"]["N"], man["rule"]["R"], man["rule"]["T"]
    snap = ((man.get("inputs") or {}).get("glider") or {}).get("snapshot") or ""
    p = params or ScoreParams(N=N, R=float(R), T=float(T), horizon=float(man["horizon_tu"]),
                              g_kind="passive" if str(snap).startswith("BLOB") else "glider")
    fr = np.load(frames or d / "frames.npz")
    ck = np.load(d / "checkpoints.npz")
    tr = np.load(d / "trace.npz")
    S0 = ck["S_00000"]
    s_const = all(np.array_equal(ck[k], S0) for k in ck.files if k.startswith("S_"))
    E, G, res = fr["E"], fr["G"], tr["residual_max"]
    rec = EncounterRecorder(E[0], G[0], S0, p, 0.0, res[0])
    for k in range(1, len(E)):
        rec.update(E[k], G[k], S0, k / T, res[k])
    rec.s_checkpoints_constant = s_const
    rec.manifest = man
    return rec


def ring_exact_f64(run_dir, rec, t_end):
    """D-013: RING_EXACT judged on the latest float64 E checkpoint at or before the window end."""
    ck = np.load(Path(run_dir) / "checkpoints.npz")
    T = rec.p.T
    steps = sorted(int(k[2:]) for k in ck.files if k.startswith("E_") and int(k[2:]) <= round(t_end * T))
    k = steps[-1]
    by, bx = rec._box
    E, S = ck[f"E_{k:05d}"], ck["S_00000"]
    return bool(np.array_equal(E[np.ix_(by, bx)], S[np.ix_(by, bx)])), k / T


def score_run_dir(run_dir, params: ScoreParams | None = None, frames=None):
    """Returns (result, recorder) for a REEF-field run directory (frames.npz may live elsewhere)."""
    rec = record_run_dir(run_dir, params, frames)
    res = score_trace(rec.rows, rec.p)
    exact, t_ck = ring_exact_f64(run_dir, rec, res["observables"]["t_end"])
    fl = [f for f in res["flags"] if f not in ("RING_EXACT", "RING_PERTURBED")]
    o = res["observables"]
    o["ring_exact_f64"], o["ring_exact_checkpoint_t"] = exact, t_ck
    if exact:
        fl.append("RING_EXACT")
    elif "ring_mass_rel" in o and abs(o["ring_mass_rel"]) <= rec.p.ring_tol and abs(o["ring_gyr_rel"]) <= rec.p.ring_tol:
        fl.append("RING_PERTURBED")
    res["flags"] = fl
    if not rec.s_checkpoints_constant:
        res["flags"].append("S_CHECKPOINTS_NOT_CONSTANT")
        res["class"] = "CONTROL_FAILURE"
    res["run_id"] = rec.manifest.get("run_id")
    res["frames"] = "float32 E/G frames; float64 S and residual"
    return res, rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--out", help="write the result JSON here (and trace.jsonl next to it)")
    ap.add_argument("--frames", help="frames.npz path if not in the run directory")
    a = ap.parse_args(argv)
    res, rec = score_run_dir(a.run_dir, frames=a.frames)
    if a.frames:
        import hashlib

        res["frames_sha256"] = hashlib.sha256(Path(a.frames).read_bytes()).hexdigest()
    if a.out:
        out = Path(a.out)
        rec.write(out.parent)
        out.write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps({k: res[k] for k in ("run_id", "class", "partial_class", "flags", "t_int", "t_kr", "t_c", "t_cen")}, default=float))


if __name__ == "__main__":
    main()
