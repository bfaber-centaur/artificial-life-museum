"""Render a grid of final states from a sweep .npz (crops centred on the mass)."""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from field import centroids  # noqa: E402


def crop(A, half=40):
    cx, cy = centroids(A[None].astype(np.float64))
    if np.isnan(cx[0]):
        return np.zeros((2 * half, 2 * half))
    A = np.roll(A, (A.shape[0] // 2 - int(cy[0]), A.shape[1] // 2 - int(cx[0])), (0, 1))
    c = A.shape[0] // 2
    return A[c - half : c + half, c - half : c + half]


def gallery(states, titles, out, ncol=8, half=40):
    n = len(states)
    nrow = (n + ncol - 1) // ncol
    fig, axs = plt.subplots(nrow, ncol, figsize=(1.6 * ncol, 1.75 * nrow), squeeze=False)
    for ax in axs.flat:
        ax.axis("off")
    for ax, A, t in zip(axs.flat, states, titles):
        ax.imshow(crop(A, half), cmap="magma", vmin=0, vmax=1, interpolation="nearest")
        ax.set_title(t, fontsize=6)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
