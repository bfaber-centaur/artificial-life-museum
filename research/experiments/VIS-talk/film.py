"""VIS-talk films: deterministic simulations rendered for a projector.

Each exhibit is a function that builds an exact initial state, runs ``alm.lenia.Lenia`` (the ALM
simulator, unchanged), keeps frames, and writes media plus ``provenance.json`` into
``research/gallery/exhibits/G0xx-*/``. Every provenance file records the rule, world, initial
and final state sha256 (``alm.provenance.state_sha256``) and the command. ``verify`` re-runs the
simulation without rendering and fails unless every final hash matches.

Rendering rules (same as the gallery, research/gallery/README.md): A in [0, 1] mapped linearly
onto matplotlib ``inferno``, nearest-neighbour upscaling, no smoothing; text and the white
scale bars are overlays. G011's growth panel is signed and uses ``RdBu_r`` (disclosed there).

Usage:
  python film.py G008 [G009 ...]     render exhibits
  python film.py verify [G008 ...]   replay and compare final hashes with provenance.json
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from alm import rle, specimens  # noqa: E402
from alm.lenia import Lenia, Rule, growth  # noqa: E402
from alm.measure import periodic_centroid  # noqa: E402
from alm.provenance import code_version, state_sha256  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = specimens.REPO_ROOT
EXHIBITS = REPO / "research" / "gallery" / "exhibits"
FONT_DIR = Path(__import__("matplotlib").get_data_path()) / "fonts" / "ttf"
BG = (12, 10, 18)
INK = (236, 230, 220)
DIM = (150, 144, 140)
ACCENT = (120, 220, 255)

S001_RULE = Rule(R=13, T=10, mu=0.15, sigma=0.015)
COEX_RULE = Rule(R=13, T=10, mu=0.155, sigma=0.020)


# --- drawing ------------------------------------------------------------------------------------

_LUTS: dict[str, np.ndarray] = {}


def lut(name: str = "inferno") -> np.ndarray:
    if name not in _LUTS:
        import matplotlib

        _LUTS[name] = (matplotlib.colormaps[name](np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)
    return _LUTS[name]


def colorize(A: np.ndarray, scale: int = 1, cmap: str = "inferno", lo: float = 0.0, hi: float = 1.0) -> np.ndarray:
    idx = np.rint(np.clip((A - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
    rgb = lut(cmap)[idx]
    if scale > 1:
        rgb = np.repeat(np.repeat(rgb, scale, axis=0), scale, axis=1)
    return rgb


def font(size: int, bold: bool = False):
    from PIL import ImageFont

    return ImageFont.truetype(str(FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


def text(img, xy, s, size=16, fill=INK, bold=False, anchor="la"):
    from PIL import ImageDraw

    ImageDraw.Draw(img).text(xy, s, fill=fill, font=font(size, bold), anchor=anchor)


def bar(img, cells: int, scale: float, xy, label: str, size=14):
    from PIL import ImageDraw

    x, y = xy
    ImageDraw.Draw(img).rectangle([x, y, x + int(round(cells * scale)), y + 3], fill=INK)
    text(img, (x, y + 7), label, size=size)


def write_media(frames: list, folder: Path, stem: str, fps: int, gif_width: int | None = None,
                gif_every: int = 1, gif_colors: int = 128, crf: int = 20) -> list[str]:
    """MP4 (H.264, full size) and a looping GIF (optionally downsized / decimated)."""
    from PIL import Image

    folder.mkdir(parents=True, exist_ok=True)
    out = []
    w, h = frames[0].size
    mp4 = folder / f"{stem}.mp4"
    proc = subprocess.Popen(
        [shutil.which("ffmpeg") or "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), "-preset", "slow", "-movflags", "+faststart",
         str(mp4)], stdin=subprocess.PIPE)
    for f in frames:
        proc.stdin.write(f.convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    out.append(mp4.name)
    gf = frames[::gif_every]
    if gif_width and gif_width < w:
        gh = int(round(h * gif_width / w))
        gf = [f.resize((gif_width, gh), Image.Resampling.LANCZOS) for f in gf]
    pal = [f.convert("P", palette=Image.Palette.ADAPTIVE, colors=gif_colors) for f in gf]
    gif = folder / f"{stem}.gif"
    pal[0].save(gif, save_all=True, append_images=pal[1:], duration=int(1000 * gif_every / fps), loop=0,
                optimize=True, disposal=1)
    out.append(gif.name)
    return out


# --- simulation records -------------------------------------------------------------------------

@dataclass
class Run:
    key: str
    rule: Rule
    A0: np.ndarray
    steps: int
    built: str  # how the initial state was made, in words
    keep_every: int = 1
    keep_from: int = 0
    frames: dict = field(default_factory=dict)
    mass: list = field(default_factory=list)
    final_sha: str = ""
    init_sha: str = ""
    make_sim: object = None  # optional factory A0 -> simulator with .A and .step() (G014+ field rules)
    rule_note: str = ""  # how the rule departs from `rule`, if it does

    def go(self, record=True, on_step=None) -> "Run":
        self.init_sha = state_sha256(self.A0)
        sim = self.make_sim(self.A0) if self.make_sim else Lenia(self.rule, self.A0)
        R2 = self.rule.R ** 2
        for s in range(self.steps + 1):
            if record:
                self.mass.append(float(sim.A.sum()) / R2)
                if s >= self.keep_from and (s - self.keep_from) % self.keep_every == 0:
                    self.frames[s] = sim.A.astype(np.float32) if on_step is None else on_step(sim, s)
            if s < self.steps:
                sim.step()
        self.final_sha = state_sha256(sim.A)
        self.final = sim.A
        return self

    def record(self) -> dict:
        return {"key": self.key, "rule": self.rule.to_dict(), "grid": {"shape": list(self.A0.shape),
                "boundary": "periodic", "dtype": "float64"}, "integrator": "euler+clip[0,1]",
                "steps": self.steps, "time_units": self.steps / self.rule.T, "initial_state": self.built,
                "initial_state_sha256": self.init_sha, "final_state_sha256": self.final_sha,
                **({"rule_note": self.rule_note} if self.rule_note else {})}


def save_provenance(folder: Path, exhibit: dict, runs: list[Run]) -> None:
    cv = code_version()
    exhibit = dict(exhibit)
    exhibit["runs"] = [r.record() for r in runs]
    exhibit["simulator"] = {"package": "alm.lenia.Lenia (unchanged)", "git_commit": cv.get("git_commit"),
                            "git_dirty": cv.get("git_dirty")}
    exhibit["render"] = {"colormap": "matplotlib inferno, A in [0,1] mapped linearly, nearest-neighbour",
                         "script": "research/experiments/VIS-talk/film.py"}
    exhibit["reproduce"] = (f"git checkout <this commit> && .venv/bin/python research/experiments/VIS-talk/film.py "
                            f"{exhibit['exhibit']}   # verify only: film.py verify {exhibit['exhibit']}")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "provenance.json").write_text(json.dumps(exhibit, indent=2) + "\n")


# --- seeds --------------------------------------------------------------------------------------

def roll_to_centre(A: np.ndarray) -> np.ndarray:
    cx, cy = periodic_centroid(A)
    n = A.shape[0]
    return np.roll(A, (int(round(n / 2 - cy)), int(round(n / 2 - cx))), axis=(0, 1))


def settled_orbium(burn_steps: int = 1000) -> np.ndarray:
    """S001 placed on 128^2, run burn_steps, integer-rolled so its centroid is at the centre."""
    A = specimens.load("S001").place(128)
    sim = Lenia(S001_RULE, A)
    for _ in range(burn_steps):
        sim.step()
    return roll_to_centre(sim.A)


def crop(A: np.ndarray, size: int) -> np.ndarray:
    n = A.shape[0]
    o = (n - size) // 2
    return A[o:o + size, o:o + size]


def paste(world: np.ndarray, patch: np.ndarray, cy: int, cx: int) -> None:
    """Add patch centred at (cy, cx) on the torus; refuses overlapping support."""
    h, w = patch.shape
    ys = (np.arange(h) + cy - h // 2) % world.shape[0]
    xs = (np.arange(w) + cx - w // 2) % world.shape[1]
    sub = world[np.ix_(ys, xs)]
    if ((sub > 0) & (patch > 0)).any():
        raise ValueError("supports overlap")
    world[np.ix_(ys, xs)] = sub + patch


def catalog_entry(index: int) -> tuple[dict, Rule, np.ndarray]:
    import hashlib

    raw = specimens.ANIMALS_JSON.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == specimens.ANIMALS_SHA256
    e = json.loads(raw)[index]
    p = e["params"]
    kn = {1: "poly", 2: "exp"}
    rule = Rule(R=int(p["R"]), T=p["T"], mu=p["m"], sigma=p["s"],
                beta=tuple(float(Fraction(x)) for x in str(p["b"]).split(",")),
                kernel=kn[p.get("kn", 1)], growth=kn[p.get("gn", 1)])
    return e, rule, rle.decode(e["cells"]) / 255.0


EXHIBIT_FUNCS: dict[str, callable] = {}


def exhibit(gid: str):
    def deco(f):
        EXHIBIT_FUNCS[gid] = f
        return f
    return deco


# exhibits are defined in ex_*.py modules next to this file
def _load_modules():
    sys.modules.setdefault("film", sys.modules[__name__])
    sys.path.insert(0, str(HERE))
    for p in sorted(HERE.glob("ex_*.py")):
        __import__(p.stem)


def verify(gids: list[str]) -> int:
    bad = 0
    for gid in gids:
        folder = next(EXHIBITS.glob(f"{gid}-*"))
        prov = json.loads((folder / "provenance.json").read_text())
        runs = EXHIBIT_FUNCS[gid](render=False)
        got = {r.key: r.final_sha for r in runs}
        for rec in prov["runs"]:
            ok = got.get(rec["key"]) == rec["final_state_sha256"]
            bad += not ok
            print(f"{gid} {rec['key']}: {'OK' if ok else 'MISMATCH'}", flush=True)
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    _load_modules()
    if argv[:1] == ["verify"]:
        return verify(argv[1:] or sorted(EXHIBIT_FUNCS))
    for gid in argv:
        EXHIBIT_FUNCS[gid](render=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
