"""G052: one genome, seven landings. Re-runs a C078 mutant at its first-trial spot ("o", as in
mutant.py, dominant) and at the six replay spots (as in replay.py), keeping frames, and checks
each replay's final hash against replay.jsonl (first trials, which ran 5000 steps: their
recorded mutant-mass series up to step 2500 against mutant.jsonl, within 0.1, since the delta
there is rounded to 4 decimals). Then draws the film.

  python replay_film.py run <k> <o|j> ...        frames -> SOUP_OUT/rf_<k>_<j>.npz
  python replay_film.py film <out.mp4> <k> <k>   one row per genome
"""
import hashlib, json, os, sys
from pathlib import Path
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
from soup import Kernels, Soup
from mutant import RULE, N, settled
from film import Writer, font

HERE = Path(__file__).parent
OUT = Path(os.environ.get("SOUP_OUT", HERE / "states"))
STEPS, FRAME = 2500, 25


def record(k, j):
    if j == "o":
        return next(r for r in map(json.loads, open(HERE / "mutant.jsonl")) if r["mutant"] == k and r["mode"] == "dominant")
    return next(r for r in map(json.loads, open(HERE / "replay.jsonl")) if r["mutant"] == k and r["placement"] == int(j))


def run(k, j):
    kern = Kernels(np.random.default_rng([7, RULE]))
    A0, G0 = settled(kern)
    h = kern.h
    m = next(r for r in map(json.loads, open(HERE / "mutant.jsonl")) if r["mutant"] == k)
    rec = record(k, j)
    y, x = rec["y"], rec["x"]
    mut = np.clip(h + np.array(m["delta"]), 0, 1); deff = mut - h
    u = deff / np.linalg.norm(deff); half = np.linalg.norm(deff) / 2
    yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    dy = np.minimum(np.abs(yy - y), N - np.abs(yy - y)); dx = np.minimum(np.abs(xx - x), N - np.abs(xx - x))
    G1 = G0.copy(); G1[:, dy ** 2 + dx ** 2 <= 100] = mut[:, None]
    S = Soup(kern, A0, G1, mut_every=0, inherit="dominant")
    As, Ms, mass = [], [], []
    for t in range(STEPS + 1):
        if t % FRAME == 0:
            proj = np.tensordot(u, S.G - h[:, None, None], 1)
            mk = (S.A > 0.05) & (proj > half)
            As.append(S.A.astype(np.float16)); Ms.append(mk); mass.append(float(S.A[mk].sum()))
        if t < STEPS:
            S.step()
    if j == "o":
        # First trials ran 5000 steps from the unrounded delta; mutant.jsonl keeps delta to 4 decimals, so
        # this is a close re-creation, not bitwise: check its mutant mass stays within 0.1 of the record.
        e = rec["every"] // FRAME
        ok = float(np.max(np.abs(np.array(mass[::e]) - rec["mutant_mass"][: len(mass[::e])]))) < 0.1
    else:
        ok = hashlib.sha256(S.A.tobytes() + S.G.tobytes()).hexdigest() == rec["final_sha256"]
    np.savez_compressed(OUT / f"rf_{k}_{j}.npz", A=np.array(As), M=np.array(Ms), mass=np.array(mass), ok=ok)
    print(k, j, "hash match" if ok else "HASH MISMATCH", round(mass[0], 1), round(mass[-1], 1), flush=True)


def film(out, ks, scale=1, cols=("o", 0, 1, 2, 3, 4, 5)):
    n = N * scale; pad = 6; top = 34; lab = 22
    W = len(cols) * (n + pad) + pad
    H = top + len(ks) * (n + lab + pad) + pad
    d = {(k, j): np.load(OUT / f"rf_{k}_{j}.npz") for k in ks for j in cols}
    assert all(bool(v["ok"]) for v in d.values()), "a run does not match its recorded hash"
    gain = np.percentile(d[(ks[0], "o")]["A"][0][d[(ks[0], "o")]["A"][0] > 0.05].astype(np.float32), 99)
    F, f2 = font(17), font(14)
    w = Writer(out, fps=20); last = None
    nf = len(d[(ks[0], "o")]["A"])
    for i in range(nf):
        im = Image.new("RGB", (W, H), (11, 13, 18)); dr = ImageDraw.Draw(im)
        dr.text((pad, 8), f"Same genome, dropped in seven places  ·  t = {i * FRAME * 0.2:.0f}", fill=(220, 220, 214), font=F)
        for r, k in enumerate(ks):
            y0 = top + r * (n + lab + pad)
            for c, j in enumerate(cols):
                x0 = pad + c * (n + pad)
                v = d[(k, j)]; A = v["A"][i].astype(np.float32); M = v["M"][i]
                b = np.clip(A / gain, 0, 1) ** 0.8
                rgb = np.stack([b * 0.32, b * 0.40, b * 0.52], -1)
                rgb[M] = np.stack([b[M] * 1.0, b[M] * 0.62, b[M] * 0.15], -1) * 1.15
                tile = (np.clip(rgb, 0, 1) * 255).astype(np.uint8).repeat(scale, 0).repeat(scale, 1)
                im.paste(Image.fromarray(tile), (x0, y0 + lab))
                ratio = v["mass"][i] / v["mass"][0]
                tag = ("first trial" if j == "o" else f"replay {j + 1}") + f"   ×{ratio:.2f}"
                col = (255, 175, 70) if ratio >= 1 else (150, 160, 175)
                dr.text((x0 + 2, y0 + 3), (f"mutant {k}: " if c == 0 else "") + tag, fill=col, font=f2)
        fr = np.asarray(im); w.append_data(fr); last = fr
    for _ in range(40):
        w.append_data(last)
    w.close()
    Image.fromarray(last).save(str(out).replace(".mp4", "-final.png"))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        a = sys.argv[2:]
        for k, j in zip(a[0::2], a[1::2]):
            run(int(k), j)
    else:
        film(sys.argv[2], [int(x) for x in sys.argv[3:]])
