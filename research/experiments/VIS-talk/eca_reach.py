"""Which Wolfram elementary CA rules does classic 1-D Lenia reach exactly in its discrete limit?

Setting (claim C061): one-row world, R = 2 (poly or exp kernel core: weight 1/2 at offsets +-1 and
0 at the cell itself, because both cores vanish at r = 0 and r = 1), T = 1, binary states.
The next state is clip(c + G(u)) with u = (l + r) / 2. A rule counts as reached when all eight
neighbourhoods give 0 or 1 to within 1e-3. Sweeps mu on a 401-point grid in [0, 1] and sigma on a
300-point log grid in [0.005, 1], for both growth families.

Usage: python eca_reach.py
"""

import numpy as np

from alm.lenia import growth


def reached():
    found = {}
    for g in ("poly", "exp"):
        for mu in np.linspace(0, 1, 401):
            for sigma in np.geomspace(0.005, 1, 300):
                rule, ok = 0, True
                for idx in range(8):
                    l, c, r = (idx >> 2) & 1, (idx >> 1) & 1, idx & 1
                    a = float(np.clip(c + growth(g, np.array((l + r) / 2), mu, sigma), 0, 1))
                    if min(a, 1 - a) > 1e-3:
                        ok = False
                        break
                    rule |= int(round(a)) << idx
                if ok:
                    found.setdefault(rule, (g, round(float(mu), 4), round(float(sigma), 4)))
    return found


if __name__ == "__main__":
    f = reached()
    print("rules reached:", sorted(f))
    for k in sorted(f):
        print(f"  rule {k:3d}: first found with growth={f[k][0]}, mu={f[k][1]}, sigma={f[k][2]}")
