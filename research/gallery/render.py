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

import galspec  # noqa: E402
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


SUBJECTS = [
    Subject("S001", "glides", "Orbium (O2u)"),
    Subject("S101", "glides as a bound pair", "bound Orbium pair"),
    Subject("S102", "circles", "circler"),
    Subject("S103", "holds still", "static ring"),
]


# --- collection -------------------------------------------------------------------------------

def collect() -> None:
    galspec.ensure_registered()
    runs = {}
    for s in SUBJECTS:
        cfg = almrun.RunConfig(specimen=s.specimen, steps=STEPS, every=EVERY)
        res = almrun.run(cfg)
        runs[s.specimen] = res.run_id
        print(f"{s.specimen}: {res.run_id} final {res.manifest['final_state_sha256'][:12]}")
    RUNS_JSON.write_text(json.dumps(runs, indent=2) + "\n")


# --- replay -----------------------------------------------------------------------------------

@dataclass
class Replay:
    run_id: str
    manifest: dict
    rule: Rule
    frames: dict[int, np.ndarray]  # step -> state, for the requested steps
    centroids: np.ndarray  # (steps + 1, 2) wrapped periodic centroid (cx, cy) per step


def replay(run_id: str, keep: set[int]) -> Replay:
    """Re-run ``run_id`` from its manifest, keeping states at ``keep``; verify the final hash."""
    man = json.loads((TRACES / run_id / "manifest.json").read_text())
    cfg = man["config"]
    if cfg["interventions"]:
        raise ValueError(f"{run_id}: replay of intervention runs is not implemented")
    spec = specimens.load(cfg["specimen"])
    if spec.cells_sha256 != man["specimen"]["cells_sha256_int16le"]:
        raise ValueError(f"{run_id}: specimen cells differ from the run's")
    rule = Rule(**{k: v for k, v in man["rule"].items() if k != "dt"})
    A0 = spec.place(cfg["size"])
    if provenance.state_sha256(A0) != man["initial_state_sha256"]:
        raise ValueError(f"{run_id}: initial state differs from the run's")
    sim = Lenia(rule, A0)
    n = man["timestep"]["steps"]
    frames, cents = {}, np.empty((n + 1, 2))
    for t in range(n + 1):
        if t > 0:
            sim.step()
        cents[t] = measure.periodic_centroid(sim.A)
        if t in keep:
            frames[t] = sim.A.copy()
    final = provenance.state_sha256(sim.A)
    if final != man["final_state_sha256"]:
        raise ValueError(f"{run_id}: replay final sha256 {final} != manifest {man['final_state_sha256']}")
    return Replay(run_id, man, rule, frames, cents)


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
    if r.manifest["specimen"]["id"] in galspec.PR11:
        cmd = cmd.replace("python -m alm.run", "python research/gallery/run_specimen.py", 1)
    return f"git checkout {r.manifest['simulator']['git_commit'][:12]} && .venv/bin/{cmd}"


def write_video(frames: list, path_gif: Path, path_mp4: Path | None, fps: int) -> None:
    from PIL import Image

    pal = [f.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for f in frames]
    pal[0].save(path_gif, save_all=True, append_images=pal[1:], duration=int(1000 / fps), loop=0,
                optimize=True, disposal=1)
    if path_mp4 is None or shutil.which("ffmpeg") is None:
        return
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
    write_video(out, folder / "four-ways.gif", folder / "four-ways.mp4", fps)
    out[-1].save(folder / "four-ways-final.png")
    save_provenance(folder, {
        "exhibit": "G001",
        "title": "Four ways to move",
        "media": ["four-ways.gif", "four-ways.mp4", "four-ways-final.png"],
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


def render() -> None:
    galspec.ensure_registered()
    runs = json.loads(RUNS_JSON.read_text())
    keep = set(range(WINDOW[0], WINDOW[1] + 1))
    reps = {}
    for s in SUBJECTS:
        reps[s.specimen] = replay(runs[s.specimen], keep)
        print(f"{s.specimen}: replay of {runs[s.specimen]} matches its final_state_sha256")
    g001_four_ways(reps)
    g002_portraits(reps)
    g003_contact_sheet(reps)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=["collect", "render"])
    a = ap.parse_args(argv)
    {"collect": collect, "render": render}[a.what]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
