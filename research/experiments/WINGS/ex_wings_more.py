"""WINGS exhibits G025-G027: a SmoothLife glider, Lenia in three dimensions, a three-channel
aquarium. Loaded by film_wings.py."""

from __future__ import annotations

import numpy as np
from PIL import Image

from film_wings import ACCENT, BG, DIM, EXHIBITS, canvas, exhibit, rgb_tile, save_provenance, text, tile, write_media
from alm.provenance import state_sha256


def follow(A, w, axes=(0, 1)):
    """Integer-roll A so the periodic centroid of A (or A summed over leading channels) is centred,
    then crop a w-wide window (all given axes)."""
    from nd_survey import centroid
    T = A if A.ndim == len(axes) else A.sum(0)
    c = np.rint(centroid(T)).astype(int)
    n = T.shape[0]
    shift = tuple(n // 2 - x for x in c)
    lead = A.ndim - len(axes)
    B = np.roll(A, shift, tuple(range(lead, A.ndim)))
    sl = (slice(None),) * lead + tuple(slice(n // 2 - w // 2, n // 2 + w // 2) for _ in axes)
    return B[sl]


# --- G025 SmoothLife glider --------------------------------------------------------------------

@exhibit("G025")
def g025(render=True):
    import sl_glider as SG

    every = 4
    data, runs = {}, []
    for arm in ("dt10", "ring"):
        fr = [] if render else None
        S, A0, track = SG.run(arm, frames=fr, frame_every_tu=every)
        data[arm] = (fr, track)
        runs.append({"key": f"G025:{arm}", "rule": {"model": "SmoothLife (Rafler 2011), smooth time step",
                     **{k: getattr(S, k) for k in ("ra", "ri", "b1", "b2", "d1", "d2", "alpha_n", "alpha_m", "dt")}},
                     "grid": list(S.A.shape), "boundary": "periodic", "time_units": SG.TU,
                     "initial_state": ("sl_glider.build('%s'): 40x40 window of the rule-32 scout world at step 1500" % arm)
                     + (" plus the scout's still ring 60 cells ahead" if arm == "ring" else ""),
                     "initial_state_sha256": state_sha256(A0), "final_state_sha256": state_sha256(S.A)})
        print("G025", arm, flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G025-smoothlife-glider"
    T, pad, top, head = 384, 14, 70, 30
    W = 2 * T + 3 * pad
    H = top + head + T + pad
    out = []
    for k in range(len(data["dt10"][0])):
        t = k * every
        img = canvas(W, H, "A SmoothLife glider", f"Rafler's SmoothLife, outer radius 8.8, one of 80 random rules   t = {t:5d}")
        text(img, (pad, top), "alone (view follows it)", 14)
        img.paste(tile(follow(data["dt10"][0][k], 96), T), (pad, top + head))
        x = 2 * pad + T
        text(img, (x, top), "aimed at a still ring (whole world)", 14)
        img.paste(tile(data["ring"][0][k], T), (x, top + head))
        out.append(img)
    media = write_media(out, folder, "glider", fps=25, gif_width=520, gif_every=2, gif_colors=64)
    out[len(out) // 2].save(folder / "glider-still.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G025", "title": "A SmoothLife glider", "media": media + ["glider-still.png"],
        "frames": {"every_tu": every, "mp4_fps": 25}, "view": "left: 96x96 window following the periodic centroid; right: whole 192^2 torus; A in [0, 1] on inferno",
        "claim": "C068",
        "caveats": ["SmoothLife gliders are Rafler's 2011 result; this one comes from our own random-rule scout (sl_scan.py, rule 32)."],
    }, runs)
    return runs


# --- G026 Lenia in three dimensions, and flattened -----------------------------------------------

SPECIES_3D = [(2, "Triguttome labens (4Gu3l)"), (10, "Ovome ellipsis (3Ov1e)"), (4, "Sphaerome ventilans (1Sp1v)")]


@exhibit("G026")
def g026(render=True):
    from nd_lenia import NDLenia, entry_state, load_catalog
    from nd_survey import centroid

    cat = load_catalog("animals3D.json")
    settle, film_tu, fpt = 20, 100, 2
    runs, frames3, frames2 = [], {}, {}
    for idx, label in SPECIES_3D:
        e = cat[idx]
        p, A = entry_state(e, 3, 64)
        T = p[0]["T"]
        L = NDLenia(p, A)
        for _ in range(int(settle * T)):
            L.step()
        A3 = L.A[0].copy()
        c = np.rint(centroid(A3)).astype(int) % 64
        sl = A3[c[0]]
        W = np.zeros((128, 128)); W[32:96, 32:96] = sl
        L3, L2 = NDLenia(p, A3[None]), NDLenia(p, W[None])
        f3, f2 = [], []
        for s in range(int(film_tu * T) + 1):
            if render and s % int(T // fpt) == 0:
                f3.append(follow(L3.A[0], 48, axes=(0, 1, 2)).sum(0).astype(np.float32))
                f2.append(L2.A[0].astype(np.float32).copy())
            if s < film_tu * T:
                L3.step(); L2.step()
        frames3[idx], frames2[idx] = f3, f2
        common = {"rule": p[0], "settle_tu": settle, "time_units": film_tu}
        runs.append({"key": f"G026:{e['code']}:3d", **common, "grid": [64, 64, 64], "boundary": "periodic",
                     "initial_state": f"animals3D.json entry {idx} ({e['code']} {e['name']}) centred on 64^3, settled {settle} tu",
                     "initial_state_sha256": state_sha256(A3), "final_state_sha256": state_sha256(L3.A[0])})
        runs.append({"key": f"G026:{e['code']}:flat", **common, "grid": [128, 128], "boundary": "periodic",
                     "initial_state": f"plane axis-0 = {int(c[0])} (through the centroid) of the settled 3-D state, pasted at the centre of 128^2",
                     "initial_state_sha256": state_sha256(W), "final_state_sha256": state_sha256(L2.A[0])})
        print("G026", e["code"], flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G026-three-dimensions"
    T_, pad, top, head, mid = 260, 14, 70, 36, 30
    W_ = 3 * T_ + 4 * pad
    H_ = top + 2 * (T_ + head) + mid + pad
    out = []
    n = min(len(v) for v in frames3.values())
    for k in range(n):
        img = canvas(W_, H_, "Lenia in three dimensions", f"top: 3-D species, density summed along the line of sight   t = {k / fpt:5.1f}")
        for j, (idx, label) in enumerate(SPECIES_3D):
            x = pad + j * (T_ + pad)
            text(img, (x, top + 6), label, 13)
            img.paste(tile(frames3[idx][k], T_, 0.0, float(frames3[idx][0].max())), (x, top + head))
            y2 = top + T_ + head + mid
            if j == 0:
                text(img, (pad, y2 - 22), "bottom: one slice through the middle, run in 2-D under the same rule", 13, fill=DIM)
            img.paste(tile(frames2[idx][k], T_), (x, y2 + 6))
        out.append(img)
    media = write_media(out, folder, "three-d", fps=20, gif_width=600, gif_every=2, gif_colors=96)
    out[-1].save(folder / "three-d-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G026", "title": "Lenia in three dimensions", "media": media + ["three-d-final.png"],
        "frames": {"frames_per_tu": fpt, "mp4_fps": 20},
        "view": "top: sum along axis 0 of a 48^3 box following the 3-D centroid, scaled to the first frame's maximum per species; bottom: whole 128^2 2-D world; inferno, [0, 1]",
        "claim": ["C069", "C070"],
        "caveats": ["Species, names and seeds are Chan's (animals3D.json, pinned adfc542); the engine is ours (nd_lenia.py).",
                    "The flattening is our intervention; one plane per species is shown, all three planes are in flatten.jsonl."],
    }, runs)
    return runs


# --- G027 three-channel aquarium -------------------------------------------------------------------

@exhibit("G027")
def g027(render=True):
    import mc_knockout as MK

    film_tu = 100
    picks = list(range(12))
    runs, frames, names = [], {}, {}
    for i in picks:
        e, p, L = MK.settled(i)
        A0 = L.A.copy()
        fr = []
        for s in range(film_tu + 1):  # dt 1
            if render:
                fr.append(follow(L.A, 128).astype(np.float32))
            if s < film_tu:
                L.step()
        frames[i], names[i] = fr, e["name"].replace("**M ", "")
        runs.append({"key": f"G027:233-{i}", "rule": "found/233.json entry %d params (15 kernels, 3 channels), dt 1" % i,
                     "grid": [3, 256, 256], "boundary": "periodic", "settle_tu": MK.SETTLE, "time_units": film_tu,
                     "initial_state": f"found/233.json entry {i} ({e['code']} {e['name']}) centred, settled {MK.SETTLE} tu",
                     "initial_state_sha256": state_sha256(A0), "final_state_sha256": state_sha256(L.A)})
        print("G027", i, flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G027-three-channel-aquarium"
    T_, pad, top, head = 200, 12, 70, 24
    cols = 4
    W_ = cols * T_ + (cols + 1) * pad
    H_ = top + 3 * (T_ + head) + pad
    out = []
    for k in range(film_tu + 1):
        img = canvas(W_, H_, "A three-channel aquarium", f"Chan's 3-channel creatures; red, green, blue = channels 0, 1, 2   t = {k:3d}")
        for j, i in enumerate(picks):
            r, c = divmod(j, cols)
            x = pad + c * (T_ + pad)
            y = top + r * (T_ + head)
            text(img, (x, y + 4), names[i], 12)
            img.paste(rgb_tile(frames[i][k], T_), (x, y + head))
        out.append(img)
    media = write_media(out, folder, "aquarium", fps=10, gif_width=600, gif_every=1, gif_colors=128)
    out[-1].save(folder / "aquarium-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G027", "title": "A three-channel aquarium", "media": media + ["aquarium-final.png"],
        "frames": {"every_tu": 1, "mp4_fps": 10},
        "view": "each tile: 128x128 window following the centroid of the summed channels; channel c -> RGB component c, [0, 1] linear",
        "claim": "C071",
        "caveats": ["Every creature, name and rule is Chan's (found/233.json, pinned adfc542); our engine (nd_lenia.py) runs them.",
                    "Upstream runs these with dt 1 (params[0].T = 1), and so do we."],
    }, runs)
    return runs
