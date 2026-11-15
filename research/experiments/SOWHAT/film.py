"""SOWHAT film: the same epidemic in three worlds, side by side, with live infection curves.

  python film.py epidemic OUT.mp4 OUT.gif
"""
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import epidemic as ep

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG = (11, 11, 15)          # vitrine
COL = {ep.S: (34, 36, 48), ep.I: (230, 159, 0), ep.R: (0, 114, 178)}   # Okabe-Ito orange / blue
LINE = {"mixed": (204, 121, 167), "lattice": (86, 180, 233), "shortcuts": (240, 228, 66)}
TITLE = {"mixed": "well mixed", "lattice": "neighbours only", "shortcuts": "neighbours + 1% far"}


def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except OSError:
        return ImageFont.load_default()


def ffmpeg():
    return shutil.which("ffmpeg") or "ffmpeg"


def render(x, scale):
    rgb = np.zeros(x.shape + (3,), np.uint8)
    for k, c in COL.items():
        rgb[x == k] = c
    return np.kron(rgb, np.ones((scale, scale, 1), np.uint8))


def epidemic_film(mp4, gif, every=5, tmax=700, scale=2, seed=0, poster=120):
    sims = {w: ep.Epidemic(ep.N, w, seed=[2026, 11, 15, 3, seed]) for w in ep.WORLDS}
    hist = {w: [s.counts()[1]] for w, s in sims.items()}
    side, pad, top, chart_h = ep.N * scale, 16, 40, 170
    W = 3 * side + 4 * pad
    H = top + side + pad + chart_h + 34
    f_t, f_s = font(17), font(13)
    frames = []
    for t in range(0, tmax + 1):
        if t:
            for w, s in sims.items():
                if s.counts()[1] > 0:
                    s.step()
                hist[w].append(s.counts()[1])
        if t % every:
            continue
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        for j, w in enumerate(ep.WORLDS):
            x0 = pad + j * (side + pad)
            im.paste(Image.fromarray(render(sims[w].x, scale)), (x0, top))
            c = sims[w].counts()
            d.text((x0, 10), TITLE[w], fill=LINE[w], font=f_t)
            d.text((x0, top + side + 4), f"sick now {100 * c[1]:4.1f}%   ever {100 * (c[1] + c[2]):5.1f}%",
                   fill=(200, 200, 210), font=f_s)
        # chart: infected fraction vs time, shared axes
        cy0, cy1 = top + side + pad + 22, top + side + pad + chart_h
        cx0, cx1 = pad + 40, W - pad
        ymax = 0.6
        d.line([(cx0, cy1), (cx1, cy1)], fill=(90, 90, 105))
        d.line([(cx0, cy0), (cx0, cy1)], fill=(90, 90, 105))
        for yv in (0.2, 0.4, 0.6):
            yy = cy1 - (cy1 - cy0) * yv / ymax
            d.line([(cx0, yy), (cx1, yy)], fill=(40, 40, 52))
            d.text((pad, yy - 7), f"{int(yv * 100)}%", fill=(150, 150, 165), font=f_s)
        for w in ep.WORLDS:
            h = np.array(hist[w])
            xs = cx0 + (cx1 - cx0) * np.arange(h.size) / tmax
            ys = cy1 - (cy1 - cy0) * np.minimum(h, ymax) / ymax
            d.line(list(zip(xs.tolist(), ys.tolist())), fill=LINE[w], width=2)
        d.text((cx0 + 6, cy0 - 18), "share of people sick at once", fill=(170, 170, 185), font=f_s)
        d.text((cx1 - 110, cy1 + 6), f"time step {t:4d}", fill=(170, 170, 185), font=f_s)
        lx = cx0
        for lab, c in (("never sick", COL[ep.S]), ("sick", COL[ep.I]), ("recovered", COL[ep.R])):
            d.rectangle([lx, cy1 + 9, lx + 11, cy1 + 20], fill=c, outline=(120, 120, 135))
            d.text((lx + 16, cy1 + 6), lab, fill=(170, 170, 185), font=f_s)
            lx += 30 + int(d.textlength(lab, font=f_s))
        frames.append(np.asarray(im))
        if t == poster:
            im.save(mp4.replace(".mp4", "-t120.png"))
    h, w_ = frames[0].shape[:2]
    p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{w_}x{h}", "-r", "20", "-i", "-", "-c:v", "libx264",
                          "-pix_fmt", "yuv420p", "-crf", "20", mp4], stdin=subprocess.PIPE)
    for fr in frames:
        p.stdin.write(np.ascontiguousarray(fr).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", mp4, "-vf",
                    "fps=12,scale=760:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=none",
                    gif], check=True)


if __name__ == "__main__":
    if sys.argv[1] == "epidemic":
        epidemic_film(sys.argv[2], sys.argv[3])
