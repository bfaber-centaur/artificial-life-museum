"""Classic Lenia on arbitrary point clouds ("graph Lenia") for the GEOM thread.

The world is a set of points (cells) with a metric. The kernel becomes a sparse matrix:

    W[i, j] = K_C(d(i, j) / R) * shell(d(i, j) / R),   row-normalised so sum_j W[i, j] = 1
    U = W @ A
    A <- clip(A + G(U) / T, 0, 1)

On the square torus with unit spacing this is exactly ``alm.lenia.Lenia`` (same kernel values,
same normalisation, same Euler step; ``tests/test_geom.py`` checks agreement to 1e-12). On any
other point set it is the natural discretisation of the same continuum rule: the kernel is the
same function of true distance, and row normalisation absorbs local density.

Worlds (all at about one cell per unit area, so R = 13 means the same physical radius):
  square_torus(N)        unit square lattice, periodic (validation)
  hex_torus(L)           triangular ("hex") lattice, spacing sqrt(2/sqrt3) so one cell per unit area
  glass_torus(L, seed)   amorphous packing: random points relaxed by soft repulsion (no lattice)
  sphere(rho, seed)      relaxed points on a sphere of radius rho cells, geodesic distance
  hyperbolic(kappa, rmax, seed)  relaxed points on a hyperbolic disk (curvature radius kappa
                         cells, geodesic radius rmax cells), stored in Poincare-disk coordinates

Everything here is deterministic given its arguments (seeded numpy Generator, no threads in the
relaxation).
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402
import scipy.sparse as sp  # noqa: E402
from scipy.ndimage import map_coordinates  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from alm.lenia import Rule, growth, kernel_core  # noqa: E402

# ---------------------------------------------------------------------------------------------
# worlds


@dataclass
class World:
    kind: str
    xy: np.ndarray  # (n, d) coordinates: torus (x, y); sphere (x, y, z); hyperbolic Poincare (x, y)
    params: dict
    box: tuple | None = None  # torus box size (Lx, Ly)
    area: np.ndarray | None = None  # quadrature weight (cell area) per point; None = all 1

    @property
    def n(self) -> int:
        return len(self.xy)

    def sha256(self) -> str:
        return hashlib.sha256(np.ascontiguousarray(self.xy, dtype="<f8").tobytes()).hexdigest()

    # pairs within geodesic distance r: returns (i, j, d) with i != j
    def pairs(self, r: float):
        if self.kind == "torus":
            t = cKDTree(self.xy, boxsize=self.box)
            m = t.sparse_distance_matrix(t, r, output_type="coo_matrix")
            i, j, d = m.row, m.col, m.data
        elif self.kind == "sphere":
            rho = self.params["rho"]
            u = self.xy / rho
            t = cKDTree(u)
            chord = 2 * np.sin(min(r / rho, np.pi) / 2)
            m = t.sparse_distance_matrix(t, chord + 1e-12, output_type="coo_matrix")
            i, j = m.row, m.col
            dots = np.clip((u[i] * u[j]).sum(1), -1, 1)
            d = rho * np.arccos(dots)
        elif self.kind == "hyperbolic":
            kap = self.params["kappa"]
            z = self.xy
            s = np.hypot(z[:, 0], z[:, 1])
            tt = np.tanh(r / kap / 2)
            lo = (s - tt) / (1 - s * tt)
            hi = (s + tt) / (1 + s * tt)
            # Euclidean disk containing the hyperbolic ball: its diameter lies on the ray through z
            uhat = np.where(s[:, None] > 0, z / np.maximum(s, 1e-300)[:, None], [1.0, 0.0])
            cen = uhat * ((lo + hi) / 2)[:, None]
            rad = (hi - lo) / 2 + 1e-12
            t = cKDTree(z)
            I, Jl, Dl = [], [], []
            for c0 in range(0, len(z), 4000):  # chunked: Python index lists are memory-hungry
                lists = t.query_ball_point(cen[c0:c0 + 4000], rad[c0:c0 + 4000])
                ii = np.repeat(np.arange(c0, c0 + len(lists)), [len(a) for a in lists])
                jj = np.concatenate([np.asarray(a, dtype=np.int64) for a in lists])
                del lists
                dd = hyp_dist(z[ii], z[jj], kap)
                k = (ii != jj) & (dd < r)
                I.append(ii[k].astype(np.int32))
                Jl.append(jj[k].astype(np.int32))
                Dl.append(dd[k])
            i, j, d = np.concatenate(I), np.concatenate(Jl), np.concatenate(Dl)
        else:
            raise ValueError(self.kind)
        keep = (i != j) & (d < r)
        return i[keep], j[keep], d[keep]


def square_torus(N: int) -> World:
    yy, xx = np.mgrid[0:N, 0:N]
    xy = np.stack([xx.ravel(), yy.ravel()], 1).astype(np.float64)
    return World("torus", xy, {"lattice": "square", "N": N}, box=(float(N), float(N)))


def hex_torus(L: float) -> World:
    s = np.sqrt(2 / np.sqrt(3))  # spacing: one point per unit area
    nx = int(round(L / s))
    ny = int(round(L / (s * np.sqrt(3) / 2)))
    ny += ny % 2  # even row count keeps the offset rows periodic
    jj, ii = np.mgrid[0:ny, 0:nx]
    x = (ii + 0.5 * (jj % 2)) * s
    y = jj * s * np.sqrt(3) / 2
    xy = np.stack([x.ravel(), y.ravel()], 1)
    return World("torus", xy, {"lattice": "hex", "L": L, "nx": nx, "ny": ny, "spacing": s},
                 box=(nx * s, ny * s * np.sqrt(3) / 2))


def _relax(xy, step_fn, n_iter):
    for _ in range(n_iter):
        xy = step_fn(xy)
    return xy


def glass_torus(L: int, seed: int = 0, n_iter: int = 120) -> World:
    """Amorphous point set on an L x L torus, density 1 (n = L*L)."""
    rng = np.random.default_rng([7, seed])
    n = L * L
    xy = rng.random((n, 2)) * L
    r0 = 1.07  # near the random-close-packing spacing at unit density

    def step(xy):
        t = cKDTree(xy, boxsize=(L, L))
        pr = t.query_pairs(r0, output_type="ndarray")
        dv = xy[pr[:, 0]] - xy[pr[:, 1]]
        dv -= L * np.round(dv / L)
        d = np.hypot(dv[:, 0], dv[:, 1])[:, None]
        push = 0.25 * (r0 - d) * dv / np.maximum(d, 1e-9)
        disp = np.zeros_like(xy)
        np.add.at(disp, pr[:, 0], push)
        np.add.at(disp, pr[:, 1], -push)
        return np.mod(xy + disp, L)

    xy = _relax(xy, step, n_iter)
    return World("torus", xy, {"lattice": "glass", "L": L, "seed": seed, "n_iter": n_iter},
                 box=(float(L), float(L)))


def sphere(rho: float, seed: int = 0, n_iter: int = 120) -> World:
    """Relaxed points on a sphere of radius rho (cells); n = round(4 pi rho^2)."""
    rng = np.random.default_rng([11, seed])
    n = int(round(4 * np.pi * rho**2))
    u = rng.normal(size=(n, 3))
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    r0 = 1.07 / rho

    def step(u):
        t = cKDTree(u)
        pr = t.query_pairs(r0, output_type="ndarray")
        dv = u[pr[:, 0]] - u[pr[:, 1]]
        d = np.linalg.norm(dv, axis=1, keepdims=True)
        push = 0.25 * (r0 - d) * dv / np.maximum(d, 1e-12)
        disp = np.zeros_like(u)
        np.add.at(disp, pr[:, 0], push)
        np.add.at(disp, pr[:, 1], -push)
        u = u + disp
        return u / np.linalg.norm(u, axis=1, keepdims=True)

    u = _relax(u, step, n_iter)
    return World("sphere", u * rho, {"rho": rho, "seed": seed, "n_iter": n_iter, "n": n})


def icosphere(rho: float) -> World:
    """Geodesic (icosahedral) grid on a sphere of radius rho cells: locally a hex lattice with 12
    five-fold defects. Frequency nu is chosen so the mean cell area is 1; each point carries its
    spherical-Voronoi area as quadrature weight."""
    from scipy.spatial import SphericalVoronoi

    nu = max(1, int(round(np.sqrt((4 * np.pi * rho**2 - 2) / 10))))
    t = (1 + 5**0.5) / 2
    V = np.array([[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t],
                  [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]], float)
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4),
         (11, 10, 2), (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8),
         (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    pts = []
    for a, b, c in F:
        for i in range(nu + 1):
            for j in range(nu + 1 - i):
                k = nu - i - j
                pts.append((i * V[a] + j * V[b] + k * V[c]) / nu)
    P = np.array(pts)
    P /= np.linalg.norm(P, axis=1, keepdims=True)
    _, keep = np.unique(np.round(P, 9), axis=0, return_index=True)
    P = P[np.sort(keep)]
    sv = SphericalVoronoi(P, radius=1.0)
    area = sv.calculate_areas() * rho**2
    return World("sphere", P * rho, {"rho": rho, "grid": "icosahedral", "nu": nu, "n": len(P)},
                 area=area)


def hyp_dist(z1, z2, kappa):
    num = 2 * ((z1 - z2) ** 2).sum(-1)
    den = (1 - (z1**2).sum(-1)) * (1 - (z2**2).sum(-1))
    return kappa * np.arccosh(1 + num / np.maximum(den, 1e-300))


def _mink(a, b):
    return -a[..., 0] * b[..., 0] + a[..., 1] * b[..., 1] + a[..., 2] * b[..., 2]


def hyper_grid(kappa: float, rmax: float) -> World:
    """Geodesic grid on the hyperbolic plane: the {3,7} triangle tiling (seven triangles at every
    vertex) out to geodesic radius rmax, each triangle subdivided with frequency nu like the
    icosphere, so the grid is locally a hex lattice with seven-fold defects. Curvature radius kappa
    and rmax are in cells; nu is chosen for about one cell per unit area. Each point carries its
    area (one third of each incident sub-triangle, exact hyperbolic triangle areas)."""
    J = np.array([-1.0, 1.0, 1.0])
    al = 2 * np.pi / 7  # {3,7}: equilateral triangles with angle 2 pi / 7
    ell = np.arccosh((np.cos(al) + np.cos(al) ** 2) / np.sin(al) ** 2)  # edge length, kappa = 1
    tri_area = np.pi / 7
    nu = max(1, int(round(np.sqrt(2 * tri_area) * kappa)))
    a = rmax / kappa

    def vert(r, th):
        return np.array([np.cosh(r), np.sinh(r) * np.cos(th), np.sinh(r) * np.sin(th)])

    def reflect(v, p, q):
        n = J * np.cross(p, q)
        return v - 2 * _mink(v, n) / _mink(n, n) * n

    def hdist(p, q):
        return np.arccosh(np.maximum(-_mink(p, q), 1.0))

    def norm_h(x):
        return x / np.sqrt(-_mink(x, x))[..., None]

    verts, vkey = [], {}

    def vid(v):
        # snap to an existing vertex within 0.3 (hyperboloid x1, x2); distinct tiling vertices
        # are >= 2 sinh(ell / 2) = 1.2 apart there, so rounding error can never merge two
        v = norm_h(v)
        b = (int(np.floor(v[1] / 0.5)), int(np.floor(v[2] / 0.5)))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for i in vkey.get((b[0] + dx, b[1] + dy), ()):
                    if abs(verts[i][1] - v[1]) + abs(verts[i][2] - v[2]) < 0.3:
                        return i
        vkey.setdefault(b, []).append(len(verts))
        verts.append(v)
        return len(verts) - 1

    o = np.array([1.0, 0, 0])
    t0 = (vid(o), vid(vert(ell, 0.0)), vid(vert(ell, 2 * np.pi / 7)))
    seen = {frozenset(t0): t0}
    from collections import deque

    queue = deque([t0])  # breadth first: every vertex is reached by a shortest reflection chain
    while queue:
        t = queue.popleft()
        for k in range(3):
            p, q, v = (verts[t[(k + 1) % 3]], verts[t[(k + 2) % 3]], verts[t[k]])
            nv = vid(reflect(v, p, q))
            nt = (t[(k + 1) % 3], t[(k + 2) % 3], nv)
            kk = frozenset(nt)
            if kk in seen:
                continue
            if hdist(o, norm_h(p + q + verts[nv])) > a + ell:
                continue
            seen[kk] = nt
            queue.append(nt)
    tris = [tuple(verts[i] for i in t) for t in seen.values()]
    # sub-triangle lattice points
    pts, faces = [], []
    idx = {}

    def pid(x):
        x = norm_h(x)
        z = x[1:] / (1 + x[0])
        kk = (round(z[0], 7), round(z[1], 7))
        if kk not in idx:
            idx[kk] = len(pts)
            pts.append(x)
        return idx[kk]

    for A_, B_, C_ in tris:
        ids = {}
        for i in range(nu + 1):
            for j in range(nu + 1 - i):
                k = nu - i - j
                ids[i, j] = pid((i * A_ + j * B_ + k * C_) / nu)
        for i in range(nu):
            for j in range(nu - i):
                faces.append((ids[i, j], ids[i + 1, j], ids[i, j + 1]))
                if i + j < nu - 1:
                    faces.append((ids[i + 1, j], ids[i + 1, j + 1], ids[i, j + 1]))
    X = np.array(pts)
    F = np.array(faces)
    # exact hyperbolic triangle areas: pi - sum of angles (law of cosines)
    P0, P1, P2 = X[F[:, 0]], X[F[:, 1]], X[F[:, 2]]
    sa, sb, sc = hdist(P1, P2), hdist(P0, P2), hdist(P0, P1)

    def ang(opp, s1, s2):
        c = (np.cosh(s1) * np.cosh(s2) - np.cosh(opp)) / (np.sinh(s1) * np.sinh(s2))
        return np.arccos(np.clip(c, -1, 1))

    tA = np.pi - ang(sa, sb, sc) - ang(sb, sa, sc) - ang(sc, sa, sb)
    area = np.zeros(len(X))
    for k in range(3):
        np.add.at(area, F[:, k], tA / 3)
    r = hdist(o, X)
    keep = r <= a
    z = X[:, 1:] / (1 + X[:, :1])
    return World("hyperbolic", z[keep], {"kappa": kappa, "rmax": rmax, "grid": "{3,7} geodesic",
                                         "nu": nu, "n": int(keep.sum())},
                 area=area[keep] * kappa**2)


def hyperbolic(kappa: float, rmax: float, seed: int = 0, n_iter: int = 120) -> World:
    """Relaxed points of unit density on a hyperbolic disk of geodesic radius rmax (cells)."""
    rng = np.random.default_rng([13, seed])
    a = rmax / kappa
    area = 2 * np.pi * kappa**2 * (np.cosh(a) - 1)
    n = int(round(area))
    # uniform hyperbolic density: cosh(r) - 1 uniform
    rr = np.arccosh(1 + rng.random(n) * (np.cosh(a) - 1))
    th = rng.random(n) * 2 * np.pi
    s = np.tanh(rr / 2)
    z = np.stack([s * np.cos(th), s * np.sin(th)], 1)
    smax = np.tanh(a / 2)
    r0 = 1.07

    def step(z):
        w = World("hyperbolic", z, {"kappa": kappa})
        i, j, d = w.pairs(r0)
        keep = i < j
        i, j, d = i[keep], j[keep], d[keep]
        lam = 2 / (1 - (z**2).sum(1))  # conformal factor (kappa = 1 units)
        dv = z[i] - z[j]
        e = np.hypot(dv[:, 0], dv[:, 1])[:, None]
        mag = 0.25 * (r0 - d)[:, None] / kappa  # hyperbolic displacement, kappa units
        disp = np.zeros_like(z)
        np.add.at(disp, i, mag * dv / np.maximum(e, 1e-12) / lam[i, None])
        np.add.at(disp, j, -mag * dv / np.maximum(e, 1e-12) / lam[j, None])
        z = z + disp
        rad = np.hypot(z[:, 0], z[:, 1])
        over = rad > smax
        z[over] *= (smax / rad[over])[:, None]
        return z

    z = _relax(z, step, n_iter)
    return World("hyperbolic", z, {"kappa": kappa, "rmax": rmax, "seed": seed, "n_iter": n_iter,
                                   "n": n})


# ---------------------------------------------------------------------------------------------
# dynamics


def kernel_matrix(world: World, rule: Rule) -> sp.csr_matrix:
    i, j, d = world.pairs(rule.R)
    D = d / rule.R
    B = len(rule.beta)
    Br = B * D
    shell = np.asarray(rule.beta)[np.minimum(np.floor(Br).astype(int), B - 1)]
    w = kernel_core(rule.kernel, np.minimum(Br % 1, 1)) * shell
    if world.area is not None:
        w = w * world.area[j]
    W = sp.csr_matrix((w, (i, j)), shape=(world.n, world.n))
    W.sum_duplicates()
    rs = np.asarray(W.sum(1)).ravel()
    if world.kind == "hyperbolic" and "rmax" in world.params:
        kap = world.params["kappa"]
        r0 = hyp_dist(world.xy, np.zeros_like(world.xy), kap)
        edge = r0 > world.params["rmax"] - rule.R - 1
        rs = np.where(edge, np.median(rs[~edge]), rs)  # boundary = vacuum beyond, not renormalised
    W = sp.diags(1 / rs) @ W
    return W.tocsr()


@dataclass
class GraphLenia:
    world: World
    rule: Rule
    A: np.ndarray
    mu_field: np.ndarray | None = None  # optional per-cell mu (terrain)
    t: int = 0
    W: sp.csr_matrix = field(init=False, repr=False)

    def __post_init__(self):
        self.A = np.array(self.A, dtype=np.float64, copy=True)
        self.W = kernel_matrix(self.world, self.rule)

    def step(self):
        r = self.rule
        mu = r.mu if self.mu_field is None else self.mu_field
        U = self.W @ self.A
        self.A = np.clip(self.A + growth(r.growth, U, mu, r.sigma) * r.dt, 0.0, 1.0)
        self.t += 1


# ---------------------------------------------------------------------------------------------
# seeding and measurement


def patch_sampler(cells: np.ndarray, pad: int = 6):
    """Cubic interpolant of a cell patch (values 0..1), zero outside. Returns f(x, y) with (x, y)
    measured from the patch centre in cells (x = column, y = row)."""
    c = np.pad(np.asarray(cells, dtype=np.float64), pad)
    h, w = c.shape
    cy, cx = (h - 1) / 2, (w - 1) / 2

    def f(x, y):
        v = map_coordinates(c, [y + cy, x + cx], order=3, mode="constant", cval=0.0)
        return np.clip(v, 0, 1)

    return f


def rot2(theta_deg):
    t = np.radians(theta_deg)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


def seed_torus(world: World, f, centre, theta_deg=0.0) -> np.ndarray:
    """Place patch f at centre, rotated by theta (counter-clockwise in (x, y))."""
    Lx, Ly = world.box
    dv = world.xy - np.asarray(centre)
    dv[:, 0] -= Lx * np.round(dv[:, 0] / Lx)
    dv[:, 1] -= Ly * np.round(dv[:, 1] / Ly)
    q = dv @ rot2(theta_deg)  # rotate points back by theta: q = R(-theta) dv
    return f(q[:, 0], q[:, 1])


def torus_centroid(world: World, A: np.ndarray) -> np.ndarray:
    Lx, Ly = world.box
    out = []
    for k, Lk in enumerate((Lx, Ly)):
        ang = 2 * np.pi * world.xy[:, k] / Lk
        out.append((np.angle((A * np.exp(1j * ang)).sum()) % (2 * np.pi)) * Lk / (2 * np.pi))
    return np.array(out)


def tangent_frame(p):
    """Orthonormal (e1, e2) tangent to the sphere at unit vector p (e1 points 'east')."""
    p = p / np.linalg.norm(p)
    ref = np.array([0.0, 0.0, 1.0]) if abs(p[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = np.cross(ref, p)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(p, e1)
    return e1, e2


def seed_sphere(world: World, f, p, heading_vec, theta_extra=0.0):
    """Place patch f on the sphere at unit vector p, its native heading (68.2 deg for S001 in
    the patch frame) turned to point along tangent vector heading_vec. Uses the exponential map
    (azimuthal equidistant chart) at p."""
    rho = world.params["rho"]
    u = world.xy / rho
    p = p / np.linalg.norm(p)
    h = heading_vec - (heading_vec @ p) * p
    h /= np.linalg.norm(h)
    e1, e2 = h, np.cross(p, h)
    cosd = np.clip(u @ p, -1, 1)
    ang = np.arccos(cosd)
    x1, x2 = u @ e1, u @ e2
    nrm = np.maximum(np.hypot(x1, x2), 1e-15)
    gx, gy = rho * ang * x1 / nrm, rho * ang * x2 / nrm  # chart coords, gx along heading
    # rotate chart so the patch's own heading (theta_extra, degrees, in patch frame) aligns with gx
    q = np.stack([gx, gy], 1) @ rot2(theta_extra).T  # q = R(theta) g: chart +x -> patch heading
    v = f(q[:, 0], q[:, 1])
    v[ang * rho > 60] = 0.0
    return v


def mass(world: World, A: np.ndarray) -> float:
    return float(A.sum() if world.area is None else (A * world.area).sum())


def sphere_centroid(world: World, A: np.ndarray) -> np.ndarray:
    a = A if world.area is None else A * world.area
    c = (a[:, None] * world.xy).sum(0)
    return c / np.linalg.norm(c)


def components(world: World, A: np.ndarray, thr=0.1, link=2.5):
    """Connected blobs of cells with A > thr (cells within `link` cells are linked)."""
    from scipy.sparse.csgraph import connected_components

    idx = np.flatnonzero(A > thr)
    if len(idx) == 0:
        return []
    sub = World(world.kind, world.xy[idx], world.params, world.box)
    i, j, _ = sub.pairs(link)
    g = sp.csr_matrix((np.ones(len(i)), (i, j)), shape=(len(idx), len(idx)))
    nc, lab = connected_components(g, directed=False)
    out = []
    for k in range(nc):
        m = idx[lab == k]
        out.append(m)
    return out


def seed_disk(world: World, f, p: complex, heading_deg: float, home_deg: float = 68.198):
    """Place patch f on a hyperbolic world at Poincare point p, heading heading_deg (direction
    in the disk picture at p). Uses geodesic polar coordinates at p via the isometry
    w = (z - p) / (1 - conj(p) z); its derivative at p is real and positive only when p is
    real or imaginary... in general it rotates by arg(1/(1 - |p|^2)) = 0, so headings carry
    over unchanged."""
    kap = world.params["kappa"]
    z = world.xy[:, 0] + 1j * world.xy[:, 1]
    w = (z - p) / (1 - np.conj(p) * z)
    r = 2 * kap * np.arctanh(np.minimum(np.abs(w), 1 - 1e-15))
    ang = np.angle(w) - np.radians(heading_deg)
    gx, gy = r * np.cos(ang), r * np.sin(ang)
    q = np.stack([gx, gy], 1) @ rot2(home_deg).T
    v = f(q[:, 0], q[:, 1])
    v[r > 60] = 0.0
    return v


def disk_centroid(world: World, A: np.ndarray, mask=None) -> complex:
    """Mass-weighted centre on the hyperbolic disk (Einstein midpoint in the hyperboloid model),
    returned as a Poincare point."""
    a = (A if world.area is None else A * world.area)
    if mask is not None:
        a = a * mask
    z = world.xy
    s2 = (z**2).sum(1)
    X = np.stack([(1 + s2), 2 * z[:, 0], 2 * z[:, 1]], 1) / (1 - s2)[:, None]
    c = (a[:, None] * X).sum(0)
    c = c / np.sqrt(c[0] ** 2 - c[1] ** 2 - c[2] ** 2)
    return complex(c[1] / (1 + c[0]), c[2] / (1 + c[0]))
