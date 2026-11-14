"""Track bodies of a dividing creature frame by frame and build its family tree.

Every `every` steps, label bodies (sum of channels, optionally Gaussian-blurred, > thr, mass >= min_mass, torus) and match
them to the previous frame by pixel overlap:
  one parent, one child      -> same body
  one parent, >= 2 children  -> DIVISION if at least two children carry >= frac of the parent's
                                mass (each such child is a new body); smaller pieces are debris
                                and keep the parent's id
  >= 2 parents, one child    -> FUSION (new body, keeps the heavier parent's colour interval)
  no parent                  -> appearance; no child -> DEATH
Each body owns an interval of [0, 1); daughters split their mother's interval, so the
interval midpoint is both the body's hue and its row in the family-tree plot.
"""
from __future__ import annotations

import colorsys
from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage

from common import torus_label


@dataclass
class Body:
    id: int
    lo: float
    hi: float
    born: float
    parent: int | None
    gen: int
    how: str  # founder | division | fusion | appeared
    died: float | None = None
    end: str | None = None  # death | division | fusion | alive
    track: list = field(default_factory=list)  # (t, y, x, mass)

    @property
    def mid(self):
        return 0.5 * (self.lo + self.hi)


class Tracker:
    def __init__(self, thr=0.2, min_mass=5.0, frac=0.2, blur=0.0):
        self.thr, self.min_mass, self.frac, self.blur = thr, min_mass, frac, blur
        self.bodies: dict[int, Body] = {}
        self.prev_lab = None
        self.prev_ids: dict[int, int] = {}
        self.next_id = 0
        self.events = []  # (t, kind, parent ids, child ids)

    def _new(self, lo, hi, t, parent, gen, how):
        b = Body(self.next_id, lo, hi, t, parent, gen, how)
        self.bodies[b.id] = b
        self.next_id += 1
        return b.id

    def update(self, t, S):
        Sm = ndimage.gaussian_filter(S, self.blur, mode="wrap") if self.blur else S
        lab, n = torus_label(Sm > self.thr)
        idx = np.arange(1, n + 1)
        mass = ndimage.sum(S, lab, idx) if n else np.zeros(0)
        keep = {i for i, m in zip(idx, mass) if m >= self.min_mass}
        lab = np.where(np.isin(lab, list(keep)), lab, 0)
        mass_of = {i: float(m) for i, m in zip(idx, mass)}
        H, W = S.shape
        cy = {}
        for i in keep:  # circular centroid
            ys, xs = np.nonzero(lab == i)
            wts = S[ys, xs]
            ay = np.angle(np.sum(wts * np.exp(2j * np.pi * ys / H))) % (2 * np.pi) * H / (2 * np.pi)
            ax = np.angle(np.sum(wts * np.exp(2j * np.pi * xs / W))) % (2 * np.pi) * W / (2 * np.pi)
            cy[i] = (ay, ax)
        ids = {}
        if self.prev_lab is None:
            for i in sorted(keep):
                ids[i] = self._new(0.0, 1.0, t, None, 0, "founder") if not ids else self._new(0, 1, t, None, 0, "appeared")
        else:
            both = (self.prev_lab > 0) & (lab > 0)
            pairs = {}
            for a, b in zip(self.prev_lab[both], lab[both]):
                pairs[(a, b)] = pairs.get((a, b), 0) + 1
            kids, pars = {}, {}
            for (a, b) in pairs:
                kids.setdefault(a, []).append(b)
                pars.setdefault(b, []).append(a)
            done = set()
            for a, bs in kids.items():
                pid = self.prev_ids[a]
                single = [b for b in bs if len(pars[b]) == 1]
                if len(single) >= 2:
                    pm = self.bodies[pid].track[-1][3]
                    big = sorted([b for b in single if mass_of[b] >= self.frac * pm], key=lambda b: cy[b][1])
                    if len(big) >= 2:
                        P = self.bodies[pid]
                        P.died, P.end = t, "division"
                        step = (P.hi - P.lo) / len(big)
                        new = []
                        for k, b in enumerate(big):
                            ids[b] = self._new(P.lo + k * step, P.lo + (k + 1) * step, t, pid, P.gen + 1, "division")
                            new.append(ids[b]); done.add(b)
                        for b in single:
                            if b not in done:
                                ids[b] = new[0]; done.add(b)  # debris rides with the first daughter
                        self.events.append((t, "division", [pid], new))
                        continue
                for b in single:
                    if b not in done:
                        ids[b] = pid; done.add(b)
            for b in keep:
                if b in done:
                    continue
                ps = pars.get(b, [])
                if not ps:
                    ids[b] = self._new(0, 1, t, None, 0, "appeared")
                    self.events.append((t, "appeared", [], [ids[b]]))
                else:
                    pids = sorted({self.prev_ids[a] for a in ps}, key=lambda p: -self.bodies[p].track[-1][3])
                    if len(pids) == 1:
                        ids[b] = pids[0]
                    else:
                        H0 = self.bodies[pids[0]]
                        nid = self._new(H0.lo, H0.hi, t, pids[0], H0.gen, "fusion")
                        for p in pids:
                            self.bodies[p].died, self.bodies[p].end = t, "fusion"
                        ids[b] = nid
                        self.events.append((t, "fusion", pids, [nid]))
            alive_now = set(ids.values())
            for a, pid in self.prev_ids.items():
                B = self.bodies[pid]
                if pid not in alive_now and B.end is None:
                    B.died, B.end = t, "death"
                    self.events.append((t, "death", [pid], []))
        # duplicates (one id on several pieces) are fine: debris shares its body's id
        seen = set()
        for i, bid in ids.items():
            if bid in seen:
                continue
            seen.add(bid)
            m = sum(mass_of[j] for j, k in ids.items() if k == bid)
            self.bodies[bid].track.append((t, cy[i][0], cy[i][1], m))
        self.prev_lab, self.prev_ids = lab, ids
        return lab, ids

    def finish(self, t):
        for B in self.bodies.values():
            if B.end is None:
                B.died, B.end = t, "alive"

    def colorize(self, S, lab, ids, gain=1.0):
        H, W = S.shape
        rgb = np.zeros((H, W, 3))
        v = np.clip(S * gain, 0, 1)
        base = np.stack([v * 0.35] * 3, -1)  # unlabelled halo: dim grey
        rgb[:] = base
        for i, bid in ids.items():
            hue = self.bodies[bid].mid
            c = np.array(colorsys.hsv_to_rgb(hue, 0.85, 1.0))
            m = lab == i
            rgb[m] = (0.15 + 0.85 * v[m])[:, None] * c
        return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)

    def summary(self):
        kinds = {}
        for e in self.events:
            kinds[e[1]] = kinds.get(e[1], 0) + 1
        return dict(bodies=len(self.bodies), events=kinds,
                    max_gen=max(b.gen for b in self.bodies.values()))
