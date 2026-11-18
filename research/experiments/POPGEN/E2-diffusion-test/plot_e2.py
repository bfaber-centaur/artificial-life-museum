"""Figure for E2: s_t vs delta (left), observed vs diffusion-predicted take-hold (right)."""
import json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
r = json.load(open("e2_results.json"))
ds = ["0.0", "0.02", "0.05", "0.1", "0.2"]
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
st = r["s_t"]
x = [float(d) for d in ds[1:]]
ax[0].axhline(0, color="#888", lw=0.8)
for d in ds[1:]:
    ax[0].scatter([float(d)] * len(st[d]["each"]), [v * 1e3 for v in st[d]["each"]], color="#3b6ea5", s=18, alpha=0.6)
ax[0].plot(x, [st[d]["mean"] * 1e3 for d in ds[1:]], "o-", color="#1f3b5c")
ax[0].set_xlabel("mutant δ (rule g = 0.5 + δ)"); ax[0].set_ylabel("selection $s_t$ (×10⁻³ per tu)")
ax[0].set_title("Head-to-head selection at p≈0.5")
c = r["conditions"]
obs = [c[d]["observed"] / c[d]["n"] for d in ds]
pred = [c[d]["predicted_pi"] for d in ds]
lo = [c[d]["interval95"][0] / c[d]["n"] for d in ds]; hi = [c[d]["interval95"][1] / c[d]["n"] for d in ds]
xx = range(len(ds))
ax[1].vlines(xx, lo, hi, color="#c9a227", lw=6, alpha=0.5, label="95% interval from diffusion")
ax[1].scatter(xx, pred, marker="_", s=300, color="#8a6d00", label="predicted π")
ax[1].scatter(xx, obs, color="#b22222", zorder=3, label="observed")
ax[1].set_xticks(list(xx)); ax[1].set_xticklabels(["0", "0.02", "0.05", "0.1", "0.2"])
ax[1].set_xlabel("mutant δ"); ax[1].set_ylabel("fraction with share ≥ 0.05 at 3000 tu")
ax[1].set_title("Single-cell mutants: theory vs Lenia"); ax[1].legend(fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(sys.argv[1] if len(sys.argv) > 1 else "e2.png", dpi=150)
