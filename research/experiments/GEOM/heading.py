"""GEOM-H: does S001's heading lock to the lattice on a hex lattice, and on an amorphous glass?

Mirrors H001-X1 (h001_explore.py): S001 seeded at start rotation theta, 8000 steps (T = 10,
R = 13), heading of the periodic-centroid velocity in 1000-step windows. The worlds hold one cell
per unit area so R = 13 is the same physical radius as on the square grid.

Usage:  python heading.py {hex|glass|square} [step_deg] [max_deg] > heading_<lattice>.csv\n(hex: 0..30 by 1 covers the lattice's symmetry domain; glass: 0..30 by 2)
"""
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomlenia as g  # noqa: E402
from alm import specimens  # noqa: E402

STEPS, WIN, L = 8000, 1000, 128
HOME = 68.198  # S001 native heading in the patch frame, degrees (atan 5/2)


def world(kind):
    return {"hex": lambda: g.hex_torus(L), "glass": lambda: g.glass_torus(L, 0),
            "square": lambda: g.square_torus(L)}[kind]()


def run(args):
    kind, theta = args
    s = specimens.load("S001")
    w = world(kind)
    f = g.patch_sampler(s.cells / 255.0)
    c = np.array(w.box) / 2
    G = g.GraphLenia(w, s.rule, g.seed_torus(w, f, c, theta))
    cs = []
    for t in range(STEPS):
        G.step()
        cs.append(g.torus_centroid(w, G.A))
    cs = np.array(cs)
    box = np.array(w.box)
    d = np.diff(np.unwrap(cs * 2 * np.pi / box, axis=0), axis=0) * box / (2 * np.pi)
    out = []
    for k in range(STEPS // WIN):
        vx, vy = d[k * WIN:(k + 1) * WIN - 1].mean(0)
        out.append((np.degrees(np.arctan2(vy, vx)) % 360, np.hypot(vx, vy) / s.rule.R * s.rule.T))
    return kind, theta, int(G.A.sum() > 1), float(G.A.sum()), out


if __name__ == "__main__":
    kind = sys.argv[1]
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 1
    mx = float(sys.argv[3]) if len(sys.argv) > 3 else 60
    thetas = list(np.arange(0, mx + 1e-9, step))
    wins = [f"w{k}" for k in range(STEPS // WIN)]
    print("lattice,rot,expected,alive,mass," + ",".join(f"heading_{w}" for w in wins)
          + ",speed_R_per_time_last", flush=True)
    # rows are printed as runs finish (order varies); sort by rot when reading
    with Pool(int(os.environ.get("GEOM_PROCS", 4))) as p:
        for kind, th, alive, mass, out in p.imap_unordered(run, [(kind, float(t)) for t in thetas],
                                                           chunksize=1):
            print(f"{kind},{th:g},{(HOME + th) % 360:.3f},{alive},{mass:.4f},"
                  + ",".join(f"{h:.3f}" for h, _ in out) + f",{out[-1][1]:.5f}", flush=True)
