"""Drawing a Klein-bottle world: the chart (fundamental domain with its gluing marks) and the
classic glass bottle in 3-D.

Gallery rules: A in [0, 1] mapped linearly onto ``inferno``; every pixel shows the value of its
nearest cell (no interpolation). The 3-D bottle adds Lambert shading (0.35 + 0.65 |cos|) and draws
the surface as tinted glass, compositing the four nearest layers, so the part of the bottle
behind the neck shows through; the glass is drawn transparent, more opaque where it is seen edge-on; both are disclosed in each caption.

The bottle is the standard immersion (u in [0, pi], v in [0, 2 pi)), with
(u = pi, v) ~ (u = 0, pi - v). Chart cell (y, x) of an Nx x Ny bottle sits at
u = arc_u((y + 0.5) / Ny) (rows evenly spaced along the bottle), v = 2 pi x / Nx + pi / 2, which matches klein.Klein's gluing
(x, y + Ny) ~ (-x, y). Areas are distorted (the neck is thin): a picture, not a measurement.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GEOM"))
from geomrender import BG, colour, label, save_png, write_mp4  # noqa: E402,F401
from PIL import Image, ImageDraw  # noqa: E402


def bottle(u, v):
    cu, su, cv, sv = np.cos(u), np.sin(u), np.cos(v), np.sin(v)
    x = -2 / 15 * cu * (3 * cv - 30 * su + 90 * cu**4 * su - 60 * cu**6 * su + 5 * cu * cv * su)
    y = -1 / 15 * su * (3 * cv - 3 * cu**2 * cv - 48 * cu**4 * cv + 48 * cu**6 * cv - 60 * su
                        + 5 * cu * cv * su - 5 * cu**3 * cv * su - 80 * cu**5 * cv * su + 80 * cu**7 * cv * su)
    z = 2 / 15 * (3 + 5 * cu * su) * sv
    return np.stack([x, y, z], -1)


def arc_u(f, n=4000):
    """u at fraction f of the bottle's mean length along u, so chart rows are evenly spaced along
    the bottle (the circumference still varies: the neck is thin)."""
    u = np.linspace(0, np.pi, n)
    v = np.linspace(0, 2 * np.pi, 64, endpoint=False)
    P = bottle(u[:, None], v[None, :])
    seg = np.linalg.norm(np.diff(P, axis=0), axis=-1).mean(1)
    s = np.r_[0, np.cumsum(seg)]
    return np.interp(f, s / s[-1], u)


class Bottle:
    """Renders an (Ny, Nx) chart state onto the bottle. ``oversample`` surface samples per cell side."""

    def __init__(self, ny, nx, size=520, oversample=8, layers=4, alpha=0.5):
        self.ny, self.nx, self.size, self.layers, self.alpha = ny, nx, size, layers, alpha
        nu, nv = ny * oversample, nx * oversample
        uu = arc_u((np.arange(nu) + 0.5) / nu)
        vv = 2 * np.pi * (np.arange(nv) + 0.5) / nv
        U, V = np.meshgrid(uu, vv, indexing="ij")
        P = bottle(U, V + np.pi / 2)
        e = 1e-4
        Pu = (bottle(U + e, V + np.pi / 2) - bottle(U - e, V + np.pi / 2)) / (2 * e)
        Pv = (bottle(U, V + e + np.pi / 2) - bottle(U, V - e + np.pi / 2)) / (2 * e)
        N = np.cross(Pu, Pv)
        N /= np.linalg.norm(N, axis=-1, keepdims=True) + 1e-12
        self.P = P.reshape(-1, 3)
        self.P -= (self.P.max(0) + self.P.min(0)) / 2
        self.N = N.reshape(-1, 3)
        # nearest chart cell of each surface sample
        iy = (np.arange(nu) * ny // nu)
        ix = (np.arange(nv) * nx // nv)
        self.cell = (iy[:, None] * nx + ix[None, :]).ravel()
        self.scale = 0.92 * size / (2 * np.linalg.norm(self.P, axis=1).max())

    def frame(self, A, az_deg, el_deg=18):
        az, el = np.radians(az_deg), np.radians(el_deg)
        # camera: rotate about the bottle's long axis (x of the immersion is along its length? use z up)
        Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
        Rx = np.array([[1, 0, 0], [0, np.cos(el), -np.sin(el)], [0, np.sin(el), np.cos(el)]])
        M = Rx @ Rz
        # put the bottle upright: immersion y axis (its length) -> screen up
        Q = self.P[:, [0, 2, 1]] * np.array([1, 1, -1])
        Nq = self.N[:, [0, 2, 1]] * np.array([1, 1, -1])
        Q = Q @ M.T
        Nq = Nq @ M.T
        s = self.size
        px = np.clip((Q[:, 0] * self.scale + s / 2).astype(int), 0, s - 1)
        py = np.clip((-Q[:, 2] * self.scale + s / 2).astype(int), 0, s - 1)
        depth = Q[:, 1]  # larger = farther
        light = np.array([-0.4, -0.7, 0.6])
        light /= np.linalg.norm(light)
        shade = 0.35 + 0.65 * np.abs(Nq @ light)
        a = np.clip(A.ravel()[self.cell], 0, 1)
        glass = np.array([95, 130, 185.0])
        col = (colour(a) * (a[:, None] > 0.02) + glass * (a[:, None] <= 0.02)) * shade[:, None]
        facing = np.abs(Nq[:, 1])  # 1 = facing the camera, 0 = seen edge-on
        alpha = np.where(a > 0.02, 0.95, self.alpha * (0.35 + 0.9 * (1 - facing) ** 2))
        col = col + (a[:, None] <= 0.02) * 90 * (1 - facing[:, None]) ** 3
        pix = py * s + px
        order = np.lexsort((depth, pix))
        pix_o = pix[order]
        first = np.r_[True, pix_o[1:] != pix_o[:-1]]
        # keep one sample per (pixel, layer): break layers where depth jumps
        d_o = depth[order]
        gap = np.r_[True, (np.diff(d_o) > 0.06) | (pix_o[1:] != pix_o[:-1])]
        keep = gap
        idx = order[keep]
        pk = pix[idx]
        grp_start = np.r_[True, pk[1:] != pk[:-1]]
        starts = np.flatnonzero(grp_start)
        rank = np.arange(len(pk)) - np.repeat(starts, np.diff(np.r_[starts, len(pk)]))
        img = np.tile(BG.astype(float), (s * s, 1))
        trans = np.ones(s * s)
        out = np.zeros((s * s, 3))
        for r in range(self.layers):
            m = rank == r
            p, i = pk[m], idx[m]
            out[p] += trans[p, None] * alpha[i, None] * col[i]
            trans[p] *= 1 - alpha[i]
        img = out + trans[:, None] * img
        return np.clip(img, 0, 255).astype(np.uint8).reshape(s, s, 3)


class Chart:
    """The fundamental domain, nearest cell per pixel, with the gluing marks: single arrows on the
    left and right edges (glued straight), double arrows pointing opposite ways on the top and
    bottom edges (glued with a flip)."""

    def __init__(self, ny, nx, scale=4, pad=26, klein=True):
        self.ny, self.nx, self.sc, self.pad, self.klein = ny, nx, scale, pad, klein

    def frame(self, A):
        sc, pad = self.sc, self.pad
        h, w = self.ny * sc, self.nx * sc
        img = np.empty((h + 2 * pad, w + 2 * pad, 3), np.uint8)
        img[:] = BG
        c = colour(A).astype(np.uint8)
        img[pad:pad + h, pad:pad + w] = np.repeat(np.repeat(c, sc, 0), sc, 1)
        im = Image.fromarray(img)
        d = ImageDraw.Draw(im)
        edge = (150, 200, 255)
        flip = (255, 150, 120)
        d.rectangle([pad - 1, pad - 1, pad + w, pad + h], outline=(90, 90, 110))

        def arrow(x0, y0, x1, y1, col, n=1):
            d.line([x0, y0, x1, y1], fill=col, width=3)
            vx, vy = x1 - x0, y1 - y0
            L = np.hypot(vx, vy)
            ux, uy = vx / L, vy / L
            for k in range(n):
                tx, ty = x1 - ux * 12 * k, y1 - uy * 12 * k
                d.polygon([(tx, ty), (tx - 11 * ux + 6 * uy, ty - 11 * uy - 6 * ux),
                           (tx - 11 * ux - 6 * uy, ty - 11 * uy + 6 * ux)], fill=col)
        m = pad // 2
        # left / right: same direction (glued straight)
        arrow(m, pad + h * 0.7, m, pad + h * 0.3, edge)
        arrow(pad + w + m, pad + h * 0.7, pad + w + m, pad + h * 0.3, edge)
        # top / bottom: opposite directions if Klein
        arrow(pad + w * 0.3, m, pad + w * 0.7, m, flip, 2)
        if self.klein:
            arrow(pad + w * 0.7, pad + h + m, pad + w * 0.3, pad + h + m, flip, 2)
        else:
            arrow(pad + w * 0.3, pad + h + m, pad + w * 0.7, pad + h + m, flip, 2)
        return np.asarray(im)
