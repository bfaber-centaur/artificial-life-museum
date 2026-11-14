"""Rendering for GEOM point-cloud worlds.

Gallery rules (research/gallery/README.md): A in [0, 1] mapped linearly onto ``inferno``; each
pixel shows the value of its *nearest* cell (no smoothing or interpolation), so the cell mosaic of
each world is visible when zoomed in. The globe adds a Lambert shading factor (0.5 + 0.5 cos)
so the sphere reads as a sphere; that is disclosed in each caption. Background #0b0b0f.
"""

from __future__ import annotations

import subprocess

import numpy as np
from matplotlib import colormaps
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree

BG = np.array([11, 11, 15], dtype=np.uint8)
CMAP = colormaps["inferno"]


def colour(v):
    return (CMAP(np.clip(v, 0, 1))[..., :3] * 255).astype(np.float64)


class Globe:
    """Orthographic view of a sphere world from direction `eye` (unit 3-vector)."""

    def __init__(self, world, size=520, margin=10):
        self.u = world.xy / np.linalg.norm(world.xy, axis=1, keepdims=True)
        self.tree = cKDTree(self.u)
        self.size, self.margin = size, margin
        r = (size - 2 * margin) / 2
        yy, xx = np.mgrid[0:size, 0:size]
        X = (xx - size / 2 + 0.5) / r
        Y = -(yy - size / 2 + 0.5) / r
        self.inside = X**2 + Y**2 < 1
        self.X, self.Y = X[self.inside], Y[self.inside]
        self.Z = np.sqrt(1 - self.X**2 - self.Y**2)
        self.light = np.array([-0.45, 0.55, 0.70])
        self.light /= np.linalg.norm(self.light)

    def frame(self, A, eye, up=(0, 0, 1)):
        f = np.asarray(eye, float)
        f /= np.linalg.norm(f)
        up = np.asarray(up, float)
        r = np.cross(up, f)
        if np.linalg.norm(r) < 1e-6:
            r = np.cross([0, 1, 0], f)
        r /= np.linalg.norm(r)
        u = np.cross(f, r)
        P = self.X[:, None] * r + self.Y[:, None] * u + self.Z[:, None] * f
        _, idx = self.tree.query(P)
        shade = 0.5 + 0.5 * np.clip(np.stack([self.X, self.Y, self.Z], 1) @ self.light, 0, 1)
        img = np.empty((self.size, self.size, 3), dtype=np.uint8)
        img[:] = BG
        c = colour(A[idx]) * shade[:, None]
        # faint ocean so the empty sphere is visible: inferno(0) is near-black, lift it a little
        c += (1 - np.clip(A[idx], 0, 1))[:, None] * np.array([14, 16, 30]) * shade[:, None]
        img[self.inside] = np.clip(c, 0, 255).astype(np.uint8)
        return img


class Flat:
    """Top-down raster of a torus world, nearest cell per pixel."""

    def __init__(self, world, scale=3.0, window=None):
        Lx, Ly = world.box
        x0, y0, w, h = window if window else (0, 0, Lx, Ly)
        self.W, self.H = int(round(w * scale)), int(round(h * scale))
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        px = np.mod(x0 + (xx + 0.5) / scale, Lx)
        py = np.mod(y0 + (self.H - 1 - yy + 0.5) / scale, Ly)  # y up
        tree = cKDTree(world.xy, boxsize=world.box)
        _, self.idx = tree.query(np.stack([px.ravel(), py.ravel()], 1))

    def frame(self, A):
        return colour(A[self.idx]).reshape(self.H, self.W, 3).astype(np.uint8)


class Disk:
    """Poincare-disk view of a hyperbolic world."""

    def __init__(self, world, size=620, margin=8):
        z = world.xy
        self.tree = cKDTree(z)
        self.size = size
        r = (size - 2 * margin) / 2
        yy, xx = np.mgrid[0:size, 0:size]
        X = (xx - size / 2 + 0.5) / r
        Y = -(yy - size / 2 + 0.5) / r
        smax = np.hypot(z[:, 0], z[:, 1]).max()
        self.inside = X**2 + Y**2 < smax**2
        self.rim = (X**2 + Y**2 >= smax**2) & (X**2 + Y**2 < 1)
        _, self.idx = self.tree.query(np.stack([X[self.inside], Y[self.inside]], 1))

    def frame(self, A):
        img = np.empty((self.size, self.size, 3), dtype=np.uint8)
        img[:] = BG
        img[self.rim] = (24, 24, 34)
        c = colour(A[self.idx]) + (1 - np.clip(A[self.idx], 0, 1))[:, None] * np.array([10, 12, 24])
        img[self.inside] = np.clip(c, 0, 255).astype(np.uint8)
        return img


def font(size=16):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def label(img, text, xy=(10, 8), size=16, fill=(235, 235, 235)):
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    d.text(xy, text, font=font(size), fill=fill)
    return np.asarray(im)


def write_mp4(frames, path, fps=30):
    h, w, _ = frames[0].shape
    h2, w2 = h + h % 2, w + w % 2
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{w2}x{h2}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
                          "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "slow",
                          "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)
    for f in frames:
        if f.shape[:2] != (h2, w2):
            g = np.empty((h2, w2, 3), np.uint8)
            g[:] = BG
            g[:h, :w] = f
            f = g
        p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg failed")


def save_png(img, path):
    Image.fromarray(img).save(path, optimize=True)
