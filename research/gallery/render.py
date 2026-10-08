"""Build the gallery's exhibits from simulator runs.

    .venv/bin/python research/gallery/render.py collect   # run the simulator, record run IDs
    .venv/bin/python research/gallery/render.py render    # replay those runs, draw the exhibits

``collect`` runs ``alm.run`` for every subject (writing ``research/traces/<run_id>/`` as usual)
and records the run IDs in ``runs.json``. ``render`` never trusts a cached picture: it replays
each recorded run from its manifest (specimen cells, rule, grid), keeps the frames it needs,
and refuses to draw unless the replay's final state hashes to the manifest's
``final_state_sha256``. Every exhibit gets a ``provenance.json`` next to its media.

Rendering method (shared by all exhibits; see README "How the pictures are made"):

- one image pixel block = one simulation cell (nearest-neighbour upscaling, no smoothing);
- cell value A in [0, 1] maps linearly onto the colormap; no gamma, no contrast stretch;
- crops are integer periodic shifts (np.roll) of the torus, so geometry is untouched;
- overlays (centroid trail, scale bar, labels) are drawn on top and listed per exhibit.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import galintervene  # noqa: E402
from alm import interventions as ivs  # noqa: E402
from alm import measure, provenance, specimens  # noqa: E402
from alm import run as almrun  # noqa: E402
from alm.lenia import Lenia, Rule  # noqa: E402

EXHIBITS = HERE / "exhibits"
RUNS_JSON = HERE / "runs.json"
TRACES = specimens.REPO_ROOT / "research" / "traces"

CMAP = "inferno"
FONT_DIR = Path(__import__("matplotlib").get_data_path()) / "fonts" / "ttf"

# The four subjects of the introductory gallery. Behaviour words are what the camera shows,
# not classifications; names are the registered specimen names, never nicknames.
STEPS, EVERY = 3000, 10
WINDOW = (2600, 3000)  # animation window (steps); the run's last 40 time units


@dataclass(frozen=True)
class Subject:
    specimen: str
    label: str  # short behaviour word for panel captions
    name: str  # display name, taken from the specimen registry / ledger


# G004: Lane 4's I004 port injury, same strength, on the bound pair and on a single Orbium
# (ledger C041). Both runs settle for G4_T0 steps first, as in L6-005.
G4_STEPS, G4_T0, G4_S = 5000, 3000, 0.25
G4_SUBJECTS = [("S101", "bound Orbium pair"), ("S001", "Orbium (O2u)")]

# G005: the circler under the same cut one and two steps apart (ledger C040). Lane 6's L6-005
# heading (10-step chord) and phases t0 = 3000 and 3002; Lane 6 saw circler -> S103 only at 3002.
G5_STEPS, G5_T0S, G5_S = 5002, (3000, 3002), 0.25

# G006: the circler from twin starts (Lane 7 HR-009 E1 recipe, our own seeds): the unperturbed
# seed plus G6_RUNS - 1 copies with noise of size G6_DELTA on the creature's support, all run for
# G6_STEPS (5000 tu, the horizon of L6-007's follow-up and HR-009 E1). Seeds 1..G6_RUNS-1 in order;
# none is chosen by outcome.
G6_STEPS, G6_RUNS, G6_DELTA = 50000, 12, 1e-12
G6_FILM_STRIDE = 100  # film samples every 10 tu: a stroboscopic view, see the exhibit's disclosures
G6_DEAD = 0.01  # "gone": total mass / R^2 below this (L6-007 follow-up and HR-009 E1 threshold)

SUBJECTS = [
    Subject("S001", "glides", "Orbium (O2u)"),
    Subject("S101", "glides as a bound pair", "bound Orbium pair"),
    Subject("S102", "circles", "circler"),
    Subject("S103", "holds still", "static ring"),
]


# --- collection -------------------------------------------------------------------------------

def run_configs() -> dict[str, almrun.RunConfig]:
    """Every run the gallery shows, keyed as in runs.json."""
    cfgs = {s.specimen: almrun.RunConfig(specimen=s.specimen, steps=STEPS, every=EVERY) for s in SUBJECTS}
    for sid, _ in G4_SUBJECTS:
        cfgs[f"G004:{sid}"] = almrun.RunConfig(
            specimen=sid, steps=G4_STEPS, every=EVERY,
            interventions=[(G4_T0, galintervene.GalleryPortInjury(s=G4_S))],
        )
    for t0 in G5_T0S:
        hx, hy = galintervene.chord_heading("S102", t0)
        cfgs[f"G005:S102@{t0}"] = almrun.RunConfig(
            specimen="S102", steps=G5_STEPS, every=EVERY,
            interventions=[(t0, galintervene.GalleryPortInjuryH(s=G5_S, hx=hx, hy=hy))],
        )
    for k in range(G6_RUNS):
        cfgs[f"G006:S102#{k}"] = almrun.RunConfig(
            specimen="S102", steps=G6_STEPS, every=EVERY, seed=k,
            interventions=[(0, galintervene.GalleryTinyNoise(delta=G6_DELTA))] if k else [],
        )
    return cfgs


def collect() -> None:
    """Run every configuration not yet recorded in runs.json (recorded runs are kept)."""
    runs = json.loads(RUNS_JSON.read_text()) if RUNS_JSON.exists() else {}
    for key, cfg in run_configs().items():
        if key in runs and (TRACES / runs[key] / "manifest.json").exists():
            continue
        res = almrun.run(cfg, out_root=TRACES)
        runs[key] = res.run_id
        print(f"{key}: {res.run_id} final {res.manifest['final_state_sha256'][:12]}")
    RUNS_JSON.write_text(json.dumps(runs, indent=2) + "\n")


# --- replay -----------------------------------------------------------------------------------

@dataclass
class Replay:
    run_id: str
    manifest: dict
    rule: Rule
    frames: dict[int, np.ndarray]  # step -> state, for the requested steps
    edits: dict[int, tuple[np.ndarray, np.ndarray]]  # step -> (pre, post) of each intervention
    centroids: np.ndarray  # (steps + 1, 2) wrapped periodic centroid (cx, cy) per step
    mass: np.ndarray  # (steps + 1,) total mass / R^2 per step


def replay(run_id: str, keep: set[int]) -> Replay:
    """Re-run ``run_id`` from its manifest, keeping states at ``keep``; verify the final hash."""
    man = json.loads((TRACES / run_id / "manifest.json").read_text())
    cfg = man["config"]
    schedule: dict[int, list] = {}
    for iv in cfg["interventions"]:
        schedule.setdefault(iv["step"], []).append(ivs.make(iv["name"], **iv["params"]))
    rng = np.random.default_rng(cfg["seed"])
    spec = specimens.load(cfg["specimen"])
    if spec.cells_sha256 != man["specimen"]["cells_sha256_int16le"]:
        raise ValueError(f"{run_id}: specimen cells differ from the run's")
    rule = Rule(**{k: v for k, v in man["rule"].items() if k != "dt"})
    A0 = spec.place(cfg["size"])
    if provenance.state_sha256(A0) != man["initial_state_sha256"]:
        raise ValueError(f"{run_id}: initial state differs from the run's")
    sim = Lenia(rule, A0)
    n = man["timestep"]["steps"]
    frames, edits, cents, mass = {}, {}, np.empty((n + 1, 2)), np.empty(n + 1)
    for t in range(n + 1):
        if t > 0:
            sim.step()
        for iv in schedule.get(t, []):  # as alm.run: after the step, then re-clip
            pre = sim.A.copy()
            sim.A = np.clip(np.asarray(iv.apply(pre.copy(), sim, rng), dtype=np.float64), 0.0, 1.0)
            edits[t] = (pre, sim.A.copy())
        cents[t] = measure.periodic_centroid(sim.A)
        mass[t] = sim.A.sum() / rule.R**2
        if t in keep:
            frames[t] = sim.A.copy()
    final = provenance.state_sha256(sim.A)
    if final != man["final_state_sha256"]:
        raise ValueError(f"{run_id}: replay final sha256 {final} != manifest {man['final_state_sha256']}")
    return Replay(run_id, man, rule, frames, edits, cents, mass)


# --- drawing primitives -----------------------------------------------------------------------

def _lut() -> np.ndarray:
    import matplotlib

    return (matplotlib.colormaps[CMAP](np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)


LUT = None


def colorize(A: np.ndarray, scale: int) -> np.ndarray:
    """RGB uint8 image of A, linear value -> colormap, each cell a scale x scale block."""
    global LUT
    if LUT is None:
        LUT = _lut()
    idx = np.rint(np.clip(A, 0, 1) * 255).astype(np.uint8)
    rgb = LUT[idx]
    return np.repeat(np.repeat(rgb, scale, axis=0), scale, axis=1)


def centred(A: np.ndarray, c: tuple[float, float], size: int) -> np.ndarray:
    """size x size crop of the torus with cell (round(cx), round(cy)) at the centre."""
    ny, nx = A.shape
    sx = nx // 2 - int(round(c[0])) % nx
    sy = ny // 2 - int(round(c[1])) % ny
    B = np.roll(np.roll(A, sy, axis=0), sx, axis=1)
    y0, x0 = (ny - size) // 2, (nx - size) // 2
    return B[y0 : y0 + size, x0 : x0 + size]


def font(size: int, bold: bool = False):
    from PIL import ImageFont

    return ImageFont.truetype(str(FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


BG = (12, 10, 18)
INK = (236, 230, 220)
DIM = (150, 144, 140)
TRAIL = (120, 220, 255)


def draw_trail(img, pts: np.ndarray, scale: int, n: int, width: int = 2) -> None:
    """Fading polyline through wrapped centroid points; breaks where the torus wraps."""
    from PIL import ImageDraw

    d = ImageDraw.Draw(img, "RGBA")
    m = len(pts)
    for i in range(1, m):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        if abs(x1 - x0) > n / 2 or abs(y1 - y0) > n / 2:
            continue
        a = int(15 + 105 * i / m)
        d.line([((x0 + 0.5) * scale, (y0 + 0.5) * scale), ((x1 + 0.5) * scale, (y1 + 0.5) * scale)],
               fill=(*TRAIL, a), width=width)


def scale_bar(img, R: int, scale: int, xy: tuple[int, int], label: str = "R") -> None:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    x, y = xy
    d.rectangle([x, y, x + R * scale, y + 3], fill=INK)
    d.text((x, y + 6), f"{label} = {R} cells", fill=INK, font=font(12))


def save_provenance(folder: Path, exhibit: dict, replays: list[Replay]) -> None:
    exhibit = dict(exhibit)
    exhibit["sources"] = [
        {
            "specimen": r.manifest["specimen"]["id"],
            "specimen_name": r.manifest["specimen"]["name"],
            "specimen_source": r.manifest["specimen"]["source"],
            "run_id": r.run_id,
            "trace": f"research/traces/{r.run_id}/",
            "rule": r.manifest["rule"],
            "grid": r.manifest["grid"],
            "integrator": r.manifest["integrator"],
            "simulator_commit": r.manifest["simulator"]["git_commit"],
            "final_state_sha256": r.manifest["final_state_sha256"],
            "replay_verified": True,
            "reproduce_run": _run_command(r),
        }
        for r in replays
    ]
    exhibit["render"] = {
        "script": "research/gallery/render.py render",
        "colormap": f"matplotlib {CMAP}, A in [0,1] mapped linearly",
        "upscaling": "nearest neighbour (one block per cell)",
    }
    (folder / "provenance.json").write_text(json.dumps(exhibit, indent=2) + "\n")


def _run_command(r: Replay) -> str:
    cmd = r.manifest["reproduction"]["command"]
    gallery_ivs = any(iv["name"].startswith("gallery_") for iv in r.manifest["config"]["interventions"])
    # Runs made from the pre-#11 vendored seeds need the wrapper at their own commit.
    vendored = "research/gallery/vendor/" in r.manifest["specimen"]["source"]
    if gallery_ivs or vendored:
        cmd = cmd.replace("python -m alm.run", "python research/gallery/run_specimen.py", 1)
    return f"git checkout {r.manifest['simulator']['git_commit'][:12]} && .venv/bin/{cmd}"


def write_video(frames: list, path_gif: Path, path_mp4: Path | None, fps: int) -> bool:
    """Write the GIF, and the MP4 when ffmpeg is available; True if the MP4 was written."""
    from PIL import Image

    pal = [f.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for f in frames]
    pal[0].save(path_gif, save_all=True, append_images=pal[1:], duration=int(1000 / fps), loop=0,
                optimize=True, disposal=1)
    if path_mp4 is None or shutil.which("ffmpeg") is None:
        return False
    w, h = frames[0].size
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
         "-r", str(fps), "-i", "-", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264",
         "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(path_mp4)],
        stdin=subprocess.PIPE,
    )
    for f in frames:
        proc.stdin.write(f.convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    return True


# --- exhibits ---------------------------------------------------------------------------------

def g001_four_ways(reps: dict[str, Replay]) -> None:
    """G001: the four subjects side by side on their full 128 x 128 torus, same clock."""
    from PIL import Image, ImageDraw

    folder = EXHIBITS / "G001-four-ways-to-move"
    folder.mkdir(parents=True, exist_ok=True)
    scale, stride, trail_steps, fps = 2, 2, 300, 20
    n = 128
    pw, head = n * scale, 46
    gap = 6
    W, H = 2 * pw + 3 * gap, 2 * (pw + head) + 3 * gap + 22
    steps = list(range(WINDOW[0], WINDOW[1] + 1, stride))
    out = []
    for t in steps:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for k, s in enumerate(SUBJECTS):
            r = reps[s.specimen]
            x0 = gap + (k % 2) * (pw + gap)
            y0 = gap + (k // 2) * (pw + head + gap)
            d.text((x0, y0 + 2), f"{s.specimen}  {s.label}", fill=INK, font=font(15, True))
            d.text((x0, y0 + 23), f"{s.name} · μ {r.rule.mu:g}  σ {r.rule.sigma:g}", fill=DIM,
                   font=font(12))
            panel = Image.fromarray(colorize(r.frames[t], scale))
            lo = max(0, t - trail_steps)
            draw_trail(panel, r.centroids[lo : t + 1], scale, n)
            img.paste(panel, (x0, y0 + head))
        d.text((gap, H - 20), f"t = {t / 10:6.1f} time units (step {t})   ·   R = 13 cells   ·   "
               f"blue line: centroid, last {trail_steps // 10} tu", fill=DIM, font=font(12))
        out.append(img)
    mp4 = write_video(out, folder / "four-ways.gif", folder / "four-ways.mp4", fps)
    out[-1].save(folder / "four-ways-final.png")
    save_provenance(folder, {
        "exhibit": "G001",
        "title": "Four ways to move",
        "media": ["four-ways.gif"] + (["four-ways.mp4"] if mp4 else []) + ["four-ways-final.png"],
        "frames": {"steps": [steps[0], steps[-1]], "stride_steps": stride, "count": len(steps),
                   "playback_fps": fps, "time_compression": f"{fps * stride / 10:g} time units per second"},
        "view": "full 128x128 periodic world, fixed camera, no crop; 2x nearest-neighbour",
        "overlays": [f"centroid trail over the last {trail_steps} steps (periodic circular-mean centroid, "
                     "computed every step of the replay)", "text labels"],
        "disclosures": ["the four panels use two different rules: S001/S101 the S001 rule, "
                        "S102/S103 the coexistence rule mu 0.155 sigma 0.020",
                        "GIF palette reduced to 128 colours; the MP4 is H.264 (lossy)"],
    }, [reps[s.specimen] for s in SUBJECTS])


def g002_portraits(reps: dict[str, Replay]) -> None:
    """G002: one still portrait per subject at the run's final step, centred on its centroid."""
    from PIL import Image, ImageDraw

    folder = EXHIBITS / "G002-portraits"
    folder.mkdir(parents=True, exist_ok=True)
    size, scale = 64, 8
    t = WINDOW[1]
    media = []
    for s in SUBJECTS:
        r = reps[s.specimen]
        A = r.frames[t]
        c = r.centroids[t]
        img = Image.fromarray(colorize(centred(A, c, size), scale))
        foot = Image.new("RGB", (img.width, 64), BG)
        d = ImageDraw.Draw(foot)
        d.text((12, 8), f"{s.specimen} · {s.name}", fill=INK, font=font(17, True))
        d.text((12, 34), f"step {t} (t = {t / 10:g} tu) · run {r.run_id} · μ {r.rule.mu:g} σ {r.rule.sigma:g}",
               fill=DIM, font=font(12))
        canvas = Image.new("RGB", (img.width, img.height + foot.height), BG)
        canvas.paste(img, (0, 0))
        canvas.paste(foot, (0, img.height))
        scale_bar(canvas, r.rule.R, scale, (16, img.height - 34))
        name = f"{s.specimen}-portrait.png"
        canvas.save(folder / name, optimize=True)
        media.append(name)
    save_provenance(folder, {
        "exhibit": "G002",
        "title": "Portraits",
        "media": media,
        "frames": {"step": t},
        "view": f"{size}x{size}-cell window of the torus, shifted by whole cells so the periodic "
                f"centroid sits at the centre; {scale}x nearest-neighbour",
        "overlays": ["scale bar of one kernel radius R", "caption strip"],
        "disclosures": [],
    }, [reps[s.specimen] for s in SUBJECTS])


def g003_contact_sheet(reps: dict[str, Replay]) -> None:
    """G003: eight poses per subject, half a time unit apart (about one circler lap), camera following."""
    from PIL import Image, ImageDraw

    folder = EXHIBITS / "G003-contact-sheet"
    folder.mkdir(parents=True, exist_ok=True)
    size, scale, cols, dstep = 48, 3, 8, 5
    t0 = WINDOW[1] - dstep * (cols - 1)
    cell = size * scale
    left, top, gap = 190, 30, 4
    W = left + cols * (cell + gap)
    H = top + len(SUBJECTS) * (cell + gap) + 26
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for j in range(cols):
        t = t0 + j * dstep
        d.text((left + j * (cell + gap) + 4, 8), f"t = {t / 10:g}", fill=DIM, font=font(12))
    for i, s in enumerate(SUBJECTS):
        r = reps[s.specimen]
        y = top + i * (cell + gap)
        d.text((10, y + 8), s.specimen, fill=INK, font=font(16, True))
        d.text((10, y + 30), s.name, fill=DIM, font=font(12))
        d.text((10, y + 48), s.label, fill=DIM, font=font(12))
        for j in range(cols):
            t = t0 + j * dstep
            tile = Image.fromarray(colorize(centred(r.frames[t], r.centroids[t], size), scale))
            img.paste(tile, (left + j * (cell + gap), y))
    d.text((10, H - 20), f"each tile: {size}x{size} cells centred on the creature's centroid "
           f"(camera follows) · columns {dstep / 10:g} time units apart", fill=DIM, font=font(12))
    img.save(folder / "contact-sheet.png", optimize=True)
    save_provenance(folder, {
        "exhibit": "G003",
        "title": "Contact sheet: half a time unit at a time",
        "media": ["contact-sheet.png"],
        "frames": {"steps": [t0 + j * dstep for j in range(cols)]},
        "view": f"{size}x{size}-cell windows, each shifted by whole cells to centre the centroid "
                f"(the camera follows, so travel is hidden; G001 shows travel); {scale}x nearest-neighbour",
        "overlays": ["text labels"],
        "disclosures": ["camera follows the centroid in every tile"],
    }, [reps[s.specimen] for s in SUBJECTS])


REMOVED = (213, 94, 0)  # Lane 9's "mass removed" vermillion, #D55E00


def _ffill(cents: np.ndarray) -> np.ndarray:
    """Centroids with NaN (empty world) replaced by the last defined one, so the camera stays put."""
    out = cents.copy()
    for t in range(1, len(out)):
        if np.isnan(out[t, 0]):
            out[t] = out[t - 1]
    return out


def _tint_removed(img_rgb: np.ndarray, pre: np.ndarray, post: np.ndarray, scale: int) -> np.ndarray:
    """Overlay cells the edit emptied, in vermillion with opacity = mass removed from that cell."""
    lost = np.clip(pre - post, 0, 1)
    a = np.repeat(np.repeat(lost, scale, 0), scale, 1)[..., None]
    a = np.where(a > 0, 0.35 + 0.65 * a, 0.0)
    return (img_rgb * (1 - a) + np.array(REMOVED) * a).astype(np.uint8)


AFTER = (5, 20, 100, 500, 2000)  # sheet columns: 0.5, 2, 10, 50 and 200 time units after the cut


def g4_steps() -> list[int]:
    """Tile steps: the cut step twice (just before and just after the edit), then 0.5, 2, 10, 50
    and 200 time units after (capped at the run's length)."""
    return [G4_T0, G4_T0] + [G4_T0 + k for k in AFTER if G4_T0 + k <= G4_STEPS]


def _cut_steps(t0: int, n: int) -> list[int]:
    return [t0, t0] + [t0 + k for k in AFTER if t0 + k <= n]


def _film_offsets(t0: int, n: int, stride: int = 2) -> list[int]:
    return list(range(-20, min(600, n - t0) + 1, stride))


def injury_exhibit(reps, rows, folder: Path, stem: str, fate, footer: str, prov: dict) -> None:
    """Before/after sheet and film for injury runs. ``rows`` are (runs key, specimen ID, name, t0);
    each row's columns and film frames are timed from its own cut step."""
    from PIL import Image, ImageDraw

    folder.mkdir(parents=True, exist_ok=True)
    size, scale = 64, 3
    cell = size * scale
    ncols = max(len(_cut_steps(t0, reps[k].manifest["timestep"]["steps"])) for k, _, _, t0 in rows)
    left, top, gap = 200, 34, 4
    W = left + ncols * (cell + gap)
    H = top + len(rows) * (cell + gap) + 44
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    heads = ["before", "cut"] + [f"+{k / 10:g} tu" for k in AFTER][: ncols - 2]
    for j, h in enumerate(heads):
        d.text((left + j * (cell + gap) + 4, 10), h, fill=DIM, font=font(13))
    for i, (key, sid, name, t0) in enumerate(rows):
        r = reps[key]
        steps = _cut_steps(t0, r.manifest["timestep"]["steps"])
        cents = _ffill(r.centroids)
        pre, post = r.edits[t0]
        iv = r.manifest["interventions_applied"][0]
        y = top + i * (cell + gap)
        d.text((10, y + 8), sid, fill=INK, font=font(16, True))
        d.text((10, y + 30), name, fill=DIM, font=font(12))
        d.text((10, y + 48), f"{100 * (1 - iv['mass_after'] / iv['mass_before']):.1f}% of mass cut", fill=DIM,
               font=font(12))
        d.text((10, y + 66), fate(r, r.frames[steps[-1]]), fill=INK, font=font(12, True))
        for j, t in enumerate(steps):
            c = cents[t]
            if j == 0:
                rgb = colorize(centred(pre, c, size), scale)
            elif j == 1:
                rgb = _tint_removed(colorize(centred(post, c, size), scale), centred(pre, c, size),
                                    centred(post, c, size), scale)
            else:
                rgb = colorize(centred(r.frames[t], c, size), scale)
            sheet.paste(Image.fromarray(rgb), (left + j * (cell + gap), y))
    d.text((10, H - 38), "vermillion: cells the cut emptied (opacity = value removed) · each tile 64x64 cells, "
           "camera follows the centroid", fill=DIM, font=font(12))
    d.text((10, H - 20), footer, fill=DIM, font=font(12))
    sheet.save(folder / f"{stem}-sheet.png", optimize=True)

    # The film: each creature from 2 tu before its cut, camera following, clocks aligned on the cut.
    stride, fps = 2, 20
    offsets = min((_film_offsets(t0, reps[k].manifest["timestep"]["steps"], stride) for k, _, _, t0 in rows), key=len)
    pw, head = cell + 0, 40
    FW, FH = len(rows) * pw + (len(rows) + 1) * gap, pw + head + 2 * gap + 22
    out = []
    for o in offsets:
        img = Image.new("RGB", (FW, FH), BG)
        d = ImageDraw.Draw(img)
        for k, (key, sid, name, t0) in enumerate(rows):
            r = reps[key]
            t = t0 + o
            c = _ffill(r.centroids)[t]
            x0 = gap + k * (pw + gap)
            d.text((x0, gap), sid, fill=INK, font=font(14, True))
            d.text((x0, gap + 19), name, fill=DIM, font=font(11))
            rgb = colorize(centred(r.frames[t], c, size), scale)
            if o == 0:  # the cut frame shows what was removed
                pre, post = r.edits[t0]
                rgb = _tint_removed(rgb, centred(pre, c, size), centred(post, c, size), scale)
            img.paste(Image.fromarray(rgb), (x0, gap + head))
        label = ("before the cut" if o < 0 else "the cut (held 1 s; vermillion = removed)" if o == 0
                 else f"+{o / 10:.1f} tu after the cut")
        d.text((gap, FH - 20), label, fill=DIM, font=font(12))
        out.extend([img] * (fps if o == 0 else 1))
    mp4 = write_video(out, folder / f"{stem}.gif", folder / f"{stem}.mp4", fps)
    media = [f"{stem}-sheet.png", f"{stem}.gif"] + ([f"{stem}.mp4"] if mp4 else [])
    head_keys = ("exhibit", "title")
    rest = {k: v for k, v in prov.items() if k not in head_keys and k != "extra_disclosures"}
    save_provenance(folder, {
        **{k: prov[k] for k in head_keys},
        "media": media,
        "frames": {"sheet_steps": {key: _cut_steps(t0, reps[key].manifest["timestep"]["steps"])
                                   for key, _, _, t0 in rows} if len({t0 for *_, t0 in rows}) > 1
                   else _cut_steps(rows[0][3], reps[rows[0][0]].manifest["timestep"]["steps"]),
                   "sheet_note": "columns 1-2 are the state at the cut step just before "
                   "and just after the edit", **({"film_offsets_from_cut": [offsets[0], offsets[-1]]}
                   if len({t0 for *_, t0 in rows}) > 1 else
                   {"film_steps": [rows[0][3] + offsets[0], rows[0][3] + offsets[-1]]}),
                   "film_stride_steps": stride, "playback_fps": fps},
        **rest,
        "view": f"{size}x{size}-cell windows shifted by whole cells to centre the centroid (camera follows; "
                "after death the camera holds its last position); 3x nearest-neighbour",
        "overlays": ["vermillion tint on cells emptied by the cut (sheet column 'cut'; the film's cut frame), "
                     "opacity 0.35 + 0.65 x value removed", "text labels"],
        "disclosures": ["camera follows the centroid, so travel is hidden",
                        "the film holds the cut frame for one second (20 repeated frames); all other "
                        "frames are 2 steps apart",
                        "GIF palette reduced to 128 colours; the MP4 is H.264 (lossy)"] + prov.get("extra_disclosures", []),
    }, [reps[key] for key, *_ in rows])


def _orbium_fate(r, A) -> str:
    m_end = A.sum() / r.rule.R**2
    return ("dies" if m_end == 0 else "one Orbium-mass body remains" if abs(m_end / 0.4358 - 1) < 0.01
            else f"survives, mass {m_end:.3f}")


def g004_shedding(reps: dict[str, Replay]) -> None:
    """G004: the same port injury on the bound pair and on a single Orbium (C041)."""
    injury_exhibit(
        reps, [(f"G004:{sid}", sid, name, G4_T0) for sid, name in G4_SUBJECTS],
        EXHIBITS / "G004-port-injury", "port-injury", _orbium_fate,
        f"Lane 4 I004 port injury, s = {G4_S:g}, at step {G4_T0} after settling; "
        "heading by forward difference (see provenance)",
        {"exhibit": "G004", "title": "Same cut, two fates",
         "intervention": {"name": "gallery_port_injury", "lane4_id": "I004", "s": G4_S, "step": G4_T0,
                          "definition": "alm.disturb.i004_port_injury (L4-001 protocol)",
                          "heading": "forward difference over one probe step (Lane 4 uses the previous "
                                     "step's centroid); see research/gallery/galintervene.py"}},
    )


def equals_up_to_shift(A: np.ndarray, B: np.ndarray) -> bool:
    """True if A is B rolled by some whole-cell shift on the torus (exact float equality)."""
    c = np.real(np.fft.ifft2(np.fft.fft2(A) * np.conj(np.fft.fft2(B))))
    dy, dx = np.unravel_index(int(np.argmax(c)), c.shape)
    return bool(np.array_equal(np.roll(np.roll(B, dy, 0), dx, 1), A))


def _ring_fate(r, A) -> str:
    m_end = A.sum() / r.rule.R**2
    if m_end == 0:
        return "dies"
    if equals_up_to_shift(A, specimens.load("S103").place(A.shape)):
        return "becomes S103 exactly"
    return f"survives, mass {m_end:.4f}"


def g005_circler_to_ring(reps: dict[str, Replay]) -> None:
    """G005: the circler under the same port injury at two phases two steps apart (C040)."""
    rows = [(f"G005:S102@{t0}", "S102", f"circler, cut at step {t0}", t0) for t0 in G5_T0S]
    injury_exhibit(
        reps, rows, EXHIBITS / "G005-circler-to-ring", "circler-ring", _ring_fate,
        f"Lane 4 I004 port injury, s = {G5_S:g}, heading from the 10-step centroid chord (Lane 6 L6-005); "
        "same recipe, cut two steps apart",
        {"exhibit": "G005", "title": "Two steps apart",
         "intervention": {"name": "gallery_port_injury_h", "lane4_id": "I004", "s": G5_S, "steps": list(G5_T0S),
                          "definition": "alm.disturb.i004_port_injury (L4-001 protocol), frame centred on the "
                                        "periodic centroid at the cut step",
                          "heading": "unit vector of the unwrapped centroid shift over the previous 10 steps of "
                                     "the uninterrupted run, as in Lane 6's disturb_switch.py; computed by "
                                     "galintervene.chord_heading and stored in the run's intervention params"}},
    )


G6_LAST = (-500, -200, -100, -50, -20, 0)  # sheet columns: steps before the end of the life or run
G6_CROP, G6_SCALE = 64, 3


def _death_step(mass: np.ndarray) -> int | None:
    """First step whose total mass / R^2 is below G6_DEAD, or None if the run never gets there."""
    below = np.flatnonzero(mass < G6_DEAD)
    return int(below[0]) if len(below) else None


def _g6_job(run_id: str) -> dict:
    """Replay one G006 run (in a worker) and reduce it to 64x64 crops, so the 12 replays fit in memory.
    The death step is planned from the run's own series.npz and then checked against the replay."""
    n = json.loads((TRACES / run_id / "manifest.json").read_text())["timestep"]["steps"]
    planned = _death_step(np.load(TRACES / run_id / "series.npz")["mass"])
    end = planned if planned is not None else n
    film = list(range(0, n + 1, G6_FILM_STRIDE))
    last = [max(0, end + o) for o in G6_LAST]
    r = replay(run_id, set(film) | set(last))
    death = _death_step(r.mass)
    if death != planned:
        raise ValueError(f"{run_id}: replay death step {death} != recorded {planned}")
    cents = _ffill(r.centroids)
    crop = {t: centred(r.frames[t], cents[t], G6_CROP) for t in r.frames}
    return {"run_id": run_id, "manifest": r.manifest, "rule": r.rule, "death": death, "steps": n,
            "film": film, "last": last, "crops": crop, "mass": r.mass[film]}


def g006_eventually_gone(jobs: list[dict]) -> None:
    """G006: the circler from twin starts that differ by 1e-12, run to 5000 tu (HR-009 E1, L6-007)."""
    from PIL import Image, ImageDraw

    folder = EXHIBITS / "G006-eventually-gone"
    folder.mkdir(parents=True, exist_ok=True)
    cell = G6_CROP * G6_SCALE
    n = jobs[0]["steps"]
    T = jobs[0]["rule"].T
    died = [j for j in jobs if j["death"] is not None]

    def name(k: int) -> str:
        return "registered seed" if k == 0 else f"twin {k} (seed {k})"

    # The sheet: one row per run. A lifeline from 0 to the end of the life (x, Lane 9's "died") or
    # to the horizon (arrow: still above the threshold when the run stopped), then the last moments.
    th = G6_CROP * 2  # thumbnails: the central 32x32 cells at 4x
    left, line_w, gap, top = 170, 360, 4, 40
    W = left + line_w + 20 + len(G6_LAST) * (th + gap)
    H = top + len(jobs) * (th + gap) + 64
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    x_line = left
    d.text((x_line, 10), f"lifeline, 0 to {n / T:g} tu", fill=DIM, font=font(13))
    x_th = left + line_w + 20
    for c, o in enumerate(G6_LAST):
        d.text((x_th + c * (th + gap) + 4, 10), "end" if o == 0 else f"{o / T:g} tu", fill=DIM, font=font(13))
    for i, j in enumerate(jobs):
        y = top + i * (th + gap)
        mid = y + th // 2
        d.text((10, mid - 18), name(i), fill=INK, font=font(14, True))
        fate = (f"mass < {G6_DEAD:g} at {j['death'] / T:g} tu" if j["death"] is not None
                else f"still above {G6_DEAD:g} at {n / T:g} tu")
        d.text((10, mid + 2), fate, fill=DIM, font=font(11))
        end = j["death"] if j["death"] is not None else n
        xe = x_line + line_w * end / n
        d.line([(x_line, mid), (xe, mid)], fill=INK, width=3)
        if j["death"] is not None:
            d.line([(xe - 6, mid - 6), (xe + 6, mid + 6)], fill=REMOVED, width=3)
            d.line([(xe - 6, mid + 6), (xe + 6, mid - 6)], fill=REMOVED, width=3)
        else:
            d.polygon([(xe, mid - 6), (xe + 10, mid), (xe, mid + 6)], fill=(189, 189, 189))
        for c, t in enumerate(j["last"]):
            tile = Image.fromarray(colorize(j["crops"][t][G6_CROP // 4: 3 * G6_CROP // 4,
                                                          G6_CROP // 4: 3 * G6_CROP // 4], 4))
            sheet.paste(tile, (x_th + c * (th + gap), y))
    for k in range(0, int(n / T) + 1, max(1, int(n / T) // 5)):
        xk = x_line + line_w * k * T / n
        d.line([(xk, H - 58), (xk, H - 52)], fill=DIM, width=1)
        d.text((xk - 10, H - 50), f"{k:g}", fill=DIM, font=font(11))
    d.text((10, H - 32), f"{len(died)} of {len(jobs)} runs fell below mass {G6_DEAD:g} before {n / T:g} tu "
           f"(x); the rest were still above it when the run stopped (arrow). Thumbnails: 32x32 cells around "
           "the centroid, 4x; 'end' is the death step or the last step.", fill=DIM, font=font(11))
    d.text((10, H - 16), f"Twins start from the registered seed plus noise of size {G6_DELTA:g} on its support "
           "(HR-009 E1 recipe, our seeds 1-11, none chosen by outcome) · μ 0.155 σ 0.020 R 13 T 10 · "
           "128x128 torus", fill=DIM, font=font(11))
    sheet.save(folder / "lifelines-sheet.png", optimize=True)

    # The film: all runs side by side, sampled every G6_FILM_STRIDE steps, camera following.
    cols = 4
    rows = math.ceil(len(jobs) / cols)
    head = 36
    FW = cols * cell + (cols + 1) * gap
    FH = rows * (cell + head + gap) + gap + 24
    fps = 25
    out = []
    for f, t in enumerate(jobs[0]["film"]):
        img = Image.new("RGB", (FW, FH), BG)
        d = ImageDraw.Draw(img)
        for i, j in enumerate(jobs):
            x0 = gap + (i % cols) * (cell + gap)
            y0 = gap + (i // cols) * (cell + head + gap)
            d.text((x0, y0), name(i), fill=INK, font=font(13, True))
            gone = j["death"] is not None and t >= j["death"]
            d.text((x0, y0 + 17), f"mass < {G6_DEAD:g} since {j['death'] / T:g} tu" if gone
                   else f"mass {j['mass'][f]:.3f}", fill=REMOVED if gone else DIM, font=font(11))
            img.paste(Image.fromarray(colorize(j["crops"][t], G6_SCALE)), (x0, y0 + head))
        d.text((gap, FH - 20), f"t = {t / T:6.0f} tu (step {t}) · one frame every {G6_FILM_STRIDE / T:g} tu: "
               "the circler turns many times between frames", fill=DIM, font=font(12))
        out.append(img)
    out.extend([out[-1]] * fps * 2)  # hold the last frame for two seconds
    mp4 = write_video(out, folder / "eventually-gone.gif", folder / "eventually-gone.mp4", fps)
    save_provenance(folder, {
        "exhibit": "G006",
        "title": "The circler that eventually disappears",
        "status": "provisional: built while PR #27 (L6-007) and PR #30 (HR-009) are under review; the ledger "
                  "holds no claim on S102's lifetime yet",
        "media": ["lifelines-sheet.png", "eventually-gone.gif"] + (["eventually-gone.mp4"] if mp4 else []),
        "runs": [{"label": name(i), "run_id": j["run_id"], "seed": j["manifest"]["seed"],
                  "noise_delta": G6_DELTA if i else 0.0,
                  "death_step": j["death"], "death_tu": None if j["death"] is None else j["death"] / T,
                  "censored_at_step": None if j["death"] is not None else n} for i, j in enumerate(jobs)],
        "death_definition": f"first step whose total mass / R^2 is below {G6_DEAD:g}, from the replay's "
                            "per-step mass (checked against the run's series.npz)",
        "frames": {"film_stride_steps": G6_FILM_STRIDE, "film_steps": [0, n], "playback_fps": fps,
                   "film_hold_last_frame_s": 2,
                   "sheet_offsets_from_end_steps": list(G6_LAST)},
        "view": f"film: {G6_CROP}x{G6_CROP}-cell windows shifted by whole cells to centre the centroid (camera "
                f"follows; after death it holds its last position), {G6_SCALE}x nearest-neighbour; sheet "
                f"thumbnails: the central 32x32 cells of the same windows, 4x",
        "overlays": ["lifeline bars, Lane 9 'died' x marker (#D55E00) and a grey arrow for runs still above the "
                     "threshold at the horizon", "per-tile mass readout", "text labels"],
        "disclosures": [
            "the film samples one frame every 10 tu; the circler turns about 95 degrees per tu, so its pose "
            "between frames is not continuous motion",
            "twins are our own draws of HR-009's recipe (noise U(-1,1) x 1e-12 on cells within 3 of the "
            "seed's support) in alm.lenia; they are not HR-009's or Lane 6's runs, and their death times "
            "are not expected to match those runs'",
            "12 runs show spread, not a lifetime distribution; HR-009 pools 37 runs",
            "GIF palette reduced to 128 colours; the MP4 is H.264 (lossy)",
        ],
        "sources_of_interpretation": {
            "L6-007 follow-up": "PR #27 @ 3ccb804, research/experiments/L6-007-attractor-geography/",
            "HR-009 E1": "PR #30 @ 9fc48b4, research/reports/hostile-review.md and "
                         "research/experiments/HR009-l6-review/e1.csv",
        },
    }, [_Src(j) for j in jobs])


class _Src:
    """The parts of a Replay that save_provenance reads, for runs reduced in a worker."""

    def __init__(self, job: dict):
        self.run_id, self.manifest = job["run_id"], job["manifest"]


def render() -> None:
    runs = json.loads(RUNS_JSON.read_text())
    keep = set(range(WINDOW[0], WINDOW[1] + 1))
    reps = {}
    for s in SUBJECTS:
        reps[s.specimen] = replay(runs[s.specimen], keep)
        print(f"{s.specimen}: replay of {runs[s.specimen]} matches its final_state_sha256")
    g001_four_ways(reps)
    g002_portraits(reps)
    g003_contact_sheet(reps)
    g4 = {}
    keep4 = set(g4_steps()) | set(range(G4_T0 - 20, min(G4_T0 + 600, G4_STEPS) + 1))
    for sid, _ in G4_SUBJECTS:
        g4[f"G004:{sid}"] = replay(runs[f"G004:{sid}"], keep4)
        print(f"G004:{sid}: replay of {runs[f'G004:{sid}']} matches its final_state_sha256")
    g004_shedding(g4)
    g5 = {}
    for t0 in G5_T0S:
        key = f"G005:S102@{t0}"
        n = G5_STEPS
        g5[key] = replay(runs[key], set(_cut_steps(t0, n)) | {t0 + o for o in _film_offsets(t0, n)})
        print(f"{key}: replay of {runs[key]} matches its final_state_sha256")
    g005_circler_to_ring(g5)
    from multiprocessing import Pool

    keys = [f"G006:S102#{k}" for k in range(G6_RUNS)]
    with Pool(min(4, len(keys))) as pool:
        jobs = pool.map(_g6_job, [runs[k] for k in keys])
    for k, j in zip(keys, jobs):
        print(f"{k}: replay of {j['run_id']} matches its final_state_sha256")
    g006_eventually_gone(jobs)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=["collect", "render"])
    a = ap.parse_args(argv)
    {"collect": collect, "render": render}[a.what]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
