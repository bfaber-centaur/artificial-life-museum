"""G028 still: final states of the 60 Flow-Lenia scout rules (flow_scan.py), one tile each.

Needs states/flow_<seed>.npy from `flow_scan.py 0 60` (gitignored; the scout rebuilds them).
Writes research/gallery/exhibits/G028-sixty-flow-worlds/{sixty-flow-worlds.png, provenance.json}.
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent.parent / "VIS-talk"))
from film import BG, DIM, EXHIBITS, colorize, text  # noqa: E402

H = Path(__file__).parent
rows = {json.loads(l)["seed"]: json.loads(l) for l in (H / "flow_scan.jsonl").open()}
S, pad, cols = 128, 8, 10
seeds = sorted(rows)[:60]
W = cols * (S + pad) + pad
Hh = 64 + (len(seeds) // cols) * (S + pad + 16)
img = Image.new("RGB", (W, Hh), BG)
text(img, (pad, 12), "Sixty Flow-Lenia worlds", 24, bold=True)
text(img, (pad, 42), "one random rule each, one noise patch each, after 600 time units (128 x 128, A in [0, 1])", 13, fill=DIM)
shas = {}
for j, s in enumerate(seeds):
    A = np.load(H / "states" / f"flow_{s}.npy")
    shas[s] = hashlib.sha256(np.ascontiguousarray(A).tobytes()).hexdigest()
    r, c = divmod(j, cols)
    x, y = pad + c * (S + pad), 64 + r * (S + pad + 16)
    text(img, (x, y), f"FL-{s}", 11, fill=DIM)
    img.paste(Image.fromarray(colorize(A.astype(np.float64))), (x, y + 14))
out = EXHIBITS / "G028-sixty-flow-worlds"
out.mkdir(parents=True, exist_ok=True)
img.save(out / "sixty-flow-worlds.png", optimize=True)
(out / "provenance.json").write_text(json.dumps({
    "exhibit": "G028", "title": "Sixty Flow-Lenia worlds", "media": ["sixty-flow-worlds.png"],
    "runs": "research/experiments/WINGS/flow_scan.jsonl (rule seeds 0-59, rule = FlowRule.random(default_rng([7, seed])), "
            "40x40 noise patch, 128^2, 3000 steps, float64); tiles are the float32 final states",
    "tile_sha256_float32": shas, "claim": "C064",
    "reproduce": "python research/experiments/WINGS/flow_scan.py 0 60 && python research/experiments/WINGS/flow_sheet.py"}, indent=2) + "\n")
print("ok", len(seeds))
