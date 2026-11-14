"""WINGS films: exhibits G022+ for the museum's new wings (worlds beyond classic 2-D Lenia).

Each exhibit rebuilds its runs from fixed seeds with the WINGS simulators (flow_lenia.py,
other_worlds.py, nd_lenia.py), renders frames, and writes media plus provenance.json into
research/gallery/exhibits/G0xx-*/. ``verify`` replays every run without rendering and compares
final-state sha256 (float64, C order) with provenance.json.

Rendering: scalar fields on matplotlib ``inferno`` (range stated per exhibit), nearest-neighbour;
multi-channel Lenia maps channels 0, 1, 2 to red, green, blue; particles are drawn as discs.

  python film_wings.py G022 [G023 ...]
  python film_wings.py verify [G022 ...]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "VIS-talk"))

from film import BG, DIM, EXHIBITS, INK, ACCENT, bar, colorize, text, write_media  # noqa: E402
from alm.provenance import code_version, state_sha256  # noqa: E402

EXHIBIT_FUNCS: dict = {}


def exhibit(gid):
    def deco(f):
        EXHIBIT_FUNCS[gid] = f
        return f
    return deco


def save_provenance(folder: Path, meta: dict, runs: list[dict], script_note: str = "") -> None:
    cv = code_version()
    meta = dict(meta)
    meta["runs"] = runs
    meta["simulator"] = {"package": "research/experiments/WINGS (flow_lenia.py, other_worlds.py, nd_lenia.py)",
                         "git_commit": cv.get("git_commit"), "git_dirty": cv.get("git_dirty")}
    meta["render"] = {"script": "research/experiments/WINGS/film_wings.py", **({"note": script_note} if script_note else {})}
    meta["reproduce"] = (f"git checkout <this commit> && .venv/bin/python research/experiments/WINGS/film_wings.py "
                         f"{meta['exhibit']}   # verify only: film_wings.py verify {meta['exhibit']}")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "provenance.json").write_text(json.dumps(meta, indent=2) + "\n")


def tile(A, size, lo=0.0, hi=1.0, cmap="inferno"):
    return Image.fromarray(colorize(A, cmap=cmap, lo=lo, hi=hi)).resize((size, size), Image.Resampling.NEAREST)


def rgb_tile(A3, size):
    """(C, H, W) with C <= 3 -> RGB image, channel c -> colour c, [0, 1] linear."""
    C, H, W = A3.shape
    rgb = np.zeros((H, W, 3))
    rgb[..., :C] = np.clip(A3[:3].transpose(1, 2, 0), 0, 1)
    return Image.fromarray((rgb * 255).round().astype(np.uint8)).resize((size, size), Image.Resampling.NEAREST)


def canvas(w, h, title, sub):
    img = Image.new("RGB", (w, h), BG)
    text(img, (14, 12), title, 24, bold=True)
    text(img, (14, 44), sub, 14, fill=DIM)
    return img


# --- G022 Flow-Lenia: conservation makes individuals ------------------------------------------

@exhibit("G022")
def g022(render=True):
    from flow_lenia import FlowLenia
    import flow_rings as FR

    steps, every = 2000, 10
    A0 = FR.patch_state(40, 0)
    arms = [("flow", True, "Flow-Lenia: matter flows, total mass fixed"),
            ("classic", False, "same kernels, classic Lenia update")]
    runs, frames, masses = [], {}, {}
    for key, cons, _ in arms:
        L = FlowLenia(FR.rule(), A0, conserve=cons)
        fr, ms = [], []
        for s in range(steps + 1):
            if render and s % every == 0:
                fr.append(L.A.astype(np.float32).copy())
                ms.append(float(L.A.sum()))
            if s < steps:
                L.step()
        frames[key], masses[key] = fr, ms
        runs.append({"key": f"G022:{key}", "rule": "FL-43 = FlowRule.random(default_rng([7, 43])) (flow_rings.rule())",
                     "rule_params": FR.rule().to_dict(), "conserve": cons, "grid": [256, 256], "boundary": "periodic",
                     "steps": steps, "time_units": steps * 0.2,
                     "initial_state": "40x40 uniform(0,1) noise from default_rng([17, 0]) centred on zero 256^2 (flow_rings.patch_state(40, 0))",
                     "initial_state_sha256": state_sha256(A0), "final_state_sha256": state_sha256(L.A)})
        print("G022", key, flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G022-conservation-makes-individuals"
    T, pad, top, head = 384, 14, 70, 44
    W = 2 * T + 3 * pad
    H = top + head + T + pad
    out = []
    for k in range(len(frames["flow"])):
        img = canvas(W, H, "Matter that cannot be destroyed",
                     f"one noise patch, one set of kernels, two update laws   t = {k * every * 0.2:5.0f}")
        for j, (key, _, label) in enumerate(arms):
            x = pad + j * (T + pad)
            text(img, (x, top), label, 14)
            text(img, (x, top + 20), f"total mass {masses[key][k]:8.1f}", 12, fill=ACCENT if key == "flow" else DIM)
            img.paste(tile(frames[key][k], T), (x, top + head))
        out.append(img)
    media = write_media(out, folder, "conservation", fps=20, gif_width=520, gif_every=2, gif_colors=96)
    out[-1].save(folder / "conservation-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G022", "title": "Matter that cannot be destroyed", "media": media + ["conservation-final.png"],
        "frames": {"every_steps": every, "dt": 0.2, "mp4_fps": 20}, "view": "whole 256^2 torus, A in [0, 1] on inferno (Flow-Lenia A can exceed 1 locally; clipped for display)",
        "claim": ["C064", "C065"],
        "caveats": ["One rule (FL-43) from a 60-rule scout; most other rules made one droplet, membrane or crystal instead (flow_scan.jsonl).",
                    "The Flow-Lenia code is our own numpy implementation from Plantec et al. 2023's equations, not the authors' code."],
    }, runs)
    return runs


# --- G023 Gray-Scott: spots that divide --------------------------------------------------------

@exhibit("G023")
def g023(render=True):
    import gs_mitosis as GM

    every = 100
    res = {}
    runs = []
    for arm in ("control", "wipe"):
        fr = [] if render else None
        G, counts, left = GM.run(arm, 0, frames=fr, frame_every=every)
        res[arm] = (fr, counts)
        u0, v0 = GM.seed_state(0)
        runs.append({"key": f"G023:{arm}", "rule": {"model": "Gray-Scott", "F": GM.F, "k": GM.K, "Du": G.Du, "Dv": G.Dv,
                     "dt": G.dt, "laplacian": "5-point", "integrator": "forward Euler"}, "grid": [GM.N, GM.N],
                     "boundary": "periodic", "steps": GM.T_END,
                     "intervention": "at t 20000 the left half (x < 128) reset to u 1, v 0" if arm == "wipe" else None,
                     "initial_state": "u 1, v 0; centre 10x10 u 0.5, v 0.25 + uniform(0, 0.01) from default_rng([11, 0]) (gs_mitosis.seed_state(0))",
                     "initial_state_sha256": state_sha256(np.stack([u0, v0])),
                     "final_state_sha256": state_sha256(np.stack([G.u, G.v]))})
        print("G023", arm, flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G023-spots-that-divide"
    T, pad, top, head = 384, 14, 70, 44
    W = 2 * T + 3 * pad
    H = top + head + T + pad
    out = []
    for k in range(len(res["control"][0])):
        t = k * every
        img = canvas(W, H, "Spots that divide", f"Gray-Scott reaction-diffusion, F 0.0367, k 0.0649   t = {t:6d}")
        for j, arm in enumerate(("control", "wipe")):
            x = pad + j * (T + pad)
            label = "untouched" if arm == "control" else ("left half wiped at t = 20000" if t >= GM.T_WIPE else "will be half wiped at t = 20000")
            text(img, (x, top), label, 14)
            n = res[arm][1][t // GM.EVERY] if t % GM.EVERY == 0 else None
            spots_now = GM.spots(res[arm][0][k])
            text(img, (x, top + 20), f"spots {spots_now:4d}", 12, fill=ACCENT)
            img.paste(tile(res[arm][0][k], T, 0.0, 0.45), (x, top + head))
        out.append(img)
    media = write_media(out, folder, "spots", fps=25, gif_width=520, gif_every=3, gif_colors=96)
    out[-1].save(folder / "spots-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G023", "title": "Spots that divide", "media": media + ["spots-final.png"],
        "frames": {"every_steps": every, "mp4_fps": 25}, "view": "whole 256^2 torus, v in [0, 0.45] on inferno",
        "claim": "C066",
        "caveats": ["Pearson (1993) mapped this regime; the dividing spots are textbook, filmed here as a specimen.",
                    "Spot = 8-connected component of v > 0.2; two touching spots during division count as one."],
    }, runs)
    return runs


# --- G024 Particle Lenia: a spinning body ------------------------------------------------------

def particle_frame(P, size, extent, color=(255, 190, 90), rad=3):
    img = Image.new("RGB", (size, size), (11, 11, 15))
    d = ImageDraw.Draw(img)
    s = size / (2 * extent)
    for x, y in P:
        px, py = (x + extent) * s, (extent - y) * s
        d.ellipse([px - rad, py - rad, px + rad, py + rad], fill=color)
    return img


@exhibit("G024")
def g024(render=True):
    import pl_rotor as PR

    keep = 50
    data, runs = {}, []
    for arm in ("control", "mirror", "cull"):
        L, spins, rg, energy, frames = PR.run(arm, 0, keep_every=keep if render else None)
        data[arm] = (frames, spins)
        runs.append({"key": f"G024:{arm}", "rule": {"model": "Particle Lenia", "mu_k": L.mu_k, "sigma_k": L.sigma_k, "w_k": L.w_k,
                     "mu_g": L.mu_g, "sigma_g": L.sigma_g, "c_rep": L.c_rep, "dt": L.dt}, "particles": 200,
                     "steps": int(PR.TU_END / L.dt),
                     "intervention": {"mirror": "x -> -x at t 1000", "cull": "50 particles removed at t 1000 (default_rng([23, 0]))"}.get(arm),
                     "initial_state": "200 particles uniform in [-6, 6]^2 from default_rng([19, 0])",
                     "initial_state_sha256": state_sha256(PR.start(0)), "final_state_sha256": state_sha256(L.P)})
        print("G024", arm, flush=True)
    if not render:
        return runs
    folder = EXHIBITS / "G024-particle-pinwheel"
    T, pad, top, head = 300, 14, 70, 44
    W = 3 * T + 4 * pad
    H = top + head + T + pad
    labels = {"control": "untouched", "mirror": "mirrored at t = 1000", "cull": "50 of 200 removed at t = 1000"}
    out = []
    n = len(data["control"][0])
    for k in range(n):
        t = (k + 1) * keep * 0.1
        img = canvas(W, H, "A pinwheel made of particles", f"Particle Lenia, 200 particles, default parameters   t = {t:6.0f}")
        for j, arm in enumerate(("control", "mirror", "cull")):
            x = pad + j * (T + pad)
            text(img, (x, top), labels[arm], 14)
            win = min(int(t // PR.WIN), len(data[arm][1]) - 1)
            sp = data[arm][1][win - 1] if win >= 1 else 0.0
            text(img, (x, top + 20), f"spin {sp:+.3f} rad / 100 t", 12, fill=ACCENT)
            P = data[arm][0][k]
            c = P.mean(0)
            img.paste(particle_frame(P - c, T, 13.0), (x, top + head))
        out.append(img)
    media = write_media(out, folder, "pinwheel", fps=25, gif_width=600, gif_every=4, gif_colors=64)
    out[-1].save(folder / "pinwheel-final.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G024", "title": "A pinwheel made of particles", "media": media + ["pinwheel-final.png"],
        "frames": {"every_steps": keep, "dt": 0.1, "mp4_fps": 25},
        "view": "particles as discs, each tile centred on its own particle centroid, half-width 13 units",
        "claim": "C067",
        "caveats": ["Rotating bodies at these parameters are shown in Mordvintsev et al. 2022; ours is an independent numpy re-implementation."],
    }, runs)
    return runs


def _load_more():
    for p in sorted(HERE.glob("ex_wings_*.py")):
        __import__(p.stem)


def verify(gids):
    bad = 0
    for gid in gids:
        folder = next(EXHIBITS.glob(f"{gid}-*"))
        prov = json.loads((folder / "provenance.json").read_text())
        got = {r["key"]: r["final_state_sha256"] for r in EXHIBIT_FUNCS[gid](render=False)}
        for rec in prov["runs"]:
            ok = got.get(rec["key"]) == rec["final_state_sha256"]
            bad += not ok
            print(f"{gid} {rec['key']}: {'OK' if ok else 'MISMATCH'}", flush=True)
    return 1 if bad else 0


def main(argv):
    sys.modules.setdefault("film_wings", sys.modules[__name__])
    _load_more()
    if argv[:1] == ["verify"]:
        return verify(argv[1:] or sorted(EXHIBIT_FUNCS))
    for gid in argv:
        EXHIBIT_FUNCS[gid](render=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
