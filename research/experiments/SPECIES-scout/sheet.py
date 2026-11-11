"""Contact sheet of every BODY world found by scout.py, cropped around its largest body.

Usage: python sheet.py REGION [MAX]  -> sheet-REGION.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent


def crop(A: np.ndarray, half: int) -> np.ndarray:
    y, x = np.unravel_index(np.argmax(np.real(np.fft.ifft2(np.fft.fft2(A) * np.fft.fft2(np.ones((9, 9)), s=A.shape)))), A.shape)
    A = np.roll(A, (A.shape[0] // 2 - y + 4, A.shape[1] // 2 - x + 4), axis=(0, 1))
    c = A.shape[0] // 2
    return A[c - half:c + half, c - half:c + half]


def main(region: str, cap: int = 80):
    rows = [json.loads(l) for l in (HERE / f"scout-{region}.jsonl").read_text().splitlines()]
    items = []
    for r in rows:
        f = HERE / "snaps" / region / f"{r['seed']}-{r['k']}.npz"
        if not f.exists():
            continue
        z = np.load(f)
        for A, b in zip(z["A"], z["idx"]):
            items.append((r, int(b), A))
    items = items[:cap]
    if not items:
        print("no bodies")
        return
    cols = 8
    rws = (len(items) + cols - 1) // cols
    fig, axs = plt.subplots(rws, cols, figsize=(cols * 1.9, rws * 2.1), squeeze=False)
    for ax in axs.flat:
        ax.axis("off")
    for ax, (r, b, A) in zip(axs.flat, items):
        ru, w = r["rule"], r["worlds"][b]
        ax.imshow(crop(A, 4 * ru["R"]), cmap="inferno", vmin=0, vmax=1)
        beta = ",".join(f"{x:.2g}" for x in ru["beta"])
        ax.set_title(f"k{r['k']}.{b} {w['sub']}\n{ru['kernel'][0]}{ru['growth'][0]} m{ru['mu']:.3f} s{ru['sigma']:.4f}\nb[{beta}]",
                     fontsize=6)
    fig.tight_layout()
    fig.savefig(HERE / f"sheet-{region}.png", dpi=110)
    print(len(items), "bodies")


if __name__ == "__main__":
    main(sys.argv[1], *(int(a) for a in sys.argv[2:]))
