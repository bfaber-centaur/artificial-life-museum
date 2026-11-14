"""WINGS-FL: Flow-Lenia rule FL-43 (flow_scan rule seed 43) turns a noise patch into a colony of
ring cells. Does the number of cells follow the mass? And what does the rule do without
mass conservation?

Arms, all on a 256^2 torus, 3000 steps (600 time units, dt 0.2):
  size-<p>-s<k> : p x p patch of uniform(0, 1) noise from default_rng([17, k]) at the centre,
                  p in {20, 28, 40, 56, 80} (mass ~ p^2), k in {0, 1, 2, 3}; conservation on
  classic-s<k>  : p 40, same kernels and affinity, but A <- clip(A + dt U, 0, 1) (no flow, no
                  conservation), 1500 steps
Per run: total mass at start and end, components above 0.05 (torus-merged), mass of each.
Writes flow_rings.jsonl.

  python flow_rings.py sizes|classic
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from flow_lenia import FlowLenia, FlowRule
from flow_scan import comps

HERE = Path(__file__).parent
N = 256
RULE_SEED = 43


def rule():
    rng = np.random.default_rng([7, RULE_SEED])
    return FlowRule.random(rng)


def patch_state(p, k, n=N):
    rng = np.random.default_rng([17, k])
    A = np.zeros((n, n)); o = (n - p) // 2
    A[o:o + p, o:o + p] = rng.uniform(0, 1, (p, p))
    return A


def measure(A):
    lab, ids = comps(A)
    masses = sorted((float(A[lab == i].sum()) for i in ids), reverse=True)
    return masses


def go(key, A, steps, conserve=True):
    L = FlowLenia(rule(), A, conserve=conserve)
    m0 = float(L.A.sum())
    for _ in range(steps):
        L.step()
    masses = measure(L.A)
    rec = {"key": key, "steps": steps, "conserve": conserve, "mass0": m0, "mass1": float(L.A.sum()),
           "rel_mass_drift": float(L.A.sum() / m0 - 1), "ncomp": len(masses), "comp_masses": [round(x, 3) for x in masses],
           "cover": float((L.A > 0.05).mean()),
           "final_sha256": hashlib.sha256(np.ascontiguousarray(L.A).tobytes()).hexdigest()}
    with (HERE / "flow_rings.jsonl").open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    np.save(HERE / "states" / f"fr_{key}.npy", L.A.astype(np.float32))
    print(key, rec["ncomp"], "median %.1f" % (np.median(masses) if masses else 0), "drift %.1e" % rec["rel_mass_drift"], flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "sizes":
        for k in range(4):
            for p in (20, 28, 40, 56, 80):
                go(f"size-{p}-s{k}", patch_state(p, k), 3000)
    else:
        for k in range(4):
            go(f"classic-s{k}", patch_state(40, k), 1500, conserve=False)
