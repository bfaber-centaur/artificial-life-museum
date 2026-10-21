"""Torus re-encounter margin of the pilot geometry under a post-contact turn (§6.6).

Model: the undisturbed G-alone centroid track, turned once by phi at the geometric contact time
t_c, speed unchanged. For phi over [-180°, 180°) in 0.5° steps, find when the track first comes
within D_int of a ring image other than the primary one, before H. Reports the earliest such
time over all phi (and its phi), and the smallest |phi| that causes any hit before H.
Not modelled: speed changes, several turns, fragments, return to the primary ring after
separation. The scorer must recompute t_cen on the measured encounter track.
Usage: python research/experiments/REEF-field/torus_margin.py [N]   (default 256)
"""
import json
import sys

import numpy as np

from reefcore import HERE

N = int(sys.argv[1]) if len(sys.argv) > 1 else 256
c = json.loads((HERE / "controls.json").read_text())
R, H = 13, c["H_tu"]
t = np.arange(0, H + 1e-9, 0.1)
images = [np.array([ky, kx]) * N / R for ky in range(-4, 5) for kx in range(-4, 5) if (ky, kx) != (0, 0)]
out = []
for p in c["geometry"]["pilots"]:
    v = c[p["snapshot"]]["motion_fit"]["speed_R_per_tu"]
    h0 = np.radians(p["heading_deg"])
    g0 = np.array(p["glider_centroid_yx"]) / R
    s = np.array(p["ring_centroid_yx"]) / R
    tc = p["t_c_geometric_tu"]
    pre = g0 + v * np.minimum(t, tc)[:, None] * np.array([np.sin(h0), np.cos(h0)])
    hits = {}
    for phi in np.arange(-180, 180, 0.5):
        a = h0 + np.radians(phi)
        g = pre + v * np.maximum(t - tc, 0)[:, None] * np.array([np.sin(a), np.cos(a)])
        first = min((t[i[0]] for im in images
                     for i in [np.nonzero(np.hypot(*(s + im - g).T) < p["D_int_R"])[0]] if len(i)), default=None)
        if first is not None:
            hits[float(phi)] = float(first)
    earliest = min(hits.items(), key=lambda kv: kv[1]) if hits else None
    smallest = min(hits, key=abs) if hits else None
    res = {"pilot": p["pilot"], "N": N, "t_c_geometric_tu": tc, "t_c_plus_20": tc + 20,
           "earliest_image_hit": None if earliest is None else {"phi_deg": earliest[0], "t_tu": earliest[1]},
           "smallest_turn_with_hit": None if smallest is None else {"phi_deg": smallest, "t_tu": hits[smallest]},
           "window_safe_for_any_single_turn": earliest is None or earliest[1] >= tc + 20}
    out.append(res)
    print(json.dumps(res))
(HERE / f"torus-margin-N{N}.json").write_text(json.dumps(out, indent=1) + "\n")
