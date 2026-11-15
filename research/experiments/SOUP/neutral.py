"""Drift baseline for the fit-or-lucky replays (C099-C101): how does a NEUTRAL patch fare at the
same 72 places?

Same settled one-species world as mutant.py / replay.py (kernel set 16, 256², dominant heredity,
no background mutation). The 72 places are exactly replay.py's: for mutant k and placement j the
disc (radius 10) is centred on a mass-weighted random cell from default_rng([777, k, j]).

Instead of a mutant genome each disc gets a *marker*: the resident genome h plus 1e-6 along one
genome axis (pointing into [0, 1]). A change of 1e-6 in a kernel weight has no systematic effect
on the dynamics, so the marked matter is a neutral lineage: whatever happens to it is what the
place and the world's own dynamics do to any patch of residents. Because the ten genome axes are
orthogonal, up to ten non-overlapping discs are traced in one run without mixing them up.
Places are packed greedily into groups of at most ten discs whose discs do not touch (torus
distance > 21). Metric exactly as replay.py: matter with A > 0.05 whose genome lies more than
halfway from h towards its marker, every 50 steps.

  python neutral.py plan                 print the groups
  python neutral.py run <g0> <g1> [steps]  run groups g0..g1-1, append to neutral.jsonl
"""
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from soup import Kernels, Soup  # noqa: E402
from mutant import RULE, N, settled  # noqa: E402

HERE = Path(__file__).parent
EPS = 1e-6


def places(A0):
    out = []
    for k in range(12):
        for j in range(6):
            rng = np.random.default_rng([777, k, j])
            c = rng.choice(N * N, p=(A0 / A0.sum()).ravel())
            y, x = divmod(int(c), N)
            out.append((k, j, y, x))
    return out


def tdist(a, b):
    dy = abs(a[2] - b[2]); dx = abs(a[3] - b[3])
    return np.hypot(min(dy, N - dy), min(dx, N - dx))


def plan(A0, K=10):
    groups = []
    for p in places(A0):
        for g in groups:
            if len(g) < K and all(tdist(p, q) > 21 for q in g):
                g.append(p)
                break
        else:
            groups.append([p])
    return groups


def run(g0, g1, steps=2500, every=50):
    kern = Kernels(np.random.default_rng([7, RULE]))
    A0, G0 = settled(kern)
    h = kern.h
    groups = plan(A0, kern.K)
    yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    for gi in range(g0, min(g1, len(groups))):
        G1 = G0.copy()
        marks = []
        for axis, (k, j, y, x) in enumerate(groups[gi]):
            dy = np.minimum(np.abs(yy - y), N - np.abs(yy - y))
            dx = np.minimum(np.abs(xx - x), N - np.abs(xx - x))
            disc = dy ** 2 + dx ** 2 <= 100
            sign = 1.0 if h[axis] < 0.5 else -1.0
            G1[axis, disc] = h[axis] + sign * EPS
            marks.append((k, j, y, x, axis, sign))
        S = Soup(kern, A0, G1, mut_every=0, inherit="dominant")
        series = {m[:2]: [] for m in marks}
        for t in range(steps + 1):
            if t % every == 0:
                live = S.A > 0.05
                for (k, j, y, x, axis, sign) in marks:
                    proj = sign * (S.G[axis] - h[axis])
                    series[(k, j)].append(round(float(S.A[live & (proj > EPS / 2)].sum()), 3))
            if t < steps:
                S.step()
        sha = hashlib.sha256(S.A.tobytes() + S.G.tobytes()).hexdigest()
        with open(HERE / "neutral.jsonl", "a") as fh:
            for (k, j, y, x, axis, sign) in marks:
                fh.write(json.dumps(dict(place_of_mutant=k, placement=j, y=y, x=x, group=gi, axis=axis,
                                         eps=EPS, every=every, marker_mass=series[(k, j)],
                                         group_final_sha256=sha)) + "\n")
        print(gi, [(m[0], m[1], series[m[:2]][0], series[m[:2]][-1]) for m in marks], flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "plan":
        kern = Kernels(np.random.default_rng([7, RULE]))
        A0, _ = settled(kern)
        for i, g in enumerate(plan(A0, kern.K)):
            print(i, len(g), [(p[0], p[1]) for p in g])
    else:
        a = [int(v) for v in sys.argv[2:]]
        run(*a)
