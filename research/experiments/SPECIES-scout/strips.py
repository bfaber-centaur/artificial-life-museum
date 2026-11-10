"""Thumbnail strips of walks.jsonl: one image per start, one row per direction."""
import json, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import numpy as np
from sheet import crop
from scout import HERE
rows = [json.loads(l) for l in (HERE / "walks.jsonl").read_text().splitlines()]
every = int(sys.argv[1]) if len(sys.argv) > 1 else 2
for s in sorted({r["start"] for r in rows}):
    rs = [r for r in rows if r["start"] == s]
    cols = max(len(r["stages"]) for r in rs) // every + 1
    fig, axs = plt.subplots(len(rs), cols, figsize=(cols * 1.1, len(rs) * 1.25), squeeze=False)
    for ax in axs.flat: ax.axis("off")
    for row, r in zip(axs, rs):
        A = np.load(HERE / "walks" / f"{s.replace(':', '-')}-{r['dir']}.npz")["A"]
        for j, i in enumerate(range(0, len(r["stages"]), every)):
            st = r["stages"][i]
            row[j].imshow(crop(A[i], 30), cmap="inferno", vmin=0, vmax=1)
            row[j].set_title(f"d{r['dir']} m{st['mu']:.3f}\ns{st['sigma']:.4f} {st.get('sub', st['cls'])[:4]}", fontsize=5)
    fig.tight_layout(); fig.savefig(HERE / f"strip-{s.replace(':', '-')}.png", dpi=100)
