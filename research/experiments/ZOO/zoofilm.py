"""Film one collision of the atlas (deterministic rerun).

    PYTHONPATH=src:research/experiments/ZOO .venv/bin/python research/experiments/ZOO/zoofilm.py \
        O O2u O2u 75 0.75 --tu 120 --out /tmp/x.mp4 [--crop 256] [--every 0.5]

Prints the mass series, writes an mp4 (and a final png next to it).
"""

from __future__ import annotations

import argparse
import math

import imageio.v2 as imageio
import numpy as np
import matplotlib

from atlas import WORLDS, body
from zoocore import classify, components, place_pair, run_collision, sha

CMAP = matplotlib.colormaps["inferno"]


def rgb(A, gamma=0.8):
    x = np.clip(A, 0, 1) ** gamma
    return (CMAP(x)[..., :3] * 255).astype(np.uint8)


def write_mp4(ims, out, fps=30, scale=1):
    import shutil, subprocess
    h, w = ims[0].shape[:2]
    h, w = h * scale, w * scale
    p = subprocess.Popen([shutil.which("ffmpeg"), "-y", "-loglevel", "error", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                          "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264",
                          "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    for im in ims:
        if scale > 1:
            im = im.repeat(scale, 0).repeat(scale, 1)
        p.stdin.write(np.ascontiguousarray(im).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg failed")


def setup(world, a, b, theta, b_R):
    W = WORLDS[world]
    A = body(world, a, 0.0)
    hA = A.heading if A.heading is not None else 0.0
    B = body(world, b, hA + theta)
    A0, info = place_pair(A, B, b_R, W["rule"].R, W["N"])
    return W, A, B, A0, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("world")
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("theta", type=float)
    ap.add_argument("b_R", type=float)
    ap.add_argument("--tu", type=float, default=100)
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--scale", type=int, default=2)
    a = ap.parse_args()
    W, A, B, A0, info = setup(a.world, a.a, a.b, a.theta, a.b_R)
    frames, times, film = run_collision(W["rule"], A0, a.tu, every_tu=5.0, film_every_tu=a.every)
    ms = [round(float(F.sum()) / (A.mass + B.mass), 3) for F in frames]
    print("tc", info["tc"], "mass/initial every 5 tu:", ms)
    print("final components", [round(c["mass"]) for c in components(frames[-1], floor=0.15 * min(A.mass, B.mass))][:20])
    print("final sha256", sha(frames[-1]))
    write_mp4([rgb(F) for F in film], a.out, a.fps, a.scale)
    imageio.imwrite(a.out.rsplit(".", 1)[0] + "-final.png", rgb(film[-1]))


if __name__ == "__main__":
    main()
