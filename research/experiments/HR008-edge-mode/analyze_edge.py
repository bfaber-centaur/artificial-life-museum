#!/usr/bin/env python3
"""HR-008: fit lambda two ways per intervention from edge_mode.json and compare lingering states.

(a) slope of death step vs ln(s - s*)            -> 1/lambda_a  (steps per e-fold)
(b) slope of ln|A_die - A_surv| in its exponential range (1e-9 .. 1e-2) -> lambda_b per step
Usage: python analyze_edge.py   (in this directory)
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(HERE, "edge_mode.json")))
print("iv,s_star,bracket,lambda_a_per_tu,lambda_b_per_tu,linger_step,death_scaling")
for r in res:
    sc = [(d, t) for d, t in r["scaling"] if t is not None]
    x = np.log([d for d, _ in sc]); y = np.array([t for _, t in sc], float)
    slope_a = np.polyfit(x, y, 1)[0]                       # steps per e-fold (negative)
    diff = np.array(r["diff"]); t = np.arange(1, len(diff) + 1)
    m = (diff > 1e-9) & (diff < 1e-2)
    if m.sum() < 5:   # no exponential phase: the bracket straddles a discrete (pixel) jump
        print(f"{r['iv']},{r['s_star']:.12f},{r['s_hi'] - r['s_lo']:.1e},n/a,n/a,n/a,"
              f"pair differs by {diff[0]:.2f} at step 1 (discrete edit); death step "
              + " ".join(f"{d:.0e}:{t}" for d, t in r["scaling"]))
        continue
    slope_b = np.polyfit(t[m], np.log(diff[m]), 1)[0]      # per step
    print(f"{r['iv']},{r['s_star']:.12f},{r['s_hi'] - r['s_lo']:.1e},{-10 / slope_a:.3f},"
          f"{10 * slope_b:.3f},{r['linger_step']},"
          + " ".join(f"{d:.0e}:{t}" for d, t in r["scaling"]))
E = {r["iv"]: np.load(os.path.join(HERE, f"edge-{r['iv']}.npy")) for r in res if r["linger_step"] > 1}
print("\nlingering state (aligned): mass sum/R^2, and pairwise Pearson correlation / max|diff|")
for k, A in E.items():
    print(f"  {k}: mass {A.sum() / 169:.4f}")
ks = list(E)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        a, b = E[ks[i]], E[ks[j]]
        print(f"  {ks[i]} vs {ks[j]}: corr {np.corrcoef(a.ravel(), b.ravel())[0, 1]:.4f}, "
              f"max|diff| {np.abs(a - b).max():.3f}, rel L2 {np.linalg.norm(a - b) / np.linalg.norm(a):.3f}")
