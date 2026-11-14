"""SOUP films.

  python film.py duel <blend.npz> <dominant.npz> <out.mp4>   same world, two heredities, side by side,
                                                              with the live genome-diversity curve
  python film.py solo <npz> <out.mp4> [title]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import shutil, subprocess
from viz import colour
from diversity import spread

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG = (11, 13, 18)


def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except OSError:
        return ImageFont.load_default()


class Writer:
    """Raw RGB frames piped to ffmpeg (libx264, yuv420p, crf 20)."""

    def __init__(self, out, fps=30):
        self.out, self.fps, self.p = out, fps, None

    def append_data(self, fr):
        fr = np.ascontiguousarray(fr[: fr.shape[0] // 2 * 2, : fr.shape[1] // 2 * 2])
        if self.p is None:
            h, w = fr.shape[:2]
            self.p = subprocess.Popen([shutil.which("ffmpeg") or "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
                                       "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(self.fps), "-i", "-",
                                       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", self.out],
                                      stdin=subprocess.PIPE)
        self.p.stdin.write(fr.tobytes())

    def close(self):
        self.p.stdin.close()
        if self.p.wait():
            raise RuntimeError("ffmpeg failed")


def gain_of(A):
    a = A[-1].astype(np.float32)
    return np.percentile(a[a > 0.05], 99)


def duel(pb, pd, out, scale=2):
    db, dd = np.load(pb), np.load(pd)
    Ab, Gb, T = db["A"], db["G"], db["t"]
    Ad, Gd = dd["A"], dd["G"]
    n = Ab.shape[1] * scale
    sb = [spread(Ab[s].astype(np.float32), Gb[s].astype(np.float32) / 255) for s in range(len(T))]
    sd = [spread(Ad[s].astype(np.float32), Gd[s].astype(np.float32) / 255) for s in range(len(T))]
    gb, gd = gain_of(Ab), gain_of(Ad)
    W, H = 2 * n + 30 + 0, n + 70 + 150
    w = Writer(out)
    f1, f2 = font(22), font(15)
    lo, hi = min(min(sb), min(sd)) * 0.9, max(max(sb), max(sd)) * 1.05
    for s in range(len(T)):
        im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
        for k, (A, G, g, lab, sub) in enumerate([(Ab, Gb, gb, "Blending heredity", "genomes average where matter meets"),
                                                 (Ad, Gd, gd, "Particulate heredity", "a cell keeps its biggest parcel's genome")]):
            x0 = 10 + k * (n + 10)
            fr = colour(A[s], G[s], g).repeat(scale, 0).repeat(scale, 1)
            im.paste(Image.fromarray(fr), (x0, 60))
            dr.text((x0, 8), lab, fill=(232, 230, 223), font=f1)
            dr.text((x0, 36), sub, fill=(138, 143, 153), font=f2)
        # diversity strip
        y0, y1, x0, x1 = 60 + n + 20, H - 25, 60, W - 20
        dr.text((10, y0 - 4), "genome", fill=(138, 143, 153), font=f2)
        dr.text((10, y0 + 14), "diversity", fill=(138, 143, 153), font=f2)
        dr.line([(x0, y1), (x1, y1)], fill=(60, 60, 60))
        for ser, col in ((sb, (200, 120, 255)), (sd, (120, 230, 200))):
            pts = [(x0 + (x1 - x0) * i / (len(T) - 1), y1 - (y1 - y0) * (v - lo) / (hi - lo)) for i, v in enumerate(ser[:s + 1])]
            if len(pts) > 1:
                dr.line(pts, fill=col, width=3)
                dr.text((pts[-1][0] + 6, pts[-1][1] - 9), "blending" if ser is sb else "particulate", fill=col, font=f2)
        dr.text((x0 + 4, y1 + 4), f"t = {T[s] * 0.2:6.0f} time units", fill=(138, 143, 153), font=f2)
        w.append_data(np.asarray(im))
    for _ in range(45):
        w.append_data(np.asarray(im))
    w.close()


def solo(p, out, title="", scale=3):
    d = np.load(p); A, G, T = d["A"], d["G"], d["t"]
    g = gain_of(A); n = A.shape[1] * scale
    w = Writer(out)
    f1, f2 = font(22), font(15)
    for s in range(len(T)):
        im = Image.new("RGB", (n + 20, n + 70), BG); dr = ImageDraw.Draw(im)
        im.paste(Image.fromarray(colour(A[s], G[s], g).repeat(scale, 0).repeat(scale, 1)), (10, 50))
        dr.text((10, 10), title, fill=(232, 230, 223), font=f1)
        dr.text((10, n + 52), f"t = {T[s] * 0.2:6.0f} time units   colour = genome, brightness = matter",
                fill=(138, 143, 153), font=f2)
        w.append_data(np.asarray(im))
    for _ in range(45):
        w.append_data(np.asarray(im))
    w.close()


if __name__ == "__main__":
    if sys.argv[1] == "duel":
        duel(*sys.argv[2:5])
    else:
        solo(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
