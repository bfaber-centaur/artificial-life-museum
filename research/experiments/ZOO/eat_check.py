"""Does a Pteryx that swallows a Circium become the next Pteryx up? Follow the product."""
import sys, json, math
import numpy as np
from atlas import WORLDS, body, base_body
from zoocore import place_pair, components, crop, centroid, torus_delta, sha
from alm.lenia import Lenia
from zoofilm import rgb
from PIL import Image
a, b_R, tu = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
W = WORLDS["P"]; R = 13
A = body("P", a, 0.0); B = body("P", "C0v", A.heading + 180)
A0, info = place_pair(A, B, b_R, R, W["N"])
L = Lenia(W["rule"], A0)
snaps = []
for s in range(1, int(tu * 10) + 1):
    L.step()
    if s % 100 == 0:
        cs = components(L.A, floor=30)
        snaps.append((s / 10, [round(c["mass"]) for c in cs]))
print(snaps)
cs = components(L.A, floor=30)
c = cs[0]["c"]
m0 = float(L.A.sum()); c0 = centroid(L.A)
for _ in range(100): L.step()
d = torus_delta(c0, centroid(L.A), L.A.shape)
print("product mass", round(float(L.A.sum())), "speed", round(math.hypot(*d) / 10, 3), "c/tu")
P = crop(L.A, components(L.A, floor=30)[0]["c"], 70)
Image.fromarray(rgb(P)).resize((280, 280), Image.NEAREST).save(f"/tmp/claude-0/zoo/eat-{a}-{b_R}.png")
