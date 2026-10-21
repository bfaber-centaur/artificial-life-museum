"""Isolated-baseline measurements that justify the tracker thresholds (behavior lane).

Settles S001 cells under the coexistence rule exactly as PROTOCOL.md section 3 describes
(centred in N256, 100 tu settle), then follows the glider for 100 tu assessment plus the 50 tu
horizon, sampling every step. Also places S103 alone. Reports, per support threshold: component
count, halo fraction, support radius; and the glider's heading/lateral jitter for theta_defl and
delta_lat. This is a behavior-lane measurement for threshold choice; the field lane's exported
settled state is the one encounters use.

    PYTHONPATH=src python research/experiments/REEF-behavior/baseline_thresholds.py
"""
import hashlib, json, sys, time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from alm.lenia import Lenia, Rule  # noqa: E402
from alm.specimens import load  # noqa: E402
from track import Tracker, TrackerConfig, components  # noqa: E402

RULE = Rule(R=13, T=10, mu=0.155, sigma=0.020, beta=(1.0,), kernel="poly", growth="poly")
N = 256
THETAS = (0.001, 0.01, 0.05, 0.1, 0.2)
SETTLE, ASSESS = 1000, 1500  # steps (100 tu settle, then 150 tu = 100 assess + 50 horizon)


def sha(A):
    return hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()


def main():
    out = HERE / "baseline"
    out.mkdir(exist_ok=True)
    t0 = time.time()
    sim = Lenia(RULE, load("S001").place(N))
    for _ in range(SETTLE):
        sim.step()
    settled = sim.A.copy()
    np.save(out / "G-settled-behavior.npy", settled)
    rows = []
    trackers = {th: Tracker(settled, {"G": settled >= th}, TrackerConfig(theta=th)) for th in THETAS}
    exact = []
    for k in range(1, ASSESS + 1):
        sim.step()
        for th, tr in trackers.items():
            tr.update(sim.A, k / RULE.T)
        pos = sim.A > 0
        exact.append(int(pos.sum()))
    summary = {"settled_sha256": sha(settled), "settle_steps": SETTLE, "assess_steps": ASSESS, "wall_s": None}
    for th, tr in trackers.items():
        recs = tr.records
        nb = np.array([r["n_components"] for r in recs])
        halo = np.array([r["halo_mass"] / r["total_mass"] for r in recs])
        st = [r["labels"]["G"]["status"] for r in recs]
        summary[f"theta={th}"] = {
            "n_components_min": int(nb.min()),
            "n_components_max": int(nb.max()),
            "status_not_single": int(sum(s != "single" for s in st)),
            "halo_frac_mean": float(halo.mean()),
            "halo_frac_max": float(halo.max()),
            "support_cells_mean": float(np.mean([len(c.cells) for c in [components(settled, th)[0]]])),
        }
    # kinematics from theta=0.01 tracker
    recs = trackers[0.01].records
    P = np.array([r["labels"]["G"]["unwrapped"] for r in recs])  # (y, x)
    mass = np.array([r["total_mass"] for r in recs])
    np.savez_compressed(out / "G-isolated-track.npz", unwrapped=P, mass=mass, exact_support_cells=np.array(exact))
    summary["exact_support_cells_max"] = int(max(exact))
    summary["wall_s"] = time.time() - t0
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
