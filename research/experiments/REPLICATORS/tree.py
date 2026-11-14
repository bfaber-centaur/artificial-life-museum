"""Offline cell tracking and family tree for a recorded run (record.py output).

Cells are the peaks of the field blurred with a Gaussian (sigma SIG px, torus), one peak per
cell in the dividing creatures used here (checked by eye on contact sheets). Peaks are linked
frame to frame by nearest neighbour (<= LINK px; a track may skip up to GAP frames). A peak with
no predecessor is a daughter of the nearest live track within BIRTH px; a daughter counts only
if her track lives MINLIFE frames, otherwise she is a flicker and is dropped, and only if the
mother's own track also goes on for MINLIFE frames, otherwise the cell's peak merely jumped and
the two tracks are spliced into one. Each confirmed
birth splits the mother into two daughter segments (the continuing one and the new one).
Colour is a neutral heritable marker: the founder is hue 0.55 and each daughter's hue is her
mother's plus a Gaussian step (sd HUE_SD, fixed seed), so relatives look alike and lineages drift
apart. Tree rows come from a standard dendrogram layout (leaves in depth-first order).
"""
from __future__ import annotations

import colorsys

import numpy as np
from scipy import ndimage

SIG, THR, LINK, GAP, BIRTH, MINLIFE = 4.0, 0.05, 8.0, 3, 30.0, 10
HUE0, HUE_SD, HUE_SEED = 0.55, 0.08, 2026


def peaks(S, sig=SIG, thr=THR):
    G = ndimage.gaussian_filter(S, sig, mode="wrap")
    mx = ndimage.maximum_filter(G, size=2 * int(1.5 * sig) + 1, mode="wrap")
    return np.argwhere((G == mx) & (G > thr)).astype(float)


def tdist(a, b, N):
    d = np.abs(a[:, None, :] - b[None, :, :])
    d = np.minimum(d, N - d)
    return np.sqrt((d ** 2).sum(-1))


def link(frames, N):
    """Raw tracks: list of dict(pts={frame: (y, x)}, parent=track idx or None, born=frame)."""
    tracks = []
    for f, P in enumerate(frames):
        live = [k for k, tk in enumerate(tracks) if f - tk["last"] <= GAP + 1 and tk["last"] < f]
        used_t, used_p = set(), set()
        if live and len(P):
            last = np.array([tracks[k]["pts"][tracks[k]["last"]] for k in live])
            D = tdist(last, P, N)
            for i, j in sorted(np.ndindex(D.shape), key=lambda ij: D[ij]):
                if D[i, j] > LINK:
                    break
                if i in used_t or j in used_p:
                    continue
                k = live[i]
                tracks[k]["pts"][f] = tuple(P[j]); tracks[k]["last"] = f
                used_t.add(i); used_p.add(j)
        for j in range(len(P)):
            if j in used_p:
                continue
            parent = None
            if f > 0 and live:
                last = np.array([tracks[k]["pts"][tracks[k]["last"]] for k in live])
                d = tdist(P[j:j + 1], last, N)[0]
                if d.min() <= BIRTH:
                    parent = live[int(d.argmin())]
            tracks.append(dict(pts={f: tuple(P[j])}, last=f, born=f, parent=parent))
    return tracks


def build_tree(tracks, nframes):
    """Drop flicker births; split mothers at each confirmed birth. Returns segments."""
    keep = [True] * len(tracks)
    for k, tk in enumerate(tracks):
        life = tk["last"] - tk["born"] + 1
        if tk["parent"] is not None and life < MINLIFE:
            keep[k] = False
    # handover: if the mother's own peak ends within MINLIFE frames of a daughter appearing, the
    # "daughter" is the same cell whose peak jumped (no division): splice her track onto the mother
    order_k = sorted((tk["born"], k) for k, tk in enumerate(tracks) if keep[k] and tk["parent"] is not None)
    for f, k in order_k:
        p = tracks[k]["parent"]
        while not keep[p]:
            p = tracks[p]["parent"]
        tracks[k]["parent"] = p
        M = tracks[p]
        if M["last"] - f < MINLIFE and not M.get("spliced"):
            M["pts"] = {fr: pt for fr, pt in M["pts"].items() if fr < f}
            M["pts"].update(tracks[k]["pts"]); M["last"] = tracks[k]["last"]
            keep[k] = False; M["spliced_from"] = M.get("spliced_from", []) + [k]
            for tk in tracks:  # the spliced track's later daughters now belong to the mother
                if tk["parent"] == k:
                    tk["parent"] = p
    births = {}  # mother track -> sorted list of (frame, child track)
    for k, tk in enumerate(tracks):
        if keep[k] and tk["parent"] is not None:
            p = tk["parent"]
            while not keep[p]:  # a flicker's daughter belongs to the flicker's mother
                p = tracks[p]["parent"]
            births.setdefault(p, []).append((tk["born"], k))
    segs = []  # dict(track, start, end, parent_seg, lo, hi, gen, end_kind)
    seg_of_track_start = {}

    def add_track(k, lo, hi, gen, parent_seg, start):
        tk = tracks[k]
        cur = dict(track=k, start=start, lo=lo, hi=hi, gen=gen, parent=parent_seg)
        segs.append(cur)
        for f, child in sorted(births.get(k, [])):
            cur["end"] = f; cur["end_kind"] = "division"
            mid = 0.5 * (cur["lo"] + cur["hi"])
            me = len(segs) - 1
            # the continuing mother takes the half on her side of the child (stable order)
            cont = dict(track=k, start=f, lo=cur["lo"], hi=mid, gen=cur["gen"] + 1, parent=me)
            add_track(child, mid, cur["hi"], cur["gen"] + 1, me, f)
            segs.append(cont)
            cur = cont
        cur["end"] = tk["last"] + 1
        cur["end_kind"] = "alive" if tk["last"] >= nframes - 1 - GAP else "vanished"

    roots = [k for k, tk in enumerate(tracks) if keep[k] and tk["parent"] is None]
    n0 = max(1, len(roots))
    for r_i, k in enumerate(roots):
        add_track(k, r_i / n0, (r_i + 1) / n0, 0, None, tracks[k]["born"])
    rng = np.random.default_rng(HUE_SEED)
    kids = {}
    for i, sg in enumerate(segs):
        if sg["parent"] is not None:
            kids.setdefault(sg["parent"], []).append(i)
    for i, sg in enumerate(segs):  # parents precede children in segs
        sg["hue"] = (HUE0 + (0.0 if sg["parent"] is None else segs[sg["parent"]]["hue"] - HUE0
                             + rng.normal(0, HUE_SD))) % 1.0
    order = []

    def dfs(i):
        if i not in kids:
            order.append(i)
        for c in kids.get(i, []):
            dfs(c)
    for i, sg in enumerate(segs):
        if sg["parent"] is None:
            dfs(i)
    rank = {i: r for r, i in enumerate(order)}

    def ypos(i):
        if "y" not in segs[i]:
            segs[i]["y"] = rank[i] if i not in kids else float(np.mean([ypos(c) for c in kids[i]]))
        return segs[i]["y"]
    for i in range(len(segs)):
        ypos(i)
    for sg in segs:
        sg["y"] /= max(1, len(order) - 1)
    return segs, keep


def segments_at(segs, tracks, f):
    """[(y, x, seg)] for the cells alive at frame f."""
    out = []
    for s in segs:
        if s["start"] <= f < s["end"]:
            tk = tracks[s["track"]]
            if f in tk["pts"]:
                out.append((*tk["pts"][f], s))
    return out


def colorize(S, cells, N, gain=1.0, pad=48):
    """Each pixel of a cell (blurred field > THR/2) takes the hue of the nearest cell peak."""
    G = ndimage.gaussian_filter(S, 2.0, mode="wrap")
    mask = G > 0.02
    v = np.clip(S * gain, 0, 1)
    rgb = np.stack([v * 0.3] * 3, -1)
    if cells:
        seeds = np.zeros((N, N), dtype=int)
        for i, (y, x, s) in enumerate(cells):
            seeds[int(round(y)) % N, int(round(x)) % N] = i + 1
        big = np.pad(seeds, pad, mode="wrap")
        _, (iy, ix) = ndimage.distance_transform_edt(big == 0, return_indices=True)
        near = big[iy, ix][pad:-pad, pad:-pad]
        hues = np.array([0.0] + [s["hue"] for _, _, s in cells])
        H = hues[near]
        sat = np.where(mask, 0.85, 0.0)
        # vectorised hsv -> rgb
        i6 = np.floor(H * 6).astype(int) % 6
        fr = H * 6 - np.floor(H * 6)
        val = np.where(mask, 0.12 + 0.88 * v, v * 0.3)
        p, q, t = val * (1 - sat), val * (1 - sat * fr), val * (1 - sat * (1 - fr))
        R = np.choose(i6, [val, q, p, p, t, val]); Gc = np.choose(i6, [t, val, val, q, p, p]); B = np.choose(i6, [p, p, t, val, val, q])
        rgb = np.where(mask[..., None], np.stack([R, Gc, B], -1), rgb)
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def hue_rgb(h):
    return colorsys.hsv_to_rgb(h, 0.85, 1.0)
