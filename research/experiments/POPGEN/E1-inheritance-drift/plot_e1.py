"""Figure: one mutant cell under three inheritance rules (E1a/E1c) -> $POPGEN_OUT/e1-inheritance.png"""
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("POPGEN_OUT", "/tmp/claude-0/-home-user/1e73a8fc-c1a3-55c2-9798-cc47a6a901a7/scratchpad/popgen"))
rs = [json.loads(l) for l in open(HERE / "e1.jsonl")]
panels = [("blend+", 2, "Blending inheritance\n(mutant-majority matter)"), ("part+", 1, "Majority-rule inheritance"),
          ("s+", 1, "Unbiased particulate inheritance"), ("s0", 1, "Unbiased, neutral control cell")]
fig, axs = plt.subplots(1, 4, figsize=(13, 3.4), sharey=True)
for ax, (arm, col, title) in zip(axs, panels):
    for r in rs:
        if r["arm"] == arm:
            t = [x[0] for x in r["trace"]]; y = [x[col] for x in r["trace"]]
            ax.plot(t, y, color="#2b6cb0" if arm != "s0" else "#718096", lw=1.1, alpha=0.8)
    ax.set_title(title, fontsize=10); ax.set_xlabel("time (tu)"); ax.set_ylim(0, 0.7)
    ax.spines[["top", "right"]].set_visible(False); ax.grid(axis="y", color="#e2e8f0", lw=0.6)
axs[0].set_ylabel("mutant share of all matter")
fig.suptitle("One mutant cell (g 0.7) among ~74 residents (g 0.5), 12 replicates per rule", fontsize=11)
fig.tight_layout()
fig.savefig(OUT / "e1-inheritance.png", dpi=150)
print(OUT / "e1-inheritance.png")
