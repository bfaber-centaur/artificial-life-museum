"""Film a 3-D catalogue creature: rotating depth-shaded render, bodies coloured by component.

usage: film3d.py STEM IDX N TU OUTDIR NAME [DTFAC]
Each video frame (every 1 time unit): the volume (periodic) is rotated about the vertical axis
by 0.6 degrees per time unit, the first voxel above ISO along the view ray gives a depth map,
shaded with a Lambert light from its gradient; each 3-D body (26-connected component of the
field blurred by 1.5 voxels above 0.08, on the torus) gets its own hue. Also writes NAME.json with the body count and mass every 5 tu.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

from common import found_entry, nd, state_hash, torus_label

ISO = 0.25
stem, idx, N, TU, out, name = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), Path(sys.argv[5]), sys.argv[6]
dtfac = int(sys.argv[7]) if len(sys.argv) > 7 else 1
out.mkdir(parents=True, exist_ok=True)
e = found_entry(stem, idx)
params, A = nd.entry_state(e, 3, N)
for p in params:
    p["T"] = p.get("T", 10) * dtfac
w = nd.NDLenia(params, A)
h0 = state_hash(w.A)
SC = 4  # output pixels per voxel


def render(V, ang):
    lab, n = torus_label(ndimage.gaussian_filter(V, 1.5, mode="wrap") > 0.08)
    # rotate about axis 1 (vertical in the image), view along axis 0
    R = ndimage.rotate(V, ang, axes=(0, 2), reshape=False, order=1, mode="grid-wrap")
    L = ndimage.rotate(lab, ang, axes=(0, 2), reshape=False, order=0, mode="grid-wrap")
    # crop to a central cylinder so the wrapped corners do not show
    hit = R > ISO
    any_hit = hit.any(0)
    z = np.where(any_hit, hit.argmax(0), N).astype(float)
    ids = np.take_along_axis(L, np.minimum(z, N - 1).astype(int)[None], 0)[0]
    ids = np.where(ids > 0, ids, ndimage.maximum_filter(ids, size=5))
    zs = ndimage.gaussian_filter(z, 0.8)
    gy, gx = np.gradient(zs)
    nrm = np.stack([-gx, -gy, np.ones_like(zs) * 1.5]); nrm /= np.linalg.norm(nrm, axis=0)
    light = np.array([0.45, -0.55, 0.7]); light /= np.linalg.norm(light)
    lam = np.clip((nrm * light[:, None, None]).sum(0), 0, 1)
    fog = 1 - 0.55 * z / N
    hue = (0.58 + ids * 0.61803398875) % 1.0
    i6 = np.floor(hue * 6).astype(int) % 6; f = hue * 6 - np.floor(hue * 6)
    val = (0.15 + 0.85 * lam ** 1.3) * fog; s = 0.65
    p_, q, t = val * (1 - s), val * (1 - s * f), val * (1 - s * (1 - f))
    rgb = np.stack([np.choose(i6, [val, q, p_, p_, t, val]), np.choose(i6, [t, val, val, q, p_, p_]),
                    np.choose(i6, [p_, p_, t, val, val, q])], -1)
    yy, xx = np.mgrid[:N, :N]
    bg = 0.04 + 0.03 * (1 - yy / N)
    rgb = np.where(any_hit[..., None], rgb, bg[..., None] * np.array([0.8, 0.9, 1.2]))
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    return np.kron(img, np.ones((SC, SC, 1), dtype=np.uint8)), n


ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{N * SC}x{N * SC}", "-r", "30", "-i", "-", "-c:v", "libx264",
                       "-pix_fmt", "yuv420p", "-crf", "18", str(out / f"{name}.mp4")], stdin=subprocess.PIPE)
every = int(round(1 / w.dt)); steps = int(round(TU / w.dt))
trace = []; t0 = time.time(); stills = {}
for s in range(steps + 1):
    if s % every == 0:
        t = s * w.dt
        img, n = render(w.A[0], 0.6 * t)
        ff.stdin.write(img.tobytes())
        if s % (5 * every) == 0:
            trace.append((round(t, 2), n, round(float(w.A.sum()), 1)))
        for mark in (0, TU / 3, 2 * TU / 3, TU):
            if abs(t - mark) < w.dt / 2 or (mark not in stills and t >= mark):
                stills.setdefault(mark, img)
    if s < steps:
        w.step()
ff.stdin.close(); ff.wait()
import matplotlib.pyplot as plt  # noqa: E402
strip = np.concatenate([stills[k] for k in sorted(stills)], 1)
plt.imsave(out / f"{name}-strip.png", strip)
rec = dict(stem=stem, idx=idx, name=e.get("name"), N=N, tu=TU, dt=w.dt, iso=ISO, initial_sha=h0,
           final_sha=state_hash(w.A), trace=trace)
(out / f"{name}.json").write_text(json.dumps(rec))
print(name, "bodies", [x[1] for x in trace[::max(1, len(trace) // 15)]], "mass", trace[-1][2], f"{time.time() - t0:.0f}s")
