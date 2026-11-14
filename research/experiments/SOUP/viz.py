"""Render SOUP snapshots: colour = genome (fixed random projection of the K weights to RGB),
brightness = matter. Contact sheets, films, and the trait-over-time 'fan'.

  python viz.py sheet <npz> <png> [k]
  python viz.py worlds <png> <npz>:<label> ...      (G034)
"""
import json, sys
import numpy as np
from PIL import Image

PROJ = np.random.default_rng(5).normal(size=(3, 10))


def colour(A, G, gain=None):
    """A (n, n) float, G (K, n, n) in [0, 1] -> uint8 RGB."""
    g = G.astype(np.float32) / (255.0 if G.dtype == np.uint8 else 1.0) - 0.5
    c = 0.5 + 0.5 * np.tanh(np.tensordot(PROJ[:, :g.shape[0]], g, 1))
    A = A.astype(np.float32)
    if gain is None:
        live = A[A > 0.05]
        gain = np.percentile(live, 99) if live.size else 1.0
    v = np.clip(A / gain, 0, 1) ** 0.8
    return (np.moveaxis(c, 0, -1) * v[..., None] * 255).astype(np.uint8)


def load(path):
    d = np.load(path)
    return d["A"], d["G"], d["t"]


def sheet(path, out, k=8):
    A, G, t = load(path)
    idx = np.linspace(0, len(t) - 1, k).round().astype(int)
    gain = np.percentile(A[-1][A[-1] > 0.05].astype(np.float32), 99)
    ims = [colour(A[i], G[i], gain) for i in idx]
    Image.fromarray(np.concatenate(ims, 1)).save(out)




def worlds(pairs, out, cols=4, scale=1):
    """G034: final frames of several worlds, one kernel set each, labelled."""
    from PIL import ImageDraw, ImageFont
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except OSError:
        f = ImageFont.load_default()
    tiles = []
    for path, label in pairs:
        A, G, t = load(path)
        im = Image.fromarray(colour(A[-1], G[-1]).repeat(scale, 0).repeat(scale, 1))
        canvas = Image.new("RGB", (im.width, im.height + 26), (11, 13, 18))
        canvas.paste(im, (0, 26))
        ImageDraw.Draw(canvas).text((4, 4), label, fill=(200, 200, 195), font=f)
        tiles.append(np.asarray(canvas))
    rows = [np.concatenate(tiles[i:i + cols], 1) for i in range(0, len(tiles), cols)]
    pad = 6
    rows = [np.pad(r, ((0, pad), (0, 0), (0, 0)), constant_values=11) for r in rows]
    Image.fromarray(np.concatenate(rows, 0)).save(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":
        sheet(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 8)
    elif cmd == "worlds":
        worlds([tuple(a.split(":", 1)) for a in sys.argv[3:]], sys.argv[2])
