"""REEF-behavior: minimal torus-aware two-body tracker for glider/ring encounters.

Owned by the Behavior lane (research/experiments/REEF-behavior/). It reads states; it never
steps the world, so it can score any engine's output (alm, alm_check FFT or direct).

What it does, and what it refuses to do
---------------------------------------
* Support is ``A >= theta``. Connected components are taken on the torus (8-connectivity), so a
  body straddling an edge is one component, not two.
* Identity is carried per cell (maximum overlap at cell resolution, see ``Tracker``). Frames
  must be close enough in time that a body overlaps its own previous support; a component with
  no labelled cell is an orphan, never guessed.
* A label is ``single`` only when exactly one non-debris component carries its cells and that
  component carries no other label's cells (above ``debris_mass``). Two labels in one
  component are ``merged``; one label in several components is ``fragmented``; no carrier is
  ``lost``. **No per-label centroid is reported unless the label is single.** Merged or
  fragmented frames report topology, owned masses and unassigned mass instead. A label that
  separates again after a merge is reported ``reacquired``; ``contact_lineage`` keeps the fact
  that the body touched the other label.
* Masses are sum(A) / R**2, the PROTOCOL.md unit (``TrackerConfig.R``). Components lighter
  than ``debris_mass`` (default 0.01, the protocol's death threshold) are debris, not bodies:
  the isolated Orbium routinely carries detached satellites of up to ~0.002 (see README).
* Mass bookkeeping per frame: total, support (in components), sub-threshold halo
  (total - support), debris (components below ``debris_mass``) and orphan (unlabelled cells in
  bodies). Unassigned mass = halo + debris + orphan.

Interaction helpers
-------------------
* ``support_gap``: minimum torus distance between two cell sets.
* ``superposition_defect``: encounter state against the sum of its matched isolated controls.
  Before any interaction the two bodies' exact supports are more than 2R apart and the encounter
  equals the sum of the controls up to FFT rounding; the first frame where the defect exceeds a
  floor is the operational interaction onset.
* ``ImageGuard``: distance from an unwrapped glider track to periodic images of a fixed ring, for
  censoring before a distinct torus re-encounter.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

STATUS = ("single", "fragmented", "merged", "lost")

_SHIFTS8 = ((0, 1), (1, 0), (1, 1), (1, -1))
_SHIFTS4 = ((0, 1), (1, 0))


# --- components on the torus --------------------------------------------------------------


def label_torus(mask: np.ndarray, connectivity: int = 8) -> tuple[np.ndarray, int]:
    """Connected components of a boolean mask on the periodic grid.

    Returns ``(labels, n)`` with labels ``-1`` off the mask and ``0..n-1`` on it, numbered in
    raster order of each component's first cell. Pure NumPy, sparse: edges between neighbouring
    on-cells (with wrap-around), then min-label propagation with pointer jumping.
    """
    mask = np.asarray(mask, dtype=bool)
    shifts = _SHIFTS8 if connectivity == 8 else _SHIFTS4
    k = int(mask.sum())
    out = np.full(mask.shape, -1, dtype=np.int64)
    if k == 0:
        return out, 0
    idx = out.copy()
    idx[mask] = np.arange(k)
    us, vs = [], []
    for dy, dx in shifts:
        nb = np.roll(idx, (-dy, -dx), (0, 1))  # nb[y, x] = idx[y + dy, x + dx]
        e = mask & (nb >= 0)
        us.append(idx[e])
        vs.append(nb[e])
    u, v = np.concatenate(us), np.concatenate(vs)
    lab = np.arange(k)
    while True:
        m = np.minimum(lab[u], lab[v])
        new = lab.copy()
        np.minimum.at(new, u, m)
        np.minimum.at(new, v, m)
        while True:  # pointer jumping
            nxt = new[new]
            if np.array_equal(nxt, new):
                break
            new = nxt
        if np.array_equal(new, lab):
            break
        lab = new
    roots, inv = np.unique(lab, return_inverse=True)
    out[mask] = inv
    return out, len(roots)


def _min_image(d, n):
    return (np.asarray(d, dtype=float) + n / 2) % n - n / 2


@dataclass
class Component:
    cells: np.ndarray  # (k, 2) int indices (y, x)
    mass: float  # sum of A over the component's support cells
    centroid: tuple[float, float]  # (cy, cx) in [0, N)
    extent: tuple[float, float]  # unwrapped bounding-box size (y, x) in cells
    wide: bool  # extent >= N/2 on some axis: centroid not trustworthy
    gyradius: float = 0.0  # mass-weighted RMS distance from centroid, cells
    radius: float = 0.0  # max support-cell distance from centroid, cells
    unwrapped: tuple = None  # body track, carried from the max-overlap parent
    lineage: frozenset = frozenset()
    composition: dict = field(default_factory=dict)


def components(A: np.ndarray, theta: float, connectivity: int = 8) -> list[Component]:
    """Components of ``A >= theta`` with mass, torus centroid and extent."""
    A = np.asarray(A, dtype=float)
    ny, nx = A.shape
    labels, n = label_torus(A >= theta, connectivity)
    out = []
    if n == 0:
        return out
    ys, xs = np.nonzero(labels >= 0)
    lab = labels[ys, xs]
    order = np.argsort(lab, kind="stable")
    ys, xs, lab = ys[order], xs[order], lab[order]
    bounds = np.searchsorted(lab, np.arange(n + 1))
    for i in range(n):
        cy, cx = ys[bounds[i] : bounds[i + 1]], xs[bounds[i] : bounds[i + 1]]
        w = A[cy, cx]
        m = float(w.sum())
        # unwrap about the first cell, then refine about the weighted mean (exact if extent < N/2)
        oy, ox = _min_image(cy - cy[0], ny), _min_image(cx - cx[0], nx)
        my, mx = cy[0] + np.sum(w * oy) / m, cx[0] + np.sum(w * ox) / m
        oy, ox = _min_image(cy - my, ny), _min_image(cx - mx, nx)
        my, mx = my + np.sum(w * oy) / m, mx + np.sum(w * ox) / m
        ext = (float(oy.max() - oy.min() + 1), float(ox.max() - ox.min() + 1))
        r2 = oy * oy + ox * ox
        out.append(
            Component(
                cells=np.stack([cy, cx], 1),
                mass=m,
                centroid=(float(my % ny), float(mx % nx)),
                extent=ext,
                wide=ext[0] >= ny / 2 or ext[1] >= nx / 2,
                gyradius=float(np.sqrt(np.sum(w * r2) / m)),
                radius=float(np.sqrt(r2.max())),
            )
        )
    return out


# --- geometry -------------------------------------------------------------------------------


def support_gap(cells_a: np.ndarray, cells_b: np.ndarray, shape) -> float:
    """Minimum torus (Euclidean, minimum-image) distance between two cell sets, in cells.

    0 means a shared cell; 1 or sqrt(2) means 8-adjacent (one component at that threshold).
    Uses boundary cells only, so it is cheap for compact bodies.
    """
    if len(cells_a) == 0 or len(cells_b) == 0:
        return float("inf")
    a, b = _boundary(cells_a, shape), _boundary(cells_b, shape)
    best = np.inf
    for chunk in np.array_split(a, max(1, len(a) // 512)):
        dy = _min_image(chunk[:, None, 0] - b[None, :, 0], shape[0])
        dx = _min_image(chunk[:, None, 1] - b[None, :, 1], shape[1])
        best = min(best, float(np.sqrt((dy * dy + dx * dx).min())))
    return best


def _boundary(cells: np.ndarray, shape) -> np.ndarray:
    ny, nx = shape
    m = np.zeros(shape, dtype=bool)
    m[cells[:, 0], cells[:, 1]] = True
    inner = m.copy()
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        inner &= np.roll(m, (dy, dx), (0, 1))
    return np.argwhere(m & ~inner)


def mask_cells(mask: np.ndarray) -> np.ndarray:
    return np.argwhere(mask)


def superposition_defect(A_enc: np.ndarray, *controls: np.ndarray) -> dict:
    """Encounter minus the sum of matched isolated controls: max, L1 and argmax cell."""
    D = np.asarray(A_enc, dtype=float) - np.sum(controls, axis=0)
    i = int(np.argmax(np.abs(D)))
    return {
        "defect_max": float(np.abs(D).max()),
        "defect_l1": float(np.abs(D).sum()),
        "defect_cell": [int(c) for c in np.unravel_index(i, D.shape)],
    }


@dataclass
class ImageGuard:
    """Censor before a glider meets a periodic image of a fixed target other than the primary.

    ``target`` is the fixed body's centroid (cells), ``guard`` the distance (cells, between
    centroids) below which an image counts as approached. The primary image is the one nearest
    the glider's start; any other image coming within ``guard`` is a distinct re-encounter.
    Crossing the grid edge alone changes nothing.
    """

    shape: tuple[int, int]
    target: tuple[float, float]
    guard: float

    def nearest_images(self, p_unwrapped, k: int = 2):
        ny, nx = self.shape
        py, px = p_unwrapped
        out = []
        for jy in range(-k, k + 1):
            for jx in range(-k, k + 1):
                ty, tx = self.target[0] + jy * ny, self.target[1] + jx * nx
                out.append(((jy, jx), float(np.hypot(py - ty, px - tx))))
        return sorted(out, key=lambda r: r[1])

    def primary(self, p0_unwrapped):
        return self.nearest_images(p0_unwrapped)[0][0]

    def check(self, p_unwrapped, primary) -> tuple[bool, float]:
        """(censor, distance to the nearest non-primary image)."""
        others = [d for img, d in self.nearest_images(p_unwrapped) if img != tuple(primary)]
        d = min(others)
        return d < self.guard, d


# --- the tracker ----------------------------------------------------------------------------


@dataclass
class TrackerConfig:
    theta: float = 0.1  # support threshold
    debris_mass: float = 0.01  # in mass units below: a component lighter than this is debris
    connectivity: int = 8
    R: float = 13.0  # masses are reported as sum(A) / R**2 (PROTOCOL.md units); R=1 gives cells


class Tracker:
    """Follow initial labels into later connected components without forcing identities.

    ``Tracker(A0, seeds)`` where ``seeds`` maps label -> boolean mask picking that label's
    initial cells. Call ``update(A, t)`` once per frame, in order. ``records`` holds one dict
    per frame; ``events`` holds topology changes.

    Identity is carried per cell (maximum overlap at cell resolution): a support cell keeps the
    label it had last frame; new support cells take the majority label of already-labelled
    8-neighbours, repeated until the component is filled. A component holding two labels'
    cells is reported as merged (no per-label centroid); when it splits, each fragment carries
    the labels of its own cells, so a glider that brushes the ring and leaves is reacquired.
    ``contact_lineage`` (the union of every label a body has ever touched) is reported too.
    """

    def __init__(self, A0: np.ndarray, seeds: dict, config: TrackerConfig | None = None, t0: float = 0.0):
        self.cfg = config or TrackerConfig()
        A0 = np.asarray(A0, dtype=float)
        self.shape = A0.shape
        self.labels = tuple(sorted(seeds))
        comps = self._components(A0)
        support = np.zeros(self.shape, dtype=bool)
        for c in comps:
            support[c.cells[:, 0], c.cells[:, 1]] = True
        owner = np.full(self.shape, -1, dtype=np.int64)
        for i, lab in enumerate(self.labels):
            sel = np.asarray(seeds[lab], dtype=bool) & support
            if not sel.any():
                raise ValueError(f"seed label {lab!r} selects no support cell at t0")
            if (owner[sel] >= 0).any():
                raise ValueError("seed masks overlap")
            owner[sel] = i
        self.owner = self._fill(owner, support)
        self._lift = {lab: None for lab in self.labels}
        self._oc = {lab: None for lab in self.labels}
        self._lineage_prev = None
        self.prev = comps
        self.records: list[dict] = []
        self.events: list[dict] = []
        self._topology = None
        self._record(A0, comps, support, t0)

    def _components(self, A):
        comps = components(A, self.cfg.theta, self.cfg.connectivity)
        for c in comps:
            c.mass /= self.cfg.R**2
        return comps

    def _fill(self, owner, support):
        """Give unlabelled support cells the majority label of labelled 8-neighbours, repeatedly."""
        owner = np.where(support, owner, -1)
        L = len(self.labels)
        shifts = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
        while True:
            todo = support & (owner < 0)
            if not todo.any():
                break
            counts = np.zeros((L,) + self.shape, dtype=np.int64)
            for i in range(L):
                m = (owner == i).astype(np.int64)
                for dy, dx in shifts:
                    counts[i] += np.roll(m, (dy, dx), (0, 1))
            best = counts.argmax(0)
            hit = todo & (counts.max(0) > 0)
            if not hit.any():
                break  # remaining cells sit in components with no labelled cell: orphans
            owner = np.where(hit, best, owner)
        return owner

    def update(self, A: np.ndarray, t: float) -> dict:
        A = np.asarray(A, dtype=float)
        comps = self._components(A)
        support = np.zeros(self.shape, dtype=bool)
        for c in comps:
            support[c.cells[:, 0], c.cells[:, 1]] = True
        self._inherit_lineage(comps)
        self.owner = self._fill(self.owner, support)
        self.prev = comps
        return self._record(A, comps, support, t)

    def _inherit_lineage(self, comps):
        idx = np.full(self.shape, -1, dtype=np.int64)
        for j, p in enumerate(self.prev):
            idx[p.cells[:, 0], p.cells[:, 1]] = j
        for c in comps:
            ids = np.unique(idx[c.cells[:, 0], c.cells[:, 1]])
            c.lineage = frozenset().union(*[self.prev[j].lineage for j in ids if j >= 0])

    def _record(self, A, comps, support, t) -> dict:
        cfg, (ny, nx) = self.cfg, self.shape
        scale = cfg.R**2
        own = self.owner
        for c in comps:
            o = own[c.cells[:, 0], c.cells[:, 1]]
            w = A[c.cells[:, 0], c.cells[:, 1]] / scale
            c.composition = {lab: float(w[o == i].sum()) for i, lab in enumerate(self.labels)}
            c.unowned = float(w[o < 0].sum())
            c.owners = frozenset(lab for lab, m in c.composition.items() if m >= cfg.debris_mass)
            if self._lineage_prev is None:  # t0: contact lineage = labels present
                c.lineage = frozenset(lab for lab, m in c.composition.items() if m > 0)
            c.lineage = c.lineage | c.owners
        self._lineage_prev = True
        body = [c for c in comps if c.mass >= cfg.debris_mass]
        total = float(A.sum()) / scale
        supp = float(sum(c.mass for c in comps))
        rec = {
            "t": t,
            "total_mass": total,
            "support_mass": supp,
            "halo_mass": total - supp,
            "debris_mass": float(sum(c.mass for c in comps if c.mass < cfg.debris_mass)),
            "orphan_mass": float(sum(c.unowned for c in comps if c.mass >= cfg.debris_mass)),
            "n_components": len(comps),
            "n_bodies": len(body),
            "labels": {},
        }
        rec["unassigned_mass"] = rec["halo_mass"] + rec["orphan_mass"] + rec["debris_mass"]
        # per-label owned centroid (minimum image about the previous one) and continuous lift
        for i, lab in enumerate(self.labels):
            ys, xs = np.nonzero(own == i)
            carriers = [c for c in body if lab in c.owners]
            if not carriers:
                status = "lost"
            elif any(len(c.owners) > 1 for c in carriers):
                status = "merged"
            elif len(carriers) > 1:
                status = "fragmented"
            else:
                status = "single"
            r = {"status": status, "mass": float(sum(c.composition[lab] for c in carriers)), "n_carriers": len(carriers)}
            if len(ys):
                w = A[ys, xs]
                ref = self._oc[lab] if self._oc[lab] is not None else (ys[0], xs[0])
                for _ in range(2):
                    ref = (
                        ref[0] + float(np.sum(w * _min_image(ys - ref[0], ny)) / w.sum()),
                        ref[1] + float(np.sum(w * _min_image(xs - ref[1], nx)) / w.sum()),
                    )
                if self._lift[lab] is None:
                    self._lift[lab] = ref
                else:
                    last = self._oc[lab]
                    self._lift[lab] = (
                        self._lift[lab][0] + float(_min_image(ref[0] - last[0], ny)),
                        self._lift[lab][1] + float(_min_image(ref[1] - last[1], nx)),
                    )
                self._oc[lab] = ref
            if status == "single" and not carriers[0].wide:
                r["centroid"] = [self._oc[lab][0] % ny, self._oc[lab][1] % nx]
                r["unwrapped"] = list(self._lift[lab])
                r["gyradius"], r["radius"] = carriers[0].gyradius, carriers[0].radius
                r["reacquired"] = bool(self.records) and self.records[-1]["labels"][lab]["status"] != "single"
            rec["labels"][lab] = r
        for c in comps:  # body tracks in each majority label's lift
            if c.owners or any(v > 0 for v in c.composition.values()):
                lab = max(c.composition, key=c.composition.get)
                oc, lift = self._oc[lab], self._lift[lab]
                c.unwrapped = (
                    lift[0] + float(_min_image(c.centroid[0] - oc[0], ny)),
                    lift[1] + float(_min_image(c.centroid[1] - oc[1], nx)),
                )
            else:
                c.unwrapped = c.centroid
        rec["bodies"] = [
            {
                "owners": "".join(sorted(map(str, c.owners))) or "-",
                "contact_lineage": "".join(sorted(map(str, c.lineage))) or "-",
                "mass": c.mass,
                "owned_mass": {str(k): v for k, v in c.composition.items()},
                "unowned_mass": c.unowned,
                "centroid": list(c.centroid),
                "unwrapped": list(c.unwrapped),
                "extent": list(c.extent),
                "wide": c.wide,
                "gyradius": c.gyradius,
                "radius": c.radius,
            }
            for c in sorted(body, key=lambda c: ("".join(sorted(map(str, c.owners))), -c.mass))
        ]
        if len(self.labels) == 2:  # gap between the two labels' owned support cells
            a, b = np.argwhere(own == 0), np.argwhere(own == 1)
            rec["support_gap"] = support_gap(a, b, self.shape) if len(a) and len(b) else None
        topo = "|".join(sorted(b["owners"] for b in rec["bodies"]))
        rec["topology"] = topo
        if self._topology is not None and topo != self._topology:
            self.events.append({"t": t, "from": self._topology, "to": topo, "kind": _event_kind(self._topology, topo)})
        self._topology = topo
        self.records.append(rec)
        return rec


def _event_kind(before: str, after: str) -> str:
    b, a = before.split("|") if before else [], after.split("|") if after else []
    if len(a) < len(b) and any(len(x) > 1 for x in a) and not any(len(x) > 1 for x in b):
        return "merge"
    if len(a) > len(b):
        return "split"
    if len(a) < len(b):
        return "loss_or_merge"
    return "relabel"


def exact_support_gap(A: np.ndarray, mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    """Gap between the exact supports (A > 0) inside two disjoint selection masks."""
    pos = np.asarray(A) > 0
    return support_gap(mask_cells(pos & mask_a), mask_cells(pos & mask_b), np.asarray(A).shape)
